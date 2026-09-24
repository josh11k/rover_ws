/*
 * fan_protocol.h
 *
 *  Created on: 2026年9月17日
 *      Author: caiderui, linxinyu
 */

#ifndef INC_FAN_PROTOCOL_H_
#define INC_FAN_PROTOCOL_H_

#include "main.h"

void FanProtocol_Init(UART_HandleTypeDef *uart);
void FanProtocol_Task(void);

#endif /* INC_FAN_PROTOCOL_H_ */
