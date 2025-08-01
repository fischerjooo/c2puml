@echo off
REM Simple test runner script

echo 🧪 Running C to PlantUML Converter Tests
echo ========================================

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
echo Script directory: %SCRIPT_DIR%

REM Change to the project root directory (parent of scripts)
cd /d %SCRIPT_DIR%..
echo 📁 Working directory: %cd%

REM Detect Python version
where python3 >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_CMD=python3
    goto :python_found
)

where python >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_CMD=python
    goto :python_found
)

echo ❌ Error: Python not found. Please install Python 3.8+
exit /b 1

:python_found
for /f "tokens=*" %%i in ('%PYTHON_CMD% --version') do echo 🐍 Using Python: %%i

echo 🎯 Running all tests...
%PYTHON_CMD% scripts/run_all_tests.py

if %errorlevel%==0 (
    echo.
    echo ✅ All tests passed successfully!
    exit /b 0
) else (
    echo.
    echo ❌ Some tests failed. Please check the output above.
    exit /b 1
)