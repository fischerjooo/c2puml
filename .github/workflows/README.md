# GitHub Workflows Documentation

## Overview

This repository uses a streamlined, numbered workflow system that follows a clear execution hierarchy. The workflows are designed to be simple, reliable, and easy to understand, with different workflows for side branches vs main branch.

## Workflow Hierarchy

### 00. Test (`00-test.yml`)
**Purpose**: Basic testing for pull requests
**Triggers**: 
- Pull requests to main/master branches

**Steps**:
1. **00.01-00.04**: Setup environment and dependencies
2. **00.05**: Verify package installation
3. **00.06-00.08**: Run different test suites (unit, integration, feature)
4. **00.09**: Run example workflow
5. **00.10**: Upload test artifacts (7-day retention)

**Outputs**: Test results, artifacts (no coverage, no subsequent workflows)

### 01. Test and Coverage (`01-test-and-coverage.yml`)
**Purpose**: Comprehensive testing and coverage for main branch
**Triggers**: 
- Push to main/master branches (excluding generated files)
- Manual dispatch

**Steps**:
1. **01.01-01.04**: Setup environment and dependencies
2. **01.05**: Verify package installation
3. **01.06-01.08**: Run different test suites (unit, integration, feature)
4. **01.09**: Run example workflow
5. **01.10**: Generate coverage reports
6. **01.11**: Upload test artifacts (30-day retention)
7. **01.12**: Trigger PlantUML generation

**Outputs**: Test results, coverage reports, artifacts, triggers PlantUML generation

### 02. PlantUML to PNG (`02-puml-to-png.yml`)
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

### Pull Requests
```
Pull Request → 00. Test
    ↓ (stops here - no further workflows)
```

### Main Branch
```
Main Branch Push (source code) → 01. Test and Coverage
    ↓ (if successful)
    02. PlantUML to PNG
    ↓ (commits generated files to main)
    03. Deploy Website
    ↓ (no loop - workflow 01 ignores generated files)
```

## Key Improvements Over Previous Setup

### ✅ **Optimized for Different Branch Types**
- **Pull requests**: Lightweight testing only (workflow 00)
- **Main branch**: Full pipeline with coverage and deployment (workflows 01-03)
- **Clear separation**: Different workflows for different purposes

### ✅ **Clear Naming Convention**
- **Workflows**: `00-test.yml`, `01-test-and-coverage.yml`, `02-puml-to-png.yml`, `03-deploy-website.yml`
- **Steps**: `00.01`, `00.02`, `01.01`, `01.02`, etc.
- **Consistent patterns**: All workflows follow the same structure

### ✅ **Eliminated Redundancy**
- **Pull requests**: No unnecessary coverage or deployment
- **Main branch**: Full pipeline only when needed
- **Streamlined triggers**: Clear, linear trigger chain
- **No infinite loops**: Path filtering prevents workflow loops

### ✅ **Improved Reliability**
- **Simplified Git operations**: Basic pull/push with fallback
- **Clear dependencies**: Each workflow shows what it depends on
- **Better error handling**: Predictable failure scenarios

### ✅ **Enhanced Maintainability**
- **Modular design**: Each workflow is independent
- **Clear documentation**: This README explains the entire system
- **Consistent patterns**: All workflows follow the same structure

## Manual Workflow Execution

### Run All Workflows (Main Branch)
```bash
# Trigger the entire pipeline
gh workflow run "01-test-and-coverage.yml"
```

### Run Individual Workflows
```bash
# Run only tests
gh workflow run "00-test.yml"

# Run tests with coverage
gh workflow run "01-test-and-coverage.yml"

# Generate only PlantUML diagrams
gh workflow run "02-puml-to-png.yml"

# Deploy only website
gh workflow run "03-deploy-website.yml"
```

## Configuration

### Required Secrets
- `PERSONAL_ACCESS_TOKEN`: For repository write access (optional, falls back to `github.token`)

### Branch Protection
- **Pull requests**: Only workflow 00 runs
- **Main branch**: Full pipeline (workflows 01-03)
- **PR workflows**: Only workflow 00 runs
- **Main branch triggers**: All subsequent workflows

### Path Filtering
- **Workflow 01**: Ignores generated files (PNG, HTML, test reports, coverage) to prevent infinite loops
- **Workflow 02**: Only triggers on PlantUML file changes or manual dispatch
- **Workflow 03**: Only triggers on workflow completion or manual dispatch

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

The old workflows have been replaced with the new numbered system. The new structure provides better separation between side branch and main branch workflows.

### Migration Checklist
- [ ] Test new workflow 00 with a pull request
- [ ] Test new workflow 01 with main branch
- [ ] Verify workflow 02 triggers correctly
- [ ] Confirm workflow 03 deploys successfully
- [ ] Update any external references to old workflow names

## Branch Strategy

### Pull Requests
- **Purpose**: Code review and validation
- **Workflow**: 00-test.yml only
- **Benefits**: Fast feedback, no unnecessary overhead
- **Retention**: 7-day artifact retention

### Main Branch
- **Purpose**: Production-ready code
- **Workflow**: Full pipeline (01-03)
- **Benefits**: Comprehensive testing, coverage, deployment
- **Retention**: 30-day artifact retention