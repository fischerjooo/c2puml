#!/bin/bash

# Simple Test Execution with Coverage Script
# This script runs tests and generates basic HTML coverage reports
# Usage: ./run_tests_with_coverage.sh

set -e  # Exit on any error

REPORTS_DIR="tests/reports"

echo "🧪 Running comprehensive test suite with coverage..."

# Create reports directory
mkdir -p "$REPORTS_DIR"

# Run tests with coverage
coverage erase
coverage run -m unittest discover tests -v

# Generate HTML coverage report
echo "📊 Generating HTML coverage report..."
coverage html -d "$REPORTS_DIR/coverage-html" --title "Code Coverage Report" --show-contexts

# Generate text reports
coverage report > "$REPORTS_DIR/coverage-summary.txt"
coverage report --show-missing > "$REPORTS_DIR/coverage-detailed.txt"

# Create coverage index page
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
        <h3>📄 Text Reports</h3>
        <p>Coverage summary and detailed missing line information in text format.</p>
        <a href="coverage-summary.txt" class="btn">Summary</a>
        <a href="coverage-detailed.txt" class="btn">Detailed</a>
    </div>
</body>
</html>
EOF

echo "✅ Coverage reports generated in $REPORTS_DIR/"

# Display summary
if [ -f "$REPORTS_DIR/coverage-summary.txt" ]; then
    echo ""
    echo "📊 Coverage Summary:"
    echo "-------------------"
    cat "$REPORTS_DIR/coverage-summary.txt"
fi

echo ""
echo "🌐 Open the coverage dashboard: file://$(pwd)/$REPORTS_DIR/coverage-index.html"