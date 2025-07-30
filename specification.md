# C to PlantUML Converter - Component Specification

**Current Implementation Status**: ✅ **FULLY IMPLEMENTED**  
**Last Updated**: July 2024  
**Version**: 1.0 (Production Ready)

This specification reflects the current implementation with all features fully functional and tested.

## 1. High-Level Functional Specification

The C to PlantUML Converter is a Python-based tool that analyzes C/C++ source code projects and generates comprehensive PlantUML class diagrams. The system provides a complete workflow from source code parsing to structured diagram generation with advanced filtering and transformation capabilities.

### Core Functionality
- **Source Code Analysis**: Deep parsing of C/C++ files including structs, enums, unions, functions, macros, typedefs, and global variables
- **Recursive Search**: Configurable recursive directory search for comprehensive project analysis
- **Typedef Relationship Analysis**: Comprehensive parsing of typedef relationships with proper UML stereotypes («defines», «alias»)
- **Union Support**: Full parsing and visualization of union definitions with fields
- **Include Depth Processing**: Configurable depth for processing include relationships and their content
- **Model Generation**: Creates comprehensive JSON-based abstract models of parsed code structures
- **Diagram Generation**: Converts models into PlantUML class diagrams with proper UML notation
- **Advanced Filtering**: Regex-based filtering of files and code elements
- **Model Transformation**: Renaming, filtering, and addition of elements using configuration-driven rules
- **File Selection for Transformations**: Apply transformations to all files or selected ones
- **Structured Output**: Organized packaging of generated diagrams with customizable structure

### Processing Flow
The application follows a clear 3-step processing flow:

1. **Parse** - Parses C code files and generates model.json (with essential file filtering only)
2. **Transform** - Modifies the model file based on transformation configuration (includes model element filtering and file selection)
3. **Generate** - Generates puml files based on the model.json

All steps can be executed individually or can be chained together.

**Important**: Model element filtering is NOT part of the parsing step - it is only performed in the transformer step to ensure complete model preservation during parsing.

## 2. High-Level Requirements

### 2.1 Core Requirements
- **R1**: Parse C/C++ source files and extract structural information (structs, enums, unions, functions, macros, globals, typedefs)
- **R2**: Generate comprehensive JSON models representing parsed code structure
- **R3**: Convert JSON models into PlantUML class diagrams with proper UML notation
- **R4**: Support multi-project analysis with configurable project roots
- **R5**: Provide command-line interface with multiple operation modes
- **R6**: Parse and visualize typedef relationships with proper UML stereotypes («defines», «alias»)
- **R7**: Support configurable include depth processing for header relationships
- **R8**: Support configurable recursive search for comprehensive project analysis

### 2.2 Advanced Requirements
- **R9**: Support regex-based filtering of files and code elements
- **R10**: Enable model transformation with renaming and element addition capabilities
- **R11**: Support multi-configuration file loading and merging
- **R12**: Generate structured output with customizable packaging
- **R13**: Provide robust error handling
- **R14**: Parse and visualize unions with their fields
- **R15**: Handle typedefs for struct/enum/union (named and anonymous) with content display
- **R16**: Show relationships between typedefs and their underlying types
- **R17**: Support file selection for transformer actions (apply to all files or selected ones)

### 2.3 Quality Requirements
- **R18**: Provide comprehensive error handling and validation
- **R19**: Optimize performance with pre-compiled regex patterns
- **R20**: Support both single-file and batch processing workflows
- **R21**: Comprehensive testing with unit, integration, and output verification tests

## 3. Software Architecture and Structure

### 3.1 Overall Architecture
The system follows a modular architecture with clear separation of concerns and 3 distinct processing steps:

```
c_to_plantuml/
├── main.py                 # CLI entry point and command routing
├── parser.py               # Step 1: Parse C/C++ files and generate model.json
├── transformer.py          # Step 2: Transform model based on configuration
├── generator.py            # Step 3: Generate puml files based on model.json
├── models.py               # Data models and serialization
├── config.py               # Configuration management and input file filtering
└── __init__.py             # Package initialization

tests/
├── unit/                   # Unit tests
│   ├── test_parser.py      # Parser functionality tests
│   ├── test_transformer.py # Transformer functionality tests
│   ├── test_generator.py   # PlantUML generation tests
│   ├── test_config.py      # Configuration tests
│   └── test_parser_filtering.py # User configurable filtering tests
├── feature/                # Feature tests
│   ├── test_integration.py # Complete workflow tests
│   ├── test_parser_features.py # Parser feature tests
│   ├── test_generator_features.py # Generator feature tests
│   ├── test_transformer_features.py # Transformer feature tests
│   └── test_project_analysis_features.py # Project analysis tests
├── test_files/             # Test input files
└── run_all_tests.py        # Test runner script
```

