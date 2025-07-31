@echo off
REM Simple test runner script

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

cd /d %SCRIPT_DIR%..

python scripts/run_all_tests.py

if %errorlevel%==0 (
    echo.
    echo All tests passed successfully!
    exit /b 0
) else (
    echo.
    echo Some tests failed. Please check the output above.
    exit /b 1
)