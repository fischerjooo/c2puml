@echo off
cd /d "%~dp0"

call python -u check_tests_mapping.py
set "rc=%errorlevel%"
if "%rc%"=="0" (
    echo.
    echo All test mapping is correct
) else (
    echo.
    echo Some test mapping is incorrect. Please check the output above
    exit /b 1
)

call python run_all_tests.py
set "rc=%errorlevel%"

if "%rc%"=="0" (
    echo.
    echo All tests passed successfully!
    exit /b 0
) else (
    echo.
    echo Some tests failed. Please check the output above
    exit /b 1
)
