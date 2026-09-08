/*
 * ina228_monitor.c
 *
 *  Created on: 2026年9月3日
 *      Author: caiderui
 */


#include "ina228_monitor.h"

#include "ina228.h"
#include "main.h"

#include <stdio.h>

// USER CONFIGURATION: INA228 address range.
#define INA228_ADDRESS_MIN 0x40U
#define INA228_ADDRESS_MAX 0x4FU

// USER CONFIGURATION: Maximum number of INA228 devices.
#define INA228_MAX_DEVICES 16U

// USER CONFIGURATION: Time between reports.
// Change to 1000U for one report every second.
#define INA228_REPORT_INTERVAL_MS 2000U

static uint8_t addresses[INA228_MAX_DEVICES];
static uint8_t deviceCount = 0U;
static uint32_t lastReportTick = 0U;

static void INA228Monitor_Scan(void); // Finds all connected INA228 devices.

static void INA228Monitor_PrintMeasurement(
    uint8_t address); // Reads and prints one INA228 measurement.

static void INA228Monitor_PrintSignedValue(
    int32_t value,
    int32_t divisor); // Prints a signed fixed-point value.

void INA228Monitor_Init(void)
{
    printf("\r\nINA228 Multi-Device Monitor\r\n");

    INA228Monitor_Scan();

    for (uint8_t index = 0U;
         index < deviceCount;
         index++)
    {
        if (INA228_SetAveraging64(addresses[index]))
        {
            printf(
                "INA228 0x%02X averaging: 64 samples\r\n",
                addresses[index]);
        }
        else
        {
            printf(
                "INA228 0x%02X averaging setup failed\r\n",
                addresses[index]);
        }
    }

    if (deviceCount > 0U)
        HAL_Delay(250U);

    // Makes the first report appear immediately.
    lastReportTick =
        HAL_GetTick() - INA228_REPORT_INTERVAL_MS;
}

void INA228Monitor_Task(void)
{
    uint32_t now = HAL_GetTick();

    if (now - lastReportTick <
        INA228_REPORT_INTERVAL_MS)
    {
        return;
    }

    lastReportTick = now;

    for (uint8_t index = 0U;
         index < deviceCount;
         index++)
    {
        INA228Monitor_PrintMeasurement(
            addresses[index]);
    }
}

static void INA228Monitor_Scan(void)
{
    deviceCount = 0U;

    printf("INA228 addresses:");

    for (uint8_t address = INA228_ADDRESS_MIN;
         address <= INA228_ADDRESS_MAX;
         address++)
    {
        if (INA228_IsReady(address) &&
            deviceCount < INA228_MAX_DEVICES)
        {
            addresses[deviceCount] = address;
            deviceCount++;

            printf(" 0x%02X", address);
        }
    }

    if (deviceCount == 0U)
        printf(" none");

    printf("\r\n");
}

static void INA228Monitor_PrintMeasurement(
    uint8_t address)
{
    INA228_Measurement measurement;

    printf("[INA228 0x%02X]\r\n", address);

    if (!INA228_ReadMeasurement(
            address,
            &measurement))
    {
        printf("Measurement read failed\r\n\r\n");
        return;
    }

    printf("INA Temperature: ");

    INA228Monitor_PrintSignedValue(
        measurement.temperatureMilliC,
        1000L);

    printf(" degree C\r\n");

    printf(
        "Bus Voltage: %lu.%03lu V\r\n",
        (unsigned long)
            (measurement.busVoltageMilliV / 1000U),
        (unsigned long)
            (measurement.busVoltageMilliV % 1000U));

    printf("Calculated Current: ");

    INA228Monitor_PrintSignedValue(
        measurement.currentMicroA,
        1000L);

    printf(" mA\r\n\r\n");
}

static void INA228Monitor_PrintSignedValue(
    int32_t value,
    int32_t divisor)
{
    int32_t absoluteValue;

    if (value < 0)
        absoluteValue = -value;
    else
        absoluteValue = value;

    printf(
        "%s%ld.%03ld",
        value < 0 ? "-" : "",
        (long)(absoluteValue / divisor),
        (long)(absoluteValue % divisor));
}
