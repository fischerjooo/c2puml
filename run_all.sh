#!/bin/bash

# Complete workflow script that runs all tests, example, and generates PNG images
# This script chains together: run_all_tests -> run_example -> picgen

set -e  # Exit on any error

echo "🚀 Starting complete workflow..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if required commands exist
if ! command_exists python3; then
    print_status $RED "❌ Error: python3 is not installed"
    exit 1
fi

if ! command_exists java; then
    print_status $YELLOW "⚠️  Warning: java is not installed. PlantUML conversion may fail."
fi

# Step 1: Run all tests
print_status $BLUE "📋 Step 1: Running all tests..."
echo "----------------------------------------"
if python3 run_all_tests.py; then
    print_status $GREEN "✅ All tests passed!"
else
    print_status $RED "❌ Tests failed! Stopping workflow."
    exit 1
fi

echo ""

# Step 2: Run example
print_status $BLUE "📋 Step 2: Running example..."
echo "----------------------------------------"
if ./run_example.sh; then
    print_status $GREEN "✅ Example completed successfully!"
else
    print_status $RED "❌ Example failed! Stopping workflow."
    exit 1
fi

echo ""

# Step 3: Generate PNG images
print_status $BLUE "📋 Step 3: Generating PNG images..."
echo "----------------------------------------"
if ./picgen.sh; then
    print_status $GREEN "✅ PNG generation completed successfully!"
else
    print_status $RED "❌ PNG generation failed!"
    exit 1
fi

echo ""
print_status $GREEN "🎉 Complete workflow finished successfully!"
echo "=================================="
print_status $BLUE "📁 Check the output directory for generated files:"
echo "   - .puml files (PlantUML diagrams)"
echo "   - .png files (Generated images)"
echo "   - .json files (Configuration and results)"

# Show summary of generated files
if [ -d "output" ]; then
    echo ""
    print_status $BLUE "📊 Generated files summary:"
    echo "----------------------------------------"
    
    puml_count=$(find output -name "*.puml" | wc -l)
    png_count=$(find output -name "*.png" | wc -l)
    json_count=$(find output -name "*.json" | wc -l)
    
    echo "   📄 PlantUML files (.puml): $puml_count"
    echo "   🖼️  PNG images (.png): $png_count"
    echo "   📋 JSON files (.json): $json_count"
    
    if [ $png_count -gt 0 ]; then
        echo ""
        print_status $GREEN "🖼️  Generated PNG images:"
        for png_file in output/*.png; do
            if [ -f "$png_file" ]; then
                size=$(du -h "$png_file" | cut -f1)
                echo "   - $(basename "$png_file") ($size)"
            fi
        done
    fi
fi

echo ""
print_status $GREEN "✨ Workflow completed! All steps passed successfully."