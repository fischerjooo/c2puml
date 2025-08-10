# C2PUML Test Framework

This directory contains the unified testing framework for C2PUML tests. The framework provides a standardized approach to testing the C2PUML tool through its CLI interface, ensuring consistent, maintainable, and comprehensive test coverage.

## **Important: Test Implementation Priority**

**When creating new tests, ALWAYS try to use the simple pattern first:**

```python
class TestSimpleCFileParsing(UnifiedTestCase):
    """Test parsing a simple C file through the CLI interface"""
    
    def test_simple_c_file_parsing(self):
        """Test parsing a simple C file through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("simple_c_file_parsing")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)
```

**This simple pattern:**
- Uses the base class's high-level methods (`run_test`, `validate_execution_success`, `validate_test_output`)
- Handles all generic assertions through the framework
- Requires only the test name and YAML file
- Minimizes boilerplate code
- Ensures consistent test patterns

**Only use the detailed custom pattern when you need assertions or behavior not supported by the simple pattern.**

## Multi-Scenario Bundles (New)

For large families of scenarios, define multiple scenarios in a single YAML using a `scenarios` array. Reference scenarios via `bundle::scenario`.

- YAML: `tests/<category>/test_<bundle>.yml`
- Python usage:
  - `result = self.run_test("<bundle>::<scenario_id>")`
  - Subsequent validations: `self.validate_execution_success(result)` + `self.validate_test_output(result)`
- Backward compatibility: Single-scenario YAMLs remain supported. If a file contains `scenarios`, a specific scenario id is required.

## **Extending the Framework vs Test-Specific Assertions**

### **Framework Extension Priority**

**When you need new assertions, always consider extending the framework first:**

1. **Check existing validators**: Look in `validators.py` for existing validation methods
2. **Extend ValidatorsProcessor**: Add new assertion types to `validators_processor.py` if they can be reused
3. **Extend Validators**: Add new validation methods to appropriate validator classes in `validators.py`
4. **Update YAML schema**: Add new assertion types to the YAML structure documentation

### **When to Extend the Framework**

**Extend the framework when:**
- The assertion could be useful for multiple tests
- It's a common validation pattern (file content, structure, syntax, etc.)
- It follows existing validation patterns
- It can be expressed in YAML format

**Examples of framework-worthy extensions:**
- New PlantUML validation patterns
- Additional model validation checks
- File content validation methods
- Performance or timing validations
- Error message validation patterns

### **When to Keep Test-Specific**

**Keep assertions test-specific when:**
- The validation is truly unique to one test
- It's testing framework internals (not recommended)
- It requires complex setup that can't be expressed in YAML
- It's a one-off validation that won't be reused

### **Framework Extension Process**

1. **Identify the need**: Determine if the assertion could be reused
2. **Check existing methods**: Look for similar functionality in validators
3. **Extend appropriate validator**: Add method to `ModelValidator`, `PlantUMLValidator`, etc.
4. **Update ValidatorsProcessor**: Add processing logic for new assertion type
5. **Update documentation**: Add new assertion type to YAML schema docs
6. **Update tests**: Use the new framework feature instead of custom code

### **Practical Example: Extending the Framework**

**Scenario**: You need to validate that a PlantUML file contains specific relationship types.

**Step 1: Check existing validators**
```python
# Look in validators.py - PlantUMLValidator class
# Found: assert_puml_contains, assert_puml_contains_lines
# But no specific relationship validation
```

**Step 2: Extend PlantUMLValidator**
```python
# In validators.py - PlantUMLValidator class
def assert_puml_contains_relationship(self, content: str, relationship_type: str, from_class: str, to_class: str) -> None:
    """Assert that PlantUML contains specific relationship"""
    expected = f"{from_class} --> {to_class}"
    if relationship_type == "composition":
        expected = f"{from_class} *-- {to_class}"
    elif relationship_type == "aggregation":
        expected = f"{from_class} o-- {to_class}"
    
    if expected not in content:
        raise AssertionError(f"Expected relationship '{expected}' not found in PlantUML")
```

**Step 3: Extend ValidatorsProcessor**
```python
# In validators_processor.py - _process_puml_assertions method
if "relationships" in puml_assertions:
    for rel in puml_assertions["relationships"]:
        self.puml_validator.assert_puml_contains_relationship(
            puml_content, rel["type"], rel["from"], rel["to"]
        )
```

**Step 4: Update YAML schema documentation**
```yaml
# In tests/README.md - PlantUML Assertions section
relationships:
  - type: "composition"
    from: "ClassA"
    to: "ClassB"
```

**Step 5: Use in tests**
```yaml
# In test YAML file
puml:
  files:
    diagram.puml:
      relationships:
        - type: "composition"
          from: "Person"
          to: "Address"
```

**Result**: The new validation is now available to all tests through the framework!

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
    
def validate_execution_success(self, result: TestResult):
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
        self.validate_execution_success(result)
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