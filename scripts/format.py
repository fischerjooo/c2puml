#!/usr/bin/env python3
"""
Script to automatically fix formatting issues using black and isort.
Comprehensive formatting for all Python files in the project.
"""

import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔧 {description}...")
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
    """Main function to run formatting tools."""
    print("🚀 Starting automatic code formatting...")
    print("=" * 60)

    # Check if we're in the right directory
    if not Path("c_to_plantuml").exists():
        print("❌ Error: Please run this script from the project root directory")
        sys.exit(1)

    # Find all Python files
    python_files = find_python_files()
    print(f"📁 Found {len(python_files)} Python files to format:")
    for file in sorted(python_files):
        print(f"   - {file}")

    success = True

    # Run black formatting
    print("\n🎨 Running black code formatting...")
    black_cmd = "python3 -m black ."
    if not run_command(black_cmd, "black code formatting"):
        success = False

    # Run isort import sorting
    print("\n📦 Running isort import sorting...")
    isort_cmd = "python3 -m isort ."
    if not run_command(isort_cmd, "isort import sorting"):
        success = False

    # Run pre-commit hooks if available
    print("\n🔧 Running pre-commit hooks...")
    try:
        pre_commit_cmd = "python3 -m pre_commit run --all-files"
        if not run_command(pre_commit_cmd, "pre-commit hooks"):
            print("⚠️  pre-commit hooks failed or not available, continuing...")
    except FileNotFoundError:
        print("⚠️  pre-commit not available, skipping...")

    print("\n" + "=" * 60)
    if success:
        print("🎉 All formatting completed successfully!")
        print("\n💡 To check if everything is properly formatted, run:")
        print("   python scripts/lint.py")
        print("\n💡 To run tests, use:")
        print("   python run_all_tests.py")
    else:
        print("❌ Some formatting operations failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
