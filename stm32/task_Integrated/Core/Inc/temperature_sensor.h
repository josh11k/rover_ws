/*
 * temperature_sensor.h
 *
 *  Created on: 2026年9月18日
 *      Author: 22319
 */

#ifndef INC_TEMPERATURE_SENSOR_H_
#define INC_TEMPERATURE_SENSOR_H_

#include "main.h"

#define TEMP_SENSOR_COUNT 5U

typedef struct
{
    uint16_t rawSupply;
    uint16_t rawPt[TEMP_SENSOR_COUNT];

    float uSupplyAdc;
    float uSupply;
    float uPt[TEMP_SENSOR_COUNT];

    float resistance[TEMP_SENSOR_COUNT];
    float temperature[TEMP_SENSOR_COUNT];

    uint8_t valid[TEMP_SENSOR_COUNT];
} TemperatureSensorData;

void TemperatureSensor_Init(ADC_HandleTypeDef *hadc);
uint8_t TemperatureSensor_Read(TemperatureSensorData *data);
void TemperatureSensor_PrintHeartbeat(void);

#endif /* INC_TEMPERATURE_SENSOR_H_ */
