@echo off
setlocal enabledelayedexpansion

echo Windows c2puml Example Runner
echo =============================

REM Check if we're in the right directory
if not exist "pyproject.toml" (
    echo Error: pyproject.toml not found. Please run this script from the project root directory.
    pause
    exit /b 1
)

REM Check if c2puml is installed
python -c "import c2puml" >nul 2>&1
if errorlevel 1 (
    echo c2puml module not found. Installing in development mode...
    python -m pip install -e .
    if errorlevel 1 (
        echo Failed to install c2puml. Trying with --break-system-packages...
        python -m pip install -e . --break-system-packages
        if errorlevel 1 (
            echo Error: Could not install c2puml package
            echo Please check your Python installation and try again.
            pause
            exit /b 1
        )
    )
    echo Installation successful!
)

REM Clean previous output
echo Cleaning previous output...
if exist "artifacts\output_example" rmdir /s /q "artifacts\output_example"
if exist "tests\example\artifacts\output_example" rmdir /s /q "tests\example\artifacts\output_example"

REM Run the full workflow
echo Running example workflow with config.json...
set PYTHONPATH=src
python -m c2puml.main --config tests/example/config.json --verbose

if errorlevel 1 (
    echo.
    echo Error: Failed to run c2puml
    echo.
    echo Troubleshooting steps:
    echo 1. Make sure Python is installed and in PATH
    echo 2. Try running: python -m pip install -e . --break-system-packages
    echo 3. Check the WINDOWS_SETUP.md file for more help
    echo.
    pause
    exit /b 1
)

echo.
echo PlantUML diagrams generated in: ./artifacts/output_example
echo.

REM Run assertions
echo Running assertions to validate generated PUML files...
cd tests/example
python test-example.py

echo.
echo Example completed successfully!
echo Check the generated diagrams in: ..\..\artifacts\output_example
pause