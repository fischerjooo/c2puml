#!/bin/bash

# Complete workflow script that chains together: run_all_tests -> run_example -> picgen
# This script simply calls the other shell scripts in sequence

set -e  # Exit on any error

echo "🚀 Starting complete workflow..."
echo "=================================="

# Step 1: Run all tests
echo "📋 Step 1: Running all tests..."
echo "----------------------------------------"
$(dirname "$0")/run_all_tests.sh
echo "✅ All tests passed!"

echo ""

# Step 2: Run example
echo "📋 Step 2: Running example..."
echo "----------------------------------------"
$(dirname "$0")/run_example.sh
echo "✅ Example completed successfully!"

echo ""

# Step 3: Generate PNG images
echo "📋 Step 3: Generating PNG images..."
echo "----------------------------------------"
$(dirname "$0")/picgen.sh
echo "✅ PNG generation completed successfully!"

echo ""
echo "🎉 Complete workflow finished successfully!"
echo "=================================="
echo "📁 Check the output directory for generated files:"
echo "   - .puml files (PlantUML diagrams)"
echo "   - .png files (Generated images)"
echo "   - .json files (Configuration and results)"