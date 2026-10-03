#include "motor_manager.h"

#include "herkulex.h"
#include "main.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef enum
{
    MOTOR_STANDBY = 0,
    MOTOR_HOLDING,
    MOTOR_WORKING,
    MOTOR_BRAKED
} MotorState;

typedef struct
{
    uint8_t id;
    uint16_t initialPosition;
} MotorConfig;

typedef struct
{
    uint8_t connected;
    uint8_t missCount;
    MotorState state;
    uint16_t currentPosition;
    uint8_t standbyLedOn;
    uint8_t workingLedOn;
    uint32_t lastLedChange;
    uint8_t moveActive;
    uint16_t moveTarget;
    uint32_t moveEndTick;
} MotorControl;

#define MOTOR_INITIAL_POSITION_UNSET 0xFFFFU

// USER CONFIGURATION: Add or remove rows to change the controlled motors.
// USER CONFIGURATION: Each row is {motor ID, initial position}.
// USER CONFIGURATION: Use MOTOR_INITIAL_POSITION_UNSET when no initial position is assigned.
static const MotorConfig motorConfigs[] =
{
    {1U, 490U},
    {2U, MOTOR_INITIAL_POSITION_UNSET},
    {3U, MOTOR_INITIAL_POSITION_UNSET},
    {6U, MOTOR_INITIAL_POSITION_UNSET}
};

#define MOTOR_COUNT ((uint8_t)(sizeof(motorConfigs) / sizeof(motorConfigs[0])))
#define DRS_ID_COUNT 254U
#define DRS_MAX_ID 253U

// USER CONFIGURATION: These values control discovery and disconnect timing.
#define MOTOR_DISCOVERY_INTERVAL_MS 10U
#define MOTOR_DISCOVERY_TIMEOUT_MS 10U
#define MOTOR_DISCOVERY_MISS_LIMIT 3U
#define MOTOR_CONNECTION_INTERVAL_MS 200U

// USER CONFIGURATION: Position mode is allowed only inside this holding range.
#define DRS_PROTOCOL_POSITION_MIN 0L
#define DRS_PROTOCOL_POSITION_MAX 1023L
#define DRS_HOLD_POSITION_MIN 21L
#define DRS_HOLD_POSITION_MAX 1002L

// USER CONFIGURATION: These values control movement speed and LED timing.
#define MOTOR_SPEED_COMMAND 80
#define MOTOR_MIN_MOVE_TIME_MS 500L
#define MOTOR_MAX_MOVE_TIME_MS 2800L
#define MOTOR_TIME_PER_POSITION_MS 20L
#define MOTOR_STANDBY_LED_INTERVAL_MS 1000U
#define MOTOR_WORK_LED_INTERVAL_MS 250U

static MotorControl motors[MOTOR_COUNT];
static uint8_t detectedMotor[DRS_ID_COUNT];
static uint8_t discoveryMissCount[DRS_ID_COUNT];
static uint8_t discoveryMotorId;
static uint8_t scanMotorIndex;
static uint32_t lastDiscoveryCheck;
static uint32_t lastMotorCheck;

static int8_t Motor_FindIndex(uint8_t motorId); // Finds the configured array entry for one motor ID.
static uint8_t Motor_IsInPositionDeadZone(uint16_t position); // Reports whether position mode is unsafe at this position.
static void Motor_SetState(uint8_t motorIndex,
                           MotorState newState); // Applies torque and LED behavior for one state.
static void Motor_LedTask(void); // Updates the standby and working LED blink patterns.
static void Motor_StartPositionMove(uint8_t motorIndex,
                                    uint16_t position,
                                    uint16_t durationMs); // Starts and tracks one position movement.
