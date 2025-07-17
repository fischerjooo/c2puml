# c_to_plantuml

C to PlantUML Class Diagram Generator
=====================================

A Python tool for converting C code projects to PlantUML class diagrams.

## Features
- Parses C structs, enums, typedefs, and functions
- Generates PlantUML class diagrams
- Supports JSON-based filtering, renaming, and styling
- CLI for easy usage

## Installation

```bash
pip install .
```

or for development:

```bash
pip install -e .
```

## Usage

```bash
python -m c_to_plantuml /path/to/c/project -o diagram.puml
python -m c_to_plantuml /path/to/c/project -j config.json -o diagram.puml
python -m c_to_plantuml /path/to/c/project --print
python -m c_to_plantuml /path/to/c/project --no-recursive -o diagram.puml
```

## JSON Config Example

```json
{
  "filters": {
    "exclude_structs": ["internal_struct", "debug_info"],
    "include_enums": ["ErrorCode", "State", "Mode"]
  },
  "transformations": {
    "rename_structs": {
      "old_struct_name": "NewStructName"
    },
    "rename_enums": {
      "old_enum": "NewEnum"
    }
  },
  "styling": {
    "colors": {
      "class": "LightBlue",
      "enum": "LightGreen"
    },
    "layout": "top to bottom direction"
  }
}
```

## License
MIT 