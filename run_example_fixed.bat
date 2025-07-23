@echo off
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
"C:\toolbase\python\3.12.5.0-2\python.exe" main.py --config example/config.json --verbose
if %errorlevel% equ 0 goto :success

REM Option 4: Try virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
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
