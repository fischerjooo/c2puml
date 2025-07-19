# C to PlantUML Converter

A comprehensive Python tool that analyzes C/C++ source code projects and generates PlantUML class diagrams with advanced filtering and transformation capabilities.

## Features

- **Complete C/C++ Parsing**: Parse structs, enums, unions, functions, macros, globals, and typedefs
- **Typedef Relationship Analysis**: Visualize typedef relationships with proper UML stereotypes («defines», «alias»)
- **Include Depth Processing**: Configurable depth for processing include relationships
- **Advanced Filtering**: Regex-based filtering of files and code elements
- **Model Transformation**: Rename and add elements using configuration-driven rules
- **Robust Error Handling**: Graceful handling of encoding issues and parsing errors
- **Comprehensive Testing**: Extensive unit tests covering all use cases

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd c_to_plantuml

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Basic Usage

```bash
# Analyze a C project and generate PlantUML diagrams
python -m c_to_plantuml config config.json

# Or use the step-by-step approach
python -m c_to_plantuml analyze ./src
python -m c_to_plantuml generate project_model.json
```

### Configuration Example

```json
{
  "project_name": "my_project",
  "project_root": "./src",
  "output_directory": "./output",
  "include_depth": 2,
  "file_patterns": {
    "include": ["*.c", "*.h"],
    "exclude": ["*_test.c"]
  },
  "element_filters": {
    "structs": {
      "include": [],
      "exclude": ["*_internal"]
    }
  }
}
```

## Examples

The project includes comprehensive examples demonstrating various use cases:

### Basic Project Example
- Simple C project with structs, functions, and includes
- Shows basic PlantUML generation

### Complex Typedef Example
- Demonstrates typedef relationships and stereotypes
- Shows «defines» vs «alias» relationships

### Large Codebase Example
- Multi-module project with complex include hierarchies
- Performance testing and organization

### Header-Only Library Example
- Template-like constructs and macros
- Header file analysis

### Legacy Code Example
- Complex structs and unions
- Documentation generation

Run all examples:
```bash
cd examples
python run_examples.py
```

## Testing

The project includes comprehensive unit tests covering:

- **Use Case Tests**: Real-world scenarios and behavioral testing
- **Parser Tests**: C/C++ parsing accuracy and edge cases
- **Configuration Tests**: Filtering and transformation validation
- **Generator Tests**: PlantUML output verification
- **Integration Tests**: Complete workflow testing
- **Error Handling Tests**: Robust error recovery

Run tests:
```bash
# Run all tests
python -m unittest discover tests/

# Run specific test categories
python -m unittest tests.test_use_cases
python -m unittest tests.test_parser
python -m unittest tests.test_generator
```

## Architecture

The system follows a clear 3-step processing flow:

1. **Parse C/C++ files and generate model** - Extract structural information
2. **Apply configuration/transformers** - Filter and transform the model
3. **Generate PlantUML files** - Convert to UML diagrams

### Core Components

- **Parser**: C/C++ source code parsing with error recovery
- **Analyzer**: Project orchestration and model assembly
- **Generator**: PlantUML diagram generation with styling
- **Config**: Configuration management and filtering
- **Models**: Data structures for project representation

## Output Format

Generated PlantUML diagrams include:

- **Source Classes**: Main .c files with all elements
- **Header Classes**: Included .h files with full content
- **Typedef Classes**: Separate classes for typedef relationships
- **Include Relationships**: Arrows showing file dependencies
- **UML Stereotypes**: Proper notation for different element types

## Configuration Options

- **File Filtering**: Include/exclude patterns for files
- **Element Filtering**: Filter structs, enums, functions, etc.
- **Include Depth**: Control how deep to process includes
- **Output Organization**: Customize output directory structure
- **Transformation Rules**: Rename and add elements

## Contributing

1. Follow the development workflow in `workflow.md`
2. Add comprehensive tests for new features
3. Update documentation and examples
4. Ensure all tests pass before submitting

## License

[Add your license information here] 