# Linting and Formatting Setup

This project uses automated linting and formatting tools to maintain code quality and consistency.

## Tools Used

- **flake8**: Python linting tool that checks for style guide enforcement, error detection, and complexity checking
- **black**: Uncompromising Python code formatter
- **isort**: Python utility to sort imports alphabetically and automatically separated into sections

## Configuration Files

- `.flake8`: Configuration for flake8 linting rules
- `pyproject.toml`: Configuration for black and isort formatting
- `.pre-commit-config.yaml`: Pre-commit hooks for local development

## GitHub Actions Workflows

### 1. Lint and Format Workflow (`lint-and-format.yml`)

This workflow runs on every push and pull request to the main branch and:

1. **Checks code formatting** with black and isort
2. **Runs comprehensive linting** with flake8
3. **Automatically formats code** if issues are found
4. **Commits and pushes changes** back to the repository
5. **Uploads formatted files** as artifacts

### 2. Enhanced Test Workflow (`test.yml`)

The existing test workflow has been enhanced to include:

- Development dependency installation
- Comprehensive flake8 linting
- Black formatting checks
- isort import sorting checks

## Local Development

### Installation

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

### Running Linting and Formatting

#### Check for Issues (No Changes Made)

```bash
# Run all checks
python scripts/lint.py

# Or run individual tools
flake8 c_to_plantuml/ main.py run_all_tests.py setup.py
black --check --diff c_to_plantuml/ main.py run_all_tests.py setup.py
isort --check-only --diff c_to_plantuml/ main.py run_all_tests.py setup.py
```

#### Automatically Fix Issues

```bash
# Run all formatting tools
python scripts/format.py

# Or run individual tools
black c_to_plantuml/ main.py run_all_tests.py setup.py
isort c_to_plantuml/ main.py run_all_tests.py setup.py
```

### Pre-commit Hooks (Optional)

Install pre-commit hooks for automatic formatting on commit:

```bash
pip install pre-commit
pre-commit install
```

This will automatically run black, isort, and flake8 before each commit.

## Configuration Details

### Black Configuration

- **Line length**: 88 characters (Black's default)
- **Target Python version**: 3.9+
- **Excludes**: Standard directories like `.git`, `build`, `dist`, etc.

### isort Configuration

- **Profile**: Black-compatible
- **Line length**: 88 characters
- **Multi-line output**: 3 (Black-compatible)
- **Known first party**: `c_to_plantuml`

### flake8 Configuration

- **Line length**: 88 characters
- **Extended ignore**: E203, W503 (Black-compatible)
- **Excludes**: Standard directories and files
- **Per-file ignores**: F401 for `__init__.py` files

## Workflow Integration

The GitHub Actions workflows are designed to:

1. **Fail fast**: Stop on the first linting error
2. **Auto-fix**: Automatically format code when possible
3. **Commit changes**: Push formatting changes back to the repository
4. **Provide feedback**: Show detailed error messages and statistics

## Troubleshooting

### Common Issues

1. **Line length violations**: Ensure all tools use 88 characters (Black's default)
2. **Import sorting conflicts**: isort is configured to be Black-compatible
3. **flake8 conflicts with Black**: E203 and W503 are ignored to prevent conflicts

### Manual Fixes

If automatic formatting fails, you can:

1. Run individual tools to see specific errors
2. Check the configuration files for any issues
3. Review the GitHub Actions logs for detailed error messages

## Best Practices

1. **Run linting locally** before pushing code
2. **Use the provided scripts** for consistent results
3. **Check GitHub Actions** after pushing to ensure everything passes
4. **Review auto-committed changes** to ensure they're correct

## Files Covered

The linting and formatting tools check the following files:

- `c_to_plantuml/` (entire package)
- `main.py`
- `run_all_tests.py`
- `setup.py`

All Python files in the project are automatically included in the checks.