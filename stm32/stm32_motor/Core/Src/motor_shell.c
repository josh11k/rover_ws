#include "motor_shell.h"

#include "main.h"
#include "motor_manager.h"

#include <stdio.h>

// USER CONFIGURATION: Increase this only if longer terminal commands are needed.
#define MOTOR_COMMAND_BUFFER_SIZE 32U

extern UART_HandleTypeDef huart2;

static char commandBuffer[MOTOR_COMMAND_BUFFER_SIZE];
static uint8_t commandIndex = 0;

void MotorShell_Task(void)
{
    uint8_t receivedChar;

    if (HAL_UART_Receive(&huart2, &receivedChar, 1, 1U) != HAL_OK)
        return;

    HAL_UART_Transmit(&huart2, &receivedChar, 1, 10U);

    if (receivedChar == '\r' || receivedChar == '\n')
    {
        if (commandIndex > 0U)
        {
            commandBuffer[commandIndex] = '\0';
            printf("\r\n");
            MotorManager_ExecuteCommand(commandBuffer);
            commandIndex = 0;
        }

        return;
    }

    if (commandIndex < sizeof(commandBuffer) - 1U)
    {
        commandBuffer[commandIndex++] = (char)receivedChar;
    }
    else
    {
        commandIndex = 0;
        printf("\r\nCommand too long\r\n");
    }
}
