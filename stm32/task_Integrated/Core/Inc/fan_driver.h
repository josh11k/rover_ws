/*
 * fan_driver.h
 *
 *  Created on: 2026年9月17日
 *      Author: caiderui, linxinyu
 */

#ifndef FAN_DRIVER_H_
#define FAN_DRIVER_H_

#include "main.h"
#include <stdint.h>

void FanDriver_Init(void);
void FanDriver_Task(void);

uint32_t FanDriver_GetRPM(void);

#endif /* FAN_DRIVER_H_ */
