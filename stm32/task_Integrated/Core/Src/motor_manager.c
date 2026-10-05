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

    int16_t internalTemperatureC;
    uint8_t internalTemperatureValid;

    uint8_t recoveryRetryCount;
    uint8_t arrivalWaitActive;
    uint32_t arrivalWaitStartTick;
} MotorControl;

#define MOTOR_INITIAL_POSITION_UNSET 0xFFFFU

// USER CONFIGURATION: Add or remove rows to change the controlled motors.
// USER CONFIGURATION: Each row is {motor ID, initial position}.
// USER CONFIGURATION: Use MOTOR_INITIAL_POSITION_UNSET when no initial position is assigned.
static const MotorConfig motorConfigs[] =
{
    {1U, 512U},
    {2U, 512U},
    {3U, 512U},
    {4U, 512U},
    {5U, 512U}
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
#define MOTOR_SPEED_COMMAND 500
#define MOTOR_MIN_MOVE_TIME_MS 1000L
#define MOTOR_MAX_MOVE_TIME_MS 2800L
#define MOTOR_TIME_PER_POSITION_MS 80L
#define MOTOR_SEGMENT_STEP_RAW 125U
#define MOTOR_POSITION_TOLERANCE_RAW 20U
#define MOTOR_STANDBY_LED_INTERVAL_MS 1000U
#define MOTOR_WORK_LED_INTERVAL_MS 250U
#define MOTOR_POSITION_SETTLE_TIMEOUT_MS   2000U
#define MOTOR_POSITION_RECHECK_INTERVAL_MS 200U
#define MOTOR_AUTO_RECOVERY_RETRY_LIMIT 1U
#define MOTOR_ERROR_CLEAR_DELAY_MS      50U
#define MOTOR_RECOVERY_DELAY_MS         100U

// USER CONFIGURATION: Safety limits for synchronized ("sync"/"si"/SET_MOTOR) segmented moves.
// Added 2026-09 after a field incident where motors that could not complete a
// commanded move kept being re-commanded at full torque forever (no bound existed
// on the sync path, unlike the single-motor path which already has
// MOTOR_AUTO_RECOVERY_RETRY_LIMIT). These limits make the sync path bail out and
// brake instead of retrying indefinitely.
#define SYNC_SEGMENT_PROGRESS_THRESHOLD_RAW 5U
#define SYNC_SEGMENT_MAX_STALL_RETRIES 5U
#define SYNC_SEGMENT_ABSOLUTE_TIMEOUT_MS 20000U

// USER CONFIGURATION: HerkuleX status-error severity classification.
// Added 2026-09 after real testing showed motor 2 reliably reporting
// "Invalid Packet Error" (bit3/0x08) on almost every segment of a move, even
// though the position read in that exact same check was always correct
// (target reached exactly). Treating every non-zero status byte as a hard
// stop (the previous behavior) made this communication-noise bit abort real,
// successful moves - including the safety retract itself.
// Only these bits indicate an actual physical/mechanical hazard and must
// still abort a move immediately: bit0 exceed input voltage, bit1 exceed POT
// limit, bit2 exceed temperature, bit4 overload detected, bit5 driver fault,
// bit6 EEP-REG distorted.
#define HERKULEX_HARD_STATUS_ERROR_MASK 0x77U
// Bit3 (Invalid Packet Error) alone is treated as a communication artifact:
// clear it and keep going instead of aborting, since the position feedback
// read together with it has already been validated as correct.
#define HERKULEX_SOFT_STATUS_ERROR_MASK 0x08U

// USER CONFIGURATION: Fixed deployment sequence for the 4-joint arm.
// Motor 2 = top/outer joint, motor 3 = middle joint, motor 4 = base/bottom joint,
// motor 1 = turret (moved last on deploy, first on retract).
// All angles are RELATIVE and CUMULATIVE from the stowed position captured when
// "deploy" is issued, all in the same rotational direction (negative raw delta).
//
// DEPLOY_RAW_PER_DEGREE is a DATASHEET ESTIMATE (common HerkuleX DRS resolution:
// ~0.325 deg/step -> ~3.077 raw units/degree). It has NOT been empirically
// calibrated on this specific hardware/gearing. Before trusting the absolute
// targets below, verify it: command a small known move (e.g. "2 +100") and
// measure the actual physical angle change, then adjust this constant if needed.
#define DEPLOY_RAW_PER_DEGREE 3.077f

/* Stage 1:  box clearance - motors 3 and 4 rotate 30 deg together.
 * Stage 1b: motor 2 rotates 90 deg afterwards (separate step).
 * Stage 3:  motors 2 + 3 + 4 move together to their final angles.
 * All targets are ABSOLUTE degrees from stowed (the 30 deg of stage 1 are
 * therefore already included in the final angles).                          */
#define DEPLOY_STAGE1_MOTOR2_DEG 20.0f    /* stage 1b: motor 2 alone           */
#define DEPLOY_STAGE1_MOTOR3_DEG 75.0f    /* stage 1: motor 3 + motor 4        */
#define DEPLOY_STAGE1_MOTOR4_DEG 75.0f
#define DEPLOY_STAGE3_MOTOR2_DEG 180.0f   /* stage 3: motor 2 + 3 + 4, final   */
#define DEPLOY_STAGE3_MOTOR3_DEG 180.0f
#define DEPLOY_STAGE3_MOTOR4_DEG 90.0f
#define DEPLOY_SEAT_OVERSHOOT_RAW 20U
#define DEPLOY_SEAT_PUSH_DURATION_MS 800
#define DEPLOY_RETRACT_SETTLE_DURATION_MS 600U


#define DEPLOY_MOTOR_ID_TURRET 1U
#define DEPLOY_MOTOR_ID_TOP    2U
#define DEPLOY_MOTOR_ID_MID    3U
#define DEPLOY_MOTOR_ID_BASE   4U

// USER CONFIGURATION: Expected stowed ("home") positions for motors 2/3/4.
// Before running the fixed stage sequence, "deploy" checks the CURRENT position
// against these. If any motor is off by more than MOTOR_POSITION_TOLERANCE_RAW,
// all three are driven back to these exact values first, and only once that
// succeeds does stage 1 start. This also fixes deploymentHomePosition to a
// known, repeatable reference instead of "wherever the arm happened to be".
#define DEPLOY_STOWED_MOTOR2 784U
#define DEPLOY_STOWED_MOTOR3 706U
#define DEPLOY_STOWED_MOTOR4 500U

// USER CONFIGURATION: Motor 1 (turret).
// DEPLOY_STOWED_MOTOR1 = position before deploy / target at end of retract.
// DEPLOY_FINAL_MOTOR1  = final position at the end of deploy.
#define DEPLOY_STOWED_MOTOR1 580U
#define DEPLOY_FINAL_MOTOR1  60U

typedef enum
{
    DEPLOY_IDLE = 0,
    DEPLOY_MOVING_TO_STOWED,
    DEPLOY_RUNNING_STAGE1,
    DEPLOY_RUNNING_STAGE1B,
    DEPLOY_RUNNING_STAGE3,
    DEPLOY_SEATING,
    DEPLOY_MOTOR1_DEPLOY,
    DEPLOY_RETRACTING,
    DEPLOY_RETRACT_MOTOR1,
    DEPLOY_RETRACT_STAGE_A,
    DEPLOY_RETRACT_STAGE_C,
    DEPLOY_RETRACT_STAGE_D,
    DEPLOY_RETRACT_SETTLING
} DeploymentPhase;

static MotorControl motors[MOTOR_COUNT];
static uint8_t detectedMotor[DRS_ID_COUNT];
static uint8_t discoveryMissCount[DRS_ID_COUNT];
static uint8_t discoveryMotorId;
static uint8_t scanMotorIndex;
static uint8_t lastMissionSucceeded = 0U;
static uint32_t lastDiscoveryCheck;
static uint32_t lastMotorCheck;
/* Multi-motor segmented sync control */
static uint8_t syncSegmentActive;
static uint8_t syncSegmentCount;
static uint8_t syncSegmentIndexes[MOTOR_COUNT];
static uint16_t syncSegmentFinalTargets[MOTOR_COUNT];
static uint16_t syncSegmentCurrentTargets[MOTOR_COUNT];
static uint32_t syncSegmentEndTick;
/* Stall/timeout guard for the synchronized segmented move (see USER CONFIGURATION above). */
static uint8_t syncSegmentStallRetryCount;
static uint16_t syncSegmentPrevPositions[MOTOR_COUNT];
static uint32_t syncSegmentStartTick;
/* Set by Motor_BrakeSyncSegmentMotors() (failure) / cleared on a clean finish,
 * so callers like the deployment sequencer can tell how the last sync move ended. */
static uint8_t syncSegmentLastResultFailed;

/* Fixed deployment sequence state (see USER CONFIGURATION above). */
static DeploymentPhase deploymentPhase;
static uint8_t deploymentStageRetried;
static uint8_t deploymentManualAbort;
static uint16_t deploymentHomePosition[3]; /* [0]=motor2(top) [1]=motor3(mid) [2]=motor4(base) */
static uint32_t deploymentRetractSettleEndTick;
static uint32_t deploymentSeatEndTick;

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
static uint8_t Motor_IsAnyMoveActive(void); // True while any move (single or sync) is in progress, to avoid bus contention.

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
static void Motor_LogToJetson(uint8_t motorId,
                              const char *event,
                              const char *reason,
                              uint16_t target,
                              uint16_t actual,
                              uint8_t statusError,
                              uint8_t statusDetail);

static uint8_t Motor_RecoverStandbyAndRetry(uint8_t motorIndex,
                                            const char *reason,
                                            uint16_t target,
                                            uint16_t actual,
                                            uint8_t statusError,
                                            uint8_t statusDetail);
static void Motor_StopAll(void);
static void Motor_BrakeAll(void); // Applies the emergency brake to every detected motor.
static void Motor_PrintAllStatus(void); // Prints status bytes for all configured motors.
static void Motor_PrintAllPositions(void); // Prints positions for all configured motors.
static long Motor_CalculateMoveDuration(long distance); // Converts position distance into a bounded move time.
static void Motor_PrintDeadZoneWarning(uint8_t motorId,
                                       uint16_t position); // Explains how to leave the dead zone safely.

/* Fixed deployment sequence (motors 1/2/3/4). See USER CONFIGURATION above. */
static uint8_t Deployment_ValidateTarget(uint16_t target);
static void Deployment_NotifyManualAbort(void);
static void Deployment_Start(void);
static void Deployment_StartMoveToStowed(void);
static void Deployment_StartStage1(void);
static void Deployment_StartStage1B(void);
static void Deployment_StartStage3(void);
static void Deployment_StartSeating(void);
static void Deployment_SeatingTask(void);
static void Deployment_StartMotor1(uint16_t target, const char *label);
static void Deployment_StartRetract(void);
static void Deployment_StartRetractSequence(void);
static void Deployment_StartRetractA(void);
static void Deployment_StartRetractC(void);
static void Deployment_StartRetractD(void);
static void Deployment_StartSettle(void);
static void Deployment_SettleTask(void);
static void Deployment_Task(void);

void MotorManager_Init(void)
{
    memset(motors, 0, sizeof(motors));
    memset(detectedMotor, 0, sizeof(detectedMotor));
    memset(discoveryMissCount, 0, sizeof(discoveryMissCount));

    for (uint8_t index = 0; index < MOTOR_COUNT; index++)
        motors[index].state = MOTOR_STANDBY;

    syncSegmentLastResultFailed = 0U;
    deploymentPhase = DEPLOY_IDLE;
    deploymentStageRetried = 0U;
    deploymentManualAbort = 0U;
    deploymentHomePosition[0] = 0U;
    deploymentHomePosition[1] = 0U;
    deploymentHomePosition[2] = 0U;

    printf("Configured motor IDs:");
    for (uint8_t index = 0; index < MOTOR_COUNT; index++)
        printf(" %u", motorConfigs[index].id);
    printf("\r\n");
}

void MotorManager_Task(void)
{
    Motor_PositionMoveTask();
    Deployment_Task();
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

    if (strcmp(input, "deploy") == 0)
    {
        Deployment_Start();
        return;
    }

    if (strcmp(input, "deploy stop") == 0)
    {
        if (deploymentPhase != DEPLOY_IDLE)
        {
            deploymentManualAbort = 1U;
            Motor_BrakeSyncSegmentMotors();
            printf("DEPLOY stop requested\r\n");
        }
        else
        {
            printf("DEPLOY stop ignored: no deployment active\r\n");
        }
        return;
    }

    if (strcmp(input, "retract") == 0)
    {
        Deployment_StartRetractSequence();
        return;
    }

    if (strcmp(input, "retract stop") == 0)
    {
        if (deploymentPhase != DEPLOY_IDLE)
        {
            deploymentManualAbort = 1U;
            Motor_BrakeSyncSegmentMotors();
            printf("RETRACT stop requested\r\n");
        }
        else
        {
            printf("RETRACT stop ignored: no retract active\r\n");
        }
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
        printf("  deploy     Run fixed arm deployment (motors 3/4, 2, then 2/3/4 final, then motor 1)\r\n");
        printf("  deploy stop Abort an active deployment and brake\r\n");
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
        printf("  retract    Run deployment in reverse (motor 1, stage3->2->1->stowed, settle, brake)\r\n");
        printf("  retract stop Abort an active retract and brake\r\n");
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
            Deployment_NotifyManualAbort();
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

uint8_t MotorManager_GetPositionById(uint8_t motorId,
                                     uint16_t *position,
                                     uint8_t *connected)
{
    int8_t motorIndex;

    if (position == NULL || connected == NULL)
    {
        return 0U;
    }

    motorIndex = Motor_FindIndex(motorId);
    if (motorIndex < 0)
    {
        *position = 0U;
        *connected = 0U;
        return 0U;
    }

    *position = motors[(uint8_t)motorIndex].currentPosition;
    *connected = motors[(uint8_t)motorIndex].connected;

    return 1U;
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

static void Motor_LogToJetson(uint8_t motorId,
                              const char *event,
                              const char *reason,
                              uint16_t target,
                              uint16_t actual,
                              uint8_t statusError,
                              uint8_t statusDetail)
{
    printf(">>MOTOR_LOG: id=%u,event=%s,reason=%s,target=%u,actual=%u,status_error=0x%02X,status_detail=0x%02X<<\r\n",
           (unsigned)motorId,
           event,
           reason,
           (unsigned)target,
           (unsigned)actual,
           (unsigned)statusError,
           (unsigned)statusDetail);
}

static uint8_t Motor_RecoverStandbyAndRetry(uint8_t motorIndex,
                                            const char *reason,
                                            uint16_t target,
                                            uint16_t actual,
                                            uint8_t statusError,
                                            uint8_t statusDetail)
{
    MotorControl *motor;
    uint8_t motorId;
    long distance;
    long duration;
    uint16_t requestedTarget;

    if (motorIndex >= MOTOR_COUNT)
    {
        return 0U;
    }

    motor = &motors[motorIndex];
    motorId = motorConfigs[motorIndex].id;

    /*
     * For segmented movement, the real requested target is the final target,
     * not the current segment target.
     */
    requestedTarget = target;

    if (motor->segmentedMoveActive)
    {
        requestedTarget = motor->segmentedFinalTarget;
    }

    Motor_LogToJetson(motorId,
                      "RECOVERY_REQUEST",
                      reason,
                      requestedTarget,
                      actual,
                      statusError,
                      statusDetail);

    if (motor->recoveryRetryCount >= MOTOR_AUTO_RECOVERY_RETRY_LIMIT)
    {
        Motor_LogToJetson(motorId,
                          "RECOVERY_FAILED",
                          "RETRY_LIMIT",
                          requestedTarget,
                          actual,
                          statusError,
                          statusDetail);

        motor->moveActive = 0U;
        motor->segmentedMoveActive = 0U;
        motor->arrivalWaitActive = 0U;
        motor->arrivalWaitStartTick = 0U;

        Motor_SetState(motorIndex, MOTOR_BRAKED);

        return 0U;
    }

    motor->recoveryRetryCount++;

    motor->arrivalWaitActive = 0U;
    motor->arrivalWaitStartTick = 0U;

    /*
     * Clear HerkuleX internal error first.
     */
    Herkulex_ClearError(motorId);
    HAL_Delay(MOTOR_ERROR_CLEAR_DELAY_MS);

    /*
     * Put the motor into standby before retrying.
     */
    Motor_SetState(motorIndex, MOTOR_STANDBY);
    HAL_Delay(MOTOR_RECOVERY_DELAY_MS);

    /*
     * Re-read actual position after clear + standby.
     */
    if (!Herkulex_ReadPositionReliable(motorId, &motor->currentPosition))
    {
        Motor_LogToJetson(motorId,
                          "RECOVERY_FAILED",
                          "POSITION_UNAVAILABLE_AFTER_CLEAR",
                          requestedTarget,
                          actual,
                          statusError,
                          statusDetail);

        motor->moveActive = 0U;
        motor->segmentedMoveActive = 0U;
        motor->arrivalWaitActive = 0U;
        motor->arrivalWaitStartTick = 0U;

        Motor_SetState(motorIndex, MOTOR_BRAKED);

        return 0U;
    }

    if (Motor_IsInPositionDeadZone(motor->currentPosition))
    {
        Motor_LogToJetson(motorId,
                          "RECOVERY_FAILED",
                          "DEAD_ZONE_AFTER_CLEAR",
                          requestedTarget,
                          motor->currentPosition,
                          statusError,
                          statusDetail);

        motor->moveActive = 0U;
        motor->segmentedMoveActive = 0U;
        motor->arrivalWaitActive = 0U;
        motor->arrivalWaitStartTick = 0U;

        Motor_SetState(motorIndex, MOTOR_BRAKED);

        return 0U;
    }

    /*
     * Case 1:
     * This was a segmented movement.
     * Example: original command was 25, current segment target was 748.
     * After recovery, continue toward final target 25 by calculating the next segment.
     */
    if (motor->segmentedMoveActive)
    {
        uint16_t retryTarget;
        long finalError;

        finalError = labs((long)requestedTarget -
                          (long)motor->currentPosition);

        if (finalError <= MOTOR_POSITION_TOLERANCE_RAW)
        {
            Motor_LogToJetson(motorId,
                              "RECOVERY_RESOLVED",
                              reason,
                              requestedTarget,
                              motor->currentPosition,
                              statusError,
                              statusDetail);

            motor->moveActive = 0U;
            motor->segmentedMoveActive = 0U;
            motor->arrivalWaitActive = 0U;
            motor->arrivalWaitStartTick = 0U;

            Motor_SetState(motorIndex, MOTOR_HOLDING);

            return 1U;
        }

        retryTarget = Motor_GetNextSegmentTarget(motor->currentPosition,
                                                 requestedTarget);

        Motor_LogToJetson(motorId,
                          "RETRY_SEGMENT",
                          reason,
                          requestedTarget,
                          motor->currentPosition,
                          statusError,
                          statusDetail);

        printf("Motor %u retry segment: from %u to %u, final=%u\r\n",
               motorId,
               motor->currentPosition,
               retryTarget,
               requestedTarget);

        /*
         * Important:
         * Do NOT call Motor_StartSegmentedPositionMove() here,
         * because it resets recoveryRetryCount.
         */
        Motor_StartPositionSegment(motorIndex, retryTarget);

        return 1U;
    }

    /*
     * Case 2:
     * Normal non-segmented movement.
     * Retry the original target directly.
     */
    distance = labs((long)target - (long)motor->currentPosition);

    if (distance <= MOTOR_POSITION_TOLERANCE_RAW)
    {
        Motor_LogToJetson(motorId,
                          "RECOVERY_RESOLVED",
                          reason,
                          target,
                          motor->currentPosition,
                          statusError,
                          statusDetail);

        motor->moveActive = 0U;
        motor->arrivalWaitActive = 0U;
        motor->arrivalWaitStartTick = 0U;

        Motor_SetState(motorIndex, MOTOR_HOLDING);

        return 1U;
    }

    duration = Motor_CalculateMoveDuration(distance);

    Motor_LogToJetson(motorId,
                      "RETRY_COMMAND",
                      reason,
                      target,
                      motor->currentPosition,
                      statusError,
                      statusDetail);

    printf("Motor %u retry move: from %u to %u in %ld ms\r\n",
           motorId,
           motor->currentPosition,
           target,
           duration);

    Motor_SetState(motorIndex, MOTOR_WORKING);
    HAL_Delay(20U);

    Motor_StartPositionMove(motorIndex,
                            target,
                            (uint16_t)duration);

    return 1U;
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

    /*
     * Give the servo additional time after the nominal movement duration.
     */
    motor->moveEndTick = HAL_GetTick() + durationMs + 300U;

    motor->moveActive = 1U;

    motor->arrivalWaitActive = 0U;
    motor->arrivalWaitStartTick = 0U;
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

    motor->recoveryRetryCount = 0U;
    motor->arrivalWaitActive = 0U;
    motor->arrivalWaitStartTick = 0U;

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

/*
 * True while ANY motor move is in progress (a single-motor move/segment, or a
 * synchronized multi-motor segment). The HerkuleX bus is half-duplex, so the
 * background Motor_ConnectionTask()/Motor_DiscoveryTask() polling must not
 * send its own ping/read packets while a move's own commands and status
 * reads are in flight - doing so causes exactly the intermittent
 * "position read failed" / "response missed" bus contention seen during
 * multi-motor sync moves (e.g. during "deploy").
 */
static uint8_t Motor_IsAnyMoveActive(void)
{
    if (syncSegmentActive)
    {
        return 1U;
    }

    for (uint8_t index = 0; index < MOTOR_COUNT; index++)
    {
        if (motors[index].moveActive || motors[index].segmentedMoveActive)
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
    syncSegmentStallRetryCount = 0U;
    syncSegmentStartTick = 0U;
}

static void Motor_BrakeSyncSegmentMotors(void)
{
    syncSegmentLastResultFailed = 1U;

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

    /*
     * Reset the stall/timeout guard for this new synchronized move.
     * See USER CONFIGURATION block near the top of this file.
     */
    syncSegmentStallRetryCount = 0U;
    syncSegmentStartTick = HAL_GetTick();

    for (uint8_t i = 0U; i < count; i++)
    {
        uint8_t index = indexes[i];

        syncSegmentIndexes[i] = index;
        syncSegmentFinalTargets[i] = finalTargets[i];
        syncSegmentCurrentTargets[i] = finalTargets[i];
        syncSegmentPrevPositions[i] = motors[index].currentPosition;

        motors[index].recoveryRetryCount = 0U;
        motors[index].arrivalWaitActive = 0U;
        motors[index].arrivalWaitStartTick = 0U;

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

        /*
         * Snapshot the position we are starting this segment attempt from,
         * so Motor_SyncSegmentTask() can tell afterwards whether this
         * attempt actually made progress or the motor is stuck.
         */
        syncSegmentPrevPositions[i] = motor->currentPosition;

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
        syncSegmentLastResultFailed = 0U;
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
    uint16_t maxMovedThisAttempt = 0U;

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
        uint16_t movedThisAttempt;

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
            if ((statusError & HERKULEX_HARD_STATUS_ERROR_MASK) != 0x00U)
            {
                printf("SYNC segmented move stopped: motor %u error=0x%02X, detail=0x%02X\r\n",
                       motorId,
                       statusError,
                       statusDetail);

                Motor_BrakeSyncSegmentMotors();
                return;
            }

            if ((statusError & HERKULEX_SOFT_STATUS_ERROR_MASK) != 0x00U)
            {
                printf("Motor %u soft comm error 0x%02X/0x%02X (invalid packet) - "
                       "position already verified OK, clearing and continuing\r\n",
                       motorId,
                       statusError,
                       statusDetail);

                Herkulex_ClearError(motorId);
            }
        }

        finalError = labs((long)syncSegmentFinalTargets[i] -
                          (long)motor->currentPosition);

        if (finalError > MOTOR_POSITION_TOLERANCE_RAW)
        {
            allFinished = 0U;
        }

        /*
         * Track how far this motor actually moved during this attempt
         * (compared to where it stood right before we sent this segment's
         * command). A motor that never moves despite repeated commands is
         * stuck (mechanically overloaded, disconnected mid-move, etc.) and
         * must not keep being re-commanded at full torque forever.
         */
        movedThisAttempt = (uint16_t)labs((long)motor->currentPosition -
                                          (long)syncSegmentPrevPositions[i]);

        if (movedThisAttempt > maxMovedThisAttempt)
        {
            maxMovedThisAttempt = movedThisAttempt;
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
        syncSegmentLastResultFailed = 0U;
        Motor_CancelSyncSegment();
        return;
    }

    /*
     * Safety guard (added 2026-09): the sync path used to retry an
     * unfinished segment forever, at full torque, with no limit. If a
     * motor cannot make meaningful progress after several attempts, or the
     * whole move has been running for too long, stop commanding it and
     * brake everything in this sync group instead of continuing.
     */
    if (maxMovedThisAttempt < SYNC_SEGMENT_PROGRESS_THRESHOLD_RAW)
    {
        syncSegmentStallRetryCount++;
    }
    else
    {
        syncSegmentStallRetryCount = 0U;
    }

    if (syncSegmentStallRetryCount >= SYNC_SEGMENT_MAX_STALL_RETRIES ||
        (now - syncSegmentStartTick) >= SYNC_SEGMENT_ABSOLUTE_TIMEOUT_MS)
    {
        printf("SYNC segmented move ABORTED: no sufficient progress "
               "(stall retries=%u, elapsed=%lums) - braking all involved motors\r\n",
               syncSegmentStallRetryCount,
               (unsigned long)(now - syncSegmentStartTick));

        for (uint8_t i = 0U; i < syncSegmentCount; i++)
        {
            uint8_t index = syncSegmentIndexes[i];
            uint8_t motorId = motorConfigs[index].id;

            Motor_LogToJetson(motorId,
                              "SYNC_ABORTED",
                              "NO_PROGRESS_OR_TIMEOUT",
                              syncSegmentFinalTargets[i],
                              motors[index].currentPosition,
                              0U,
                              0U);
        }

        Motor_BrakeSyncSegmentMotors();
        return;
    }

    HAL_Delay(100U);
    Motor_StartSyncSegment();
}
/*
 * ---------------------------------------------------------------------
 * Fixed deployment sequence (motors 2 = top, 3 = middle, 4 = base, 1 = turret).
 *
 * Stage 1:  motor 3 (30 deg) + motor 4 (30 deg) together.
 * Stage 1b: motor 2 alone (90 deg).
 * Stage 3:  motor 2 + motor 3 + motor 4 together, to their final targets.
 * Seating: push against the end-stops, then brake.
 * Motor 1: moved to DEPLOY_FINAL_MOTOR1 as the very last step.
 *
 * Retract is the exact reverse: motor 1 -> stowed first, then undo stage 3,
 * (motor 2 back to its stage-1b angle of 90 deg, motor 3/4 back to their
 * stage-1 angle of 30 deg), undo stage 1b (motor 2 back to stowed), undo
 * stage 1 (motor 3/4 back to stowed), settle, brake.
 *
 * Each stage is a normal Motor_StartSegmentedSyncMove(), so it already gets
 * the stall/timeout/brake protection above. On top of that, this sequencer
 * adds: retry the whole stage once if it fails, and if the retry also
 * fails, retract ALL THREE motors back to the position captured when
 * "deploy" was issued, then report the failure instead of leaving the arm
 * half-deployed.
 * ---------------------------------------------------------------------
 */

void MotorManager_StartDeployment(void)
{
    Deployment_Start();
}

void MotorManager_StartRetract(void)
{
    Deployment_StartRetractSequence();
}

uint8_t MotorManager_IsMissionActive(void)
{
    return (deploymentPhase != DEPLOY_IDLE) ? 1U : 0U;
}

uint8_t MotorManager_GetLastMissionSucceeded(void)
{
    return lastMissionSucceeded;
}

static uint8_t Deployment_ValidateTarget(uint16_t target)
{
    return (target >= (uint16_t)DRS_HOLD_POSITION_MIN) &&
           (target <= (uint16_t)DRS_HOLD_POSITION_MAX);
}

static void Deployment_NotifyManualAbort(void)
{
    if (deploymentPhase != DEPLOY_IDLE)
    {
        deploymentManualAbort = 1U;
    }
}

/*
 * Single-motor sync move for motor 1 (turret). Used as the last deploy step
 * and as the first retract step.
 */
static void Deployment_StartMotor1(uint16_t target, const char *label)
{
    uint8_t indexes[1];
    uint16_t targets[1];
    int8_t idx = Motor_FindIndex(DEPLOY_MOTOR_ID_TURRET);

    if (idx < 0 || !motors[idx].connected)
    {
        printf("%s ABORTED: motor 1 not configured/connected\r\n", label);
        deploymentPhase = DEPLOY_IDLE;
        return;
    }

    if (!Deployment_ValidateTarget(target))
    {
        printf("%s ABORTED: motor 1 target %u outside safe range 25..998\r\n", label, target);
        deploymentPhase = DEPLOY_IDLE;
        return;
    }

    indexes[0] = (uint8_t)idx;
    targets[0] = target;

    printf("%s: motor 1 -> %u\r\n", label, target);

    Motor_StartSegmentedSyncMove(indexes, targets, 1U);
}

static void Deployment_StartRetractSequence(void)
{
    if (deploymentPhase != DEPLOY_IDLE)
    {
        printf("RETRACT rejected: deployment/retract already active\r\n");
        return;
    }

    lastMissionSucceeded = 0U;

    deploymentStageRetried = 0U;
    deploymentManualAbort = 0U;

    printf("RETRACT: running deployment in reverse (motor 1, final stage, 1b, 1, stowed)\r\n");

    deploymentPhase = DEPLOY_RETRACT_MOTOR1;
    Deployment_StartMotor1((uint16_t)DEPLOY_STOWED_MOTOR1, "RETRACT motor 1");
}

static void Deployment_StartRetractA(void)
{
    uint8_t indexes[3];
    uint16_t targets[3];
    int32_t rawTop;
    int32_t rawMid;
    int32_t rawBase;

    /* Undo stage 3: back to the post-stage-1b positions (motor2 at 90 deg,
     * motor3/4 at 30 deg). Uses the fixed stowed constants, not
     * deploymentHomePosition, so "retract" works standalone even without
     * a deploy earlier in this power cycle. */
    rawTop = (int32_t)DEPLOY_STOWED_MOTOR2 -
             (int32_t)(DEPLOY_STAGE1_MOTOR2_DEG * DEPLOY_RAW_PER_DEGREE + 0.5f);
    rawMid = (int32_t)DEPLOY_STOWED_MOTOR3 -
             (int32_t)(DEPLOY_STAGE1_MOTOR3_DEG * DEPLOY_RAW_PER_DEGREE + 0.5f);
    rawBase = (int32_t)DEPLOY_STOWED_MOTOR4 -
              (int32_t)(DEPLOY_STAGE1_MOTOR4_DEG * DEPLOY_RAW_PER_DEGREE + 0.5f);

    if (rawTop < 0)  rawTop = 0;
    if (rawMid < 0)  rawMid = 0;
    if (rawBase < 0) rawBase = 0;

    targets[0] = (uint16_t)rawTop;
    targets[1] = (uint16_t)rawMid;
    targets[2] = (uint16_t)rawBase;

    if (!Deployment_ValidateTarget(targets[0]) ||
        !Deployment_ValidateTarget(targets[1]) ||
        !Deployment_ValidateTarget(targets[2]))
    {
        printf("RETRACT ABORTED: stage A target outside safe range 25..998 (top=%u, mid=%u, base=%u)\r\n",
               targets[0], targets[1], targets[2]);
        deploymentPhase = DEPLOY_IDLE;
        return;
    }

    indexes[0] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_TOP);
    indexes[1] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_MID);
    indexes[2] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_BASE);

    printf("RETRACT stage A (undo stage 3): motor %u -> %u, motor %u -> %u, motor %u -> %u\r\n",
           DEPLOY_MOTOR_ID_TOP, targets[0], DEPLOY_MOTOR_ID_MID, targets[1], DEPLOY_MOTOR_ID_BASE, targets[2]);

    Motor_StartSegmentedSyncMove(indexes, targets, 3U);
}

static void Deployment_StartRetractC(void)
{
    uint8_t indexes[1];
    uint16_t targets[1];

    /* Undo stage 1b: motor 2 back to stowed. */
    targets[0] = (uint16_t)DEPLOY_STOWED_MOTOR2;

    if (!Deployment_ValidateTarget(targets[0]))
    {
        printf("RETRACT ABORTED: stage C target outside safe range 25..998 (top=%u)\r\n",
               targets[0]);
        deploymentPhase = DEPLOY_IDLE;
        return;
    }

    indexes[0] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_TOP);

    printf("RETRACT stage C (undo stage 1b): motor %u -> %u\r\n",
           DEPLOY_MOTOR_ID_TOP, targets[0]);

    Motor_StartSegmentedSyncMove(indexes, targets, 1U);
}

static void Deployment_StartRetractD(void)
{
    uint8_t indexes[2];
    uint16_t targets[2];

    /* Undo stage 1: motor 3/4 back to stowed. */
    targets[0] = (uint16_t)DEPLOY_STOWED_MOTOR3;
    targets[1] = (uint16_t)DEPLOY_STOWED_MOTOR4;

    if (!Deployment_ValidateTarget(targets[0]) || !Deployment_ValidateTarget(targets[1]))
    {
        printf("RETRACT ABORTED: stage D target outside safe range 25..998 (mid=%u, base=%u)\r\n",
               targets[0], targets[1]);
        deploymentPhase = DEPLOY_IDLE;
        return;
    }

    indexes[0] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_MID);
    indexes[1] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_BASE);

    printf("RETRACT stage D (undo stage 1): motor %u -> %u, motor %u -> %u\r\n",
           DEPLOY_MOTOR_ID_MID, targets[0], DEPLOY_MOTOR_ID_BASE, targets[1]);

    Motor_StartSegmentedSyncMove(indexes, targets, 2U);
}

