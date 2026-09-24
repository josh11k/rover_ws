/*
 * fan_driver.h
 *
 *  Created on: 2026年9月17日
 *      Author: caiderui, linxinyu
 */

#ifndef INC_FAN_DRIVER_H_
#define INC_FAN_DRIVER_H_

#include "main.h"

HAL_StatusTypeDef FanDriver_Init(TIM_HandleTypeDef *timer);
void FanDriver_SetPWM(uint8_t percent);
void FanDriver_Task(void);
uint32_t FanDriver_GetRPM(void);

#endif /* INC_FAN_DRIVER_H_ */
