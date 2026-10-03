/*
 * temperature_sensor.c
 *
 *  Created on: 2026年9月18日
 *      Author: linxinyu
 */
#include "temperature_sensor.h"
#include <stdio.h>
#include <string.h>
#include <math.h>

#define TEMP_ADC_CHANNEL_COUNT 6U

#define ADC_REF_VOLTAGE        3.3f
#define ADC_MAX_VALUE          4095.0f

/* Document Section 1: Supply voltage divider */
#define SUPPLY_R1              33000.0f
#define SUPPLY_R2              10000.0f
#define SUPPLY_DIVIDER_GAIN    ((SUPPLY_R1 + SUPPLY_R2) / SUPPLY_R2)

/* Document Section 2: PT1000 resistance calculation */
#define R_SERIES               5000.0f
#define R_PARALLEL             8200.0f

/* Document Section 3: Callendar-Van Dusen constants */
#define PT1000_R0              1000.0f
#define PT1000_A               3.9083e-3f
#define PT1000_B              -5.775e-7f
#define PT1000_C              -4.183e-12f

#define PT1000_TEMP_MIN_C      -200.0f
#define PT1000_TEMP_MAX_C       850.0f
#define TEMP_INVALID_VALUE     -999.0f

/* Engineering validity limits for rover motor temperature.
 * These limits are intentionally wider than normal motor operation,
 * but reject floating ADC values such as 700+ deg C.
 */
#define MOTOR_TEMP_VALID_MIN_C -200.0f
#define MOTOR_TEMP_VALID_MAX_C 300.0f

/* Temperature board supply validity.
 * The board is supplied from 5 V and measured through a 33k/10k divider.
 * Keep this range relatively wide to avoid false rejection.
 */
#define TEMP_SUPPLY_MIN_V 3.5f
#define TEMP_SUPPLY_MAX_V 6.5f

/* ADC rail margin.
 * Used to reject floating, shorted, or saturated ADC inputs.
 */
#define TEMP_ADC_MIN_RAW 20U
#define TEMP_ADC_MAX_RAW 4075U

/* PT1000 resistance plausibility.
 * Kept wider than the engineering temperature limit.
 */
#define PT1000_R_MIN_VALID 100.0f
#define PT1000_R_MAX_VALID 5000.0f

static ADC_HandleTypeDef *tempAdc = NULL;
static uint16_t adcRaw[TEMP_ADC_CHANNEL_COUNT];
static volatile uint8_t adcDone = 0U;

void TemperatureSensor_Init(ADC_HandleTypeDef *hadc)
{
    tempAdc = hadc;
    adcDone = 0U;
    memset(adcRaw, 0, sizeof(adcRaw));
}

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef *hadc)
{
    if (hadc == tempAdc)
    {
        adcDone = 1U;
    }
}

static void TemperatureSensor_InvalidateChannel(TemperatureSensorData *data, uint8_t index)
{
    if ((data == NULL) || (index >= TEMP_SENSOR_COUNT))
    {
        return;
    }

    data->uPt[index] = 0.0f;
    data->resistance[index] = TEMP_INVALID_VALUE;
    data->temperature[index] = TEMP_INVALID_VALUE;
    data->valid[index] = 0U;
}

static uint8_t TemperatureSensor_IsSupplyValid(float uSupply)
{
    if ((uSupply < TEMP_SUPPLY_MIN_V) || (uSupply > TEMP_SUPPLY_MAX_V))
    {
        return 0U;
    }

    return 1U;
}

static uint8_t TemperatureSensor_IsChannelValid(uint16_t raw,
                                                float uPt,
                                                float uSupply,
                                                float resistance,
                                                float temperature)
{
    /* Reject ADC rail values */
    if ((raw <= TEMP_ADC_MIN_RAW) || (raw >= TEMP_ADC_MAX_RAW))
    {
        return 0U;
    }

    /* PT voltage must be inside ADC measurable range */
    if ((uPt <= 0.0f) || (uPt >= ADC_REF_VOLTAGE))
    {
        return 0U;
    }

    /* PT voltage must also be lower than the calculated board supply */
    if (uPt >= uSupply)
    {
        return 0U;
    }

    /* Reject physically unreasonable PT1000 resistance */
    if ((resistance < PT1000_R_MIN_VALID) || (resistance > PT1000_R_MAX_VALID))
    {
        return 0U;
    }

    /* Reject unrealistic engineering temperatures */
    if ((temperature < MOTOR_TEMP_VALID_MIN_C) || (temperature > MOTOR_TEMP_VALID_MAX_C))
    {
        return 0U;
    }

    return 1U;
}

