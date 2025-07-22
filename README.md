# C to PlantUML Converter

A Python tool for converting C/C++ source code to PlantUML diagrams. Analyzes C/C++ projects and generates comprehensive PlantUML class diagrams showing structs, enums, unions, functions, global variables, macros, typedefs, and include relationships.

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

The scripts automatically download PlantUML.jar if needed.

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

## Development

```bash
# Run tests
python run_all_tests.py

# Install dev dependencies
pip install -r requirements-dev.txt
```

## License

MIT License 