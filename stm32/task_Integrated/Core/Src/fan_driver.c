/*
 * fan_driver.c
 *
 *  Created on: 2026年9月22日
 *      Author: linxinyu
 */



#include "fan_driver.h"

#define FAN_PULSES_PER_REV 2U

static volatile uint32_t tachPulses = 0U;

static uint32_t lastPulses = 0U;
static uint32_t lastTick = 0U;
static uint32_t fanRPM = 0U;

void FanDriver_Init(void)
{
    lastPulses = tachPulses;
    lastTick = HAL_GetTick();
    fanRPM = 0U;
}

/*
 * Count only falling edges; never print inside this interrupt.
 */
void HAL_GPIO_EXTI_Falling_Callback(uint16_t pin)
{
    if (pin == FAN_TACH_Pin)
    {
        tachPulses++;
    }
}

/*
 * Calculate RPM from tach pulse count.
 */
void FanDriver_Task(void)
{
    uint32_t now;
    uint32_t elapsed;
    uint32_t snapshot;
    uint32_t count;

    now = HAL_GetTick();
    elapsed = now - lastTick;

    if (elapsed < 1000U)
    {
        return;
    }

    snapshot = tachPulses;
    count = snapshot - lastPulses;

    lastPulses = snapshot;
    lastTick = now;

    fanRPM = (uint32_t)(((uint64_t)count * 60000U) /
                        ((uint64_t)elapsed * FAN_PULSES_PER_REV));
}

uint32_t FanDriver_GetRPM(void)
{
    return fanRPM;
}
