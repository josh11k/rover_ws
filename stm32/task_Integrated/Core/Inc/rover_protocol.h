#ifndef INC_ROVER_PROTOCOL_H_
#define INC_ROVER_PROTOCOL_H_

#include "main.h"

void RoverProtocol_Init(UART_HandleTypeDef *uart);
void RoverProtocol_Task(void);
void RoverProtocol_CheckAliveTimeout(void);
void SendAck(const char *message);
void SendNack(const char *reason);

#endif /* INC_ROVER_PROTOCOL_H_ */
