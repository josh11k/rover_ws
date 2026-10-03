#ifndef INC_UART_RX_H_
#define INC_UART_RX_H_

#include "main.h"

void UartRx_Start(UART_HandleTypeDef *huart);
uint8_t UartRx_GetByte(UART_HandleTypeDef *huart, uint8_t *out);

#endif /* INC_UART_RX_H_ */