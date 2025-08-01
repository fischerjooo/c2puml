# c2puml - C to PlantUML Converter

A Python tool for converting C/C++ source code to PlantUML diagrams. Analyzes C/C++ projects and generates comprehensive PlantUML class diagrams showing structs, enums, unions, functions, global variables, macros, typedefs, and include relationships.

## Status
[![Run Tests](https://github.com/fischerjooo/c2puml/actions/workflows/test.yml/badge.svg)](https://github.com/fischerjooo/c2puml/actions/workflows/test.yml)
[![Convert PlantUML to PNG](https://github.com/fischerjooo/c2puml/actions/workflows/puml2png.yml/badge.svg)](https://github.com/fischerjooo/c2puml/actions/workflows/puml2png.yml)
[![Coverage Reports](https://github.com/fischerjooo/c2puml/actions/workflows/test-coverage.yml/badge.svg)](https://github.com/fischerjooo/c2puml/actions/workflows/test-coverage.yml)
[![Deploy Website](https://github.com/fischerjooo/c2puml/actions/workflows/deploy-website.yml/badge.svg)](https://github.com/fischerjooo/c2puml/actions/workflows/deploy-website.yml)

## Reports

- [📊 Combined Coverage Report](https://fischerjooo.github.io/c2puml/artifacts/coverage/htmlcov/index.html) - Comprehensive coverage report with summary and detailed per-file analysis
- [📝 Test Summary](https://fischerjooo.github.io/c2puml/artifacts/test_reports/test_summary.html) - Test execution summary and statistics
- [📊 Example Diagrams](https://fischerjooo.github.io/c2puml/artifacts/output_example/diagram_index.html) - Quick view of all generated PlantUML diagrams and PNG images
- [📋 Example Source Code](https://github.com/fischerjooo/c2puml/tree/main/tests/example) - Browse the example C/C++ source files used for testing and demonstration

## Features

- **Comprehensive Parsing**: Parses structs, enums, unions, functions, globals, macros, typedefs, and includes
- **Project Analysis**: Analyzes entire C/C++ projects with recursive directory scanning
- **PlantUML Generation**: Creates organized PlantUML diagrams with proper UML notation
- **Configuration System**: Flexible filtering and transformation capabilities
- **Cross-Platform**: Works on Linux, macOS, and Windows with platform-specific batch/shell scripts

## Installation

```bash
git clone https://github.com/fischerjooo/c2puml.git
cd c2puml
python3 -m pip install -e .
```

## Quick Start

### Basic Usage

```bash
# Parse C project and generate diagrams
c2puml --config tests/example/config.json

# Or using module syntax
python3 -m c2puml.main --config tests/example/config.json
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

**Note**: The script automatically handles Graphviz installation and testing to resolve the "Dot executable does not exist" error.

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
```

### VSCode Configuration

The project includes pre-configured VSCode settings for:
- Python auto-formatting with Black
- Import sorting with isort
- Linting with flake8
- Auto-save and formatting on save

**VSCode Tasks**: The project includes pre-configured tasks accessible via `Ctrl+Shift+P` → "Tasks: Run Task":
- **Run Full Workflow** - Complete analysis and diagram generation
- **Run Example** - Quick test with example files
- **Generate Pictures** - Convert PlantUML to PNG images
- **Run Tests** - Execute test suite
- **Install Dependencies** - Set up development environment
- **Format & Lint** - Code quality checks

### Development Commands

```bash
# Run all tests
./run_all_tests.sh        # Linux/macOS
run_all_tests.bat         # Windows

# Run tests with coverage
run_tests_with_coverage.sh # Linux/macOS

# Format and lint code
format_lint.bat           # Windows

# Generate PNG images
./picgen.sh               # Linux/macOS
picgen.bat                # Windows

# Run full workflow
./run_all.sh              # Linux/macOS
run_all.bat               # Windows

# Install dependencies
install_dependencies.bat  # Windows

# Run example
run_example.bat           # Windows

# Git management utilities
git_manage.bat            # Windows - Interactive git operations
git_reset_pull.bat        # Windows - Reset and pull from remote
```

## License

MIT License
