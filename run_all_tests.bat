@echo off
REM Simple test runner script

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

echo Running C to PlantUML Converter Tests
echo ========================================
echo Script directory: %SCRIPT_DIR%

REM Change to the script directory
cd /d %SCRIPT_DIR%

REM Detect Python version
where python >nul 2>nul
if %errorlevel%==0 (
    set PYTHON_CMD=python
) else (
    echo Error: Python not found. Please install Python 3.8+
    exit /b 1
)

echo Using Python:
%PYTHON_CMD% --version
echo Working directory: %cd%

REM Run the test suite
%PYTHON_CMD% run_all_tests.py

REM Check exit code and provide feedback
if %errorlevel%==0 (
    echo.
    echo All tests passed successfully!
    exit /b 0
) else (
    echo.
    echo Some tests failed. Please check the output above.
    exit /b 1
)