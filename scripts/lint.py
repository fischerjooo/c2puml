#!/usr/bin/env python3
"""
Script to run linting and formatting tools locally.
Comprehensive linting for all Python files in the project.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(e.stderr)
        return False


def find_python_files():
    """Find all Python files in the project."""
    python_files = []
    exclude_dirs = {
        ".git",
        "__pycache__",
        "build",
        "dist",
        ".eggs",
        "*.egg",
        ".venv",
        "venv",
        ".tox",
        ".mypy_cache",
    }

    for path in Path(".").rglob("*.py"):
        # Skip excluded directories
        if any(exclude in str(path) for exclude in exclude_dirs):
            continue
        python_files.append(str(path))

    return python_files


def main():
    """Main function to run all linting and formatting tools."""
    print("🚀 Starting linting and formatting checks...")
    print("=" * 60)

    # Check if we're in the right directory
    if not Path("c_to_plantuml").exists():
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)

    # Find all Python files
    python_files = find_python_files()
    print(f"📁 Found {len(python_files)} Python files to check:")
    for file in sorted(python_files):
        print(f"   - {file}")

    success = True

    # Run flake8
    print("\n🔍 Running flake8 linting...")
    flake8_cmd = "python3 -m flake8 . --max-line-length=88 --extend-ignore=E203,W503,E501,F401,F841,W293 --count --show-source --statistics"
    if not run_command(flake8_cmd, "flake8 linting"):
        success = False

    # Run black check
    print("\n🎨 Running black formatting check...")
    black_cmd = "python3 -m black --check --diff ."
    if not run_command(black_cmd, "black formatting check"):
        success = False

    # Run isort check
    print("\n📦 Running isort import sorting check...")
    isort_cmd = "python3 -m isort --check-only --diff ."
    if not run_command(isort_cmd, "isort import sorting check"):
        success = False

    # Run pre-commit hooks check if available
    print("\n🔧 Running pre-commit hooks check...")
    try:
        pre_commit_cmd = "python3 -m pre_commit run --all-files"
        if not run_command(pre_commit_cmd, "pre-commit hooks check"):
            print("⚠️  pre-commit hooks failed or not available, continuing...")
    except FileNotFoundError:
        print("⚠️  pre-commit not available, skipping...")

    print("\n" + "=" * 60)
    if success:
        print("🎉 All checks passed!")
        print("\n💡 To automatically fix formatting issues, run:")
        print("   python scripts/format.py")
        print("\n💡 Or run individual tools:")
        print("   python3 -m black .")
        print("   python3 -m isort .")
        print("   python3 -m pre_commit run --all-files")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\n💡 To automatically fix formatting issues, run:")
        print("   python scripts/format.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
