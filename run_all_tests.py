#!/usr/bin/env python3
"""
Test Runner for C to PlantUML Converter
Simple and elegant test execution using unittest discovery
"""

import sys
import os
import unittest
from pathlib import Path

# Ensure the project root (parent of 'tests') is in sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = script_dir  # If 'tests' is in the same directory as this script
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def main():
    """Run all tests using unittest discovery"""
    print("🧪 Running C to PlantUML Converter Tests")
    print("=" * 50)
    print(f"Working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        test_category = sys.argv[1].lower()
        if test_category in ['unit', 'feature', 'integration']:
            print(f"Running {test_category} tests only...")
            test_suite = unittest.TestLoader().discover(f'tests/{test_category}', pattern='test_*.py')
        else:
            print(f"Unknown test category: {test_category}")
            print("Available categories: unit, feature, integration")
            return 1
    else:
        # Use unittest discovery to find and run all tests
        test_loader = unittest.TestLoader()
        test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\n❌ ERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {len(result.failures) + len(result.errors)} test(s) failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
