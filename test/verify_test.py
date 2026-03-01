#!/usr/bin/env python3
##
# @file verify_test.py
# @brief Verify scheduler test results against expected execution pattern
#

"""Verify scheduler test results against expected execution pattern"""

import sys
import re
from typing import List, Tuple, Optional
from test_config import TEST_SCENARIOS

def parse_log(log_file: str) -> List[Tuple[int, str]]:
    """Parse log file and extract (timestamp, event) pairs"""
    events = []
    
    with open(log_file, 'r') as f:
        for line in f:
            match = re.match(r'\[(\d+)\]\s+(.+)', line.strip())            
            if match:
                timestamp = int(match.group(1))
                event = match.group(2).strip()
                events.append((timestamp, event))
    
    return events

def normalize_event(event: str) -> str:
    """Normalize event string for comparison"""
    event = ' '.join(event.split())
    return event.upper()

def compare_events(actual: List[Tuple[int, str]], 
                   expected: List[Tuple[int, str]]) -> Tuple[bool, List[str]]:
    """Compare actual events with expected pattern - EXACT timing match required"""
    errors = []
    warnings = []
    
    # Check we have events
    if len(actual) == 0:
        errors.append("No events found in log")
        return False, errors
    
    print(f"\nFound {len(actual)} events in log")
    print(f"\nExpected {len(expected)} events\n")
    
    # Compare length
    if len(actual) != len(expected):
        warnings.append(f"Event count mismatch: got {len(actual)}, expected {len(expected)}")
    
    # Compare each expected event
    min_len = min(len(actual), len(expected))
    
    for i in range(min_len):
        exp_time, exp_event = expected[i]
        act_time, act_event = actual[i]
        
        # Normalize events for comparison
        exp_event_norm = normalize_event(exp_event)
        act_event_norm = normalize_event(act_event)
        
        # Check event matches
        event_match = (exp_event_norm == act_event_norm or 
                      exp_event_norm in act_event_norm or 
                      act_event_norm in exp_event_norm)
        
        tolerance = 1
        time_match = abs(act_time - exp_time) <= tolerance
        
        if event_match and time_match:
            print(f"✅ Event {i+1:2d}: [{act_time:5d}] {act_event}")
        else:
            if not event_match:
                error_msg = f"❌ Event mismatch at position {i+1}:\n"
                error_msg += f"     Expected: [{exp_time:5d}] {exp_event}\n"
                error_msg += f"     Actual:   [{act_time:5d}] {act_event}"
                errors.append(error_msg)
            elif not time_match:
                error_msg = f"❌ Timing mismatch at position {i+1}:\n"
                error_msg += f"     Expected: [{exp_time:5d}] {exp_event}\n"
                error_msg += f"     Actual:   [{act_time:5d}] {act_event}\n"
                error_msg += f"     Difference: {act_time - exp_time:+d}"
                errors.append(error_msg)

    if len(actual) < len(expected):
        print(f"\n❌ Missing {len(expected) - len(actual)} expected events:")
        for i in range(len(actual), len(expected)):
            exp_time, exp_event = expected[i]
            print(f"    [{exp_time:5d}ms] {exp_event}")
            errors.append(f"Missing event: [{exp_time}ms] {exp_event}")
    
    # Print warnings if any
    if warnings and len(errors) == 0:
        print(f"\n  {len(warnings)} warnings (not blocking):")
        for w in warnings:
            print(f"    {w}")
    
    passed = len(errors) == 0
    return passed, errors

def verify_test(log_file: str, test_name: Optional[str] = None) -> bool:
    """Verify a test log file against expected pattern"""
    
    print("="*70)
    print("  Log Verification")
    print("="*70)
    
    # Determine test scenario
    if test_name is None:
        # Try to infer from log file name
        for scenario in TEST_SCENARIOS:
            if scenario in log_file:
                test_name = scenario
                break
        
        if test_name is None:
            print("❌ Cannot determine test scenario")
            return False
    
    if test_name not in TEST_SCENARIOS:
        print(f"❌ Unknown test scenario: {test_name}")
        print(f"   Available scenarios: {', '.join(TEST_SCENARIOS.keys())}")
        return False
    
    config = TEST_SCENARIOS[test_name]
    print(f"\nTest: {config['description']}")
    print(f"Scenario: {test_name}")
    print(f"Log file: {log_file}\n")
    
    # Parse log
    try:
        actual_events = parse_log(log_file)
    except FileNotFoundError:
        print(f"❌ Log file not found: {log_file}")
        return False
    except Exception as e:
        print(f"❌ Error parsing log: {e}")
        return False
    
    # Compare with expected pattern
    expected_pattern = config['expected_pattern']
    passed, errors = compare_events(actual_events, expected_pattern)
    
    print("\n" + "="*70)
    if passed:
        print("✅ ALL CHECKS PASSED")
        print("="*70)
        return True
    else:
        print(f"❌ VERIFICATION FAILED ({len(errors)} errors)")
        print("="*70)
        print("\nErrors:")
        for i, error in enumerate(errors, 1):
            print(f"\n{i}. {error}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: verify_test.py <log_file> [--test <test_name>]")
        print("\nAvailable test scenarios:")
        for name, config in TEST_SCENARIOS.items():
            print(f"  - {name}: {config['description']}")
        sys.exit(1)
    
    log_file = sys.argv[1]
    test_name = None
    
    if len(sys.argv) > 2 and sys.argv[2] == '--test':
        if len(sys.argv) > 3:
            test_name = sys.argv[3]
    
    success = verify_test(log_file, test_name)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()