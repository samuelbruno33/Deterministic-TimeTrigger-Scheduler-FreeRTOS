# Test Journey

Todo list of the tests
- [x] First test of the system
- [x] Data Structures and Logic
- [x] Timekeeper
- [x] Hard-Real Time
- [x] Soft-Real Time

## Instruction

Navigate in the root of the project and execute:
```
make all
```
It will probably work fine, but it is recommended to check the makefile which needs changes.

Run the program
```
make qemu_start
```

Debug mode
```
make qemu_debug
```

## Phase 0: First test of the system

The first file created and tested is `FreeRTOS_test.c`. Designed to validate the baseline behavior of the standard FreeRTOS priority-based scheduler, before introducing any time-triggered mechanisms.

The test creates three dummy tasks (`TaskA`, `TaskB`, `TaskC`) with different priorities, where:
* `TaskA` has the highest priority,
* `TaskB` has an intermediate priority,
* `TaskC` has the lowest priority.

The purpose of this test is to observe and confirm that:

* task execution strictly follows **FreeRTOS priority rules**;
* higher-priority tasks preempt lower-priority ones;
* a task that does not block (`TaskC`) can still be preempted by higher-priority tasks;

## Phase 1: Data Structures and Logic

The file `test_data_structure.c` was created to validate the configuration API and the internal data structures of the Timeline Scheduler before integrating with the active system.

The test performs **White Box Testing** by directly inspecting the scheduler's internal tables (`xTimeline`) to verify:

* **Task Creation**: FreeRTOS handles are correctly allocated during configuration;
* **Sorting Algorithm**: HRT tasks must be automatically ordered by their absolute Start Time;
* **Error Detection**: The scheduler must detect and reject invalid configurations, such as overlapping tasks.

The purpose of this test is to confirm that:

* a set of unordered tasks (e.g., Start Times: 30, 10, 50) is correctly reordered in memory as `10 -> 30 -> 50`;
* defining two tasks with overlapping time windows triggers a `configASSERT` (captured via a flag in the test environment);
* the `vConfigureScheduler` function operates correctly without memory leaks or crashes.

The expected behavior is the output of three successful checks via UART:

## Phase 2: Timekeeper

After implementing the timekeeper, a test file `timekeeper_test.c` was created to validate the temporal logic of the Major Frame.

The test configures:

* a **Major Frame of 20 FreeRTOS ticks**;
* two **sub-frames**: `[0,10)` and `[10,20)`, used only as temporal partitions.

A single dummy task is created, which periodically blocks itself using `vTaskDelay(1000)`.

The purpose of the test is to check that:

* the FreeRTOS **Tick Hook** is correctly enabled;
* the timekeeper correctly tracks the passage of time;
* a **Major Frame reset event is generated exactly every 20 ticks**, regardless of which task is executing.

The expected behavior is the periodic emission of a `TIMEKEEPER MAJOR FRAME RESET` trace event at ticks:

```
20, 40, 60, ...
```

## Phase 3: Hard Real-Time Scheduling

To validate the core modifications made to the FreeRTOS Kernel (`tasks.c`), the file `hrt_test.c` was created. This test ensures that the system can switch from the standard priority-based logic to the deterministic Time-Triggered logic.

The test configures:

* a **Major Frame of 50 FreeRTOS ticks**;
* two **HRT tasks** placed in specific time windows: `HRT_A` [10, 20) and `HRT_B` [30, 40);
* explicit **Time Gaps** (0-10, 20-30, 40-50) where no HRT task is scheduled.

The purpose of this test is to confirm that:

* the **Kernel ignores standard priorities** when the Timeline Scheduler is active;
* the `vTaskSwitchContext` is forced to execute at every tick, ensuring precision even when the system is Idle;
* **HRT Tasks** are selected for execution exactly at their `Start Tick` and descheduled at their `End Tick`;
* the CPU correctly transitions to the **Idle state** during timeline gaps.

The expected behavior is a deterministic repeating pattern in the trace, where tasks execute only in their assigned slots:
```
[0] TASK SWITCH IN - Task: 'IDLE' 
[10] HRT SELECTED - Task: 'HRT_A' 
[20] CPU IDLE (Timeline Gap) 
[30] HRT SELECTED - Task: 'HRT_B' 
[40] CPU IDLE (Timeline Gap) 
[50] TIMEKEEPER MAJOR FRAME RESET
``` 

## Phase 4: Soft Real-Time Scheduling

To validate the integration of background tasks within the deterministic timeline, the file `srt_test.c` was created. This test verifies that Soft Real-Time (SRT) tasks can utilize the CPU during the idle gaps left by Hard Real-Time tasks without violating strict timing constraints.

The test configures:

* a **Major Frame of 100 FreeRTOS ticks**, divided into 10 sub-frames (10 ticks each);
* multiple **HRT tasks** (`HRT_A`, `HRT_B`, `HRT_C`, `HRT_D`) scheduled in specific sub-frames and relative ticks, intentionally leaving wide temporal gaps;
* two **SRT tasks** (`SRT_X`, `SRT_Y`) that perform a busy-wait workload.

The purpose of this test is to confirm that:

* SRT tasks correctly run in the background when no HRT task is ready;
* An incoming HRT task successfully preempts a running SRT task the moment its start tick arrives;
* A preempted SRT task correctly resumes its execution exactly where it left off once the HRT task completes or its slot ends;
* When an SRT task completes its workload for the frame and calls `vNotifySrtCompletion()`, the scheduler deterministically switches to the next ready SRT task in the list.

The expected behavior is a trace output showing the strict temporal enforcement of HRT tasks interspersed with the continuous, preemptable execution of SRT tasks:

```
HRT_A (Sub-frame 0, Start 1, End 4)
HRT_B (Sub-frame 0, Start 6, End 9)
HRT_C (Sub-frame 2, Start 0, End 3)
HRT_D (Sub-frame 3, Start 1, End 4)
```