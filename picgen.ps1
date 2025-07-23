# PlantUML to PNG converter script for Windows PowerShell
# This script converts all .puml files in the output folder to PNG images

param(
    [switch]$ForceDownload
)

Write-Host "🔄 Starting PlantUML to PNG conversion..." -ForegroundColor Cyan

# Check if output directory exists
if (-not (Test-Path "output")) {
    Write-Host "❌ Error: output directory not found" -ForegroundColor Red
    exit 1
}

# Function to test PlantUML command
function Test-PlantUML {
    param([string]$Command)
    try {
        $null = & cmd /c "$Command -version" 2>$null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

# Check if plantuml is installed or if we have the JAR file
$plantumlCmd = $null

# Check for installed PlantUML
if (Get-Command plantuml -ErrorAction SilentlyContinue) {
    $plantumlCmd = "plantuml"
    Write-Host "📦 Using installed PlantUML command" -ForegroundColor Green
}
# Check for JAR file in current directory
elseif (Test-Path "plantuml.jar") {
    $plantumlCmd = "java -jar plantuml.jar"
    Write-Host "📦 Using PlantUML JAR file from current directory" -ForegroundColor Green
}
# Check for JAR file in parent directory
elseif (Test-Path "..\plantuml.jar") {
    $plantumlCmd = "java -jar ..\plantuml.jar"
    Write-Host "📦 Using PlantUML JAR file from parent directory" -ForegroundColor Green
}
# Download PlantUML JAR file
else {
    Write-Host "📥 PlantUML JAR file not found. Attempting to download..." -ForegroundColor Yellow
    
    $plantumlVersion = "1.2024.0"
    $plantumlUrl = "https://github.com/plantuml/plantuml/releases/download/v$plantumlVersion/plantuml-$plantumlVersion.jar"
    
    Write-Host "🔄 Downloading PlantUML v$plantumlVersion..." -ForegroundColor Cyan
    Write-Host "📡 URL: $plantumlUrl" -ForegroundColor Gray
    
    $downloadSuccess = $false
    
    # Method 1: PowerShell WebRequest with TLS 1.2
    try {
        Write-Host "🔄 Trying PowerShell download method..." -ForegroundColor Cyan
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $plantumlUrl -OutFile "plantuml.jar" -UseBasicParsing -TimeoutSec 30
        if (Test-Path "plantuml.jar") {
            Write-Host "✅ PlantUML JAR file downloaded successfully via PowerShell" -ForegroundColor Green
            $downloadSuccess = $true
        }
    }
    catch {
        Write-Host "⚠️  PowerShell download failed: $($_.Exception.Message)" -ForegroundColor Yellow
        
        # Method 2: Try with curl if available
        try {
            if (Get-Command curl -ErrorAction SilentlyContinue) {
                Write-Host "🔄 Trying curl download method..." -ForegroundColor Cyan
                curl -L -o plantuml.jar $plantumlUrl
                if (Test-Path "plantuml.jar") {
                    Write-Host "✅ PlantUML JAR file downloaded successfully via curl" -ForegroundColor Green
                    $downloadSuccess = $true
                }
            }
            else {
                Write-Host "⚠️  curl not available" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "⚠️  curl download also failed: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    
    # If all download methods failed, provide manual instructions
    if (-not $downloadSuccess) {
        Write-Host ""
        Write-Host "❌ Failed to download PlantUML JAR file automatically" -ForegroundColor Red
        Write-Host ""
        Write-Host "📋 Manual download instructions:" -ForegroundColor Cyan
        Write-Host "   1. Open your web browser" -ForegroundColor White
        Write-Host "   2. Go to: $plantumlUrl" -ForegroundColor White
        Write-Host "   3. Save the file as 'plantuml.jar' in the current directory" -ForegroundColor White
        Write-Host "   4. Run this script again" -ForegroundColor White
        Write-Host ""
        Write-Host "🔗 Alternative download sources:" -ForegroundColor Cyan
        Write-Host "   - Official PlantUML releases: https://github.com/plantuml/plantuml/releases" -ForegroundColor White
        Write-Host "   - PlantUML website: https://plantuml.com/download" -ForegroundColor White
        Write-Host ""
        Write-Host "💡 You can also install PlantUML via:" -ForegroundColor Cyan
        Write-Host "   - Chocolatey: choco install plantuml" -ForegroundColor White
        Write-Host "   - Scoop: scoop install plantuml" -ForegroundColor White
        Write-Host "   - Or download from: https://plantuml.com/download" -ForegroundColor White
        Write-Host ""
        Write-Host "🔧 Troubleshooting tips:" -ForegroundColor Cyan
        Write-Host "   - Check your internet connection" -ForegroundColor White
        Write-Host "   - Try using a VPN if you're behind a corporate firewall" -ForegroundColor White
        Write-Host "   - Ensure you have write permissions in the current directory" -ForegroundColor White
        Write-Host ""
        exit 1
    }
    
    $plantumlCmd = "java -jar plantuml.jar"
}

# Test PlantUML setup
Write-Host "🔍 Testing PlantUML setup..." -ForegroundColor Cyan
if (Test-PlantUML $plantumlCmd) {
    Write-Host "✅ PlantUML setup is working correctly" -ForegroundColor Green
}
else {
    Write-Host "❌ PlantUML setup test failed" -ForegroundColor Red
    Write-Host "   Please ensure Java is installed and accessible" -ForegroundColor Yellow
    Write-Host "   You can download Java from: https://adoptium.net/" -ForegroundColor Yellow
    exit 1
}

# Change to output directory
Push-Location "output"

# Find all .puml files and convert them to PNG
Write-Host "📁 Scanning for .puml files in output directory..." -ForegroundColor Cyan

$pumlFiles = Get-ChildItem -Filter "*.puml"
if ($pumlFiles.Count -eq 0) {
    Write-Host "ℹ️  No .puml files found in output directory" -ForegroundColor Yellow
    Pop-Location
    exit 0
}

Write-Host "📊 Found $($pumlFiles.Count) .puml file(s)" -ForegroundColor Green

# Convert each .puml file to PNG
$successCount = 0
$failCount = 0

foreach ($file in $pumlFiles) {
    Write-Host "🔄 Converting $($file.Name) to PNG..." -ForegroundColor Cyan
    
    # Convert to PNG using PlantUML
    $result = & cmd /c "$plantumlCmd -tpng `"$($file.Name)`"" 2>$null
    
    # Check if PNG was created successfully
    $pngFile = [System.IO.Path]::ChangeExtension($file.FullName, "png")
    if (Test-Path $pngFile) {
        Write-Host "✅ Created $($file.BaseName).png" -ForegroundColor Green
        $successCount++
    }
    else {
        Write-Host "❌ Failed to generate $($file.BaseName).png" -ForegroundColor Red
        $failCount++
    }
}

Write-Host ""
Write-Host "📊 PlantUML to PNG conversion summary:" -ForegroundColor Cyan
Write-Host "   ✅ Successfully converted: $successCount file(s)" -ForegroundColor Green
Write-Host "   ❌ Failed conversions: $failCount file(s)" -ForegroundColor Red

if ($failCount -eq 0) {
    Write-Host "✅ All PlantUML files converted successfully!" -ForegroundColor Green
}
else {
    Write-Host "⚠️  Some conversions failed. Check the output above for details." -ForegroundColor Yellow
}

Write-Host "📁 Check the output directory for generated PNG images." -ForegroundColor Cyan

Pop-Location