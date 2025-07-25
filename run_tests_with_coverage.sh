#!/usr/bin/env bash

# run_tests_with_coverage.sh - Unified test runner with coverage reporting
# This script runs all tests, generates coverage reports, and creates a test summary

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to print section headers
print_header() {
    echo ""
    echo "=================================================================="
    echo "$1"
    echo "=================================================================="
    echo ""
}

# Start time
START_TIME=$(date +%s)

# Create reports directory
print_status "Creating reports directory..."
mkdir -p tests/reports

# Clean previous test data
print_status "Cleaning previous test data..."
rm -f tests/reports/*.txt tests/reports/*.log 2>/dev/null || true

print_header "Running Test Suite"

# Check if coverage is available
HAS_COVERAGE=false
if python3 -m coverage --version &>/dev/null; then
    HAS_COVERAGE=true
    print_status "Coverage module detected, will run tests with coverage"
else
    print_status "Coverage module not available, running tests without coverage"
fi

# Run all tests using the existing test runner
if [ "$HAS_COVERAGE" = true ]; then
    print_status "Running all unit tests with coverage..."
    python3 run_all_tests.py --coverage --verbosity 2 2>&1 | tee tests/reports/test-output.log
else
    print_status "Running all unit tests..."
    python3 run_all_tests.py --verbosity 2 2>&1 | tee tests/reports/test-output.log
fi

# Check if tests passed
TEST_EXIT_CODE=${PIPESTATUS[0]}
if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_success "All tests passed!"
else
    print_error "Some tests failed!"
fi

# Run example tests if run_example.sh exists
if [ -f "run_example.sh" ]; then
    print_status "Running example tests..."
    ./run_example.sh 2>&1 | tee tests/reports/example-output.log || true
fi

# Create test summary
print_header "Creating Test Summary"

print_status "Generating test summary report..."

# Create test summary file
cat > tests/reports/test-summary.txt << EOF
Test Execution Summary
=====================
Generated: $(date '+%Y-%m-%d %H:%M:%S')

Test Results
------------
EOF

# Extract test results from log
if [ -f "tests/reports/test-output.log" ]; then
    # Look for unittest test results summary line
    if grep -q "Ran [0-9]* test" tests/reports/test-output.log; then
        TEST_SUMMARY=$(grep -E "Ran [0-9]* test" tests/reports/test-output.log | tail -1)
        echo "$TEST_SUMMARY" >> tests/reports/test-summary.txt
        
        # Extract the actual test count from the summary
        ACTUAL_TEST_COUNT=$(echo "$TEST_SUMMARY" | grep -oE "[0-9]+" | head -1)
        
        # Check for OK or FAILED
        if grep -q "^OK$" tests/reports/test-output.log; then
            echo "Status: OK - All tests passed" >> tests/reports/test-summary.txt
            FAILED_COUNT=0
            PASSED_COUNT=$ACTUAL_TEST_COUNT
        elif grep -q "FAILED" tests/reports/test-output.log; then
            FAILURES=$(grep -E "FAILED \(.*\)" tests/reports/test-output.log | tail -1)
            echo "Status: FAILED - $FAILURES" >> tests/reports/test-summary.txt
            # Extract failure count
            FAILED_COUNT=$(echo "$FAILURES" | grep -oE "failures=[0-9]+" | grep -oE "[0-9]+" || echo "0")
            ERROR_COUNT=$(echo "$FAILURES" | grep -oE "errors=[0-9]+" | grep -oE "[0-9]+" || echo "0")
            FAILED_COUNT=$((FAILED_COUNT + ERROR_COUNT))
            PASSED_COUNT=$((ACTUAL_TEST_COUNT - FAILED_COUNT))
        else
            FAILED_COUNT=0
            PASSED_COUNT=$ACTUAL_TEST_COUNT
        fi
        echo "" >> tests/reports/test-summary.txt
    fi
    
    # Look for test statistics from run_all_tests.py
    if grep -q "Total test files:" tests/reports/test-output.log; then
        echo "Test Files Overview" >> tests/reports/test-summary.txt
        echo "-------------------" >> tests/reports/test-summary.txt
        grep -E "Total test files:|Unit tests:|Feature tests:|Integration tests:|Total lines of test code:" tests/reports/test-output.log >> tests/reports/test-summary.txt
        echo "" >> tests/reports/test-summary.txt
    fi
    
    # Extract unittest summary if available
    if grep -q "unittest Summary" tests/reports/test-output.log; then
        echo "Unittest Summary" >> tests/reports/test-summary.txt
        echo "----------------" >> tests/reports/test-summary.txt
        grep -A3 "unittest Summary" tests/reports/test-output.log | tail -3 >> tests/reports/test-summary.txt
        echo "" >> tests/reports/test-summary.txt
    fi
    
    # Use the actual counts from the test run
    if [ -n "$ACTUAL_TEST_COUNT" ]; then
        echo "Detailed Test Count" >> tests/reports/test-summary.txt
        echo "-------------------" >> tests/reports/test-summary.txt
        cat >> tests/reports/test-summary.txt << EOF
Total Tests Run: ${ACTUAL_TEST_COUNT:-0}
Passed: ${PASSED_COUNT:-0}
Failed: ${FAILED_COUNT:-0}
EOF
        echo "" >> tests/reports/test-summary.txt
    fi
fi

# Add coverage summary if available
if [ "$HAS_COVERAGE" = true ] && grep -q "TOTAL" tests/reports/test-output.log; then
    echo "Coverage Summary" >> tests/reports/test-summary.txt
    echo "----------------" >> tests/reports/test-summary.txt
    grep -A10 "Name.*Stmts.*Miss.*Cover" tests/reports/test-output.log | head -20 >> tests/reports/test-summary.txt || true
    echo "" >> tests/reports/test-summary.txt
fi

# Add execution time
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo "Execution Time: ${DURATION} seconds" >> tests/reports/test-summary.txt

# Add failed test details if any
if [ $TEST_EXIT_CODE -ne 0 ] && [ -f "tests/reports/test-output.log" ]; then
    echo "" >> tests/reports/test-summary.txt
    echo "Failed Tests" >> tests/reports/test-summary.txt
    echo "------------" >> tests/reports/test-summary.txt
    grep -B2 -A2 "FAILED\|ERROR" tests/reports/test-output.log | head -20 >> tests/reports/test-summary.txt || true
fi

print_success "Test summary generated at: tests/reports/test-summary.txt"

# If coverage module is available and we ran with coverage, generate HTML report
if [ "$HAS_COVERAGE" = true ] && grep -q "coverage report" tests/reports/test-output.log; then
    print_header "Generating HTML Coverage Report"
    
    print_status "Generating HTML coverage report..."
    python3 -m coverage html -d tests/reports/coverage-html 2>/dev/null || true
    
    if [ -d "tests/reports/coverage-html" ]; then
        print_success "HTML coverage report generated at: tests/reports/coverage-html/index.html"
    fi
fi

# Display summary
print_header "Test Execution Complete!"

echo "📊 Test Summary:"
echo "----------------"
if [ -f "tests/reports/test-summary.txt" ]; then
    cat tests/reports/test-summary.txt
fi

echo ""
echo "📁 Generated Reports:"
echo "--------------------"
find tests/reports -type f -name "*.txt" -o -name "*.log" | sort | while read -r file; do
    size=$(du -h "$file" | cut -f1)
    echo "- $file ($size)"
done

if [ -d "tests/reports/coverage-html" ]; then
    echo "- tests/reports/coverage-html/ (HTML coverage report)"
fi

echo ""
echo "🔗 Report Links:"
echo "----------------"
echo "- Test Summary: tests/reports/test-summary.txt"
echo "- Test Output: tests/reports/test-output.log"
if [ -d "tests/reports/coverage-html" ]; then
    echo "- HTML Coverage Report: tests/reports/coverage-html/index.html"
fi

# Exit with test exit code
exit $TEST_EXIT_CODE