static void Motor_PositionMoveTask(void); // Completes tracked position movements.
static void Motor_ConnectionTask(void); // Monitors configured motors for connection changes.
static void Motor_DiscoveryTask(void); // Scans all valid DRS IDs, including unconfigured motors.
static void Motor_InitializeAll(void); // Sends every configured motor to its assigned initial position.
static void Motor_BrakeAll(void); // Applies the emergency brake to every detected motor.
static void Motor_PrintAllStatus(void); // Prints status bytes for all configured motors.
static void Motor_PrintAllPositions(void); // Prints positions for all configured motors.
static long Motor_CalculateMoveDuration(long distance); // Converts position distance into a bounded move time.
static void Motor_PrintDeadZoneWarning(uint8_t motorId,
                                       uint16_t position); // Explains how to leave the dead zone safely.

void MotorManager_Init(void)
{
    memset(motors, 0, sizeof(motors));
    memset(detectedMotor, 0, sizeof(detectedMotor));
    memset(discoveryMissCount, 0, sizeof(discoveryMissCount));

    for (uint8_t index = 0; index < MOTOR_COUNT; index++)
        motors[index].state = MOTOR_STANDBY;

    printf("Configured motor IDs:");
    for (uint8_t index = 0; index < MOTOR_COUNT; index++)
        printf(" %u", motorConfigs[index].id);
    printf("\r\n");
}

void MotorManager_Task(void)
{
    Motor_PositionMoveTask();
    Motor_ConnectionTask();
    Motor_DiscoveryTask();
    Motor_LedTask();
}

