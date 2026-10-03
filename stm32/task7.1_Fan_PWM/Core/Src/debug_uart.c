/*
 * debug_uart.c
 *
 *  Created on: 2026年9月17日
 *      Author: caiderui, linxinyu
 */


#include "debug_uart.h"
#include <stdio.h>

static UART_HandleTypeDef *debugUart = NULL;

// Select the UART used by printf.
void DebugUART_Init(UART_HandleTypeDef *uart)
{
    debugUart = uart;
    setvbuf(stdout, NULL, _IONBF, 0);
}

// Send one character through the debug UART.
int __io_putchar(int ch)
{
    if (debugUart == NULL)
    {
        return EOF;
    }

    uint8_t byte = (uint8_t)ch;
    if (HAL_UART_Transmit(debugUart, &byte, 1, 100) != HAL_OK)
    {
        return EOF;
    }

    return ch;
}
