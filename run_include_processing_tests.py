#!/usr/bin/env python3
"""
Test runner for include header processing tests
Runs all tests related to include header processing functionality
"""

import sys
import subprocess
import os
from pathlib import Path


def run_tests():
    """Run all include processing tests"""
    print("=" * 80)
    print("INCLUDE HEADER PROCESSING TEST SUITE")
    print("=" * 80)
    print()
    
    # Define test files to run
    test_files = [
        "tests/unit/test_include_processing.py",
        "tests/unit/test_include_processing_enhanced.py",
        "tests/feature/test_include_processing_features.py",
        "tests/feature/test_include_processing_enhanced_features.py",
        "tests/feature/test_include_processing_integration.py",
        "tests/integration/test_include_processing_comprehensive.py"
    ]
    
    total_tests = 0
    total_passed = 0
    total_failed = 0
    
    print("Running include header processing tests...")
    print()
    
    for test_file in test_files:
        if not os.path.exists(test_file):
            print(f"⚠️  Test file not found: {test_file}")
            continue
            
        print(f"Running: {test_file}")
        print("-" * 60)
        
        try:
            # Run the test file
            result = subprocess.run([
                sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"
            ], capture_output=True, text=True, cwd=Path(__file__).parent)
            
            # Parse output to count tests
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'collected' in line and 'items' in line:
                    # Extract test count
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'collected':
                            if i + 2 < len(parts):
                                test_count = int(parts[i + 1])
                                total_tests += test_count
                            break
                elif 'passed' in line and 'failed' in line:
                    # Extract passed/failed counts
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'passed':
                            if i + 1 < len(parts):
                                passed = int(parts[i + 1])
                                total_passed += passed
                        elif part == 'failed':
                            if i + 1 < len(parts):
                                failed = int(parts[i + 1])
                                total_failed += failed
            
            # Print results
            if result.returncode == 0:
                print("✅ All tests passed")
            else:
                print("❌ Some tests failed")
                print("Error output:")
                print(result.stderr)
            
            print()
            
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print()
    
    if total_failed == 0:
        print("🎉 All include header processing tests passed!")
        print()
        print("Test coverage includes:")
        print("✅ C to H file relationships")
        print("✅ H to H file relationships") 
        print("✅ Typedef relationships")
        print("✅ Complex include scenarios")
        print("✅ Edge cases and error handling")
        return 0
    else:
        print("❌ Some tests failed. Please check the output above.")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)