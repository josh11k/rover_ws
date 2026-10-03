#ifndef INC_ESP_PROTOCOL_H_
#define INC_ESP_PROTOCOL_H_

#include "main.h"

/*
 * USER CONFIGURATION: Protocol for the ESP32 WiFi bridge. Deliberately
 * minimal and restrictive: the ESP can only request a safe stop, nothing
 * else - so a flaky or compromised WiFi link can only ever make the rover
 * safer, never trigger a movement or deployment remotely.
 */
void EspProtocol_Init(UART_HandleTypeDef *uart);
void EspProtocol_Task(void);
void EspProtocol_Send(const char *msg);

#endif /* INC_ESP_PROTOCOL_H_ */