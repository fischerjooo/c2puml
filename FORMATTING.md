# Automated Python Formatting and Import Sorting

This project uses automated formatting tools to ensure consistent code style across all Python files.

## 🛠️ Tools Used

### Core Formatting Tools
- **Black**: Code formatter that enforces consistent style
- **isort**: Import sorting and organization
- **flake8**: Linting and style checking

### Configuration Files
- `pyproject.toml`: Central configuration for all tools
- `.pre-commit-config.yaml`: Pre-commit hooks configuration (optional)

## 🚀 Quick Start

### Local Development

1. **Install dependencies**:
   ```bash
   pip install black isort flake8
   ```

2. **Run formatting**:
   ```bash
   # Format all Python files
   python scripts/format.py
   
   # Or run individual tools
   python3 -m black .
   python3 -m isort .
   ```

3. **Check formatting**:
   ```bash
   # Check all formatting and linting
   python scripts/lint.py
   
   # Or run individual checks
   python3 -m black --check .
   python3 -m isort --check-only .
   python3 -m flake8 .
   ```

### Pre-commit Hooks (Optional)

Set up pre-commit hooks for automatic formatting on commit:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files
```

## 📋 GitHub Actions Workflow

### Python Format and Lint Workflow (`python-format.yml`)
- **Trigger**: Push to main/master, PRs, manual dispatch
- **Purpose**: Check formatting and auto-fix issues
- **Tools**: black, isort, flake8
- **Python Version**: 3.9
- **Auto-commit**: Automatically commits formatting changes for both pushes and PRs

### Test Auto-Formatting Workflow (`test-format.yml`)
- **Trigger**: Manual dispatch only
- **Purpose**: Test and demonstrate auto-formatting capability
- **Tools**: black, isort, flake8
- **Python Version**: 3.9
- **Auto-commit**: Commits formatting changes when manually triggered

## ⚙️ Configuration Details

### Black Configuration
```toml
[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'
extend-exclude = '''
/(
  \.eggs | \.git | \.hg | \.mypy_cache | \.tox | \.venv | 
  build | dist | c_to_plantuml\.egg-info
)/
'''
```

### isort Configuration
```toml
[tool.isort]
profile = "black"
line_length = 88
known_first_party = ["c_to_plantuml"]
skip_glob = [
    "build/*", "dist/*", "*.egg-info/*", ".venv/*", 
    "venv/*", ".tox/*", ".mypy_cache/*"
]
```

### Flake8 Configuration
```toml
[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "W503", "E501", "F401", "F841", "W293"]
exclude = [
    ".git", "__pycache__", "build", "dist", ".eggs", "*.egg",
    ".venv", "venv", ".tox", ".mypy_cache", "c_to_plantuml.egg-info"
]
per-file-ignores = [
    "__init__.py:F401",
    "tests/*:F401",
    "scripts/*:F401",
    "run_all_tests.py:F401"
]
```

## 📁 File Organization

### Scripts
- `scripts/format.py`: Comprehensive formatting script
- `scripts/lint.py`: Comprehensive linting and checking script

### Workflows
- `.github/workflows/python-format.yml`: Main formatting workflow

### Configuration
- `pyproject.toml`: Central tool configuration
- `.pre-commit-config.yaml`: Pre-commit hooks (optional)

## 🔧 Customization

### Adding New Tools
1. Update `pyproject.toml` with tool configuration
2. Add tool to GitHub workflow
3. Update scripts in `scripts/` directory

### Modifying Rules
1. Edit `pyproject.toml` for tool-specific rules
2. Update workflow file for CI/CD changes
3. Test locally with `python scripts/lint.py`

## 🚨 Common Issues

### Import Sorting Issues
```bash
# Fix import sorting
python3 -m isort .

# Check import sorting
python3 -m isort --check-only --diff .
```

### Code Formatting Issues
```bash
# Fix code formatting
python3 -m black .

# Check code formatting
python3 -m black --check --diff .
```

### Linting Issues
```bash
# Run linting
python3 -m flake8 . --max-line-length=88 --extend-ignore=E203,W503,E501,F401,F841,W293
```

## 📊 Workflow Status

The automated workflow provides:

- ✅ **Format Checking**: Ensures all code follows style guidelines
- ✅ **Import Sorting**: Maintains consistent import organization
- ✅ **Linting**: Catches style and potential issues
- ✅ **Auto-fixing**: Automatically fixes formatting issues for pushes and PRs
- ✅ **Python 3.9 Support**: Optimized for Python 3.9 compatibility
- ✅ **PR Integration**: Auto-formats PRs and comments with success message
- ✅ **Simplified Setup**: Clean and reliable automation

## 🎯 Best Practices

1. **Always run formatting before committing**:
   ```bash
   python scripts/format.py
   ```

2. **Use pre-commit hooks** for automatic formatting (optional)

3. **Check formatting in CI/CD** before merging

4. **Keep configuration centralized** in `pyproject.toml`

5. **Ensure Python 3.9 compatibility** for optimal performance

## 📝 Contributing

When contributing to this project:

1. Install development dependencies
2. Set up pre-commit hooks (optional)
3. Run formatting before committing (optional - CI will auto-fix)
4. Ensure all checks pass locally
5. The CI/CD will automatically format and commit any formatting issues to your PR

**Note**: The workflow will automatically fix formatting issues in your PR and commit them back to your branch, so you don't need to worry about formatting manually.

For more information, see the main [README.md](README.md) and [WORKFLOWS.md](WORKFLOWS.md) files.