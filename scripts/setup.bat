@echo off
setlocal enabledelayedexpansion

echo Setting up c2puml development environment...

REM Check if python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: python is not installed or not in PATH
    echo Please install Python and ensure it's in your PATH
    pause
    exit /b 1
)

echo Python version:
python --version

REM Install the package in development mode
echo Installing c2puml in development mode...
python -m pip install -e .

if errorlevel 1 (
    echo Error: Failed to install c2puml package
    echo This might be due to an externally managed environment
    echo Try running: python -m pip install -e . --break-system-packages
    pause
    exit /b 1
)

echo.
echo Installation complete!
echo.
echo To run the example:
echo   scripts\run_example.bat
echo.
echo Or manually:
echo   set PYTHONPATH=src
echo   python -m c2puml.main --config tests/example/config.json --verbose
echo.
pause