static float ConvertAdcToVoltage(uint16_t raw)
{
    return ((float)raw * ADC_REF_VOLTAGE) / ADC_MAX_VALUE;
}

static float ConvertPtVoltageToResistance(float uPtAdc, float uSupply)
{
    float rEq;

    /*
     * Req = RSeries * UADC / (USupply - UADC)
     */
    if (uPtAdc <= 0.0f || uPtAdc >= uSupply)
    {
        return -1.0f;
    }

    rEq = R_SERIES * uPtAdc / (uSupply - uPtAdc);

    /*
     * RPT1000 = (Req * RParallel) / (RParallel - Req)
     */
    if (rEq <= 0.0f || rEq >= R_PARALLEL)
    {
        return -1.0f;
    }

    return (rEq * R_PARALLEL) / (R_PARALLEL - rEq);
}

static float CalculatePt1000ResistanceFromTemperature(float temperature)
{
    float t = temperature;

    if (t < 0.0f)
    {
        /*
         * Document Section 3, below 0 C:
         * Rt = R0 * [1 + A*t + B*t^2 + C*(t - 100)*t^3]
         */
        return PT1000_R0 *
               (1.0f
                + PT1000_A * t
                + PT1000_B * t * t
                + PT1000_C * (t - 100.0f) * t * t * t);
    }

    /*
     * Document Section 3, above 0 C:
     * Rt = R0 * (1 + A*t + B*t^2)
     */
    return PT1000_R0 *
           (1.0f
            + PT1000_A * t
            + PT1000_B * t * t);
}

static float ConvertPt1000ResistanceToTemperature(float resistance)
{
    float rMin;
    float rMax;

    if (resistance <= 0.0f)
    {
        return TEMP_INVALID_VALUE;
    }

    rMin = CalculatePt1000ResistanceFromTemperature(PT1000_TEMP_MIN_C);
    rMax = CalculatePt1000ResistanceFromTemperature(PT1000_TEMP_MAX_C);

    if (resistance < rMin || resistance > rMax)
    {
        return TEMP_INVALID_VALUE;
    }

    if (resistance >= PT1000_R0)
    {
        float ratio;
        float discriminant;

        ratio = resistance / PT1000_R0;

        /*
         * Rt = R0 * (1 + A*t + B*t^2)
         *
         * Rearranged:
         * B*t^2 + A*t + (1 - Rt/R0) = 0
         *
         * T = (-A ± sqrt(A^2 - 4B(1 - R/R0))) / (2B)
         */
        discriminant = PT1000_A * PT1000_A
                     - 4.0f * PT1000_B * (1.0f - ratio);

        if (discriminant < 0.0f)
        {
            return TEMP_INVALID_VALUE;
        }

        /*
         * Use the physical root for normal temperature.
         */
        return (-PT1000_A + sqrtf(discriminant)) / (2.0f * PT1000_B);
    }
    else
    {
        /*
         * Below 0 C:
         * The formula includes the C term:
         * Rt = R0 * [1 + A*t + B*t^2 + C*(t - 100)*t^3]
         *
         * This cannot use the simple quadratic inverse.
         * Use bisection in the valid PT1000 range: -200 C to 0 C.
         */
        float low = PT1000_TEMP_MIN_C;
        float high = 0.0f;

        for (uint8_t i = 0U; i < 40U; i++)
        {
            float mid = (low + high) * 0.5f;
            float rMid = CalculatePt1000ResistanceFromTemperature(mid);

            if (rMid < resistance)
            {
                low = mid;
            }
            else
            {
                high = mid;
            }
        }

        return (low + high) * 0.5f;
    }
}

