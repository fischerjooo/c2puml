#!/usr/bin/env python3
"""
Python Installation Diagnostic Script
This script helps identify and fix Python installation issues.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def check_python_version():
    """Check Python version and installation details."""
    print("🐍 Python Version Information:")
    print(f"   Python Version: {sys.version}")
    print(f"   Python Executable: {sys.executable}")
    print(f"   Platform: {platform.platform()}")
    print(f"   Architecture: {platform.architecture()}")
    print()


def check_python_path():
    """Check Python PATH and environment."""
    print("🔍 Python PATH Analysis:")
    print(f"   PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
    print(f"   PYTHONHOME: {os.environ.get('PYTHONHOME', 'Not set')}")

    # Check if we're in a virtual environment
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print(f"   Virtual Environment: Yes (Base: {sys.base_prefix})")
    else:
        print("   Virtual Environment: No")
    print()


def test_io_module():
    """Test if the io module can be imported properly."""
    print("📦 Testing IO Module:")
    try:
        import io

        print("   ✅ IO module imports successfully")

        # Test specific functions
        try:
            from io import text_encoding

            print("   ✅ text_encoding function available")
        except ImportError as e:
            print(f"   ⚠️  text_encoding function not available: {e}")

        # Test basic IO operations
        try:
            with io.StringIO("test") as f:
                content = f.read()
            print("   ✅ Basic IO operations work")
        except Exception as e:
            print(f"   ❌ Basic IO operations failed: {e}")

    except ImportError as e:
        print(f"   ❌ IO module import failed: {e}")
    except Exception as e:
        print(f"   ❌ Unexpected error with IO module: {e}")
    print()


def check_common_issues():
    """Check for common Python installation issues."""
    print("🔧 Common Issues Check:")

    # Check for multiple Python installations
    python_paths = []
    for path in os.environ.get("PATH", "").split(os.pathsep):
        if "python" in path.lower():
            python_paths.append(path)

    if len(python_paths) > 3:  # More than expected
        print("   ⚠️  Multiple Python installations detected in PATH")
        for path in python_paths:
            print(f"      - {path}")

    # Check for corrupted Python installation
    python_lib = os.path.join(os.path.dirname(sys.executable), "Lib")
    if os.path.exists(python_lib):
        io_path = os.path.join(python_lib, "io.py")
        if os.path.exists(io_path):
            print("   ✅ IO module file exists")
        else:
            print("   ❌ IO module file missing")
    else:
        print("   ⚠️  Python Lib directory not found")

    print()


def suggest_solutions():
    """Suggest solutions based on the diagnostic results."""
    print("💡 Suggested Solutions:")
    print()

    print("1. **Reinstall Python** (Recommended):")
    print("   - Download Python 3.12.5 from https://www.python.org/downloads/")
    print("   - Uninstall current Python installation")
    print("   - Install fresh Python with 'Add to PATH' option")
    print()

    print("2. **Use Virtual Environment** (Alternative):")
    print("   - Create a new virtual environment:")
    print("     python -m venv venv")
    print("     venv\\Scripts\\activate  # Windows")
    print("     source venv/bin/activate  # Linux/macOS")
    print()

    print("3. **Check Environment Variables**:")
    print("   - Ensure PYTHONPATH is not conflicting")
    print("   - Remove any conflicting Python installations from PATH")
    print()

    print("4. **Use Python Launcher** (Windows):")
    print("   - Use 'py' command instead of 'python':")
    print("     py -3.12 main.py --config example/config.json --verbose")
    print()


def create_fixed_batch_file():
    """Create a fixed version of the batch file."""
    print("🔧 Creating Fixed Batch File...")

    fixed_content = """@echo off
set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%

if exist output rmdir /s /q output
mkdir output

REM Try multiple Python commands
echo Trying to run Python...

REM Option 1: Try py launcher
py -3.12 main.py --config example/config.json --verbose
if %errorlevel% equ 0 goto :success

REM Option 2: Try python3
python3 main.py --config example/config.json --verbose
if %errorlevel% equ 0 goto :success

REM Option 3: Try python with full path
"C:\\toolbase\\python\\3.12.5.0-2\\python.exe" main.py --config example/config.json --verbose
if %errorlevel% equ 0 goto :success

REM Option 4: Try virtual environment
if exist venv\\Scripts\\activate.bat (
    call venv\\Scripts\\activate.bat
    python main.py --config example/config.json --verbose
    if %errorlevel% equ 0 goto :success
)

echo ❌ All Python options failed
exit /b 1

:success
echo PlantUML diagrams generated in: %SCRIPT_DIR%output

REM Run assertions to validate the generated PUML files
echo Running assertions to validate generated PUML files...
cd example
python assertions.py
"""

    with open("run_example_fixed.bat", "w") as f:
        f.write(fixed_content)

    print("   ✅ Created 'run_example_fixed.bat' with multiple Python fallback options")


def main():
    """Run the diagnostic."""
    print("🚀 Python Installation Diagnostic")
    print("=" * 50)

    check_python_version()
    check_python_path()
    test_io_module()
    check_common_issues()
    suggest_solutions()
    create_fixed_batch_file()

    print("=" * 50)
    print("📋 Summary:")
    print("   - Run 'run_example_fixed.bat' instead of 'run_example.bat'")
    print("   - Consider reinstalling Python if issues persist")
    print("   - Use virtual environment for isolated Python environment")


if __name__ == "__main__":
    main()
