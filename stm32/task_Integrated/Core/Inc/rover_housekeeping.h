#ifndef INC_ROVER_HOUSEKEEPING_H_
#define INC_ROVER_HOUSEKEEPING_H_

#include "main.h"
#include "rover_state.h"

void RoverHousekeeping_Init(ADC_HandleTypeDef *hadc);
void RoverHousekeeping_Task(void);
uint8_t RoverHousekeeping_CheckThresholds(FaultCode *outFault);

#endif /* INC_ROVER_HOUSEKEEPING_H_ */
