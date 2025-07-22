#!/bin/bash

# PlantUML to PNG converter script
# This script converts all .puml files in the output folder to PNG images

set -e  # Exit on any error

echo "🔄 Starting PlantUML to PNG conversion..."

# Check if output directory exists
if [ ! -d "output" ]; then
    echo "❌ Error: output directory not found"
    exit 1
fi

# Function to install Graphviz
install_graphviz() {
    echo "📦 Installing Graphviz..."
    
    # Detect OS and install Graphviz
    if command -v apt-get &> /dev/null; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y graphviz
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum install -y graphviz
    elif command -v brew &> /dev/null; then
        # macOS with Homebrew
        brew install graphviz
    elif command -v pacman &> /dev/null; then
        # Arch Linux
        sudo pacman -S graphviz
    else
        echo "❌ Error: Could not detect package manager for Graphviz installation"
        echo "   Please install Graphviz manually:"
        echo "   - Ubuntu/Debian: sudo apt-get install graphviz"
        echo "   - CentOS/RHEL: sudo yum install graphviz"
        echo "   - macOS: brew install graphviz"
        echo "   - Arch: sudo pacman -S graphviz"
        return 1
    fi
}

# Function to test PlantUML setup
test_plantuml_setup() {
    local plantuml_cmd="$1"
    echo "🔍 Testing PlantUML setup..."
    
    # Test if PlantUML can find the dot executable
    if $plantuml_cmd -testdot 2>&1 | grep -q "Installation seems OK"; then
        echo "✅ PlantUML setup is working correctly"
        return 0
    else
        echo "❌ PlantUML cannot find the dot executable (Graphviz)"
        echo "   Attempting to install Graphviz..."
        
        if install_graphviz; then
            echo "✅ Graphviz installed successfully"
            # Test again after installation
            if $plantuml_cmd -testdot 2>&1 | grep -q "Installation seems OK"; then
                echo "✅ PlantUML setup is now working correctly"
                return 0
            else
                echo "❌ PlantUML still cannot find dot executable after Graphviz installation"
                return 1
            fi
        else
            echo "❌ Failed to install Graphviz automatically"
            return 1
        fi
    fi
}

# Check if plantuml is installed or if we have the JAR file
if ! command -v plantuml &> /dev/null; then
    if [ -f "../plantuml.jar" ]; then
        PLANTUML_CMD="java -jar ../plantuml.jar"
        echo "📦 Using PlantUML JAR file from parent directory"
    elif [ -f "plantuml.jar" ]; then
        PLANTUML_CMD="java -jar plantuml.jar"
        echo "📦 Using PlantUML JAR file from current directory"
    else
        echo "📥 PlantUML JAR file not found. Downloading..."
        
        # Check if wget is available
        if command -v wget &> /dev/null; then
            DOWNLOAD_CMD="wget"
        elif command -v curl &> /dev/null; then
            DOWNLOAD_CMD="curl -L -o"
        else
            echo "❌ Error: Neither wget nor curl found. Cannot download PlantUML."
            echo "   Please install wget or curl, or download plantuml.jar manually"
            exit 1
        fi
        
        # Download PlantUML JAR file
        PLANTUML_VERSION="1.2024.0"
        PLANTUML_URL="https://github.com/plantuml/plantuml/releases/download/v${PLANTUML_VERSION}/plantuml-${PLANTUML_VERSION}.jar"
        
        echo "🔄 Downloading PlantUML v${PLANTUML_VERSION}..."
        
        if [ "$DOWNLOAD_CMD" = "wget" ]; then
            wget "$PLANTUML_URL" -O plantuml.jar
        else
            curl -L -o plantuml.jar "$PLANTUML_URL"
        fi
        
        if [ $? -eq 0 ] && [ -f "plantuml.jar" ]; then
            echo "✅ PlantUML JAR file downloaded successfully"
            PLANTUML_CMD="java -jar plantuml.jar"
        else
            echo "❌ Failed to download PlantUML JAR file"
            echo "   Please download it manually from: $PLANTUML_URL"
            exit 1
        fi
    fi
else
    PLANTUML_CMD="plantuml"
fi

# Store the current directory to reference the JAR file correctly
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to output directory
cd output

