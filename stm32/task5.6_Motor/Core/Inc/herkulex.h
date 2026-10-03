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
void Herkulex_ClearError(uint8_t id);

uint8_t Herkulex_ReadPosition(uint8_t id,
                              uint16_t *position); // Reads the calibrated position once.
uint8_t Herkulex_ReadPositionReliable(uint8_t id,
                                      uint16_t *position); // Retries a position read up to three times.
typedef enum
{
    HERKULEX_JOG_POSITION = 0,
    HERKULEX_JOG_SPEED = 1
} HerkulexJogMode;

typedef struct
{
    uint8_t id;
    HerkulexJogMode mode;
    int16_t value;
    uint8_t led;
} HerkulexJogCommand;

void Herkulex_MoveToPosition(uint8_t id,
                             uint16_t position,
                             uint16_t durationMs); // Sends one position-mode movement command.
void Herkulex_SyncMoveToPositions(const uint8_t *ids,
                                  const uint16_t *positions,
                                  uint8_t count,
                                  uint16_t durationMs);
void Herkulex_MoveSpeed(uint8_t id,
                        int16_t speed); // Starts continuous speed-mode movement.
void Herkulex_SyncJogMixed(const HerkulexJogCommand *commands,
                           uint8_t count,
                           uint16_t durationMs);

#endif // HERKULEX_H_
