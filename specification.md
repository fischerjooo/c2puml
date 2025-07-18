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
@startuml CLS: {filename}

class "{filename}" as {UML_ID} <<source>> #LightBlue
{
    {global_variables}
    {macros}
    {functions}
}

interface "{header_name}" as {HEADER_UML_ID} <<public_header>> #LightGreen
{
    {header_macros}
    {header_prototypes}
}

{source_class} --> {header_interface} : <<include>>

@enduml
```

### 5.2 Styling and Formatting

#### 5.2.1 Color Scheme
- **Source files**: `#LightBlue` background
- **Header files**: `#LightGreen` background
- **Stereotypes**: `<<source>>`, `<<public_header>>`, `<<private_header>>`

#### 5.2.2 Visibility Notation
- **Public members**: `+` prefix
- **Private/Static members**: `-` prefix
- **Macros**: `#define` prefix with `-` visibility

#### 5.2.3 Element Representation
- **Functions**: `{visibility}{return_type} {function_name}({parameters})`
- **Global variables**: `{visibility} {type} {variable_name}`
- **Macros**: `{visibility} #define {macro_name}`
- **Struct fields**: `{visibility} {type} {field_name}`

#### 5.2.4 Relationships
- **Include relationships**: `{source} --> {header} : <<include>>`
- **Dependency arrows**: Standard PlantUML arrow notation

### 5.3 Output Organization
- **File naming**: `{basename}.puml` for each source file
- **Directory structure**: Mirrors source project structure
- **Packaging**: Optional structured output with custom organization
- **Overview diagrams**: Project-level summary diagrams

### 5.4 Configuration-Driven Customization
The output can be customized through JSON configuration:
- File filtering patterns
- Element inclusion/exclusion rules
- Transformation and renaming rules
- Custom element additions
- Output directory structure

This specification provides a comprehensive overview of the C to PlantUML converter's architecture, requirements, processing flow, and output format, enabling effective development, maintenance, and extension of the system.