void MotorManager_ExecuteCommand(const char *input)
{
    char *idEnd;
    char *valueEnd;
    long parsedMotorId;
    long value;
    long target;
    long distance;
    long duration;
    uint8_t motorId;
    int8_t motorIndex;
    const char *command;
    MotorControl *motor;
    uint8_t statusError;
    uint8_t statusDetail;

    if (strcmp(input, "b") == 0)
    {
        Motor_BrakeAll();
        return;
    }

    if (strcmp(input, "i") == 0)
    {
        Motor_InitializeAll();
        return;
    }

    if (strcmp(input, "status") == 0)
    {
        Motor_PrintAllStatus();
        return;
    }

    if (strcmp(input, "pos") == 0)
    {
        Motor_PrintAllPositions();
        return;
    }

    parsedMotorId = strtol(input, &idEnd, 10);

    if (idEnd == input || *idEnd != ' ')
    {
        printf("Invalid format. Example: 1 +300\r\n");
        return;
    }

    while (*idEnd == ' ')
        idEnd++;

    if (*idEnd == '\0' || parsedMotorId < 0 || parsedMotorId > DRS_MAX_ID)
    {
        printf("Invalid motor command\r\n");
        return;
    }

    motorId = (uint8_t)parsedMotorId;
    motorIndex = Motor_FindIndex(motorId);

    if (motorIndex < 0)
    {
        printf("Unknown motor ID: %u\r\n", motorId);
        return;
    }

    motor = &motors[motorIndex];
    command = idEnd;

    if (!motor->connected)
    {
        printf("Command rejected: motor %u is not connected\r\n", motorId);
        return;
    }

    if (strcmp(command, "status") == 0)
    {
        if (!Herkulex_ReadStatus(motorId, &statusError, &statusDetail))
        {
            printf("Motor %u status read failed\r\n", motorId);
            return;
        }

        printf("Motor %u Status Error: 0x%02X\r\n", motorId, statusError);
        printf("Motor %u Status Detail: 0x%02X\r\n", motorId, statusDetail);
        return;
    }

    if (motor->state == MOTOR_WORKING &&
        strcmp(command, "s") != 0 &&
        strcmp(command, "b") != 0 &&
        strcmp(command, "pos") != 0)
    {
        printf("Command rejected: motor %u is already moving\r\n", motorId);
        return;
    }

    if (strcmp(command, "+") == 0 || strcmp(command, "-") == 0)
    {
        Motor_SetState((uint8_t)motorIndex, MOTOR_WORKING);
        Herkulex_MoveSpeed(motorId,
                          command[0] == '+' ? MOTOR_SPEED_COMMAND : -MOTOR_SPEED_COMMAND);
        printf("Motor %u continuous movement started\r\n", motorId);
        return;
    }

    if (strcmp(command, "b") == 0)
    {
        motor->moveActive = 0;
        Motor_SetState((uint8_t)motorIndex, MOTOR_BRAKED);
        printf("Motor %u emergency brake applied\r\n", motorId);
        return;
    }

    if (strcmp(command, "s") == 0)
    {
        motor->moveActive = 0;
        Motor_SetState((uint8_t)motorIndex, MOTOR_STANDBY);
        return;
    }

    if (strcmp(command, "pos") == 0)
    {
        if (Herkulex_ReadPositionReliable(motorId, &motor->currentPosition))
            printf("POSITION,%u,%u\r\n", motorId, motor->currentPosition);
        else
            printf("Motor %u position read failed\r\n", motorId);
        return;
    }

    if (strcmp(command, "i") == 0)
    {
        if (motorConfigs[motorIndex].initialPosition == MOTOR_INITIAL_POSITION_UNSET)
        {
            printf("Initialization rejected: motor %u initial position is not configured\r\n",
                   motorId);
            return;
        }

        value = motorConfigs[motorIndex].initialPosition;
        printf("Manual initialization: motor %u -> position %ld\r\n",
               motorId, value);
    }
    else
    {
        value = strtol(command, &valueEnd, 10);

        if (valueEnd == command || *valueEnd != '\0')
        {
            printf("Unknown motor command\r\n");
            return;
        }
    }

    if (!Herkulex_ReadPositionReliable(motorId, &motor->currentPosition))
    {
        printf("Motor %u movement cancelled: position unavailable\r\n", motorId);
        return;
    }

    if (Motor_IsInPositionDeadZone(motor->currentPosition))
    {
        Motor_PrintDeadZoneWarning(motorId, motor->currentPosition);
        return;
    }

    if (strcmp(command, "i") == 0)
        target = value;
    else if (command[0] == '+' || command[0] == '-')
        target = (long)motor->currentPosition + value;
    else
        target = value;

    if (target < DRS_PROTOCOL_POSITION_MIN ||
        target > DRS_PROTOCOL_POSITION_MAX)
    {
        printf("Motor %u REJECTED: target %ld is outside 0..1023\r\n",
               motorId, target);
        return;
    }

    if (target < DRS_HOLD_POSITION_MIN ||
        target > DRS_HOLD_POSITION_MAX)
    {
        printf("Motor %u REJECTED: target %ld is outside holding range 21..1002\r\n",
               motorId, target);
        return;
    }

    distance = labs(target - (long)motor->currentPosition);
    duration = Motor_CalculateMoveDuration(distance);

    Motor_SetState((uint8_t)motorIndex, MOTOR_WORKING);
    HAL_Delay(20U);
    Motor_StartPositionMove((uint8_t)motorIndex,
                            (uint16_t)target,
                            (uint16_t)duration);

    printf("Motor %u moving from %u to %ld in %ld ms\r\n",
           motorId, motor->currentPosition, target, duration);
}

static int8_t Motor_FindIndex(uint8_t motorId)
{
    for (uint8_t index = 0; index < MOTOR_COUNT; index++)
    {
        if (motorConfigs[index].id == motorId)
            return (int8_t)index;
    }

    return -1;
}

static uint8_t Motor_IsInPositionDeadZone(uint16_t position)
{
    return position < DRS_HOLD_POSITION_MIN ||
           position > DRS_HOLD_POSITION_MAX;
}