static void Deployment_StartSettle(void)
{
    uint8_t indexes[3];

    indexes[0] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_TOP);
    indexes[1] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_MID);
    indexes[2] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_BASE);

    printf("RETRACT settling: releasing torque for %u ms to let the arm sag into its stowed rest before braking\r\n",
           (unsigned)DEPLOY_RETRACT_SETTLE_DURATION_MS);

    Motor_SetState(indexes[0], MOTOR_STANDBY);
    Motor_SetState(indexes[1], MOTOR_STANDBY);
    Motor_SetState(indexes[2], MOTOR_STANDBY);

    deploymentRetractSettleEndTick = HAL_GetTick() + DEPLOY_RETRACT_SETTLE_DURATION_MS;
    deploymentPhase = DEPLOY_RETRACT_SETTLING;
}

static void Deployment_SettleTask(void)
{
    uint8_t indexes[3];

    if ((int32_t)(HAL_GetTick() - deploymentRetractSettleEndTick) < 0)
    {
        /* Still settling, torque-free. */
        return;
    }

    indexes[0] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_TOP);
    indexes[1] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_MID);
    indexes[2] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_BASE);

    Motor_SetState(indexes[0], MOTOR_BRAKED);
    Motor_SetState(indexes[1], MOTOR_BRAKED);
    Motor_SetState(indexes[2], MOTOR_BRAKED);

    printf("RETRACT complete: settled and braked at stowed position\r\n");
    lastMissionSucceeded = 1U;
    deploymentPhase = DEPLOY_IDLE;
}

