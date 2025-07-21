@echo off
set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%

if exist output rmdir /s /q output
mkdir output

python main.py --config example/config.json --verbose

echo PlantUML diagrams generated in: %SCRIPT_DIR%output