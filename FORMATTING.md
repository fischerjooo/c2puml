# Python Code Formatting

This project uses a simple local script to format all Python files consistently.

## 🛠️ Tools Used

### Formatting Tools
- **Black**: Code formatter that enforces consistent style
- **isort**: Import sorting and organization

### Configuration Files
- `pyproject.toml`: Configuration for black and isort
- `scripts/format.py`: Single script to format all Python files

## 🚀 Quick Start

### Local Development

1. **Install dependencies**:
   ```bash
   pip install black isort
   ```

2. **Format all Python files**:
   ```bash
   python scripts/format.py
   ```

3. **Or run individual tools**:
   ```bash
   python3 -m black .
   python3 -m isort .
   ```

## 📁 File Organization

### Scripts
- `scripts/format.py`: Single script to format all Python files

### Configuration
- `pyproject.toml`: Tool configuration for black and isort

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

## 🎯 Usage

### Format All Files
```bash
# Run the single formatting script
python scripts/format.py
```

### What It Does
1. **Finds all Python files** in the project (excluding build directories)
2. **Formats code** with black (consistent style)
3. **Sorts imports** with isort (organized imports)
4. **Reports results** with clear success/failure messages

### Example Output
```
🚀 Auto-formatting all Python files...
============================================================
📁 Found 26 Python files to format:
   - c_to_plantuml/__init__.py
   - c_to_plantuml/config.py
   - c_to_plantuml/generator.py
   ...

🎨 Running black code formatting...
🔧 black code formatting...
✅ black code formatting completed successfully

📦 Running isort import sorting...
🔧 isort import sorting...
✅ isort import sorting completed successfully

============================================================
🎉 All Python files formatted successfully!

💡 To run tests, use:
   python run_all_tests.py
```

## 🔧 Customization

### Adding New Tools
1. Update `pyproject.toml` with tool configuration
2. Add tool to `scripts/format.py`

### Modifying Rules
1. Edit `pyproject.toml` for tool-specific rules
2. Test locally with `python scripts/format.py`

## 🎯 Best Practices

1. **Run formatting before committing**:
   ```bash
   python scripts/format.py
   ```

2. **Keep configuration centralized** in `pyproject.toml`

3. **Use consistent Python version** (3.9) for optimal compatibility

## 📝 Contributing

When contributing to this project:

1. Install development dependencies: `pip install black isort`
2. Run formatting before committing: `python scripts/format.py`
3. Ensure all tests pass: `python run_all_tests.py`

That's it! No complex CI/CD, no automated workflows - just a simple local script to keep your code formatted.

For more information, see the main [README.md](README.md) file.