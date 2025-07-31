# c2puml - C to PlantUML Converter

A Python tool for converting C/C++ source code to PlantUML diagrams. Analyzes C/C++ projects and generates comprehensive PlantUML class diagrams showing structs, enums, unions, functions, global variables, macros, typedefs, and include relationships.

## Status
[![Run Tests](https://github.com/fischerjooo/c2puml/actions/workflows/test.yml/badge.svg)](https://github.com/fischerjooo/c2puml/actions/workflows/test.yml)
[![Convert PlantUML to PNG](https://github.com/fischerjooo/c2puml/actions/workflows/puml2png.yml/badge.svg)](https://github.com/fischerjooo/c2puml/actions/workflows/puml2png.yml)
[![Coverage Reports](https://github.com/fischerjooo/c2puml/actions/workflows/test-coverage.yml/badge.svg)](https://github.com/fischerjooo/c2puml/actions/workflows/test-coverage.yml)
[![Deploy Website](https://github.com/fischerjooo/c2puml/actions/workflows/deploy-website.yml/badge.svg)](https://github.com/fischerjooo/c2puml/actions/workflows/deploy-website.yml)

## Reports

- [📊 Combined Coverage Report](https://fischerjooo.github.io/c2puml/tests/reports/coverage/htmlcov/index.html) - Comprehensive coverage report with summary and detailed per-file analysis
- [📝 Test Summary](https://fischerjooo.github.io/c2puml/tests/reports/test_summary.html) - Test execution summary and statistics
- [📊 Example Diagrams](https://fischerjooo.github.io/c2puml/output/diagram_index.html) - Quick view of all generated PlantUML diagrams and PNG images

## Features

- **Comprehensive Parsing**: Parses structs, enums, unions, functions, globals, macros, typedefs, and includes
- **Project Analysis**: Analyzes entire C/C++ projects with recursive directory scanning
- **PlantUML Generation**: Creates organized PlantUML diagrams with proper UML notation
- **Configuration System**: Flexible filtering and transformation capabilities
- **Cross-Platform**: Works on Linux, macOS, and Windows

## Installation

```bash
git clone <repository-url>
cd c2puml
python3 -m pip install -e .
```

## Quick Start

### Basic Usage

```bash
# Parse C project and generate diagrams
c2puml --config example/config.json

# Or using module syntax
python3 -m c2puml.main --config example/config.json
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

Create `config.json` for customization. The configuration supports multiple filtering and transformation options:

### Filtering Options

- **file_filters**: Filter files by path patterns

- **file_specific**: Configure file-specific settings including include filters for each root C file

### File-Specific Configuration

The `file_specific` feature allows you to configure file-specific settings for different root files. Each file can have its own `include_filter` and `include_depth` settings:

```json
"file_specific": {
  "main.c": {
    "include_filter": ["^stdio\\.h$", "^stdlib\\.h$", "^string\\.h$"],
    "include_depth": 3
  },
  "network.c": {
    "include_filter": ["^sys/socket\\.h$", "^netinet/", "^arpa/"],
    "include_depth": 2
  },
  "database.c": {
    "include_filter": ["^sqlite3\\.h$", "^mysql\\.h$", "^postgresql/"],
    "include_depth": 4
  },
  "simple.c": {
    "include_depth": 1
  }
}
```

**Available file-specific settings:**
- **include_filter** (optional): Array of regex patterns to filter includes for this specific file
- **include_depth** (optional): Override the global include_depth setting for this specific file

Files without file-specific configuration will use the global settings. This enables fine-grained control over include processing for each root file, creating cleaner, more focused diagrams.

### Model Transformations

The transformer supports modifying the parsed model before generating diagrams:

```json
{
  "transformations": {
    "remove": {
      "typedef": ["legacy_type", "temp_struct"],
      "functions": ["debug_func", "internal_*"],
      "macros": ["DEBUG_*", "TEMP_MACRO"],
      "globals": ["old_global"],
      "includes": ["deprecated.h"]
    },
    "rename": {
      "typedef": {"old_name": "new_name"},
      "functions": {"calculate": "compute"},
      "macros": {"OLD_MACRO": "NEW_MACRO"},
      "globals": {"old_var": "new_var"},
      "includes": {"old.h": "new.h"},
      "files": {"legacy.c": "modern.c"}
    },
    "file_selection": {
      "selected_files": [".*main\\.c$"]
    }
  }
}
```

**Note:** Transformation functionality provides configuration structure with stub implementations for future development.

```json
{
  "source_folders": ["./src"],
  "project_name": "MyProject",
  "output_dir": "./output",
  "recursive_search": true,
  "include_depth": 2,
  "file_filters": {
    "include": [".*\\.c$", ".*\\.h$"],
    "exclude": [".*test.*"]
  },
  "file_specific": {
    "main.c": {
      "include_filter": ["^stdio\\.h$", "^stdlib\\.h$", "^string\\.h$"],
      "include_depth": 3
    },
    "network.c": {
      "include_filter": ["^sys/socket\\.h$", "^netinet/", "^arpa/"],
      "include_depth": 2
    }
  },
  "transformations": {
    "remove": {
      "typedef": [],
      "functions": [],
      "macros": [],
      "globals": [],
      "includes": []
    },
    "rename": {
      "typedef": {},
      "functions": {},
      "macros": {},
      "globals": {},
      "includes": {},
      "files": {}
    }
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

# PNG generation
./picgen.sh
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

## License

MIT License