static void Deployment_StartMoveToStowed(void)
{
    uint8_t indexes[4];
    uint16_t targets[4];

    indexes[0] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_TOP);
    indexes[1] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_MID);
    indexes[2] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_BASE);
    indexes[3] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_TURRET);

    targets[0] = (uint16_t)DEPLOY_STOWED_MOTOR2;
    targets[1] = (uint16_t)DEPLOY_STOWED_MOTOR3;
    targets[2] = (uint16_t)DEPLOY_STOWED_MOTOR4;
    targets[3] = (uint16_t)DEPLOY_STOWED_MOTOR1;

    printf("DEPLOY moving to stowed position: motor %u -> %u, motor %u -> %u, motor %u -> %u, motor %u -> %u\r\n",
           DEPLOY_MOTOR_ID_TOP, targets[0],
           DEPLOY_MOTOR_ID_MID, targets[1],
           DEPLOY_MOTOR_ID_BASE, targets[2],
           DEPLOY_MOTOR_ID_TURRET, targets[3]);

    Motor_StartSegmentedSyncMove(indexes, targets, 4U);
}

static void Deployment_Start(void)
{
    int8_t idxTop;
    int8_t idxMid;
    int8_t idxBase;
    int8_t idxTurret;
    uint16_t curTop;
    uint16_t curMid;
    uint16_t curBase;
    uint8_t needsPrecheck;

    if (deploymentPhase != DEPLOY_IDLE)
    {
        printf("DEPLOY rejected: deployment already active\r\n");
        return;
    }

    lastMissionSucceeded = 0U; /* assume failure until a success point proves otherwise */

    if (syncSegmentActive)
    {
        printf("DEPLOY rejected: another sync move is active\r\n");
        return;
    }

    idxTop = Motor_FindIndex(DEPLOY_MOTOR_ID_TOP);
    idxMid = Motor_FindIndex(DEPLOY_MOTOR_ID_MID);
    idxBase = Motor_FindIndex(DEPLOY_MOTOR_ID_BASE);
    idxTurret = Motor_FindIndex(DEPLOY_MOTOR_ID_TURRET);

    if (idxTop < 0 || idxMid < 0 || idxBase < 0 || idxTurret < 0)
    {
        printf("DEPLOY rejected: motor 1/2/3/4 not configured\r\n");
        return;
    }

    if (!motors[idxTop].connected || !motors[idxMid].connected ||
        !motors[idxBase].connected || !motors[idxTurret].connected)
    {
        printf("DEPLOY rejected: motor 1/2/3/4 not all connected\r\n");
        return;
    }

    if (motors[idxTop].state == MOTOR_WORKING ||
        motors[idxMid].state == MOTOR_WORKING ||
        motors[idxBase].state == MOTOR_WORKING ||
        motors[idxTurret].state == MOTOR_WORKING)
    {
        printf("DEPLOY rejected: motor 1/2/3/4 already moving\r\n");
        return;
    }

    if (!Herkulex_ReadPositionReliable(DEPLOY_MOTOR_ID_TOP, &motors[idxTop].currentPosition) ||
        !Herkulex_ReadPositionReliable(DEPLOY_MOTOR_ID_MID, &motors[idxMid].currentPosition) ||
        !Herkulex_ReadPositionReliable(DEPLOY_MOTOR_ID_BASE, &motors[idxBase].currentPosition) ||
        !Herkulex_ReadPositionReliable(DEPLOY_MOTOR_ID_TURRET, &motors[idxTurret].currentPosition))
    {
        printf("DEPLOY rejected: position read failed on motor 1/2/3/4\r\n");
        return;
    }

    curTop = motors[idxTop].currentPosition;
    curMid = motors[idxMid].currentPosition;
    curBase = motors[idxBase].currentPosition;

    /*
     * Deployment always measures its stage angles from the known stowed
     * configuration, not from wherever the arm happens to be right now.
     */
    deploymentHomePosition[0] = (uint16_t)DEPLOY_STOWED_MOTOR2;
    deploymentHomePosition[1] = (uint16_t)DEPLOY_STOWED_MOTOR3;
    deploymentHomePosition[2] = (uint16_t)DEPLOY_STOWED_MOTOR4;

    deploymentStageRetried = 0U;
    deploymentManualAbort = 0U;

    needsPrecheck =
        (labs((long)curTop - (long)DEPLOY_STOWED_MOTOR2) > MOTOR_POSITION_TOLERANCE_RAW) ||
        (labs((long)curMid - (long)DEPLOY_STOWED_MOTOR3) > MOTOR_POSITION_TOLERANCE_RAW) ||
        (labs((long)curBase - (long)DEPLOY_STOWED_MOTOR4) > MOTOR_POSITION_TOLERANCE_RAW) ||
        (labs((long)motors[idxTurret].currentPosition - (long)DEPLOY_STOWED_MOTOR1) > MOTOR_POSITION_TOLERANCE_RAW);

    if (needsPrecheck)
    {
        printf("DEPLOY precheck: motors not at stowed position (top=%u, mid=%u, base=%u, turret=%u) "
               "- moving to stowed (top=%u, mid=%u, base=%u, turret=%u) first\r\n",
               curTop, curMid, curBase, motors[idxTurret].currentPosition,
               deploymentHomePosition[0], deploymentHomePosition[1], deploymentHomePosition[2],
               (unsigned)DEPLOY_STOWED_MOTOR1);

        deploymentPhase = DEPLOY_MOVING_TO_STOWED;
        Deployment_StartMoveToStowed();
    }
    else
    {
        printf("DEPLOY started: already at stowed home top(2)=%u mid(3)=%u base(4)=%u\r\n",
               deploymentHomePosition[0],
               deploymentHomePosition[1],
               deploymentHomePosition[2]);

        deploymentPhase = DEPLOY_RUNNING_STAGE1;
        Deployment_StartStage1();
    }
}

