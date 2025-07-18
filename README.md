# C to PlantUML Converter

A Python tool that analyzes C/C++ source code and generates PlantUML class diagrams.

## Features

- **C/C++ Parsing**: Extracts structs, enums, functions, macros, and global variables
- **PlantUML Generation**: Creates UML class diagrams with proper notation
- **Simple Configuration**: Easy-to-use JSON configuration for filtering and transformations
- **Clean Output**: Organized PlantUML files with clear structure

## Quick Start

### Basic Usage

```bash
# Analyze a C project and generate PlantUML diagrams
python -m c_to_plantuml.main analyze ./my_project

# Generate diagrams from existing JSON model
python -m c_to_plantuml.main generate project_model.json

# Use configuration file for advanced filtering
python -m c_to_plantuml.main config config.json
```

### Configuration Example

Create a `config.json` file:

```json
{
  "project_roots": ["./src"],
  "output_dir": "./diagrams",
  "file_filters": {
    "include": [".*\\.c$", ".*\\.h$"],
    "exclude": [".*test.*"]
  },
  "element_filters": {
    "structs": {
      "include": ["^[A-Z].*"],
      "exclude": [".*_internal.*"]
    }
  }
}
```

## Installation

```bash
pip install -e .
```

## Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_parser.py
```

## Project Structure

```
c_to_plantuml/
├── main.py                 # Simple CLI interface
├── analyzer.py             # Core analysis logic
├── parser.py               # C/C++ code parsing
├── generator.py            # PlantUML generation
├── config.py               # Configuration handling
└── models.py               # Data structures
```

## License

MIT License 