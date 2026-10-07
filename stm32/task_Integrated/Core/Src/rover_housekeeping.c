#include "rover_housekeeping.h"

#include "fan_driver.h"
#include "ina228.h"
#include "motor_manager.h"
#include "rover_state.h"
#include "temperature_sensor.h"
#include "fan_control.h"
#include <stdlib.h>

#include <stdio.h>
#include <string.h>

#define HK_REPORT_INTERVAL_MS 5000U
#define INA_ADDRESS_MIN 0x40U
#define INA_ADDRESS_MAX 0x4FU
#define HK_MAX_INA_COUNT 4U
#define HK_MOTOR_COUNT 5U
#define HK_TEMP_INTERVAL_MS 1000U
#define HK_INA_INTERVAL_MS 1000U
#define HK_EXT_TEMP_MAX_C       60        /* PT1000 external sensor limit, deg C */
#define HK_MOTOR_TEMP_MAX_C     70        /* HerkuleX internal motor temp limit, deg C */
#define HK_BUS_SETTLE_MS        2000U     /* Unterspannung ignorieren, solange Schiene hochfaehrt */

/*
 * Feste Zuordnung I2C-Adresse -> Bus/Alert-Pin/PMOS und INA228-Hardware-Alert-
 * Grenzwerte (Shunt = 15 mOhm fuer alle vier Kanaele).
 * SOVL: 5 uV/LSB  -> I_max[A] * Rshunt[Ohm] / 5uV = I_max * 3000
 * BOVL/BUVL: 3.125 mV/LSB, Marge = +-10% um die Nominalspannung.
 * Ueber-/Unterspannung und Ueberstrom werden NICHT per Software-Vergleich
 * geprueft, sondern vom INA228 selbst erkannt und nur noch als DIAG_ALRT-Flag
 * ausgelesen (siehe RoverHousekeeping_CheckThresholds).
 * Die Unterspannung wird nur geprueft, wenn der zugehoerige PMOS an ist.
 */
typedef struct
{
    uint8_t address;
    const char *busName;
    int16_t sovl;   /* Ueberstrom-Schwelle */
    uint16_t bovl;  /* Ueberspannungs-Schwelle */
    uint16_t buvl;  /* Unterspannungs-Schwelle */
    int8_t pmos;    /* PowerSwitchId, -1 = Schiene immer an */
} INA228_BusConfig;

static const INA228_BusConfig inaBusConfigs[] =
{
    { 0x45U, "12V_BUS1 Jetson (3A)", 9000, 4224, 3456, PMOS_21_JETSON_12V }, /* Alert1, PC0 */
    { 0x44U, "12V_BUS2 (3A)",        9000, 4224, 3456, PMOS_22_12V },        /* Alert2, PC1 */
    { 0x41U, "9V_BUS3 Motor", 18000, 3168, 2592, PMOS_12_MOTOR_7V4 }, /* Alert3, PC2 */
    { 0x40U, "5V_BUS4 (1.6A)",       4800, 1760, 1440, PMOS_11_5V },         /* Alert4, PC3 */
};
#define INA228_BUS_CONFIG_COUNT (sizeof(inaBusConfigs) / sizeof(inaBusConfigs[0]))

static TemperatureSensorData latestTemperature;
static uint8_t temperatureValid = 0U;

static uint8_t inaAddresses[HK_MAX_INA_COUNT];
static INA228_Measurement inaMeasurements[HK_MAX_INA_COUNT];
static uint8_t inaValid[HK_MAX_INA_COUNT];
static uint16_t inaAlertFlags[HK_MAX_INA_COUNT];
static uint8_t inaCount = 0U;

static uint32_t lastTempTick = 0U;
static uint32_t lastInaTick = 0U;
static uint32_t lastReportTick = 0U;


static const INA228_BusConfig *FindBusConfig(uint8_t address)
{
    for (size_t i = 0U; i < INA228_BUS_CONFIG_COUNT; i++)
    {
        if (inaBusConfigs[i].address == address)
        {
            return &inaBusConfigs[i];
        }
    }

    return NULL;
}

static void PrintFloat1(float value)
{
    int32_t v = (int32_t)(value * 10.0f + (value >= 0.0f ? 0.5f : -0.5f));

    if (v < 0)
    {
        printf("-");
        v = -v;
    }

    printf("%ld.%ld", (long)(v / 10), (long)(v % 10));
}

static void PrintVoltageValueV(uint32_t milliV)
{
    printf("%lu.%03lu",
           (unsigned long)(milliV / 1000U),
           (unsigned long)(milliV % 1000U));
}

