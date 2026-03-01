#!/bin/bash
# @file run_all_tests.sh
# @brief Test Configuration for FreeRTOS Deterministic Timeline Scheduler Test Suite
# 

OUTPUT_DIR="test_logs"
mkdir -p "$OUTPUT_DIR"

echo "  Timeline Scheduler Test Suite"

TOTAL=0
PASSED=0

# List of test scenarios
TEST_SCENARIOS=(
    "test_single_hrt" 
    "test_preemption" 
    "test_deadline_miss"
    "test_hrt_every_subframe"
    "test_hrt_stress"
    "test_hrt_overlap"
    "test_srt_full_frame"
    "test_srt_order"
    "test_no_task"
)

# Iterate through each test scenario
for test_name in "${TEST_SCENARIOS[@]}"; do
    desc=$(python3 -c "from test_config import TEST_SCENARIOS; print(TEST_SCENARIOS['$test_name']['description'])")
    timeout_val=$(python3 -c "from test_config import TEST_SCENARIOS; print(TEST_SCENARIOS['$test_name']['timeout'])")
    
    # Define output log file path
    LOG_FILE="$OUTPUT_DIR/${test_name}.log"
    
    echo ""
    echo "[$((TOTAL+1))/${#TEST_SCENARIOS[@]}] $desc"
    echo "    Scenario: $test_name"
    echo "    Timeout: ${timeout_val}s"
    
    echo "    Compiling..."
    make -C .. cleanobj > /dev/null 2>&1
    make -C .. tests CC="arm-none-eabi-gcc -D$test_name" > /dev/null 2>&1    
    # Check status
    if [ $? -ne 0 ]; then
        echo "    ❌ Compilation failed"
        ((TOTAL++))
        continue 
    fi

    # EXECUTION PHASE    
    echo "    Output will be saved to: $LOG_FILE"
    
    # Launch Qemu with emulated timer for ticks not synchronized with the host timer to avoid non-deterministic sequences
    timeout ${timeout_val}s qemu-system-arm -machine mps2-an385 -icount shift=0,align=off,sleep=off -cpu cortex-m3 \
    -kernel ../Output/demo.elf \
    -nographic \
    > "$LOG_FILE" 2>&1 &

    QEMU_PID=$!
    wait $QEMU_PID
    
    # VERIFICATION PHASE
    echo "    Verifying..."
    VERIFY_OUTPUT=$(python3 verify_test.py "$LOG_FILE" --test "$test_name" 2>&1)
    
    # Check if verification passed
    if echo "$VERIFY_OUTPUT" | grep -q "ALL CHECKS PASSED"; then
        echo "    ✅ PASSED"
        ((PASSED++))
    else
        echo "    ❌ FAILED"
        echo "$VERIFY_OUTPUT"
    fi
    
    ((TOTAL++))
    echo ""
done

# FINAL SUMMARY
echo "  Summary: $PASSED/$TOTAL passed"

[ $PASSED -eq $TOTAL ] && exit 0 || exit 1