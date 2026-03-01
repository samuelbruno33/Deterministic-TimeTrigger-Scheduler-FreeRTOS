#include "timekeeper.h"

typedef struct {
    uint32_t ulGlobalTick;
    uint32_t ulMajorFrameTick;
    uint32_t ulCurrentSubframe;
    bool xMajorFrameRestart;
} TimekeeperState_t;

static TimekeeperConfig_t xTimekeeperConfig;
static TimekeeperState_t xTimekeeperState;


void vTimekeeperInit(const TimekeeperConfig_t *cfg){
    xTimekeeperConfig = *cfg;
    xTimekeeperState.ulGlobalTick = 0;
    xTimekeeperState.ulMajorFrameTick = 0;
    xTimekeeperState.ulCurrentSubframe = 0;
    xTimekeeperState.xMajorFrameRestart = false;
}

void vTimekeeperUpdate(void){
    xTimekeeperState.ulGlobalTick++;
    xTimekeeperState.ulMajorFrameTick++;
    xTimekeeperState.xMajorFrameRestart = false;

    if (xTimekeeperState.ulMajorFrameTick >= xTimekeeperConfig.ulMajorFrameTicks) {
        xTimekeeperState.ulMajorFrameTick = 0;
        xTimekeeperState.ulCurrentSubframe=0;
        xTimekeeperState.xMajorFrameRestart = true;
    }

    uint32_t ulSubFrameDuration = xTimekeeperConfig.ulMajorFrameTicks / xTimekeeperConfig.ulNumSubframes;
    if(xTimekeeperState.ulMajorFrameTick % ulSubFrameDuration == 0 && xTimekeeperState.ulMajorFrameTick != 0)
    {
        xTimekeeperState.ulCurrentSubframe++;
        
    }
}

// getter function
bool vTimekeeperMajorFrameRestart(void){
    return xTimekeeperState.xMajorFrameRestart;
}

uint32_t vTimekeeperGetCurrentSubframe(void){
    volatile uint32_t out = xTimekeeperState.ulCurrentSubframe;
    return out;
}

uint32_t vTimekeeperGetCurrentTickInMF(void){
    volatile uint32_t out = xTimekeeperState.ulMajorFrameTick;
    return out;
}

uint32_t vTimekeeperGetRelativeSFTick(void){
    uint32_t ulSubFrameDuration = xTimekeeperConfig.ulMajorFrameTicks / xTimekeeperConfig.ulNumSubframes;
    volatile uint32_t out = xTimekeeperState.ulMajorFrameTick % ulSubFrameDuration;
    return out;
}
