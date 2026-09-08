/*
 * rover_state.h
 *
 *  Created on: 2026年7月31日
 *      Author: caiderui
 */

#ifndef INC_ROVER_STATE_H_
#define INC_ROVER_STATE_H_

#include "main.h"

typedef enum
{
	STATE_IDLE = 0,
    STATE_MAST_DEPLOYMENT,
    STATE_STANDBY,
    STATE_SAFE
} RobotState;
typedef enum
{
    FAULT_NONE = 0,
    FAULT_VOLTAGE_HIGH,
    FAULT_TEMP_HIGH,
    FAULT_CURRENT_HIGH,
    FAULT_COMM_TIMEOUT
} FaultCode;

extern RobotState currentState;
extern FaultCode activeFault;

const char* StateToString(void);
const char* FaultToString(void);
void ReportFault(FaultCode fault);
void PrintState(void);
void Robot_Task(void);

#endif /* INC_ROVER_STATE_H_ */
