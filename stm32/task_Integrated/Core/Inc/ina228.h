/*
 * ina228.h
 *
 *  Created on: 2026年9月3日
 *      Author: caiderui
 */

#ifndef INC_INA228_H_
#include <stdint.h>

#define INC_INA228_H_

#define INA228_DIAGALRT_TMPOL  0x0080U
#define INA228_DIAGALRT_SHNTOL 0x0040U
#define INA228_DIAGALRT_SHNTUL 0x0020U
#define INA228_DIAGALRT_BUSOL  0x0010U
#define INA228_DIAGALRT_BUSUL  0x0008U
#define INA228_DIAGALRT_POL    0x0004U

uint8_t INA228_ReadAlertFlags(uint8_t address, uint16_t *flags);



typedef struct
{
    int32_t temperatureMilliC;
    uint32_t busVoltageMilliV;
    int32_t currentMicroA;
} INA228_Measurement;

uint8_t INA228_IsReady(uint8_t address); // Checks whether an INA228 responds at this 7-bit address.

uint8_t INA228_SetAveraging64(uint8_t address); // Configures averaging over 64 samples.

uint8_t INA228_SetAlertLimits(uint8_t address,
                              int16_t sovl,
                              uint16_t bovl,
                              uint16_t buvl);

uint8_t INA228_ReadTemperature(
    uint8_t address,
    int32_t *temperatureMilliC); // Reads temperature in thousandths of a degree Celsius.

uint8_t INA228_ReadBusVoltage(
    uint8_t address,
    uint32_t *voltageMilliV); // Reads bus voltage in millivolts.

uint8_t INA228_ReadCurrent(
    uint8_t address,
    int32_t *currentMicroA); // Calculates current in microamps.

uint8_t INA228_ReadMeasurement(
    uint8_t address,
    INA228_Measurement *measurement); // Reads temperature, voltage, and current together.


#endif /* INC_INA228_H_ */
