#include "uart_rx.h"
#include <stddef.h>

#define UART_RX_CHANNEL_COUNT 2U        /* USART2 (Jetson) + USART3 (ESP) */
#define UART_RX_BUFFER_SIZE   256U      /* muss Zweierpotenz sein */
#define UART_RX_BUFFER_MASK   (UART_RX_BUFFER_SIZE - 1U)

typedef struct
{
    UART_HandleTypeDef *huart;
    volatile uint16_t head;             /* wird nur in der ISR geschrieben */
    volatile uint16_t tail;             /* wird nur in der Hauptschleife geschrieben */
    uint8_t rxByte;
    uint8_t buffer[UART_RX_BUFFER_SIZE];
} UartRxChannel;

static UartRxChannel channels[UART_RX_CHANNEL_COUNT];

static UartRxChannel *FindChannel(UART_HandleTypeDef *huart)
{
    for (uint8_t i = 0U; i < UART_RX_CHANNEL_COUNT; i++)
    {
        if (channels[i].huart == huart)
        {
            return &channels[i];
        }
    }
    return NULL;
}

void UartRx_Start(UART_HandleTypeDef *huart)
{
    UartRxChannel *ch;

    if (huart == NULL)
    {
        return;
    }

    ch = FindChannel(huart);
    if (ch == NULL)
    {
        ch = FindChannel(NULL);         /* freien Slot belegen */
        if (ch == NULL)
        {
            return;
        }
        ch->huart = huart;
    }

    ch->head = 0U;
    ch->tail = 0U;
    (void)HAL_UART_Receive_IT(huart, &ch->rxByte, 1U);
}

uint8_t UartRx_GetByte(UART_HandleTypeDef *huart, uint8_t *out)
{
    UartRxChannel *ch;
    uint16_t tail;

    if (huart == NULL || out == NULL)
    {
        return 0U;
    }

    ch = FindChannel(huart);
    if (ch == NULL)
    {
        return 0U;
    }

    tail = ch->tail;
    if (tail == ch->head)
    {
        return 0U;                      /* Puffer leer */
    }

    *out = ch->buffer[tail];
    ch->tail = (uint16_t)((tail + 1U) & UART_RX_BUFFER_MASK);
    return 1U;
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    UartRxChannel *ch;
    uint16_t next;

    if (huart == NULL)
    {
        return;
    }

    ch = FindChannel(huart);
    if (ch == NULL)
    {
        return;
    }

    next = (uint16_t)((ch->head + 1U) & UART_RX_BUFFER_MASK);
    if (next != ch->tail)               /* bei vollem Puffer Byte verwerfen */
    {
        ch->buffer[ch->head] = ch->rxByte;
        ch->head = next;
    }

    (void)HAL_UART_Receive_IT(huart, &ch->rxByte, 1U);
}

void HAL_UART_ErrorCallback(UART_HandleTypeDef *huart)
{
    UartRxChannel *ch;

    if (huart == NULL)
    {
        return;
    }

    ch = FindChannel(huart);
    if (ch == NULL)
    {
        return;
    }

    /* Nach Overrun/Framing-Fehler Empfang neu starten (HAL_BUSY ist harmlos) */
    (void)HAL_UART_Receive_IT(huart, &ch->rxByte, 1U);
}