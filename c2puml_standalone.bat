@echo off
REM Standalone C to PlantUML converter for Windows
REM This batch file allows running c2puml without installation

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or later and try again
    pause
    exit /b 1
)

REM Run the standalone script with all arguments passed through
python c2puml_standalone.py %*

REM Pause to see any error messages
if errorlevel 1 (
    echo.
    echo Script failed with error code %errorlevel%
    pause
)