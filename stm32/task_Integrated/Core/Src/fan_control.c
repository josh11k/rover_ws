/*
 * fan_control.c
 *
 *  Created on: 2026年9月17日
 *      Author: caiderui, linxinyu
 */


#include "fan_control.h"
#include "fan_driver.h"

// USER CONFIGURATION: test curve and input timeout, not fan specifications.
#define TEMP_TIMEOUT_MS 5000U
#define FAN_FAULT_PWM_THRESHOLD 30U
#define FAN_FAULT_RPM_THRESHOLD 100U
#define FAN_FAULT_DELAY_MS 3000U

static int temperature;
static uint8_t manualMode;
static uint8_t hasTemperature, fresh, pwm;
static uint8_t fanFault;
static uint32_t lastTemperatureTick;
static uint32_t faultStartTick;

static void FanControl_UpdateFault(void)
{
    uint32_t now;
    uint32_t rpm;

    now = HAL_GetTick();
    rpm = FanDriver_GetRPM();

    if (pwm < FAN_FAULT_PWM_THRESHOLD)
    {
        fanFault = 0U;
        faultStartTick = 0U;
        return;
    }

    if (rpm >= FAN_FAULT_RPM_THRESHOLD)
    {
        fanFault = 0U;
        faultStartTick = 0U;
        return;
    }

    if (faultStartTick == 0U)
    {
        faultStartTick = now;
        return;
    }

    if ((now - faultStartTick) >= FAN_FAULT_DELAY_MS)
    {
        fanFault = 1U;
    }
}

// Start with full cooling demand until valid temperature arrives.
void FanControl_Init(void)
{
    temperature = 0;
    hasTemperature = fresh = 0;
    manualMode = 0U;
    fanFault = 0U;
    faultStartTick = 0U;

    pwm = 100;
    FanDriver_SetPWM(pwm);
}

// Accept integer temperatures from 0 to 120 C; refresh even if unchanged.
uint8_t FanControl_SetTemperature(int value)
{
    if (value < 0 || value > 120) return 0;
    manualMode = 0U;
    temperature = value;
    hasTemperature = 1;
    lastTemperatureTick = HAL_GetTick();
    FanControl_Task();
    return 1;
}

// Apply a piecewise-linear test curve; missing data requests full cooling.
void FanControl_Task(void)
{
    if (manualMode)
    {
    	FanControl_UpdateFault();
    	return;
    }
    // USER CONFIGURATION: temperature C and PWM percent; validate under load.
    static const int points[] = {40, 45, 50, 55, 60, 65, 70};
    static const uint8_t duties[] = {30, 40, 50, 60, 70, 85, 100};
    uint8_t next = 100;

    fresh = hasTemperature &&
            (HAL_GetTick() - lastTemperatureTick < TEMP_TIMEOUT_MS);

    if (fresh)
    {
        if (temperature <= points[0])
        {
        	next = duties[0];
        }
        else
        {
            for (unsigned i = 1; i < sizeof(points) / sizeof(points[0]); i++)
            {
                if (temperature <= points[i])
                {
                    next = duties[i - 1] +
                           (temperature - points[i - 1]) *
                           (duties[i] - duties[i - 1]) /
                           (points[i] - points[i - 1]);
                    break;
                }
            }
        }
    }
    if (next != pwm)
    {
        pwm = next;
        FanDriver_SetPWM(pwm);
    }

    FanControl_UpdateFault();

    if (fanFault && pwm < 100U)
    {
        pwm = 100U;
        FanDriver_SetPWM(pwm);
    }
}

int FanControl_GetTemperature(void) { return temperature; }
uint8_t FanControl_GetPWM(void) { return pwm; }
uint8_t FanControl_IsFresh(void) { return fresh; }

uint8_t FanControl_HasFault(void)
{
    return fanFault;
}

void FanControl_SetManualPWM(uint8_t percent)
{
    if (percent > 100U)
    {
        percent = 100U;
    }

    manualMode = 1U;
    pwm = percent;

    fanFault = 0U;
    faultStartTick = 0U;

    FanDriver_SetPWM(pwm);
}

void FanControl_ClearManualPWM(void)
{
    manualMode = 0U;
    FanControl_Task();
}

uint8_t FanControl_IsManual(void)
{
    return manualMode;
}
