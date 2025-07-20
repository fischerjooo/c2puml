# C to PlantUML Converter - Component Specification

## 1. High-Level Functional Specification

The C to PlantUML Converter is a Python-based tool that analyzes C/C++ source code projects and generates comprehensive PlantUML class diagrams. The system provides a complete workflow from source code parsing to structured diagram generation with advanced filtering and transformation capabilities.

### Core Functionality
- **Source Code Analysis**: Deep parsing of C/C++ files including structs, enums, unions, functions, macros, typedefs, and global variables
- **Typedef Relationship Analysis**: Comprehensive parsing of typedef relationships with proper UML stereotypes
- **Include Depth Processing**: Configurable depth for processing include relationships and their content
- **Model Generation**: Creates comprehensive JSON-based abstract models of parsed code structures
- **Diagram Generation**: Converts models into PlantUML class diagrams with proper UML notation
- **Advanced Filtering**: Regex-based filtering of files and code elements
- **Model Transformation**: Renaming, filtering, and addition of elements using configuration-driven rules
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

### 2.2 Advanced Requirements
- **R8**: Support regex-based filtering of files and code elements
- **R9**: Enable model transformation with renaming and element addition capabilities
- **R10**: Support multi-configuration file loading and merging
- **R11**: Generate structured output with customizable packaging
- **R12**: Handle encoding issues and provide robust error handling
- **R13**: Parse and visualize unions with their fields
- **R14**: Handle typedefs for struct/enum/union (named and anonymous) with content display
- **R15**: Show relationships between typedefs and their underlying types

### 2.3 Quality Requirements
- **R16**: Maintain backward compatibility with existing configurations
- **R17**: Provide comprehensive error handling and validation
- **R18**: Optimize performance with pre-compiled regex patterns
- **R19**: Support both single-file and batch processing workflows
- **R20**: Comprehensive testing with unit, integration, and output verification tests

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
└── __init__.py             # Package initialization

tests/
├── test_parser.py          # Parser functionality tests
├── test_transformer.py     # Transformer functionality tests
├── test_generator.py       # PlantUML generation tests
├── test_integration.py     # Complete workflow tests
├── test_files/             # Test input files
├── test_output/            # Expected output files
├── test_config.json        # Test configuration
└── run_tests.py           # Test runner script
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
  - C/C++ source code parsing
  - Model assembly and serialization
  - Encoding detection and handling
  - Robust typedef parsing for struct/enum/union (named and anonymous)
  - **Note**: Does NOT perform model element filtering - preserves all elements for transformer

#### 3.2.3 Transformer (`transformer.py`)
- **Purpose**: Step 2 - Transform model based on configuration
- **Responsibilities**:
  - Configuration loading and validation
  - User-configured file filtering (essential filtering already done in parser)
  - Model element filtering (structs, enums, functions, etc.)
  - Model transformation and filtering
  - Include depth processing
  - Element renaming and addition
  - File selection for transformer actions (apply to all files or selected ones)

#### 3.2.4 Generator (`generator.py`)
- **Purpose**: Step 3 - Generate puml files based on model.json
- **Responsibilities**:
  - PlantUML diagram generation
  - Typedef relationship visualization with stereotypes
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
    encoding_used: str
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

### 3.4 Command Interface
The system provides multiple CLI commands for the 3-step workflow:
- `parse`: Step 1 - Parse C projects and generate JSON models
- `transform`: Step 2 - Transform JSON models based on configuration
- `generate`: Step 3 - Convert JSON models to PlantUML diagrams
- `workflow`: Complete workflow (Steps 1-3) using configuration files

## 4. Testing Architecture

### 4.1 Test Organization
All tests are organized under the `tests/` directory with comprehensive coverage:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test complete workflows and component interactions
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
# Run all tests
python tests/run_tests.py

# Run specific test module
python tests/run_tests.py test_parser

# Run with unittest directly
python -m unittest discover tests/
```

## 5. PlantUML Output Specification

### 5.1 Diagram Structure
Each generated PlantUML file follows this structure:

```plantuml
@startuml {basename}

class "{basename}" as {UML_ID} <<source>> #LightBlue
{
    {macros}
    {typedefs}
    {global_variables}
    {functions}
    {structs}
    {enums}
    {unions}
}

' For each included header file with actual content:
class "{header_name}" as {HEADER_UML_ID} <<header>> #LightGreen
{
    -- Macros --
    + #define {macro_name}
    
    -- Typedefs --
    + typedef {original_type} {typedef_name}
    
    -- Global Variables --
    - {type} {variable_name}
    
    -- Functions --
    + {return_type} {function_name}()
    
    -- Structs --
    + struct {struct_name}
        + {type} {field_name}
    
    -- Enums --
    + enum {enum_name}
        + {value}
    
    -- Unions --
    + union {union_name}
        + {type} {field_name}
}