### 3.2 Core Components

#### 3.2.1 Main Entry Point (`main.py`)
- **Purpose**: CLI interface and command routing
- **Responsibilities**: 
  - Command-line argument parsing
  - Workflow orchestration (Steps 1-3)
  - Error handling and logging setup

#### 3.2.2 Parser (`parser.py`)
- **Purpose**: Step 1 - Parse C code files and generate model.json
- **Responsibilities**: 
  - File discovery and essential filtering (hidden files, common exclude patterns)
  - C/C++ source code parsing with configurable recursive search
  - Model assembly and serialization
  - Cross-platform file handling
  - Robust typedef parsing for struct/enum/union (named and anonymous)
  - Include dependency processing with configurable depth
  - **Note**: Does NOT perform model element filtering - preserves all elements for transformer

#### 3.2.3 Transformer (`transformer.py`)
- **Purpose**: Step 2 - Transform model based on configuration
- **Responsibilities**:
  - Configuration loading and validation
  - User-configured file filtering (essential filtering already done in parser)
  - Model element filtering (structs, enums, unions, functions, etc.)
  - Model transformation and filtering
  - Include depth processing
  - Element renaming and addition
  - File selection for transformer actions (apply to all files or selected ones)

#### 3.2.4 Configuration (`config.py`)
- **Purpose**: Configuration management and input filtering
- **Responsibilities**:
  - Configuration loading and validation
  - Regex pattern compilation and validation
  - File and element filtering logic
  - Configuration serialization and deserialization
  - Backward compatibility handling
  - Recursive search configuration management

#### 3.2.5 Generator (`generator.py`)
- **Purpose**: Step 3 - Generate puml files based on model.json
- **Responsibilities**:
  - PlantUML diagram generation
  - Typedef relationship visualization with stereotypes («defines», «alias»)
  - Header content display in diagrams
  - Header-to-header relationship arrows
  - Union field display
  - Enhanced typedef content and relationship display

### 3.3 Data Models

#### 3.3.1 Project Model (`models.py`)
```python
@dataclass
class ProjectModel:
    project_name: str
    project_root: str
    files: Dict[str, FileModel]
    created_at: str
```

#### 3.3.2 File Model
```python
@dataclass
class FileModel:
    file_path: str
    relative_path: str
    project_root: str
    structs: Dict[str, Struct]
    enums: Dict[str, Enum]
    unions: Dict[str, Union]
    functions: List[Function]
    globals: List[Field]
    includes: List[str]
    macros: List[str]
    typedefs: Dict[str, str]
    typedef_relations: List[TypedefRelation]
    include_relations: List[IncludeRelation]
```

#### 3.3.3 Typedef Relation Model
```python
@dataclass
class TypedefRelation:
    typedef_name: str
    original_type: str
    relationship_type: str  # 'defines' or 'alias'
```

#### 3.3.4 Include Relation Model
```python
@dataclass
class IncludeRelation:
    source_file: str
    included_file: str
    depth: int
```

#### 3.3.5 Union Model
```python
@dataclass
class Union:
    name: str
    fields: List[Field]
```

### 3.4 Configuration Parameters

#### 3.4.1 Core Configuration
The system uses a JSON-based configuration file with the following parameters:

```json
{
  "project_name": "example_project",
  "source_folders": ["example/source"],
  "output_dir": "./output",
  "model_output_path": "model.json",
  "recursive_search": true,
  "include_depth": 3,
  "file_filters": {
    "include": [],
    "exclude": []
  },
  "transformations": {
    "rename": {},
    "add": {},
    "remove": {},
    "file_selection": {
      "selected_files": []
    }
  }
}
```

#### 3.4.2 Configuration Parameters
- **`project_name`**: Name of the project for identification
- **`source_folders`**: List of source directories to analyze
- **`output_dir`**: Output directory for generated files
- **`model_output_path`**: Filename for the generated JSON model
- **`recursive_search`**: Whether to search subdirectories recursively (default: true)
- **`include_depth`**: Depth for processing include relationships (default: 1)
- **`file_filters`**: Regex patterns for including/excluding files

- **`transformations`**: Rules for model transformation and file selection

**Note**: The `recursive_search` parameter was renamed from `recursive` in a recent update for better clarity. The system maintains backward compatibility for configuration loading.

### 3.5 Command Interface
The system provides multiple CLI commands for the 3-step workflow:
- `parse`: Step 1 - Parse C projects and generate JSON models
- `transform`: Step 2 - Transform JSON models based on configuration
- `generate`: Step 3 - Convert JSON models to PlantUML diagrams
- `workflow`: Complete workflow (Steps 1-3) using configuration files

## 4. Testing Architecture

