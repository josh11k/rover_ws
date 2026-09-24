/*
 * temperature_logger.c
 *
 *  Created on: 2026年9月18日
 *      Author: linxinyu
 */
#include "temperature_logger.h"
#include <stdio.h>

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

void TemperatureLogger_PrintMotorTemperatures(const TemperatureSensorData *data)
{
    if (data == NULL)
    {
        return;
    }

    for (uint8_t i = 0U; i < TEMP_SENSOR_COUNT; i++)
    {
        printf("Temp. Motor %u: T=", (unsigned)(i + 1U));

        if (data->valid[i])
        {
            PrintFixed1(data->temperature[i]);

            /*
             * UTF-8 degree sign + C.
             * This prints: °C
             */
            printf("\xC2\xB0""C");
        }
        else
        {
            printf("NA");
        }

        printf("\r\n");
    }

    printf("\r\n");
}
