#include "herkulex.h"

#include "main.h"

#include <stddef.h>

#define HERKULEX_RX_BUFFER_SIZE 32U
#define HERKULEX_FIRST_BYTE_TIMEOUT_MS 100U
#define HERKULEX_NEXT_BYTE_TIMEOUT_MS 5U

extern UART_HandleTypeDef huart1;

static uint8_t rxBuffer[HERKULEX_RX_BUFFER_SIZE];

static void Herkulex_SendPacket(uint8_t id,
                                uint8_t command,
                                const uint8_t *data,
                                uint8_t dataLength); // Builds and sends one Herkulex packet.
static void Herkulex_SendStat(uint8_t id); // Sends a STAT request.
static void Herkulex_FlushRx(void); // Discards stale USART1 receive data.
static uint16_t Herkulex_ReadRaw(uint8_t *buffer,
                                 uint16_t capacity); // Reads one reply until the UART becomes quiet.
static uint8_t Herkulex_ValidateStatusReply(const uint8_t *reply,
                                            uint8_t id); // Validates a nine-byte STAT reply.

static void Herkulex_SendPacket(uint8_t id,
                                uint8_t command,
                                const uint8_t *data,
                                uint8_t dataLength)
{
    uint8_t packet[HERKULEX_RX_BUFFER_SIZE];
    uint8_t packetSize = 7U + dataLength;
    uint8_t checksum1 = packetSize ^ id ^ command;

    if (packetSize > sizeof(packet))
        return;

    packet[0] = 0xFF;
    packet[1] = 0xFF;
    packet[2] = packetSize;
    packet[3] = id;
    packet[4] = command;

    for (uint8_t i = 0; i < dataLength; i++)
    {
        packet[7U + i] = data[i];
        checksum1 ^= data[i];
    }

    packet[5] = checksum1 & 0xFE;
    packet[6] = (~packet[5]) & 0xFE;

    HAL_UART_Transmit(&huart1, packet, packetSize, 100U);
}

static void Herkulex_SendStat(uint8_t id)
{
    Herkulex_SendPacket(id, 0x07, NULL, 0);
}

static void Herkulex_FlushRx(void)
{
    HAL_UART_AbortReceive(&huart1);
    __HAL_UART_CLEAR_OREFLAG(&huart1);
    __HAL_UART_SEND_REQ(&huart1, UART_RXDATA_FLUSH_REQUEST);
}

static uint16_t Herkulex_ReadRaw(uint8_t *buffer, uint16_t capacity)
{
    uint16_t length = 0;

    if (capacity == 0U)
        return 0;

    if (HAL_UART_Receive(&huart1,
                         &buffer[0],
                         1,
                         HERKULEX_FIRST_BYTE_TIMEOUT_MS) != HAL_OK)
    {
        return 0;
    }

    length = 1;

    while (length < capacity)
    {
        if (HAL_UART_Receive(&huart1,
                             &buffer[length],
                             1,
                             HERKULEX_NEXT_BYTE_TIMEOUT_MS) != HAL_OK)
        {
            break;
        }

        length++;
    }

    return length;
}

static uint8_t Herkulex_ValidateStatusReply(const uint8_t *reply, uint8_t id)
{
    uint8_t checksum1;

    if (reply[0] != 0xFF ||
        reply[1] != 0xFF ||
        reply[2] != 0x09 ||
        reply[3] != id ||
        reply[4] != 0x47)
    {
        return 0;
    }

    checksum1 = (reply[2] ^ reply[3] ^ reply[4] ^
                 reply[7] ^ reply[8]) & 0xFE;

    return reply[5] == checksum1 &&
           reply[6] == ((~checksum1) & 0xFE);
}

