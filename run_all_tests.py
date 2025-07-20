#!/usr/bin/env python3
"""
Robust Test Runner for C to PlantUML Converter
Single entry point for all test executions - works locally and in CI
"""

import sys
import os
import unittest
from pathlib import Path

# Get the script directory and change to it
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add the current directory to the path so we can import the module
sys.path.insert(0, script_dir)


def run_tests_with_discovery():
    """Run tests using unittest discovery - most reliable method"""
    print("🔍 Using unittest discovery method...")
    
    # Use unittest.main() with discovery - this is the most robust approach
    # that works consistently across different environments
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(test_suite)


def run_tests_with_imports():
    """Run tests by importing test classes directly - fallback method"""
    print("📦 Using direct import method...")
    
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
        print("✅ Unit tests imported successfully")
    except ImportError as e:
        print(f"⚠️  Warning: Could not import unit tests: {e}")
    
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
        print("✅ Feature tests imported successfully")
    except ImportError as e:
        print(f"⚠️  Warning: Could not import feature tests: {e}")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(all_tests)


def main():
    """Main test runner function with multiple fallback strategies"""
    print("🧪 Running C to PlantUML Converter Tests")
    print("=" * 60)
    print(f"Working directory: {os.getcwd()}")
    print(f"Script directory: {script_dir}")
    print(f"Python version: {sys.version}")
    
    # Try multiple approaches to run tests
    result = None
    
    # Method 1: Try unittest discovery (most reliable)
    try:
        print("\n🔄 Attempting unittest discovery...")
        result = run_tests_with_discovery()
        if result.testsRun > 0:
            print("✅ Discovery method successful!")
        else:
            raise Exception("No tests found with discovery")
    except Exception as e:
        print(f"❌ Discovery failed: {e}")
        
        # Method 2: Try direct imports
        try:
            print("\n🔄 Attempting direct imports...")
            result = run_tests_with_imports()
            if result.testsRun > 0:
                print("✅ Import method successful!")
            else:
                raise Exception("No tests found with imports")
        except Exception as e2:
            print(f"❌ Import method failed: {e2}")
            
            # Method 3: Last resort - try unittest.main()
            try:
                print("\n🔄 Attempting unittest.main()...")
                # Temporarily modify argv for unittest.main()
                old_argv = sys.argv
                sys.argv = ['run_all_tests.py', 'discover', '-s', 'tests', '-p', 'test_*.py', '-v']
                
                # Capture the result
                test_suite = unittest.defaultTestLoader.discover('tests', pattern='test_*.py')
                runner = unittest.TextTestRunner(verbosity=2)
                result = runner.run(test_suite)
                
                sys.argv = old_argv
                print("✅ unittest.main() method successful!")
            except Exception as e3:
                print(f"❌ All methods failed: {e3}")
                print("\n💡 Debugging information:")
                print(f"Current directory contents: {os.listdir('.')}")
                if os.path.exists('tests'):
                    print(f"Tests directory contents: {os.listdir('tests')}")
                else:
                    print("Tests directory not found!")
                return 1
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
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
