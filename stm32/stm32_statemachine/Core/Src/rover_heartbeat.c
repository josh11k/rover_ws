/*
 * rover_heartbeat.c
 *
 *  Created on: 2026年7月31日
 *      Author: caiderui
 */

#include "rover_heartbeat.h"
#include "rover_state.h"
#include <stdio.h>

void Heartbeat_Task(void)
{
    static uint32_t lastHeartbeat = 0;
    uint32_t now = HAL_GetTick();

    if (now - lastHeartbeat >= 1000)
    {
        lastHeartbeat = now;
        printf("HB: %s, t = %lus\r\n", StateToString(), HAL_GetTick() / 1000);
    }
}
