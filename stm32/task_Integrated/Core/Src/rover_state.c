#include "rover_state.h"

#include "motor_manager.h"
#include "rover_housekeeping.h"
#include "rover_protocol.h"

#include <stdio.h>
#include <string.h>

// USER CONFIGURATION: Mission lifecycle timing. PLACEHOLDERS - tune to your
// real Jetson boot/shutdown behavior before relying on this unattended.
#define ROVERSTATE_SETUP_TIMEOUT_MS     20000U
#define ROVERSTATE_SHUTDOWN_WAIT_MS     30000U  /* must be long enough for a clean Jetson shutdown */
#define ROVERSTATE_SHUTDOWN_MAX_RETRIES 2U

// USER CONFIGURATION: PMOS power-switch pins (HIGH = switch ON). Order here
// is also the SETUP power-up sequence order, with
// ROVERSTATE_PMOS_STEP_DELAY_MS between each step.
#define ROVERSTATE_PMOS_STEP_DELAY_MS 500U

typedef struct
{
    GPIO_TypeDef *port;
    uint16_t pin;
    const char *label;
} PowerSwitchDef;

static const PowerSwitchDef pmosDefs[PMOS_COUNT] =
{
    { GPIOB, GPIO_PIN_4,  "PMOS11 7.4V motor bus" },
    { GPIOB, GPIO_PIN_5,  "PMOS12 5V bus" },
    { GPIOB, GPIO_PIN_13, "PMOS21 12V Jetson bus" },
    { GPIOB, GPIO_PIN_14, "PMOS22 12V bus" }
};

RobotState currentState = STATE_IDLE;
FaultCode activeFault = FAULT_NONE;

static uint32_t setupEntryTick = 0U;
static uint32_t shutdownCycleStartTick = 0U;
static uint32_t shutdownWaitEndTick = 0U;
static uint8_t shutdownRetryCount = 0U;

static uint8_t setupPowerStepIndex = 0U;
static uint32_t setupPowerStepNextTick = 0U;
static uint8_t setupPowerSequenceDone = 0U;

static void RoverState_OnEnter(RobotState state);
static void RoverState_ShutdownTask(void);
static void RoverState_PowerSequenceTask(void);
static void RoverState_PowerSwitchesOff(void);
static uint8_t FaultIsCritical(FaultCode fault);

const char* StateToString(void)
{
    switch (currentState)
    {
        case STATE_IDLE:            return "IDLE";
        case STATE_SETUP:           return "SETUP";
        case STATE_MAST_DEPLOYMENT: return "MAST_DEPLOYMENT";
        case STATE_STANDBY:         return "STANDBY";
        case STATE_RETRACT:         return "RETRACT";
        case STATE_SHUTDOWN:        return "SHUTDOWN";
        case STATE_SAFE:            return "SAFE";
        default:                    return "UNKNOWN";
    }
}

const char* FaultToString(void)
{
    switch (activeFault)
    {
        case FAULT_NONE:           return "NONE";
        case FAULT_VOLTAGE_HIGH:   return "VOLTAGE_HIGH";
        case FAULT_TEMP_HIGH:      return "TEMP_HIGH";
        case FAULT_CURRENT_HIGH:   return "CURRENT_HIGH";
        case FAULT_COMM_TIMEOUT:   return "COMM_TIMEOUT";
        case FAULT_JETSON_ERROR:   return "JETSON_ERROR";
        case FAULT_UNKNOWN:        return "UNKNOWN";
        case FAULT_SETUP_TIMEOUT:  return "SETUP_TIMEOUT";
        case FAULT_DEPLOY_FAILED:  return "DEPLOY_FAILED";
        case FAULT_RETRACT_FAILED: return "RETRACT_FAILED";
        default:                   return "UNKNOWN";
    }
}

uint8_t RoverState_IsLocked(void)
{
    return currentState == STATE_SAFE;
}

uint8_t RoverState_SetState(RobotState state)
{
    RobotState previous = currentState;

    if (currentState == STATE_SAFE && state != STATE_SAFE)
    {
        return 0U;
    }

    currentState = state;

    if (previous != state)
    {
        RoverState_OnEnter(state);
    }

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

    if (strcmp(stateText, "SETUP") == 0)
    {
        return RoverState_SetState(STATE_SETUP);
    }

    if (strcmp(stateText, "MAST_DEPLOYMENT") == 0)
    {
        return RoverState_SetState(STATE_MAST_DEPLOYMENT);
    }

    if (strcmp(stateText, "STANDBY") == 0)
    {
        return RoverState_SetState(STATE_STANDBY);
    }

    if (strcmp(stateText, "RETRACT") == 0)
    {
        return RoverState_SetState(STATE_RETRACT);
    }

    if (strcmp(stateText, "SHUTDOWN") == 0)
    {
        return RoverState_SetState(STATE_SHUTDOWN);
    }

    if (strcmp(stateText, "SAFE") == 0)
    {
        return RoverState_SetState(STATE_SAFE);
    }

    return 0U;
}

