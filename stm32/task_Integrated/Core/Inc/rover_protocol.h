#ifndef INC_ROVER_PROTOCOL_H_
#define INC_ROVER_PROTOCOL_H_

#include "main.h"

void RoverProtocol_Init(UART_HandleTypeDef *uart);
void RoverProtocol_Task(void);
void RoverProtocol_CheckAliveTimeout(void);
void SendAck(const char *message);
void SendNack(const char *reason);
void RoverProtocol_ProcessCommand(char *line);
void RoverProtocol_SetReplyUart(UART_HandleTypeDef *uart);
void RoverProtocol_SendToJetson(const char *text);
UART_HandleTypeDef *RoverProtocol_GetReplyUart(void);
uint8_t RoverProtocol_HasAliveSince(uint32_t sinceTick);
uint8_t RoverState_IsLocked(void);

#endif /* INC_ROVER_PROTOCOL_H_ */
