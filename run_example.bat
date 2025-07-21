@echo off
REM Run the example workflow using the provided config.json and source files

set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%

REM Clean previous output
echo Cleaning previous output...
if exist plantuml_output rmdir /s /q plantuml_output
mkdir plantuml_output

REM Run the workflow
echo Running example workflow with config.json...
python main.py workflow example/source example/config.json

REM Output location
echo PlantUML diagrams generated in: %SCRIPT_DIR%plantuml_output