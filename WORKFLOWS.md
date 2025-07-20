# GitHub Actions Workflows

This document explains the GitHub Actions workflow structure for the C to PlantUML converter project.

## Workflow Overview

The project uses a **sequenced workflow approach** where linting and formatting run first, followed by testing on the updated code. This ensures that tests always run on properly formatted code.

## Workflow Files

### 1. `main.yml` - Main Orchestration Workflow
**Purpose**: Orchestrates the complete CI/CD pipeline with proper sequencing.

**Triggers**:
- Push to `main`/`master` branches
- Pull requests to `main`/`master` branches
- Manual dispatch

**Sequence**:
1. **Step 1**: Lint and Format (`lint-and-format.yml`)
2. **Step 2**: Test (runs on updated code after formatting)

**Key Features**:
- ✅ **Proper sequencing**: Tests run after formatting
- ✅ **Auto-commit**: Automatically commits formatting changes on pushes
- ✅ **PR feedback**: Comments on PRs when formatting issues are detected
- ✅ **Artifact sharing**: Formatted files are available to test job

### 2. `lint-and-format.yml` - Linting and Formatting Workflow
**Purpose**: Handles code linting and automatic formatting.

**Features**:
- **Comprehensive linting**: flake8 with all relevant checks
- **Code formatting**: black for consistent code style
- **Import sorting**: isort for organized imports
- **Auto-commit**: Automatically commits changes (except on PRs)
- **PR feedback**: Comments on PRs when formatting is needed

**Auto-commit Behavior**:
- **Push to main/master**: ✅ Auto-commits formatting changes
- **Pull requests**: ❌ No auto-commit, but comments on PR

### 3. `lint-check.yml` - Lint Check Only (PR-focused)
**Purpose**: Lightweight linting check for pull requests without auto-commit.

**Triggers**:
- Pull requests to `main`/`master` branches
- Manual dispatch

**Features**:
- ✅ **Fast feedback**: Quick linting checks for PRs
- ✅ **No auto-commit**: Safe for PR reviews
- ✅ **Comprehensive checks**: Same linting standards as main workflow

### 4. `test.yml` - Standalone Testing Workflow
**Purpose**: Independent testing workflow for manual execution.

**Triggers**:
- Manual dispatch only

**Features**:
- ✅ **Complete testing**: All test scenarios
- ✅ **Manual control**: Can be run independently
- ✅ **Artifact generation**: Test outputs are preserved

## Workflow Sequence Diagram

```
Push/PR → main.yml
    ↓
┌─────────────────┐
│ lint-and-format │ ← Step 1: Format code
│     (Job 1)     │
└─────────────────┘
    ↓ (if changes made)
┌─────────────────┐
│ Auto-commit     │ ← Commit formatting changes
│   (if push)     │
└─────────────────┘
    ↓
┌─────────────────┐
│     test        │ ← Step 2: Test formatted code
│   (Job 2)       │
└─────────────────┘
```

## Key Benefits

### 1. **Proper Sequencing**
- Tests always run on properly formatted code
- No false failures due to formatting issues
- Consistent code quality across all test runs

### 2. **Auto-commit Safety**
- **Main branch**: Auto-commits formatting changes
- **Pull requests**: No auto-commit, but provides feedback
- **Manual control**: Standalone workflows available

### 3. **Comprehensive Coverage**
- **Linting**: flake8 with comprehensive rule set
- **Formatting**: black for consistent style
- **Import sorting**: isort for organized imports
- **Testing**: Complete test suite on formatted code

### 4. **Developer Experience**
- **Fast feedback**: Quick linting checks on PRs
- **Clear guidance**: Helpful comments when formatting is needed
- **Local tools**: Scripts for local development

## Usage Scenarios

### For Developers

#### 1. **Making Changes**
```bash
# Local development
python scripts/format.py  # Format code
python scripts/lint.py    # Check formatting
git push                  # Triggers main workflow
```

#### 2. **Pull Request Workflow**
1. Create PR → `lint-check.yml` runs automatically
2. If formatting issues detected → PR gets helpful comment
3. Fix formatting locally → Push updates
4. `main.yml` runs → Tests on formatted code

#### 3. **Manual Testing**
- Use GitHub Actions UI to run `test.yml` manually
- Useful for testing specific scenarios

### For Maintainers

#### 1. **Main Branch Protection**
- `main.yml` ensures all code is properly formatted
- Tests run on formatted code only
- Auto-commit maintains code quality

#### 2. **Release Process**
- All code is automatically formatted
- Tests pass on formatted code
- Consistent code quality across releases

## Configuration Files

### Linting Configuration
- **`.flake8`**: flake8 configuration with Black-compatible settings
- **`pyproject.toml`**: Configuration for black and isort
- **`.pre-commit-config.yaml`**: Pre-commit hooks for local development

### Workflow Configuration
- **Matrix testing**: Python 3.9
- **Artifact sharing**: Formatted files shared between jobs
- **Conditional execution**: Smart handling of different trigger types

## Troubleshooting

### Common Issues

#### 1. **Formatting Issues on PR**
- Run `python scripts/format.py` locally
- Commit and push the changes
- PR will be updated automatically

#### 2. **Test Failures After Formatting**
- Tests run on formatted code, so failures indicate real issues
- Check the test logs for specific error messages
- Ensure all dependencies are properly installed

#### 3. **Workflow Not Triggering**
- Check branch protection rules
- Ensure workflows are enabled in repository settings
- Verify trigger conditions in workflow files

### Debugging

#### 1. **Manual Workflow Execution**
- Use GitHub Actions UI to run workflows manually
- Check workflow logs for detailed error messages
- Use `workflow_dispatch` trigger for testing

#### 2. **Local Development**
```bash
# Install tools
pip install -r requirements-dev.txt

# Format code
python scripts/format.py

# Check formatting
python scripts/lint.py

# Run tests
python run_all_tests.py
```

## Best Practices

### 1. **Local Development**
- Always run formatting before pushing
- Use the provided scripts for consistency
- Check linting locally to avoid CI failures

### 2. **Pull Requests**
- Keep PRs focused and small
- Address formatting feedback promptly
- Use the standalone test workflow for complex scenarios

### 3. **Main Branch**
- Let the auto-commit handle formatting
- Monitor workflow results
- Use manual workflows for special cases

## Future Enhancements

### Potential Improvements
1. **Multi-Python Testing**: Add Python 3.10, 3.11 support
2. **Performance Optimization**: Parallel job execution where possible
3. **Advanced Linting**: Add mypy for type checking
4. **Security Scanning**: Add security vulnerability scanning
5. **Dependency Updates**: Automated dependency update workflows

### Monitoring
- Track workflow execution times
- Monitor formatting change frequency
- Analyze test failure patterns
- Optimize based on usage patterns