#include "rover_state.h"

#include <stdio.h>
#include <string.h>

RobotState currentState = STATE_IDLE;
FaultCode activeFault = FAULT_NONE;

const char* StateToString(void)
{
    switch (currentState)
    {
        case STATE_IDLE:            return "IDLE";
        case STATE_MAST_DEPLOYMENT: return "MAST_DEPLOYMENT";
        case STATE_STANDBY:         return "STANDBY";
        case STATE_AUTO:            return "AUTO";
        case STATE_SAFE:            return "SAFE";
        default:                    return "UNKNOWN";
    }
}

const char* FaultToString(void)
{
    switch (activeFault)
    {
        case FAULT_NONE:         return "NONE";
        case FAULT_VOLTAGE_HIGH: return "VOLTAGE_HIGH";
        case FAULT_TEMP_HIGH:    return "TEMP_HIGH";
        case FAULT_CURRENT_HIGH: return "CURRENT_HIGH";
        case FAULT_COMM_TIMEOUT: return "COMM_TIMEOUT";
        case FAULT_JETSON_ERROR: return "JETSON_ERROR";
        case FAULT_UNKNOWN:      return "UNKNOWN";
        default:                 return "UNKNOWN";
    }
}

uint8_t RoverState_IsLocked(void)
{
    return currentState == STATE_SAFE;
}

uint8_t RoverState_SetState(RobotState state)
{
    if (currentState == STATE_SAFE && state != STATE_SAFE)
    {
        return 0U;
    }

    currentState = state;
    return 1U;
}

uint8_t RoverState_SetStateFromString(const char *stateText)
{
    if (stateText == NULL)
    {
        return 0U;
    }

    if (strcmp(stateText, "IDLE") == 0)
    {
        return RoverState_SetState(STATE_IDLE);
    }

    if (strcmp(stateText, "MAST_DEPLOYMENT") == 0)
    {
        return RoverState_SetState(STATE_MAST_DEPLOYMENT);
    }

    if (strcmp(stateText, "STANDBY") == 0)
    {
        return RoverState_SetState(STATE_STANDBY);
    }

    if (strcmp(stateText, "AUTO") == 0)
    {
        return RoverState_SetState(STATE_AUTO);
    }

    if (strcmp(stateText, "SAFE") == 0)
    {
        return RoverState_SetState(STATE_SAFE);
    }

    return 0U;
}

void ReportFault(FaultCode fault)
{
    activeFault = fault;
    currentState = STATE_SAFE;

    printf(">>NACK, %s<<\r\n", FaultToString());
    printf("System is locked in SAFE mode. Use RECOVER after resolving the fault.\r\n");
}

void RecoverFromFault(void)
{
    activeFault = FAULT_NONE;
    currentState = STATE_STANDBY;

    printf(">>ACK, RECOVER<<\r\n");
    printf(">>SET_STATE STANDBY<<\r\n");
}

void PrintState(void)
{
    printf(">>SET_STATE %s<<\r\n", StateToString());
}

void Robot_Task(void)
{
    static uint32_t lastTick = 0U;
    static uint8_t mastBlinkStep = 0U;
    uint32_t now = HAL_GetTick();

    switch (currentState)
    {
        case STATE_IDLE:
            if (now - lastTick >= 400U)
            {
                lastTick = now;
                HAL_GPIO_TogglePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin);
            }
            break;

        case STATE_STANDBY:
            if (now - lastTick >= 1000U)
            {
                lastTick = now;
                HAL_GPIO_TogglePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin);
            }
            break;

        case STATE_MAST_DEPLOYMENT:
            if (now - lastTick >= 200U)
            {
                lastTick = now;

                if ((mastBlinkStep % 2U) == 0U)
                {
                    HAL_GPIO_WritePin(LED_GREEN_GPIO_Port,
                                      LED_GREEN_Pin,
                                      GPIO_PIN_SET);
                }
                else
                {
                    HAL_GPIO_WritePin(LED_GREEN_GPIO_Port,
                                      LED_GREEN_Pin,
                                      GPIO_PIN_RESET);
                }

                mastBlinkStep = (mastBlinkStep + 1U) % 8U;
            }
            break;

        case STATE_AUTO:
            HAL_GPIO_WritePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin, GPIO_PIN_SET);
            break;

        case STATE_SAFE:
        default:
            HAL_GPIO_WritePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin, GPIO_PIN_RESET);
            break;
    }
}
