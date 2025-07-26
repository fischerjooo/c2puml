# C to PlantUML Converter

A Python tool for converting C/C++ source code to PlantUML diagrams. Analyzes C/C++ projects and generates comprehensive PlantUML class diagrams showing structs, enums, unions, functions, global variables, macros, typedefs, and include relationships.

## Test Coverage Reports

- [📊 Combined Coverage Report](https://fischerjooo.github.io/generator_project/tests/reports/coverage/index.html) - Comprehensive coverage report with summary and detailed per-file analysis
- [📄 Coverage Summary](https://fischerjooo.github.io/generator_project/tests/reports/coverage/coverage_summary.txt) - Text-based coverage summary
- [📝 Test Summary](https://fischerjooo.github.io/generator_project/tests/reports/coverage/test_summary.html) - Test execution summary and statistics

## Features

- **Comprehensive Parsing**: Parses structs, enums, unions, functions, globals, macros, typedefs, and includes
- **Project Analysis**: Analyzes entire C/C++ projects with recursive directory scanning
- **PlantUML Generation**: Creates organized PlantUML diagrams with proper UML notation
- **Configuration System**: Flexible filtering and transformation capabilities
- **Cross-Platform**: Works on Linux, macOS, and Windows

## Installation

```bash
git clone <repository-url>
cd generator_project
python3 -m pip install -e .
```

## Quick Start

### Basic Usage

```bash
# Parse C project and generate diagrams
python3 -m c_to_plantuml.main --config example/config.json

# Or use individual steps
python3 -m c_to_plantuml.main parse example/source
python3 -m c_to_plantuml.main generate output/model.json
```

### Generate PNG Images

```bash
# Linux/macOS
./picgen.sh

# Windows
picgen.bat
```

The scripts automatically:
- Download PlantUML.jar if needed
- Install Graphviz (required for PNG generation)
- Test the setup before conversion
- Convert all .puml files to PNG images

**Note**: The script now automatically handles Graphviz installation and testing to resolve the "Dot executable does not exist" error.

## Configuration

Create `config.json` for customization:

```json
{
  "source_folders": ["./src"],
  "project_name": "MyProject",
  "output_dir": "./output",
  "recursive": true,
  "file_filters": {
    "include": [".*\\.c$", ".*\\.h$"],
    "exclude": [".*test.*"]
  }
}
```

## Generated Output

The tool creates PlantUML diagrams showing:
- Source files with functions, structs, enums, unions
- Header files with declarations
- Include relationships between files
- Typedef relationships with proper UML stereotypes
- Color-coded elements (source, headers, typedefs)

## Architecture

3-step processing pipeline:
1. **Parse** - Analyzes C/C++ files → `model.json`
2. **Transform** - Modifies model based on config (optional)
3. **Generate** - Creates PlantUML diagrams

## Development Setup

### Quick Setup (Linux/macOS)

For a complete development environment setup:

```bash
# Run the comprehensive setup script
./setup-linux.sh
```

This script will:
- Install system dependencies
- Create a Python virtual environment
- Install all development dependencies
- Set up git hooks
- Configure VSCode settings
- Test the setup

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install development dependencies
pip install -r requirements-dev.txt

# Install package in development mode
pip install -e .

# Set up git hooks
./setup-hooks.sh  # Linux/macOS
# or
setup-hooks.bat   # Windows
```

### VSCode Configuration

The project includes pre-configured VSCode settings for:
- Python auto-formatting with Black
- Import sorting with isort
- Linting with flake8
- Auto-save and formatting on save

### Development Commands

```bash
# Run tests with coverage
./run_tests_with_coverage.sh

# Format code
black .
isort .

# Lint code
flake8 .

# Test PNG generation
./test_picgen.sh
```

### Git Hooks Setup

The project includes pre-commit hooks for code quality:

```bash
# Linux/macOS
./setup-hooks.sh

# Windows
setup-hooks.bat
```

This installs a pre-commit hook that automatically runs:
- **Black** formatting check
- **isort** import sorting check

The hook will prevent commits if formatting issues are detected.

## GitHub Workflow

The repository includes an automated GitHub workflow that:
- Triggers on pushes to main/master branch when .puml files change
- Automatically installs Graphviz and PlantUML
- Converts all .puml files to PNG images
- Commits the generated images back to the repository
- Uploads images as workflow artifacts

The workflow is simplified and more reliable, removing complex Git operations and focusing on core functionality.

## License

MIT License 