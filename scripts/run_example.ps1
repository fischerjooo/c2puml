# PowerShell script to run c2puml example
param(
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

# Get script directory and change to project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir\..

Write-Host "Setting up c2puml development environment..." -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python version: $pythonVersion" -ForegroundColor Cyan
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python and ensure it's in your PATH" -ForegroundColor Yellow
    exit 1
}

# Check if c2puml is installed
try {
    python -c "import c2puml" 2>$null
    Write-Host "c2puml module found." -ForegroundColor Green
} catch {
    Write-Host "c2puml module not found. Installing in development mode..." -ForegroundColor Yellow
    
    try {
        python -m pip install -e .
        Write-Host "Installation successful!" -ForegroundColor Green
    } catch {
        Write-Host "Failed to install c2puml. Trying with --break-system-packages..." -ForegroundColor Yellow
        try {
            python -m pip install -e . --break-system-packages
            Write-Host "Installation successful!" -ForegroundColor Green
        } catch {
            Write-Host "Error: Could not install c2puml package" -ForegroundColor Red
            Write-Host "Please run scripts\setup.bat first" -ForegroundColor Yellow
            exit 1
        }
    }
}

# Clean previous output
Write-Host "Cleaning previous output..." -ForegroundColor Cyan
if (Test-Path "artifacts\output_example") {
    Remove-Item "artifacts\output_example" -Recurse -Force
}
if (Test-Path "tests\example\artifacts\output_example") {
    Remove-Item "tests\example\artifacts\output_example" -Recurse -Force
}

# Run the full workflow
Write-Host "Running example workflow with config.json..." -ForegroundColor Cyan
$env:PYTHONPATH = "src"

try {
    if ($Verbose) {
        python -m c2puml.main --config tests/example/config.json --verbose
    } else {
        python -m c2puml.main --config tests/example/config.json
    }
} catch {
    Write-Host "Error: Failed to run c2puml" -ForegroundColor Red
    Write-Host "This might be a PATH issue. Try these alternative commands:" -ForegroundColor Yellow
    Write-Host "  python -m c2puml.main --config tests/example/config.json --verbose" -ForegroundColor White
    Write-Host "  c2puml --config tests/example/config.json --verbose" -ForegroundColor White
    exit 1
}

Write-Host "PlantUML diagrams generated in: ./artifacts/output_example" -ForegroundColor Green

# Run assertions
Write-Host "Running assertions to validate generated PUML files..." -ForegroundColor Cyan
Set-Location tests/example
python test-example.py

Write-Host "Example completed successfully!" -ForegroundColor Green