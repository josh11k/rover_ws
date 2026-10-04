#ifndef INC_ROVER_STATE_H_
#define INC_ROVER_STATE_H_

#include "main.h"
#include <stdint.h>

typedef enum
{
    STATE_IDLE = 0,
    STATE_SETUP,
    STATE_MAST_DEPLOYMENT,
    STATE_STANDBY,
    STATE_RETRACT,
    STATE_SHUTDOWN,
    STATE_SAFE
} RobotState;

typedef enum
{
    FAULT_NONE = 0,
    FAULT_VOLTAGE_HIGH,
    FAULT_TEMP_HIGH,
    FAULT_CURRENT_HIGH,
    FAULT_COMM_TIMEOUT,
    FAULT_JETSON_ERROR,
    FAULT_UNKNOWN,
    FAULT_SETUP_TIMEOUT,
    FAULT_DEPLOY_FAILED,
    FAULT_RETRACT_FAILED
} FaultCode;

extern RobotState currentState;
extern FaultCode activeFault;

const char* StateToString(void);
const char* FaultToString(void);
uint8_t RoverState_SetState(RobotState state);
uint8_t RoverState_SetStateFromString(const char *stateText);
uint8_t RoverState_IsLocked(void);
void ReportFault(FaultCode fault);
void RecoverFromFault(void);
void PrintState(void);
void Robot_Task(void);
void RoverState_AutoCheckTask(void);
void RoverState_ModeTask(void);
void RoverState_InstructJetson(const char *stateName);
void RoverState_InitPowerSwitches(void);

typedef enum
{
    PMOS_11_5V = 0,
    PMOS_12_MOTOR_7V4,
    PMOS_21_JETSON_12V,
    PMOS_22_12V,
    PMOS_COUNT
} PowerSwitchId;

void RoverState_SetPowerSwitch(PowerSwitchId id, uint8_t on);

uint8_t RoverState_IsPowerSwitchOn(PowerSwitchId id);
uint32_t RoverState_PowerSwitchOnTimeMs(PowerSwitchId id);

#endif /* INC_ROVER_STATE_H_ */