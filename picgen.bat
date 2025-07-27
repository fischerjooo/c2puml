@echo off
setlocal enabledelayedexpansion

REM PlantUML to PNG converter script for Windows
REM This script converts all .puml files in the output folder to PNG images
REM Usage: picgen.bat [plantuml_jar_path]
REM Example: picgen.bat "C:\Users\username\.vscode\extensions\jebbs.plantuml-2.18.1\plantuml.jar"

REM Parse command line arguments
set "CUSTOM_PLANTUML_JAR="
if not "%~1"=="" (
    set "CUSTOM_PLANTUML_JAR=%~1"
    echo 📁 Using custom PlantUML JAR path: %CUSTOM_PLANTUML_JAR%
)

echo 🔄 Starting PlantUML to PNG conversion...

REM Check if output directory exists
if not exist "output" (
    echo ❌ Error: output directory not found
    exit /b 1
)

REM Check if plantuml is installed or if we have the JAR file
where plantuml >nul 2>&1
if %errorlevel% equ 0 (
    set "PLANTUML_CMD=plantuml"
    echo 📦 Using installed PlantUML command
) else (
    REM Check custom PlantUML JAR path first
    if not "!CUSTOM_PLANTUML_JAR!"=="" (
        if exist "!CUSTOM_PLANTUML_JAR!" (
            set "PLANTUML_CMD=java -jar "!CUSTOM_PLANTUML_JAR!""
            echo 📦 Using custom PlantUML JAR file: !CUSTOM_PLANTUML_JAR!
        ) else (
            echo ❌ Custom PlantUML JAR file not found: !CUSTOM_PLANTUML_JAR!
            echo 🔍 Falling back to default search locations...
        )
    )
    
    REM If no custom path or custom path not found, try default locations
    if "!PLANTUML_CMD!"=="" (
        if exist "plantuml.jar" (
            set "PLANTUML_CMD=java -jar plantuml.jar"
            echo 📦 Using PlantUML JAR file from current directory
        ) else if exist "..\plantuml.jar" (
            set "PLANTUML_CMD=java -jar ..\plantuml.jar"
            echo 📦 Using PlantUML JAR file from parent directory
        ) else (
            echo 📥 PlantUML JAR file not found. Attempting to download...
            
            REM Download PlantUML JAR file
            set "PLANTUML_VERSION=1.2024.0"
            set "PLANTUML_URL=https://github.com/plantuml/plantuml/releases/download/v%PLANTUML_VERSION%/plantuml-%PLANTUML_VERSION%.jar"
            
            echo 🔄 Downloading PlantUML v%PLANTUML_VERSION%...
            echo 📡 URL: %PLANTUML_URL%
            
            REM Try multiple download methods
            set "download_success=false"
            
            REM Method 1: PowerShell with TLS 1.2
            echo 🔄 Trying PowerShell download method...
            powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PLANTUML_URL%' -OutFile 'plantuml.jar' -UseBasicParsing}"
            if %errorlevel% equ 0 if exist "plantuml.jar" (
                echo ✅ PlantUML JAR file downloaded successfully via PowerShell
                set "download_success=true"
            ) else (
                echo ⚠️  PowerShell download failed, trying alternative method...
                
                REM Method 2: Try with curl if available
                where curl >nul 2>&1
                if %errorlevel% equ 0 (
                    echo 🔄 Trying curl download method...
                    curl -L -o plantuml.jar "%PLANTUML_URL%"
                    if %errorlevel% equ 0 if exist "plantuml.jar" (
                        echo ✅ PlantUML JAR file downloaded successfully via curl
                        set "download_success=true"
                    ) else (
                        echo ⚠️  curl download also failed
                    )
                ) else (
                    echo ⚠️  curl not available
                )
            )
            
            REM If all download methods failed, provide manual instructions
            if "!download_success!"=="false" (
                echo.
                echo ❌ Failed to download PlantUML JAR file automatically
                echo.
                echo 📋 Manual download instructions:
                echo    1. Open your web browser
                echo    2. Go to: %PLANTUML_URL%
                echo    3. Save the file as 'plantuml.jar' in the current directory
                echo    4. Run this script again
                echo.
                echo 🔗 Alternative download sources:
                echo    - Official PlantUML releases: https://github.com/plantuml/plantuml/releases
                echo    - PlantUML website: https://plantuml.com/download
                echo.
                echo 💡 You can also install PlantUML via:
                echo    - Chocolatey: choco install plantuml
                echo    - Scoop: scoop install plantuml
                echo    - Or download from: https://plantuml.com/download
                echo.
                exit /b 1
            )
            
            set "PLANTUML_CMD=java -jar plantuml.jar"
        )
    )
)

REM Test PlantUML setup
echo 🔍 Testing PlantUML setup...
%PLANTUML_CMD% -version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ PlantUML setup is working correctly
) else (
    echo ❌ PlantUML setup test failed
    echo    Please ensure Java is installed and accessible
    echo    You can download Java from: https://adoptium.net/
    exit /b 1
)

REM Change to output directory
cd output

REM Find all .puml files and convert them to PNG
echo 📁 Scanning for .puml files in output directory...

set "puml_count=0"
for %%f in (*.puml) do (
    set /a puml_count+=1
)

if %puml_count% equ 0 (
    echo ℹ️  No .puml files found in output directory
    exit /b 0
)

echo 📊 Found %puml_count% .puml file(s)

REM Convert each .puml file to PNG
set "success_count=0"
set "fail_count=0"

for %%f in (*.puml) do (
    echo 🔄 Converting %%f to PNG...
    
    REM Convert to PNG using PlantUML
    %PLANTUML_CMD% -tpng "%%f"
    
    REM Check if PNG was created successfully
    set "base_name=%%~nf"
    if exist "!base_name!.png" (
        echo ✅ Created !base_name!.png
        set /a success_count+=1
    ) else (
        echo ❌ Failed to generate !base_name!.png
        set /a fail_count+=1
    )
)

echo.
echo 📊 PlantUML to PNG conversion summary:
echo    ✅ Successfully converted: %success_count% file(s)
echo    ❌ Failed conversions: %fail_count% file(s)

if %fail_count% equ 0 (
    echo ✅ All PlantUML files converted successfully!
) else (
    echo ⚠️  Some conversions failed. Check the output above for details.
)

echo 📁 Check the output directory for generated PNG images.