static void Motor_SetState(uint8_t motorIndex, MotorState newState)
{
    MotorControl *motor;
    uint8_t motorId;

    if (motorIndex >= MOTOR_COUNT)
        return;

    motor = &motors[motorIndex];
    motorId = motorConfigs[motorIndex].id;
    motor->state = newState;

    if (newState == MOTOR_STANDBY)
    {
        Herkulex_SetTorque(motorId, 0x00);
        motor->standbyLedOn = 1;
        motor->lastLedChange = HAL_GetTick();
        Herkulex_SetLed(motorId, 0x02);
        printf("Motor %u state: STANDBY\r\n", motorId);
    }
    else if (newState == MOTOR_HOLDING)
    {
        Herkulex_SetTorque(motorId, 0x60);
        Herkulex_SetLed(motorId, 0x01);
        printf("Motor %u state: HOLDING\r\n", motorId);
    }
    else if (newState == MOTOR_WORKING)
    {
        Herkulex_SetTorque(motorId, 0x60);
        motor->workingLedOn = 1;
        motor->lastLedChange = HAL_GetTick();
        Herkulex_SetLed(motorId, 0x01);
        printf("Motor %u state: WORKING\r\n", motorId);
    }
    else if (newState == MOTOR_BRAKED)
    {
        Herkulex_SetTorque(motorId, 0x40);
        Herkulex_SetLed(motorId, 0x04);
        printf("Motor %u state: BRAKED\r\n", motorId);
    }
}

static void Motor_LedTask(void)
{
    uint32_t now = HAL_GetTick();

    for (uint8_t index = 0; index < MOTOR_COUNT; index++)
    {
        MotorControl *motor = &motors[index];
        uint8_t motorId = motorConfigs[index].id;

        if (!motor->connected)
            continue;

        if (motor->state == MOTOR_STANDBY &&
            now - motor->lastLedChange >= MOTOR_STANDBY_LED_INTERVAL_MS)
        {
            motor->lastLedChange = now;
            motor->standbyLedOn = !motor->standbyLedOn;
            Herkulex_SetLed(motorId, motor->standbyLedOn ? 0x02 : 0x00);
        }
        else if (motor->state == MOTOR_WORKING &&
                 now - motor->lastLedChange >= MOTOR_WORK_LED_INTERVAL_MS)
        {
            motor->lastLedChange = now;
            motor->workingLedOn = !motor->workingLedOn;
            Herkulex_SetLed(motorId, motor->workingLedOn ? 0x01 : 0x00);
        }
    }
}

static void Motor_StartPositionMove(uint8_t motorIndex,
                                    uint16_t position,
                                    uint16_t durationMs)
{
    MotorControl *motor = &motors[motorIndex];

    Herkulex_MoveToPosition(motorConfigs[motorIndex].id,
                            position,
                            durationMs);

    motor->moveTarget = position;
    motor->moveEndTick = HAL_GetTick() + durationMs + 100U;
    motor->moveActive = 1;
}

static void Motor_PositionMoveTask(void)
{
    uint32_t now = HAL_GetTick();

    for (uint8_t index = 0; index < MOTOR_COUNT; index++)
    {
        MotorControl *motor = &motors[index];
        uint8_t motorId = motorConfigs[index].id;

        if (!motor->moveActive || !motor->connected)
            continue;

        if ((int32_t)(now - motor->moveEndTick) < 0)
            continue;

        motor->moveActive = 0;

        if (Herkulex_ReadPositionReliable(motorId, &motor->currentPosition))
        {
            Motor_SetState(index, MOTOR_HOLDING);
            printf("Motor %u movement complete: target=%u, actual=%u\r\n",
                   motorId, motor->moveTarget, motor->currentPosition);
        }
        else
        {
            Motor_SetState(index, MOTOR_BRAKED);
            printf("Motor %u movement result unavailable\r\n", motorId);
        }
    }
}

