#ifndef TIMEKEEPER_H
#define TIMEKEEPER_H

#include <stdint.h>
#include <stdbool.h>
#include "FreeRTOSConfig.h"


typedef struct {
    uint32_t ulMajorFrameTicks;
    uint32_t ulNumSubframes;
} TimekeeperConfig_t;

void vTimekeeperInit(const TimekeeperConfig_t *cfg);
void vTimekeeperUpdate(void);
bool vTimekeeperMajorFrameRestart(void);
uint32_t vTimekeeperGetCurrentSubframe(void);
uint32_t vTimekeeperGetCurrentTickInMF(void);
uint32_t vTimekeeperGetRelativeSFTick(void);

#endif

