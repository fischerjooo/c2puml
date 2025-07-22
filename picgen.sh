#!/bin/bash

# PlantUML to JPEG converter script
# This script converts all .puml files in the output folder to JPEG images

set -e  # Exit on any error

echo "🔄 Starting PlantUML to JPEG conversion..."

# Check if output directory exists
if [ ! -d "output" ]; then
    echo "❌ Error: output directory not found"
    exit 1
fi

# Check if plantuml is installed
if ! command -v plantuml &> /dev/null; then
    echo "❌ Error: plantuml command not found. Please install PlantUML first."
    echo "   You can install it with: sudo apt-get install plantuml"
    exit 1
fi

# Change to output directory
cd output

# Find all .puml files and convert them to JPEG
echo "📁 Scanning for .puml files in output directory..."
puml_files=$(find . -name "*.puml" -type f)

if [ -z "$puml_files" ]; then
    echo "ℹ️  No .puml files found in output directory"
    exit 0
fi

echo "📊 Found $(echo "$puml_files" | wc -l) .puml file(s)"

# Convert each .puml file to JPEG
for puml_file in $puml_files; do
    echo "🔄 Converting $puml_file to JPEG..."
    
    # Get the base name without extension
    base_name=$(basename "$puml_file" .puml)
    
    # Convert to PNG using PlantUML
    plantuml -tpng "$puml_file"
    
    # Check if PNG was created
    if [ -f "${base_name}.png" ]; then
        # Try to convert PNG to JPEG using ImageMagick if available
        if command -v convert &> /dev/null; then
            echo "🔄 Converting ${base_name}.png to JPEG..."
            convert "${base_name}.png" "${base_name}.jpg"
            echo "✅ Created ${base_name}.jpg"
        else
            echo "⚠️  ImageMagick not found. JPEG conversion skipped."
            echo "   Install ImageMagick with: sudo apt-get install imagemagick"
        fi
        
        # Always clean up the temporary PNG file
        rm "${base_name}.png"
        echo "🧹 Cleaned up temporary ${base_name}.png"
    else
        echo "❌ Failed to generate ${base_name}.png"
    fi
done

echo "✅ PlantUML to JPEG conversion completed!"
echo "📁 Check the output directory for generated images."