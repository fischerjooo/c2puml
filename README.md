# C to PlantUML Converter

A Python tool for converting C/C++ source code to PlantUML diagrams. Analyzes C/C++ projects and generates comprehensive PlantUML class diagrams showing structs, enums, unions, functions, global variables, macros, typedefs, and include relationships.

## 🚀 Features

- **Comprehensive Parsing**: Parses structs, enums, unions, functions, globals, macros, typedefs, and includes
- **Project Analysis**: Analyzes entire C/C++ projects with recursive directory scanning
- **PlantUML Generation**: Creates organized PlantUML diagrams with proper UML notation
- **Configuration System**: Flexible filtering and transformation capabilities
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Robust Error Handling**: Custom exceptions with error codes and context preservation
- **Comprehensive Testing**: Extensive test coverage with reusable utilities
- **Code Quality**: Automated linting, formatting, and security checks
- **CI/CD Integration**: Automated quality checks and testing pipelines

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

## 🛠️ Quality Improvements

This project has been significantly enhanced with comprehensive quality improvements:

### 1. Centralized Error Handling
- **Custom exceptions** with error codes (1000-9999 range)
- **Context preservation** across error propagation
- **Centralized error handler** with logging and statistics
- **Graceful failure modes** with helpful diagnostics

### 2. Test Utilities and Maintainability
- **TestProjectBuilder** for creating test projects
- **TestModelBuilder** for creating test models
- **TestFileTemplates** for common file patterns
- **Parameterized testing** decorators
- **Automatic cleanup** mechanisms

### 3. Comprehensive Testing
- **Negative case testing** for failure modes
- **Edge case testing** for boundary conditions
- **Malformed file handling** tests
- **Performance testing** for large files
- **Unicode and encoding** tests

### 4. Code Quality Tools
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for style checking
- **pylint** for code quality
- **mypy** for type checking
- **bandit** for security
- **pydocstyle** for documentation
- **safety** for dependency security

### 5. CI/CD Integration
- **Pre-commit hooks** for local quality checks
- **GitHub Actions** for automated testing
- **Comprehensive test coverage** reporting
- **Security vulnerability** scanning

## Development

```bash
# Run comprehensive quality checks
python scripts/lint_and_format.py --verbose

# Run tests with coverage
pytest --cov=c_to_plantuml --cov-report=html

# Install dev dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Test PNG generation
./test_picgen.sh
```

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