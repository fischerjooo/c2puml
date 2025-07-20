#!/usr/bin/env python3
"""
Simplified Test Runner for C to PlantUML Converter
Single entry point for all test executions
"""

import sys
import unittest
import os
from pathlib import Path

# Get the script directory and change to it
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add the current directory to the path so we can import the module
sys.path.insert(0, script_dir)


def run_tests():
    """Run all tests and return the test result"""
    # Create test suite
    all_tests = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    # Import and add unit tests
    try:
        from tests.unit.test_config import TestConfig
        from tests.unit.test_generator import TestGenerator
        from tests.unit.test_parser import TestCParser
        from tests.unit.test_project_analyzer import TestProjectAnalyzer
        
        all_tests.addTest(loader.loadTestsFromTestCase(TestCParser))
        all_tests.addTest(loader.loadTestsFromTestCase(TestProjectAnalyzer))
        all_tests.addTest(loader.loadTestsFromTestCase(TestGenerator))
        all_tests.addTest(loader.loadTestsFromTestCase(TestConfig))
    except ImportError as e:
        print(f"Warning: Could not import unit tests: {e}")
    
    # Import and add feature tests
    try:
        from tests.feature.test_integration import TestIntegration
        from tests.feature.test_parser_features import TestParserFeatures
        from tests.feature.test_generator_features import TestGeneratorFeatures
        from tests.feature.test_project_analysis_features import TestProjectAnalysisFeatures
        
        all_tests.addTest(loader.loadTestsFromTestCase(TestIntegration))
        all_tests.addTest(loader.loadTestsFromTestCase(TestParserFeatures))
        all_tests.addTest(loader.loadTestsFromTestCase(TestGeneratorFeatures))
        all_tests.addTest(loader.loadTestsFromTestCase(TestProjectAnalysisFeatures))
    except ImportError as e:
        print(f"Warning: Could not import feature tests: {e}")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(all_tests)


def main():
    print("🧪 Running C to PlantUML Converter Tests")
    print("=" * 50)
    print(f"Working directory: {os.getcwd()}")
    print(f"Script directory: {script_dir}")
    
    result = run_tests()
    
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
