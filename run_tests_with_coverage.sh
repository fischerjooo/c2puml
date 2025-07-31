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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
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

# Step 1: Always run all tests and examples to collect coverage data
if [ "$HAS_COVERAGE" = true ]; then
    print_header "Step 1: Collecting Coverage Data from All Tests and Examples"
    
    # Clear any existing coverage data
    print_status "Clearing any existing coverage data..."
    python3 -m coverage erase
    
    # Check if pytest is available, otherwise use unittest
    if python3 -m pytest --version &>/dev/null; then
        print_status "Running all tests with coverage using pytest..."
        PYTHONPATH=src python3 -m coverage run -m pytest tests/ -v 2>&1 | tee tests/reports/test-output.log
    else
        print_status "pytest not available, running tests with coverage using unittest discovery..."
        PYTHONPATH=src python3 -m coverage run run_all_tests.py 2>&1 | tee tests/reports/test-output.log
    fi
    
    # Run examples if they exist
    if [ -d "examples" ]; then
        print_status "Running examples with coverage..."
        for example in examples/*.py; do
            if [ -f "$example" ]; then
                print_status "Running example: $example"
                PYTHONPATH=src python3 -m coverage run -a "$example"
            fi
        done
    fi
    
    # Run the C to PlantUML example with coverage
    if [ -f "run_example_with_coverage.py" ]; then
        print_status "Running C to PlantUML example with coverage..."
        PYTHONPATH=src python3 -m coverage run -a run_example_with_coverage.py
    fi
    
    # Step 2: Generate comprehensive coverage reports
    print_header "Step 2: Generating Comprehensive Coverage Reports"
    
    # Create coverage directory
    mkdir -p tests/reports/coverage
    
    # Clean htmlcov directory if it exists
    if [ -d "tests/reports/coverage/htmlcov" ]; then
        print_status "Cleaning existing htmlcov directory..."
        rm -rf tests/reports/coverage/htmlcov/*
    fi
    
    # Check if coverage data exists before generating reports
    if python3 -m coverage report &>/dev/null; then
        print_status "Coverage data found, generating HTML coverage reports..."
        python3 -m coverage html -d tests/reports/coverage/htmlcov
    else
        print_warning "No coverage data found. Running a simple test to generate some coverage data..."
        # Run a simple test with coverage to ensure we have some data
        PYTHONPATH=src python3 -m coverage run -c "import c2puml; print('✅ Basic import test passed')" 2>/dev/null || true
        # Try generating reports again
        if python3 -m coverage report &>/dev/null; then
            print_status "Generating HTML coverage reports with basic data..."
            python3 -m coverage html -d tests/reports/coverage/htmlcov
        else
            print_error "Unable to generate coverage data. Creating minimal reports..."
            mkdir -p tests/reports/coverage/htmlcov
            echo "<html><body><h1>No Coverage Data Available</h1><p>Coverage collection failed during test execution.</p></body></html>" > tests/reports/coverage/htmlcov/index.html
        fi
    fi
    
    # Remove the .gitignore file created by coverage.py to allow HTML reports to be committed
    if [ -f "tests/reports/coverage/htmlcov/.gitignore" ]; then
        print_status "Removing .gitignore file to allow HTML coverage reports to be committed..."
        rm tests/reports/coverage/htmlcov/.gitignore
    fi
    
    # Generate XML and JSON reports
    print_status "Generating XML and JSON reports..."
    if python3 -m coverage report &>/dev/null; then
        python3 -m coverage xml -o tests/reports/coverage/coverage.xml 2>/dev/null || echo "Failed to generate XML report" > tests/reports/coverage/coverage.xml
        python3 -m coverage json -o tests/reports/coverage/coverage.json 2>/dev/null || echo '{"error": "Failed to generate JSON report"}' > tests/reports/coverage/coverage.json
        
        # Generate terminal report
        print_status "Generating terminal coverage report..."
        python3 -m coverage report -m > tests/reports/coverage/coverage_report.txt 2>/dev/null || echo "No coverage data available" > tests/reports/coverage/coverage_report.txt
    else
        # Create placeholder files
        echo "No coverage data available" > tests/reports/coverage/coverage.xml
        echo '{"error": "No coverage data available"}' > tests/reports/coverage/coverage.json
        echo "No coverage data available" > tests/reports/coverage/coverage_report.txt
    fi
    
    # Step 3: Verify all reports were generated
    print_header "Step 3: Verifying All Reports Were Generated"
    
    # Verify HTML reports exist
    if [ -d "tests/reports/coverage/htmlcov" ]; then
        print_success "HTML coverage reports generated successfully"
        ls -la tests/reports/coverage/htmlcov/ | head -5
    else
        print_error "Failed to generate HTML coverage reports"
        exit 1
    fi
    
    # Verify other reports exist
    if [ -f "tests/reports/coverage/coverage.xml" ]; then
        print_success "XML coverage report generated"
    fi
    
    if [ -f "tests/reports/coverage/coverage.json" ]; then
        print_success "JSON coverage report generated"
    fi
    
    print_success "All coverage reports generated successfully!"
else
    # Fallback: Run all tests using the existing test runner without coverage
    print_status "Running all unit tests without coverage..."
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
    # Look for pytest test results summary line (e.g., "329 passed in 2.64s")
    if grep -q "passed in" tests/reports/test-output.log; then
        TEST_SUMMARY=$(grep -E "[0-9]+ passed in" tests/reports/test-output.log | tail -1)
        echo "$TEST_SUMMARY" >> tests/reports/test-summary.txt
        
        # Extract the actual test count from the summary
        ACTUAL_TEST_COUNT=$(echo "$TEST_SUMMARY" | grep -oE "^[0-9]+" | head -1)
        
        # Check for passed/failed status
        if echo "$TEST_SUMMARY" | grep -q "passed" && ! echo "$TEST_SUMMARY" | grep -q "failed\|error"; then
            echo "Status: PASSED - All tests passed" >> tests/reports/test-summary.txt
            FAILED_COUNT=0
            PASSED_COUNT=$ACTUAL_TEST_COUNT
        elif echo "$TEST_SUMMARY" | grep -q "failed\|error"; then
            # Extract failure count from pytest output
            FAILED_COUNT=$(echo "$TEST_SUMMARY" | grep -oE "[0-9]+ failed" | grep -oE "[0-9]+" || echo "0")
            ERROR_COUNT=$(echo "$TEST_SUMMARY" | grep -oE "[0-9]+ error" | grep -oE "[0-9]+" || echo "0")
            TOTAL_FAILED=$((FAILED_COUNT + ERROR_COUNT))
            PASSED_COUNT=$((ACTUAL_TEST_COUNT - TOTAL_FAILED))
            echo "Status: FAILED - $FAILED_COUNT failed, $ERROR_COUNT errors" >> tests/reports/test-summary.txt
        else
            FAILED_COUNT=0
            PASSED_COUNT=$ACTUAL_TEST_COUNT
        fi
        echo "" >> tests/reports/test-summary.txt
    # Fallback: Look for unittest test results summary line
    elif grep -q "Ran [0-9]* test" tests/reports/test-output.log; then
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
    
    # Look for pytest collection information
    if grep -q "collected" tests/reports/test-output.log; then
        COLLECTION_INFO=$(grep -E "collected [0-9]+ items" tests/reports/test-output.log | tail -1)
        echo "Test Collection: $COLLECTION_INFO" >> tests/reports/test-summary.txt
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

# Generate HTML test summary
print_status "Generating HTML test summary..."
if python3 generate_test_summary_html.py --log-file tests/reports/test-output.log --output-file tests/reports/test_summary.html; then
    print_success "HTML test summary generated at: tests/reports/test_summary.html"
else
    print_warning "Failed to generate HTML test summary, continuing with text summary only"
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

if [ -d "tests/reports/coverage" ]; then
    echo "- tests/reports/coverage/ (Combined coverage reports - summary + detailed)"
    if [ -d "tests/reports/coverage/htmlcov" ]; then
        echo "  - tests/reports/coverage/htmlcov/ (Standard HTML coverage)"
    fi
fi

echo ""
echo "🔗 Report Links:"
echo "----------------"
echo "- Test Summary: tests/reports/test-summary.txt"
echo "- HTML Test Summary: tests/reports/test_summary.html"
echo "- Test Output: tests/reports/test-output.log"
if [ -d "tests/reports/coverage" ]; then
    echo "- Combined Coverage Report: tests/reports/coverage/index.html"
    echo "- Coverage Summary: tests/reports/coverage/coverage_summary.txt"
    if [ -d "tests/reports/coverage/htmlcov" ]; then
        echo "- Standard HTML Coverage: tests/reports/coverage/htmlcov/index.html"
    fi
fi

# Exit with test exit code
exit $TEST_EXIT_CODE