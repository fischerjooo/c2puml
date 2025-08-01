@echo off
REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Change to the project root directory (parent of scripts)
cd /d %SCRIPT_DIR%..

echo Installing dependencies from requirements-dev.txt...
pip install -r requirements-dev.txt
echo Dependencies installed successfully!