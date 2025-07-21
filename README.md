# C to PlantUML Converter

A robust Python tool for converting C/C++ source code to PlantUML diagrams. This tool analyzes C/C++ projects and generates comprehensive PlantUML class diagrams showing structs, enums, unions, functions, global variables, macros, typedefs, and include relationships.

## Features

- **Comprehensive C/C++ Parsing**: Parses structs, enums, unions, functions, global variables, macros, typedefs, and includes
- **Project Analysis**: Analyzes entire C/C++ projects with recursive directory scanning
- **PlantUML Generation**: Creates beautiful, organized PlantUML diagrams with proper UML notation
- **Configuration System**: Flexible configuration with file and element filtering
- **Model Transformation**: Advanced model transformation with renaming, addition, and removal capabilities
- **Typedef Relationship Analysis**: Comprehensive parsing of typedef relationships with proper UML stereotypes
- **Union Support**: Full parsing and visualization of union definitions with fields
- **Robust Error Handling**: Graceful handling of invalid files and encoding issues
- **Cross-Platform Encoding Support**: Automatic detection and handling of different file encodings (UTF-8, Windows-1252, Windows-1254, etc.)
- **Logging Support**: Comprehensive logging for debugging and monitoring
- **Type Safety**: Full type hints and validation throughout the codebase
- **Modular Architecture**: 3-step processing pipeline for maximum flexibility

## Installation

### Prerequisites

- Python 3.7 or higher
- No external dependencies (uses only Python standard library)

### Install from Source

```bash
git clone <repository-url>
cd generator_project
python3 -m pip install -e .
```

### Development Setup

For development, install additional dependencies:

```bash
pip install -r requirements-dev.txt
```

## Usage

The tool provides a 3-step processing pipeline that can be executed individually or chained together:

### Processing Flow

1. **Parse** - Parses C code files and generates model.json
2. **Transform** - Modifies the model file based on transformation configuration
3. **Generate** - Generates puml files based on the model.json

### Command Line Interface

The tool provides a 3-step processing pipeline that can be executed individually or chained together:

#### 1. Parse C/C++ Project (Step 1)

```bash
python3 main.py parse ./src -o model.json --verbose
```

Options:
- `project_root`: Root directory of C/C++ project
- `-o, --output`: Output JSON model file (default: model.json)
- `--recursive/--no-recursive`: Search subdirectories recursively (default: True)
- `--verbose, -v`: Enable verbose output

#### 2. Transform Model (Step 2)

```bash
python3 main.py transform model.json config.json -o transformed_model.json
```

Options:
- `model_file`: Input JSON model file
- `config_file`: Configuration JSON file
- `-o, --output`: Output transformed model file (default: overwrites input)

#### 3. Generate PlantUML (Step 3)

```bash
python3 main.py generate model.json -o ./plantuml_output
```

Options:
- `model_file`: JSON model file
- `-o, --output-dir`: Output directory for PlantUML files (default: ./plantuml_output)

#### 4. Complete Workflow (All Steps)

```bash
python3 main.py workflow ./src config.json
```

Options:
- `project_root`: Root directory of C/C++ project
- `config_file`: Configuration JSON file
- `--recursive/--no-recursive`: Search subdirectories recursively (default: True)

### Configuration File

Create a JSON configuration file for transformation and filtering:

```json
{
  "source_folders": ["./src", "./include"],
  "project_name": "MyProject",
  "output_dir": "./diagrams",
  "recursive": true,
  "include_depth": 2,
  "file_filters": {
    "include": [".*\\.c$", ".*\\.h$"],
    "exclude": [".*test.*", ".*mock.*"]
  },
  "element_filters": {
    "structs": {
      "include": [".*User.*", ".*Config.*"],
      "exclude": [".*Internal.*"]
    },
    "functions": {
      "include": [".*public.*"],
      "exclude": [".*private.*"]
    }
  },
  "transformations": {
    "file_selection": {
      "selected_files": [".*main\\.c$", ".*utils\\.c$"]
    },
    "rename": {
      "structs": {
        "old_name": "new_name"
      }
    },
    "add": {
      "structs": {
        "NewStruct": {
          "fields": [
            {"name": "field1", "type": "int"},
            {"name": "field2", "type": "char*"}
          ]
        }
      }
    }
  }
}
```

## Examples

### Basic Usage

```bash
# Step 1: Parse a C project
python3 main.py parse ./my_project --verbose

# Step 2: Transform the model (optional)
python3 main.py transform model.json config.json

# Step 3: Generate diagrams
python3 main.py generate model.json -o ./diagrams
```

### Advanced Usage with Complete Workflow

```bash
# Create configuration file
cat > config.json << EOF
{
  "source_folders": ["./src"],
  "project_name": "MyLibrary",
  "output_dir": "./docs/diagrams",
  "recursive": true,
  "include_depth": 2,
  "file_filters": {
    "include": [".*\\.c$", ".*\\.h$"],
    "exclude": [".*test.*"]
  }
}
EOF

# Run complete workflow
python3 main.py workflow ./src config.json
```

