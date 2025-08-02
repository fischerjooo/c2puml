@echo off
set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%..

REM Clean previous output
echo Cleaning previous output...
if exist "artifacts\output_example" rmdir /s /q "artifacts\output_example"
if exist "tests\example\artifacts\output_example" rmdir /s /q "tests\example\artifacts\output_example"

REM Run the full workflow using the standalone c2puml.py
echo Running example workflow with config.json...
python c2puml.py --config tests/example/config.json --verbose

echo PlantUML diagrams generated in: ./artifacts/output_example (see config.json)

REM Run assertions to validate the generated PUML files
echo Running assertions to validate generated PUML files...
cd tests/example
python test-example.py