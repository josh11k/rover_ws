/*
 * temperature_logger.h
 *
 *  Created on: 2026年9月18日
 *      Author: linxinyu
 */

#ifndef INC_TEMPERATURE_LOGGER_H_
#define INC_TEMPERATURE_LOGGER_H_

#include "temperature_sensor.h"

void TemperatureLogger_PrintMotorTemperatures(const TemperatureSensorData *data);

#endif /* INC_TEMPERATURE_LOGGER_H_ */
