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

# Check if plantuml is installed or if we have the JAR file
if ! command -v plantuml &> /dev/null; then
    if [ -f "../plantuml.jar" ]; then
        PLANTUML_CMD="java -jar ../plantuml.jar"
        echo "📦 Using PlantUML JAR file from parent directory"
    elif [ -f "plantuml.jar" ]; then
        PLANTUML_CMD="java -jar ../plantuml.jar"
        echo "📦 Using PlantUML JAR file from parent directory"
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
            PLANTUML_CMD="java -jar ../plantuml.jar"
        else
            echo "❌ Failed to download PlantUML JAR file"
            echo "   Please download it manually from: $PLANTUML_URL"
            exit 1
        fi
    fi
else
    PLANTUML_CMD="plantuml"
fi

# Change to output directory
cd output

# Find all .puml files and convert them to PNG
echo "📁 Scanning for .puml files in output directory..."
puml_files=$(find . -name "*.puml" -type f)

if [ -z "$puml_files" ]; then
    echo "ℹ️  No .puml files found in output directory"
    exit 0
fi

echo "📊 Found $(echo "$puml_files" | wc -l) .puml file(s)"

# Convert each .puml file to PNG
for puml_file in $puml_files; do
    echo "🔄 Converting $puml_file to PNG..."
    
    # Convert to PNG using PlantUML
    $PLANTUML_CMD -tpng "$puml_file"
    
    # Check if PNG was created successfully
    base_name=$(basename "$puml_file" .puml)
    if [ -f "${base_name}.png" ]; then
        echo "✅ Created ${base_name}.png"
    else
        echo "❌ Failed to generate ${base_name}.png"
    fi
done

echo "✅ PlantUML to PNG conversion completed!"
echo "📁 Check the output directory for generated PNG images."