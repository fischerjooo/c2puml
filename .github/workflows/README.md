# GitHub Workflows Documentation

## Overview

This repository uses a streamlined, numbered workflow system that follows a clear execution hierarchy. The workflows are designed to be simple, reliable, and easy to understand.

## Workflow Hierarchy

### 01. Test and Validate (`01-test-and-validate.yml`)
**Purpose**: Comprehensive testing and validation of the codebase
**Triggers**: 
- Push to main/master branches
- Pull requests to main/master branches
- Manual dispatch

**Steps**:
1. **01.01-01.04**: Setup environment and dependencies
2. **01.05**: Verify package installation
3. **01.06-01.08**: Run different test suites (unit, integration, feature)
4. **01.09**: Run example workflow
5. **01.10**: Generate coverage reports (main branch only)
6. **01.11**: Upload test artifacts
7. **01.12**: Trigger PlantUML generation (main branch only)

**Outputs**: Test results, coverage reports, artifacts

### 02. Generate PlantUML Diagrams (`02-generate-plantuml.yml`)
**Purpose**: Convert PlantUML files to PNG images and create diagram index
**Triggers**:
- Called by workflow 01 (main branch only)
- Manual dispatch
- Push to PlantUML files on main/master

**Steps**:
1. **02.01-02.02**: Setup environment and Git configuration
2. **02.03-02.04**: Install system dependencies and PlantUML
3. **02.05**: Generate PNG images from PlantUML files
4. **02.06**: Commit generated images to repository (main branch only)
5. **02.07**: Upload generated images as artifacts
6. **02.08**: Trigger website deployment (main branch only)

**Outputs**: PNG images, diagram index HTML, artifacts

### 03. Deploy Website (`03-deploy-website.yml`)
**Purpose**: Deploy website to GitHub Pages with all generated content
**Triggers**:
- Called by workflow 02 (main branch only)
- Manual dispatch

**Steps**:
1. **03.01**: Checkout repository
2. **03.02**: Prepare website files (copy reports, images, documentation)
3. **03.03**: Create website index HTML
4. **03.04**: Upload website files as Pages artifact
5. **03.05**: Deploy to GitHub Pages
6. **03.06**: Generate deployment summary

**Outputs**: Deployed website at `https://{owner}.github.io/{repo}`

## Execution Flow

```
PR/Commit → 01. Test and Validate
    ↓ (if main branch)
    02. Generate PlantUML Diagrams
    ↓ (if main branch)
    03. Deploy Website
```

## Key Improvements Over Previous Setup

### ✅ **Simplified Structure**
- **Clear numbering**: 01, 02, 03 makes hierarchy obvious
- **Single responsibility**: Each workflow has one clear purpose
- **Reduced complexity**: Removed unnecessary duplicate prevention logic

### ✅ **Better Naming**
- **Descriptive names**: Each workflow name clearly indicates its purpose
- **Numbered steps**: Each step has a clear number for easy reference
- **Consistent formatting**: All workflows follow the same naming pattern

### ✅ **Eliminated Redundancy**
- **No duplicate tests**: Tests run once in workflow 01
- **No complex waiting**: Removed unnecessary workflow waiting logic
- **Streamlined triggers**: Clear trigger chain without loops

### ✅ **Improved Reliability**
- **Simplified Git operations**: Reduced complex conflict resolution
- **Clear dependencies**: Each workflow clearly shows what it depends on
- **Better error handling**: Simpler, more predictable error scenarios

### ✅ **Enhanced Maintainability**
- **Modular design**: Each workflow can be modified independently
- **Clear documentation**: This README explains the entire system
- **Consistent patterns**: All workflows follow the same structure

## Manual Workflow Execution

### Run All Workflows
```bash
# Trigger the entire pipeline
gh workflow run "01-test-and-validate.yml"
```

### Run Individual Workflows
```bash
# Run only tests
gh workflow run "01-test-and-validate.yml"

# Generate only PlantUML diagrams
gh workflow run "02-generate-plantuml.yml"

# Deploy only website
gh workflow run "03-deploy-website.yml"
```

## Configuration

### Required Secrets
- `PERSONAL_ACCESS_TOKEN`: For repository write access (optional, falls back to `github.token`)

### Branch Protection
- Workflows run on `main` and `master` branches
- PR workflows run on all PRs to main/master
- Only main/master branch triggers subsequent workflows

## Troubleshooting

### Common Issues

1. **Workflow not triggering**: Check branch name and trigger conditions
2. **Git push failures**: Ensure `PERSONAL_ACCESS_TOKEN` is configured
3. **PlantUML generation fails**: Check if PlantUML files exist in expected locations
4. **Website deployment fails**: Verify GitHub Pages is enabled for the repository

### Debug Steps

1. Check workflow logs for specific error messages
2. Verify file paths and permissions
3. Ensure all required dependencies are available
4. Check GitHub Actions permissions for the repository

## Migration from Old Workflows

The old workflows (`test.yml`, `test-coverage.yml`, `puml2png.yml`, `deploy-website.yml`) should be disabled or removed after confirming the new workflows work correctly.

### Migration Checklist
- [ ] Test new workflow 01 with a PR
- [ ] Verify workflow 02 triggers correctly
- [ ] Confirm workflow 03 deploys successfully
- [ ] Disable old workflows
- [ ] Update any external references to old workflow names