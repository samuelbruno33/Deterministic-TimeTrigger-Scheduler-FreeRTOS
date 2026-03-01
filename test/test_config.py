##
# @file test_config.py
# @brief Test Configuration for FreeRTOS Deterministic Timeline Scheduler Test Suite
#


TEST_SCENARIOS = {
    "test_single_hrt": {
        "description": "Test 1: Single HRT (Starts at 10, ends at 15, idle until 50)",
        "timeout": 3,
        "expected_pattern": [
            (0, "TASK CREATE - Task: 'HRT_A'"),
            (0, "TASK CREATE - Task: 'IDLE'"),
            (0, "TASK_SWITCH_IN - Task: 'IDLE'"),
            
            (10, "TASK_SWITCH_OUT - Task: 'IDLE'"),
            (10, "TASK_SWITCH_IN - Task: 'HRT_A'"),
            (15, "TASK_SWITCH_OUT - Task: 'HRT_A'"),
            (15, "CPU IDLE (Timeline Gap)"),
            (15, "TASK_SWITCH_IN - Task: 'IDLE'"),
            (50, "MAJOR FRAME RESTART - All tasks reset to READY"),
            
            (60, "TASK_SWITCH_OUT - Task: 'IDLE'"),
            (60, "TASK_SWITCH_IN - Task: 'HRT_A'"),
            (65, "TASK_SWITCH_OUT - Task: 'HRT_A'"),
            (65, "CPU IDLE (Timeline Gap)"),
            (65, "TASK_SWITCH_IN - Task: 'IDLE'"),
            (100, "MAJOR FRAME RESTART - All tasks reset to READY")
        ]
    },

    "test_preemption": {
        "description": "Test 2: Preemption HRT on SRT",
        "timeout": 3,
        "expected_pattern": [
            (0, "TASK CREATE - Task: 'HRT_A'"),
            (0, "TASK CREATE - Task: 'SRT_X'"),
            (0, "TASK CREATE - Task: 'IDLE'"),
            (0, "TASK_SWITCH_IN - Task: 'IDLE'"),
            (1, "TASK_SWITCH_OUT - Task: 'IDLE'"),
            (1, "SRT_RUNNING - Task: 'SRT_X'"),
            (1, "TASK_SWITCH_IN - Task: 'SRT_X'"),
            (20, "SRT_PREEMPTED - Task: 'SRT_X'"),
            (20, "TASK_SWITCH_OUT - Task: 'SRT_X'"),
            (20, "TASK_SWITCH_IN - Task: 'HRT_A'"),
            (25, "TASK_SWITCH_OUT - Task: 'HRT_A'"),
            (25, "SRT_RESUMED - Task: 'SRT_X'"),
            (25, "TASK_SWITCH_IN - Task: 'SRT_X'"),
            (46, "TASK_SWITCH_OUT - Task: 'SRT_X'"),
            (46, "CPU IDLE (Timeline Gap)"),
            (46, "TASK_SWITCH_IN - Task: 'IDLE'"),
            (50, "MAJOR FRAME RESTART - All tasks reset to READY"),
            (50, "TASK_SWITCH_OUT - Task: 'IDLE'"),
            (50, "SRT_RUNNING - Task: 'SRT_X'"),
            (50, "TASK_SWITCH_IN - Task: 'SRT_X'"),
            (70, "SRT_PREEMPTED - Task: 'SRT_X'"),
            (70, "TASK_SWITCH_OUT - Task: 'SRT_X'"),
            (70, "TASK_SWITCH_IN - Task: 'HRT_A'"),
            (75, "TASK_SWITCH_OUT - Task: 'HRT_A'"),
            (75, "SRT_RESUMED - Task: 'SRT_X'"),
            (75, "TASK_SWITCH_IN - Task: 'SRT_X'"),
            (95, "TASK_SWITCH_OUT - Task: 'SRT_X'"),
            (95, "CPU IDLE (Timeline Gap)"),
            (95, "TASK_SWITCH_IN - Task: 'IDLE'"),
            (100, "MAJOR FRAME RESTART - All tasks reset to READY")
        ]
    },
    
    "test_deadline_miss": {
        "description": "Test 3: HRT Deadline Miss",
        "timeout": 5,
        "expected_pattern": [
            (0, "TASK CREATE - Task: 'HRT_A'"),
            (0, "TASK CREATE - Task: 'IDLE'"),
            (0, "TASK_SWITCH_IN - Task: 'IDLE'"),
            
            (10, "TASK_SWITCH_OUT - Task: 'IDLE'"),
            (10, "TASK_SWITCH_IN - Task: 'HRT_A'"),
            (20, "HRT_ABORTED - Task: 'HRT_A'"),
            (20, "TASK_SWITCH_OUT - Task: 'HRT_A'"),
            (20, "CPU IDLE (Timeline Gap)"),
            (20, "TASK_SWITCH_IN - Task: 'IDLE'"),
            (50, "MAJOR FRAME RESTART - All tasks reset to READY"),

            (60, "TASK_SWITCH_OUT - Task: 'IDLE'"),
            (60, "TASK_SWITCH_IN - Task: 'HRT_A'"),
            (70, "HRT_ABORTED - Task: 'HRT_A'"),
            (70, "TASK_SWITCH_OUT - Task: 'HRT_A'"),
            (70, "CPU IDLE (Timeline Gap)"),
            (70, "TASK_SWITCH_IN - Task: 'IDLE'"),
        ]
    },

    "test_hrt_every_subframe": {
        "description": "Test 4: HRT in every subframe with idle gaps",
        "timeout": 3,
        "expected_pattern": [
            (0, "TASK CREATE - Task: 'HRT_0'"),
            (0, "TASK CREATE - Task: 'HRT_1'"),
            (0, "TASK CREATE - Task: 'HRT_2'"),
            (0, "TASK CREATE - Task: 'HRT_3'"),
            (0, "TASK CREATE - Task: 'IDLE'"),
            (0, "TASK_SWITCH_IN - Task: 'IDLE'"),
            (0, "TASK_SWITCH_OUT - Task: 'IDLE'"),
            (0, "TASK_SWITCH_IN - Task: 'HRT_0'"),
            (5, "TASK_SWITCH_OUT - Task: 'HRT_0'"),
            (5, "CPU IDLE (Timeline Gap)"),

            (5, "TASK_SWITCH_IN - Task: 'IDLE'"),
            (10, "TASK_SWITCH_OUT - Task: 'IDLE'"),
            (10, "TASK_SWITCH_IN - Task: 'HRT_1'"),
            (15, "TASK_SWITCH_OUT - Task: 'HRT_1'"),
            (15, "CPU IDLE (Timeline Gap)"),

            (15, "TASK_SWITCH_IN - Task: 'IDLE'"),
            (20, "TASK_SWITCH_OUT - Task: 'IDLE'"),
            (20, "TASK_SWITCH_IN - Task: 'HRT_2'"),
            (25, "TASK_SWITCH_OUT - Task: 'HRT_2'"),
            (25, "CPU IDLE (Timeline Gap)"),

            (25, "TASK_SWITCH_IN - Task: 'IDLE'"),
            (30, "TASK_SWITCH_OUT - Task: 'IDLE'"),
            (30, "TASK_SWITCH_IN - Task: 'HRT_3'"),
            (35, "TASK_SWITCH_OUT - Task: 'HRT_3'"),
            (35, "CPU IDLE (Timeline Gap)"),

            (35, "TASK_SWITCH_IN - Task: 'IDLE'"),
            (40, "MAJOR FRAME RESTART - All tasks reset to READY")
        ]
    },

    "test_hrt_stress": {
        "description": "Test 5: HRT back-to-back without Idle time",
        "timeout": 5,
        "expected_pattern": [
            (0 , "TASK CREATE - Task: 'HRT_A'"),
            (0 , "TASK CREATE - Task: 'HRT_B'"),
            (0 , "TASK CREATE - Task: 'HRT_C'"),
            (0 , "TASK CREATE - Task: 'IDLE'"),
            (0 , "TASK_SWITCH_IN - Task: 'IDLE'"),
            (1 , "TASK_SWITCH_OUT - Task: 'IDLE'"),
            (1 , "TASK_SWITCH_IN - Task: 'HRT_A'"),
            (5 , "HRT_ABORTED - Task: 'HRT_A'"),
            (5 , "TASK_SWITCH_OUT - Task: 'HRT_A'"),
            (5 , "TASK_SWITCH_IN - Task: 'HRT_B'"),
            (15 , "HRT_ABORTED - Task: 'HRT_B'"),
            (15 , "TASK_SWITCH_OUT - Task: 'HRT_B'"),
            (15 , "TASK_SWITCH_IN - Task: 'HRT_C'"),
            (20 , "MAJOR FRAME RESTART - All tasks reset to READY"),
            (20 , "TASK_SWITCH_OUT - Task: 'HRT_C'"),
            (20 , "TASK_SWITCH_IN - Task: 'HRT_A'"),
            (25 , "HRT_ABORTED - Task: 'HRT_A'"),
            (25 , "TASK_SWITCH_OUT - Task: 'HRT_A'"),
            (25 , "TASK_SWITCH_IN - Task: 'HRT_B'"),
            (35 , "HRT_ABORTED - Task: 'HRT_B'"),
            (35 , "TASK_SWITCH_OUT - Task: 'HRT_B'"),
            (35 , "TASK_SWITCH_IN - Task: 'HRT_C'"),
            (40 , "MAJOR FRAME RESTART - All tasks reset to READY")
        ]
    },

    "test_hrt_overlap": {
        "description": "Test 6: HRT Overlapping inside a subframe",
        "timeout": 5,
        "expected_pattern": [
            (0, "TASK CREATE - Task: 'HRT_A'"),
            (0, "TASK CREATE - Task: 'HRT_B'"),
            (0, "TASK CREATE - Task: 'HRT_C'"),
            (0, "ERROR: Hard Real-Time task overlap found in configured tasks layout")
        ]
    },

    "test_srt_full_frame": {
        "description": "Test 7: SRT Tasks sufficient to fully cover a sub-frame",
        "timeout": 5,
        "expected_pattern": [
        ]
    },

    "test_srt_order": {
        "description": "Test 8: Only SRT Tasks running. Must run in the configured order",
        "timeout": 5,
        "expected_pattern": [
            (0, "TASK CREATE - Task: 'SRT_X'"),
            (0, "TASK CREATE - Task: 'SRT_Y'"),
            (0, "TASK CREATE - Task: 'SRT_Z'"),
            (0, "TASK CREATE - Task: 'IDLE'"),
            (0, "TASK_SWITCH_IN - Task: 'IDLE'"),
            (1, "TASK_SWITCH_OUT - Task: 'IDLE'"),
            (1, "SRT_RUNNING - Task: 'SRT_X'"),
            (1, "TASK_SWITCH_IN - Task: 'SRT_X'"),
            (5, "TASK_SWITCH_OUT - Task: 'SRT_X'"),
            (5, "SRT_RUNNING - Task: 'SRT_Y'"),
            (5, "TASK_SWITCH_IN - Task: 'SRT_Y'"),
            (8, "TASK_SWITCH_OUT - Task: 'SRT_Y'"),
            (8, "SRT_RUNNING - Task: 'SRT_Z'"),
            (8, "TASK_SWITCH_IN - Task: 'SRT_Z'"),
            (11, "TASK_SWITCH_OUT - Task: 'SRT_Z'"),
            (11, "CPU IDLE (Timeline Gap)"),
            (11, "TASK_SWITCH_IN - Task: 'IDLE'"),
            (20, "MAJOR FRAME RESTART - All tasks reset to READY"),
            (20, "TASK_SWITCH_OUT - Task: 'IDLE'"),
            (20, "SRT_RUNNING - Task: 'SRT_X'"),
            (20, "TASK_SWITCH_IN - Task: 'SRT_X'"),
            (23, "TASK_SWITCH_OUT - Task: 'SRT_X'"),
            (23, "SRT_RUNNING - Task: 'SRT_Y'"),
            (23, "TASK_SWITCH_IN - Task: 'SRT_Y'"),
            (26, "TASK_SWITCH_OUT - Task: 'SRT_Y'"),
            (26, "SRT_RUNNING - Task: 'SRT_Z'"),
            (26, "TASK_SWITCH_IN - Task: 'SRT_Z'"),
            (29, "TASK_SWITCH_OUT - Task: 'SRT_Z'"),
            (29, "CPU IDLE (Timeline Gap)"),
            (29, "TASK_SWITCH_IN - Task: 'IDLE'"),
            (40, "MAJOR FRAME RESTART - All tasks reset to READY"),
            (40, "TASK_SWITCH_OUT - Task: 'IDLE'"),
            (40, "SRT_RUNNING - Task: 'SRT_X'"),
            (40, "TASK_SWITCH_IN - Task: 'SRT_X'"),
            (43, "TASK_SWITCH_OUT - Task: 'SRT_X'"),
            (43, "SRT_RUNNING - Task: 'SRT_Y'"),
            (43, "TASK_SWITCH_IN - Task: 'SRT_Y'"),
            (46, "TASK_SWITCH_OUT - Task: 'SRT_Y'"),
            (46, "SRT_RUNNING - Task: 'SRT_Z'"),
            (46, "TASK_SWITCH_IN - Task: 'SRT_Z'"),
            (49, "TASK_SWITCH_OUT - Task: 'SRT_Z'"),
            (49, "CPU IDLE (Timeline Gap)"),
            (49, "TASK_SWITCH_IN - Task: 'IDLE'"),
            (60, "MAJOR FRAME RESTART - All tasks reset to READY")
        ]
    },

    "test_no_task": {
        "description": "Test 6: No Tasks inserted",
        "timeout": 5,
        "expected_pattern": [
            (0, "ERROR: No Tasks configured to be scheduled")
        ]
    },
}