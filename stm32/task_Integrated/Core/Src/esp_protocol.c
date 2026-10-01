#include "esp_protocol.h"

#include "motor_manager.h"
#include "rover_state.h"

#include <ctype.h>
#include <stdio.h>
#include <string.h>

#define ESP_RX_LINE_BUFFER_SIZE 64U

static UART_HandleTypeDef *espUart = NULL;
static char espRxLine[ESP_RX_LINE_BUFFER_SIZE];
static uint8_t espRxIndex = 0U;
static uint8_t espRxOverflow = 0U;

static char *EspTrim(char *text)
{
    char *end;

    while (*text != '\0' && isspace((unsigned char)*text))
    {
        text++;
    }

    if (*text == '\0')
    {
        return text;
    }

    end = text + strlen(text) - 1U;
    while (end > text && isspace((unsigned char)*end))
    {
        *end = '\0';
        end--;
    }

    return text;
}

static char *EspUnframe(char *line)
{
    size_t length;
    char *message;

    line = EspTrim(line);
    length = strlen(line);

    if (length >= 4U && line[0] == '>' && line[1] == '>' &&
        line[length - 2U] == '<' && line[length - 1U] == '<')
    {
        line[length - 2U] = '\0';
        message = line + 2U;
        return EspTrim(message);
    }

    return line;
}

void EspProtocol_Send(const char *msg)
{
    if (espUart == NULL)
    {
        return;
    }

    HAL_UART_Transmit(espUart, (uint8_t *)msg, (uint16_t)strlen(msg), HAL_MAX_DELAY);
}

static void EspProcessCommand(char *line)
{
    char *message;

    if (espRxOverflow)
    {
        EspProtocol_Send(">>NACK, COMMAND_TOO_LONG<<\r\n");
        espRxOverflow = 0U;
        return;
    }

    message = EspUnframe(line);

    if (message[0] == '\0')
    {
        return;
    }

    if (strcmp(message, "SET_STATE: SAFE") == 0 ||
        strcmp(message, "STOP") == 0 ||
        strcmp(message, "SAFE") == 0)
    {
        MotorManager_ExecuteCommand("b"); /* emergency brake all motors */
        RoverState_SetState(STATE_SAFE);
        PrintState();

        EspProtocol_Send(">>ACK, SAFE<<\r\n");
        printf("ESP requested SAFE stop - motors braked\r\n");
        return;
    }

    if (strncmp(message, "SET_STATE:", 10U) == 0)
    {
        /* Everything except SAFE is explicitly rejected from this channel. */
        EspProtocol_Send(">>NACK, ESP_NOT_PERMITTED<<\r\n");
        return;
    }

    EspProtocol_Send(">>NACK, UNKNOWN_COMMAND<<\r\n");
}

void EspProtocol_Init(UART_HandleTypeDef *uart)
{
    espUart = uart;
    espRxIndex = 0U;
    espRxOverflow = 0U;
}

void EspProtocol_Task(void)
{
    if (espUart == NULL)
    {
        return;
    }

    for (uint8_t i = 0U; i < 32U; i++)
    {
        uint8_t ch;
        HAL_StatusTypeDef result;

        result = HAL_UART_Receive(espUart, &ch, 1U, 1U);
        if (result != HAL_OK)
        {
            break;
        }

        if (ch == '\r' || ch == '\n')
        {
            if (espRxIndex > 0U || espRxOverflow)
            {
                espRxLine[espRxIndex] = '\0';
                EspProcessCommand(espRxLine);
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