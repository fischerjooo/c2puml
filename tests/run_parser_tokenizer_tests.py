#!/usr/bin/env python3
"""
Test runner for parser and tokenizer tests
"""

import os
import sys
import unittest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_tests():
    """Run all parser and tokenizer tests"""
    
    # Discover and run unit tests
    print("=" * 80)
    print("RUNNING PARSER AND TOKENIZER UNIT TESTS")
    print("=" * 80)
    
    # Unit tests
    unit_test_dir = project_root / "tests" / "unit"
    unit_suite = unittest.defaultTestLoader.discover(
        str(unit_test_dir), 
        pattern="test_tokenizer.py"
    )
    
    unit_runner = unittest.TextTestRunner(verbosity=2)
    unit_result = unit_runner.run(unit_suite)
    
    # Comprehensive parser tests
    comprehensive_suite = unittest.defaultTestLoader.discover(
        str(unit_test_dir), 
        pattern="test_parser_comprehensive.py"
    )
    
    comprehensive_result = unit_runner.run(comprehensive_suite)
    
    # Integration tests
    print("\n" + "=" * 80)
    print("RUNNING PARSER AND TOKENIZER INTEGRATION TESTS")
    print("=" * 80)
    
    integration_test_dir = project_root / "tests" / "integration"
    integration_suite = unittest.defaultTestLoader.discover(
        str(integration_test_dir), 
        pattern="test_parser_tokenizer_integration.py"
    )
    
    integration_result = unit_runner.run(integration_suite)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total_tests = (unit_result.testsRun + comprehensive_result.testsRun + 
                  integration_result.testsRun)
    total_failures = (len(unit_result.failures) + len(comprehensive_result.failures) + 
                     len(integration_result.failures))
    total_errors = (len(unit_result.errors) + len(comprehensive_result.errors) + 
                   len(integration_result.errors))
    
    print(f"Total tests run: {total_tests}")
    print(f"Total failures: {total_failures}")
    print(f"Total errors: {total_errors}")
    print(f"Success rate: {((total_tests - total_failures - total_errors) / total_tests * 100):.1f}%")
    
    if total_failures > 0:
        print("\nFAILURES:")
        for test, traceback in unit_result.failures + comprehensive_result.failures + integration_result.failures:
            print(f"  {test}: {traceback}")
    
    if total_errors > 0:
        print("\nERRORS:")
        for test, traceback in unit_result.errors + comprehensive_result.errors + integration_result.errors:
            print(f"  {test}: {traceback}")
    
    return total_failures == 0 and total_errors == 0

def run_specific_test(test_name):
    """Run a specific test by name"""
    print(f"Running specific test: {test_name}")
    
    # Unit tests
    unit_test_dir = project_root / "tests" / "unit"
    unit_suite = unittest.defaultTestLoader.discover(
        str(unit_test_dir), 
        pattern=f"*{test_name}*.py"
    )
    
    # Integration tests
    integration_test_dir = project_root / "tests" / "integration"
    integration_suite = unittest.defaultTestLoader.discover(
        str(integration_test_dir), 
        pattern=f"*{test_name}*.py"
    )
    
    # Combine suites
    combined_suite = unittest.TestSuite()
    combined_suite.addTests(unit_suite)
    combined_suite.addTests(integration_suite)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(combined_suite)
    
    return len(result.failures) == 0 and len(result.errors) == 0

def main():
    """Main function"""
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        success = run_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()