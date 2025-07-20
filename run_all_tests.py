#!/usr/bin/env python3
"""
Simplified Test Runner for C to PlantUML Converter
Single entry point for all test executions
"""

import sys
import unittest
from pathlib import Path

# Add the current directory to the path so we can import the module
sys.path.insert(0, str(Path(__file__).parent))


def run_tests():
    """Run all tests and return the test result"""
    # Discover and run all tests
    loader = unittest.TestLoader()
    
    # Load unit tests
    unit_suite = loader.discover('tests/unit', pattern='test_*.py')
    
    # Load feature tests
    feature_suite = loader.discover('tests/feature', pattern='test_*.py')
    
    # Combine all test suites
    all_tests = unittest.TestSuite()
    all_tests.addTests(unit_suite)
    all_tests.addTests(feature_suite)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(all_tests)


def main():
    """Main test runner function"""
    print("🧪 Running C to PlantUML Converter Tests")
    print("=" * 50)
    
    # Run all tests
    result = run_tests()
    
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
    
    # Return appropriate exit code
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {len(result.failures) + len(result.errors)} test(s) failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
