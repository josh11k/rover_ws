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
    uint8_t segmentedMoveActive;
    uint16_t segmentedFinalTarget;
} MotorControl;

#define MOTOR_INITIAL_POSITION_UNSET 0xFFFFU

// USER CONFIGURATION: Add or remove rows to change the controlled motors.
// USER CONFIGURATION: Each row is {motor ID, initial position}.
// USER CONFIGURATION: Use MOTOR_INITIAL_POSITION_UNSET when no initial position is assigned.
static const MotorConfig motorConfigs[] =
{
    {1U, 511U},
    {2U, 512U},
    {3U, 513U},
	{4U, 514U},
	{5U, 515U},
    {6U, 516U}
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
#define DRS_HOLD_POSITION_MIN 25L
#define DRS_HOLD_POSITION_MAX 998L

// USER CONFIGURATION: These values control movement speed and LED timing.
#define MOTOR_SPEED_COMMAND 80
#define MOTOR_MIN_MOVE_TIME_MS 1000L
#define MOTOR_MAX_MOVE_TIME_MS 2800L
#define MOTOR_TIME_PER_POSITION_MS 80L
#define MOTOR_SEGMENT_STEP_RAW 125U
#define MOTOR_POSITION_TOLERANCE_RAW 20U
#define MOTOR_STANDBY_LED_INTERVAL_MS 1000U
#define MOTOR_WORK_LED_INTERVAL_MS 250U

static MotorControl motors[MOTOR_COUNT];
static uint8_t detectedMotor[DRS_ID_COUNT];
static uint8_t discoveryMissCount[DRS_ID_COUNT];
static uint8_t discoveryMotorId;
static uint8_t scanMotorIndex;
static uint32_t lastDiscoveryCheck;
static uint32_t lastMotorCheck;
/* Multi-motor segmented sync control */
static uint8_t syncSegmentActive;
static uint8_t syncSegmentCount;
static uint8_t syncSegmentIndexes[MOTOR_COUNT];
static uint16_t syncSegmentFinalTargets[MOTOR_COUNT];
static uint16_t syncSegmentCurrentTargets[MOTOR_COUNT];
static uint32_t syncSegmentEndTick;

static int8_t Motor_FindIndex(uint8_t motorId); // Finds the configured array entry for one motor ID.
static uint8_t Motor_IsInPositionDeadZone(uint16_t position); // Reports whether position mode is unsafe at this position.
static void Motor_SetState(uint8_t motorIndex,
                           MotorState newState); // Applies torque and LED behavior for one state.
static void Motor_LedTask(void); // Updates the standby and working LED blink patterns.
static void Motor_StartPositionMove(uint8_t motorIndex,
                                    uint16_t position,
                                    uint16_t durationMs); // Starts and tracks one position movement.
static uint16_t Motor_GetNextSegmentTarget(uint16_t currentPosition,
                                           uint16_t finalTarget);
static void Motor_StartPositionSegment(uint8_t motorIndex,
                                       uint16_t targetPosition);
static void Motor_StartSegmentedPositionMove(uint8_t motorIndex,
                                             uint16_t finalTarget);
static uint8_t Motor_IsSyncSegmentMotor(uint8_t motorIndex);

static void Motor_CancelSyncSegment(void);

static void Motor_BrakeSyncSegmentMotors(void);

static void Motor_StartSegmentedSyncMove(const uint8_t *indexes,
                                         const uint16_t *finalTargets,
                                         uint8_t count);

static void Motor_StartSyncSegment(void);

static void Motor_SyncSegmentTask(void);
static void Motor_PositionMoveTask(void); // Completes tracked position movements.
static void Motor_ConnectionTask(void); // Monitors configured motors for connection changes.
static void Motor_DiscoveryTask(void); // Scans all valid DRS IDs, including unconfigured motors.
static void Motor_InitializeAll(void); // Sends every configured motor to its assigned initial position.
static void Motor_SyncInitializeAll(void);
static void Motor_ExecuteSyncCommand(const char *input);
static void Motor_ExecuteMixedCommand(const char *input);
static void Motor_StopAll(void);
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
    /*long distance;*/
    /*long duration;*/
    uint8_t motorId;
    int8_t motorIndex;
    const char *command;
    MotorControl *motor;
    uint8_t statusError;
    uint8_t statusDetail;

    if (strcmp(input, "s") == 0)
    {
        Motor_StopAll();
        return;
    }

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

    if (strcmp(input, "si") == 0)
    {
        Motor_SyncInitializeAll();
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

    if (strncmp(input, "sync ", 5) == 0)
    {
        Motor_ExecuteSyncCommand(input + 5);
        return;
    }

    if (strncmp(input, "mix ", 4) == 0)
    {
        Motor_ExecuteMixedCommand(input + 4);
        return;
    }

    parsedMotorId = strtol(input, &idEnd, 10);

    if (idEnd == input || *idEnd != ' ')
    {
        printf("Invalid command format\r\n");
        printf("Global commands:\r\n");
        printf("  s          Stop all motors / standby\r\n");
        printf("  b          Emergency brake all motors\r\n");
        printf("  i          Initialize all motors\r\n");
        printf("  si         Synchronized initialize all motors\r\n");
        printf("  sync       Synchronized position move, example: sync 1 500 2 520\r\n");
        printf("  pos        Read all motor positions\r\n");
        printf("  status     Read all motor status\r\n");
        printf("Single motor commands:\r\n");
        printf("  <id> +300  Move relative +300\r\n");
        printf("  <id> -300  Move relative -300\r\n");
        printf("  <id> 500   Move to absolute position 500\r\n");
        printf("  <id> +     Continuous positive speed\r\n");
        printf("  <id> -     Continuous negative speed\r\n");
        printf("  <id> s     Stop one motor / standby\r\n");
        printf("  <id> b     Brake one motor\r\n");
        printf("  <id> pos   Read one motor position\r\n");
        printf("  <id> status Read one motor status\r\n");
        printf("  <id> clear Clear one motor error\r\n");

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

    if (strcmp(command, "clear") == 0)
    {
        Herkulex_ClearError(motorId);
        HAL_Delay(50U);

        printf("Motor %u error cleared\r\n", motorId);
        return;
    }

    if (motor->state == MOTOR_WORKING &&
        strcmp(command, "s") != 0 &&
        strcmp(command, "b") != 0 &&
        strcmp(command, "pos") != 0 &&
        strcmp(command, "status") != 0 &&
        strcmp(command, "clear") != 0)
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
    	if (syncSegmentActive)
    	{
    		Motor_BrakeSyncSegmentMotors();
    	    printf("Active sync segmented move cancelled by motor %u brake\r\n",
    	    		motorId);
    	    return;
    	}
        motor->moveActive = 0;
        motor->segmentedMoveActive = 0U;
        Motor_SetState((uint8_t)motorIndex, MOTOR_BRAKED);
        printf("Motor %u emergency brake applied\r\n", motorId);
        return;
    }

    if (strcmp(command, "s") == 0)
    {
        if (syncSegmentActive)
        {
            Motor_StopAll();
            printf("Active sync segmented move cancelled by motor %u stop\r\n",
                   motorId);
            return;
        }
    	motor->moveActive = 0;
        motor->segmentedMoveActive = 0U;
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
        printf("Motor %u REJECTED: target %ld is outside holding range 25..998\r\n",
               motorId, target);/*21...1002*/
        return;
    }

    Motor_StartSegmentedPositionMove((uint8_t)motorIndex,
                                     (uint16_t)target);
    /*
    distance = labs(target - (long)motor->currentPosition);
    duration = Motor_CalculateMoveDuration(distance);

    Motor_SetState((uint8_t)motorIndex, MOTOR_WORKING);
    HAL_Delay(20U);
    Motor_StartPositionMove((uint8_t)motorIndex,
                            (uint16_t)target,
                            (uint16_t)duration);

    printf("Motor %u moving from %u to %ld in %ld ms\r\n",
           motorId, motor->currentPosition, target, duration);
    */
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

static uint16_t Motor_GetNextSegmentTarget(uint16_t currentPosition,
                                           uint16_t finalTarget)
{
    if (finalTarget > currentPosition)
    {
        uint32_t next = (uint32_t)currentPosition + MOTOR_SEGMENT_STEP_RAW;

        if (next > finalTarget)
        {
            next = finalTarget;
        }

        return (uint16_t)next;
    }
    else
    {
        if ((currentPosition - finalTarget) > MOTOR_SEGMENT_STEP_RAW)
        {
            return (uint16_t)(currentPosition - MOTOR_SEGMENT_STEP_RAW);
        }

        return finalTarget;
    }
}

static void Motor_StartPositionSegment(uint8_t motorIndex,
                                       uint16_t targetPosition)
{
    MotorControl *motor = &motors[motorIndex];
    uint8_t motorId = motorConfigs[motorIndex].id;
    long distance;
    long duration;

    distance = labs((long)targetPosition - (long)motor->currentPosition);
    duration = Motor_CalculateMoveDuration(distance);

    Motor_SetState(motorIndex, MOTOR_WORKING);

    HAL_Delay(20U);

    Motor_StartPositionMove(motorIndex,
                            targetPosition,
                            (uint16_t)duration);

    printf("Motor %u segment move: from %u to %u in %ld ms\r\n",
           motorId,
           motor->currentPosition,
           targetPosition,
           duration);
}

static void Motor_StartSegmentedPositionMove(uint8_t motorIndex,
                                             uint16_t finalTarget)
{
    MotorControl *motor = &motors[motorIndex];
    uint8_t motorId = motorConfigs[motorIndex].id;
    uint16_t firstTarget;

    motor->segmentedMoveActive = 1U;
    motor->segmentedFinalTarget = finalTarget;

    firstTarget = Motor_GetNextSegmentTarget(motor->currentPosition,
                                             finalTarget);

    printf("Motor %u segmented move started: current=%u, final=%u, step=%u\r\n",
           motorId,
           motor->currentPosition,
           finalTarget,
           MOTOR_SEGMENT_STEP_RAW);

    Motor_StartPositionSegment(motorIndex, firstTarget);
}

static uint8_t Motor_IsSyncSegmentMotor(uint8_t motorIndex)
{
    if (!syncSegmentActive)
    {
        return 0U;
    }

    for (uint8_t i = 0U; i < syncSegmentCount; i++)
    {
        if (syncSegmentIndexes[i] == motorIndex)
        {
            return 1U;
        }
    }

    return 0U;
}

static void Motor_CancelSyncSegment(void)
{
    syncSegmentActive = 0U;
    syncSegmentCount = 0U;
}

static void Motor_BrakeSyncSegmentMotors(void)
{
    for (uint8_t i = 0U; i < syncSegmentCount; i++)
    {
        uint8_t index = syncSegmentIndexes[i];
        MotorControl *motor = &motors[index];

        motor->moveActive = 0U;
        motor->segmentedMoveActive = 0U;

        if (motor->connected)
        {
            Motor_SetState(index, MOTOR_BRAKED);
        }
    }

    Motor_CancelSyncSegment();
}

static void Motor_StartSegmentedSyncMove(const uint8_t *indexes,
                                         const uint16_t *finalTargets,
                                         uint8_t count)
{
    if (indexes == NULL ||
        finalTargets == NULL ||
        count == 0U ||
        count > MOTOR_COUNT)
    {
        printf("SYNC segmented move rejected: invalid input\r\n");
        return;
    }

    if (syncSegmentActive)
    {
        printf("SYNC segmented move rejected: another sync move is active\r\n");
        return;
    }

    syncSegmentActive = 1U;
    syncSegmentCount = count;

    for (uint8_t i = 0U; i < count; i++)
    {
        uint8_t index = indexes[i];

        syncSegmentIndexes[i] = index;
        syncSegmentFinalTargets[i] = finalTargets[i];
        syncSegmentCurrentTargets[i] = finalTargets[i];

        motors[index].moveActive = 0U;
        motors[index].segmentedMoveActive = 0U;
        motors[index].segmentedFinalTarget = finalTargets[i];
    }

    printf("SYNC segmented move started: motors=%u, step=%u\r\n",
           count,
           MOTOR_SEGMENT_STEP_RAW);

    Motor_StartSyncSegment();
}

static void Motor_StartSyncSegment(void)
{
    uint8_t ids[MOTOR_COUNT];
    uint16_t targets[MOTOR_COUNT];
    long maxDistance = 0L;
    long duration;
    uint32_t now;

    if (!syncSegmentActive || syncSegmentCount == 0U)
    {
        return;
    }

    for (uint8_t i = 0U; i < syncSegmentCount; i++)
    {
        uint8_t index = syncSegmentIndexes[i];
        MotorControl *motor = &motors[index];
        uint8_t motorId = motorConfigs[index].id;
        uint16_t nextTarget;
        long distance;

        if (!motor->connected)
        {
            printf("SYNC segmented move stopped: motor %u not connected\r\n",
                   motorId);
            Motor_BrakeSyncSegmentMotors();
            return;
        }

        if (!Herkulex_ReadPositionReliable(motorId, &motor->currentPosition))
        {
            printf("SYNC segmented move stopped: motor %u position unavailable\r\n",
                   motorId);
            Motor_BrakeSyncSegmentMotors();
            return;
        }

        if (Motor_IsInPositionDeadZone(motor->currentPosition))
        {
            Motor_PrintDeadZoneWarning(motorId, motor->currentPosition);
            Motor_BrakeSyncSegmentMotors();
            return;
        }

        nextTarget = Motor_GetNextSegmentTarget(motor->currentPosition,
                                                syncSegmentFinalTargets[i]);

        ids[i] = motorId;
        targets[i] = nextTarget;
        syncSegmentCurrentTargets[i] = nextTarget;

        distance = labs((long)nextTarget - (long)motor->currentPosition);

        if (distance > maxDistance)
        {
            maxDistance = distance;
        }

        printf("Motor %u sync segment: %u -> %u, final=%u\r\n",
               motorId,
               motor->currentPosition,
               nextTarget,
               syncSegmentFinalTargets[i]);
    }

    if (maxDistance == 0L)
    {
        for (uint8_t i = 0U; i < syncSegmentCount; i++)
        {
            Motor_SetState(syncSegmentIndexes[i], MOTOR_HOLDING);
        }

        printf("SYNC segmented move finished\r\n");
        Motor_CancelSyncSegment();
        return;
    }

    duration = Motor_CalculateMoveDuration(maxDistance);
    now = HAL_GetTick();

    for (uint8_t i = 0U; i < syncSegmentCount; i++)
    {
        uint8_t index = syncSegmentIndexes[i];
        MotorControl *motor = &motors[index];

        Motor_SetState(index, MOTOR_WORKING);

        motor->moveActive = 0U;
        motor->segmentedMoveActive = 0U;
        motor->moveTarget = syncSegmentCurrentTargets[i];
        motor->moveEndTick = now + (uint32_t)duration + 100U;
    }

    syncSegmentEndTick = now + (uint32_t)duration + 100U;

    Herkulex_SyncMoveToPositions(ids,
                                 targets,
                                 syncSegmentCount,
                                 (uint16_t)duration);

    printf("SYNC segment command sent to %u motor(s), duration=%ld ms\r\n",
           syncSegmentCount,
           duration);
}

static void Motor_SyncSegmentTask(void)
{
    uint32_t now;
    uint8_t allFinished = 1U;

    if (!syncSegmentActive)
    {
        return;
    }

    now = HAL_GetTick();

    if ((int32_t)(now - syncSegmentEndTick) < 0)
    {
        return;
    }

    for (uint8_t i = 0U; i < syncSegmentCount; i++)
    {
        uint8_t index = syncSegmentIndexes[i];
        MotorControl *motor = &motors[index];
        uint8_t motorId = motorConfigs[index].id;
        uint8_t statusError;
        uint8_t statusDetail;
        long finalError;

        if (!Herkulex_ReadPositionReliable(motorId, &motor->currentPosition))
        {
            printf("SYNC segmented move stopped: motor %u position read failed\r\n",
                   motorId);
            Motor_BrakeSyncSegmentMotors();
            return;
        }

        printf("Motor %u sync segment complete: target=%u, actual=%u\r\n",
               motorId,
               motor->moveTarget,
               motor->currentPosition);

        if (Herkulex_ReadStatus(motorId, &statusError, &statusDetail))
        {
            if (statusError != 0x00U)
            {
                printf("SYNC segmented move stopped: motor %u error=0x%02X, detail=0x%02X\r\n",
                       motorId,
                       statusError,
                       statusDetail);

                Motor_BrakeSyncSegmentMotors();
                return;
            }
        }

        finalError = labs((long)syncSegmentFinalTargets[i] -
                          (long)motor->currentPosition);

        if (finalError > MOTOR_POSITION_TOLERANCE_RAW)
        {
            allFinished = 0U;
        }
    }

    if (allFinished)
    {
        for (uint8_t i = 0U; i < syncSegmentCount; i++)
        {
            uint8_t index = syncSegmentIndexes[i];

            motors[index].moveActive = 0U;
            motors[index].segmentedMoveActive = 0U;

            Motor_SetState(index, MOTOR_HOLDING);
        }

        printf("SYNC segmented move finished\r\n");
        Motor_CancelSyncSegment();
    }
    else
    {
        HAL_Delay(100U);
        Motor_StartSyncSegment();
    }
}

static void Motor_PositionMoveTask(void)
{
	uint32_t now;

	Motor_SyncSegmentTask();

	now = HAL_GetTick();

    for (uint8_t index = 0; index < MOTOR_COUNT; index++)
    {
        MotorControl *motor = &motors[index];
        uint8_t motorId = motorConfigs[index].id;

        if (Motor_IsSyncSegmentMotor(index))
        {
            continue;
        }

        if (!motor->moveActive || !motor->connected)
        {
            continue;
        }

        if ((int32_t)(now - motor->moveEndTick) < 0)
        {
            continue;
        }

        motor->moveActive = 0;

        if (!Herkulex_ReadPositionReliable(motorId, &motor->currentPosition))
        {
            motor->segmentedMoveActive = 0U;

            Motor_SetState(index, MOTOR_BRAKED);

            printf("Motor %u movement result unavailable\r\n", motorId);
            continue;
        }

        printf("Motor %u movement complete: target=%u, actual=%u\r\n",
               motorId,
               motor->moveTarget,
               motor->currentPosition);

        {
            uint8_t statusError;
            uint8_t statusDetail;

            if (Herkulex_ReadStatus(motorId, &statusError, &statusDetail))
            {
                if (statusError != 0x00U)
                {
                    printf("Motor %u segmented move stopped: error=0x%02X, detail=0x%02X\r\n",
                           motorId,
                           statusError,
                           statusDetail);

                    motor->segmentedMoveActive = 0U;

                    Motor_SetState(index, MOTOR_BRAKED);
                    continue;
                }
            }
        }

        if (motor->segmentedMoveActive)
        {
            long finalError;

            finalError = labs((long)motor->segmentedFinalTarget -
                              (long)motor->currentPosition);

            if (finalError <= MOTOR_POSITION_TOLERANCE_RAW)
            {
                printf("Motor %u segmented move finished: final=%u, actual=%u\r\n",
                       motorId,
                       motor->segmentedFinalTarget,
                       motor->currentPosition);

                motor->segmentedMoveActive = 0U;

                Motor_SetState(index, MOTOR_HOLDING);
            }
            else
            {
                uint16_t nextTarget;

                nextTarget = Motor_GetNextSegmentTarget(motor->currentPosition,
                                                        motor->segmentedFinalTarget);

                HAL_Delay(100U);

                Motor_StartPositionSegment(index, nextTarget);
            }
        }
        else
        {
            Motor_SetState(index, MOTOR_HOLDING);
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
        /*
        printf("Motor %u position = %u\r\n",
               motorId, motor->currentPosition);
        */
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
            motor->segmentedMoveActive = 0U;
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

static void Motor_SyncInitializeAll(void)
{
    uint16_t targets[MOTOR_COUNT];
    uint8_t indexes[MOTOR_COUNT];
    uint8_t syncCount = 0U;

    printf("SYNC INITIALIZE ALL MOTORS\r\n");

    for (uint8_t index = 0; index < MOTOR_COUNT; index++)
    {
        MotorControl *motor = &motors[index];
        uint8_t motorId = motorConfigs[index].id;
        uint16_t initialPosition = motorConfigs[index].initialPosition;

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

        indexes[syncCount] = index;
        targets[syncCount] = initialPosition;
        syncCount++;

        printf("Motor %u: SYNC TARGET from %u to %u\r\n",
               motorId,
               motor->currentPosition,
               initialPosition);
    }

    if (syncCount == 0U)
    {
        printf("No motors available for sync initialize\r\n");
        return;
    }

    Motor_StartSegmentedSyncMove(indexes,
                                 targets,
                                 syncCount);
}

static void Motor_ExecuteSyncCommand(const char *input)
{
    uint16_t targets[MOTOR_COUNT];
    uint8_t indexes[MOTOR_COUNT];
    uint8_t used[MOTOR_COUNT] = {0};

    uint8_t count = 0U;
    const char *cursor = input;
    char *endPtr;

    printf("SYNC MOVE\r\n");

    while (*cursor != '\0')
    {
        long parsedId;
        long parsedTarget;
        int8_t motorIndex;
        MotorControl *motor;
        /*long distance;*/

        while (*cursor == ' ')
        {
            cursor++;
        }

        if (*cursor == '\0')
        {
            break;
        }

        parsedId = strtol(cursor, &endPtr, 10);

        if (endPtr == cursor ||
            parsedId < 0L ||
            parsedId > DRS_MAX_ID)
        {
            printf("SYNC rejected: invalid motor ID\r\n");
            return;
        }

        cursor = endPtr;

        while (*cursor == ' ')
        {
            cursor++;
        }

        if (*cursor == '\0')
        {
            printf("SYNC rejected: target missing for motor %ld\r\n",
                   parsedId);
            return;
        }

        if (*cursor == '+' || *cursor == '-')
        {
            printf("SYNC rejected: use absolute target position only\r\n");
            printf("Example: sync 1 510 2 520\r\n");
            return;
        }

        parsedTarget = strtol(cursor, &endPtr, 10);

        if (endPtr == cursor)
        {
            printf("SYNC rejected: invalid target for motor %ld\r\n",
                   parsedId);
            return;
        }

        cursor = endPtr;

        if (parsedTarget < DRS_HOLD_POSITION_MIN ||
            parsedTarget > DRS_HOLD_POSITION_MAX)
        {
            printf("SYNC rejected: motor %ld target %ld outside holding range 25..998\r\n",
                   parsedId,
                   parsedTarget);/*21...1002*/
            return;
        }

        motorIndex = Motor_FindIndex((uint8_t)parsedId);

        if (motorIndex < 0)
        {
            printf("SYNC rejected: unknown motor ID %ld\r\n",
                   parsedId);
            return;
        }

        if (used[(uint8_t)motorIndex])
        {
            printf("SYNC rejected: duplicate motor ID %ld\r\n",
                   parsedId);
            return;
        }

        motor = &motors[motorIndex];

        if (!motor->connected)
        {
            printf("SYNC rejected: motor %ld not connected\r\n",
                   parsedId);
            return;
        }

        if (motor->state == MOTOR_WORKING)
        {
            printf("SYNC rejected: motor %ld already moving\r\n",
                   parsedId);
            return;
        }

        if (!Herkulex_ReadPositionReliable((uint8_t)parsedId,
                                           &motor->currentPosition))
        {
            printf("SYNC rejected: motor %ld position unavailable\r\n",
                   parsedId);
            return;
        }

        if (Motor_IsInPositionDeadZone(motor->currentPosition))
        {
            Motor_PrintDeadZoneWarning((uint8_t)parsedId,
                                       motor->currentPosition);
            return;
        }

        if (count >= MOTOR_COUNT)
        {
            printf("SYNC rejected: too many motors\r\n");
            return;
        }

        /*
        distance = labs(parsedTarget - (long)motor->currentPosition);

        if (distance > maxDistance)
        {
            maxDistance = distance;
        }
		*/

        /*ids[count] = (uint8_t)parsedId;*/
        targets[count] = (uint16_t)parsedTarget;
        indexes[count] = (uint8_t)motorIndex;
        used[(uint8_t)motorIndex] = 1U;

        printf("Motor %ld: %u -> %ld\r\n",
               parsedId,
               motor->currentPosition,
               parsedTarget);

        count++;
    }

    if (count == 0U)
    {
        printf("SYNC rejected: no motors specified\r\n");
        return;
    }

    Motor_StartSegmentedSyncMove(indexes,
                                 targets,
                                 count);
}

static void Motor_ExecuteMixedCommand(const char *input)
{
    HerkulexJogCommand jogCommands[MOTOR_COUNT];
    uint8_t indexes[MOTOR_COUNT];
    uint8_t used[MOTOR_COUNT] = {0};

    uint8_t count = 0U;
    long maxDistance = 0L;

    const char *cursor = input;
    char *endPtr;

    printf("MIXED MOVE\r\n");

    if (syncSegmentActive)
    {
        printf("MIX rejected: sync segmented move is active\r\n");
        return;
    }

    while (*cursor != '\0')
    {
        long parsedId;
        int8_t motorIndex;
        MotorControl *motor;
        uint8_t motorId;

        while (*cursor == ' ')
        {
            cursor++;
        }

        if (*cursor == '\0')
        {
            break;
        }

        parsedId = strtol(cursor, &endPtr, 10);

        if (endPtr == cursor ||
            parsedId < 0L ||
            parsedId > DRS_MAX_ID)
        {
            printf("MIX rejected: invalid motor ID\r\n");
            return;
        }

        cursor = endPtr;

        while (*cursor == ' ')
        {
            cursor++;
        }

        if (*cursor == '\0')
        {
            printf("MIX rejected: command missing for motor %ld\r\n",
                   parsedId);
            return;
        }

        motorId = (uint8_t)parsedId;
        motorIndex = Motor_FindIndex(motorId);

        if (motorIndex < 0)
        {
            printf("MIX rejected: unknown motor ID %u\r\n", motorId);
            return;
        }

        if (used[(uint8_t)motorIndex])
        {
            printf("MIX rejected: duplicate motor ID %u\r\n", motorId);
            return;
        }

        motor = &motors[motorIndex];

        if (!motor->connected)
        {
            printf("MIX rejected: motor %u not connected\r\n", motorId);
            return;
        }

        if (motor->state == MOTOR_WORKING)
        {
            printf("MIX rejected: motor %u already moving\r\n", motorId);
            return;
        }

        if (count >= MOTOR_COUNT)
        {
            printf("MIX rejected: too many motors\r\n");
            return;
        }

        if (*cursor == '+' && (*(cursor + 1) == '\0' || *(cursor + 1) == ' '))
        {
            jogCommands[count].id = motorId;
            jogCommands[count].mode = HERKULEX_JOG_SPEED;
            jogCommands[count].value = MOTOR_SPEED_COMMAND;
            jogCommands[count].led = 0x08U;      /* blue */

            printf("Motor %u: MIX continuous positive speed\r\n", motorId);

            cursor++;
        }
        else if (*cursor == '-' && (*(cursor + 1) == '\0' || *(cursor + 1) == ' '))
        {
            jogCommands[count].id = motorId;
            jogCommands[count].mode = HERKULEX_JOG_SPEED;
            jogCommands[count].value = -MOTOR_SPEED_COMMAND;
            jogCommands[count].led = 0x08U;      /* blue */

            printf("Motor %u: MIX continuous negative speed\r\n", motorId);

            cursor++;
        }
        else
        {
            long target;

            if (!Herkulex_ReadPositionReliable(motorId, &motor->currentPosition))
            {
                printf("MIX rejected: motor %u position unavailable\r\n",
                       motorId);
                return;
            }

            if (Motor_IsInPositionDeadZone(motor->currentPosition))
            {
                Motor_PrintDeadZoneWarning(motorId, motor->currentPosition);
                return;
            }

            if (*cursor == '+' || *cursor == '-')
            {
                long relativeMove;

                relativeMove = strtol(cursor, &endPtr, 10);

                if (endPtr == cursor)
                {
                    printf("MIX rejected: invalid relative command for motor %u\r\n",
                           motorId);
                    return;
                }

                target = (long)motor->currentPosition + relativeMove;
                cursor = endPtr;

                printf("Motor %u: MIX relative %+ld, from %u to %ld\r\n",
                       motorId,
                       relativeMove,
                       motor->currentPosition,
                       target);
            }
            else
            {
                target = strtol(cursor, &endPtr, 10);

                if (endPtr == cursor)
                {
                    printf("MIX rejected: invalid target for motor %u\r\n",
                           motorId);
                    return;
                }

                cursor = endPtr;

                printf("Motor %u: MIX absolute from %u to %ld\r\n",
                       motorId,
                       motor->currentPosition,
                       target);
            }

            if (target < DRS_HOLD_POSITION_MIN ||
                target > DRS_HOLD_POSITION_MAX)
            {
                printf("MIX rejected: motor %u target %ld outside holding range\r\n",
                       motorId,
                       target);
                return;
            }

            {
                long distance;

                distance = labs(target - (long)motor->currentPosition);

                if (distance > maxDistance)
                {
                    maxDistance = distance;
                }
            }

            jogCommands[count].id = motorId;
            jogCommands[count].mode = HERKULEX_JOG_POSITION;
            jogCommands[count].value = (int16_t)target;
            jogCommands[count].led = 0x04U;      /* green */

            indexes[count] = (uint8_t)motorIndex;
        }

        used[(uint8_t)motorIndex] = 1U;
        indexes[count] = (uint8_t)motorIndex;
        count++;
    }

    if (count == 0U)
    {
        printf("MIX rejected: no motor command specified\r\n");
        return;
    }

    {
        long duration;

        if (maxDistance == 0L)
        {
            duration = MOTOR_MIN_MOVE_TIME_MS;
        }
        else
        {
            duration = Motor_CalculateMoveDuration(maxDistance);
        }

        for (uint8_t i = 0U; i < count; i++)
        {
            uint8_t index = indexes[i];
            MotorControl *motor = &motors[index];

            Motor_SetState(index, MOTOR_WORKING);

            motor->moveActive = 0U;
            motor->segmentedMoveActive = 0U;

            if (jogCommands[i].mode == HERKULEX_JOG_POSITION)
            {
                motor->moveTarget = (uint16_t)jogCommands[i].value;
                motor->moveEndTick = HAL_GetTick() + (uint32_t)duration + 100U;
                motor->moveActive = 1U;
            }
        }

        Herkulex_SyncJogMixed(jogCommands,
                              count,
                              (uint16_t)duration);

        printf("MIX command sent to %u motor(s), duration=%ld ms\r\n",
               count,
               duration);
    }
}

static void Motor_StopAll(void)
{
    uint16_t stoppedCount = 0;

    Motor_CancelSyncSegment();

    printf("STOP: ALL CONFIGURED MOTORS\r\n");

    for (uint8_t index = 0; index < MOTOR_COUNT; index++)
    {
        MotorControl *motor = &motors[index];
        uint8_t motorId = motorConfigs[index].id;

        if (!motor->connected)
        {
            printf("Motor %u: SKIPPED, not connected\r\n", motorId);
            continue;
        }

        motor->moveActive = 0;
        motor->segmentedMoveActive = 0U;
        Motor_SetState(index, MOTOR_STANDBY);
        stoppedCount++;

        HAL_Delay(10U);
    }

    printf("Stop applied to %u motor(s)\r\n", stoppedCount);
}

static void Motor_BrakeAll(void)
{
    uint16_t brakedCount = 0;

    Motor_CancelSyncSegment();

    printf("EMERGENCY BRAKE: ALL MOTORS\r\n");

    for (uint8_t index = 0; index < MOTOR_COUNT; index++)
    {
        MotorControl *motor = &motors[index];

        if (!motor->connected)
            continue;

        motor->moveActive = 0;
        motor->segmentedMoveActive = 0U;
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
    printf("Position mode is disabled outside 25..998\r\n");/*21...1002*/
    printf("Use '%u +' or '%u -' to leave the dead zone, then use '%u s'\r\n",
           motorId, motorId, motorId);
}