### 4.1 Test Organization
All tests are organized under the `tests/` directory with comprehensive coverage:

- **Unit Tests** (`tests/unit/`): Test individual components in isolation
  - Parser tests
  - Transformer tests
  - Generator tests
  - Configuration tests
  - User configurable filtering tests
- **Feature Tests** (`tests/feature/`): Test complete workflows and integrations
  - Integration tests
  - Parser feature tests
  - Generator feature tests
  - Transformer feature tests
  - Project analysis tests
- **Configuration Tests**: Test configuration loading, validation, and filtering
- **Output Verification Tests**: Test PlantUML generation and output quality
- **Typedef Relationship Tests**: Test typedef parsing and relationship visualization
- **Union Tests**: Test union parsing and field display

### 4.2 Test Categories
- **Parser Tests**: Verify C/C++ parsing accuracy and edge cases
- **Transformer Tests**: Validate model transformation and filtering
- **Generator Tests**: Ensure PlantUML output correctness and formatting
- **Integration Tests**: Test complete workflows from parsing to diagram generation
- **Typedef Tests**: Test typedef relationship parsing and visualization
- **Union Tests**: Test union parsing and content display

### 4.3 Test Execution
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

## 5. PlantUML Output Specification

### 5.1 Diagram Structure
The PlantUML formatting template and all diagram structure rules are now maintained in [puml_template.md](./puml_template.md). Please refer to that file for the up-to-date template, class structure, and relationship grouping rules.

### 5.2 Typedef Relationship Visualization

#### 5.2.1 Typedef Stereotypes
- **«defines»**: Used when a typedef defines a new type (e.g., `typedef struct { ... } MyStruct;`)
- **«alias»**: Used when a typedef creates an alias for an existing type (e.g., `typedef int MyInt;`)

#### 5.2.2 Typedef Filtering in File/Header Classes
- **Primitive typedefs only**: Only typedefs with `relationship_type = "alias"` and `original_type` not starting with "struct", "enum", or "union" are shown in file/header classes
- **Complex typedefs excluded**: Struct, enum, and union typedefs are NOT shown in file/header classes to avoid duplication with their separate typedef classes
- **Typedef classes**: All typedefs (primitive and complex) are shown in separate typedef classes with their content and relationships

#### 5.2.3 Relationship Notation
- **Defines relationship**: `{typedef} *-- {original_type} : «defines»`
- **Alias relationship**: `{typedef} -|> {original_type} : «alias»`

#### 5.2.4 Typedef Content Display
- **Source/Header files**: Show only primitive typedef declarations (e.g., `typedef int MyInt`, `typedef char* String`) - struct/enum/union typedefs are NOT shown in file/header classes
- **Typedef classes**: Show the actual content:
  - **Struct typedefs**: Show struct field names and types (e.g., `+ int x`, `+ char* name`)
  - **Enum typedefs**: Show enum value names (e.g., `+ LOG_DEBUG`, `+ LOG_INFO`, `+ STATE_IDLE`, `+ STATE_RUNNING`)
  - **Union typedefs**: Show union field names and types (e.g., `+ int i`, `+ float f`)
  - **Primitive typedefs**: Show the original type name (e.g., `+ uint32_t`, `+ char*`)

#### 5.2.5 Macro Display
- **Simple defines**: Show only the macro name (e.g., `#define PI`, `#define VERSION`, `#define MAX_LABEL_LEN`)
- **Function-like macros**: Show the macro name with parameters (e.g., `#define MIN(a, b)`, `#define MAX(a, b)`)
- **Macro values are not displayed**: Only the macro name and parameters (if any) are shown, not the actual values or definitions

### 5.3 Include Depth Configuration

#### 5.3.1 Configuration Parameter
- **`include_depth`**: Controls how deep to process include relationships
- **Default**: 1 (only direct includes)
- **Values**: 1, 2, 3, etc. (recursive depth)

#### 5.3.2 Processing Behavior
- **Depth 1**: Only direct includes are processed
- **Depth 2+**: Includes of includes are also processed and their content is displayed
- **Header relationships**: All header-to-header relationships are shown with arrows
- **Recursive search**: When `recursive_search` is true, subdirectories are searched for include files

### 5.4 Recursive Search Configuration

#### 5.4.1 Configuration Parameter
- **`recursive_search`**: Controls whether to search subdirectories recursively for source files
- **Default**: true (search subdirectories)
- **Values**: true/false

#### 5.4.2 Processing Behavior
- **`recursive_search: true`**: Searches all subdirectories recursively for C/C++ files
- **`recursive_search: false`**: Only searches the specified source directories (no subdirectories)
- **File discovery**: Uses `rglob()` for recursive search, `glob()` for non-recursive search
- **Include file resolution**: Recursive search also affects how included files are found in subdirectories

