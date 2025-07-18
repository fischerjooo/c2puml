# C to PlantUML Converter - Component Specification

## 1. High-Level Functional Specification

The C to PlantUML Converter is a Python-based tool that analyzes C/C++ source code projects and generates comprehensive PlantUML class diagrams. The system provides a complete workflow from source code parsing to structured diagram generation with advanced filtering and transformation capabilities.

### Core Functionality
- **Source Code Analysis**: Deep parsing of C/C++ files including structs, enums, functions, macros, typedefs, and global variables
- **Model Generation**: Creates comprehensive JSON-based abstract models of parsed code structures
- **Diagram Generation**: Converts models into PlantUML class diagrams with proper UML notation
- **Advanced Filtering**: Regex-based filtering of files and code elements
- **Model Transformation**: Renaming, filtering, and addition of elements using configuration-driven rules
- **Structured Output**: Organized packaging of generated diagrams with customizable structure

### Processing Flow
The application follows a clear 3-step processing flow:

1. **Parse C/C++ files and generate model** - Extract structural information from source code
2. **Apply configuration/transformers** - Filter and transform the model based on configuration
3. **Generate PlantUML files** - Convert the transformed model into PlantUML diagrams

## 2. High-Level Requirements

### 2.1 Core Requirements
- **R1**: Parse C/C++ source files and extract structural information (structs, enums, functions, macros, globals)
- **R2**: Generate comprehensive JSON models representing parsed code structure
- **R3**: Convert JSON models into PlantUML class diagrams with proper UML notation
- **R4**: Support multi-project analysis with configurable project roots
- **R5**: Provide command-line interface with multiple operation modes

### 2.2 Advanced Requirements
- **R6**: Support regex-based filtering of files and code elements
- **R7**: Enable model transformation with renaming and element addition capabilities
- **R8**: Support multi-configuration file loading and merging
- **R9**: Generate structured output with customizable packaging
- **R10**: Handle encoding issues and provide robust error handling

### 2.3 Quality Requirements
- **R11**: Maintain backward compatibility with existing configurations
- **R12**: Provide comprehensive error handling and validation
- **R13**: Optimize performance with pre-compiled regex patterns
- **R14**: Support both single-file and batch processing workflows
- **R15**: Comprehensive testing with unit, integration, and output verification tests

## 3. Software Architecture and Structure

### 3.1 Overall Architecture
The system follows a modular architecture with clear separation of concerns:

```
c_to_plantuml/
├── main.py                 # CLI entry point and command routing
├── analyzer.py             # Project analysis orchestration
├── parser.py               # C/C++ parser implementation
├── generator.py            # PlantUML diagram generation
├── config.py               # Configuration handling and filtering
├── models.py               # Data models and serialization
└── __init__.py             # Package initialization

tests/
├── test_parser.py          # Parser functionality tests
├── test_project_analyzer.py # Project analysis tests
├── test_config.py          # Configuration functionality tests
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

#### 3.2.2 Project Analyzer (`analyzer.py`)
- **Purpose**: Orchestrates the complete analysis workflow
- **Responsibilities**: 
  - File discovery and filtering
  - Parser coordination
  - Model assembly and serialization
  - Configuration integration

#### 3.2.3 C Parser (`parser.py`)
- **Purpose**: Parses C/C++ source code into structured data
- **Capabilities**:
  - Multi-line macro parsing
  - Function declaration extraction
  - Struct and enum parsing
  - Header file resolution
  - Encoding detection and handling

#### 3.2.4 Configuration Handler (`config.py`)
- **Purpose**: Configuration loading, validation, and filtering
- **Features**:
  - JSON configuration file loading
  - Regex-based file filtering
  - Element-level filtering (structs, enums, functions, globals)
  - Configuration validation and error handling

#### 3.2.5 PlantUML Generator (`generator.py`)
- **Purpose**: Converts JSON models into PlantUML diagrams
- **Output**: Structured PlantUML files with proper UML notation

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
    functions: List[Function]
    globals: List[Field]
    includes: List[str]
    macros: List[str]
    typedefs: Dict[str, str]
```

