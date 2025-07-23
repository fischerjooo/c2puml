@echo off
set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%

if exist output rmdir /s /q output
mkdir output

REM Try multiple Python commands to handle installation issues
echo 🔍 Trying to run Python with multiple fallback options...

REM Option 1: Try py launcher (Windows Python Launcher)
echo 📦 Trying Python Launcher (py -3.12)...
py -3.12 main.py --config example/config.json --verbose
if %errorlevel% equ 0 goto :success

REM Option 2: Try python3
echo 📦 Trying python3...
python3 main.py --config example/config.json --verbose
if %errorlevel% equ 0 goto :success

REM Option 3: Try python with full path (from error message)
echo 📦 Trying full Python path...
"C:\toolbase\python\3.12.5.0-2\python.exe" main.py --config example/config.json --verbose
if %errorlevel% equ 0 goto :success

REM Option 4: Try virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo 📦 Trying virtual environment...
    call venv\Scripts\activate.bat
    python main.py --config example/config.json --verbose
    if %errorlevel% equ 0 goto :success
)

REM Option 5: Try python command (original)
echo 📦 Trying standard python command...
python main.py --config example/config.json --verbose
if %errorlevel% equ 0 goto :success

echo ❌ All Python options failed
echo.
echo 💡 Troubleshooting suggestions:
echo    1. Run 'python diagnose_python.py' to diagnose the issue
echo    2. Reinstall Python from https://www.python.org/downloads/
echo    3. Create a virtual environment: python -m venv venv
echo    4. Check if PYTHONPATH environment variable is conflicting
echo.
exit /b 1

:success
echo ✅ Python script executed successfully!
echo PlantUML diagrams generated in: %SCRIPT_DIR%output

REM Run assertions to validate the generated PUML files
echo Running assertions to validate generated PUML files...
cd example
python assertions.py