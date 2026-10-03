/*
 * ina228.c
 *
 *  Created on: 2026年9月3日
 *      Author: caiderui
 */


#include "ina228.h"
#include "main.h"

#include <stddef.h>

#define INA228_REG_ADC_CONFIG 0x01U
#define INA228_REG_VSHUNT     0x04U
#define INA228_REG_VBUS       0x05U
#define INA228_REG_DIETEMP    0x06U
#define INA228_I2C_TIMEOUT_MS 100U

// USER CONFIGURATION: Adafruit INA228 uses a 15000 microohm shunt.
#define INA228_SHUNT_RESISTANCE_MICROOHM 15000LL

extern I2C_HandleTypeDef hi2c1;

static uint8_t INA228_ReadRegister(
    uint8_t address,
    uint8_t registerAddress,
    uint8_t *data,
    uint16_t length); // Reads bytes from one INA228 register.

static uint8_t INA228_WriteRegister16(
    uint8_t address,
    uint8_t registerAddress,
    uint16_t value); // Writes a 16-bit INA228 register.

static int32_t INA228_SignExtend20(
    uint32_t value); // Converts a signed 20-bit value to int32_t.

uint8_t INA228_IsReady(uint8_t address)
{
    return HAL_I2C_IsDeviceReady(
               &hi2c1,
               (uint16_t)address << 1,
               2U,
               20U) == HAL_OK;
}

uint8_t INA228_SetAveraging64(uint8_t address)
{
    uint8_t data[2];
    uint16_t config;

    if (!INA228_ReadRegister(address,
                             INA228_REG_ADC_CONFIG,
                             data,
                             sizeof(data)))
    {
        return 0U;
    }

    config = ((uint16_t)data[0] << 8) | data[1];
    config = (config & ~0x0007U) | 0x0003U;

    return INA228_WriteRegister16(
        address,
        INA228_REG_ADC_CONFIG,
        config);
}

uint8_t INA228_ReadTemperature(
    uint8_t address,
    int32_t *temperatureMilliC)
{
    uint8_t data[2];
    int16_t raw;

    if (temperatureMilliC == NULL)
        return 0U;

    if (!INA228_ReadRegister(address,
                             INA228_REG_DIETEMP,
                             data,
                             sizeof(data)))
    {
        return 0U;
    }

    raw = (int16_t)(((uint16_t)data[0] << 8) | data[1]);

    *temperatureMilliC =
        (int32_t)(((int64_t)raw * 78125LL) / 10000LL);

    return 1U;
}

uint8_t INA228_ReadBusVoltage(
    uint8_t address,
    uint32_t *voltageMilliV)
{
    uint8_t data[3];
    uint32_t raw24;
    uint32_t raw20;

    if (voltageMilliV == NULL)
        return 0U;

    if (!INA228_ReadRegister(address,
                             INA228_REG_VBUS,
                             data,
                             sizeof(data)))
    {
        return 0U;
    }

    raw24 = ((uint32_t)data[0] << 16) |
            ((uint32_t)data[1] << 8) |
            data[2];

    raw20 = raw24 >> 4;

    *voltageMilliV =
        (uint32_t)(((uint64_t)raw20 * 25ULL) / 128ULL);

    return 1U;
}

uint8_t INA228_ReadCurrent(
    uint8_t address,
    int32_t *currentMicroA)
{
    uint8_t data[3];
    uint32_t raw24;
    int32_t raw20;

    if (currentMicroA == NULL)
        return 0U;

    if (!INA228_ReadRegister(address,
                             INA228_REG_VSHUNT,
                             data,
                             sizeof(data)))
    {
        return 0U;
    }

    raw24 = ((uint32_t)data[0] << 16) |
            ((uint32_t)data[1] << 8) |
            data[2];

    raw20 = INA228_SignExtend20(raw24 >> 4);

    *currentMicroA =
        (int32_t)(((int64_t)raw20 * 312500LL) /
                  INA228_SHUNT_RESISTANCE_MICROOHM);

    return 1U;
}

uint8_t INA228_ReadMeasurement(
    uint8_t address,
    INA228_Measurement *measurement)
{
    if (measurement == NULL)
        return 0U;

    if (!INA228_ReadTemperature(
            address,
            &measurement->temperatureMilliC))
    {
        return 0U;
    }

    if (!INA228_ReadBusVoltage(
            address,
            &measurement->busVoltageMilliV))
    {
        return 0U;
    }

    if (!INA228_ReadCurrent(
            address,
            &measurement->currentMicroA))
    {
        return 0U;
    }

    return 1U;
}

static uint8_t INA228_ReadRegister(
    uint8_t address,
    uint8_t registerAddress,
    uint8_t *data,
    uint16_t length)
{
    return HAL_I2C_Mem_Read(
               &hi2c1,
               (uint16_t)address << 1,
               registerAddress,
               I2C_MEMADD_SIZE_8BIT,
               data,
               length,
               INA228_I2C_TIMEOUT_MS) == HAL_OK;
}

static uint8_t INA228_WriteRegister16(
    uint8_t address,
    uint8_t registerAddress,
    uint16_t value)
{
    uint8_t data[2];

    data[0] = (uint8_t)(value >> 8);
    data[1] = (uint8_t)(value & 0xFFU);

    return HAL_I2C_Mem_Write(
               &hi2c1,
               (uint16_t)address << 1,
               registerAddress,
               I2C_MEMADD_SIZE_8BIT,
               data,
               sizeof(data),
               INA228_I2C_TIMEOUT_MS) == HAL_OK;
}

static int32_t INA228_SignExtend20(uint32_t value)
{
    if ((value & 0x00080000U) != 0U)
        value |= 0xFFF00000U;

    return (int32_t)value;
}
