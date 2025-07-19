# C to PlantUML Converter - Enhanced Component Specification

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

1. **Parse C/C++ files and generate model** - Extract structural information from source code
2. **Apply configuration/transformers** - Filter and transform the model based on configuration
3. **Generate PlantUML files** - Convert the transformed model into PlantUML diagrams

## 2. Detailed Functional Requirements

### 2.1 Core Requirements

#### R1: C/C++ Source File Parsing
**Description**: Parse C/C++ source files and extract comprehensive structural information
**Behavior**:
- Parse `.c`, `.cpp`, `.h`, `.hpp` files with configurable extensions
- Extract structs, enums, unions, functions, macros, globals, typedefs
- Handle multi-line macros and complex C constructs
- Support nested structs, enums, and unions
- Parse function declarations with parameters and return types
- Extract global variable declarations with types
- Handle typedefs for basic types, structs, enums, and unions
- Support both named and anonymous struct/enum/union typedefs
- Parse include directives and track include relationships
- Handle encoding issues and provide robust error recovery

#### R2: JSON Model Generation
**Description**: Generate comprehensive JSON models representing parsed code structure
**Behavior**:
- Create hierarchical model with project, file, and element levels
- Include metadata (timestamps, encoding, file paths)
- Store all parsed elements with their properties
- Track relationships between elements (typedefs, includes)
- Support model serialization and deserialization
- Maintain backward compatibility with existing model formats

#### R3: PlantUML Diagram Generation
**Description**: Convert JSON models into PlantUML class diagrams with proper UML notation
**Behavior**:
- Generate UML-compliant class diagrams
- Use proper stereotypes and colors for different element types
- Show relationships with appropriate UML notation
- Display element content (fields, methods, values)
- Support custom styling and formatting
- Generate only `.c` files as main diagram files
- Show header files as classes within diagrams
- Display typedef relationships with stereotypes («defines», «alias»)

#### R4: Multi-Project Analysis
**Description**: Support analysis of multiple projects with configurable project roots
**Behavior**:
- Accept multiple project directories
- Merge results into unified model
- Handle project-specific configurations
- Support relative and absolute paths
- Maintain project separation in output

#### R5: Command-Line Interface
**Description**: Provide comprehensive command-line interface with multiple operation modes
**Behavior**:
- Support three main commands: `analyze`, `generate`, `config`
- Provide verbose and quiet modes
- Handle errors gracefully with meaningful messages
- Support configuration file specification
- Allow output customization

#### R6: Typedef Relationship Analysis
**Description**: Parse and visualize typedef relationships with proper UML stereotypes
**Behavior**:
- Distinguish between «defines» and «alias» relationships
- Parse typedefs for structs, enums, unions, and basic types
- Show typedef content within separate classes
- Display relationships with appropriate UML notation
- Handle complex typedef chains and nested typedefs

#### R7: Include Depth Processing
**Description**: Support configurable depth for processing include relationships
**Behavior**:
- Control how deep to process include relationships
- Show header content at specified depth
- Display header-to-header relationships
- Support infinite depth (0) or specific limits
- Optimize performance for large include trees

### 2.2 Advanced Requirements

#### R8: Regex-Based Filtering
**Description**: Support regex-based filtering of files and code elements
**Behavior**:
- Filter files by path patterns
- Filter elements by name patterns
- Support include and exclude patterns
- Apply filters at parsing and generation stages
- Provide case-sensitive and case-insensitive options

#### R9: Model Transformation
**Description**: Enable model transformation with renaming and element addition
**Behavior**:
- Rename elements using pattern matching
- Add custom elements to models
- Transform element properties
- Support conditional transformations
- Maintain transformation history

#### R10: Multi-Configuration Support
**Description**: Support loading and merging multiple configuration files
**Behavior**:
- Load configurations from multiple sources
- Merge configurations with precedence rules
- Validate configuration syntax and semantics
- Support configuration inheritance
- Provide configuration templates

#### R11: Structured Output
**Description**: Generate structured output with customizable packaging
**Behavior**:
- Organize output by project structure
- Support custom output directories
- Generate summary reports
- Create index files for navigation
- Support batch processing

#### R12: Error Handling and Recovery
**Description**: Handle encoding issues and provide robust error handling
**Behavior**:
- Detect and handle various file encodings
- Provide detailed error messages
- Support partial parsing on errors
- Log errors with context information
- Continue processing despite individual file errors