static void PrintSignedCurrentValueA(int32_t microA)
{
    int32_t absolute;

    if (microA < 0)
    {
        printf("-");
        absolute = -microA;
    }
    else
    {
        absolute = microA;
    }

    printf("%ld.%03ld",
           (long)(absolute / 1000000L),
           (long)((absolute % 1000000L) / 1000L));
}

static void PrintSignedMilliCValueC(int32_t milliC)
{
    int32_t absolute;

    if (milliC < 0)
    {
        printf("-");
        absolute = -milliC;
    }
    else
    {
        absolute = milliC;
    }

    printf("%ld.%03ld",
           (long)(absolute / 1000L),
           (long)(absolute % 1000L));
}

static void ScanINADevices(void)
{
    inaCount = 0U;
    memset(inaValid, 0, sizeof(inaValid));
    memset(inaAlertFlags, 0, sizeof(inaAlertFlags));

    for (uint8_t address = INA_ADDRESS_MIN;
         address <= INA_ADDRESS_MAX && inaCount < HK_MAX_INA_COUNT;
         address++)
    {
        if (INA228_IsReady(address))
        {
            inaAddresses[inaCount] = address;
            inaValid[inaCount] = 0U;

            if (INA228_SetAveraging64(address))
            {
                printf("INA%u detected at 0x%02X, averaging=64\r\n",
                       (unsigned)(inaCount + 1U),
                       address);
            }
            else
            {
                printf("INA%u detected at 0x%02X, averaging setup failed\r\n",
                       (unsigned)(inaCount + 1U),
                       address);
            }

            {
                const INA228_BusConfig *busConfig = FindBusConfig(address);

                if (busConfig != NULL)
                {
                    if (INA228_SetAlertLimits(address,
                                              busConfig->sovl,
                                              busConfig->bovl,
                                              busConfig->buvl))
                    {
                        printf("INA%u (0x%02X) = %s, alert limits armed\r\n",
                               (unsigned)(inaCount + 1U),
                               address,
                               busConfig->busName);
                    }
                    else
                    {
                        printf("INA%u (0x%02X) = %s, alert limit setup FAILED\r\n",
                               (unsigned)(inaCount + 1U),
                               address,
                               busConfig->busName);
                    }
                }
                else
                {
                    printf("INA%u (0x%02X): no bus config found, alert limits NOT armed\r\n",
                           (unsigned)(inaCount + 1U),
                           address);
                }
            }

            inaCount++;
        }
    }

    if (inaCount == 0U)
    {
        printf("No INA228 detected\r\n");
    }
}

static void ReadTemperatures(void)
{
    if (TemperatureSensor_Read(&latestTemperature))
    {
        temperatureValid = 1U;
    }
    else
    {
        temperatureValid = 0U;
    }
}

static uint8_t IsUndervoltageArmed(uint8_t address)
{
    const INA228_BusConfig *busConfig = FindBusConfig(address);

    if (busConfig != NULL && busConfig->pmos >= 0)
    {
        PowerSwitchId id = (PowerSwitchId)busConfig->pmos;

        if (!RoverState_IsPowerSwitchOn(id) ||
            RoverState_PowerSwitchOnTimeMs(id) < HK_BUS_SETTLE_MS)
        {
            return 0U;
        }
    }

    return 1U;
}

static void ReadINADevices(void)
{
    for (uint8_t i = 0U; i < inaCount; i++)
    {
        inaValid[i] = INA228_ReadMeasurement(inaAddresses[i],
                                             &inaMeasurements[i]);

        if (!INA228_ReadAlertFlags(inaAddresses[i], &inaAlertFlags[i]))
        {
            inaAlertFlags[i] = 0U;
        }
        
        if (!IsUndervoltageArmed(inaAddresses[i]))
        {
            inaAlertFlags[i] &= (uint16_t)~INA228_DIAGALRT_BUSUL;
        }
    }
}

