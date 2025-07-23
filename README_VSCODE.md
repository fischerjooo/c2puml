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

The `debug.py` file provides a convenient way to debug the converter with predefined configurations and **interactive mode** for flexible workflow selection.

#### Available Debug Configurations:

1. **Debug Interactive Mode** - **NEW!** Interactive workflow and configuration selection
2. **Debug Main (Full Workflow)** - Runs the complete workflow
3. **Debug Parse Only** - Runs only the parsing step
4. **Debug Transform Only** - Runs only the transformation step
5. **Debug Generate Only** - Runs only the generation step
6. **Debug Example** - Runs with example configuration
7. **Debug Tests** - Runs all tests
8. **Debug Specific Test** - Runs the currently open test file

#### Interactive Mode - NEW!

The interactive mode allows you to select your workflow and configuration at runtime:

```bash
python debug.py --interactive
```

**Interactive Workflow Options:**
1. **Full Workflow** (parse → transform → generate)
2. **Parse Only** (generate model.json)
3. **Transform Only** (transform existing model.json)
4. **Generate Only** (generate PlantUML from model)
5. **Parse + Transform** (skip generation)
6. **Transform + Generate** (skip parsing)

**Interactive Configuration Options:**
1. **Test Configuration** (with filters)
2. **Example Configuration** (minimal)
3. **Custom Configuration** (interactive setup)
4. **Use existing config file**

**Custom Configuration Setup:**
- Project name and source folders
- Output directory and model filename
- Recursive search and include depth
- File filters (include/exclude patterns)
- Element filters (structs, functions)
- Verbose output option

#### How to Use:

1. **Set breakpoints** in your code by clicking in the gutter next to line numbers
2. **Press F5** or go to Run → Start Debugging
3. **Select a debug configuration** from the dropdown
4. **Debug** with full control over execution

#### Command Line Debug:

You can also run debug commands directly:

```bash
# Interactive mode (recommended for flexible debugging)
python debug.py --interactive

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

# Run with custom config
python debug.py --config path/to/config.json
```

### Debug Configurations

The debug configurations automatically:
- Set up the correct Python path
- Use predefined test configurations
- Enable detailed logging
- Provide full stack traces
- Support interactive workflow selection

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

## Interactive Debugging Workflow

### Step-by-Step Interactive Debugging:

1. **Start Interactive Mode:**
   ```bash
   python debug.py --interactive
   ```

2. **Select Workflow:**
   - Choose from 6 different workflow combinations
   - Mix and match parsing, transformation, and generation steps

3. **Select Configuration:**
   - Use predefined configurations
   - Create custom configurations interactively
   - Use existing configuration files

4. **Customize Settings:**
   - Set project name and source folders
   - Configure file and element filters
   - Adjust processing parameters

5. **Execute and Debug:**
   - Set breakpoints in the code
   - Run the selected workflow
   - Debug with full control

### Example Interactive Session:

```
=== C to PlantUML Converter - Interactive Debug Mode ===

1. Select Workflow:
   1. Full Workflow (parse → transform → generate)
   2. Parse Only (generate model.json)
   3. Transform Only (transform existing model.json)
   4. Generate Only (generate PlantUML from model)
   5. Parse + Transform (skip generation)
   6. Transform + Generate (skip parsing)

Select workflow (1-6) [1]: 2

2. Select Configuration:
   1. Test Configuration (with filters)
   2. Example Configuration (minimal)
   3. Custom Configuration (interactive setup)
   4. Use existing config file

Select configuration (1-4) [1]: 3

=== Custom Configuration Setup ===
Project name [Debug_Custom_Project]: MyTestProject
Source folders (comma-separated) [./example]: ./my_source_code
Output directory [./output/custom]: ./output/my_test
...

3. Verbose output? (y/n) [n]: y

=== Executing Workflow ===
Workflow: 2
Config: ./output/my_test/custom_config.json
Verbose: True
```

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

5. **Interactive mode issues:**
   - Make sure you're running in a terminal that supports input
   - Check that the configuration file paths are valid

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

### Custom Workflow Combinations:

The interactive mode supports custom workflow combinations:

- **Parse + Transform**: Useful when you want to process the model but not generate diagrams
- **Transform + Generate**: Useful when you have an existing model and want to apply transformations before generating diagrams

### Configuration Management:

- **Test Configuration**: Includes comprehensive filters for development testing
- **Example Configuration**: Minimal configuration for quick testing
- **Custom Configuration**: Interactive setup for specific requirements
- **Existing Config**: Use any existing configuration file

### Debugging Specific Issues:

1. **Parsing Issues**: Use "Parse Only" to isolate parsing problems
2. **Transformation Issues**: Use "Transform Only" with existing model.json
3. **Generation Issues**: Use "Generate Only" with existing model files
4. **Filter Issues**: Use custom configuration to test specific filters
5. **Performance Issues**: Use verbose mode to see detailed execution flow