### 3.4 Command Interface
The system provides multiple CLI commands:
- `analyze`: Step 1 - Parse C projects and generate JSON models
- `generate`: Step 3 - Convert JSON models to PlantUML diagrams
- `config`: Complete workflow (Steps 1-3) using configuration files

## 4. Testing Architecture

### 4.1 Test Organization
All tests are organized under the `tests/` directory with comprehensive coverage:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test complete workflows and component interactions
- **Configuration Tests**: Test configuration loading, validation, and filtering
- **Output Verification Tests**: Test PlantUML generation and output quality

### 4.2 Test Categories
- **Parser Tests**: Verify C/C++ parsing accuracy and edge cases
- **Configuration Tests**: Validate configuration loading, filtering, and transformation
- **Generator Tests**: Ensure PlantUML output correctness and formatting
- **Integration Tests**: Test complete workflows from parsing to diagram generation

### 4.3 Test Execution
```bash
# Run all tests
python tests/run_tests.py

# Run specific test module
python tests/run_tests.py test_config

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
}

{UML_ID} --> {HEADER_UML_ID} : <<include>>

' Header-to-header relationships:
{HEADER_UML_ID} --> {OTHER_HEADER_UML_ID} : <<include>>

@enduml
```

- **Header files show their actual content**: Macros, typedefs, global variables, functions, structs, and enums from header files are displayed in the header classes.
- **Header-to-header relationships**: When headers include other headers, these relationships are shown with arrows.
- **Only .c files generate diagrams**: The output filename is `{basename}.puml` (no `.c` extension).
- **Header files do not generate separate diagrams**: They are shown as classes within .c file diagrams.

### 5.2 Styling and Formatting

#### 5.2.1 Color Scheme
- **Source files**: `#LightBlue` background, `<<source>>` stereotype
- **Header files**: `#LightGreen` background, `<<header>>` stereotype
- **Typedefs**: `#LightYellow` background, `<<typedef>>` stereotype
- **Types**: `#LightGray` background, `<<type>>` stereotype

#### 5.2.2 Visibility Notation
- **Public members**: `+` prefix
- **Private/Static members**: `-` prefix
- **Macros**: `#define` prefix with `+` visibility

#### 5.2.3 Element Representation
- **Functions**: `{visibility}{return_type} {function_name}()`
- **Global variables**: `{visibility} {type} {variable_name}`
- **Macros**: `{visibility} #define {macro_name}`
- **Struct fields**: `{visibility} {type} {field_name}`

#### 5.2.4 Relationships
- **Include relationships**: `{source} --> {header} : <<include>>` (arrows only)
- **Header-to-header relationships**: `{header1} --> {header2} : <<include>>`
- **Typedef relationships**: `*--` for «defines», `-|>` for «alias»

### 5.3 Output Organization
- **File naming**: `{basename}.puml` for each .c file (no extension in the name)
- **Directory structure**: Mirrors source project structure
- **Header files**: Shown as classes with full content in diagrams, but do not generate separate .puml files
- **Header relationships**: Include relationships between headers are displayed with arrows

### 5.4 Configuration-Driven Customization
The output can be customized through JSON configuration:
- File filtering patterns
- Element inclusion/exclusion rules
- Transformation and renaming rules
- Custom element additions
- Output directory structure

**Note:**
- Only .c files generate PlantUML diagrams. Header files are represented as classes with their full content and arrows, but do not have their own .puml files.
- All referenced include files are shown as classes with the `<<header>>` stereotype and their actual content (macros, typedefs, globals, functions, structs, enums).
- Header-to-header include relationships are displayed with arrows.
- No #include lines are shown in the class content; all include relationships are visualized with arrows only.