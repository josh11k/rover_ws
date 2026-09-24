#include "rover_protocol.h"


#include "motor_manager.h"
#include "rover_state.h"

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define RX_LINE_BUFFER_SIZE 160U
#define JETSON_ALIVE_TIMEOUT_MS 180000U

#define JETSON_MOTOR_CODE_MIN      25L
#define JETSON_MOTOR_CODE_MAX      998L

#define SET_MOTOR_TARGET_MIN_COUNT 4U
#define SET_MOTOR_TARGET_MAX_COUNT 5U
#define SET_MOTOR_TARGET_COUNT     6U

static UART_HandleTypeDef *protocolUart = NULL;
static char rxLine[RX_LINE_BUFFER_SIZE];
static uint8_t rxIndex = 0U;
static uint8_t rxOverflow = 0U;
static uint32_t lastAliveTick = 0U;
static uint8_t aliveTimeoutReported = 0U;

static char *Trim(char *text)
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

static char *UnframeJetsonMessage(char *line)
{
    size_t length;
    char *message;

    line = Trim(line);
    length = strlen(line);

    if (length >= 4U && line[0] == '>' && line[1] == '>' &&
        line[length - 2U] == '<' && line[length - 1U] == '<')
    {
        line[length - 2U] = '\0';
        message = line + 2U;
        return Trim(message);
    }

    return line;
}

static FaultCode ParseFault(const char *text)
{
    if (strcmp(text, "VOLTAGE_HIGH") == 0) return FAULT_VOLTAGE_HIGH;
    if (strcmp(text, "TEMP_HIGH") == 0)    return FAULT_TEMP_HIGH;
    if (strcmp(text, "CURRENT_HIGH") == 0) return FAULT_CURRENT_HIGH;
    if (strcmp(text, "COMM_TIMEOUT") == 0) return FAULT_COMM_TIMEOUT;
    if (strcmp(text, "JETSON_ERROR") == 0) return FAULT_JETSON_ERROR;
    return FAULT_UNKNOWN;
}

static uint8_t ParseSetMotorSyncTargets(const char *message,
                                        uint16_t *targets,
                                        uint8_t *targetCount)
{
    const char *cursor;
    char *endPtr;
    long value;
    uint8_t count = 0U;

    if ((message == NULL) || (targets == NULL) || (targetCount == NULL))
    {
        return 0U;
    }

    cursor = message;

    while (1)
    {
        while (*cursor == ' ')
        {
            cursor++;
        }

        if (*cursor == '\0')
        {
            break;
        }

        if (count >= SET_MOTOR_TARGET_MAX_COUNT)
        {
            return 0U;
        }

        value = strtol(cursor, &endPtr, 10);

        if (endPtr == cursor)
        {
            return 0U;
        }

        /*
         * Input-side position-mode range check.
         * Motor manager still keeps its own protection as second layer.
         */
        if ((value < JETSON_MOTOR_CODE_MIN) ||
            (value > JETSON_MOTOR_CODE_MAX))
        {
            return 0U;
        }

        targets[count] = (uint16_t)value;
        count++;

        cursor = endPtr;

        while (*cursor == ' ')
        {
            cursor++;
        }

        if (*cursor == ',')
        {
            cursor++;
            continue;
        }

        if (*cursor == '\0')
        {
            break;
        }

        return 0U;
    }

    if ((count < SET_MOTOR_TARGET_MIN_COUNT) ||
        (count > SET_MOTOR_TARGET_MAX_COUNT))
    {
        return 0U;
    }

    *targetCount = count;
    return 1U;
}

static void PrintHelp(void)
{
    printf("Integrated STM test commands:\r\n");
    printf("  >>ALIVE: IDLE<<\r\n");
    printf("  >>SET_STATE: IDLE<<\r\n");
    printf("  >>SET_STATE: MAST_DEPLOYMENT<<\r\n");
    printf("  >>SET_STATE: STANDBY<<\r\n");
    printf("  >>SET_STATE: AUTO<<\r\n");
    printf("  >>SET_MOTOR: 512,512,512,512,512<<  (M1..M5 position codes, 25..998)\r\n");
    printf("  >>ERROR: TEMP_HIGH<<\r\n");
    printf("  RECOVER\r\n");
    printf("  pos / status / s / b / si  (direct motor debug commands)\r\n");
}

