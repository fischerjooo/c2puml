# Fix for Duplicate puml2png Workflow Execution

## Problem Description

The `puml2png.yml` workflow was being executed **twice** when a pull request was merged due to conflicting trigger mechanisms:

1. **Direct push trigger**: The workflow had a `push` trigger that activated when PlantUML files were pushed to main/master branches
2. **Workflow call from test-coverage**: The `test-coverage.yml` workflow (triggered on PR merge) explicitly called `puml2png.yml` via `workflow_dispatch`

## Root Cause

When a PR was merged:
1. The merge created a push to the main branch
2. If PlantUML files were changed, this triggered `puml2png.yml` via the `push` trigger
3. Simultaneously, `test-coverage.yml` ran (triggered by PR merge) and called `puml2png.yml` again via `workflow_dispatch`

This resulted in duplicate workflow executions, wasting resources and potentially causing conflicts.

## Solution Implemented

### 1. Removed Redundant Push Trigger

**File**: `.github/workflows/puml2png.yml`

**Change**: Removed the `push` trigger section:
```yaml
# REMOVED:
push:
  paths:
    - 'output/**/*.puml'
    - 'picgen.sh'
    - '.github/workflows/puml2png.yml'
  branches: [ main, master ]
```

**Reasoning**: The `test-coverage.yml` workflow already handles triggering `puml2png.yml` when needed after PR merges, making the push trigger redundant.

### 2. Added Concurrency Control

**File**: `.github/workflows/puml2png.yml`

**Change**: Added concurrency group to prevent multiple simultaneous executions:
```yaml
jobs:
  convert-puml:
    runs-on: ubuntu-latest
    concurrency:
      group: "puml2png-conversion"
      cancel-in-progress: true
```

**Benefit**: If somehow multiple instances are triggered, only one will run at a time, with others being cancelled.

### 3. Enhanced Documentation

**File**: `.github/workflows/puml2png.yml`

**Change**: Added clear documentation explaining the trigger mechanisms:
```yaml
# NOTE: This workflow is triggered by:
# 1. Manual workflow_dispatch (for manual runs)
# 2. workflow_call from test-coverage.yml (for automated runs after PR merge)
#
# The push trigger was removed to prevent duplicate execution when PRs are merged,
# as the test-coverage workflow already handles triggering this workflow when needed.
```

## Current Trigger Flow

After the fix, the workflow execution follows this pattern:

1. **PR is merged** → Triggers `test-coverage.yml`
2. **test-coverage.yml completes successfully** → Calls `puml2png.yml` via `workflow_dispatch`
3. **puml2png.yml executes once** → Converts PlantUML files to PNG

## Manual Execution

The workflow can still be triggered manually via:
- GitHub Actions UI (workflow_dispatch)
- API calls to workflow_dispatch endpoint

## Benefits of the Fix

1. **Eliminates duplicate executions** - Only one instance runs per PR merge
2. **Reduces resource usage** - No wasted CI/CD minutes
3. **Prevents potential conflicts** - No race conditions between multiple instances
4. **Maintains functionality** - All existing use cases are preserved
5. **Improves reliability** - Concurrency control prevents overlapping executions

## Testing the Fix

To verify the fix works correctly:

1. Create a PR with PlantUML file changes
2. Merge the PR
3. Check GitHub Actions - only one `puml2png.yml` execution should occur
4. Verify that PNG files are generated correctly

## Rollback Plan

If issues arise, the push trigger can be restored by adding back the removed section:

```yaml
push:
  paths:
    - 'output/**/*.puml'
    - 'picgen.sh'
    - '.github/workflows/puml2png.yml'
  branches: [ main, master ]
```

However, this would reintroduce the duplicate execution issue.