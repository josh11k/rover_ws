/*
 * fan_protocol.c
 *
 *  Created on: 2026年9月17日
 *      Author: caiderui, linxinyu
 */


#include "fan_protocol.h"
#include "fan_control.h"
#include "fan_driver.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static UART_HandleTypeDef *inputUart;
static char lineBuffer[20];
static uint8_t lineLength;
static uint8_t invalid;

// Select the temperature input UART.
void FanProtocol_Init(UART_HandleTypeDef *uart)
{
    inputUart = uart;
    lineLength = 0U;
    invalid = 0U;
}

// Complete one line; accept temperature, manual PWM, or auto command.
static void ProcessLine(void)
{
    char *endPtr;
    long value;

    if (lineLength == 0U && !invalid)
    {
        return;
    }

    lineBuffer[lineLength] = '\0';

    if (invalid)
    {
        printf("REJECTED: command too long\r\n");
    }
    else if (strncmp(lineBuffer, "pwm ", 4) == 0)
    {
        value = strtol(lineBuffer + 4, &endPtr, 10);

        while (*endPtr == ' ')
        {
            endPtr++;
        }

        if (endPtr == lineBuffer + 4 || *endPtr != '\0' ||
            value < 0L || value > 100L)
        {
            printf("REJECTED: use pwm 0..100\r\n");
        }
        else
        {
            FanControl_SetManualPWM((uint8_t)value);
            printf("UPDATE,MODE=MANUAL,PWM=%lu\r\n", value);
        }
    }
    else if (strcmp(lineBuffer, "auto") == 0)
    {
        FanControl_ClearManualPWM();
        printf("UPDATE,MODE=AUTO,PWM=%u\r\n",
               (unsigned)FanControl_GetPWM());
    }
    else
    {
        value = strtol(lineBuffer, &endPtr, 10);

        while (*endPtr == ' ')
        {
            endPtr++;
        }

        if (endPtr == lineBuffer || *endPtr != '\0' ||
            value < 0L || value > 120L)
        {
            printf("REJECTED: enter temperature 0..120, pwm 0..100, or auto\r\n");
        }
        else
        {
            uint8_t changed;

            changed = !FanControl_IsFresh() ||
                      FanControl_GetTemperature() != (int)value;

            if (FanControl_SetTemperature((int)value) && changed)
            {
                printf("UPDATE,TEMP=%ld,PWM=%u\r\n",
                       value,
                       (unsigned)FanControl_GetPWM());
            }
        }
    }

    lineLength = 0U;
    invalid = 0U;
}

// Report once per second; NA means no fresh temperature is available.
static void Heartbeat_Task(void)
{
    static uint32_t lastHeartbeat;
    uint32_t now = HAL_GetTick();
    if (now - lastHeartbeat < 1000U) return;
    lastHeartbeat = now;

    const char *mode;

    if (FanControl_IsManual())
    {
        mode = "MANUAL";
    }
    else if (FanControl_IsFresh())
    {
        mode = "AUTO";
    }
    else
    {
        mode = "FAILSAFE";
    }

    printf("HB,t=%lus,MODE=%s,TEMP=",
           (unsigned long)(now / 1000U),
           mode);
    if (FanControl_IsFresh()) printf("%d", FanControl_GetTemperature());
    else printf("NA");
    printf(",PWM=%u,RPM=%lu,FAN=%s\r\n",
           (unsigned)FanControl_GetPWM(),
           (unsigned long)FanDriver_GetRPM(),
		   FanControl_HasFault() ? "FAULT" : "OK");
}

// Poll a bounded number of bytes so other tasks keep running.
void FanProtocol_Task(void)
{
	FanDriver_Task();
	FanControl_Task();
	Heartbeat_Task();

    if (inputUart == NULL) return;
    for (unsigned i = 0; i < 32U; i++)
    {
        uint8_t ch;
        HAL_StatusTypeDef result = HAL_UART_Receive(inputUart, &ch, 1, 1);
        if (result != HAL_OK)
        {
            if (result != HAL_TIMEOUT) invalid = 1;
            break;
        }
        if (ch == '\r' || ch == '\n')
        {
            ProcessLine();
        }
        else
        {
            if (lineLength < sizeof(lineBuffer) - 1U)
            {
                lineBuffer[lineLength++] = (char)ch;
            }
            else
            {
                invalid = 1U;
            }
        }
    }
}
