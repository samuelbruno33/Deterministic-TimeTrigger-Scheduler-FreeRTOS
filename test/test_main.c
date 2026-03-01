#include "FreeRTOS.h"
#include "task.h"
#include "timeline_scheduler.h"
#include "timekeeper.h"
#include "emulated_uart.h"
#include <string.h>

#define TEST             1

void vTestTaskHRT(void *pvParameters) {
    
    uint32_t wcet = (uint32_t)(uintptr_t)pvParameters;
    for (;;) {

    vTestTaskHRT_reset_point:

        if (wcet != 0xFFFFFFFF) {
            volatile uint32_t tickToBurn = wcet;
            volatile TickType_t ActualTick;
            volatile TickType_t ReferenceTick;
            while (tickToBurn > 0) {
                tickToBurn--;
                ActualTick = xTaskGetTickCount();
                while (xTaskGetTickCount() <= ActualTick) { }
                ReferenceTick = xTaskGetTickCount() - ActualTick;
                if(ReferenceTick > 2) {
                    goto vTestTaskHRT_reset_point;
                };
            }
            vNotifyHRTCompletion(NULL); 
        } else {
            while(1) { }
        }
    }
}

void vTestTaskSRT(void *pvParameters) {
    uint32_t wcet_per_frame = (uint32_t)(uintptr_t)pvParameters;
    for (;;) {
        volatile uint32_t tickToBurn = wcet_per_frame;
        volatile TickType_t ActualTick;
        while (tickToBurn > 0) {
            tickToBurn--;
            ActualTick = xTaskGetTickCount();
            while (xTaskGetTickCount() <= ActualTick) { }
        }
        vNotifySrtCompletion();
    }
}

// TEST SCENARIOS

// Single HRT 
void run_test_single_hrt(void) {
    static TimelineTaskConfig_t xTasks[] = {
        {"HRT_A", vTestTaskHRT, (void*)(uintptr_t)5, 128, TIMELINE_TASK_HRT, 10, 20, 0}
    };
    TimekeeperConfig_t xTkConfig = { .ulMajorFrameTicks = 50, .ulNumSubframes = 1 };
    SchedulerConfig_t xConfig = { &xTkConfig, xTasks, 1 };

    vConfigureScheduler(&xConfig);
    vTimekeeperInit(&xTkConfig);
    extern BaseType_t xIsTimelineSchedulerActive;
    xIsTimelineSchedulerActive = pdTRUE;
    vTaskStartScheduler();
}

// Preemption HRT on SRT
void run_test_preemption(void) {
    static TimelineTaskConfig_t xTasks[] = {
        {"HRT_A", vTestTaskHRT, (void*)(uintptr_t)5, 128, TIMELINE_TASK_HRT, 20, 30, 0},
        {"SRT_X", vTestTaskSRT, (void*)(uintptr_t)40, 128, TIMELINE_TASK_SRT, 0, 0, 0}
    };
    TimekeeperConfig_t xTkConfig = { .ulMajorFrameTicks = 50, .ulNumSubframes = 1 };
    SchedulerConfig_t xConfig = { &xTkConfig, xTasks, 2 };

    vConfigureScheduler(&xConfig);
    vTimekeeperInit(&xTkConfig);
    extern BaseType_t xIsTimelineSchedulerActive;
    xIsTimelineSchedulerActive = pdTRUE;
    vTaskStartScheduler();
}

// HRT deadline miss
void run_test_deadline_miss(void) {
    static TimelineTaskConfig_t xTasks[] = {
        {"HRT_A", vTestTaskHRT, (void*)(uintptr_t)0xFFFFFFFF, 128, TIMELINE_TASK_HRT, 10, 20, 0}
    };
    TimekeeperConfig_t xTkConfig = { .ulMajorFrameTicks = 50, .ulNumSubframes = 1 };
    SchedulerConfig_t xConfig = { &xTkConfig, xTasks, 1 };

    vConfigureScheduler(&xConfig);
    vTimekeeperInit(&xTkConfig);
    extern BaseType_t xIsTimelineSchedulerActive;
    xIsTimelineSchedulerActive = pdTRUE;
    vTaskStartScheduler();
}

// HRT in every subframe with idle gaps
void run_test_hrt_every_subframe(void) {
    static TimelineTaskConfig_t xTasks[] = {
        {"HRT_0", vTestTaskHRT, (void*)(uintptr_t)5, 128, TIMELINE_TASK_HRT, 0, 10, 0},
        {"HRT_1", vTestTaskHRT, (void*)(uintptr_t)5, 128, TIMELINE_TASK_HRT, 0, 10, 1},
        {"HRT_2", vTestTaskHRT, (void*)(uintptr_t)5, 128, TIMELINE_TASK_HRT, 0, 10, 2},
        {"HRT_3", vTestTaskHRT, (void*)(uintptr_t)5, 128, TIMELINE_TASK_HRT, 0, 10, 3}
    };

    TimekeeperConfig_t xTkConfig = { .ulMajorFrameTicks = 40, .ulNumSubframes = 4 };
    SchedulerConfig_t xConfig = { &xTkConfig, xTasks, 4 };

    vConfigureScheduler(&xConfig);
    vTimekeeperInit(&xTkConfig);
    extern BaseType_t xIsTimelineSchedulerActive;
    xIsTimelineSchedulerActive = pdTRUE;
    
    vTaskStartScheduler();
}

