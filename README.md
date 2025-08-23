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

## Documentation

- [📖 Specification](https://github.com/fischerjooo/c2puml/blob/main/docs/specification.md) - Complete technical specification and architecture documentation
- [🎨 PlantUML Template](https://github.com/fischerjooo/c2puml/blob/main/docs/puml_template.md) - PlantUML formatting template and diagram structure rules
- [⚙️ Configuration Guide](https://github.com/fischerjooo/c2puml/blob/main/docs/configuration.md) - Detailed config.json reference and examples

## Releases

- [📦 Download ZIP](https://github.com/fischerjooo/c2puml/archive/refs/heads/release.zip) - Download the latest release as ZIP archive
- [📦 Download TAR.GZ](https://github.com/fischerjooo/c2puml/archive/refs/heads/release.tar.gz) - Download the latest release as TAR.GZ archive

## Features

- **Advanced C/C++ Parsing**: Comprehensive tokenization-based parsing with robust preprocessor handling and conditional compilation support
- **Project Analysis**: Analyzes entire C/C++ projects with recursive directory scanning and configurable include depth processing
- **PlantUML Generation**: Creates organized PlantUML diagrams with proper UML notation and relationship visualization
- **Configuration System**: Flexible filtering and transformation capabilities with file-specific settings
- **Model Verification**: Built-in sanity checking and validation of parsed models to ensure accuracy
- **Cross-Platform**: Works on Linux, macOS, and Windows with platform-specific batch/shell scripts
- **Enhanced UML Stereotypes**: Uses specific stereotypes for different typedef types (<<enumeration>>, <<struct>>, <<union>>, <<typedef>>)
- **Smart Visibility Detection**: Automatically determines public/private visibility based on header file declarations

## Installation

### Option 1: Install as Python Package (Recommended)

```bash
git clone https://github.com/fischerjooo/c2puml.git
cd c2puml
python3 -m pip install -e .
```

### Option 2: Use Standalone Script (No Installation Required)

If you prefer not to install the package, you can use the standalone script directly:

```bash
git clone https://github.com/fischerjooo/c2puml.git
cd c2puml
# No installation needed - just run the script directly
python3 main.py --config tests/example/config.json
```

**Prerequisites for standalone usage:**
- Python 3.7 or later
- The complete c2puml source code (including the `src/` directory)

## Quick Start

### Basic Usage

#### Using Installed Package

```bash
# Full workflow: Parse → Transform → Generate diagrams
c2puml --config tests/example/config.json

# Using current directory configuration (merges all .json files)
c2puml

# Individual steps
c2puml --config tests/example/config.json parse      # Step 1: Parse only
c2puml --config tests/example/config.json transform  # Step 2: Transform only
c2puml --config tests/example/config.json generate   # Step 3: Generate only

# With verbose output for debugging
c2puml --config tests/example/config.json --verbose

# Alternative module syntax
python3 -m c2puml.main --config tests/example/config.json
```

#### Using Standalone Script (No Installation)

```bash
# Full workflow: Parse → Transform → Generate diagrams
python3 main.py --config tests/example/config.json

# Using current directory configuration (merges all .json files)
python3 main.py

# Individual steps
python3 main.py --config tests/example/config.json parse      # Step 1: Parse only
python3 main.py --config tests/example/config.json transform  # Step 2: Transform only
python3 main.py --config tests/example/config.json generate   # Step 3: Generate only

# With verbose output for debugging
python3 main.py --config tests/example/config.json --verbose
```

**Note**: Both methods provide identical functionality. Choose the one that best fits your workflow.

### Installation vs Standalone: Which to Choose?

| Feature | Installed Package | Standalone Script |
|---------|-------------------|-------------------|
| **Installation** | `pip install -e .` | None required |
| **Command** | `c2puml` | `python3 main.py` |
| **Portability** | System dependent | High (copy files) |
| **Updates** | `pip install --upgrade` | Manual (update source) |
| **Dependencies** | Automatic via pip | Manual management |
| **Development** | Good | Excellent |
| **CI/CD Integration** | Standard | Easy |
| **Distribution** | Package distribution | Source required |

**Choose installed package if:**
- You plan to use c2puml regularly
- You want automatic dependency management
- You prefer standard Python package workflows

**Choose standalone script if:**
- You want to try c2puml without installation
- You're in a restricted environment
- You need maximum portability
- You're doing development or testing

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

The `file_specific` feature allows you to configure file-specific settings for different root `.c` files. Each file can have its own `include_filter` and can override the global `include_depth` used by the transformer:

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
- **include_depth** (optional): Override the global include_depth setting for this specific file (applied by transformer)

Files without file-specific configuration will use the global settings. Include relationships are computed in the transformer and stored in `include_relations` on root `.c` files, which the generator consumes. The generator no longer accepts an `include_depth` parameter and falls back to direct includes only when `include_relations` are absent.

- **always_show_includes** (optional, global): When set to `true`, headers filtered out by `include_filter` remain visible in the diagram as empty header classes. Their contents and further includes are not processed, but their include relationships are still drawn from the file that included them.

### Model Transformations

The transformer supports modifying the parsed model before generating diagrams. Transformations are fully implemented and support multi-stage, containerized configuration with deterministic ordering (alphabetical by container name).

Recommended containerized configuration (use numeric prefixes to control order):

```json
{
  "transformations_01_rename": {
    "file_selection": [".*main\\.c$"],
    "rename": {
      "typedef": {"^old_name$": "new_name"},
      "functions": {"^calculate$": "compute"},
      "macros": {"^OLD_MACRO$": "NEW_MACRO"},
      "globals": {"^old_var$": "new_var"},
      "includes": {"^old\\.h$": "new\\.h"},
      "files": {"^legacy\\.c$": "modern\\.c"}
    }
  },
  "transformations_02_cleanup": {
    "file_selection": [],
    "remove": {
      "typedef": ["^legacy_.*"],
      "functions": ["^debug_.*", "^internal_.*"],
      "macros": ["^DEBUG_.*", "^TEMP_.*"],
      "globals": ["^old_global$"],
      "includes": ["^deprecated\\.h$"]
    }
  }
}
```

Notes:
- Containers are discovered by keys starting with `transformations` and applied in alphabetical order.
- `file_selection` is a list of regex patterns matched against file paths; omitted or empty applies to all files.
- Typedef renames automatically update type references in functions, globals, structs, and unions.
- Removing typedefs cleans up type references across the model.
- Include/file renames propagate to `includes` and `include_relations`.
- `add` is reserved for future use.

## Generated Output

The tool creates PlantUML diagrams showing:
- Source files with functions, structs, enums, unions
- Header files with declarations
- Include relationships between files
- Typedef relationships with enhanced UML stereotypes
- Color-coded elements (source, headers, typedefs)
- Dynamic visibility detection (public/private based on header presence)

## Architecture

**3-step processing pipeline with modular core components:**

1. **Parse** - Advanced C/C++ parsing with tokenization → `model.json`
2. **Transform** - Model transformation based on configuration → `model_transformed.json`  
3. **Generate** - PlantUML diagram generation with proper UML notation

### Core Components

- **Parser (`core/parser.py`)** - Main parsing orchestration with CParser implementation
- **Tokenizer (`core/parser_tokenizer.py`)** - Advanced C/C++ tokenization and lexical analysis
- **Preprocessor (`core/preprocessor.py`)** - Handles conditional compilation and preprocessor directives
- **Transformer (`core/transformer.py`)** - Model transformation and filtering engine
- **Generator (`core/generator.py`)** - PlantUML diagram generation with proper formatting
- **Verifier (`core/verifier.py`)** - Model validation and sanity checking

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
- **Run Full Workflow** - Complete analysis and diagram generation (parse → transform → generate)
- **Run Example** - Quick test with example files and comprehensive verification
- **Generate Pictures** - Convert PlantUML to PNG images with PlantUML toolchain
- **Run Tests** - Execute comprehensive test suite with coverage reporting
- **Install Dependencies** - Set up development environment with all required packages
- **Format & Lint** - Code quality checks with Black, isort, and flake8

### Development Commands

```bash
# Run all tests
./scripts/run_all_tests.sh     # Linux/macOS
scripts/run_all_tests.bat      # Windows
python scripts/run_all_tests.py # Cross-platform

# Run tests with coverage
./scripts/run_tests_with_coverage.sh # Linux/macOS (comprehensive coverage)

# Format and lint code
scripts/format_lint.bat        # Windows

# Generate PNG images from PlantUML
./scripts/picgen.sh            # Linux/macOS (comprehensive PlantUML toolchain)
scripts/picgen.bat             # Windows

# Run full workflow (parse → transform → generate)
./scripts/run_all.sh           # Linux/macOS
scripts/run_all.bat            # Windows

# Run example workflow
./scripts/run_example.sh       # Linux/macOS
scripts/run_example.bat        # Windows
# Or use standalone script directly:
python3 main.py --config tests/example/config.json

# Install dependencies
scripts/install_dependencies.bat # Windows

# Git management utilities
scripts/git_manage.bat         # Windows - Interactive git operations
scripts/git_reset_pull.bat     # Windows - Reset and pull from remote

# Debug and development utilities
python scripts/debug.py        # Development debugging script
python scripts/run_example_with_coverage.py # Example with coverage
```

## Troubleshooting

### Common Issues

**"Command 'c2puml' not found"**
- **Solution**: Install the package with `pip install -e .`
- **Alternative**: Use the standalone script: `python3 main.py --config config.json`

**"Module 'c2puml' not found"**
- **Solution**: Ensure you're in the project root directory and the `src/` folder exists
- **Alternative**: Use the standalone script which handles path setup automatically

**"Permission denied" errors**
- **Solution**: Use the standalone script which doesn't require installation: `python3 main.py`

**"Dot executable does not exist" (PlantUML PNG generation)**
- **Solution**: Install Graphviz or use the provided scripts: `./scripts/picgen.sh` or `scripts/picgen.bat`


### Getting Help

- **Quick Test**: Try the standalone script first: `python3 main.py --config tests/example/config.json`
- **Development**: Use the debug script: `python scripts/debug.py`
- **Examples**: Run the example workflow: `./scripts/run_example.sh` or `scripts/run_example.bat`

## License

MIT License