# Update PLANTUML_CMD to use absolute path if it's a JAR file
if [[ "$PLANTUML_CMD" == *"plantuml.jar"* ]]; then
    if [[ "$PLANTUML_CMD" == *"../plantuml.jar"* ]]; then
        PLANTUML_CMD="java -jar ${SCRIPT_DIR}/plantuml.jar"
    elif [[ "$PLANTUML_CMD" == *"plantuml.jar"* ]]; then
        PLANTUML_CMD="java -jar ${SCRIPT_DIR}/plantuml.jar"
    fi
fi

# Test PlantUML setup before proceeding
if ! test_plantuml_setup "$PLANTUML_CMD"; then
    echo "❌ PlantUML setup test failed. Cannot proceed with conversion."
    echo "💡 Manual troubleshooting steps:"
    echo "   1. Install Graphviz: sudo apt-get install graphviz (Ubuntu/Debian)"
    echo "   2. Verify dot is in PATH: which dot"
    echo "   3. Test PlantUML: $PLANTUML_CMD -testdot"
    exit 1
fi

# Find all .puml files and convert them to PNG
echo "📁 Scanning for .puml files in output directory..."
puml_files=$(find . -name "*.puml" -type f)

if [ -z "$puml_files" ]; then
    echo "ℹ️  No .puml files found in output directory"
    exit 0
fi

echo "📊 Found $(echo "$puml_files" | wc -l) .puml file(s)"

# Track success and failure counts
success_count=0
failure_count=0
failed_files=()

# Convert each .puml file to PNG
for puml_file in $puml_files; do
    echo "🔄 Converting $puml_file to PNG..."
    
    # Get the base name for the output file
    base_name=$(basename "$puml_file" .puml)
    png_file="${base_name}.png"
    
    # Remove any existing PNG file to ensure clean generation
    if [ -f "$png_file" ]; then
        rm "$png_file"
    fi
    
    # Convert to PNG using PlantUML and capture both output and error
    # Use a temporary file to capture the output
    temp_output=$(mktemp)
    temp_error=$(mktemp)
    
    if $PLANTUML_CMD -tpng "$puml_file" > "$temp_output" 2> "$temp_error"; then
        # PlantUML command succeeded
        if [ -f "$png_file" ]; then
            echo "✅ Created $png_file"
            success_count=$((success_count + 1))
        else
            echo "❌ PlantUML succeeded but $png_file was not created"
            echo "   This might indicate a PlantUML internal error"
            failure_count=$((failure_count + 1))
            failed_files+=("$puml_file (no output file)")
        fi
    else
        # PlantUML command failed
        echo "❌ Failed to generate $png_file"
        echo "   PlantUML error output:"
        if [ -s "$temp_error" ]; then
            # Indent error messages for better readability
            sed 's/^/   /' "$temp_error"
        else
            echo "   (No error output captured)"
        fi
        
        # Check if a PNG was created despite the error (this shouldn't happen but let's be safe)
        if [ -f "$png_file" ]; then
            echo "   Removing failed image file: $png_file"
            rm "$png_file"
        fi
        
        failure_count=$((failure_count + 1))
        failed_files+=("$puml_file")
    fi
    
    # Clean up temporary files
    rm -f "$temp_output" "$temp_error"
done

# Print summary
echo ""
echo "📊 PlantUML to PNG conversion summary:"
echo "   ✅ Successfully converted: $success_count file(s)"
echo "   ❌ Failed conversions: $failure_count file(s)"

if [ $failure_count -gt 0 ]; then
    echo ""
    echo "❌ Failed files:"
    for failed_file in "${failed_files[@]}"; do
        echo "   - $failed_file"
    done
    echo ""
    echo "💡 Tips for fixing failed conversions:"
    echo "   - Check the PlantUML syntax in the failed .puml files"
    echo "   - Ensure all referenced files and includes exist"
    echo "   - Verify that the PlantUML syntax is valid"
    echo "   - Check for any special characters or encoding issues"
fi

if [ $failure_count -gt 0 ]; then
    echo ""
    echo "⚠️  Some files failed to convert. Check the error messages above."
    exit 1
else
    echo ""
    echo "✅ All PlantUML files converted successfully!"
    echo "📁 Check the output directory for generated PNG images."
fi