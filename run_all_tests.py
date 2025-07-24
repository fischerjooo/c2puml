#!/usr/bin/env python3
"""
Enhanced Test Runner for C to PlantUML Converter

This script provides comprehensive testing capabilities including:
- Unittest and pytest support
- Coverage reporting
- Test categorization (unit, feature, integration)
- Detailed reporting and styling
"""

import argparse
import os
import subprocess
import sys
import time
import unittest
from pathlib import Path
from typing import List, Optional


def setup_environment():
    """Set up the testing environment."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = script_dir
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    return script_dir


def print_header(title: str, char: str = "=", width: int = 70):
    """Print a formatted header."""
    print(f"\n{char * width}")
    print(f"{title:^{width}}")
    print(f"{char * width}")


def print_subheader(title: str, char: str = "-", width: int = 50):
    """Print a formatted subheader."""
    print(f"\n{char * width}")
    print(f"{title:^{width}}")
    print(f"{char * width}")


def print_success(message: str):
    """Print a success message."""
    print(f"✅ {message}")


def print_error(message: str):
    """Print an error message."""
    print(f"❌ {message}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"⚠️  {message}")


def print_info(message: str):
    """Print an info message."""
    print(f"ℹ️  {message}")


def check_dependencies() -> bool:
    """Check if required dependencies are available."""
    print_subheader("Checking Dependencies")
    
    dependencies = {
        "pytest": "pytest --version",
        "coverage": "coverage --version"
    }
    
    missing_deps = []
    
    for dep_name, check_cmd in dependencies.items():
        try:
            result = subprocess.run(
                check_cmd.split(),
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print_success(f"{dep_name} is available")
            else:
                missing_deps.append(dep_name)
                print_error(f"{dep_name} is not available")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            missing_deps.append(dep_name)
            print_error(f"{dep_name} is not available")
    
    if missing_deps:
        print_warning(f"Missing dependencies: {', '.join(missing_deps)}")
        print_info("Install with: pip install pytest coverage")
        return False
    
    return True


def run_unittest_tests(test_pattern: str = "test_*.py", verbosity: int = 2) -> bool:
    """Run tests using unittest framework sequentially (no parallel execution)."""
    print_subheader("Running Tests with unittest")
    
    # Use unittest discovery to find and run all tests sequentially
    # unittest runs tests in a single thread by default (no parallel execution)
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover("tests", pattern=test_pattern)
    
    # Run tests sequentially in a single thread
    runner = unittest.TextTestRunner(verbosity=verbosity, stream=sys.stdout)
    result = runner.run(test_suite)
    
    # Print detailed summary
    print_subheader("unittest Summary")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print_error("FAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}")
            if verbosity > 1:
                print(f"    {traceback[:200]}...")
    
    if result.errors:
        print_error("ERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}")
            if verbosity > 1:
                print(f"    {traceback[:200]}...")
    
    return result.wasSuccessful()


def run_pytest_tests(
    test_categories: List[str],
    verbosity: int = 1,
    with_coverage: bool = False
) -> bool:
    """Run tests using pytest framework sequentially (no parallel execution)."""
    print_subheader("Running Tests with pytest")
    
    cmd = ["python", "-m", "pytest"]
    
    # Ensure sequential execution (no parallel workers)
    cmd.extend(["-n", "0"])  # Explicitly disable parallel execution
    
    # Add verbosity
    if verbosity >= 2:
        cmd.append("-v")
    elif verbosity >= 3:
        cmd.append("-vv")
    
    # Add coverage if requested
    if with_coverage:
        cmd.extend([
            "--cov=c_to_plantuml",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-fail-under=80"
        ])
    
    # Add test categories/markers
    if test_categories:
        for category in test_categories:
            cmd.extend(["-m", category])
    
    # Add test directories
    cmd.append("tests/")
    
    print_info(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, timeout=300)  # 5 minutes timeout
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print_error("Tests timed out after 5 minutes")
        return False
    except Exception as e:
        print_error(f"Error running pytest: {e}")
        return False


def run_coverage_only() -> bool:
    """Run coverage analysis without tests."""
    print_subheader("Running Coverage Analysis")
    
    commands = [
        ["coverage", "erase"],
        ["coverage", "run", "-m", "unittest", "discover", "tests"],
        ["coverage", "report", "-m"],
        ["coverage", "html"]
    ]
    
    for cmd in commands:
        print_info(f"Running: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, timeout=120)
            if result.returncode != 0:
                print_error(f"Command failed: {' '.join(cmd)}")
                return False
        except subprocess.TimeoutExpired:
            print_error(f"Command timed out: {' '.join(cmd)}")
            return False
        except Exception as e:
            print_error(f"Error running command {' '.join(cmd)}: {e}")
            return False
    
    print_success("Coverage analysis completed")
    print_info("HTML coverage report generated in htmlcov/")
    return True


def get_test_statistics() -> dict:
    """Get statistics about the test suite."""
    test_dir = Path("tests")
    if not test_dir.exists():
        return {}
    
    stats = {
        "unit_tests": 0,
        "feature_tests": 0,
        "integration_tests": 0,
        "total_test_files": 0,
        "total_lines": 0
    }
    
    for test_file in test_dir.rglob("test_*.py"):
        stats["total_test_files"] += 1
        
        # Count lines
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                stats["total_lines"] += sum(1 for _ in f)
        except Exception:
            pass
        
        # Categorize by directory
        if "unit" in str(test_file):
            stats["unit_tests"] += 1
        elif "feature" in str(test_file):
            stats["feature_tests"] += 1
        elif "integration" in str(test_file):
            stats["integration_tests"] += 1
    
    return stats


def print_test_statistics():
    """Print test suite statistics."""
    print_subheader("Test Suite Statistics")
    stats = get_test_statistics()
    
    if not stats:
        print_warning("No test statistics available")
        return
    
    print(f"Total test files: {stats['total_test_files']}")
    print(f"Unit tests: {stats['unit_tests']}")
    print(f"Feature tests: {stats['feature_tests']}")
    print(f"Integration tests: {stats['integration_tests']}")
    print(f"Total lines of test code: {stats['total_lines']}")


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(
        description="Enhanced test runner for C to PlantUML Converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_all_tests.py                      # Run all tests with unittest
  python run_all_tests.py --pytest           # Run all tests with pytest
  python run_all_tests.py --coverage         # Run with coverage
  python run_all_tests.py --category unit    # Run only unit tests
  python run_all_tests.py --stats            # Show test statistics
        """
    )
    
    parser.add_argument(
        "--pytest",
        action="store_true",
        help="Use pytest instead of unittest"
    )
    
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage analysis"
    )
    
    parser.add_argument(
        "--coverage-only",
        action="store_true",
        help="Run only coverage analysis"
    )
    
    parser.add_argument(
        "--category", "--categories",
        nargs="*",
        choices=["unit", "feature", "integration"],
        help="Run specific test categories (pytest only)"
    )
    
    parser.add_argument(
        "--verbosity", "-v",
        type=int,
        default=2,
        choices=[0, 1, 2, 3],
        help="Test output verbosity level"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show test suite statistics"
    )
    
    parser.add_argument(
        "--pattern",
        default="test_*.py",
        help="Test file pattern (unittest only)"
    )
    
    args = parser.parse_args()
    
    # Set up environment
    script_dir = setup_environment()
    
    print_header("🧪 C to PlantUML Converter Test Suite")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print(f"Script directory: {script_dir}")
    
    # Show statistics if requested
    if args.stats:
        print_test_statistics()
        if not any([args.pytest, args.coverage, args.coverage_only]):
            return 0
    
    # Check dependencies for advanced features
    deps_available = check_dependencies()
    
    # Handle coverage-only mode
    if args.coverage_only:
        if not deps_available:
            print_error("Coverage dependencies not available")
            return 1
        success = run_coverage_only()
        return 0 if success else 1
    
    # Determine test runner and run tests
    start_time = time.time()
    success = False
    
    if args.pytest and deps_available:
        success = run_pytest_tests(
            test_categories=args.category or [],
            verbosity=args.verbosity,
            with_coverage=args.coverage
        )
    else:
        if args.pytest and not deps_available:
            print_warning("pytest not available, falling back to unittest")
        if args.coverage and not deps_available:
            print_warning("Coverage not available, running without coverage")
        
        success = run_unittest_tests(
            test_pattern=args.pattern,
            verbosity=args.verbosity
        )
    
    # Final summary
    end_time = time.time()
    duration = end_time - start_time
    
    print_header("🎯 Test Execution Summary")
    print(f"Duration: {duration:.2f} seconds")
    
    if success:
        print_success("All tests passed!")
        return 0
    else:
        print_error("Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