#### R13: Union Support
**Description**: Parse and visualize unions with their fields
**Behavior**:
- Parse union declarations and definitions
- Extract union field information
- Display unions in PlantUML diagrams
- Handle union typedefs
- Show union relationships

#### R14: Typedef Content Display
**Description**: Handle typedefs for struct/enum/union with content display
**Behavior**:
- Show struct fields within typedef classes
- Display enum values within typedef classes
- Show union fields within typedef classes
- Handle anonymous struct/enum/union typedefs
- Support nested typedef content

#### R15: Relationship Visualization
**Description**: Show relationships between typedefs and their underlying types
**Behavior**:
- Display «defines» relationships with composition notation
- Show «alias» relationships with inheritance notation
- Handle complex relationship chains
- Support bidirectional relationship display
- Provide relationship filtering options

### 2.3 Quality Requirements

#### R16: Backward Compatibility
**Description**: Maintain backward compatibility with existing configurations
**Behavior**:
- Support legacy configuration formats
- Maintain API compatibility
- Provide migration tools if needed
- Document breaking changes
- Support version-specific features

#### R17: Comprehensive Error Handling
**Description**: Provide comprehensive error handling and validation
**Behavior**:
- Validate all inputs and configurations
- Provide clear error messages
- Support error recovery strategies
- Log errors with sufficient detail
- Handle edge cases gracefully

#### R18: Performance Optimization
**Description**: Optimize performance with pre-compiled regex patterns
**Behavior**:
- Use pre-compiled regex patterns
- Implement efficient parsing algorithms
- Support incremental processing
- Optimize memory usage
- Provide performance metrics

#### R19: Workflow Support
**Description**: Support both single-file and batch processing workflows
**Behavior**:
- Process individual files efficiently
- Support batch processing of multiple projects
- Provide progress indicators
- Support parallel processing where possible
- Handle large codebases efficiently

#### R20: Comprehensive Testing
**Description**: Comprehensive testing with unit, integration, and output verification tests
**Behavior**:
- Unit tests for all components
- Integration tests for complete workflows
- Output verification tests
- Performance tests
- Regression tests for bug fixes

## 3. Use Case Scenarios

### 3.1 Basic Project Analysis
**Scenario**: Analyze a simple C project with basic structs and functions
**Input**: Single directory with `.c` and `.h` files
**Expected Output**: PlantUML diagram showing all structs, functions, and relationships
**Configuration**: Default settings

### 3.2 Complex Typedef Analysis
**Scenario**: Analyze project with complex typedef relationships
**Input**: Code with typedefs for structs, enums, and unions
**Expected Output**: Separate typedef classes with «defines» and «alias» relationships
**Configuration**: Include depth 2, show all typedefs

### 3.3 Large Codebase Analysis
**Scenario**: Analyze large C codebase with many files and includes
**Input**: Multiple directories with complex include hierarchies
**Expected Output**: Organized diagrams with proper include relationships
**Configuration**: Filtered by specific patterns, include depth 3

### 3.4 Header-Only Library Analysis
**Scenario**: Analyze header-only library with template-like constructs
**Input**: Collection of header files with macros and typedefs
**Expected Output**: Diagrams showing macro definitions and type relationships
**Configuration**: Show macros, include depth 1

### 3.5 Legacy Code Documentation
**Scenario**: Generate documentation for legacy C code
**Input**: Old C codebase with complex structs and unions
**Expected Output**: Clear diagrams showing data structures and relationships
**Configuration**: Focus on structs and unions, hide implementation details

## 4. Software Architecture and Structure

### 4.1 Overall Architecture
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

