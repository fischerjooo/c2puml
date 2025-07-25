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
        body {
            font-family: monospace;
            line-height: 1.4;
            margin: 0;
            padding: 15px;
            background-color: white;
            color: #333;
            font-size: 14px;
        }
        h1, h3 {
            color: #333;
            font-weight: normal;
            margin: 20px 0 10px 0;
            padding: 0;
            border: none;
            background: none;
            font-family: monospace;
        }
        h1 {
            font-size: 18px;
            border-bottom: 1px solid #ccc;
            padding-bottom: 5px;
        }
        h3 {
            font-size: 14px;
            margin: 15px 0 5px 0;
        }
        p {
            margin: 5px 0 10px 0;
            color: #666;
            font-size: 13px;
        }
        a {
            color: #0066cc;
            text-decoration: none;
            display: block;
            margin: 5px 0;
            padding: 3px 0;
        }
        a:hover {
            text-decoration: underline;
        }
        .timestamp {
            color: #888;
            font-size: 12px;
            margin-bottom: 20px;
        }
        .report-section {
            margin: 20px 0;
            padding: 10px 0;
            border-bottom: 1px dotted #ccc;
        }
        @media (max-width: 768px) {
            body {
                padding: 8px;
                font-size: 13px;
            }
            h1 {
                font-size: 16px;
            }
            h3 {
                font-size: 13px;
            }
            p {
                font-size: 12px;
            }
        }
    </style>
</head>
<body>
    <h1>Coverage Reports Dashboard</h1>
    <p class="timestamp">Generated: $(date)</p>
    
    <div class="report-section">
        <h3>Interactive HTML Report</h3>
        <p>Complete coverage report with syntax highlighting and interactive features.</p>
        <a href="coverage-html/index.html">View HTML Report</a>
    </div>
    
    <div class="report-section">
        <h3>Text Reports</h3>
        <p>Coverage summary and detailed missing line information in text format.</p>
        <a href="coverage-summary.txt">Coverage Summary</a>
        <a href="coverage-detailed.txt">Detailed Report</a>
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