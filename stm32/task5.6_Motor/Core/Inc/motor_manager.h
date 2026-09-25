#ifndef MOTOR_MANAGER_H_
#define MOTOR_MANAGER_H_

void MotorManager_Init(void); // Initializes the configured motor table.
void MotorManager_Task(void); // Runs connection, discovery, movement, and LED tasks.
void MotorManager_ExecuteCommand(const char *input); // Executes one complete terminal command.

#endif // MOTOR_MANAGER_H_