uint8_t TemperatureSensor_Read(TemperatureSensorData *data)
{
    uint32_t startTick;

    if (tempAdc == NULL || data == NULL)
    {
        return 0U;
    }

    adcDone = 0U;

    if (HAL_ADC_Start_DMA(tempAdc,
                          (uint32_t *)adcRaw,
                          TEMP_ADC_CHANNEL_COUNT) != HAL_OK)
    {
        return 0U;
    }

    startTick = HAL_GetTick();

    while (!adcDone)
    {
        if ((HAL_GetTick() - startTick) > 100U)
        {
            HAL_ADC_Stop_DMA(tempAdc);
            return 0U;
        }
    }

    HAL_ADC_Stop_DMA(tempAdc);

    memset(data, 0, sizeof(*data));

    /*
     * ADC Rank order:
     * adcRaw[0] = Uref / supply divider
     * adcRaw[1] = PT1
     * adcRaw[2] = PT2
     * adcRaw[3] = PT3
     * adcRaw[4] = PT4
     * adcRaw[5] = PT5
     */
    data->rawSupply = adcRaw[0];
    data->uSupplyAdc = ConvertAdcToVoltage(adcRaw[0]);
    data->uSupply = data->uSupplyAdc * SUPPLY_DIVIDER_GAIN;

    /*
     * The PT1000 resistance calculation depends on the shared board supply.
     * If the supply measurement itself is invalid, all temperature channels
     * are unreliable.
     */
    if (!TemperatureSensor_IsSupplyValid(data->uSupply))
    {
        for (uint8_t i = 0U; i < TEMP_SENSOR_COUNT; i++)
        {
            data->rawPt[i] = adcRaw[i + 1U];
            TemperatureSensor_InvalidateChannel(data, i);
        }

        return 1U;
    }

    /*
     * Per-channel independent validation.
     * One invalid PT1000 channel will not affect the other channels.
     */
    for (uint8_t i = 0U; i < TEMP_SENSOR_COUNT; i++)
    {
        uint16_t raw;
        float uPt;
        float resistance;
        float temperature;

        raw = adcRaw[i + 1U];
        uPt = ConvertAdcToVoltage(raw);
        resistance = ConvertPtVoltageToResistance(uPt, data->uSupply);
        temperature = ConvertPt1000ResistanceToTemperature(resistance);

        data->rawPt[i] = raw;
        data->uPt[i] = uPt;
        data->resistance[i] = resistance;
        data->temperature[i] = temperature;

        if (TemperatureSensor_IsChannelValid(raw,
                                             uPt,
                                             data->uSupply,
                                             resistance,
                                             temperature))
        {
            data->valid[i] = 1U;
        }
        else
        {
            TemperatureSensor_InvalidateChannel(data, i);
        }
    }

    return 1U;
}

static void PrintFixed1(float value)
{
    int32_t v = (int32_t)(value * 10.0f + (value >= 0.0f ? 0.5f : -0.5f));

    if (v < 0)
    {
        printf("-");
        v = -v;
    }

    printf("%ld.%ld", (long)(v / 10), (long)(v % 10));
}

static void PrintFixed2(float value)
{
    int32_t v = (int32_t)(value * 100.0f + (value >= 0.0f ? 0.5f : -0.5f));

    if (v < 0)
    {
        printf("-");
        v = -v;
    }

    printf("%ld.%02ld", (long)(v / 100), (long)(v % 100));
}

void TemperatureSensor_PrintHeartbeat(void)
{
    TemperatureSensorData data;

    if (!TemperatureSensor_Read(&data))
    {
        printf("TEMP_HB,t=%lus,ADC=ERROR\r\n",
               (unsigned long)(HAL_GetTick() / 1000U));
        return;
    }

    printf("TEMP_HB,t=%lus,USUPPLY=",
           (unsigned long)(HAL_GetTick() / 1000U));

    PrintFixed2(data.uSupply);
    printf("V");

    for (uint8_t i = 0U; i < TEMP_SENSOR_COUNT; i++)
    {
    	/*
    	printf(",PT%u_RAW=%u,PT%u_U=",
    			(unsigned)(i + 1U),
    	        data.rawPt[i],
    	        (unsigned)(i + 1U));

    	PrintFixed2(data.uPt[i]);

    	printf("V,PT%u_R=", (unsigned)(i + 1U));
		*/

    	printf(",PT%u=", (unsigned)(i + 1U));

        if (data.valid[i])
        {
        	/*
        	PrintFixed1(data.resistance[i]);
        	printf("ohm,PT%u_T=", (unsigned)(i + 1U));
			*/
            PrintFixed1(data.temperature[i]);
            printf("C");
        }
        else
        {
            printf("NA");
        }
    }

    printf("\r\n");
}