examples/
├── run_examples.py         # Central script to run all examples
├── basic_project/          # Basic C project example
├── typedef_example/        # Complex typedef example
├── large_codebase/         # Large codebase example
├── header_only/            # Header-only library example
└── legacy_code/            # Legacy code documentation example
```

### 4.2 Core Components

#### 4.2.1 Main Entry Point (`main.py`)
**Purpose**: CLI interface and command routing
**Responsibilities**: 
- Command-line argument parsing and validation
- Workflow orchestration (Steps 1-3)
- Error handling and logging setup
- Exit code management
- Help and usage information

#### 4.2.2 Project Analyzer (`analyzer.py`)
**Purpose**: Orchestrates the complete analysis workflow
**Responsibilities**: 
- File discovery and filtering based on patterns
- Parser coordination and result aggregation
- Model assembly and serialization
- Configuration integration and application
- Include depth processing for header relationships
- Progress tracking and reporting

#### 4.2.3 C Parser (`parser.py`)
**Purpose**: Parses C/C++ source code into structured data
**Capabilities**:
- Multi-line macro parsing with continuation lines
- Function declaration extraction with parameter parsing
- Struct, enum, and union parsing with field extraction
- Typedef relationship extraction with stereotype determination
- Header file resolution and include tracking
- Encoding detection and handling (UTF-8, ASCII, etc.)
- Robust typedef parsing for struct/enum/union (named and anonymous)
- Error recovery and partial parsing support
- Performance optimization with regex compilation

#### 4.2.4 Configuration Handler (`config.py`)
**Purpose**: Configuration loading, validation, and filtering
**Features**:
- JSON configuration file loading with schema validation
- Regex-based file filtering with include/exclude patterns
- Element-level filtering (structs, enums, unions, functions, globals)
- Include depth configuration and validation
- Configuration merging and inheritance
- Transformation rule application
- Error handling and validation reporting

#### 4.2.5 PlantUML Generator (`generator.py`)
**Purpose**: Converts JSON models into PlantUML diagrams
**Output**: Structured PlantUML files with proper UML notation
**Features**:
- Typedef relationship visualization with stereotypes
- Header content display in diagrams with proper formatting
- Header-to-header relationship arrows with depth indication
- Union field display with proper UML notation
- Enhanced typedef content and relationship display
- Custom styling and color schemes
- Output organization and file management

### 4.3 Data Models

#### 4.3.1 Project Model (`models.py`)
```python
@dataclass
class ProjectModel:
    project_name: str
    project_root: str
    files: Dict[str, FileModel]
    created_at: str
    version: str
    metadata: Dict[str, Any]
```

#### 4.3.2 File Model
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
    metadata: Dict[str, Any]
```

#### 4.3.3 Typedef Relation Model
```python
@dataclass
class TypedefRelation:
    typedef_name: str
    original_type: str
    relationship_type: str  # 'defines' or 'alias'
    content: Optional[Dict[str, Any]]  # For struct/enum/union content
    location: str  # File and line information
```

#### 4.3.4 Include Relation Model
```python
@dataclass
class IncludeRelation:
    source_file: str
    included_file: str
    depth: int
    resolved_path: Optional[str]
    is_system_include: bool
```

#### 4.3.5 Union Model
```python
@dataclass
class Union:
    name: str
    fields: List[Field]
    is_anonymous: bool
    location: str
    documentation: Optional[str]
```

### 4.4 Command Interface
The system provides multiple CLI commands:
- `analyze`: Step 1 - Parse C projects and generate JSON models
- `generate`: Step 3 - Convert JSON models to PlantUML diagrams
- `config`: Complete workflow (Steps 1-3) using configuration files

## 5. Testing Architecture

### 5.1 Test Organization
All tests are organized under the `tests/` directory with comprehensive coverage:

- **Unit Tests**: Test individual components in isolation with mocked dependencies
- **Integration Tests**: Test complete workflows and component interactions
- **Configuration Tests**: Test configuration loading, validation, and filtering
- **Output Verification Tests**: Test PlantUML generation and output quality
- **Typedef Relationship Tests**: Test typedef parsing and relationship visualization
- **Union Tests**: Test union parsing and field display
- **Performance Tests**: Test parsing and generation performance
- **Error Handling Tests**: Test error conditions and recovery

### 5.2 Test Categories

#### 5.2.1 Parser Tests
- Verify C/C++ parsing accuracy and edge cases
- Test macro parsing with continuation lines
- Test function parameter parsing
- Test struct/enum/union field extraction
- Test typedef relationship detection
- Test encoding handling and error recovery

#### 5.2.2 Configuration Tests
- Validate configuration loading and schema validation
- Test file filtering with regex patterns
- Test element filtering and transformation
- Test configuration merging and inheritance
- Test error handling for invalid configurations

#### 5.2.3 Generator Tests
- Ensure PlantUML output correctness and formatting
- Test typedef relationship visualization
- Test include relationship display
- Test styling and color schemes
- Test output organization and file structure

#### 5.2.4 Integration Tests
- Test complete workflows from parsing to diagram generation
- Test multi-project analysis
- Test configuration-driven workflows
- Test error handling across components
- Test performance with large codebases

#### 5.2.5 Typedef Tests
- Test typedef relationship parsing and visualization
- Test complex typedef chains
- Test typedef content display
- Test stereotype determination («defines» vs «alias»)

#### 5.2.6 Union Tests
- Test union parsing and content display
- Test union field extraction
- Test union typedefs
- Test union relationships

