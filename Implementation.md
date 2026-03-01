Politecnico di Torino - Accademic Year 2025/26
# Precise Scheduler for FreeRTOS
## Project 1 - Assignment
### Project Overview & Goals
This project implements a deterministic, timeline-based scheduler designed to replace the standard priority-based scheduling model of FreeRTOS. The primary objective is to transform the kernel into a Time-Triggered Architecture(TTA), where task execution is governed by the progression pf a global time reference(ticks), rather than asynchronous events or fixed priorities.
The scheduler currently handles:
    -Hard Real-Time periodic tasks,
    -Soft Real-Time periodic tasks.

## Key Features
### 1 - Major Frame Structure
The scheduler operates within a major frame. A major frame is the total duration of the scheduling cycle, defined at compile time (e.g. 100ms). Upon completion of a Major Frame, the scheduler resets the timeline and repeats the cycle. 
Each major frame is divided into sub-frames, smaller time windows that host a groups of tasks. 
Each sub-frame act as a dedicated time window that contains a specific set of tasks. 

### 2 - Determinism
Every task is assigned a precise start tick and end tick, relative to the start of the Major Frame.

### 2 - Task Model
Each task is implemented as a single function that executes from start to end and then terminates. Tasks do not include periodicity or self-rescheduling logic, but the scheduler controls activation timing. If two tasks need to communicate, they do through polling.

### 3 - Task Categories
**Hard Real-Time Tasks (HRT)**

These tasks have a very strict deadline: they have priority over Soft Real-Time tasks and each one is assigned to a specific sub-frame. The scheduler knows the start and end time of each task within the sub-frame. A task is spawned at the beginning of its slot and either:
- run until completion, or
- is terminated if it exceeds its deadline.

Tasks are non-preemptive, once started they cannot be interrupted.

**Soft Real-Time Tasks (SRT)**

Tasks executed during idle time left by HRT tasks. They are scheduled in a fixed compile-time order (e.g. Task_X -> Task_Y -> Task_Z). They are preemptible by any HRT Task, and there's no guarantee of completation within the frame.

### 4 - Periodic Repetition
At the end of each major frame:
- All tasks are reset and reinitialized. This can be done by destroying and recreating all tasks or by resetting their state to an initial value.
- The scheduler replays the same timeline, guaranteeing deterministic repetiotin across frames.
<br>

