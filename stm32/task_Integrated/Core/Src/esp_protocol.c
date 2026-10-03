#include "esp_protocol.h"
#include "rover_protocol.h"
#include "uart_rx.h"

#include <string.h>

#define ESP_RX_LINE_BUFFER_SIZE 160U
#define ESP_LOOPBACK_TEST 1   /* TEMP: nach dem Test entfernen */

extern UART_HandleTypeDef huart2; /* TEMP Debug: ESP-RX-Ausgabe auf Tera Term */

static UART_HandleTypeDef *espUart = NULL;
static char espRxLine[ESP_RX_LINE_BUFFER_SIZE];
static uint8_t espRxIndex = 0U;
static uint8_t espRxOverflow = 0U;

void EspProtocol_Send(const char *msg)
{
    if (espUart == NULL)
    {
        return;
    }

    HAL_UART_Transmit(espUart, (uint8_t *)msg, (uint16_t)strlen(msg), HAL_MAX_DELAY);
}

void EspProtocol_Init(UART_HandleTypeDef *uart)
{
    espUart = uart;
    espRxIndex = 0U;
    espRxOverflow = 0U;
    UartRx_Start(uart);
}

void EspProtocol_Task(void)
{
    if (espUart == NULL)
    {
        return;
    }

    for (uint8_t i = 0U; i < 64U; i++)
    {
        uint8_t ch;

        if (!UartRx_GetByte(espUart, &ch))
        {
            break;
        }

        if (ch == '\r' || ch == '\n')
        {
            if (espRxIndex > 0U || espRxOverflow)
            {
                espRxLine[espRxIndex] = '\0';

                /* ESP hat dieselbe Befehlsberechtigung wie der Jetson */

                RoverProtocol_SetReplyUart(espUart);
                RoverProtocol_ProcessCommand(espRxLine);
                RoverProtocol_SetReplyUart(NULL);

            }

            espRxIndex = 0U;
            espRxOverflow = 0U;
        }
        else
        {
            if (espRxIndex < (ESP_RX_LINE_BUFFER_SIZE - 1U))
            {
                espRxLine[espRxIndex++] = (char)ch;
            }
            else
            {
                espRxOverflow = 1U;
            }
        }
    }
}