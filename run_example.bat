@echo off
set SCRIPT_DIR=%~dp0
cd /d %SCRIPT_DIR%

if exist plantuml_output rmdir /s /q plantuml_output
mkdir plantuml_output

python main.py workflow example/source example/config.json

echo PlantUML diagrams generated in: %SCRIPT_DIR%plantuml_output