// Solo HRT (No Idle time)
void run_test_hrt_stress(void) {
    static TimelineTaskConfig_t xTasks[] = {
        {"HRT_A", vTestTaskHRT, (void*)(uintptr_t)5,  128, TIMELINE_TASK_HRT, 0,   5,  0},
        {"HRT_B", vTestTaskHRT, (void*)(uintptr_t)10, 128, TIMELINE_TASK_HRT, 5,   15, 0},
        {"HRT_C", vTestTaskHRT, (void*)(uintptr_t)5,  128, TIMELINE_TASK_HRT, 15,  20, 0}
    };

    TimekeeperConfig_t xTkConfig = { .ulMajorFrameTicks = 20, .ulNumSubframes = 1 };
    SchedulerConfig_t xConfig = { &xTkConfig, xTasks, 3 };

    vConfigureScheduler(&xConfig);
    vTimekeeperInit(&xTkConfig);
    extern BaseType_t xIsTimelineSchedulerActive;
    xIsTimelineSchedulerActive = pdTRUE;
    
    vTaskStartScheduler();
}

// HRT Overlap
void run_test_hrt_overlap(void) {
    static TimelineTaskConfig_t xTasks[] = {
        {"HRT_A", vTestTaskHRT, (void*)(uintptr_t)5,  128, TIMELINE_TASK_HRT, 0,   5,  0},
        {"HRT_B", vTestTaskHRT, (void*)(uintptr_t)10, 128, TIMELINE_TASK_HRT, 3,   13, 0},
        {"HRT_C", vTestTaskHRT, (void*)(uintptr_t)5,  128, TIMELINE_TASK_HRT, 10,  15, 0}
    };

    TimekeeperConfig_t xTkConfig = { .ulMajorFrameTicks = 20, .ulNumSubframes = 1 };
    SchedulerConfig_t xConfig = { &xTkConfig, xTasks, 3 };

    vConfigureScheduler(&xConfig);
    vTimekeeperInit(&xTkConfig);
    extern BaseType_t xIsTimelineSchedulerActive;
    xIsTimelineSchedulerActive = pdTRUE;
    
    vTaskStartScheduler();
}

// SRT Full frame
void run_test_srt_full_frame(void) {
    static TimelineTaskConfig_t xTasks[] = {
        {"SRT_X", vTestTaskSRT, (void*)(uintptr_t)10,  128, TIMELINE_TASK_SRT, 0,   0,  0},
        {"SRT_Y", vTestTaskSRT, (void*)(uintptr_t)10, 128, TIMELINE_TASK_SRT, 0,   0, 0},
        {"SRT_Z", vTestTaskSRT, (void*)(uintptr_t)10,  128, TIMELINE_TASK_SRT, 0,  0, 0}
    };

    TimekeeperConfig_t xTkConfig = { .ulMajorFrameTicks = 30, .ulNumSubframes = 1 };
    SchedulerConfig_t xConfig = { &xTkConfig, xTasks, 3 };

    vConfigureScheduler(&xConfig);
    vTimekeeperInit(&xTkConfig);
    extern BaseType_t xIsTimelineSchedulerActive;
    xIsTimelineSchedulerActive = pdTRUE;
    
    vTaskStartScheduler();
}


// SRT Run in order
void run_test_srt_order(void) {
    static TimelineTaskConfig_t xTasks[] = {
        {"SRT_X", vTestTaskSRT, (void*)(uintptr_t)3,  128, TIMELINE_TASK_SRT, 0,   0,  0},
        {"SRT_Y", vTestTaskSRT, (void*)(uintptr_t)3, 128, TIMELINE_TASK_SRT, 0,   0, 0},
        {"SRT_Z", vTestTaskSRT, (void*)(uintptr_t)3,  128, TIMELINE_TASK_SRT, 0,  0, 0}
    };

    TimekeeperConfig_t xTkConfig = { .ulMajorFrameTicks = 20, .ulNumSubframes = 1 };
    SchedulerConfig_t xConfig = { &xTkConfig, xTasks, 3 };
    
    vConfigureScheduler(&xConfig);
    vTimekeeperInit(&xTkConfig);
    extern BaseType_t xIsTimelineSchedulerActive;
    xIsTimelineSchedulerActive = pdTRUE;
    
    vTaskStartScheduler();
}

// No Task
void run_test_no_task(void){
    static TimelineTaskConfig_t xTasks[] = {};

    TimekeeperConfig_t xTkConfig = { .ulMajorFrameTicks = 20, .ulNumSubframes = 1 };
    SchedulerConfig_t xConfig = { &xTkConfig, xTasks, 0 };

    vConfigureScheduler(&xConfig);
    vTimekeeperInit(&xTkConfig);
    extern BaseType_t xIsTimelineSchedulerActive;
    xIsTimelineSchedulerActive = pdTRUE;
    
    vTaskStartScheduler();
}

// MAIN DISPATCHER
int main(void) {
    UART_init();
    
    #ifdef test_single_hrt
        run_test_single_hrt();
    #endif
    #ifdef test_preemption
        run_test_preemption();
    #endif
    #ifdef test_deadline_miss
        run_test_deadline_miss();
    #endif
    #ifdef test_hrt_every_subframe
        run_test_hrt_every_subframe();
    #endif
    #ifdef test_hrt_stress
        run_test_hrt_stress();
    #endif
    #ifdef test_hrt_overlap
        run_test_hrt_overlap();
    #endif
    #ifdef test_srt_full_frame
        run_test_srt_full_frame();
    #endif
    #ifdef test_srt_order
        run_test_srt_order();
    #endif
    #ifdef test_no_task
        run_test_no_task();
    #endif
    return 0;
}