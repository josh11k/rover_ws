/*
 * fan_control.h
 *
 *  Created on: 2026年9月17日
 *      Author: caiderui, linxinyu
 */

#ifndef INC_FAN_CONTROL_H_
#define INC_FAN_CONTROL_H_

#include "main.h"

void FanControl_Init(void);
void FanControl_Task(void);
uint8_t FanControl_SetTemperature(int temperature);

void FanControl_SetManualPWM(uint8_t percent);
void FanControl_ClearManualPWM(void);
uint8_t FanControl_IsManual(void);

int FanControl_GetTemperature(void);
uint8_t FanControl_GetPWM(void);
uint8_t FanControl_IsFresh(void);
uint8_t FanControl_HasFault(void);

#endif /* INC_FAN_CONTROL_H_ */
