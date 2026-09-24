#ifndef INC_ROVER_STATE_H_
#define INC_ROVER_STATE_H_

#include "main.h"
#include <stdint.h>

typedef enum
{
    STATE_IDLE = 0,
    STATE_MAST_DEPLOYMENT,
    STATE_STANDBY,
    STATE_AUTO,
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
    FAULT_UNKNOWN
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

#endif /* INC_ROVER_STATE_H_ */
