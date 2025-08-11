@echo off
REM Simple test runner script

echo 🧪 Running C to PlantUML Converter Tests
echo ========================================

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
echo Script directory: %SCRIPT_DIR%

REM Run mapping validation first
echo 🔎 Pre-check: Validating tests mapping rules...
pushd "%SCRIPT_DIR%.."
python scripts\check_tests_mapping.py
if not %errorlevel%==0 (
    echo ❌ Test mapping validation failed.
    popd
    exit /b 1
)
popd
echo ✅ Test mapping validation passed!

echo 🎯 Running all tests...
cd /d %SCRIPT_DIR%
python run_all_tests.py

if %errorlevel%==0 (
    echo.
    echo ✅ All tests passed successfully!
    exit /b 0
) else (
    echo.
    echo ❌ Some tests failed. Please check the output above.
    exit /b 1
)
