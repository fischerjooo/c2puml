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

   **Note:** The `.vscode/` directory is included in the repository, so all workspace settings, tasks, and debug configurations are automatically available.

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

The `debug.py` file provides a convenient way to debug the converter with **in-file configuration**. Simply modify the configuration variables at the top of the file and run it.

#### Configuration Constants in debug.py:

```python
# =============================================================================
# DEBUG CONFIGURATION - Modify these constants as needed
# =============================================================================

# Workflow selection: "full", "parse", "transform", "generate"
WORKFLOW: str = "full"

# Configuration file path (relative to project root)
CONFIG_PATH: str = "./example/config.json"

# Verbose output
VERBOSE: bool = True

# =============================================================================
# END CONFIGURATION
# =============================================================================
```

#### Available Debug Configurations:

1. **Debug Main (Full Workflow)** - Runs the complete workflow
2. **Debug Parse Only** - Runs only the parsing step (automatically modifies debug.py)
3. **Debug Transform Only** - Runs only the transformation step (automatically modifies debug.py)
4. **Debug Generate Only** - Runs only the generation step (automatically modifies debug.py)
5. **Debug Tests** - Runs all tests
6. **Debug Specific Test** - Runs the currently open test file

#### How to Use:

1. **Configure debug.py** by modifying the constants at the top of the file:
   ```python
   WORKFLOW = "parse"  # or "transform", "generate", "full"
   CONFIG_PATH = "./my_config.json"  # path to your config file
   VERBOSE = True  # or False
   ```

2. **Set breakpoints** in your code by clicking in the gutter next to line numbers

3. **Press F5** or go to Run → Start Debugging

4. **Select a debug configuration** from the dropdown

5. **Debug** with full control over execution

#### Quick Workflow Selection:

For quick workflow selection, use the predefined debug configurations:
- **"Debug Parse Only"** - Automatically sets `WORKFLOW = "parse"`
- **"Debug Transform Only"** - Automatically sets `WORKFLOW = "transform"`
- **"Debug Generate Only"** - Automatically sets `WORKFLOW = "generate"`

These configurations use pre-launch tasks to modify the `debug.py` file automatically.

#### Command Line Debug:

You can also run debug.py directly:

```bash
# Run with current configuration in debug.py
python debug.py
```

### Debug Configurations

The debug configurations automatically:
- Set up the correct Python path
- Use the configuration specified in `debug.py`
- Enable detailed logging based on `VERBOSE` setting
- Provide full stack traces
- Support automatic workflow selection via pre-launch tasks

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

## Debugging Workflow

### Step-by-Step Debugging:

1. **Configure debug.py:**
   ```python
   WORKFLOW = "parse"  # Choose your workflow
   CONFIG_PATH = "./example/config.json"  # Choose your config
   VERBOSE = True  # Enable detailed logging
   ```

2. **Set breakpoints** in the code you want to debug

3. **Run debug configuration** from VSCode

4. **Debug** with full control over execution

### Workflow Options:

- **"full"** - Complete workflow (parse → transform → generate)
- **"parse"** - Only parsing step (generate model.json)
- **"transform"** - Only transformation step (transform existing model.json)
- **"generate"** - Only generation step (generate PlantUML from model)

### Configuration Management:

- **Default**: Uses `./example/config.json`
- **Custom**: Change `CONFIG_PATH` to point to your configuration file
- **Multiple configs**: Create different config files for different scenarios

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
   - Ensure the config file specified in `CONFIG_PATH` exists

4. **Tasks not running:**
   - Ensure you're in the correct directory
   - Check that the required tools (python, pip, etc.) are in your PATH

5. **Configuration file not found:**
   - Check that the path in `CONFIG_PATH` is correct
   - Ensure the config file exists and is valid JSON

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

## Advanced Debugging Tips

### Configuration Management:

- **Example Config**: Use `./example/config.json` for basic testing
- **Custom Configs**: Create different config files for different scenarios
- **Multiple Configs**: Switch between configs by changing `CONFIG_PATH`

### Debugging Specific Issues:

1. **Parsing Issues**: Set `WORKFLOW = "parse"` to isolate parsing problems
2. **Transformation Issues**: Set `WORKFLOW = "transform"` with existing model.json
3. **Generation Issues**: Set `WORKFLOW = "generate"` with existing model files
4. **Filter Issues**: Use custom configuration files to test specific filters
5. **Performance Issues**: Set `VERBOSE = True` to see detailed execution flow

### Quick Configuration Changes:

```python
# For parsing only
WORKFLOW = "parse"
CONFIG_PATH = "./example/config.json"
VERBOSE = True

# For transformation only
WORKFLOW = "transform"
CONFIG_PATH = "./my_custom_config.json"
VERBOSE = False

# For full workflow with custom config
WORKFLOW = "full"
CONFIG_PATH = "./debug_config.json"
VERBOSE = True
```

### Pre-launch Tasks:

The debug configurations use pre-launch tasks to automatically modify `debug.py`:
- **modify-debug-config-parse**: Sets `WORKFLOW: str = "parse"`
- **modify-debug-config-transform**: Sets `WORKFLOW: str = "transform"`
- **modify-debug-config-generate**: Sets `WORKFLOW: str = "generate"`

This allows you to quickly switch between workflows without manually editing the file.