### 5.3 Test Execution
```bash
# Run all tests
python tests/run_tests.py

# Run specific test module
python tests/run_tests.py test_config

# Run with unittest directly
python -m unittest discover tests/

# Run with coverage
python -m coverage run -m unittest discover tests/
python -m coverage report
```

## 6. PlantUML Output Specification

### 6.1 Diagram Structure
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

### 6.2 Typedef Relationship Visualization

#### 6.2.1 Typedef Stereotypes
- **«defines»**: Used when a typedef defines a new type (e.g., `typedef struct { ... } MyStruct;`)
- **«alias»**: Used when a typedef creates an alias for an existing type (e.g., `typedef int MyInt;`)

#### 6.2.2 Relationship Notation
- **Defines relationship**: `{typedef} *-- {original_type} : «defines»`
- **Alias relationship**: `{typedef} -|> {original_type} : «alias»`

#### 6.2.3 Typedef Content Display
- **Struct typedefs**: Show struct fields within the typedef class
- **Enum typedefs**: Show enum values within the typedef class
- **Union typedefs**: Show union fields within the typedef class
- **Basic type typedefs**: Show the original type name

### 6.3 Include Depth Configuration

#### 6.3.1 Configuration Parameter
- **`include_depth`**: Controls how deep to process include relationships
- **Default**: 1 (only direct includes)
- **Values**: 0 (infinite), 1, 2, 3, etc. (recursive depth)

#### 6.3.2 Processing Behavior
- **Depth 0**: Process all includes recursively (infinite depth)
- **Depth 1**: Only direct includes are processed
- **Depth 2+**: Includes of includes are also processed and their content is displayed
- **Header relationships**: All header-to-header relationships are shown with arrows

### 6.4 Styling and Formatting

#### 6.4.1 Color Scheme
- **Source files**: `#LightBlue` background, `<<source>>` stereotype
- **Header files**: `#LightGreen` background, `<<header>>` stereotype
- **Typedefs**: `#LightYellow` background, `<<typedef>>` stereotype
- **Types**: `#LightGray` background, `<<type>>` stereotype

#### 6.4.2 Visibility Notation
- **Public members**: `+` prefix
- **Private/Static members**: `-` prefix
- **Macros**: `#define` prefix with `+` visibility

#### 6.4.3 Element Representation
- **Functions**: `{visibility}{return_type} {function_name}()`
- **Global variables**: `{visibility} {type} {variable_name}`
- **Macros**: `{visibility} #define {macro_name}`
- **Struct fields**: `{visibility} {type} {field_name}`
- **Union fields**: `{visibility} {type} {field_name}`
- **Enum values**: `{visibility} {value}`

#### 6.4.4 Relationships
- **Include relationships**: `{source} --> {header} : <<include>>` (arrows only)
- **Header-to-header relationships**: `{header1} --> {header2} : <<include>>`
- **Typedef relationships**: `*--` for «defines», `-|>` for «alias»

### 6.5 Output Organization
- **File naming**: `{basename}.puml` for each .c file (no extension in the name)
- **Directory structure**: Mirrors source project structure
- **Header files**: Shown as classes with full content in diagrams, but do not generate separate .puml files
- **Header relationships**: Include relationships between headers are displayed with arrows
- **Typedef classes**: Separate classes for typedefs with their content and relationships

### 6.6 Configuration-Driven Customization
The output can be customized through JSON configuration:
- File filtering patterns with regex support
- Element inclusion/exclusion rules with granular control
- Transformation and renaming rules with pattern matching
- Custom element additions with metadata
- Output directory structure customization
- Include depth configuration with performance considerations

**Key Features:**
- **Only .c files generate PlantUML diagrams**: Header files are represented as classes with their full content and arrows, but do not have their own .puml files
- **All referenced include files are shown**: As classes with the `<<header>>` stereotype and their actual content (macros, typedefs, globals, functions, structs, enums, unions)
- **Header-to-header include relationships**: Displayed with arrows and depth indication
- **No #include lines in class content**: All include relationships are visualized with arrows only
- **Typedef relationships**: Shown with proper UML stereotypes («defines», «alias») and relationship notation
- **Typedef content display**: Struct/enum/union typedefs show their fields/values within the typedef class
- **Union support**: Unions are parsed and displayed with their fields and proper UML notation
- **Include depth processing**: Configurable depth for processing include relationships with performance optimization
- **Error handling**: Robust error handling with partial parsing and recovery
- **Performance optimization**: Pre-compiled regex patterns and efficient algorithms for large codebases