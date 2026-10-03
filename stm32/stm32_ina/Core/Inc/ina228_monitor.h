/*
 * ina228_monitor.h
 *
 *  Created on: 2026年9月3日
 *      Author: caiderui
 */

#ifndef INC_INA228_MONITOR_H_
#define INC_INA228_MONITOR_H_

void INA228Monitor_Init(void); // Discovers and configures all connected INA228 devices.
void INA228Monitor_Task(void); // Periodically reads and prints every discovered INA228.

#endif /* INC_INA228_MONITOR_H_ */
