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

## 3. Software Architecture and Structure

### 3.1 Overall Architecture
The system follows a modular architecture with clear separation of concerns:

```
c_to_plantuml/
├── main.py                 # CLI entry point and command routing
├── project_analyzer.py     # Project analysis orchestration
├── models/                 # Data models and serialization
│   ├── project_model.py    # Main project model classes
│   └── c_structures.py     # C language structure definitions
├── parsers/                # Source code parsing
│   └── c_parser.py         # C/C++ parser implementation
├── generators/             # Output generation
│   └── plantuml_generator.py # PlantUML diagram generation
├── manipulators/           # Model transformation
│   ├── model_transformer.py # Advanced filtering and transformation
│   └── json_manipulator.py  # JSON model manipulation utilities
└── utils/                  # Utility functions
    └── file_utils.py       # File system utilities
```

### 3.2 Core Components

#### 3.2.1 Project Analyzer (`project_analyzer.py`)
- **Purpose**: Orchestrates the complete analysis workflow
- **Responsibilities**: 
  - File discovery and filtering
  - Parser coordination
  - Model assembly and serialization
  - Configuration integration

#### 3.2.2 C Parser (`parsers/c_parser.py`)
- **Purpose**: Parses C/C++ source code into structured data
- **Capabilities**:
  - Multi-line macro parsing
  - Function declaration extraction
  - Struct and enum parsing
  - Header file resolution
  - Encoding detection and handling

#### 3.2.3 Model Transformer (`manipulators/model_transformer.py`)
- **Purpose**: Advanced model manipulation and filtering
- **Features**:
  - Regex-based file filtering
  - Element-level filtering (structs, enums, functions, globals)
  - Pattern-based transformations and renaming
  - Dynamic element addition
  - Multi-configuration support

#### 3.2.4 PlantUML Generator (`generators/plantuml_generator.py`)
- **Purpose**: Converts JSON models into PlantUML diagrams
- **Output**: Structured PlantUML files with proper UML notation

### 3.3 Data Models

#### 3.3.1 Project Model (`models/project_model.py`)
```python
@dataclass
class ProjectModel:
    project_name: str
    project_roots: List[str]
    files: Dict[str, FileModel]
    global_includes: List[str]
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
- `analyze`: Parse C projects and generate JSON models
- `generate`: Convert JSON models to PlantUML diagrams
- `config`: Run analysis using configuration files
- `filter`: Apply transformations to existing models
- `full`: Complete workflow (analyze + generate)

## 4. PlantUML Output Specification

### 4.1 Diagram Structure
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

### 4.2 Styling and Formatting

#### 4.2.1 Color Scheme
- **Source files**: `#LightBlue` background
- **Header files**: `#LightGreen` background
- **Stereotypes**: `<<source>>`, `<<public_header>>`, `<<private_header>>`

#### 4.2.2 Visibility Notation
- **Public members**: `+` prefix
- **Private/Static members**: `-` prefix
- **Macros**: `#define` prefix with `-` visibility

#### 4.2.3 Element Representation
- **Functions**: `{visibility}{return_type} {function_name}({parameters})`
- **Global variables**: `{visibility} {type} {variable_name}`
- **Macros**: `{visibility} #define {macro_name}`
- **Struct fields**: `{visibility} {type} {field_name}`

#### 4.2.4 Relationships
- **Include relationships**: `{source} --> {header} : <<include>>`
- **Dependency arrows**: Standard PlantUML arrow notation

### 4.3 Output Organization
- **File naming**: `{basename}.puml` for each source file
- **Directory structure**: Mirrors source project structure
- **Packaging**: Optional structured output with custom organization
- **Overview diagrams**: Project-level summary diagrams

### 4.4 Configuration-Driven Customization
The output can be customized through JSON configuration:
- File filtering patterns
- Element inclusion/exclusion rules
- Transformation and renaming rules
- Custom element additions
- Output directory structure

This specification provides a comprehensive overview of the C to PlantUML converter's architecture, requirements, and output format, enabling effective development, maintenance, and extension of the system.