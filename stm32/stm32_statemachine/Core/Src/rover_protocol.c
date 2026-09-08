/*
 * rover_protocol.c
 *
 *  Created on: 2026年7月31日
 *      Author: caiderui
 */

#include "rover_protocol.h"
#include "rover_state.h"
#include <stdio.h>
#include <string.h>

extern UART_HandleTypeDef huart2;

uint8_t rx_char;
char rx_buffer[64];
uint8_t rx_index = 0;

void ExecuteCommand(void)
{
    if(strcmp(rx_buffer, "help") == 0)
    {
        printf("Available commands:\r\n");
        printf("-------------------------\r\n");
        printf("help                         - Show command list\r\n");
        printf("state                        - Show current state\r\n");
        printf("SET_STATE: IDLE              - Switch to IDLE mode\r\n");
        printf("SET_STATE: MAST_DEPLOYMENT   - Switch to MAST_DEPLOYMENT mode\r\n");
        printf("SET_STATE: STANDBY           - Switch to STANDBY mode\r\n");
        printf("STOP                         - Enter STANDBY for safety\r\n");
        printf("MOTOR, m1,m2,m3,m4,m5         - Motor command placeholder only\r\n");
        printf("7    - Manual High Current(SAFE mode)\r\n");
        printf("8    - Manual High Voltage(SAFE mode)\r\n");
        printf("9    - Manual High Temperature(SAFE mode)\r\n");
        printf("0    - Manual Communication Time out(SAFE mode)\r\n");
        printf("RECOVER    - Recover SAFE to STANDBY mode\r\n");
        printf("-------------------------\r\n");
        return;
    }

    if(strcmp(rx_buffer, "state") == 0)
    {
        PrintState();
        return;
    }

    if(currentState == STATE_SAFE)
    {
        if(strcmp(rx_buffer, "RECOVER") == 0)
        {
            activeFault = FAULT_NONE;
            currentState = STATE_STANDBY;

            printf("ACK,RECOVER\r\n");
            printf("Fault cleared.\r\n");
            printf("Entering STANDBY mode.\r\n");
            PrintState();
        }
        else
        {
            printf("NACK, STATE_LOCKED\r\n");
            printf("System is in SAFE mode. Input 'RECOVER' to STANDBY mode.\r\n");
        }

        return;
    }

    if(strcmp(rx_buffer, "7") == 0)
    {
        ReportFault(FAULT_CURRENT_HIGH);
        return;
    }

    if(strcmp(rx_buffer, "8") == 0)
    {
        ReportFault(FAULT_VOLTAGE_HIGH);
        return;
    }

    if(strcmp(rx_buffer, "9") == 0)
    {
        ReportFault(FAULT_TEMP_HIGH);
        return;
    }

    if(strcmp(rx_buffer, "0") == 0)
    {
        ReportFault(FAULT_COMM_TIMEOUT);
        return;
    }

    if(strcmp(rx_buffer, "STOP") == 0)
    {
        currentState = STATE_STANDBY;

        printf("ACK, STOP\r\n");
        PrintState();
        return;
    }

    if(strcmp(rx_buffer, "SET_STATE: IDLE") == 0)
    {
        currentState = STATE_IDLE;

        printf("ACK, SET_STATE IDLE\r\n");
        PrintState();
        return;
    }

    if(strcmp(rx_buffer, "SET_STATE: MAST_DEPLOYMENT") == 0)
    {
        currentState = STATE_MAST_DEPLOYMENT;

        printf("ACK, SET_STATE MAST_DEPLOYMENT\r\n");
        PrintState();
        return;
    }

    if(strcmp(rx_buffer, "SET_STATE: STANDBY") == 0)
    {
        currentState = STATE_STANDBY;

        printf("ACK, SET_STATE STANDBY\r\n");
        PrintState();
        return;
    }

    if(strncmp(rx_buffer, "MOTOR,", 6) == 0)
    {
        printf("ACK, MOTOR\r\n");
        return;
    }

    printf("NACK, UNKNOWN_COMMAND\r\n");
}

void Shell_Task(void)
{
    if (HAL_UART_Receive(&huart2, &rx_char, 1, 100) == HAL_OK)
    {
        if (rx_char == '\r' || rx_char == '\n')
        {
            rx_buffer[rx_index] = '\0';

            if(rx_index > 0)
            {
            	ExecuteCommand();
            }

            rx_index = 0;
        }
        else
        {
        	if(rx_index < sizeof(rx_buffer)-1)
        	{
        		rx_buffer[rx_index++] = rx_char;
        	}
        	else
        	{
        	    printf("\r\nError: command too long\r\n");
        	    rx_index = 0;
        	}
        }
    }
}

void SendAck(const char *message)
{
    printf("ACK, %s\r\n", message);
}

void SendNack(const char *reason)
{
    printf("NACK, %s\r\n", reason);
}
