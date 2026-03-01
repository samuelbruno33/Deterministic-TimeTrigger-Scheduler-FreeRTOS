#include "FreeRTOS.h"
#include "task.h"
#include "timeline_scheduler.h"
#include "timekeeper.h"
#include "emulated_uart.h"
#include "trace.h"

/**
 * @brief Dummy HRT Task
 */
void vHrtTask(void *pvParams) {
    (void)pvParams;
    
    /* In a real HRT system, it would perform work and finish.
       Here we just want to test if it gets selected. But it needs to run in loop, if a task finishes, the system crash */
    for (;;) {
    }
}

/**
 * @brief Dummy SRT Task
 */
void vSrtTask(void *pvParams) {
    (void)pvParams;
while(1)
{
    for(volatile int i = 0; i < 1000; i++)
    {
        //Busy
    }
    // UART_printf("SRT task finished cycle\0");
    traceTASK_SRT_COMPLETED(pcTaskGetName(NULL));
    vNotifySrtCompletion();
}
}


int main(void)
{
    UART_init();
    UART_printf("\n--- SRT SCHEDULING TEST ---\n");

    /*
        Major Frame = 40 ticks

        HRT_A -> [0,10)
        HRT_B -> [20,30)

        SRT_X
        SRT_Y
    */

    TimelineTaskConfig_t xTasks[] = {
        {"HRT_A", vHrtTask, "A", 128, TIMELINE_TASK_HRT, 1, 4, 0},
        {"HRT_B", vHrtTask, "B", 128, TIMELINE_TASK_HRT, 6, 9, 0},
        {"HRT_C", vHrtTask, "C", 128, TIMELINE_TASK_HRT, 0, 3, 2}, // da 21 a 28
        {"HRT_D", vHrtTask, "D", 128, TIMELINE_TASK_HRT, 1, 4, 3},
        {"SRT_X", vSrtTask, "X", 128, TIMELINE_TASK_SRT, 0, 0, 0},
        {"SRT_Y", vSrtTask, "Y", 128, TIMELINE_TASK_SRT, 0, 0, 0}
    };

    TimekeeperConfig_t xTkConfig =
    {
        .ulMajorFrameTicks = 100,
        .ulNumSubframes     = 10,
    };
    SchedulerConfig_t xConfig =
    {
        .xTimekeeperConfig = &xTkConfig,
        .pxTasks           = xTasks,
        .ulNumTasks        = 6
    };

    /* Configure scheduler */
    vConfigureScheduler(&xConfig);

    /* Configure timekeeper */
    vTimekeeperInit(&xTkConfig);

    /* Activate timeline scheduler */
    extern BaseType_t xIsTimelineSchedulerActive;
    xIsTimelineSchedulerActive = pdTRUE;
    UART_printf("Expect pattern (Major Frame: 100 ticks, Subframe: 10 ticks):\n");
    UART_printf("Tick [  1 -  4 ] : HRT_A\n");
    UART_printf("Tick [  6 -  9 ] : HRT_B\n");
    UART_printf("Tick [ 20 - 23 ] : HRT_C\n");
    UART_printf("Tick [ 31 - 34 ] : HRT_D\n");
    UART_printf("All remaining gaps (0, 4-6, 9-20, 23-31, 34-99) : SRT tasks\n");
    UART_printf("\nSRT_X runs continuously in gaps until completion, \n");
    UART_printf("Pattern repeats deterministically every 100 ticks.\n\n");

    vTaskStartScheduler();

    for(;;);
}