#### 5.4.3 Use Cases
- **Large projects**: Use `recursive_search: true` to analyze entire project hierarchies
- **Focused analysis**: Use `recursive_search: false` to limit analysis to specific directories
- **Performance optimization**: Non-recursive search can be faster for large projects when only specific directories are needed

### 5.5 Styling and Formatting

#### 5.5.1 Color Scheme
- **Source files**: `#LightBlue` background, `<<source>>` stereotype
- **Header files**: `#LightGreen` background, `<<header>>` stereotype
- **Typedefs**: `#LightYellow` background, `<<typedef>>` stereotype
- **Types**: `#LightGray` background, `<<type>>` stereotype

#### 5.5.2 Visibility Notation
- **Source files (C files)**: 
  - Macros: `-` prefix
  - Typedefs: `-` prefix
  - Global variables: No prefix
  - Functions: No prefix
  - Structs: No prefix
  - Enums: No prefix
  - Unions: No prefix
- **Header files**: 
  - All elements: `+` prefix
- **Included typedefs in source files**: `+` prefix (from header files) - only primitive typedefs
- **Macros**: `#define` prefix with appropriate visibility

#### 5.5.3 Element Representation
- **Functions**: `{return_type} {function_name}()` (source) or `+ {return_type} {function_name}()` (header)
- **Global variables**: `{type} {variable_name}` (source) or `+ {type} {variable_name}` (header)
- **Macros**: `- #define {macro_name}` (source) or `+ #define {macro_name}` (header)
- **Primitive Typedefs**: `- typedef {original_type} {typedef_name}` (source) or `+ typedef {original_type} {typedef_name}` (header) - only for primitive type aliases (relationship_type = "alias" and not struct/enum/union)
- **Structs**: `struct {struct_name}` (source) or `+ struct {struct_name}` (header) - only the name
- **Enums**: `enum {enum_name}` (source) or `+ enum {enum_name}` (header) - only the name
- **Unions**: `union {union_name}` (source) or `+ union {union_name}` (header) - only the name
- **Struct fields**: `+ {type} {field_name}` (shown in typedef/type classes only)
- **Union fields**: `+ {type} {field_name}` (shown in typedef/type classes only)
- **Enum values**: `+ {value}` (shown in typedef/type classes only)

#### 5.5.4 Relationships
- **Include relationships**: `{source} --> {header} : <<include>>` (arrows only)
- **Header-to-header relationships**: `{header1} --> {header2} : <<include>>`
- **Typedef relationships**: `*--` for «defines», `-|>` for «alias»

### 5.6 Output Organization
- **File naming**: `{basename}.puml` for each .c file (no extension in the name)
- **Directory structure**: Mirrors source project structure
- **Header files**: Shown as classes with full content in diagrams, but do not generate separate .puml files
- **Header relationships**: Include relationships between headers are displayed with arrows
- **Typedef classes**: Separate classes for typedefs with their content and relationships

### 5.7 Configuration-Driven Customization
The output can be customized through JSON configuration:
- File filtering patterns
- Element inclusion/exclusion rules
- Transformation and renaming rules
- Custom element additions
- Output directory structure
- Include depth configuration
- Recursive search configuration
- File selection for transformer actions

#### 5.7.1 File Selection for Transformer Actions
The transformer supports applying actions to all model files or only selected ones:

```json
{
  "transformations": {
    "file_selection": {
      "selected_files": [".*main\\.c$", ".*utils\\.c$"]
    },
    "rename": {
      "structs": {
        "old_name": "new_name"
      }
    }
  }
}
```

- **`selected_files`**: List of regex patterns for files to apply transformations to
- **Empty list or missing field**: Applies transformations to all files
- **Non-empty list**: Applies transformations only to files matching the patterns

#### 5.7.2 Filtering Separation
- **Parser Step**: Essential file filtering (hidden files, common exclude patterns)
- **Transformer Step**: User-configured file filtering and model element filtering

**Key Features:**
- **Only .c files generate PlantUML diagrams**: Header files are represented as classes with their full content and arrows, but do not have their own .puml files
- **All referenced include files are shown**: As classes with the `<<header>>` stereotype and their actual content (macros, primitive typedefs, globals, functions, structs, enums, unions)
- **Header-to-header include relationships**: Displayed with arrows
- **No #include lines in class content**: All include relationships are visualized with arrows only
- **Typedef relationships**: Shown with proper UML stereotypes («defines», «alias») and relationship notation
- **Typedef content display**: Only primitive typedefs are shown in file/header classes; struct/enum/union typedefs are shown in separate typedef classes with their fields/values
- **Union support**: Unions are parsed and displayed with their fields
- **Include depth processing**: Configurable depth for processing include relationships