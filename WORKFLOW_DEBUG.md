# GitHub Actions Workflow Debug Guide

## Issue: test-coverage.yml not uploading modified files

### Problem Analysis

The `test-coverage.yml` GitHub Actions workflow was not properly uploading modified files due to several issues:

1. **Conditional Logic Problems**: The workflow only committed and pushed files under very specific conditions that weren't being met reliably.

2. **Missing Manual Trigger Support**: The workflow had `workflow_dispatch` trigger but didn't handle manual triggers in the commit logic.

3. **Permission Issues**: The workflow might not have had the right permissions to push to the main branch when triggered from a PR context.

4. **Token Issues**: Using `github.token` which has limited permissions in PR contexts.

### Root Causes

1. **Complex Conditional Logic**: The original condition was:
   ```yaml
   if: (github.event_name == 'push' && github.ref == 'refs/heads/main') || (github.event_name == 'pull_request' && github.event.pull_request.merged == true && github.event.pull_request.base.ref == 'main')
   ```

2. **PR Context Issues**: When a PR is merged, the workflow runs in the PR context, but the `github.event.pull_request.merged` property might not be reliable.

3. **Branch Switching**: The workflow didn't properly handle switching to the main branch when running from a PR context.

### Solutions Implemented

#### 1. Enhanced Debugging
- Added a debug step that logs all workflow context variables
- Added debug information to the workflow summary
- Created a local debug script (`test_workflow_debug.sh`) to test logic locally

#### 2. Improved Conditional Logic
- Replaced complex YAML conditions with bash script logic
- Added support for manual triggers (`workflow_dispatch`)
- Better handling of different event types
- More explicit logging of decision points

#### 3. Better Branch Handling
- Added explicit branch switching logic
- Ensures we're on the main branch before committing
- Uses `git fetch` and `git checkout` to switch branches safely

#### 4. Enhanced Error Handling
- Added more detailed logging
- Better error messages
- Graceful handling of edge cases

### Key Changes

#### Before:
```yaml
- name: 🚀 Commit and push coverage reports
  if: (github.event_name == 'push' && github.ref == 'refs/heads/main') || (github.event_name == 'pull_request' && github.event.pull_request.merged == true && github.event.pull_request.base.ref == 'main')
```

#### After:
```yaml
- name: 🚀 Commit and push coverage reports
  if: always()
  run: |
    # Determine if we should commit and push
    SHOULD_COMMIT=false
    
    if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
      echo "✅ Manual trigger detected - will commit and push"
      SHOULD_COMMIT=true
      TARGET_BRANCH="main"
    elif [ "${{ github.event_name }}" = "push" ] && [ "${{ github.ref }}" = "refs/heads/main" ]; then
      echo "✅ Direct push to main detected - will commit and push"
      SHOULD_COMMIT=true
      TARGET_BRANCH="main"
    elif [ "${{ github.event_name }}" = "pull_request" ]; then
      if [ "${{ github.event.pull_request.merged }}" = "true" ] && [ "${{ github.event.pull_request.base.ref }}" = "main" ]; then
        echo "✅ Merged PR to main detected - will commit and push"
        SHOULD_COMMIT=true
        TARGET_BRANCH="main"
      else
        echo "ℹ️ PR not merged or not to main - skipping commit and push"
      fi
    fi
```

### Testing

#### Local Testing
Run the debug script to test the logic locally:
```bash
./test_workflow_debug.sh
```

#### Manual Workflow Trigger
1. Go to the GitHub repository
2. Navigate to Actions → Test Suite with Coverage Reports
3. Click "Run workflow" to trigger manually
4. Check the logs for debug information

### Expected Behavior

The workflow should now:

1. **Always run the tests and generate reports** regardless of trigger type
2. **Commit and push files when**:
   - Manually triggered (`workflow_dispatch`)
   - Direct push to main branch
   - Merged PR to main branch
3. **Skip commit and push when**:
   - PR is not merged
   - PR is not targeting main branch
   - Other event types
4. **Provide detailed logging** about why decisions were made

### Troubleshooting

If the workflow still doesn't upload files:

1. **Check the debug output** in the workflow logs
2. **Verify the trigger conditions** are being met
3. **Check repository permissions** for the GitHub Actions bot
4. **Verify the PERSONAL_ACCESS_TOKEN** secret is configured (optional but recommended)
5. **Run the local debug script** to test logic

### Files Modified

- `.github/workflows/test-coverage.yml` - Main workflow file
- `test_workflow_debug.sh` - Local debug script
- `WORKFLOW_DEBUG.md` - This documentation

### Next Steps

1. Test the workflow with a manual trigger
2. Monitor the next PR merge to ensure it works
3. Check the debug output to verify the logic is working correctly
4. Consider adding a Personal Access Token secret for more reliable authentication