static void Deployment_StartStage1(void)
{
    uint8_t indexes[2];
    uint16_t targets[2];
    int32_t raw[2];

    raw[0] = (int32_t)deploymentHomePosition[1] -
             (int32_t)(DEPLOY_STAGE1_MOTOR3_DEG * DEPLOY_RAW_PER_DEGREE + 0.5f);
    raw[1] = (int32_t)deploymentHomePosition[2] -
             (int32_t)(DEPLOY_STAGE1_MOTOR4_DEG * DEPLOY_RAW_PER_DEGREE + 0.5f);

    for (uint8_t i = 0U; i < 2U; i++)
    {
        if (raw[i] < 0)
        {
            raw[i] = 0;
        }

        targets[i] = (uint16_t)raw[i];
    }

    if (!Deployment_ValidateTarget(targets[0]) || !Deployment_ValidateTarget(targets[1]))
    {
        printf("DEPLOY ABORTED: stage 1 target outside safe range 25..998 (mid=%u, base=%u)\r\n",
               targets[0], targets[1]);
        deploymentPhase = DEPLOY_IDLE;
        return;
    }

    indexes[0] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_MID);
    indexes[1] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_BASE);

    printf("DEPLOY stage 1: motor %u -> %u (%d deg), motor %u -> %u (%d deg)\r\n",
           DEPLOY_MOTOR_ID_MID, targets[0], (int)DEPLOY_STAGE1_MOTOR3_DEG,
           DEPLOY_MOTOR_ID_BASE, targets[1], (int)DEPLOY_STAGE1_MOTOR4_DEG);

    Motor_StartSegmentedSyncMove(indexes, targets, 2U);
}