static void ProcessCommand(char *line)
{
    char *message;
    char *payload;

    if (rxOverflow)
    {
        SendNack("COMMAND_TOO_LONG");
        rxOverflow = 0U;
        return;
    }

    message = UnframeJetsonMessage(line);

    if (message[0] == '\0')
    {
        return;
    }

    if (strcmp(message, "help") == 0 || strcmp(message, "HELP") == 0)
    {
        PrintHelp();
        return;
    }

    if (strcmp(message, "state") == 0 || strcmp(message, "STATE") == 0)
    {
        PrintState();
        return;
    }

    if (strcmp(message, "RECOVER") == 0 || strcmp(message, "recover") == 0)
    {
        RecoverFromFault();
        return;
    }

    if (strncmp(message, "ALIVE:", 6U) == 0)
    {
        lastAliveTick = HAL_GetTick();
        aliveTimeoutReported = 0U;
        SendAck("ALIVE");
        return;
    }

    if (strncmp(message, "ERROR:", 6U) == 0)
    {
        payload = Trim(message + 6U);
        ReportFault(ParseFault(payload));
        return;
    }

    if (strncmp(message, "SET_STATE:", 10U) == 0)
    {
        payload = Trim(message + 10U);

        if (RoverState_SetStateFromString(payload))
        {
            SendAck("SET_STATE");
            PrintState();
        }
        else
        {
            SendNack(RoverState_IsLocked() ? "STATE_LOCKED_SAFE" : "UNKNOWN_STATE");
        }
        return;
    }

    if (strncmp(message, "SET_MOTOR:", 10U) == 0)
    {
        uint16_t targets[SET_MOTOR_TARGET_MAX_COUNT];
        uint8_t targetCount;
        char syncCommand[96];
        size_t used = 0U;

        if (RoverState_IsLocked())
        {
            SendNack("STATE_LOCKED_SAFE");
            return;
        }

        if (!ParseSetMotorSyncTargets(message + 10U,
                                      targets,
                                      &targetCount))
        {
            SendNack("INVALID_MOTOR_COMMAND");
            return;
        }

        used += (size_t)snprintf(syncCommand + used,
                                 sizeof(syncCommand) - used,
                                 "sync");

        for (uint8_t i = 0U; i < targetCount; i++)
        {
            used += (size_t)snprintf(syncCommand + used,
                                     sizeof(syncCommand) - used,
                                     " %u %u",
                                     (unsigned)(i + 1U),
                                     (unsigned)targets[i]);

            if (used >= sizeof(syncCommand))
            {
                SendNack("MOTOR_COMMAND_TOO_LONG");
                return;
            }
        }

        SendAck("MOTOR");
        MotorManager_ExecuteCommand(syncCommand);

        return;
    }

    if (strncmp(message, "MOTOR_CMD:", 10U) == 0 ||
        strncmp(message, "RAW_MOTOR:", 10U) == 0)
    {
        payload = Trim(message + 10U);
        MotorManager_ExecuteCommand(payload);
        return;
    }

    /* Direct motor debug commands inherited from Task 5.6. */
    if (strcmp(message, "s") == 0 || strcmp(message, "b") == 0 ||
        strcmp(message, "i") == 0 || strcmp(message, "si") == 0 ||
        strcmp(message, "pos") == 0 || strcmp(message, "status") == 0 ||
        strncmp(message, "sync ", 5U) == 0 || strncmp(message, "mix ", 4U) == 0 ||
        (message[0] >= '0' && message[0] <= '9'))
    {
        MotorManager_ExecuteCommand(message);
        return;
    }

    SendNack("UNKNOWN_COMMAND");
}

void RoverProtocol_Init(UART_HandleTypeDef *uart)
{
    protocolUart = uart;
    rxIndex = 0U;
    rxOverflow = 0U;
    lastAliveTick = HAL_GetTick();
    aliveTimeoutReported = 0U;
}

void RoverProtocol_Task(void)
{
    if (protocolUart == NULL)
    {
        return;
    }

    for (uint8_t i = 0U; i < 32U; i++)
    {
        uint8_t ch;
        HAL_StatusTypeDef result;

        result = HAL_UART_Receive(protocolUart, &ch, 1U, 1U);
        if (result != HAL_OK)
        {
            break;
        }

        if (ch == '\r' || ch == '\n')
        {
            if (rxIndex > 0U || rxOverflow)
            {
                rxLine[rxIndex] = '\0';
                ProcessCommand(rxLine);
            }

            rxIndex = 0U;
            rxOverflow = 0U;
        }
        else
        {
            if (rxIndex < (RX_LINE_BUFFER_SIZE - 1U))
            {
                rxLine[rxIndex++] = (char)ch;
            }
            else
            {
                rxOverflow = 1U;
            }
        }
    }
}

void RoverProtocol_CheckAliveTimeout(void)
{
    uint32_t now = HAL_GetTick();

    if (!aliveTimeoutReported &&
        activeFault == FAULT_NONE &&
        (now - lastAliveTick) > JETSON_ALIVE_TIMEOUT_MS)
    {
        aliveTimeoutReported = 1U;
        ReportFault(FAULT_COMM_TIMEOUT);
    }
}

void SendAck(const char *message)
{
    printf(">>ACK, %s<<\r\n", message);
}

void SendNack(const char *reason)
{
    printf(">>NACK, %s<<\r\n", reason);
}
