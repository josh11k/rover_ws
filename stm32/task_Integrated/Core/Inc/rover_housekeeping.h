#ifndef INC_ROVER_HOUSEKEEPING_H_
#define INC_ROVER_HOUSEKEEPING_H_

#include "main.h"

void RoverHousekeeping_Init(ADC_HandleTypeDef *hadc);
void RoverHousekeeping_Task(void);

#endif /* INC_ROVER_HOUSEKEEPING_H_ */