' Typedef classes for struct/enum/union:
class "{typedef_name}" as {TYPEDEF_UML_ID} <<typedef>> #LightYellow
{
    + struct {original_type}
        + {type} {field_name}
}

class "{original_type}" as {TYPE_UML_ID} <<type>> #LightGray
{
    + struct {original_type}
        + {type} {field_name}
}

' Relationships:
{UML_ID} --> {HEADER_UML_ID} : <<include>>
{HEADER_UML_ID} --> {OTHER_HEADER_UML_ID} : <<include>>
{TYPEDEF_UML_ID} *-- {TYPE_UML_ID} : «defines»
{TYPEDEF_UML_ID} -|> {TYPE_UML_ID} : «alias»

@enduml
```

### 5.2 Typedef Relationship Visualization

#### 5.2.1 Typedef Stereotypes
- **«defines»**: Used when a typedef defines a new type (e.g., `typedef struct { ... } MyStruct;`)
- **«alias»**: Used when a typedef creates an alias for an existing type (e.g., `typedef int MyInt;`)

#### 5.2.2 Relationship Notation
- **Defines relationship**: `{typedef} *-- {original_type} : «defines»`
- **Alias relationship**: `{typedef} -|> {original_type} : «alias»`

#### 5.2.3 Typedef Content Display
- **Struct typedefs**: Show struct fields within the typedef class
- **Enum typedefs**: Show enum values within the typedef class
- **Union typedefs**: Show union fields within the typedef class
- **Basic type typedefs**: Show the original type name

### 5.3 Include Depth Configuration

#### 5.3.1 Configuration Parameter
- **`include_depth`**: Controls how deep to process include relationships
- **Default**: 1 (only direct includes)
- **Values**: 1, 2, 3, etc. (recursive depth)

#### 5.3.2 Processing Behavior
- **Depth 1**: Only direct includes are processed
- **Depth 2+**: Includes of includes are also processed and their content is displayed
- **Header relationships**: All header-to-header relationships are shown with arrows

### 5.4 Styling and Formatting

#### 5.4.1 Color Scheme
- **Source files**: `#LightBlue` background, `<<source>>` stereotype
- **Header files**: `#LightGreen` background, `<<header>>` stereotype
- **Typedefs**: `#LightYellow` background, `<<typedef>>` stereotype
- **Types**: `#LightGray` background, `<<type>>` stereotype

#### 5.4.2 Visibility Notation
- **Public members**: `+` prefix
- **Private/Static members**: `-` prefix
- **Macros**: `#define` prefix with `+` visibility

#### 5.4.3 Element Representation
- **Functions**: `{visibility}{return_type} {function_name}()`
- **Global variables**: `{visibility} {type} {variable_name}`
- **Macros**: `{visibility} #define {macro_name}`
- **Struct fields**: `{visibility} {type} {field_name}`
- **Union fields**: `{visibility} {type} {field_name}`
- **Enum values**: `{visibility} {value}`

#### 5.4.4 Relationships
- **Include relationships**: `{source} --> {header} : <<include>>` (arrows only)
- **Header-to-header relationships**: `{header1} --> {header2} : <<include>>`
- **Typedef relationships**: `*--` for «defines», `-|>` for «alias»

### 5.5 Output Organization
- **File naming**: `{basename}.puml` for each .c file (no extension in the name)
- **Directory structure**: Mirrors source project structure
- **Header files**: Shown as classes with full content in diagrams, but do not generate separate .puml files
- **Header relationships**: Include relationships between headers are displayed with arrows
- **Typedef classes**: Separate classes for typedefs with their content and relationships

### 5.6 Configuration-Driven Customization
The output can be customized through JSON configuration:
- File filtering patterns
- Element inclusion/exclusion rules
- Transformation and renaming rules
- Custom element additions
- Output directory structure
- Include depth configuration
- File selection for transformer actions

#### 5.6.1 File Selection for Transformer Actions
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

#### 5.6.2 Filtering Separation
- **Parser Step**: Essential file filtering (hidden files, common exclude patterns)
- **Transformer Step**: User-configured file filtering and model element filtering

**Key Features:**
- **Only .c files generate PlantUML diagrams**: Header files are represented as classes with their full content and arrows, but do not have their own .puml files
- **All referenced include files are shown**: As classes with the `<<header>>` stereotype and their actual content (macros, typedefs, globals, functions, structs, enums, unions)
- **Header-to-header include relationships**: Displayed with arrows
- **No #include lines in class content**: All include relationships are visualized with arrows only
- **Typedef relationships**: Shown with proper UML stereotypes («defines», «alias») and relationship notation
- **Typedef content display**: Struct/enum/union typedefs show their fields/values within the typedef class
- **Union support**: Unions are parsed and displayed with their fields
- **Include depth processing**: Configurable depth for processing include relationships