static void Deployment_StartStage1B(void)
{
    uint8_t indexes[1];
    uint16_t targets[1];
    int32_t raw;

    raw = (int32_t)deploymentHomePosition[0] -
          (int32_t)(DEPLOY_STAGE1_MOTOR2_DEG * DEPLOY_RAW_PER_DEGREE + 0.5f);

    if (raw < 0)
    {
        raw = 0;
    }

    targets[0] = (uint16_t)raw;

    if (!Deployment_ValidateTarget(targets[0]))
    {
        printf("DEPLOY ABORTED: stage 1b target %u for motor %u outside safe range 25..998\r\n",
               targets[0], DEPLOY_MOTOR_ID_TOP);
        deploymentPhase = DEPLOY_IDLE;
        return;
    }

    indexes[0] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_TOP);

    printf("DEPLOY stage 1b: motor %u -> %u (%d deg)\r\n",
           DEPLOY_MOTOR_ID_TOP, targets[0], (int)DEPLOY_STAGE1_MOTOR2_DEG);

    Motor_StartSegmentedSyncMove(indexes, targets, 1U);
}

static void Deployment_StartStage3(void)
{
    uint8_t indexes[3];
    uint16_t targets[3];
    int32_t rawTop;
    int32_t rawMid;
    int32_t rawBase;
    uint16_t targetTop;
    uint16_t targetMid;
    uint16_t targetBase;

    rawTop = (int32_t)deploymentHomePosition[0] -
             (int32_t)(DEPLOY_STAGE3_MOTOR2_DEG * DEPLOY_RAW_PER_DEGREE + 0.5f);
    rawMid = (int32_t)deploymentHomePosition[1] -
             (int32_t)(DEPLOY_STAGE3_MOTOR3_DEG * DEPLOY_RAW_PER_DEGREE + 0.5f);
    rawBase = (int32_t)deploymentHomePosition[2] -
              (int32_t)(DEPLOY_STAGE3_MOTOR4_DEG * DEPLOY_RAW_PER_DEGREE + 0.5f);

    if (rawTop < 0)
    {
        rawTop = 0;
    }

    if (rawMid < 0)
    {
        rawMid = 0;
    }

    if (rawBase < 0)
    {
        rawBase = 0;
    }

    targetTop = (uint16_t)rawTop;
    targetMid = (uint16_t)rawMid;
    targetBase = (uint16_t)rawBase;

    if (!Deployment_ValidateTarget(targetTop) ||
        !Deployment_ValidateTarget(targetMid) ||
        !Deployment_ValidateTarget(targetBase))
    {
        printf("DEPLOY ABORTED: stage 3 target outside safe range 25..998 (top=%u, mid=%u, base=%u)\r\n",
               targetTop, targetMid, targetBase);
        deploymentPhase = DEPLOY_IDLE;
        return;
    }

    indexes[0] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_TOP);
    indexes[1] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_MID);
    indexes[2] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_BASE);
    targets[0] = targetTop;
    targets[1] = targetMid;
    targets[2] = targetBase;

    printf("DEPLOY stage 3 (final): motor %u -> %u, motor %u -> %u, motor %u -> %u "
           "(%d/%d/%d deg from stowed)\r\n",
           DEPLOY_MOTOR_ID_TOP, targetTop,
           DEPLOY_MOTOR_ID_MID, targetMid,
           DEPLOY_MOTOR_ID_BASE, targetBase,
           (int)DEPLOY_STAGE3_MOTOR2_DEG, (int)DEPLOY_STAGE3_MOTOR3_DEG, (int)DEPLOY_STAGE3_MOTOR4_DEG);

    Motor_StartSegmentedSyncMove(indexes, targets, 3U);
}

