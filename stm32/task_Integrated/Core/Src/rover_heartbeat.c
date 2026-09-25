#include "rover_heartbeat.h"
#include "rover_state.h"

#include <stdio.h>

void Heartbeat_Task(void)
{
    static uint32_t lastHeartbeat = 0U;
    uint32_t now = HAL_GetTick();

    if (now - lastHeartbeat >= 1000U)
    {
        lastHeartbeat = now;
        printf(">>HB: %s, t = %lus<<\r\n",
               StateToString(),
               (unsigned long)(now / 1000U));	/*1s pro time*/
    }
}