static void PrintHousekeeping(void)
{
    printf(">>HOUSE_KEEPING_DATA:\r\n");

    printf("Time: %lus\r\n", (unsigned long)(HAL_GetTick() / 1000U));

    printf("STM Status: %s\r\n", StateToString());

    printf("STM Fault: %s\r\n", FaultToString());

    for (uint8_t motorId = 1U; motorId <= HK_MOTOR_COUNT; motorId++)
    {
        uint16_t position;
        uint8_t connected;

        printf("Motor %u: Position: ", (unsigned)motorId);

        if (MotorManager_GetPositionById(motorId, &position, &connected) &&
            connected)
        {
            printf("%u", (unsigned)position);
        }
        else
        {
            printf("NA");
        }

        printf("\r\n");

        /*
         * This is reserved for HerkuleX internal motor temperature.
         * If internal temperature reading is not implemented yet, print NA.
         */
        printf("Motor %u: Temperature \xC2\xB0""C: ", (unsigned)motorId);

        {
            int16_t motorTemperatureC;
            uint8_t tempConnected;

            if (MotorManager_GetInternalTemperatureCById(motorId,
                                                         &motorTemperatureC,
                                                         &tempConnected) &&
                tempConnected)
            {
                printf("%d", (int)motorTemperatureC);
            }
            else
            {
                printf("NA");
            }
        }

        printf("\r\n");
    }

    /*
     * Fan PWM wire is disconnected.
     * Fan runs at default full speed.
     */
    {
        uint32_t fanRpm = FanDriver_GetRPM();

        printf("Fan: Status: %s\r\n", fanRpm > 0U ? "ON" : "NA");
        printf("Fan: Speed rpm: %lu\r\n", (unsigned long)fanRpm);
    }

    for (uint8_t i = 0U; i < HK_MAX_INA_COUNT; i++)
    {
        printf("INA%u: Voltage V: ", (unsigned)(i + 1U));

        if (i < inaCount && inaValid[i])
        {
            PrintVoltageValueV(inaMeasurements[i].busVoltageMilliV);
        }
        else
        {
            printf("NA");
        }

        printf("\r\n");

        printf("INA%u: Current A: ", (unsigned)(i + 1U));

        if (i < inaCount && inaValid[i])
        {
            PrintSignedCurrentValueA(inaMeasurements[i].currentMicroA);
        }
        else
        {
            printf("NA");
        }

        printf("\r\n");

        printf("INA%u: Temperature \xC2\xB0""C: ", (unsigned)(i + 1U));

        if (i < inaCount && inaValid[i])
        {
            PrintSignedMilliCValueC(inaMeasurements[i].temperatureMilliC);
        }
        else
        {
            printf("NA");
        }

        printf("\r\n");
    }

    /*
     * Sensor 1..5 = PT1000 external temperature sensors.
     */
    for (uint8_t i = 0U; i < TEMP_SENSOR_COUNT; i++)
    {
        printf("Sensor %u: Temperature \xC2\xB0""C: ",
               (unsigned)(i + 1U));

        if (temperatureValid && latestTemperature.valid[i])
        {
            PrintFloat1(latestTemperature.temperature[i]);
        }
        else
        {
            printf("NA");
        }

        printf("\r\n");
    }

    printf("<<\r\n");
}

uint8_t RoverHousekeeping_CheckThresholds(FaultCode *outFault)
{
    for (uint8_t i = 0U; i < inaCount; i++)
    {
        const INA228_BusConfig *busConfig;
        uint8_t undervoltageArmed = 1U;

        if (!inaValid[i])
        {
            continue;
        }

        /*
         * Unterspannung nur pruefen, wenn der zugehoerige PMOS an ist und die
         * Schiene Zeit zum Hochfahren hatte. Ueberspannung und Ueberstrom
         * sind immer aktiv.
         */
        busConfig = FindBusConfig(inaAddresses[i]);
        if (busConfig != NULL && busConfig->pmos >= 0)
        {
            PowerSwitchId id = (PowerSwitchId)busConfig->pmos;

            if (!RoverState_IsPowerSwitchOn(id) ||
                RoverState_PowerSwitchOnTimeMs(id) < HK_BUS_SETTLE_MS)
            {
                undervoltageArmed = 0U;
            }
        }

        /*
         * Ueber-/Unterspannung und Ueberstrom werden vom INA228 selbst
         * erkannt (SOVL/BOVL/BUVL, siehe ScanINADevices) und hier nur noch
         * als gelatchtes DIAG_ALRT-Flag abgeholt.
         */
        if (inaAlertFlags[i] & INA228_DIAGALRT_BUSOL)
        {
            if (outFault != NULL) { *outFault = FAULT_VOLTAGE_HIGH; }
            return 1U;
        }

        if (undervoltageArmed && (inaAlertFlags[i] & INA228_DIAGALRT_BUSUL))
        {
            if (outFault != NULL) { *outFault = FAULT_VOLTAGE_HIGH; }
            return 1U;
        }

        if (inaAlertFlags[i] & INA228_DIAGALRT_SHNTOL)
        {
            if (outFault != NULL) { *outFault = FAULT_CURRENT_HIGH; }
            return 1U;
        }
    }

    if (temperatureValid)
    {
        for (uint8_t i = 0U; i < TEMP_SENSOR_COUNT; i++)
        {
            if (latestTemperature.valid[i] &&
                latestTemperature.temperature[i] > (float)HK_EXT_TEMP_MAX_C)
            {
                if (outFault != NULL) { *outFault = FAULT_TEMP_HIGH; }
                return 1U;
            }
        }
    }

    for (uint8_t motorId = 1U; motorId <= HK_MOTOR_COUNT; motorId++)
    {
        int16_t motorTemperatureC;
        uint8_t tempConnected;

        if (MotorManager_GetInternalTemperatureCById(motorId, &motorTemperatureC, &tempConnected) &&
            tempConnected &&
            motorTemperatureC > (int16_t)HK_MOTOR_TEMP_MAX_C)
        {
            if (outFault != NULL) { *outFault = FAULT_TEMP_HIGH; }
            return 1U;
        }
    }

    return 0U;
}

