#include "rover_housekeeping.h"

#include "fan_driver.h"
#include "ina228.h"
#include "motor_manager.h"
#include "rover_state.h"
#include "temperature_sensor.h"

#include <stdio.h>
#include <string.h>

#define INA_ADDRESS_MIN 0x40U
#define INA_ADDRESS_MAX 0x4FU
#define HK_MAX_INA_COUNT 4U
#define HK_MOTOR_COUNT 5U
#define HK_TEMP_INTERVAL_MS 1000U
#define HK_INA_INTERVAL_MS 1000U
#define HK_REPORT_INTERVAL_MS 10000U		/*HB 1s pro time*/


static TemperatureSensorData latestTemperature;
static uint8_t temperatureValid = 0U;

static uint8_t inaAddresses[HK_MAX_INA_COUNT];
static INA228_Measurement inaMeasurements[HK_MAX_INA_COUNT];
static uint8_t inaValid[HK_MAX_INA_COUNT];
static uint8_t inaCount = 0U;

static uint32_t lastTempTick = 0U;
static uint32_t lastInaTick = 0U;
static uint32_t lastReportTick = 0U;


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


static void ReadINADevices(void)
{
    for (uint8_t i = 0U; i < inaCount; i++)
    {
        inaValid[i] = INA228_ReadMeasurement(inaAddresses[i],
                                             &inaMeasurements[i]);
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
