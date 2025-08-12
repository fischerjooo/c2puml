#!/bin/bash

# Complete workflow script that chains together: run_all_tests -> run_example -> picgen
# This script simply calls the other shell scripts in sequence

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/.."

echo "🚀 Starting complete workflow..."
echo "=================================="

# Step 0: Validate tests mapping rules
echo "🔎 Pre-check: Validating tests mapping rules..."
python3 "$PROJECT_ROOT/scripts/check_tests_mapping.py"
echo "✅ Test mapping validation passed!"

echo ""

# Step 1: Run all tests
echo "📋 Step 1: Running all tests..."
echo "----------------------------------------"
"$SCRIPT_DIR"/run_all_tests.sh
echo "✅ All tests passed!"

echo ""

# Step 2: Run example
echo "📋 Step 2: Running example..."
echo "----------------------------------------"
"$SCRIPT_DIR"/run_example.sh
echo "✅ Example completed successfully!"

echo ""

# Step 3: Generate PNG images
echo "📋 Step 3: Generating PNG images..."
echo "----------------------------------------"
"$SCRIPT_DIR"/picgen.sh
echo "✅ PNG generation completed successfully!"

echo ""

# Step 4: Verify artifacts/output_example contents
echo "📋 Step 4: Verifying generated artifacts..."
echo "----------------------------------------"
OUTPUT_DIR="$PROJECT_ROOT/artifacts/output_example"

if [ ! -d "$OUTPUT_DIR" ]; then
  echo "❌ Output directory not found: $OUTPUT_DIR" >&2
  exit 1
fi

required_basenames=(
  application complex database geometry logger math_utils network preprocessed sample sample2 transformed typedef_test
)

missing=0
for base in "${required_basenames[@]}"; do
  if [ ! -f "$OUTPUT_DIR/${base}.puml" ]; then
    echo "❌ Missing PUML: ${base}.puml" >&2
    missing=1
  fi
  if [ ! -f "$OUTPUT_DIR/${base}.png" ]; then
    echo "❌ Missing PNG: ${base}.png" >&2
    missing=1
  fi
done

# Check model files and index
for f in model.json model_transformed.json diagram_index.html; do
  if [ ! -f "$OUTPUT_DIR/$f" ]; then
    echo "❌ Missing file: $f" >&2
    missing=1
  fi
done

if [ $missing -ne 0 ]; then
  echo "⚠️  Artifact verification failed. See missing items above." >&2
  exit 1
fi

echo "✅ All expected artifacts are present in $OUTPUT_DIR"

echo "🎉 Complete workflow finished successfully!"
echo "=================================="
echo "📁 Check the output directory for generated files:"
echo "   - .puml files (PlantUML diagrams)"
echo "   - .png files (Generated images)"
echo "   - .json files (Configuration and results)"