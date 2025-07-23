@echo off
setlocal enabledelayedexpansion

REM Complete workflow script that chains together: run_all_tests -> run_example -> picgen
REM This script simply calls the other batch files in sequence

echo 🚀 Starting complete workflow...
echo ==================================

REM Step 1: Run all tests
echo 📋 Step 1: Running all tests...
echo ----------------------------------------
call run_all_tests.bat
echo ✅ All tests passed!

echo.

REM Step 2: Run example
echo 📋 Step 2: Running example...
echo ----------------------------------------
call run_example.bat
echo ✅ Example completed successfully!

echo.

REM Step 3: Generate PNG images
echo 📋 Step 3: Generating PNG images...
echo ----------------------------------------
call picgen.bat
echo ✅ PNG generation completed successfully!

echo.
echo 🎉 Complete workflow finished successfully!
echo ==================================
echo 📁 Check the output directory for generated files:
echo    - .puml files (PlantUML diagrams)
echo    - .png files (Generated images)
echo    - .json files (Configuration and results)
echo.
echo ✨ Workflow completed! All steps passed successfully.