static void Deployment_StartSeating(void)
{
    uint8_t indexes[3];
    uint8_t ids[3];
    uint16_t targets[3];
    int32_t rawTop;
    int32_t rawMid;
    int32_t rawBase;
    uint16_t targetTop;
    uint16_t targetMid;
    uint16_t targetBase;
    uint32_t now;

    /* Same stage-3 final targets, then push DEPLOY_SEAT_OVERSHOOT_RAW further
     * in the same direction so the joint makes firm contact with its
     * mechanical end-stop despite small calibration inaccuracies. */
    rawTop = (int32_t)deploymentHomePosition[0] -
             (int32_t)(DEPLOY_STAGE3_MOTOR2_DEG * DEPLOY_RAW_PER_DEGREE + 0.5f) -
             (int32_t)DEPLOY_SEAT_OVERSHOOT_RAW;
    rawMid = (int32_t)deploymentHomePosition[1] -
             (int32_t)(DEPLOY_STAGE3_MOTOR3_DEG * DEPLOY_RAW_PER_DEGREE + 0.5f) -
             (int32_t)DEPLOY_SEAT_OVERSHOOT_RAW;
    rawBase = (int32_t)deploymentHomePosition[2] -
              (int32_t)(DEPLOY_STAGE3_MOTOR4_DEG * DEPLOY_RAW_PER_DEGREE + 0.5f) -
              (int32_t)DEPLOY_SEAT_OVERSHOOT_RAW;

    if (rawTop < 0)  rawTop = 0;
    if (rawMid < 0)  rawMid = 0;
    if (rawBase < 0) rawBase = 0;

    targetTop = (uint16_t)rawTop;
    targetMid = (uint16_t)rawMid;
    targetBase = (uint16_t)rawBase;

    if (!Deployment_ValidateTarget(targetTop) ||
        !Deployment_ValidateTarget(targetMid) ||
        !Deployment_ValidateTarget(targetBase))
    {
        /* Overshoot would leave the safe 25..998 range - skip seating and
         * continue directly with the final motor 1 move. */
        printf("DEPLOY: seating overshoot out of safe range (top=%u, mid=%u, base=%u) - skipping seating\r\n",
               targetTop, targetMid, targetBase);
        deploymentStageRetried = 0U;
        deploymentPhase = DEPLOY_MOTOR1_DEPLOY;
        Deployment_StartMotor1((uint16_t)DEPLOY_FINAL_MOTOR1, "DEPLOY motor 1");
        return;
    }

    indexes[0] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_TOP);
    indexes[1] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_MID);
    indexes[2] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_BASE);

    ids[0] = DEPLOY_MOTOR_ID_TOP;
    ids[1] = DEPLOY_MOTOR_ID_MID;
    ids[2] = DEPLOY_MOTOR_ID_BASE;

    targets[0] = targetTop;
    targets[1] = targetMid;
    targets[2] = targetBase;

    printf("DEPLOY seating: pushing motor %u/%u/%u to %u/%u/%u (stage-3 target + %u raw) against end-stops for %u ms\r\n",
           DEPLOY_MOTOR_ID_TOP, DEPLOY_MOTOR_ID_MID, DEPLOY_MOTOR_ID_BASE,
           targetTop, targetMid, targetBase,
           (unsigned)DEPLOY_SEAT_OVERSHOOT_RAW, (unsigned)DEPLOY_SEAT_PUSH_DURATION_MS);

    /* Deliberately bypass Motor_StartSegmentedSyncMove(): its stall/no-progress
     * detection would treat "motor can't move any further" as a failure and
     * trigger a retry/retract here, but that is exactly the expected,
     * successful outcome once the joint is pressed against its end-stop. */
    Motor_SetState(indexes[0], MOTOR_WORKING);
    Motor_SetState(indexes[1], MOTOR_WORKING);
    Motor_SetState(indexes[2], MOTOR_WORKING);

    Herkulex_SyncMoveToPositions(ids, targets, 3U, (uint16_t)DEPLOY_SEAT_PUSH_DURATION_MS);

    now = HAL_GetTick();
    deploymentSeatEndTick = now + (uint32_t)DEPLOY_SEAT_PUSH_DURATION_MS + 100U;
    deploymentPhase = DEPLOY_SEATING;
}

