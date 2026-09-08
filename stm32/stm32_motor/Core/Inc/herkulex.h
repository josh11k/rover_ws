#ifndef HERKULEX_H_
#define HERKULEX_H_

#include <stdint.h>

uint8_t Herkulex_ReadStatus(uint8_t id,
                            uint8_t *statusError,
                            uint8_t *statusDetail); // Reads the two status bytes from one motor.
uint8_t Herkulex_QuickPing(uint8_t id,
                           uint32_t timeoutMs); // Checks whether one motor ID replies.
void Herkulex_SetLed(uint8_t id,
                     uint8_t color); // Sets the motor's RGB LED register.
void Herkulex_SetTorque(uint8_t id,
                        uint8_t torqueMode); // Selects torque-free, brake, or torque-on mode.
uint8_t Herkulex_ReadPosition(uint8_t id,
                              uint16_t *position); // Reads the calibrated position once.
uint8_t Herkulex_ReadPositionReliable(uint8_t id,
                                      uint16_t *position); // Retries a position read up to three times.
void Herkulex_MoveToPosition(uint8_t id,
                             uint16_t position,
                             uint16_t durationMs); // Sends one position-mode movement command.
void Herkulex_MoveSpeed(uint8_t id,
                        int16_t speed); // Starts continuous speed-mode movement.

#endif // HERKULEX_H_
