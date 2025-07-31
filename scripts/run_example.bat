@echo off
set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%..

if exist output rmdir /s /q output
mkdir output

set PYTHONPATH=src && python -m c2puml.main --config tests/example/config.json --verbose

echo PlantUML diagrams generated in: %SCRIPT_DIR%output

REM Run assertions to validate the generated PUML files
echo Running assertions to validate generated PUML files...
cd tests/example
python test-example.py