static void Deployment_SeatingTask(void)
{
    uint8_t indexes[3];
    uint32_t now = HAL_GetTick();

    if ((int32_t)(now - deploymentSeatEndTick) < 0)
    {
        /* Still pushing into the end-stops. */
        return;
    }

    indexes[0] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_TOP);
    indexes[1] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_MID);
    indexes[2] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_BASE);

    /* Passive brake instead of the active HOLDING position-servo loop: this
     * is the actual fix for the oscillation, since BRAKED has no correction
     * loop left to hunt/resonate once resting against the mechanical stop. */
    Motor_SetState(indexes[0], MOTOR_BRAKED);
    Motor_SetState(indexes[1], MOTOR_BRAKED);
    Motor_SetState(indexes[2], MOTOR_BRAKED);

    printf("DEPLOY seated against end-stops (BRAKE mode) - now moving motor 1\r\n");

    deploymentStageRetried = 0U;
    deploymentPhase = DEPLOY_MOTOR1_DEPLOY;
    Deployment_StartMotor1((uint16_t)DEPLOY_FINAL_MOTOR1, "DEPLOY motor 1");
}

static void Deployment_StartRetract(void)
{
    uint8_t indexes[3];
    uint16_t targets[3];

    indexes[0] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_TOP);
    indexes[1] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_MID);
    indexes[2] = (uint8_t)Motor_FindIndex(DEPLOY_MOTOR_ID_BASE);

    targets[0] = deploymentHomePosition[0];
    targets[1] = deploymentHomePosition[1];
    targets[2] = deploymentHomePosition[2];

    printf("DEPLOY RETRACT: returning motor 2/3/4 to stowed home position (%u/%u/%u)\r\n",
           targets[0], targets[1], targets[2]);

    deploymentPhase = DEPLOY_RETRACTING;

    Motor_StartSegmentedSyncMove(indexes, targets, 3U);
}

