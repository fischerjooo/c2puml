#!/bin/bash

# Test Execution with Coverage Script
# This script runs tests with coverage but does not generate reports
# Usage: ./run_tests_coverage.sh [verbosity]
# verbosity: 0|1|2 (default: 1)

set -e  # Exit on any error

# Configuration
VERBOSITY="${1:-1}"
REPORTS_DIR="tests/reports"

echo "🧪 Running tests with coverage analysis..."
echo "📋 Test verbosity: $VERBOSITY"

# Create reports directory
mkdir -p "$REPORTS_DIR"

# Clear any existing coverage data
echo "🧹 Clearing previous coverage data..."
coverage erase

# Run tests with coverage
echo "🧪 Executing test suite with coverage..."
coverage run -m unittest discover tests -v

# Save test results separately (re-run without coverage for clean output)
echo "📋 Generating clean test execution log..."
python3 run_all_tests.py --verbosity "$VERBOSITY" --stats > "$REPORTS_DIR/test-results.txt" 2>&1 || true

echo "✅ Test execution with coverage complete!"
echo "📊 Coverage data collected and ready for report generation"

# Display basic coverage info
echo ""
echo "📈 Basic Coverage Summary:"
echo "-------------------------"
coverage report || echo "Coverage data available for report generation"