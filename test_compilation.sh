#!/bin/bash

# Test compilation of all .c files in the project
echo "Testing compilation of all .c files..."
echo "======================================"

# Get all .c files
C_FILES=$(find . -name "*.c" | grep -v ".git" | sort)

# Counters
TOTAL_FILES=0
SUCCESS_COUNT=0
FAIL_COUNT=0
FAILED_FILES=""

# Test each .c file
for file in $C_FILES; do
    TOTAL_FILES=$((TOTAL_FILES + 1))
    echo -n "Testing $file... "
    
    # Try to compile the file
    if gcc -c "$file" -o "${file%.c}.o" 2>/dev/null; then
        echo "✓ SUCCESS"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        # Clean up object file
        rm -f "${file%.c}.o"
    else
        echo "✗ FAILED"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        FAILED_FILES="$FAILED_FILES $file"
    fi
done

echo ""
echo "======================================"
echo "COMPILATION TEST RESULTS:"
echo "Total .c files tested: $TOTAL_FILES"
echo "Successful compilations: $SUCCESS_COUNT"
echo "Failed compilations: $FAIL_COUNT"

if [ $FAIL_COUNT -gt 0 ]; then
    echo ""
    echo "Failed files:"
    for file in $FAILED_FILES; do
        echo "  - $file"
    done
    echo ""
    echo "Testing failed files with verbose output:"
    for file in $FAILED_FILES; do
        echo "=== $file ==="
        gcc -c "$file" -o "${file%.c}.o"
        echo ""
    done
else
    echo ""
    echo "🎉 All .c files compile successfully!"
fi