static void Deployment_Task(void)
{
    if (deploymentPhase == DEPLOY_IDLE)
    {
        return;
    }

    if (deploymentPhase == DEPLOY_SEATING)
    {
        if (deploymentManualAbort)
        {
            printf("DEPLOY aborted by manual stop/brake command during seating\r\n");
            deploymentPhase = DEPLOY_IDLE;
            deploymentManualAbort = 0U;
            return;
        }

        Deployment_SeatingTask();
        return;
    }

    if (deploymentPhase == DEPLOY_RETRACT_SETTLING)
    {
        if (deploymentManualAbort)
        {
            printf("RETRACT aborted by manual stop/brake command during settle\r\n");
            deploymentPhase = DEPLOY_IDLE;
            deploymentManualAbort = 0U;
            return;
        }

        Deployment_SettleTask();
        return;
    }

    if (syncSegmentActive)
    {
        /* Current stage (or retract) still running. */
        return;
    }

    if (deploymentManualAbort)
    {
        printf("DEPLOY aborted by manual stop/brake command\r\n");
        deploymentPhase = DEPLOY_IDLE;
        deploymentManualAbort = 0U;
        return;
    }

    if (syncSegmentLastResultFailed)
    {
        if (deploymentPhase == DEPLOY_RETRACTING)
        {
            printf("DEPLOY CRITICAL: retract to stowed position FAILED - manual inspection required\r\n");
            Motor_LogToJetson(0U, "DEPLOY_RETRACT_FAILED", "SYNC_FAILED", 0U, 0U, 0U, 0U);
            deploymentPhase = DEPLOY_IDLE;
            return;
        }

        if (deploymentPhase == DEPLOY_MOVING_TO_STOWED)
        {
            if (!deploymentStageRetried)
            {
                deploymentStageRetried = 1U;
                printf("DEPLOY precheck move to stowed failed, retrying once\r\n");
                Deployment_StartMoveToStowed();
                return;
            }

            printf("DEPLOY ABORTED: could not reach stowed position - deployment not started\r\n");
            Motor_LogToJetson(0U, "DEPLOY_PRECHECK_FAILED", "RETRY_LIMIT", 0U, 0U, 0U, 0U);
            deploymentPhase = DEPLOY_IDLE;
            return;
        }

        if (!deploymentStageRetried)
        {
            deploymentStageRetried = 1U;
            printf("DEPLOY stage failed, retrying once\r\n");

            switch (deploymentPhase)
            {
                case DEPLOY_RUNNING_STAGE1:
                    Deployment_StartStage1();
                    break;
                case DEPLOY_RUNNING_STAGE1B:
                    Deployment_StartStage1B();
                    break;
                case DEPLOY_RUNNING_STAGE3:
                    Deployment_StartStage3();
                    break;
                case DEPLOY_MOTOR1_DEPLOY:
                    Deployment_StartMotor1((uint16_t)DEPLOY_FINAL_MOTOR1, "DEPLOY motor 1 retry");
                    break;
                case DEPLOY_RETRACT_MOTOR1:
                    Deployment_StartMotor1((uint16_t)DEPLOY_STOWED_MOTOR1, "RETRACT motor 1 retry");
                    break;
                case DEPLOY_RETRACT_STAGE_A:
                    Deployment_StartRetractA();
                    break;
                case DEPLOY_RETRACT_STAGE_C:
                    Deployment_StartRetractC();
                    break;
                case DEPLOY_RETRACT_STAGE_D:
                    Deployment_StartRetractD();
                    break;
                default:
                    break;
            }
            return;
        }
        if (deploymentPhase == DEPLOY_RETRACT_MOTOR1 ||
            deploymentPhase == DEPLOY_RETRACT_STAGE_A ||
            deploymentPhase == DEPLOY_RETRACT_STAGE_C ||
            deploymentPhase == DEPLOY_RETRACT_STAGE_D)
        {
            printf("RETRACT CRITICAL: retract sequence failed twice - motors braked in place, manual inspection required\r\n");
            Motor_LogToJetson(0U, "RETRACT_FAILED", "RETRY_LIMIT", 0U, 0U, 0U, 0U);
            deploymentPhase = DEPLOY_IDLE;
            return;
        }
        printf("DEPLOY stage failed twice - retracting to stowed position\r\n");
        Motor_LogToJetson(0U, "DEPLOY_STAGE_FAILED", "RETRY_LIMIT", 0U, 0U, 0U, 0U);
        Deployment_StartRetract();
        return;
    }

    /* Current stage succeeded, advance to the next one. */
    deploymentStageRetried = 0U;

    switch (deploymentPhase)
    {
        case DEPLOY_MOVING_TO_STOWED:
            printf("DEPLOY precheck complete: motors at stowed position\r\n");
            deploymentPhase = DEPLOY_RUNNING_STAGE1;
            Deployment_StartStage1();
            break;

        case DEPLOY_RUNNING_STAGE1:
            printf("DEPLOY stage 1 complete\r\n");
            deploymentPhase = DEPLOY_RUNNING_STAGE1B;
            Deployment_StartStage1B();
            break;

        case DEPLOY_RUNNING_STAGE1B:
            printf("DEPLOY stage 1b complete\r\n");
            deploymentPhase = DEPLOY_RUNNING_STAGE3;
            Deployment_StartStage3();
            break;

        case DEPLOY_RUNNING_STAGE3:
            printf("DEPLOY stage 3 complete - seating against end-stops\r\n");
            Deployment_StartSeating();
            break;

        case DEPLOY_MOTOR1_DEPLOY:
            printf("DEPLOY complete: arm seated, motor 1 in final position\r\n");
            lastMissionSucceeded = 1U;
            deploymentPhase = DEPLOY_IDLE;
            break;

        case DEPLOY_RETRACTING:
            printf("DEPLOY retract complete: motor 2/3/4 back at stowed position\r\n");
            deploymentPhase = DEPLOY_IDLE;
            break;

        case DEPLOY_RETRACT_MOTOR1:
            printf("RETRACT motor 1 complete\r\n");
            deploymentPhase = DEPLOY_RETRACT_STAGE_A;
            Deployment_StartRetractA();
            break;

        case DEPLOY_RETRACT_STAGE_A:
            printf("RETRACT stage A complete (undo stage 3)\r\n");
            deploymentPhase = DEPLOY_RETRACT_STAGE_C;
            Deployment_StartRetractC();
            break;

        case DEPLOY_RETRACT_STAGE_C:
            printf("RETRACT stage C complete (undo stage 1b)\r\n");
            deploymentPhase = DEPLOY_RETRACT_STAGE_D;
            Deployment_StartRetractD();
            break;

        case DEPLOY_RETRACT_STAGE_D:
            printf("RETRACT stage D complete (undo stage 1, at stowed position)\r\n");
            Deployment_StartSettle();
            break;

        default:
            deploymentPhase = DEPLOY_IDLE;
            break;
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
            if (Motor_RecoverStandbyAndRetry(index,
                                             "POSITION_READ_FAILED",
                                             motor->moveTarget,
                                             0U,
                                             0U,
                                             0U))
            {
                continue;
            }

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
                if ((statusError & HERKULEX_HARD_STATUS_ERROR_MASK) != 0x00U)
                {
                    printf("Motor %u error detected: error=0x%02X, detail=0x%02X\r\n",
                           motorId,
                           statusError,
                           statusDetail);

                    if (Motor_RecoverStandbyAndRetry(index,
                                                     "STATUS_ERROR",
                                                     motor->moveTarget,
                                                     motor->currentPosition,
                                                     statusError,
                                                     statusDetail))
                    {
                        continue;
                    }

                    continue;
                }

                if ((statusError & HERKULEX_SOFT_STATUS_ERROR_MASK) != 0x00U)
                {
                    printf("Motor %u soft comm error 0x%02X/0x%02X (invalid packet) - "
                           "position already verified OK, clearing and continuing\r\n",
                           motorId,
                           statusError,
                           statusDetail);

                    Herkulex_ClearError(motorId);
                }
            }
        }

        {
            long targetError;

            targetError = labs((long)motor->moveTarget -
                               (long)motor->currentPosition);

            if (targetError > MOTOR_POSITION_TOLERANCE_RAW)
            {
                /*
                 * Do not trigger recovery immediately.
                 * The motor may still be settling or the position feedback may lag.
                 */
                if (!motor->arrivalWaitActive)
                {
                    motor->arrivalWaitActive = 1U;
                    motor->arrivalWaitStartTick = now;

                    /*
                     * Keep this motor active so Motor_PositionMoveTask()
                     * will check it again later.
                     */
                    motor->moveActive = 1U;
                    motor->moveEndTick = now + MOTOR_POSITION_RECHECK_INTERVAL_MS;

                    printf("Motor %u waiting for target: target=%u, actual=%u, error=%ld\r\n",
                           motorId,
                           motor->moveTarget,
                           motor->currentPosition,
                           targetError);

                    continue;
                }

                if (now - motor->arrivalWaitStartTick < MOTOR_POSITION_SETTLE_TIMEOUT_MS)
                {
                    /*
                     * Keep rechecking until settle timeout expires.
                     */
                    motor->moveActive = 1U;
                    motor->moveEndTick = now + MOTOR_POSITION_RECHECK_INTERVAL_MS;

                    printf("Motor %u still settling: target=%u, actual=%u, error=%ld\r\n",
                           motorId,
                           motor->moveTarget,
                           motor->currentPosition,
                           targetError);

                    continue;
                }

                /*
                 * Only now treat it as real POSITION_NOT_REACHED.
                 */
                if (Motor_RecoverStandbyAndRetry(index,
                                                 "POSITION_NOT_REACHED",
                                                 motor->moveTarget,
                                                 motor->currentPosition,
                                                 0U,
                                                 0U))
                {
                    continue;
                }

                continue;
            }
            else
            {
                /*
                 * Target reached.
                 */
                motor->arrivalWaitActive = 0U;
                motor->arrivalWaitStartTick = 0U;
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

    /*
     * Never share the half-duplex HerkuleX bus with an in-progress move.
     * See Motor_IsAnyMoveActive() for why.
     */
    if (Motor_IsAnyMoveActive())
    {
        return;
    }

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
        uint8_t temperatureRaw;

        motor->missCount = 0;

        if (Herkulex_ReadTemperatureRawReliable(motorId, &temperatureRaw))
        {
            motor->internalTemperatureC =
                Herkulex_ConvertTemperatureRawToC(temperatureRaw);

            motor->internalTemperatureValid = 1U;
        }
        else
        {
            motor->internalTemperatureValid = 0U;
        }
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
            motor->moveActive = 0U;
            motor->segmentedMoveActive = 0U;
            motor->internalTemperatureValid = 0U;
            motor->arrivalWaitActive = 0U;
            motor->arrivalWaitStartTick = 0U;
            motor->recoveryRetryCount = 0U;
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

    /*
     * Never share the half-duplex HerkuleX bus with an in-progress move.
     * This task normally fires every MOTOR_DISCOVERY_INTERVAL_MS (10ms) and
     * sweeps every possible ID, so during a several-second sync move it
     * would otherwise ping motors 2/3/4 dozens of times while they are
     * mid-move, corrupting the move's own command/response traffic.
     */
    if (Motor_IsAnyMoveActive())
    {
        return;
    }

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

    Deployment_NotifyManualAbort();
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

    Deployment_NotifyManualAbort();
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

uint8_t MotorManager_GetInternalTemperatureCById(uint8_t motorId,
                                                 int16_t *temperatureC,
                                                 uint8_t *connected)
{
    int8_t index;
    MotorControl *motor;

    if (temperatureC == NULL || connected == NULL)
    {
        return 0U;
    }

    index = Motor_FindIndex(motorId);
    if (index < 0)
    {
        return 0U;
    }

    motor = &motors[index];

    *connected = motor->connected;

    if (!motor->connected || !motor->internalTemperatureValid)
    {
        return 0U;
    }

    *temperatureC = motor->internalTemperatureC;

    return 1U;
}