static void Motor_ConnectionTask(void)
{
    uint32_t now = HAL_GetTick();
    uint8_t index;
    uint8_t motorId;
    MotorControl *motor;

    if (now - lastMotorCheck < MOTOR_CONNECTION_INTERVAL_MS)
        return;

    lastMotorCheck = now;
    index = scanMotorIndex;
    scanMotorIndex = (scanMotorIndex + 1U) % MOTOR_COUNT;

    motorId = motorConfigs[index].id;
    motor = &motors[index];

    if (!motor->connected)
    {
        if (Herkulex_QuickPing(motorId, MOTOR_DISCOVERY_TIMEOUT_MS))
        {
            motor->connected = 1;
            motor->missCount = 0;
            detectedMotor[motorId] = 1;
            printf("Motor %u connected\r\n", motorId);
            Motor_SetState(index, MOTOR_STANDBY);
        }
        return;
    }

    if (Herkulex_ReadPositionReliable(motorId, &motor->currentPosition))
    {
        motor->missCount = 0;
        printf("Motor %u position = %u\r\n",
               motorId, motor->currentPosition);
    }
    else
    {
        motor->missCount++;
        printf("Motor %u response missed (%u/%u)\r\n",
               motorId, motor->missCount, MOTOR_DISCOVERY_MISS_LIMIT);

        if (motor->missCount >= MOTOR_DISCOVERY_MISS_LIMIT)
        {
            motor->connected = 0;
            motor->missCount = 0;
            motor->moveActive = 0;
            detectedMotor[motorId] = 0;
            printf("Motor %u disconnected\r\n", motorId);
        }
    }
}

static void Motor_DiscoveryTask(void)
{
    uint32_t now = HAL_GetTick();
    uint8_t id;
    int8_t configuredIndex;

    if (now - lastDiscoveryCheck < MOTOR_DISCOVERY_INTERVAL_MS)
        return;

    lastDiscoveryCheck = now;
    id = discoveryMotorId;
    configuredIndex = Motor_FindIndex(id);

    if (Herkulex_QuickPing(id, MOTOR_DISCOVERY_TIMEOUT_MS))
    {
        discoveryMissCount[id] = 0;

        if (!detectedMotor[id])
        {
            detectedMotor[id] = 1;

            if (configuredIndex < 0)
                printf("Motor %u detected (not configured)\r\n", id);
        }
    }
    else if (detectedMotor[id])
    {
        discoveryMissCount[id]++;

        if (discoveryMissCount[id] >= MOTOR_DISCOVERY_MISS_LIMIT)
        {
            detectedMotor[id] = 0;
            discoveryMissCount[id] = 0;

            if (configuredIndex < 0)
                printf("Motor %u disconnected (not configured)\r\n", id);
        }
    }

    discoveryMotorId =
        (discoveryMotorId >= DRS_MAX_ID) ? 0U : discoveryMotorId + 1U;
}

static void Motor_InitializeAll(void)
{
    uint8_t startedCount = 0;

    printf("INITIALIZE ALL MOTORS\r\n");

    for (uint8_t index = 0; index < MOTOR_COUNT; index++)
    {
        MotorControl *motor = &motors[index];
        uint8_t motorId = motorConfigs[index].id;
        uint16_t initialPosition = motorConfigs[index].initialPosition;
        long distance;
        long duration;

        if (!motor->connected)
        {
            printf("Motor %u: SKIPPED, not connected\r\n", motorId);
            continue;
        }

        if (initialPosition == MOTOR_INITIAL_POSITION_UNSET)
        {
            printf("Motor %u: SKIPPED, initial position not configured\r\n",
                   motorId);
            continue;
        }

        if (motor->state == MOTOR_WORKING)
        {
            printf("Motor %u: SKIPPED, already moving\r\n", motorId);
            continue;
        }

        if (!Herkulex_ReadPositionReliable(motorId, &motor->currentPosition))
        {
            printf("Motor %u: SKIPPED, position unavailable\r\n", motorId);
            continue;
        }

        if (Motor_IsInPositionDeadZone(motor->currentPosition))
        {
            Motor_PrintDeadZoneWarning(motorId, motor->currentPosition);
            continue;
        }

        distance = labs((long)initialPosition - (long)motor->currentPosition);
        duration = Motor_CalculateMoveDuration(distance);

        Motor_SetState(index, MOTOR_WORKING);
        HAL_Delay(20U);
        Motor_StartPositionMove(index, initialPosition, (uint16_t)duration);

        printf("Motor %u: INITIALIZING from %u to %u\r\n",
               motorId, motor->currentPosition, initialPosition);
        startedCount++;
    }

    printf("Initialization commands started: %u\r\n", startedCount);
}