## Generated PlantUML Output

The tool generates PlantUML diagrams with the following structure:

```plantuml
@startuml filename

class "filename" as FILENAME <<source>> #LightBlue
{
    -- Macros --
    + #define MAX_SIZE
    + #define DEBUG_MODE

    -- Typedefs --
    + typedef int Integer
    + typedef char* String

    -- Global Variables --
    - int global_var
    - float global_float

    -- Functions --
    + int main()
    + int public_function()

    -- Structs --
    + struct Person
        + char name[50]
        + int age

    -- Enums --
    + enum Status
        + OK
        + ERROR

    -- Unions --
    + union Data
        + int int_val
        + float float_val
}

class "stdio" as HEADER_STDIO <<header>> #LightGreen
{
    -- Functions --
    + int printf()
    + int scanf()
}

class "Integer" as TYPEDEF_INTEGER <<typedef>> #LightYellow
{
    + int
}

class "Person" as TYPE_PERSON <<type>> #LightGray
{
    + struct Person
        + char name[50]
        + int age
}

FILENAME --> HEADER_STDIO : <<include>>
TYPEDEF_INTEGER *-- TYPE_PERSON : «defines»

@enduml
```

### Key Features of Generated Diagrams

- **Typedef Relationships**: Proper UML stereotypes («defines», «alias») for typedef relationships
- **Union Support**: Full parsing and display of union definitions with fields
- **Include Depth Processing**: Configurable depth for processing include relationships
- **Header Content Display**: All referenced include files shown as classes with their actual content
- **Header-to-Header Relationships**: Include relationships between headers displayed with arrows
- **Color-Coded Stereotypes**: Different colors for source files, headers, typedefs, and types

## Architecture

The tool is organized into a modular 3-step architecture:

### Core Modules

- **`main.py`**: Command-line interface and entry point
- **`parser.py`**: Step 1 - Parse C/C++ files and generate model.json
- **`transformer.py`**: Step 2 - Transform model based on configuration
- **`generator.py`**: Step 3 - Generate puml files based on model.json
- **`models.py`**: Data models and serialization
- **`config.py`**: Configuration management and filtering

### Key Features

1. **Robust Parsing**: Handles various C/C++ constructs including:
   - Struct definitions with fields
   - Enum definitions with values
   - Union definitions with fields
   - Function declarations
   - Global variable declarations
   - Macro definitions
   - Typedef relationships with proper UML stereotypes
   - Include relationships

2. **Advanced Filtering**: 
   - File-level filtering with regex patterns
   - Element-level filtering for structs, enums, unions, functions, etc.
   - Include depth configuration
   - File selection for transformer actions

3. **Model Transformation**:
   - Element renaming
   - Element addition
   - Element removal
   - Configuration-driven transformations
   - File selection for applying transformations

4. **PlantUML Generation**:
   - Proper UML notation
   - Typedef relationship visualization with stereotypes («defines», «alias»)
   - Header content display
   - Include relationship arrows
   - Color-coded stereotypes
   - Union field display

5. **Cross-Platform Encoding Support**:
   - Automatic detection of file encodings (UTF-8, Windows-1252, Windows-1254, etc.)
   - Platform-aware encoding fallbacks
   - BOM (Byte Order Mark) detection for UTF-8 and UTF-16 files
   - Graceful handling of encoding detection failures
   - Consistent behavior across Windows, Linux, and macOS

## Development

### Project Structure

```
c_to_plantuml/
├── main.py                 # CLI entry point
├── parser.py               # Step 1: Parse C/C++ files
├── transformer.py          # Step 2: Transform model
├── generator.py            # Step 3: Generate PlantUML
├── models.py               # Data models
├── config.py               # Configuration management
└── __init__.py             # Package initialization

tests/
├── unit/                   # Unit tests
│   ├── test_parser.py      # Parser tests
│   ├── test_transformer.py # Transformer tests
│   ├── test_generator.py   # Generator tests
│   ├── test_config.py      # Configuration tests
│   └── test_parser_filtering.py # User configurable filtering tests
├── feature/                # Feature tests
│   ├── test_integration.py # Integration tests
│   ├── test_parser_features.py # Parser feature tests
│   ├── test_generator_features.py # Generator feature tests
│   ├── test_transformer_features.py # Transformer feature tests
│   └── test_project_analysis_features.py # Project analysis tests
└── test_files/             # Test input files
```

### Running Tests

```bash
# Run all tests (recommended)
python run_all_tests.py

# Run with shell script
./test.sh

# Run specific test categories
python -m unittest tests.unit.test_parser
python -m unittest tests.unit.test_generator
python -m unittest tests.feature.test_integration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the 3-step architecture
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 