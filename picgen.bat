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

REM Generate diagram index HTML file
echo 📄 Generating diagram index HTML file...

REM Get current timestamp
for /f "tokens=1-4 delims=/ " %%a in ('date /t') do set "date_part=%%a %%b %%c %%d"
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set "time_part=%%a:%%b"
set "timestamp=%date_part% %time_part%"

REM Count PNG and PlantUML files
set "png_count=0"
set "puml_count=0"
for %%f in (*.png) do set /a png_count+=1
for %%f in (*.puml) do set /a puml_count+=1

REM Create the HTML file
echo ^<!DOCTYPE html^> > diagram_index.html
echo ^<html lang="en"^> >> diagram_index.html
echo ^<head^> >> diagram_index.html
echo     ^<meta charset="UTF-8"^> >> diagram_index.html
echo     ^<meta name="viewport" content="width=device-width, initial-scale=1.0"^> >> diagram_index.html
echo     ^<title^>PlantUML Diagrams - C to PlantUML Converter^</title^> >> diagram_index.html
echo     ^<style^> >> diagram_index.html
echo         body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background: #f6f8fa; } >> diagram_index.html
echo         .container { max-width: 1200px; margin: 0 auto; } >> diagram_index.html
echo         .header { background: white; padding: 20px; border-radius: 6px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); } >> diagram_index.html
echo         .nav { background: #0366d6; color: white; padding: 15px 20px; border-radius: 6px; margin-bottom: 20px; } >> diagram_index.html
echo         .nav a { color: white; text-decoration: none; margin-right: 20px; font-weight: 500; } >> diagram_index.html
echo         .nav a:hover { text-decoration: underline; } >> diagram_index.html
echo         .stats { background: white; padding: 15px; border-radius: 6px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); } >> diagram_index.html
echo         .diagram-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); gap: 20px; margin-top: 20px; } >> diagram_index.html
echo         .diagram-card { background: white; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden; transition: transform 0.2s; } >> diagram_index.html
echo         .diagram-card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); } >> diagram_index.html
echo         .diagram-card h3 { margin: 0; padding: 15px; background: #f1f3f4; border-bottom: 1px solid #e1e4e8; font-size: 16px; color: #24292e; } >> diagram_index.html
echo         .diagram-image { width: 100%%; height: auto; display: block; } >> diagram_index.html
echo         .diagram-links { padding: 15px; background: #f8f9fa; } >> diagram_index.html
echo         .diagram-links a { display: inline-block; margin: 5px 10px 5px 0; padding: 5px 10px; background: #0366d6; color: white; text-decoration: none; border-radius: 4px; font-size: 12px; } >> diagram_index.html
echo         .diagram-links a:hover { background: #0256b3; } >> diagram_index.html
echo         .footer { text-align: center; margin-top: 40px; padding: 20px; color: #586069; } >> diagram_index.html
echo         .no-diagrams { background: white; padding: 40px; text-align: center; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); } >> diagram_index.html
echo     ^</style^> >> diagram_index.html
echo ^</head^> >> diagram_index.html
echo ^<body^> >> diagram_index.html
echo     ^<div class="container"^> >> diagram_index.html
echo         ^<div class="nav"^> >> diagram_index.html
echo             ^<a href="../index.html"^>🏠 Home^</a^> >> diagram_index.html
echo             ^<a href="../tests/reports/coverage/index.html"^>📊 Coverage^</a^> >> diagram_index.html
echo             ^<a href="../tests/reports/test_summary.html"^>📝 Tests^</a^> >> diagram_index.html
echo             ^<a href="diagram_index.html"^>📊 Diagrams^</a^> >> diagram_index.html
echo             ^<a href="../example/"^>📋 Examples^</a^> >> diagram_index.html
echo         ^</div^> >> diagram_index.html
echo         ^<div class="header"^> >> diagram_index.html
echo             ^<h1^>📊 PlantUML Diagrams^</h1^> >> diagram_index.html
echo             ^<p^>Generated diagrams from C/C++ source code analysis^</p^> >> diagram_index.html
echo             ^<p^>^<strong^>Generated:^</strong^> %timestamp%^</p^> >> diagram_index.html
echo         ^</div^> >> diagram_index.html
echo         ^<div class="stats"^> >> diagram_index.html
echo             ^<h3^>📈 Statistics^</h3^> >> diagram_index.html
echo             ^<p^>^<strong^>PNG Images:^</strong^> %png_count%^</p^> >> diagram_index.html
echo             ^<p^>^<strong^>PlantUML Files:^</strong^> %puml_count%^</p^> >> diagram_index.html
echo             ^<p^>^<strong^>Total Files:^</strong^> %((png_count + puml_count))%^</p^> >> diagram_index.html
echo         ^</div^> >> diagram_index.html

REM Check if we have any PNG files
if %png_count% gtr 0 (
    echo         ^<div class="diagram-grid"^> >> diagram_index.html
    
    REM Process each PNG file
    for %%f in (*.png) do (
        set "basename=%%~nf"
        echo             ^<div class="diagram-card"^> >> diagram_index.html
        echo                 ^<h3^>!basename!^</h3^> >> diagram_index.html
        echo                 ^<img src="%%f" alt="!basename! diagram" class="diagram-image" loading="lazy"^> >> diagram_index.html
        echo                 ^<div class="diagram-links"^> >> diagram_index.html
        echo                     ^<a href="%%f" target="_blank"^>🖼️ Full Size^</a^> >> diagram_index.html
        REM Check if corresponding PlantUML file exists
        if exist "!basename!.puml" (
            echo                     ^<a href="!basename!.puml"^>📄 Source^</a^> >> diagram_index.html
        )
        echo                 ^</div^> >> diagram_index.html
        echo             ^</div^> >> diagram_index.html
    )
    
    echo         ^</div^> >> diagram_index.html
) else (
    echo         ^<div class="no-diagrams"^> >> diagram_index.html
    echo             ^<h3^>📭 No Diagrams Found^</h3^> >> diagram_index.html
    echo             ^<p^>No PNG images were found in the output directory.^</p^> >> diagram_index.html
    echo             ^<p^>Run the conversion script to generate diagrams from PlantUML files.^</p^> >> diagram_index.html
    echo         ^</div^> >> diagram_index.html
)

echo         ^<div class="footer"^> >> diagram_index.html
echo             ^<p^>Generated by ^<a href="https://github.com/fischerjooo/generator_project"^>C to PlantUML Converter^</a^>^</p^> >> diagram_index.html
echo             ^<p^>Last updated: %timestamp%^</p^> >> diagram_index.html
echo         ^</div^> >> diagram_index.html
echo     ^</div^> >> diagram_index.html
echo ^</body^> >> diagram_index.html
echo ^</html^> >> diagram_index.html

echo ✅ Diagram index generated: diagram_index.html
echo 📊 Found %png_count% PNG files and %puml_count% PlantUML files