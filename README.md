<h1 align="center">c2puml - C to PlantUML Converter</h1>
<p align="center">
  <img src="docs/c2puml.jpg" alt="C 2 Puml" width="128"/>
</p>
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

- **C/C++ Parsing**: Comprehensive tokenization-based parsing with preprocessor handling and conditional compilation support
- **Project Analysis**: Analyzes entire C/C++ projects with recursive directory scanning and configurable include depth processing
- **PlantUML Generation**: Creates organized PlantUML diagrams with proper UML notation and relationship visualization
- **Configuration System**: Flexible filtering and transformation capabilities with file-specific settings
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

Create a `config.json` to customize analysis and output. Minimal example:

```json
{
  "project_name": "my_project",
  "source_folders": ["./src"],
  "output_dir": "./output"
}
```

Run with a config file:

```bash
c2puml --config config.json
# or (merges all .json files in the current directory)
c2puml
```

For full examples (file-specific include filters, include depth, formatting, and the transformation system), see the Configuration Guide: [docs/configuration.md](docs/configuration.md).

## Generated Output

The tool creates PlantUML diagrams showing:
- Source files with functions, structs, enums, unions
- Header files with declarations
- Include relationships between files
- Typedef relationships with enhanced UML stereotypes
- Color-coded elements (source, headers, typedefs)
- Dynamic visibility detection (public/private based on header presence)

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
