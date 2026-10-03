/*
 * rover_protocol.h
 *
 *  Created on: 2026年7月31日
 *      Author: caiderui
 */

#ifndef INC_ROVER_PROTOCOL_H_
#define INC_ROVER_PROTOCOL_H_

#include "main.h"

void Shell_Task(void);
void ExecuteCommand(void);
void SendAck(const char *message);
void SendNack(const char *reason);

#endif /* INC_ROVER_PROTOCOL_H_ */
