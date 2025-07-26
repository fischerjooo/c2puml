#!/usr/bin/env bash

# test_workflow_debug.sh - Debug script to test workflow logic locally
# This script simulates the workflow conditions and file generation

set -e

echo "🔍 Testing workflow logic and file generation..."

# Simulate workflow environment variables
export GITHUB_EVENT_NAME="workflow_dispatch"
export GITHUB_REF="refs/heads/main"
export GITHUB_SHA="test-sha-123"
export GITHUB_WORKFLOW="Test Suite with Coverage Reports"
export GITHUB_RUN_NUMBER="1"
export GITHUB_REPOSITORY="test/repo"

echo "📋 Workflow Context:"
echo "- Event name: $GITHUB_EVENT_NAME"
echo "- Ref: $GITHUB_REF"
echo "- SHA: $GITHUB_SHA"
echo "- Workflow: $GITHUB_WORKFLOW"
echo "- Run number: $GITHUB_RUN_NUMBER"

# Test the conditional logic
echo ""
echo "🔍 Testing conditional logic..."

SHOULD_COMMIT=false

if [ "$GITHUB_EVENT_NAME" = "workflow_dispatch" ]; then
    echo "✅ Manual trigger detected - will commit and push"
    SHOULD_COMMIT=true
    TARGET_BRANCH="main"
elif [ "$GITHUB_EVENT_NAME" = "push" ] && [ "$GITHUB_REF" = "refs/heads/main" ]; then
    echo "✅ Direct push to main detected - will commit and push"
    SHOULD_COMMIT=true
    TARGET_BRANCH="main"
elif [ "$GITHUB_EVENT_NAME" = "pull_request" ]; then
    if [ "$GITHUB_EVENT_PULL_REQUEST_MERGED" = "true" ] && [ "$GITHUB_EVENT_PULL_REQUEST_BASE_REF" = "main" ]; then
        echo "✅ Merged PR to main detected - will commit and push"
        SHOULD_COMMIT=true
        TARGET_BRANCH="main"
    else
        echo "ℹ️ PR not merged or not to main - skipping commit and push"
    fi
else
    echo "ℹ️ Event not eligible for commit and push - skipping"
fi

echo "Should commit: $SHOULD_COMMIT"
echo "Target branch: $TARGET_BRANCH"

# Test file generation
echo ""
echo "🧪 Testing file generation..."

# Create test reports directory
mkdir -p tests/reports/coverage

# Generate a test file
cat > tests/reports/test-debug.txt << EOF
Test Debug Report
================
Generated: $(date)
Workflow: $GITHUB_WORKFLOW
Run: $GITHUB_RUN_NUMBER
Event: $GITHUB_EVENT_NAME
EOF

# Generate a test coverage file
cat > tests/reports/coverage/debug-coverage.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Debug Coverage Report</title>
</head>
<body>
    <h1>Debug Coverage Report</h1>
    <p>Generated: $(date)</p>
    <p>This is a test coverage report for debugging the workflow.</p>
</body>
</html>
EOF

echo "✅ Test files generated:"
find tests/reports -type f -name "*" | sort

# Test git operations (dry run)
echo ""
echo "🔍 Testing git operations (dry run)..."

if [ "$SHOULD_COMMIT" = "true" ]; then
    echo "📁 Files that would be added:"
    git status --porcelain tests/reports/ || echo "No git repository or no changes"
    
    echo ""
    echo "📝 Files that would be committed:"
    find tests/reports -type f -name "*" | sort | sed 's/^/- /'
    
    echo ""
    echo "🔄 Push strategy:"
    if [ "$GITHUB_REF" != "refs/heads/$TARGET_BRANCH" ]; then
        echo "Would push to $TARGET_BRANCH branch using: git push origin HEAD:$TARGET_BRANCH"
        echo "If that fails, would create coverage branch: coverage-reports-$(date +%Y%m%d-%H%M%S)"
    else
        echo "Would push to current branch using: git push origin $GITHUB_REF"
    fi
else
    echo "ℹ️ Would skip commit based on conditions"
fi

echo ""
echo "✅ Debug test completed!"