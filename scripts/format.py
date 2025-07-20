#!/usr/bin/env python3
"""
Script to automatically fix formatting issues using black and isort.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
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
    """Main function to run formatting tools."""
    print("🚀 Starting automatic code formatting...")
    
    # Define the Python files to format
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
    
    # Run black formatting
    black_cmd = f"black {' '.join(python_files)}"
    if not run_command(black_cmd, "black code formatting"):
        success = False
    
    # Run isort import sorting
    isort_cmd = f"isort {' '.join(python_files)}"
    if not run_command(isort_cmd, "isort import sorting"):
        success = False
    
    if success:
        print("🎉 All formatting completed successfully!")
        print("\n💡 To check if everything is properly formatted, run:")
        print("   python scripts/lint.py")
    else:
        print("❌ Some formatting operations failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()