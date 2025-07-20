#!/usr/bin/env python3
"""
Script to run linting and formatting tools locally.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(e.stderr)
        return False


def main():
    """Main function to run all linting and formatting tools."""
    print("🚀 Starting linting and formatting checks...")
    
    # Define the Python files to check
    python_files = [
        "c_to_plantuml/",
        "main.py",
        "run_all_tests.py",
        "setup.py"
    ]
    
    # Check if we're in the right directory
    if not Path("c_to_plantuml").exists():
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)
    
    success = True
    
    # Run flake8
    flake8_cmd = f"flake8 {' '.join(python_files)}"
    if not run_command(flake8_cmd, "flake8 linting"):
        success = False
    
    # Run black check
    black_cmd = f"black --check --diff {' '.join(python_files)}"
    if not run_command(black_cmd, "black formatting check"):
        success = False
    
    # Run isort check
    isort_cmd = f"isort --check-only --diff {' '.join(python_files)}"
    if not run_command(isort_cmd, "isort import sorting check"):
        success = False
    
    if success:
        print("🎉 All checks passed!")
        print("\n💡 To automatically fix formatting issues, run:")
        print("   black c_to_plantuml/ main.py run_all_tests.py setup.py")
        print("   isort c_to_plantuml/ main.py run_all_tests.py setup.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()