uint8_t Herkulex_ReadStatus(uint8_t id,
                            uint8_t *statusError,
                            uint8_t *statusDetail)
{
    uint16_t length;

    Herkulex_FlushRx();
    Herkulex_SendStat(id);
    length = Herkulex_ReadRaw(rxBuffer, sizeof(rxBuffer));

    if (length != 9U || !Herkulex_ValidateStatusReply(rxBuffer, id))
        return 0;

    *statusError = rxBuffer[7];
    *statusDetail = rxBuffer[8];
    return 1;
}

uint8_t Herkulex_QuickPing(uint8_t id, uint32_t timeoutMs)
{
    uint8_t reply[9];

    Herkulex_FlushRx();
    Herkulex_SendStat(id);

    if (HAL_UART_Receive(&huart1,
                         reply,
                         sizeof(reply),
                         timeoutMs) != HAL_OK)
    {
        return 0;
    }

    return Herkulex_ValidateStatusReply(reply, id);
}

void Herkulex_SetLed(uint8_t id, uint8_t color)
{
    const uint8_t data[] = {0x35, 0x01, color};
    Herkulex_SendPacket(id, 0x03, data, sizeof(data));
}

void Herkulex_SetTorque(uint8_t id, uint8_t torqueMode)
{
    const uint8_t data[] = {0x34, 0x01, torqueMode};
    Herkulex_SendPacket(id, 0x03, data, sizeof(data));
}

uint8_t Herkulex_ReadPosition(uint8_t id, uint16_t *position)
{
    const uint8_t request[] = {0x3A, 0x02};
    uint16_t length;
    uint8_t checksum1;

    Herkulex_FlushRx();
    Herkulex_SendPacket(id, 0x04, request, sizeof(request));
    length = Herkulex_ReadRaw(rxBuffer, sizeof(rxBuffer));

    if (length != 13U ||
        rxBuffer[0] != 0xFF ||
        rxBuffer[1] != 0xFF ||
        rxBuffer[2] != 0x0D ||
        rxBuffer[3] != id ||
        rxBuffer[4] != 0x44 ||
        rxBuffer[7] != 0x3A ||
        rxBuffer[8] != 0x02)
    {
        return 0;
    }

    checksum1 = rxBuffer[2] ^ rxBuffer[3] ^ rxBuffer[4];

    for (uint8_t i = 7; i < 13U; i++)
        checksum1 ^= rxBuffer[i];

    checksum1 &= 0xFE;

    if (rxBuffer[5] != checksum1 ||
        rxBuffer[6] != ((~checksum1) & 0xFE))
    {
        return 0;
    }

    *position = ((uint16_t)(rxBuffer[10] & 0x03) << 8) |
                rxBuffer[9];
    return 1;
}

uint8_t Herkulex_ReadPositionReliable(uint8_t id, uint16_t *position)
{
    for (uint8_t attempt = 0; attempt < 3U; attempt++)
    {
        if (Herkulex_ReadPosition(id, position))
            return 1;

        HAL_Delay(20U);
    }

    return 0;
}

void Herkulex_MoveToPosition(uint8_t id,
                             uint16_t position,
                             uint16_t durationMs)
{
    uint32_t playTime;

    if (position > 1023U)
        position = 1023U;

    playTime = ((uint32_t)durationMs * 10U + 56U) / 112U;

    if (playTime > 255U)
        playTime = 255U;

    const uint8_t data[] =
    {
        (uint8_t)playTime,
        (uint8_t)(position & 0xFF),
        (uint8_t)((position >> 8) & 0x03),
        0x04,
        id
    };

    Herkulex_SendPacket(id, 0x06, data, sizeof(data));
}

void Herkulex_MoveSpeed(uint8_t id, int16_t speed)
{
    uint16_t speedValue;

    if (speed < 0)
        speedValue = (uint16_t)(-speed) | 0x4000U;
    else
        speedValue = (uint16_t)speed;

    const uint8_t data[] =
    {
        45,
        (uint8_t)(speedValue & 0xFF),
        (uint8_t)((speedValue >> 8) & 0xFF),
        0x06,
        id
    };

    Herkulex_SendPacket(id, 0x06, data, sizeof(data));
}
