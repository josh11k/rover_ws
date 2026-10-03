/*
 * fan_driver.c
 *
 *  Created on: 2026年9月17日
 *      Author: caiderui, linxinyu
 */


#include "fan_driver.h"

// USER CONFIGURATION: provisional pulses per revolution; verify for XF065.
#define FAN_PULSES_PER_REV 2U

static TIM_HandleTypeDef *fanTimer;
static volatile uint32_t tachPulses;
static uint32_t lastPulses, lastTick, fanRPM;

// Start CH1 at 100% demand before temperature data becomes available.
HAL_StatusTypeDef FanDriver_Init(TIM_HandleTypeDef *timer)
{
    fanTimer = timer;
    lastPulses = tachPulses;
    lastTick = HAL_GetTick();
    fanRPM = 0;
    FanDriver_SetPWM(100);
    return HAL_TIM_PWM_Start(fanTimer, TIM_CHANNEL_1);
}

// Convert percentage to timer compare value; ARR must remain 639.
void FanDriver_SetPWM(uint8_t percent)
{
    if (fanTimer == NULL) return;
    if (percent > 100U) percent = 100U;
    uint32_t period = __HAL_TIM_GET_AUTORELOAD(fanTimer) + 1U;
    __HAL_TIM_SET_COMPARE(fanTimer, TIM_CHANNEL_1,
                         period * percent / 100U);
}

// Count only falling edges; never print inside this interrupt.
void HAL_GPIO_EXTI_Falling_Callback(uint16_t pin)
{
    if (pin == FAN_TACH_Pin) tachPulses++;
}

// Use elapsed time rather than assuming the loop runs exactly every second.
void FanDriver_Task(void)
{
    uint32_t now = HAL_GetTick();
    uint32_t elapsed = now - lastTick;
    if (elapsed < 1000U) return;
    uint32_t snapshot = tachPulses;
    uint32_t count = snapshot - lastPulses;
    lastPulses = snapshot;
    lastTick = now;
    fanRPM = (uint32_t)(((uint64_t)count * 60000U) /
                       ((uint64_t)elapsed * FAN_PULSES_PER_REV));
}

uint32_t FanDriver_GetRPM(void) { return fanRPM; }