static void Motor_BrakeAll(void)
{
    uint16_t brakedCount = 0;

    printf("EMERGENCY BRAKE: ALL MOTORS\r\n");

    for (uint8_t index = 0; index < MOTOR_COUNT; index++)
    {
        MotorControl *motor = &motors[index];

        if (!motor->connected)
            continue;

        motor->moveActive = 0;
        Motor_SetState(index, MOTOR_BRAKED);
        brakedCount++;
    }

    for (uint16_t id = 0; id < DRS_ID_COUNT; id++)
    {
        if (!detectedMotor[id] || Motor_FindIndex((uint8_t)id) >= 0)
            continue;

        Herkulex_SetTorque((uint8_t)id, 0x40);
        Herkulex_SetLed((uint8_t)id, 0x04);
        printf("Motor %u state: BRAKED (not configured)\r\n", id);
        brakedCount++;
    }

    printf("Emergency brake applied to %u motor(s)\r\n", brakedCount);
}

static void Motor_PrintAllStatus(void)
{
    printf("ALL MOTOR STATUS\r\n");

    for (uint8_t index = 0; index < MOTOR_COUNT; index++)
    {
        MotorControl *motor = &motors[index];
        uint8_t motorId = motorConfigs[index].id;
        uint8_t statusError;
        uint8_t statusDetail;

        if (!motor->connected)
        {
            printf("Motor %u: NOT_CONNECTED\r\n", motorId);
            continue;
        }

        if (Herkulex_ReadStatus(motorId, &statusError, &statusDetail))
        {
            printf("Motor %u: ERROR=0x%02X, DETAIL=0x%02X\r\n",
                   motorId, statusError, statusDetail);
        }
        else
        {
            printf("Motor %u: STATUS_READ_FAILED\r\n", motorId);
        }
    }
}

static void Motor_PrintAllPositions(void)
{
    printf("ALL MOTOR POSITIONS\r\n");

    for (uint8_t index = 0; index < MOTOR_COUNT; index++)
    {
        MotorControl *motor = &motors[index];
        uint8_t motorId = motorConfigs[index].id;

        if (!motor->connected)
        {
            printf("Motor %u: NOT_CONNECTED\r\n", motorId);
            continue;
        }

        if (Herkulex_ReadPositionReliable(motorId, &motor->currentPosition))
            printf("POSITION,%u,%u\r\n", motorId, motor->currentPosition);
        else
            printf("Motor %u: POSITION_READ_FAILED\r\n", motorId);
    }
}

static long Motor_CalculateMoveDuration(long distance)
{
    long duration = distance * MOTOR_TIME_PER_POSITION_MS;

    if (duration < MOTOR_MIN_MOVE_TIME_MS)
        return MOTOR_MIN_MOVE_TIME_MS;

    if (duration > MOTOR_MAX_MOVE_TIME_MS)
        return MOTOR_MAX_MOVE_TIME_MS;

    return duration;
}

static void Motor_PrintDeadZoneWarning(uint8_t motorId, uint16_t position)
{
    printf("Motor %u REJECTED: current position %u is in the dead zone\r\n",
           motorId, position);
    printf("Position mode is disabled outside 21..1002\r\n");
    printf("Use '%u +' or '%u -' to leave the dead zone, then use '%u s'\r\n",
           motorId, motorId, motorId);
}
