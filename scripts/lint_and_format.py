#!/usr/bin/env python3
"""
Comprehensive linting and formatting script for C to PlantUML converter.

This script runs all quality checks including:
- Code formatting (black, isort)
- Linting (flake8, pylint, bandit)
- Type checking (mypy)
- Documentation style (pydocstyle)
- Security checks (safety)
- Test coverage (pytest-cov)

Usage:
    python scripts/lint_and_format.py [--fix] [--check-only] [--verbose]
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional
import os


class LintingError(Exception):
    """Exception raised when linting fails."""
    pass


class QualityChecker:
    """Comprehensive quality checker for the codebase."""
    
    def __init__(self, verbose: bool = False, fix: bool = False, check_only: bool = False):
        self.verbose = verbose
        self.fix = fix
        self.check_only = check_only
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def log(self, message: str) -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(f"[INFO] {message}")
    
    def run_command(self, cmd: List[str], description: str) -> bool:
        """Run a command and return success status."""
        self.log(f"Running {description}...")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=not self.verbose,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                self.log(f"✓ {description} passed")
                return True
            else:
                error_msg = f"✗ {description} failed"
                if result.stdout:
                    error_msg += f"\nSTDOUT: {result.stdout}"
                if result.stderr:
                    error_msg += f"\nSTDERR: {result.stderr}"
                
                self.errors.append(error_msg)
                self.log(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"✗ {description} failed with exception: {e}"
            self.errors.append(error_msg)
            self.log(error_msg)
            return False
    
    def check_black(self) -> bool:
        """Check code formatting with black."""
        cmd = ["black", "--check", "--diff", "."]
        if self.fix:
            cmd = ["black", "."]
        
        return self.run_command(cmd, "Black code formatting")
    
    def check_isort(self) -> bool:
        """Check import sorting with isort."""
        cmd = ["isort", "--check-only", "--diff", "."]
        if self.fix:
            cmd = ["isort", "."]
        
        return self.run_command(cmd, "isort import sorting")
    
    def check_flake8(self) -> bool:
        """Check code style with flake8."""
        cmd = ["flake8", "."]
        return self.run_command(cmd, "flake8 code style")
    
    def check_pylint(self) -> bool:
        """Check code quality with pylint."""
        cmd = ["pylint", "c_to_plantuml", "tests"]
        return self.run_command(cmd, "pylint code quality")
    
    def check_mypy(self) -> bool:
        """Check type annotations with mypy."""
        cmd = ["mypy", "c_to_plantuml"]
        return self.run_command(cmd, "mypy type checking")
    
    def check_bandit(self) -> bool:
        """Check security with bandit."""
        cmd = ["bandit", "-r", "c_to_plantuml"]
        return self.run_command(cmd, "bandit security check")
    
    def check_pydocstyle(self) -> bool:
        """Check documentation style with pydocstyle."""
        cmd = ["pydocstyle", "c_to_plantuml"]
        return self.run_command(cmd, "pydocstyle documentation")
    
    def check_safety(self) -> bool:
        """Check dependencies for security vulnerabilities."""
        cmd = ["safety", "check"]
        return self.run_command(cmd, "safety dependency check")
    
    def run_tests(self) -> bool:
        """Run tests with coverage."""
        cmd = [
            "pytest",
            "--cov=c_to_plantuml",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml:coverage.xml",
            "tests/"
        ]
        return self.run_command(cmd, "pytest with coverage")
    
    def run_all_checks(self) -> bool:
        """Run all quality checks."""
        self.log("Starting comprehensive quality check...")
        
        checks = [
            ("Black formatting", self.check_black),
            ("Import sorting", self.check_isort),
            ("Code style", self.check_flake8),
            ("Code quality", self.check_pylint),
            ("Type checking", self.check_mypy),
            ("Security", self.check_bandit),
            ("Documentation", self.check_pydocstyle),
            ("Dependencies", self.check_safety),
        ]
        
        if not self.check_only:
            checks.append(("Tests", self.run_tests))
        
        all_passed = True
        
        for name, check_func in checks:
            if not check_func():
                all_passed = False
                if not self.fix:
                    break  # Stop on first error if not fixing
        
        return all_passed
    
    def print_summary(self) -> None:
        """Print a summary of all results."""
        print("\n" + "="*60)
        print("QUALITY CHECK SUMMARY")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ {len(self.errors)} ERROR(S):")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} WARNING(S):")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.errors and not self.warnings:
            print("\n✅ All quality checks passed!")
        
        print("="*60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run comprehensive quality checks on the codebase"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix formatting issues where possible"
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only run checks, skip tests"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error code on any failure"
    )
    
    args = parser.parse_args()
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    if not (project_root / "pyproject.toml").exists():
        print("Error: Must run from project root directory")
        sys.exit(1)
    
    os.chdir(project_root)
    
    checker = QualityChecker(
        verbose=args.verbose,
        fix=args.fix,
        check_only=args.check_only
    )
    
    try:
        success = checker.run_all_checks()
        checker.print_summary()
        
        if not success and args.strict:
            sys.exit(1)
        elif success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ Quality check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Quality check failed with exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()