#define HK_ESP_TEMP_TIMEOUT_MS 15000U

static int16_t espTemperatureC = 0;
static uint32_t espTemperatureTick = 0U;
static uint8_t espTemperatureSeen = 0U;

void RoverHousekeeping_SetEspTemperatureC(int16_t temperatureC)
{
    espTemperatureC = temperatureC;
    espTemperatureTick = HAL_GetTick();
    espTemperatureSeen = 1U;
}

/* Hoechste plausible Temperatur aller Quellen an die Luefterregelung geben. */
static void UpdateFanTemperature(void)
{
    float maxT = -1000.0f;

    /* PT1000 */
    if (temperatureValid)
    {
        for (uint8_t i = 0U; i < TEMP_SENSOR_COUNT; i++)
        {
            float t = latestTemperature.temperature[i];
            if (latestTemperature.valid[i] && t > -40.0f && t < 150.0f && t > maxT)
            {
                maxT = t;
            }
        }
    }

    /* INA228 Chiptemperatur (in Milli-Grad) */
    for (uint8_t i = 0U; i < inaCount; i++)
    {
        if (inaValid[i])
        {
            float t = (float)inaMeasurements[i].temperatureMilliC / 1000.0f;
            if (t > -40.0f && t < 150.0f && t > maxT)
            {
                maxT = t;
            }
        }
    }

    /* HerkuleX-Motoren (interne Temperatur) */
    for (uint8_t motorId = 1U; motorId <= HK_MOTOR_COUNT; motorId++)
    {
        int16_t motorTemperatureC;
        uint8_t tempConnected;

        if (MotorManager_GetInternalTemperatureCById(motorId, &motorTemperatureC, &tempConnected) &&
            tempConnected &&
            motorTemperatureC > -40 && motorTemperatureC < 150 &&
            (float)motorTemperatureC > maxT)
        {
            maxT = (float)motorTemperatureC;
        }
    }

    /* ESP32 (nur, wenn zuletzt gemeldet) */
    if (espTemperatureSeen &&
        (HAL_GetTick() - espTemperatureTick) < HK_ESP_TEMP_TIMEOUT_MS &&
        espTemperatureC > -40 && espTemperatureC < 150 &&
        (float)espTemperatureC > maxT)
    {
        maxT = (float)espTemperatureC;
    }

    if (maxT > -999.0f)
    {
        if (maxT < 0.0f)
        {
            maxT = 0.0f;
        }
        FanControl_SetTemperature((int)maxT);
    }
}

void RoverHousekeeping_Init(ADC_HandleTypeDef *hadc)
{
    TemperatureSensor_Init(hadc);
    memset(&latestTemperature, 0, sizeof(latestTemperature));
    temperatureValid = 0U;

    ScanINADevices();
    ReadTemperatures();
    ReadINADevices();

    lastTempTick = HAL_GetTick();
    lastInaTick = HAL_GetTick();
    lastReportTick = HAL_GetTick() - HK_REPORT_INTERVAL_MS;
}

void RoverHousekeeping_Task(void)
{
    uint32_t now = HAL_GetTick();

    if (now - lastTempTick >= HK_TEMP_INTERVAL_MS)
    {
        lastTempTick = now;
        ReadTemperatures();
        UpdateFanTemperature();
    }

    if (now - lastInaTick >= HK_INA_INTERVAL_MS)
    {
        lastInaTick = now;
        ReadINADevices();
    }

    if (now - lastReportTick >= HK_REPORT_INTERVAL_MS)
    {
        lastReportTick = now;
        PrintHousekeeping();
    }
}