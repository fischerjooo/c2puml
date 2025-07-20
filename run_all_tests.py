#!/usr/bin/env python3
"""
Comprehensive Test Runner for C to PlantUML Converter
Single entry point for all test executions - both local and CI/CD
"""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add the current directory to the path so we can import the module
sys.path.insert(0, str(Path(__file__).parent))


def run_unit_tests():
    """Run all unit tests and return the test result"""
    # Import and run unit tests from test files
    from tests.unit.test_config import TestConfig
    from tests.unit.test_generator import TestGenerator
    from tests.unit.test_parser import TestCParser
    from tests.unit.test_project_analyzer import TestProjectAnalyzer

    # Create test suite for unit tests
    unit_suite = unittest.TestSuite()

    # Add unit test classes using TestLoader
    loader = unittest.TestLoader()
    unit_suite.addTest(loader.loadTestsFromTestCase(TestCParser))
    unit_suite.addTest(loader.loadTestsFromTestCase(TestProjectAnalyzer))
    unit_suite.addTest(loader.loadTestsFromTestCase(TestGenerator))
    unit_suite.addTest(loader.loadTestsFromTestCase(TestConfig))

    # Run unit tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(unit_suite)

    return result


def run_feature_tests():
    """Run all feature-based tests and return the test result"""
    # Import feature test classes
    from tests.feature.test_configuration_features import TestConfigurationFeatures
    from tests.feature.test_error_handling_features import TestErrorHandlingFeatures
    from tests.feature.test_generator_features import TestGeneratorFeatures
    from tests.feature.test_parser_features import TestParserFeatures
    from tests.feature.test_performance_features import TestPerformanceFeatures
    from tests.feature.test_project_analysis_features import TestProjectAnalysisFeatures
    from tests.feature.test_workflow_features import TestWorkflowFeatures

    # Create test suite for feature tests
    feature_suite = unittest.TestSuite()

    # Add feature test classes using TestLoader
    loader = unittest.TestLoader()
    feature_suite.addTest(loader.loadTestsFromTestCase(TestParserFeatures))
    feature_suite.addTest(loader.loadTestsFromTestCase(TestProjectAnalysisFeatures))
    feature_suite.addTest(loader.loadTestsFromTestCase(TestGeneratorFeatures))
    feature_suite.addTest(loader.loadTestsFromTestCase(TestConfigurationFeatures))
    feature_suite.addTest(loader.loadTestsFromTestCase(TestWorkflowFeatures))
    feature_suite.addTest(loader.loadTestsFromTestCase(TestErrorHandlingFeatures))
    feature_suite.addTest(loader.loadTestsFromTestCase(TestPerformanceFeatures))

    # Run feature tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(feature_suite)

    return result


def main():
    """Main test runner function"""
    print("🧪 Running C to PlantUML Converter Tests")
    print("=" * 60)

    # Track overall results
    total_tests_run = 0
    total_failures = 0
    total_errors = 0
    all_failures = []
    all_errors = []

    # Run unit tests
    print("\n📋 Running Unit Tests...")
    print("-" * 40)
    unit_result = run_unit_tests()

    total_tests_run += unit_result.testsRun
    total_failures += len(unit_result.failures)
    total_errors += len(unit_result.errors)
    all_failures.extend(unit_result.failures)
    all_errors.extend(unit_result.errors)

    # Run feature tests
    print("\n📋 Running Feature Tests...")
    print("-" * 40)
    feature_result = run_feature_tests()

    total_tests_run += feature_result.testsRun
    total_failures += len(feature_result.failures)
    total_errors += len(feature_result.errors)
    all_failures.extend(feature_result.failures)
    all_errors.extend(feature_result.errors)

    # Print comprehensive summary
    print("\n" + "=" * 60)
    print("COMPREHENSIVE TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests run: {total_tests_run}")
    print(f"Unit Tests: {unit_result.testsRun}")
    print(f"Feature Tests: {feature_result.testsRun}")
    print(f"Total Failures: {total_failures}")
    print(f"Total Errors: {total_errors}")
    unit_skipped = len(unit_result.skipped) if hasattr(unit_result, "skipped") else 0
    feature_skipped = (
        len(feature_result.skipped) if hasattr(feature_result, "skipped") else 0
    )
    print(f"Skipped: {unit_skipped + feature_skipped}")

    if all_failures:
        print("\n❌ FAILURES:")
        for test, traceback in all_failures:
            print(f"  {test}: {traceback}")

    if all_errors:
        print("\n❌ ERRORS:")
        for test, traceback in all_errors:
            print(f"  {test}: {traceback}")

    # Return appropriate exit code
    if total_failures == 0 and total_errors == 0:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {total_failures + total_errors} test(s) failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
