#!/bin/bash

# PlantUML to PNG converter script
# This script converts all .puml files in the output folder to PNG images
# Usage: ./picgen.sh [plantuml_jar_path]
# Example: ./picgen.sh "/home/username/.vscode/extensions/jebbs.plantuml-2.18.1/plantuml.jar"

set -e  # Exit on any error

# Parse command line arguments
CUSTOM_PLANTUML_JAR=""
if [ $# -gt 0 ]; then
    CUSTOM_PLANTUML_JAR="$1"
    echo "📁 Using custom PlantUML JAR path: $CUSTOM_PLANTUML_JAR"
fi

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

# Function to validate JAR file
validate_jar_file() {
    local jar_path="$1"
    if [ ! -f "$jar_path" ]; then
        return 1
    fi
    # Check if file size is greater than 0
    if [ ! -s "$jar_path" ]; then
        echo "⚠️  JAR file is empty or corrupted: $jar_path"
        return 1
    fi
    # Test if the JAR file is valid
    if ! java -jar "$jar_path" -version &> /dev/null; then
        echo "⚠️  JAR file appears to be corrupted: $jar_path"
        return 1
    fi
    return 0
}

# Check if plantuml is installed or if we have the JAR file
if ! command -v plantuml &> /dev/null; then
    # Check custom PlantUML JAR path first
    if [ -n "$CUSTOM_PLANTUML_JAR" ] && validate_jar_file "$CUSTOM_PLANTUML_JAR"; then
        PLANTUML_CMD="java -jar \"$CUSTOM_PLANTUML_JAR\""
        echo "📦 Using custom PlantUML JAR file: $CUSTOM_PLANTUML_JAR"
    elif validate_jar_file "../plantuml.jar"; then
        PLANTUML_CMD="java -jar ../plantuml.jar"
        echo "📦 Using PlantUML JAR file from parent directory"
    elif validate_jar_file "plantuml.jar"; then
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
        
        # Remove corrupted JAR file if it exists
        if [ -f "plantuml.jar" ]; then
            echo "🗑️  Removing corrupted/empty plantuml.jar file"
            rm -f plantuml.jar
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
        
        if [ $? -eq 0 ] && validate_jar_file "plantuml.jar"; then
            echo "✅ PlantUML JAR file downloaded and validated successfully"
            PLANTUML_CMD="java -jar plantuml.jar"
        else
            echo "❌ Failed to download or validate PlantUML JAR file"
            echo "   Please download it manually from: $PLANTUML_URL"
            echo "   Make sure the downloaded file is not corrupted"
            rm -f plantuml.jar  # Remove potentially corrupted download
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

# Generate diagram index HTML file
echo "📄 Generating diagram index HTML file..."
generate_diagram_index() {
    local output_dir="$1"
    local index_file="$output_dir/diagram_index.html"
    
    # Get current timestamp
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S UTC')
    
    # Find all PNG files
    local png_files=$(find "$output_dir" -name "*.png" -type f | sort)
    local png_count=$(echo "$png_files" | wc -l)
    
    # Find all PlantUML files
    local puml_files=$(find "$output_dir" -name "*.puml" -type f | sort)
    local puml_count=$(echo "$puml_files" | wc -l)
    
    # Create the HTML file
    cat > "$index_file" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PlantUML Diagrams - C to PlantUML Converter</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            line-height: 1.6; 
            margin: 0; 
            padding: 20px; 
            background: #f6f8fa; 
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
        }
        .header { 
            background: white; 
            padding: 20px; 
            border-radius: 6px; 
            margin-bottom: 20px; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
        }
        .nav { 
            background: #0366d6; 
            color: white; 
            padding: 15px 20px; 
            border-radius: 6px; 
            margin-bottom: 20px; 
        }
        .nav a { 
            color: white; 
            text-decoration: none; 
            margin-right: 20px; 
            font-weight: 500; 
        }
        .nav a:hover { 
            text-decoration: underline; 
        }
        .stats { 
            background: white; 
            padding: 15px; 
            border-radius: 6px; 
            margin-bottom: 20px; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
        }
        .diagram-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr)); 
            gap: 20px; 
            margin-top: 20px; 
        }
        .diagram-card { 
            background: white; 
            border-radius: 6px; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
            overflow: hidden; 
            transition: transform 0.2s; 
        }
        .diagram-card:hover { 
            transform: translateY(-2px); 
            box-shadow: 0 4px 8px rgba(0,0,0,0.15); 
        }
        .diagram-card h3 { 
            margin: 0; 
            padding: 15px; 
            background: #f1f3f4; 
            border-bottom: 1px solid #e1e4e8; 
            font-size: 16px; 
            color: #24292e; 
        }
        .diagram-image { 
            width: 100%; 
            height: auto; 
            display: block; 
        }
        .diagram-links { 
            padding: 15px; 
            background: #f8f9fa; 
        }
        .diagram-links a { 
            display: inline-block; 
            margin: 5px 10px 5px 0; 
            padding: 5px 10px; 
            background: #0366d6; 
            color: white; 
            text-decoration: none; 
            border-radius: 4px; 
            font-size: 12px; 
        }
        .diagram-links a:hover { 
            background: #0256b3; 
        }
        .footer { 
            text-align: center; 
            margin-top: 40px; 
            padding: 20px; 
            color: #586069; 
        }
        .no-diagrams { 
            background: white; 
            padding: 40px; 
            text-align: center; 
            border-radius: 6px; 
            box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="nav">
            <span>📊 Diagrams</span>
        </div>
        
        <div class="header">
            <h1>📊 PlantUML Diagrams</h1>
            <p>Generated diagrams from C/C++ source code analysis</p>
            <p><strong>Generated:</strong> $timestamp</p>
        </div>
        
        <div class="stats">
            <h3>📈 Statistics</h3>
            <p><strong>PNG Images:</strong> $png_count</p>
            <p><strong>PlantUML Files:</strong> $puml_count</p>
            <p><strong>Total Files:</strong> $((png_count + puml_count))</p>
        </div>
EOF

    # Check if we have any PNG files
    if [ -n "$png_files" ]; then
        echo "        <div class=\"diagram-grid\">" >> "$index_file"
        
        # Process each PNG file
        while IFS= read -r png_file; do
            local filename=$(basename "$png_file")
            local basename=$(basename "$png_file" .png)
            local relative_path=$(echo "$png_file" | sed "s|^$output_dir/||")
            
            # Check if corresponding PlantUML file exists
            local puml_file="$output_dir/${basename}.puml"
            local puml_link=""
            if [ -f "$puml_file" ]; then
                local puml_relative=$(echo "$puml_file" | sed "s|^$output_dir/||")
                puml_link="<a href=\"$puml_relative\">📄 Source</a>"
            fi
            
            cat >> "$index_file" << EOF
            
            <div class="diagram-card">
                <h3>$basename</h3>
                <img src="$relative_path" alt="$basename diagram" class="diagram-image" loading="lazy">
                <div class="diagram-links">
                    <a href="$relative_path" target="_blank">🖼️ Full Size</a>
                    $puml_link
                </div>
            </div>
EOF
        done <<< "$png_files"
        
        echo "        </div>" >> "$index_file"
    else
        cat >> "$index_file" << EOF
        
        <div class="no-diagrams">
            <h3>📭 No Diagrams Found</h3>
            <p>No PNG images were found in the output directory.</p>
            <p>Run the conversion script to generate diagrams from PlantUML files.</p>
        </div>
EOF
    fi
    
    cat >> "$index_file" << EOF
        
        <div class="footer">
            <p>Generated by <a href="https://github.com/fischerjooo/generator_project">C to PlantUML Converter</a></p>
            <p>Last updated: $timestamp</p>
        </div>
    </div>
</body>
</html>
EOF
    
    echo "✅ Diagram index generated: $index_file"
    echo "📊 Found $png_count PNG files and $puml_count PlantUML files"
}

# Generate the diagram index
generate_diagram_index "."