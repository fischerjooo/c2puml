@echo off
setlocal enabledelayedexpansion

REM PlantUML to PNG converter script for Windows
REM This script converts all .puml files in the output folder to PNG images

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
    if exist "plantuml.jar" (
        set "PLANTUML_CMD=java -jar plantuml.jar"
        echo 📦 Using PlantUML JAR file from current directory
    ) else if exist "..\plantuml.jar" (
        set "PLANTUML_CMD=java -jar ..\plantuml.jar"
        echo 📦 Using PlantUML JAR file from parent directory
    ) else (
        echo 📥 PlantUML JAR file not found. Downloading...
        
        REM Download PlantUML JAR file
        set "PLANTUML_VERSION=1.2024.0"
        set "PLANTUML_URL=https://github.com/plantuml/plantuml/releases/download/v%PLANTUML_VERSION%/plantuml-%PLANTUML_VERSION%.jar"
        
        echo 🔄 Downloading PlantUML v%PLANTUML_VERSION%...
        
        REM Try using PowerShell to download
        powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '!PLANTUML_URL!' -OutFile 'plantuml.jar'}"
        
        if %errorlevel% equ 0 if exist "plantuml.jar" (
            echo ✅ PlantUML JAR file downloaded successfully
            set "PLANTUML_CMD=java -jar plantuml.jar"
        ) else (
            echo ❌ Failed to download PlantUML JAR file
            echo    Please download it manually from: %PLANTUML_URL%
            exit /b 1
        )
    )
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
for %%f in (*.puml) do (
    echo 🔄 Converting %%f to PNG...
    
    REM Convert to PNG using PlantUML
    %PLANTUML_CMD% -tpng "%%f"
    
    REM Check if PNG was created successfully
    set "base_name=%%~nf"
    if exist "!base_name!.png" (
        echo ✅ Created !base_name!.png
    ) else (
        echo ❌ Failed to generate !base_name!.png
    )
)

echo ✅ PlantUML to PNG conversion completed!
echo 📁 Check the output directory for generated PNG images.