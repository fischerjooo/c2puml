# VSCode Development Setup for C to PlantUML Converter

This document describes how to set up and use VSCode for developing and debugging the C to PlantUML converter.

## Quick Start

1. **Open the project in VSCode:**
   ```bash
   code .
   ```

2. **Install recommended extensions** when prompted, or manually install:
   - Python extension
   - PlantUML extension
   - Git extension
   - And others listed in `.vscode/extensions.json`

3. **Set up Python environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

4. **Select Python interpreter** in VSCode:
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Python: Select Interpreter"
   - Choose the interpreter from your `venv` folder

## Debugging

### Using the Debug Entry Point

The `debug.py` file provides a convenient way to debug the converter with predefined configurations:

#### Available Debug Configurations:

1. **Debug Main (Full Workflow)** - Runs the complete workflow
2. **Debug Parse Only** - Runs only the parsing step
3. **Debug Transform Only** - Runs only the transformation step
4. **Debug Generate Only** - Runs only the generation step
5. **Debug Example** - Runs with example configuration
6. **Debug Tests** - Runs all tests
7. **Debug Specific Test** - Runs the currently open test file

#### How to Use:

1. **Set breakpoints** in your code by clicking in the gutter next to line numbers
2. **Press F5** or go to Run → Start Debugging
3. **Select a debug configuration** from the dropdown
4. **Debug** with full control over execution

#### Command Line Debug:

You can also run debug commands directly:

```bash
# Run full workflow
python debug.py

# Run specific step
python debug.py parse
python debug.py transform
python debug.py generate

# Run with example config
python debug.py example

# Run with verbose output
python debug.py --verbose
```

### Debug Configurations

The debug configurations automatically:
- Set up the correct Python path
- Use predefined test configurations
- Enable detailed logging
- Provide full stack traces

## Tasks

VSCode tasks provide quick access to common development operations:

### Build Tasks:
- **Run Full Workflow (Windows/Linux/Mac)** - Executes the complete pipeline
- **Run Example (Windows/Linux/Mac)** - Runs with example configuration
- **Generate Pictures (Windows/Linux/Mac)** - Generates PlantUML diagrams
- **Parse Only (Python)** - Runs parsing step
- **Transform Only (Python)** - Runs transformation step
- **Generate Only (Python)** - Runs generation step

### Development Tasks:
- **Install Dependencies** - Installs development dependencies
- **Lint Code** - Runs flake8 linting
- **Format Code** - Formats code with black
- **Clean Output** - Removes output files

### Test Tasks:
- **Run All Tests (Windows/Linux/Mac)** - Runs all tests
- **Run Pytest** - Runs pytest directly

### How to Use Tasks:

1. **Press `Ctrl+Shift+P`** (or `Cmd+Shift+P` on Mac)
2. **Type "Tasks: Run Task"**
3. **Select the desired task**

Or use the keyboard shortcut `Ctrl+Shift+P` → "Tasks: Run Build Task" for quick access to build tasks.

## Features

### Auto-formatting
- Code is automatically formatted on save using Black
- Imports are automatically organized
- Auto-save is enabled with 1-second delay

### IntelliSense
- Full Python IntelliSense support
- C/C++ IntelliSense for example files
- PlantUML syntax highlighting and preview

### Testing
- Integrated pytest support
- Test discovery and execution
- Debug support for individual tests

### PlantUML Integration
- Syntax highlighting for `.puml` files
- Live preview using PlantUML server
- Automatic rendering of diagrams

## Workspace Settings

The workspace is configured with:

- **Python settings** for development environment
- **File associations** for various file types
- **Search exclusions** for build artifacts
- **Formatting rules** for consistent code style

## Troubleshooting

### Common Issues:

1. **Python interpreter not found:**
   - Make sure you've created and activated a virtual environment
   - Select the correct interpreter in VSCode

2. **Import errors:**
   - Ensure `PYTHONPATH` includes the project root
   - Check that all dependencies are installed

3. **Debug not working:**
   - Verify that `debug.py` is in the project root
   - Check that the Python path is correctly set

4. **Tasks not running:**
   - Ensure you're in the correct directory
   - Check that the required tools (python, pip, etc.) are in your PATH

### Getting Help:

- Check the main `README.md` for project overview
- Look at the `specification.md` for detailed technical information
- Review the `workflow.md` for process documentation

## Keyboard Shortcuts

| Action | Windows/Linux | Mac |
|--------|---------------|-----|
| Start Debugging | F5 | F5 |
| Stop Debugging | Shift+F5 | Shift+F5 |
| Step Over | F10 | F10 |
| Step Into | F11 | F11 |
| Step Out | Shift+F11 | Shift+F11 |
| Run Task | Ctrl+Shift+P → "Tasks: Run Task" | Cmd+Shift+P → "Tasks: Run Task" |
| Run Build Task | Ctrl+Shift+P → "Tasks: Run Build Task" | Cmd+Shift+P → "Tasks: Run Build Task" |
| Select Python Interpreter | Ctrl+Shift+P → "Python: Select Interpreter" | Cmd+Shift+P → "Python: Select Interpreter" |

## Extensions

The following extensions are recommended for this project:

- **Python** - Python language support
- **PlantUML** - PlantUML diagram support
- **Git** - Git integration
- **GitHub** - GitHub integration
- **Docker** - Docker support
- **YAML** - YAML file support
- **JSON** - JSON file support
- **Markdown** - Markdown support
- **PowerShell** - PowerShell support
- **Remote Development** - Remote development support

These extensions will be automatically suggested when you open the project in VSCode.