static uint8_t FaultIsCritical(FaultCode fault)
{
    switch (fault)
    {
        case FAULT_COMM_TIMEOUT:
        case FAULT_SETUP_TIMEOUT:
            return 0U; /* non-critical -> STANDBY */
        default:
            return 1U; /* critical -> SAFE */
    }
}

void ReportFault(FaultCode fault)
{
    activeFault = fault;

    printf(">>NACK, %s<<\r\n", FaultToString());

    if (FaultIsCritical(fault))
    {
        printf("System is locked in SAFE mode. Use RECOVER after resolving the fault.\r\n");
        RoverState_SetState(STATE_SAFE);
    }
    else
    {
        printf("System moved to STANDBY (non-critical fault) - no lock, further commands accepted.\r\n");
        RoverState_SetState(STATE_STANDBY);
    }

    PrintState();
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

void RoverState_InstructJetson(const char *stateName)
{
    /*
     * One-shot instruction to the Jetson, deliberately decoupled from our
     * own currentState - the Jetson can have its own internal sub-states
     * (e.g. MAPPING -> TRACKING) that the STM never adopts itself.
     */
    printf(">>SET_STATE %s<<\r\n", stateName);
}

void RoverState_SetPowerSwitch(PowerSwitchId id, uint8_t on)
{
    if (id >= PMOS_COUNT)
    {
        return;
    }

    HAL_GPIO_WritePin(pmosDefs[id].port, pmosDefs[id].pin,
                       on ? GPIO_PIN_SET : GPIO_PIN_RESET);

    printf("Power switch %s turned %s\r\n", pmosDefs[id].label, on ? "ON" : "OFF");
}

static void RoverState_PowerSequenceTask(void)
{
    if (setupPowerSequenceDone)
    {
        return;
    }

    if ((int32_t)(HAL_GetTick() - setupPowerStepNextTick) < 0)
    {
        return;
    }

    RoverState_SetPowerSwitch((PowerSwitchId)setupPowerStepIndex, 1U);
    setupPowerStepIndex++;

    if (setupPowerStepIndex >= PMOS_COUNT)
    {
        setupPowerSequenceDone = 1U;
        setupEntryTick = HAL_GetTick(); /* Jetson-ALIVE-Timeout erst jetzt starten */
        printf("SETUP: power sequence complete, waiting for Jetson ALIVE\r\n");
    }
    else
    {
        setupPowerStepNextTick = HAL_GetTick() + ROVERSTATE_PMOS_STEP_DELAY_MS;
    }
}

static void RoverState_PowerSwitchesOff(void)
{
    for (uint8_t i = 0U; i < PMOS_COUNT; i++)
    {
        RoverState_SetPowerSwitch((PowerSwitchId)i, 0U);
    }
}

void RoverState_InitPowerSwitches(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    uint32_t pinMask = 0U;

    __HAL_RCC_GPIOB_CLK_ENABLE();

    for (uint8_t i = 0U; i < PMOS_COUNT; i++)
    {
        pinMask |= pmosDefs[i].pin;
    }

    GPIO_InitStruct.Pin = pinMask;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

    HAL_GPIO_WritePin(GPIOB, (uint16_t)pinMask, GPIO_PIN_RESET);
}

static void RoverState_OnEnter(RobotState state)
{
    switch (state)
    {
        case STATE_SETUP:
            setupPowerStepIndex = 0U;
            setupPowerSequenceDone = 0U;
            setupPowerStepNextTick = HAL_GetTick();
            break;

        case STATE_MAST_DEPLOYMENT:
            MotorManager_StartDeployment();
            break;

        case STATE_RETRACT:
            MotorManager_StartRetract();
            break;

        case STATE_SHUTDOWN:
            shutdownRetryCount = 0U;
            RoverState_InstructJetson("SHUTDOWN");
            shutdownCycleStartTick = HAL_GetTick();
            shutdownWaitEndTick = shutdownCycleStartTick + ROVERSTATE_SHUTDOWN_WAIT_MS;
            break;

        case STATE_SAFE:
            printf("SAFE: braking all motors\r\n");
            MotorManager_ExecuteCommand("b");
            break;

        default:
            break;
    }
}

static void RoverState_ShutdownTask(void)
{
    if ((int32_t)(HAL_GetTick() - shutdownWaitEndTick) < 0)
    {
        return; /* still waiting out this cycle */
    }

    if (!RoverProtocol_HasAliveSince(shutdownCycleStartTick))
    {
        printf("SHUTDOWN: no ALIVE since shutdown instruction - Jetson appears down, cutting power\r\n");
        RoverState_PowerSwitchesOff();
        RoverState_SetState(STATE_IDLE);
        return;
    }

    if (shutdownRetryCount >= ROVERSTATE_SHUTDOWN_MAX_RETRIES)
    {
        printf("SHUTDOWN: Jetson still alive after max retries - forcing power cut (procedural failure)\r\n");
        RoverState_PowerSwitchesOff();
        RoverState_SetState(STATE_IDLE);
        return;
    }

    shutdownRetryCount++;
    printf("SHUTDOWN: Jetson still alive, retry %u/%u - resending shutdown instruction\r\n",
           (unsigned)shutdownRetryCount, (unsigned)ROVERSTATE_SHUTDOWN_MAX_RETRIES);
    RoverState_InstructJetson("SHUTDOWN");
    shutdownCycleStartTick = HAL_GetTick();
    shutdownWaitEndTick = shutdownCycleStartTick + ROVERSTATE_SHUTDOWN_WAIT_MS;
}

void RoverState_AutoCheckTask(void)
{
    FaultCode detected;

    if (activeFault != FAULT_NONE)
    {
        return;
    }

    if (RoverHousekeeping_CheckThresholds(&detected))
    {
        ReportFault(detected);
    }
}

void RoverState_ModeTask(void)
{
    static uint8_t missionWasActive = 0U;
    uint8_t missionActiveNow = MotorManager_IsMissionActive();

    switch (currentState)
    {
        case STATE_SETUP:
            RoverState_PowerSequenceTask();

            if (!setupPowerSequenceDone)
            {
                break; /* noch beim Hochfahren der Spannungsschienen */
            }

            if (RoverProtocol_HasAliveSince(setupEntryTick))
            {
                printf("SETUP complete: Jetson alive - starting mast deployment\r\n");
                RoverState_SetState(STATE_MAST_DEPLOYMENT);
            }
            else if ((int32_t)(HAL_GetTick() - setupEntryTick) > (int32_t)ROVERSTATE_SETUP_TIMEOUT_MS)
            {
                printf("SETUP failed: no ALIVE from Jetson within timeout\r\n");
                ReportFault(FAULT_SETUP_TIMEOUT);
            }
            break;

        case STATE_MAST_DEPLOYMENT:
            if (missionWasActive && !missionActiveNow)
            {
                if (MotorManager_GetLastMissionSucceeded())
                {
                    printf("MAST_DEPLOYMENT complete - instructing Jetson to start mapping\r\n");
                    RoverState_InstructJetson("MAPPING");
                    RoverState_SetState(STATE_IDLE);
                }
                else
                {
                    printf("MAST_DEPLOYMENT failed\r\n");
                    ReportFault(FAULT_DEPLOY_FAILED);
                }
            }
            break;

        case STATE_RETRACT:
            if (missionWasActive && !missionActiveNow)
            {
                if (MotorManager_GetLastMissionSucceeded())
                {
                    printf("RETRACT complete - proceeding to shutdown\r\n");
                    RoverState_SetState(STATE_SHUTDOWN);
                }
                else
                {
                    printf("RETRACT failed\r\n");
                    ReportFault(FAULT_RETRACT_FAILED);
                }
            }
            break;

        case STATE_SHUTDOWN:
            RoverState_ShutdownTask();
            break;

        default:
            break;
    }

    missionWasActive = missionActiveNow;
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

        case STATE_SETUP:
            if (now - lastTick >= 100U)
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
                    HAL_GPIO_WritePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin, GPIO_PIN_SET);
                }
                else
                {
                    HAL_GPIO_WritePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin, GPIO_PIN_RESET);
                }

                mastBlinkStep = (mastBlinkStep + 1U) % 8U;
            }
            break;

        case STATE_RETRACT:
            if (now - lastTick >= 600U)
            {
                lastTick = now;
                HAL_GPIO_TogglePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin);
            }
            break;

        case STATE_SHUTDOWN:
            if (now - lastTick >= 150U)
            {
                lastTick = now;
                HAL_GPIO_TogglePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin);
            }
            break;

        case STATE_SAFE:
        default:
            HAL_GPIO_WritePin(LED_GREEN_GPIO_Port, LED_GREEN_Pin, GPIO_PIN_RESET);
            break;
    }
}