# C to PlantUML Converter - Component Specification

**Current Implementation Status**: ✅ **FULLY IMPLEMENTED AND VERIFIED**  
**Last Updated**: August 2025  
**Version**: 3.1.0 (Production Ready with Advanced Tokenization and Transformation)

This specification reflects the current implementation with all features fully functional and tested, including advanced tokenization, preprocessor handling, model verification capabilities, and comprehensive transformation system. All functionality has been verified through extensive testing with 376 unit tests and integration tests passing.

## 1. High-Level Functional Specification

The C to PlantUML Converter is a Python-based tool that analyzes C/C++ source code projects and generates comprehensive PlantUML class diagrams. The system provides a complete workflow from source code parsing to structured diagram generation with advanced filtering and transformation capabilities, powered by robust tokenization and preprocessor handling.

### Core Functionality
- **Advanced Source Code Analysis**: Deep parsing of C/C++ files using comprehensive tokenization, including structs, enums, unions, functions, macros, typedefs, and global variables
- **Preprocessor Support**: Full handling of conditional compilation directives (#if, #ifdef, #ifndef, #elif, #else, #endif) with macro expansion
- **Robust Tokenization**: Advanced lexical analysis with comprehensive C/C++ token recognition and classification
- **Recursive Search**: Configurable recursive directory search for comprehensive project analysis with encoding detection
- **Typedef Relationship Analysis**: Comprehensive parsing of typedef relationships with proper UML stereotypes («defines», «alias»)
- **Union Support**: Full parsing and visualization of union definitions with fields
- **Include Depth Processing**: Configurable depth for processing include relationships and their content
- **Model Generation**: Creates comprehensive JSON-based abstract models of parsed code structures with validation
- **Model Verification**: Built-in sanity checking and validation of parsed models to ensure accuracy and detect issues
- **Diagram Generation**: Converts models into PlantUML class diagrams with proper UML notation and formatting standards
- **Advanced Filtering**: Regex-based filtering of files and code elements with pattern matching
- **Model Transformation**: Multi-stage renaming, filtering, and addition of elements using configuration-driven rules
- **File Selection for Transformations**: Apply transformations to all files or selected ones with regex patterns
- **Structured Output**: Organized packaging of generated diagrams with customizable structure and artifact management

### Transformation System
The system includes a comprehensive transformation pipeline that allows for sophisticated code model manipulation:

#### Renaming Transformations
- **Function Renaming**: Regex-based function name transformation (e.g., `^deprecated_(.*)` → `legacy_\1`)
- **Typedef Renaming**: Type definition renaming with pattern matching (e.g., `^old_config_t$` → `config_t`)
- **Macro Renaming**: Preprocessor macro renaming (e.g., `^OLD_(.*)` → `LEGACY_\1`)
- **Global Variable Renaming**: Global variable name transformation
- **Struct Renaming**: Structure type renaming with pattern matching
- **Type Reference Updates**: Automatic updating of type references when typedefs are renamed

#### Cleanup Transformations
- **Element Removal**: Remove deprecated or unwanted code elements using regex patterns
- **Function Cleanup**: Remove test functions, debug functions, and deprecated functions
- **Typedef Cleanup**: Remove legacy type definitions
- **Macro Cleanup**: Remove deprecated preprocessor macros
- **Global Variable Cleanup**: Remove old global variables
- **Include Cleanup**: Remove unwanted include relationships
- **Struct/Enum/Union Cleanup**: Remove deprecated data structures

#### File-Specific Configuration
- **Include Depth Control**: Set different include depth limits for specific files
- **Include Filtering**: Apply include filters to specific files only
- **Selective Transformation**: Apply transformations to specific files using regex patterns
- **Configuration Inheritance**: Fallback to global settings when file-specific settings are not defined

#### Transformation Pipeline
- **Multi-Stage Processing**: Support for multiple transformation containers applied in order
- **Backward Compatibility**: Support for legacy transformation format
- **Validation**: Comprehensive validation of transformation patterns and results
- **Logging**: Detailed logging of transformation operations for debugging

### Processing Flow
The application follows a clear 3-step processing flow:

1. **Parse** - Parses C code files and generates model.json (with essential file filtering only)
2. **Transform** - Modifies the model file based on transformation configuration (includes model element filtering and file selection)
3. **Generate** - Generates puml files based on the model.json

All steps can be executed individually or can be chained together.

**Important**: Model element filtering is NOT part of the parsing step - it is only performed in the transformer step to ensure complete model preservation during parsing.

### Functional Verification
The system has been verified to correctly implement all specified functionality:

#### Core Functionality Verification
- ✅ **Parsing**: C/C++ source files parsed correctly with all elements extracted
- ✅ **Transformation**: Renaming and cleanup transformations applied correctly
- ✅ **Include Processing**: File-specific include depth and filtering working properly
- ✅ **Model Generation**: JSON models generated with complete structure information
- ✅ **PlantUML Generation**: Diagrams generated with proper UML notation and relationships

#### Transformation Verification
- **Function Renaming**: `deprecated_print_info` → `legacy_print_info` ✅
- **Typedef Renaming**: `old_config_t` → `config_t` ✅
- **Element Cleanup**: Test functions, debug functions, deprecated macros removed ✅
- **Include Filtering**: File-specific include filters applied correctly ✅
- **Include Depth**: Depth limits respected for all configured files ✅

### Error Handling
The system provides functional error handling for core operations:

#### File Processing
- **Missing Files**: Graceful handling when included files don't exist
- **Encoding Issues**: Automatic detection and handling of UTF-8, ASCII, and BOM encodings
- **Malformed C Code**: Robust parsing that continues processing despite syntax errors

#### Configuration
- **Invalid JSON**: Error messages for malformed configuration files
- **Invalid Regex Patterns**: Warning messages with fallback behavior
- **Missing Configuration**: Sensible defaults when parameters are missing

#### Transformations
- **Pattern Matching Failures**: Non-blocking errors when patterns don't match
- **Circular Dependencies**: Detection and handling of circular include relationships
- **Type Reference Issues**: Automatic cleanup of broken type references after transformations

### File Format Support
The system supports C/C++ file formats and language features:

#### File Extensions
- **Source Files**: `.c`, `.cpp`, `.cc`, `.cxx`
- **Header Files**: `.h`, `.hpp`, `.hh`, `.hxx`

#### Language Standards
- **C**: C89/C90, C99, C11
- **C++**: C++98/03, C++11/14/17 (limited)

#### Preprocessor Support
- **Conditional Compilation**: `#if`, `#ifdef`, `#ifndef`, `#elif`, `#else`, `#endif`
- **Macro Definitions**: `#define`, `#undef`
- **Include Directives**: `#include` with angle brackets and quotes

### Configuration Examples
Functional configuration examples for common use cases:

#### File-Specific Configuration
```json
{
  "file_specific": {
    "sample.c": {
      "include_filter": ["^stdio\\.h$", "^stdlib\\.h$", "^sample\\.h$"],
      "include_depth": 3
    },
    "utils.c": {
      "include_filter": ["^math\\.h$", "^time\\.h$"],
      "include_depth": 2
    }
  }
}
```

#### Transformation Configuration
```json
{
  "transformations_01_rename": {
    "file_selection": [".*transformed\\.(c|h)$"],
    "rename": {
      "typedef": {
        "^old_config_t$": "config_t"
      },
      "functions": {
        "^deprecated_(.*)": "legacy_\\1"
      }
    }
  },
  "transformations_02_cleanup": {
    "file_selection": [".*transformed\\.(c|h)$"],
    "remove": {
      "typedef": ["^legacy_.*", "^old_.*"],
      "functions": ["^test_.*", "^debug_.*"],
      "macros": ["^DEPRECATED_.*", "^LEGACY_.*"]
    }
  }
}
```

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
The system follows a modular architecture with clear separation of concerns and 3 distinct processing steps, now organized into specialized core components:

```
c2puml/
├── main.py                 # CLI entry point and command routing
├── config.py               # Configuration management and input file filtering
├── models.py               # Data models and serialization
├── utils.py                # Utility functions and helpers
├── __init__.py             # Package initialization with backward compatibility
└── core/                   # Core processing modules
    ├── parser.py           # Step 1: Parse C/C++ files and generate model.json
    ├── parser_tokenizer.py # Advanced C/C++ tokenization and lexical analysis
    ├── preprocessor.py     # Preprocessor directive handling and conditional compilation
    ├── transformer.py      # Step 2: Transform model based on configuration
    ├── generator.py        # Step 3: Generate puml files based on model.json
    ├── verifier.py         # Model validation and sanity checking
    └── __init__.py         # Core module exports

tests/
├── unit/                   # Unit tests (18 test files)
│   ├── test_parser.py      # Parser functionality tests
│   ├── test_parser_comprehensive.py # Comprehensive parser tests
│   ├── test_parser_filtering.py # User configurable filtering tests
│   ├── test_tokenizer.py   # Tokenizer functionality tests
│   ├── test_preprocessor_*.py # Preprocessor tests
│   ├── test_transformer.py # Transformer functionality tests
│   ├── test_generator.py   # PlantUML generation tests
│   ├── test_verifier.py    # Model verification tests
│   └── test_config.py      # Configuration tests
├── feature/                # Feature tests (10 test files)
│   ├── test_integration.py # Complete workflow tests
│   ├── test_component_features.py # Component feature tests
│   ├── test_cli_*.py       # CLI feature tests
│   └── test_*_features.py  # Various feature test suites
├── integration/            # Integration tests
└── example/                # Example test data and configuration
    ├── config.json         # Example configuration
    ├── source/             # Example C/C++ source files
    └── test-example.py     # Comprehensive example test suite
```

### 3.2 Core Components

#### 3.2.1 Main Entry Point (`main.py`)
- **Purpose**: CLI interface and command routing
- **Responsibilities**: 
  - Command-line argument parsing
  - Workflow orchestration (Steps 1-3)
  - Error handling and logging setup

#### 3.2.2 Parser (`core/parser.py`)
- **Purpose**: Step 1 - Parse C code files and generate model.json
- **Responsibilities**: 
  - File discovery and essential filtering (hidden files, common exclude patterns)
  - C/C++ source code parsing orchestration with configurable recursive search
  - Model assembly and serialization using advanced tokenization
  - Cross-platform file handling with encoding detection
  - Robust typedef parsing for struct/enum/union (named and anonymous)
  - Include dependency processing with configurable depth
  - Integration with tokenizer, preprocessor, and verifier components
  - **Note**: Does NOT perform model element filtering - preserves all elements for transformer

#### 3.2.3 Tokenizer (`core/parser_tokenizer.py`)
- **Purpose**: Advanced C/C++ lexical analysis and tokenization
- **Responsibilities**:
  - Comprehensive C/C++ token recognition and classification
  - Struct, enum, union, and function parsing with field extraction
  - Complex typedef relationship analysis and resolution
  - String literal and comment handling
  - Operator and punctuation recognition
  - Preprocessor directive tokenization
  - Token stream management and navigation

#### 3.2.4 Preprocessor (`core/preprocessor.py`)
- **Purpose**: Handle preprocessor directives and conditional compilation
- **Responsibilities**:
  - #if, #elif, #else, #endif directive processing
  - #ifdef, #ifndef conditional compilation
  - #define and #undef macro management
  - Macro expansion and substitution
  - Conditional block evaluation and code filtering
  - Nested preprocessor block handling
  - Integration with tokenizer for directive detection

#### 3.2.5 Verifier (`core/verifier.py`)
- **Purpose**: Model validation and sanity checking
- **Responsibilities**:
  - Project model structure validation
  - Field and function parameter validation
  - Type name and identifier validation
  - Include relationship verification
  - Enum value and struct field consistency checking
  - Comprehensive error reporting and issue tracking
  - Post-parsing model quality assurance

#### 3.2.6 Transformer (`core/transformer.py`)
- **Purpose**: Step 2 - Transform model based on configuration
- **Responsibilities**:
  - Configuration loading and validation
  - User-configured file filtering (essential filtering already done in parser)
  - Model element filtering (structs, enums, unions, functions, etc.)
  - Model transformation and filtering with pattern matching
  - Include depth processing and relationship management
  - Element renaming and addition with regex support
  - File selection for transformer actions (apply to all files or selected ones)
  - Multi-stage transformation pipeline support

#### 3.2.7 Generator (`core/generator.py`)
- **Purpose**: Step 3 - Generate puml files based on model.json
- **Responsibilities**:
  - PlantUML diagram generation with proper formatting and styling
  - Typedef relationship visualization with stereotypes («defines», «alias»)
  - Header content display in diagrams with proper UML notation
  - Header-to-header relationship arrows and include tree management
  - Union field display and complex type visualization
  - Enhanced typedef content and relationship display
  - Output file organization and directory structure management
  - PlantUML template compliance and formatting standards

#### 3.2.8 Configuration (`config.py`)
- **Purpose**: Configuration management and input filtering
- **Responsibilities**:
  - Configuration loading and validation with backward compatibility
  - Regex pattern compilation and validation
  - File and element filtering logic with advanced pattern matching
  - Configuration serialization and deserialization
  - File-specific configuration management
  - Recursive search configuration management
  - Multi-stage transformation configuration support

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
  "source_folders": ["tests/example/source"],
  "output_dir": "./output",
  "model_output_path": "model.json",
  "recursive_search": true,
  "include_depth": 3,
  "file_filters": {
    "include": [],
    "exclude": []
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
    },
    "add": {},
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
The system provides a simplified CLI with optional step specification:

```bash
# Full workflow (default) - all three steps
c2puml --config config.json
c2puml  # Uses current directory for configuration

# Individual steps
c2puml --config config.json parse      # Step 1: Parse only
c2puml --config config.json transform  # Step 2: Transform only  
c2puml --config config.json generate   # Step 3: Generate only

# With verbose output
c2puml --config config.json --verbose

# Using config folder (merges all .json files)
c2puml config_folder/
```

**CLI Commands:**
- `parse`: Step 1 - Parse C projects and generate JSON models with advanced tokenization
- `transform`: Step 2 - Transform JSON models based on configuration with filtering and renaming
- `generate`: Step 3 - Convert JSON models to PlantUML diagrams with proper formatting
- **Default (no command)**: Complete workflow (Steps 1-3) using configuration files

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
# Run all tests (recommended) - Main test runners
python scripts/run_all_tests.py
./scripts/run_all_tests.sh        # Linux/macOS
scripts/run_all_tests.bat         # Windows

# Run with coverage
./scripts/run_tests_with_coverage.sh  # Linux/macOS (comprehensive coverage)

# Run example workflow
./scripts/run_example.sh          # Linux/macOS
scripts/run_example.bat           # Windows

# Run specific test categories using pytest
pytest tests/unit/test_parser.py
pytest tests/unit/test_tokenizer.py
pytest tests/unit/test_preprocessor_handling.py
pytest tests/unit/test_verifier.py
pytest tests/feature/test_integration.py
pytest tests/feature/test_component_features.py
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

#### 5.7.1 Transformations Configuration

The transformer supports comprehensive model transformations:

##### Remove Operations
Remove specific elements from the model:

```json
{
  "transformations": {
    "remove": {
      "typedef": ["unwanted_type", "legacy_type"],
      "functions": ["deprecated_func", "internal_helper"],
      "macros": ["DEBUG_MACRO", "TEMP_*"],
      "globals": ["old_global_var"],
      "includes": ["obsolete_header.h"]
    }
  }
}
```

##### Rename Operations  
Rename elements in the model:

```json
{
  "transformations": {
    "rename": {
      "typedef": {
        "old_struct_name": "new_struct_name",
        "legacy_type": "modern_type"
      },
      "functions": {
        "old_func": "new_func",
        "calculate": "compute"
      },
      "macros": {
        "OLD_MACRO": "NEW_MACRO"
      },
      "globals": {
        "old_var": "new_var"
      },
      "includes": {
        "old_header.h": "new_header.h"
      },
      "files": {
        "legacy.c": "modern.c"
      }
    }
  }
}
```

##### File Selection
Apply transformations to specific files only:

```json
{
  "transformations": {
    "file_selection": {
      "selected_files": [".*main\\.c$", ".*utils\\.c$"]
    }
  }
}
```

**Configuration Details:**
- **`remove`**: Arrays of element names/patterns to remove
- **`rename`**: Objects mapping old names to new names
- **`file_selection.selected_files`**: Regex patterns for target files
  - **Empty list or missing**: Applies to all files
  - **Non-empty list**: Applies only to matching files

**Note:** Current implementation provides configuration structure with stub methods for future development.

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

