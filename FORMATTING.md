# Automated Python Formatting and Import Sorting

This project uses comprehensive automated formatting tools to ensure consistent code style across all Python files.

## 🛠️ Tools Used

### Core Formatting Tools
- **Black**: Code formatter that enforces consistent style
- **isort**: Import sorting and organization
- **flake8**: Linting and style checking
- **pre-commit**: Git hooks for automated formatting

### Configuration Files
- `pyproject.toml`: Central configuration for all tools
- `.pre-commit-config.yaml`: Pre-commit hooks configuration
- `.flake8`: Flake8 configuration (legacy, now in pyproject.toml)

## 🚀 Quick Start

### Local Development

1. **Install dependencies**:
   ```bash
   pip install black isort flake8 pre-commit
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

### Pre-commit Hooks

Set up pre-commit hooks for automatic formatting on commit:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files
```

## 📋 GitHub Actions Workflows

### 1. Format Check Workflow (`format-check.yml`)
- **Trigger**: Push to main/master, PRs, manual dispatch
- **Purpose**: Check formatting without making changes
- **Tools**: black, isort, flake8, pre-commit
- **Matrix**: Python 3.9

### 2. Lint and Format Workflow (`lint-and-format.yml`)
- **Trigger**: Push to main/master, PRs, manual dispatch
- **Purpose**: Check formatting and auto-fix issues
- **Tools**: black, isort, flake8, pre-commit
- **Auto-commit**: Automatically commits formatting changes
- **Matrix**: Python 3.9

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
multi_line_output = 3
line_length = 88
known_first_party = ["c_to_plantuml"]
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
default_section = "THIRDPARTY"
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
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
- `.github/workflows/format-check.yml`: Format checking workflow
- `.github/workflows/lint-and-format.yml`: Format fixing workflow

### Configuration
- `pyproject.toml`: Central tool configuration
- `.pre-commit-config.yaml`: Pre-commit hooks
- `.flake8`: Legacy flake8 config (deprecated)

## 🔧 Customization

### Adding New Tools
1. Update `pyproject.toml` with tool configuration
2. Add tool to GitHub workflows
3. Update scripts in `scripts/` directory
4. Update pre-commit hooks if needed

### Modifying Rules
1. Edit `pyproject.toml` for tool-specific rules
2. Update workflow files for CI/CD changes
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

The automated workflows provide:

- ✅ **Format Checking**: Ensures all code follows style guidelines
- ✅ **Import Sorting**: Maintains consistent import organization
- ✅ **Linting**: Catches style and potential issues
- ✅ **Auto-fixing**: Automatically fixes formatting issues
- ✅ **Python 3.9 Support**: Optimized for Python 3.9 compatibility
- ✅ **PR Integration**: Comments on PRs with formatting issues
- ✅ **Artifact Upload**: Provides formatted files as artifacts

## 🎯 Best Practices

1. **Always run formatting before committing**:
   ```bash
   python scripts/format.py
   ```

2. **Use pre-commit hooks** for automatic formatting

3. **Check formatting in CI/CD** before merging

4. **Keep configuration centralized** in `pyproject.toml`

5. **Ensure Python 3.9 compatibility** for optimal performance

## 📝 Contributing

When contributing to this project:

1. Install development dependencies
2. Set up pre-commit hooks
3. Run formatting before committing
4. Ensure all checks pass locally
5. The CI/CD will automatically format and check your code

For more information, see the main [README.md](README.md) and [WORKFLOWS.md](WORKFLOWS.md) files.