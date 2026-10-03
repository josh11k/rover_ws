/*
 * rover_state.c
 *
 *  Created on: 2026年7月31日
 *      Author: caiderui
 */

#include "rover_state.h"
#include <stdio.h>

RobotState currentState = STATE_IDLE;
FaultCode activeFault = FAULT_NONE;

const char* StateToString(void)
{
    switch(currentState)
    {
        case STATE_IDLE:
            return "IDLE";

        case STATE_MAST_DEPLOYMENT:
            return "MAST_DEPLOYMENT";

        case STATE_STANDBY:
            return "STANDBY";

        case STATE_SAFE:
            return "SAFE";

        default:
            return "UNKNOWN";
    }
}

const char* FaultToString(void)
{
    switch(activeFault)
    {
        case FAULT_NONE:
            return "NONE";

        case FAULT_VOLTAGE_HIGH:
            return "VOLTAGE_HIGH";

        case FAULT_TEMP_HIGH:
            return "TEMP_HIGH";

        case FAULT_CURRENT_HIGH:
            return "CURRENT_HIGH";

        case FAULT_COMM_TIMEOUT:
            return "COMM_TIMEOUT";

        default:
            return "UNKNOWN";
    }
}

void ReportFault(FaultCode fault)
{
    activeFault = fault;
    currentState = STATE_SAFE;

    printf("\r\nFAULT DETECTED: ");

    switch(fault)
    {
        case FAULT_VOLTAGE_HIGH:
            printf("Voltage too high!\r\n");
            break;

        case FAULT_TEMP_HIGH:
            printf("Temperature too high!\r\n");
            break;

        case FAULT_CURRENT_HIGH:
            printf("Current too high!\r\n");
            break;

        case FAULT_COMM_TIMEOUT:
            printf("Communication timeout!\r\n");
            break;

        default:
            printf("Unknown fault.\r\n");
            break;
    }

    PrintState();
    printf("System is in SAFE mode. Input '4' to STANDBY mode.\r\n");
}

void PrintState(void)
{
    printf("STATE: %s\r\n", StateToString());
}

void Robot_Task(void)
{
    static uint32_t lastTick = 0;
    static uint8_t driveStep = 0;

    uint32_t now = HAL_GetTick();

    switch(currentState)
    {
    	case STATE_IDLE:
    		if(now - lastTick >= 400)
    		{
    			lastTick = now;
    			HAL_GPIO_TogglePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin);
    		}
    		break;

        case STATE_STANDBY:
            if(now - lastTick >= 1000)
            {
                lastTick = now;
                HAL_GPIO_TogglePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin);
            }
            break;

        case STATE_MAST_DEPLOYMENT:
            if(now - lastTick >= 200)
            {
                lastTick = now;

                if(driveStep == 0)
                {
                    HAL_GPIO_WritePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin, GPIO_PIN_SET);
                    driveStep = 1;
                }
                else if(driveStep == 1)
                {
                    HAL_GPIO_WritePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin, GPIO_PIN_RESET);
                    driveStep = 2;
                }
                else if(driveStep == 2)
                {
                    HAL_GPIO_WritePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin, GPIO_PIN_SET);
                    driveStep = 3;
                }
                else if(driveStep == 3)
                {
                    HAL_GPIO_WritePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin, GPIO_PIN_RESET);
                    driveStep = 4;
                    lastTick = now - 1000;
                }
                else
                {
                    driveStep = 0;
                }
            }
            break;

        default:
            break;
    }
}
