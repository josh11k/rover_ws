#ifndef MOTOR_MANAGER_H_
#define MOTOR_MANAGER_H_

#include <stdint.h>

void MotorManager_Init(void); // Initializes the configured motor table.
void MotorManager_Task(void); // Runs connection, discovery, movement, and LED tasks.
void MotorManager_ExecuteCommand(const char *input); // Executes one complete terminal command.
uint8_t MotorManager_GetPositionById(uint8_t motorId, uint16_t *position, uint8_t *connected); // Returns cached position/connection state.
uint8_t MotorManager_GetInternalTemperatureCById(uint8_t motorId,
                                                 int16_t *temperatureC,
                                                 uint8_t *connected);
#endif // MOTOR_MANAGER_H_
