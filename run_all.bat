@echo off
setlocal enabledelayedexpansion

REM Complete workflow script that runs all tests, example, and generates PNG images
REM This script chains together: run_all_tests -> run_example -> picgen

echo 🚀 Starting complete workflow...
echo ==================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python is not installed or not in PATH
    exit /b 1
)

REM Check if Java is available (for PlantUML)
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Warning: Java is not installed. PlantUML conversion may fail.
)

REM Step 1: Run all tests
echo 📋 Step 1: Running all tests...
echo ----------------------------------------
python run_all_tests.py
if %errorlevel% neq 0 (
    echo ❌ Tests failed! Stopping workflow.
    exit /b 1
)
echo ✅ All tests passed!

echo.

REM Step 2: Run example
echo 📋 Step 2: Running example...
echo ----------------------------------------
call run_example.bat
if %errorlevel% neq 0 (
    echo ❌ Example failed! Stopping workflow.
    exit /b 1
)
echo ✅ Example completed successfully!

echo.

REM Step 3: Generate PNG images
echo 📋 Step 3: Generating PNG images...
echo ----------------------------------------
call picgen.bat
if %errorlevel% neq 0 (
    echo ❌ PNG generation failed!
    exit /b 1
)
echo ✅ PNG generation completed successfully!

echo.
echo 🎉 Complete workflow finished successfully!
echo ==================================
echo 📁 Check the output directory for generated files:
echo    - .puml files (PlantUML diagrams)
echo    - .png files (Generated images)
echo    - .json files (Configuration and results)

REM Show summary of generated files
if exist "output" (
    echo.
    echo 📊 Generated files summary:
    echo ----------------------------------------
    
    REM Count files
    set "puml_count=0"
    set "png_count=0"
    set "json_count=0"
    
    for %%f in (output\*.puml) do set /a puml_count+=1
    for %%f in (output\*.png) do set /a png_count+=1
    for %%f in (output\*.json) do set /a json_count+=1
    
    echo    📄 PlantUML files (.puml): !puml_count!
    echo    🖼️  PNG images (.png): !png_count!
    echo    📋 JSON files (.json): !json_count!
    
    if !png_count! gtr 0 (
        echo.
        echo 🖼️  Generated PNG images:
        for %%f in (output\*.png) do (
            echo    - %%~nxf
        )
    )
)

echo.
echo ✨ Workflow completed! All steps passed successfully.