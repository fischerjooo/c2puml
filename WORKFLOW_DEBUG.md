# GitHub Actions Workflow Debug Guide

## Issue: test-coverage.yml not uploading modified files

### Problem Analysis

The `test-coverage.yml` GitHub Actions workflow was not properly uploading modified files due to several issues:

1. **Conditional Logic Problems**: The workflow only committed and pushed files under very specific conditions that weren't being met reliably.

2. **Missing Manual Trigger Support**: The workflow had `workflow_dispatch` trigger but didn't handle manual triggers in the commit logic.

3. **Permission Issues**: The workflow might not have had the right permissions to push to the main branch when triggered from a PR context.

4. **Token Issues**: Using `github.token` which has limited permissions in PR contexts.

5. **Branch Switching Issues**: The workflow tried to switch branches with uncommitted changes, causing "local changes would be overwritten" errors.

6. **Non-Fast-Forward Push Errors**: The workflow failed to push to main when the main branch had been updated since the workflow started.

### Root Causes

1. **Complex Conditional Logic**: The original condition was:
   ```yaml
   if: (github.event_name == 'push' && github.ref == 'refs/heads/main') || (github.event_name == 'pull_request' && github.event.pull_request.merged == true && github.event.pull_request.base.ref == 'main')
   ```

2. **PR Context Issues**: When a PR is merged, the workflow runs in the PR context, but the `github.event.pull_request.merged` property might not be reliable.

3. **Branch Switching Problems**: The workflow tried to switch to main branch before committing changes, which failed when there were uncommitted files.

4. **Push Conflicts**: When pushing from a feature branch to main, the main branch might have been updated, causing non-fast-forward errors.

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

#### 3. Simplified Branch Handling
- **Fixed**: Commit changes first, then push to target branch
- **Removed**: Complex branch switching logic that caused conflicts
- **Added**: Smart push strategy that works from any branch context
- Uses `git push origin HEAD:main` when pushing to main from a different branch

#### 4. Enhanced Error Handling
- Added more detailed logging
- Better error messages
- Graceful handling of edge cases

#### 5. Non-Fast-Forward Push Handling
- **Added**: Fetch latest main branch before pushing
- **Added**: Fallback to create coverage branch if push fails
- **Added**: Timestamped branch names for coverage reports
- **Added**: Clear messaging about alternative approaches

### Key Changes

#### Before (Problematic):
```yaml
- name: 🚀 Commit and push coverage reports
  if: (github.event_name == 'push' && github.ref == 'refs/heads/main') || (github.event_name == 'pull_request' && github.event.pull_request.merged == true && github.event.pull_request.base.ref == 'main')
  run: |
    # Switch to main branch first (CAUSED ERROR)
    git checkout main
    # Add and commit files
    git add tests/reports/
    git commit -m "Update coverage"
    git push origin main
```

#### After (Fixed):
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
    
    if [ "$SHOULD_COMMIT" = "true" ]; then
      # Add and commit files first
      git add tests/reports/
      git commit -F /tmp/commit_msg
      
      # Push to target branch using smart strategy
      if [ "${{ github.ref }}" != "refs/heads/$TARGET_BRANCH" ]; then
        # Fetch latest main branch
        git fetch origin "$TARGET_BRANCH:$TARGET_BRANCH"
        
        # Try to push to main branch
        if git push origin "HEAD:$TARGET_BRANCH"; then
          echo "✅ Successfully pushed to $TARGET_BRANCH"
        else
          # Create coverage branch as fallback
          COVERAGE_BRANCH="coverage-reports-$(date +%Y%m%d-%H%M%S)"
          git push origin "HEAD:$COVERAGE_BRANCH"
        fi
      else
        git push origin "${{ github.ref }}"
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
5. **Handle branch contexts properly** without switching branches with uncommitted changes
6. **Handle push conflicts gracefully** by creating coverage branches when needed

### Troubleshooting

If the workflow still doesn't upload files:

1. **Check the debug output** in the workflow logs
2. **Verify the trigger conditions** are being met
3. **Check repository permissions** for the GitHub Actions bot
4. **Verify the PERSONAL_ACCESS_TOKEN** secret is configured (optional but recommended)
5. **Run the local debug script** to test logic
6. **Check for branch switching errors** - should no longer occur
7. **Check for push conflicts** - workflow will create coverage branches as fallback

### Files Modified

- `.github/workflows/test-coverage.yml` - Main workflow file (fixed branch switching and push conflicts)
- `test_workflow_debug.sh` - Local debug script (updated with push strategy)
- `WORKFLOW_DEBUG.md` - This documentation (updated with fix details)

### Next Steps

1. Test the workflow with a manual trigger
2. Monitor the next PR merge to ensure it works
3. Check the debug output to verify the logic is working correctly
4. Consider adding a Personal Access Token secret for more reliable authentication

### Recent Fixes (Latest Updates)

#### Fix 1: Branch Switching Error
**Issue**: Workflow failed with "Your local changes to the following files would be overwritten by checkout"

**Root Cause**: The workflow was trying to switch to the main branch before committing the generated coverage reports, causing a conflict.

**Solution**: 
1. Commit the generated files first
2. Use smart push strategy: `git push origin HEAD:main` when pushing to main from a different branch
3. Removed complex branch switching logic that caused conflicts

#### Fix 2: Non-Fast-Forward Push Error
**Issue**: Workflow failed with "Updates were rejected because a pushed branch tip is behind its remote counterpart"

**Root Cause**: The main branch was updated since the workflow started, causing a non-fast-forward error when trying to push.

**Solution**:
1. Fetch the latest main branch before pushing
2. Try to push to main branch first
3. If that fails, create a timestamped coverage branch as fallback
4. Provide clear messaging about the alternative approach

**Result**: The workflow now handles push conflicts gracefully and ensures coverage reports are always saved.