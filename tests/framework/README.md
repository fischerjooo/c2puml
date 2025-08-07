# C2PUML Test Framework

This directory contains the unified testing framework for C2PUML tests. The framework provides a standardized approach to testing the C2PUML tool through its CLI interface, ensuring consistent, maintainable, and comprehensive test coverage.

## Framework Structure

```
tests/framework/
├── __init__.py              # Package initialization
├── base.py                  # Enhanced base class with high-level methods
├── data_loader.py           # YAML loading and file creation with schema validation
├── executor.py              # CLI execution
├── validators.py            # Individual validator classes for specific validation tasks
├── validators_processor.py  # Coordinates execution of validators from validators.py
└── README.md               # This file
```

## Key Components

### UnifiedTestCase (base.py)
The base class for all tests, providing:
- **High-level convenience methods** for common test patterns
- **Component initialization** for all framework components
- **Test setup and teardown** with proper resource management
- **Enhanced error handling** with context-rich error messages

#### High-Level Methods
```python
def run_test(self, test_id: str) -> TestResult:
    """Run a complete test and return results"""
    
def assert_test_success(self, result: TestResult):
    """Assert test execution was successful"""
    
def validate_test_output(self, result: TestResult):
    """Validate all test outputs using assertions from YAML"""
```

### TestDataLoader (data_loader.py)
Handles loading test data from YAML files and creating temporary files:
- **Multi-document YAML parsing** with `---` separators
- **Schema validation** for test data structure
- **Temporary file creation** in test-specific folders
- **Support for both standard and example tests**

### TestExecutor (executor.py)
Executes C2PUML via CLI interface:
- **CLI-only execution** (no direct API imports)
- **Comprehensive result capture** (stdout, stderr, exit code, timing)
- **Working directory management** for proper file resolution

### Validators (validators.py)
Individual validator classes for specific validation tasks:
- **TestError class** for context-rich error messages
- **CLIValidator** for execution-related assertions
- **OutputValidator** for file existence and content validation
- **ModelValidator** for model.json content validation
- **PlantUMLValidator** for PlantUML diagram validation
- **FileValidator** for general file operations

### ValidatorsProcessor (validators_processor.py)
Coordinates the execution of validators from validators.py:
- **Orchestrates validation process** by delegating to appropriate validators
- **Processes assertions from YAML** using the correct validator for each type
- **Handles execution assertions** using CLIValidator
- **Handles model assertions** using ModelValidator
- **Handles PlantUML assertions** using PlantUMLValidator

## Test Types and Structures

### Standard Tests (Unit, Feature, Integration)
These tests use the complete YAML structure with embedded source files and config:

```yaml
# Test metadata
test:
  name: "Simple C File Parsing"
  description: "Test parsing a simple C file"
  category: "unit"

---
# Source files
source_files:
  simple.c: |
    #include <stdio.h>
    struct Person { char name[50]; int age; };
    int main() { return 0; }

---
# Configuration
config.json: |
  {
    "project_name": "test_parser_simple",
    "source_folders": ["."],
    "output_dir": "../output"
  }

---
# Assertions
assertions:
  execution:
    exit_code: 0
  model:
    files:
      simple.c:
        structs: ["Person"]
        functions: ["main"]
  puml:
    contains_elements: ["Person", "main"]
```

### Example Tests
These tests use external source folders and config files, with YAML containing only assertions:

```yaml
# Example test YAML (assertions only)
assertions:
  execution:
    exit_code: 0
  model:
    files:
      main.c:
        structs: ["ExampleStruct"]
  puml:
    contains_elements: ["ExampleStruct"]
```

## Usage Patterns

### Standard Test Implementation
```python
class TestSimpleCFileParsing(UnifiedTestCase):
    def test_simple_c_file_parsing(self):
        """Test parsing a simple C file through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("simple_c_file_parsing")
        
        # Validate results
        self.assert_test_success(result)
        self.validate_test_output(result)
```

### Example Test Implementation
```python
class TestBasicExample(UnifiedTestCase):
    def test_basic_example(self):
        """Test basic example using external source folder and config"""
        # Load test data from YAML (contains only assertions)
        test_data = self.data_loader.load_test_data("basic_example")
        
        # Get the example directory (where config.json and source/ are located)
        example_dir = os.path.dirname(__file__)
        
        # Execute c2puml with example directory as working directory
        result = self.executor.run_full_pipeline("config.json", example_dir)
        
        # Validate execution
        self.cli_validator.assert_cli_success(result)
        
        # Load output files (output is created in test-specific folder)
        test_dir = os.path.join(example_dir, "test-basic_example")
        output_dir = os.path.join(test_dir, "output")
        model_file = self.output_validator.assert_model_file_exists(output_dir)
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        
        # Load content for validation
        with open(model_file, 'r') as f:
            model_data = json.load(f)
        with open(puml_files[0], 'r') as f:
            puml_content = f.read()
        
        # Process assertions from YAML using ValidatorsProcessor
        self.validators_processor.process_assertions(
            test_data["assertions"], model_data, puml_content, result, self
        )
```

## Key Concepts

### Test Isolation
Each test creates its own temporary folder structure with complete cleanup:
- **setUp()**: Cleans up any existing test-* folders before creating new ones
- **Test Execution**: Creates fresh test-specific folder structure
- **tearDown()**: Preserves output for debugging (no automatic cleanup)

```
tests/unit/test-simple_c_file_parsing/
├── input/
│   ├── config.json
│   └── src/
│       └── simple.c
└── output/
    ├── model.json
    ├── model_transformed.json
    └── simple.puml
```

### Framework Flexibility
The framework supports both standard tests (with embedded data) and example tests (with external files), providing flexibility for different testing scenarios.

### Git Integration
Temporary test folders are automatically ignored by Git, keeping the repository clean while preserving test outputs for debugging.

### Validator Coordination
The ValidatorsProcessor orchestrates the validation process by:
1. **Analyzing YAML assertions** to determine what needs validation
2. **Delegating to appropriate validators** from validators.py
3. **Coordinating the validation flow** to ensure all assertions are processed
4. **Providing consistent error handling** across all validation types

## Error Handling

The framework provides enhanced error handling through the `TestError` class, which includes:
- **Context information** about the test execution
- **Relevant metadata** for debugging
- **Structured error messages** with clear failure reasons

## Schema Validation

The framework validates YAML test data against a defined schema:
- **Required sections**: source_files
- **Optional sections**: model, assertions
- **Type validation**: Ensures correct data types for each section
- **Structure validation**: Validates nested structures and relationships