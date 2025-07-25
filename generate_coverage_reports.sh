#!/bin/bash

# Coverage Report Generation Script
# This script generates comprehensive coverage reports in multiple formats
# Usage: ./generate_coverage_reports.sh [format] [verbosity]
# format: all|html|xml|json (default: all)
# verbosity: 0|1|2 (default: 1)

set -e  # Exit on any error

# Configuration
COVERAGE_FORMAT="${1:-all}"
VERBOSITY="${2:-1}"
REPORTS_DIR="tests/reports"

echo "🧪 Starting comprehensive coverage report generation..."
echo "📊 Coverage format: $COVERAGE_FORMAT"
echo "📋 Test verbosity: $VERBOSITY"

# Create reports directory
mkdir -p "$REPORTS_DIR"

# Run tests with coverage
echo "🧪 Running tests with coverage..."
coverage erase
coverage run -m unittest discover tests -v

# Save test results separately (re-run without coverage for clean output)
echo "📋 Generating clean test output..."
python3 run_all_tests.py --verbosity "$VERBOSITY" --stats > "$REPORTS_DIR/test-results.txt" 2>&1 || true

# Generate coverage reports in multiple formats
echo "📈 Generating coverage reports..."

if [ "$COVERAGE_FORMAT" = "all" ] || [ "$COVERAGE_FORMAT" = "html" ]; then
    echo "📊 Generating detailed HTML coverage report..."
    coverage html -d "$REPORTS_DIR/coverage-html" --title "Code Coverage Report" --show-contexts
    echo "✅ HTML coverage report generated in $REPORTS_DIR/coverage-html/"
fi

if [ "$COVERAGE_FORMAT" = "all" ] || [ "$COVERAGE_FORMAT" = "xml" ]; then
    coverage xml -o "$REPORTS_DIR/coverage.xml"
    echo "✅ XML coverage report generated"
fi

if [ "$COVERAGE_FORMAT" = "all" ] || [ "$COVERAGE_FORMAT" = "json" ]; then
    coverage json -o "$REPORTS_DIR/coverage.json"
    echo "✅ JSON coverage report generated"
fi

# Generate text summary
coverage report > "$REPORTS_DIR/coverage-summary.txt"

# Generate detailed coverage data
coverage report --show-missing > "$REPORTS_DIR/coverage-detailed.txt"

# Generate annotated coverage report with line-by-line analysis
echo "📊 Generating annotated coverage report..."
coverage annotate -d "$REPORTS_DIR/coverage-annotated"
echo "✅ Annotated coverage report generated in $REPORTS_DIR/coverage-annotated/"

# Create a comprehensive coverage index page
echo "📋 Creating coverage reports index..."
cat > "$REPORTS_DIR/coverage-index.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Coverage Reports Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .card { background: #f5f5f5; padding: 20px; margin: 15px 0; border-radius: 8px; }
        .card h3 { margin-top: 0; color: #333; }
        .card p { color: #666; margin: 10px 0; }
        .btn { background: #007cba; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; display: inline-block; }
        .btn:hover { background: #005a87; }
        .timestamp { color: #888; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>📊 Code Coverage Reports</h1>
    <p class="timestamp">Generated: $(date)</p>
    
    <div class="card">
        <h3>🌐 Interactive HTML Report</h3>
        <p>Complete coverage report with syntax highlighting and interactive features.</p>
        <a href="coverage-html/index.html" class="btn">View HTML Report</a>
    </div>
    
    <div class="card">
        <h3>📝 Annotated Source Files</h3>
        <p>Source code with coverage annotations showing covered/uncovered lines.</p>
        <a href="coverage-annotated/" class="btn">View Annotated Files</a>
    </div>
    
    <div class="card">
        <h3>📄 Text Reports</h3>
        <p>Coverage summary and detailed missing line information in text format.</p>
        <a href="coverage-summary.txt" class="btn">Summary</a>
        <a href="coverage-detailed.txt" class="btn">Detailed</a>
    </div>
    
    <div class="card">
        <h3>🧪 Test Execution Results</h3>
        <p>Complete test execution logs and results.</p>
        <a href="test-results.txt" class="btn">View Test Results</a>
    </div>
</body>
</html>
EOF
echo "✅ Coverage reports index created at $REPORTS_DIR/coverage-index.html"

# Generate test execution summary if the script exists
if [ -f "$REPORTS_DIR/generate_test_summary.py" ]; then
    echo "📊 Generating test execution summary..."
    python3 "$REPORTS_DIR/generate_test_summary.py"
    echo "📝 Test summary generated"
fi

echo "📊 Coverage analysis complete"

# Display summary
echo ""
echo "🏆 Coverage Report Generation Complete!"
echo "================================"

if [ -f "$REPORTS_DIR/coverage-summary.txt" ]; then
    echo "📊 Coverage Summary:"
    echo "-------------------"
    cat "$REPORTS_DIR/coverage-summary.txt"
    echo ""
fi

echo "📁 Generated Reports:"
echo "--------------------"
find "$REPORTS_DIR" -type f -name "*" | sort
echo ""

echo "📏 Report Sizes:"
echo "---------------"
du -h "$REPORTS_DIR"/* 2>/dev/null || true

echo ""
echo "🌐 Open the coverage dashboard in your browser:"
echo "file://$(pwd)/$REPORTS_DIR/coverage-index.html"