### Non-Functional Requirements
- **Release Jitter**: $\le$ 1 tick;
- **Overhead**: 10% CPU ($\le$ 8 tasks);
- **Portability**: QEMU Cortex-M;
- **Thread Safety**: FreeRTOS-safe synchronization;
- **Documentation**: Clear API and Timing Model;
- **Coding Guidelines**: Strictly follow [FreeRTOS Coding Guidelines](https://freertos.org/Documentation/02-Kernel/06-Coding-guidelines/02-FreeRTOS-Coding-Standard-and-Style-Guide).

### Error Handling & Edge Cases
Handles all errors with dedicated hook functions following the FreeRTOS style.

### Trace and Monitoring System
A trace module must be developed for test and validation purposes to log and visualize scheduler behavior with tick-level precision. The information to be logged are:
- Task start and end ticks;
- Deadline misses or forced terminations;
- CPU idle time.

### Testing Suite
Develop an automated test suite to validate the scheduler's correctness and robustness. The suite must include:
- Stress tests (e.g. overlapping HRT tasks);
- Edge-case tests (e.g. minimal time gaps);
- Preemption and timing consistency checks.

Each test must:
- Produce human-readable summaries;
- Include automatic pass/fail checks for regression testing.

### Configuration Framework
Create an high-level configuration framework (e.g a Python script) that enables the user to describe the target problem, perform schedulability analysis and eventually generate the FreeRTOS skeleton application.  
<br> <br>



# IMPLEMENTATION DOCUMENTATION
## Timekeeper
The timekeeper is responsible of creating and keeping track of the time passing (ticks), ensuring that the scheduler, tasks and tracing system are all synchronized within the same temporal context.<br>
### Role
The Timekeeper is responsible for maintaining three distinct temporal metrics:
- Global Tick: represents the total time since system boot;
- Major Frame Tick(```mf_tick```): Periodic counter that tracks the current position within the Major Frame;
- Active Sub-Frame: an identifier indicating which sub-frame is currently active based on the ```mf_tick```.  

### Initialization
We initialize the timekeeper using the ```TimekeeperConfig_t``` structure, calling the function ```vTimekeeperInit(TimekeeperConfig_t *cfg)```.  
### Updates and Tick Hook
The integration with FreeRTOS kernel is handled through the Timekeeper Tunnel (```timekeeper_tunnel.c```).
 - At every sistem tick, an interrupt is triggered and the kernel invokes ```vApllicationTickHook() ``` to update the ticks. 
 - Inside this function, there's a call to another function that simply updates both the global tick and the actual major frame tick (or restarts it if the major frame reached its end cycle). 
 - At the same time, it also accounts for the current subframe, and updates it if necessary.

## Timeline Scheduler
### 1. General Scheduler Architecture 
The Timeline Scheduler is designed as an overlay for the FreeRTOS kernel. It transitions the system from a priority-driven model to a strictly governed timeline. The system activation is controlle by a global status flag, ```xIsTimelineSchedulerActive```, which determines whether the kernel follows standard scheduling rules or defers to the timeline logic.  
#### 1.1 The Global Scheduler Control Block
Ath the core of the implementation is the ```TimelineControlBlock_t```. This static internal structure maintains the entire state of the scheduling environment, including:
- **Operational Status**: A flag indicating if the scheduler is currently active.
- **Temporal Context**: Stargae for the total duration of the Major Frame and the current progress of the frame tick.
- **Task Repositories**: Pointers to internal tables where tasks are managed after being processed from the user configuration.
- **Management Indexes**: Counters and pointers used to track the next task to be released and to manage round-robin execution for secondary task types.

### 2. Configuration Interface
The scheduler is configured using a static approach. This ensures that the execution pattern is determined at startup and remains immutable during runtime, which is a prerequisite for a deterministic behaviour.
#### 2.1 Configuration Structure (```SchedulerConfig_t```)
The user defines the system behaviour through the ```SchedulerConfig_t``` structure, which aggregates the following parameters: 
- ```ulMajorFrameTicks```: The total length of the cyclic timeline in system ticks.
- ```ulSubFrameTicks0```: The duration allocated to each sub-frame division.
- ```pxTasks```: A pointer to an array of ```TimelineTaskConfig_t``` structures, each representing an individual task and its timing requirements.
- ```ulNumTasks```: The total number of task definitions provided in the array.
#### 2.2 Task Definition Parameters
Each task within the configuration includes standard FreeRTOS parameters (such as the function pointer, name, and stack depth) as well as timeline-specific attributes:
- ```eType```: Specifies the category of the task (HArd Real-Time or Soft Real-Time).
- **Timing Windows**: For tasks requiring precise execution, the configuration defines the ```ulStartTick``` and ```uEndTick``` relative to the start of the Major Frame.
- **Spatial Assignment**: A ```ulSubFrameId``` to map the task to a specific sub-frame.

### 3. Initialization Process
The initialization of the scheduler is performed via the ```vConfigureScheduler``` API, which must be invoked before the FreeRTOS scheduler starts.
#### 3.1 Data Validation and Allocation
The initialization sequence follows a strict validation protocol:
1. **Input Verification**: The system ensures the configuration pointer and task arrays are valid.
2. **Resource Allocation**: The scheduler counts the number of different task types and allocates memory for internal tables using ```pvPortMAlloc```.
3. **Parameter Checking**: For tasks with strict timing, the system asserts that the start time is less than the end time and that the deadline does not exceed the Major Frame duration. 
#### 3.2 Task Preparation
During this phase, the scheduler creates the actual FreeRTOS tasks using ```xTaskCreate```. Crucially, these tasks are acreated with a unifir priority and are immediately placed in a **Supended** state. This ensures that no task can execute until the Timekeeper and Timeline Scheduler explicitly release them at the programmed tick.
#### 3.3 Deterministic Ordering and Safety Checks
The final step pf the configuration is the organization of the internal tables: 
- **Sorting**: The internal Hard Real-Time (HRT) table is sorted by ```ulStartTick``` using a bubble sort algorithm to optimize runtime lookups.
- **Overlap Detection**: The scheduler iterates through the sorted table to ensure that no two HRT tasks have overlapping time windows, which would violate the non-preemptive requirement of the HRT model.  <br>

## Tracing
The tracing subsystem provides a dedicated framework designed to monitor the deterministic behaviour of the Timeline Scheduler and standard FreeRTOS kernel operations. This module is important for validating the temporal accuracy of HRT tasks and analyzing the system's execution flow.

### 1. Architecture and Output Interface
To minimize execution and avoid heavy dependencies on standard C libaries (such as stdio.h), the trace system implements its own lightweight string manipulation functions and directly interfaces with an emulated hardware peripheral.
- **String Manipulation**: Custom, optimized (```strcpy_light```, ```strcat_light```, ```reverse``` and ```utoa```) are implemented to format log strings in memory before transmissions.
- **Hardware Interface**: Output is routed through an emulated UART module. The ```UART_printf``` function writes character by character directly to the ```UART0DATA``` memory-mapped register at address ```0x400004000UL```.  
### 2. Core Logging Mechanism
The central component of the system is the ```trace_rtos_event```funcion. It receives an event identifier and an optional data payload (typically a pointer cast to ```uintptr_t```) to generate a timestamped log entry.  
#### 2.1 Formatting Structure
Every log message is prefixed with a timestamp derived from the FreeRTOS system tick count. The general format is ```[Timestamp] EVENT_NAME - Details```, which ensures temporal traceability for offline analysis.  
#### 2.2 Event Categorization

The system tracks a comprehensive set of events defined in the ```trace_event_t``` enumeration. These events are divided into two main categories:
1. Standard Kernel Events:
    - Task lifecycle operation such as ```TASK_CREATE``` and ```TASK_DELETE```, which extract and log the human-readable task name from the Task Control Block;
    - Context switching events (```TASK_SWITCH_IN``` and ```TASK_SWITCH_OUT```) that record which task is activerly holding the CPU;
    - Inter-Process Communication events like ```QUEUE_SEND``` and ```QUEUE_RECEIVE```, which log the memory address of the affected queue as a unique identifier.<br>

2. Timeline-Specific Events: 
    - `HRT_SELECTED` / ```HRT_RELEASE```: Triggered when the timeline scheduler explicitly selects or releases an HRT task for execution;
    - `HRT_COMPLETE`: Logged when a task successfully signals the end of its workload before its deadline;
    - `MAJOR_FRAME_RESTART`: Indicates the cyclic reset of the timeline, where all tasks are reverted to a ready state;
    - `TIMEKEEPER_RESET`: Logs the exact moment the timekeeper engine resets its internal MAjor Frame counter;
    - `CPU_IDLE`: Specifically denotes a gap in the timeline where no HRT nor SRT tasks are scheduled.<br>  

#### 2.3 Kernel Hook Integration
The module acts as a bridge between FreeRTOS native trace macros  and the custom logging engine. It provides specific hook functions (e.g., `custon_trace_task_switched_in`, `custom_trace_task_create`) that capture the native kernel pointers (like `pxCurrentTCB`) and forward them to `trace_rtos_event` for processing and formatting.  
## Kernel Modifications
This section details the explicit alterations made to the native FreeRTOS codebase and the execution environment to implement the deterministic Time-Triggered Architectures (TTA).  
### Core Kernel Engine (`tasks.c`)
The core task management file was modified to bypass the default priority-driven scheduler and hand over CPU control to the timeline logic.
- Custom modules were exposed to the kernel via `#include "timeline_scheduler.h"`, `#include "timekeeper.h"` and `#include "trace.h"`.
- The native `taskSELECT_HIGHEST_PRIORITY_TASK()` macro was **conditionally** disabled. When `configUSE_TIMELINE_SCHEDULER == 1`, the kernel explicitly queries the custom timeline via `xTimelineGetSwitchIn()`. If a valid task is returned, `pxCurrentTCP` is updated; if `NULL` is returned, the CPU is handed to the native system Idle task (`xIdleTaskHandles[0]`).
- The native optimization that skips context switch evaluations when only the Idle task is ready was ooveridden. A call to `xIsSwitchRequired()` was inkected to guarantee taht the timeline is evaluated at every single system tick, ensuring absolute precision for Hard Real-Time (HRT) task preemption.  
### Kernel Configuration & Telemetry (FreeRTOSConfig.h)

The system configuration was strictly locked to support the time-triggered paradigm and map the custom telemetry framework.

- Feature Toggles: * configUSE_TIMELINE_SCHEDULER is introduced as the master toggle (set to 1).

    - configUSE_TIME_SLICING is forced to 0, completely disabling the native round-robin execution for tasks sharing the same priority.

    - configUSE_TICK_HOOK is forced to 1, which is strictly required to drive the timekeeper module at every hardware tick.

- Native Trace Mapping: Standard FreeRTOS trace macros (e.g., traceTASK_SWITCHED_IN, traceTASK_CREATE, traceTASK_DELETE, traceQUEUE_SEND) are directly mapped to the custom tracking functions (e.g., custom_trace_task_switched_in) defined in the trace module.

- Custom Event Macros: Domain-specific macros were added to track timeline states, such as traceTASK_HRT_DEADLINE_MISS, traceTASK_SRT_PREEMPTED, and traceTASK_HRT_RUNNING.










