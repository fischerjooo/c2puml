# C2PUML Test Refactoring - Recommendations

## Overview

This document provides detailed recommendations and guidance for test developers working with the new unified testing framework. It includes practical examples, best practices, and step-by-step instructions for creating and maintaining tests.

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

## New Unified Testing Approach

### Core Concept
The new framework uses **single YAML files with multiple documents** to define complete test scenarios. Each test file contains all necessary data: source files, configuration, and assertions, making tests self-contained and easy to understand.

**Note**: Example tests have a special structure that uses external source folders and config files, with YAML containing only assertions.

### Test Types and YAML Structures

#### **Standard Tests** (Unit, Feature, Integration)
These tests use the complete YAML structure with embedded source files and config:

```yaml
# Test metadata
test:
  name: "Simple C File Parsing"
  description: "Test parsing a simple C file with struct, enum, function, global, and include"
  category: "unit"
  id: "0001"

---
# Source files
source_files:
  simple.c: |
    #include <stdio.h>
    
    struct Person {
        char name[50];
        int age;
    };
    
    enum Status {
        OK,
        ERROR
    };
    
    int main() {
        return 0;
    }
    
    int global_var;

---
# Configuration
config.json: |
  {
    "project_name": "test_parser_simple",
    "source_folders": ["."],
    "output_dir": "./output",
    "recursive_search": true,
    "include_patterns": ["*.c", "*.h"],
    "exclude_patterns": ["*_test.c"]
  }

---
# Model template (optional)
model.json: |
  {
    "files": {
      "simple.c": {
        "structs": {
          "Person": {
            "fields": ["name", "age"]
          }
        },
        "enums": {
          "Status": {
            "values": ["OK", "ERROR"]
          }
        },
        "functions": ["main"],
        "globals": ["global_var"],
        "includes": ["stdio.h"]
      }
    },
    "element_counts": {
      "structs": 1,
      "enums": 1,
      "functions": 1,
      "globals": 1,
      "includes": 1
    }
  }

---
# Assertions
assertions:
  execution:
    exit_code: 0
    output_files: ["model.json", "model_transformed.json", "simple.puml"]
    stdout_contains: "Parsing complete"
    max_execution_time: 30.0
  
  model:
    files:
      simple.c:
        structs:
          Person:
            fields: ["name", "age"]
        enums:
          Status:
            values: ["OK", "ERROR"]
        functions: ["main"]
        globals: ["global_var"]
        includes: ["stdio.h"]
    element_counts:
      structs: 1
      enums: 1
      functions: 1
      globals: 1
      includes: 1
  
  puml:
    # Global PlantUML assertions (applied to all files)
    syntax_valid: true
    
    # Per-file PlantUML assertions
    files:
      simple.puml:
        contains_elements: ["Person", "Status", "main", "global_var"]
        contains_lines: ["class \"Person\" as TYPEDEF_PERSON", "int main()"]
        class_count: 3
        relationship_count: 2
        classes:
          Person:
            fields: ["name", "age"]
        relationships:
          - type: "composition"
            from: "main"
            to: "Person"
```

#### **Example Tests** (Special Structure)
Example tests use external source folders and config files, with YAML containing ONLY assertions:

```yaml
# Test metadata
test:
  name: "Basic Example"
  description: "Test basic example with external source folder and config"
  category: "example"
  id: "3001"

---
# Assertions only (no source_files or config.json sections)
assertions:
  execution:
    exit_code: 0
    output_files: ["model.json", "model_transformed.json", "example.puml"]
    stdout_contains: "Parsing complete"
    max_execution_time: 30.0
  
  model:
    files:
      main.c:
        structs:
          ExampleStruct:
            fields: ["value", "name"]
        functions: ["main", "helper_function"]
        includes: ["header.h"]
    element_counts:
      structs: 1
      functions: 2
      includes: 1
  
  puml:
    # Global PlantUML assertions (applied to all files)
    syntax_valid: true
    
    # Per-file PlantUML assertions
    files:
      example.puml:
        contains_elements: ["ExampleStruct", "main", "helper_function"]
        contains_lines: ["class \"ExampleStruct\" as TYPEDEF_EXAMPLESTRUCT", "int main()"]
        class_count: 3
        relationship_count: 1
        classes:
          ExampleStruct:
            fields: ["value", "name"]
        relationships:
          - type: "composition"
            from: "main"
            to: "ExampleStruct"
```

### Test Category Determination
The framework automatically determines test categories based on:
- **Test ID**: Numeric ranges (0001-1000: unit, 1001-2000: feature, 2001-3000: integration, 3001-4000: example)
- **Test Name**: Pattern matching (starts with "test_example_": example, contains "feature"/"integration": feature)

### Assertion Types and Structure
The framework supports comprehensive validation through three main assertion types:

#### Execution Assertions
- `exit_code`: Expected CLI exit code (0 for success)
- `output_files`: List of expected output files
- `stdout_contains`: Text that must appear in stdout
- `stderr_contains`: Text that must appear in stderr
- `max_execution_time`: Maximum allowed execution time in seconds

#### Model Assertions
- `files`: Per-file model validation
  - `structs`: Expected struct definitions with fields
  - `enums`: Expected enum definitions with values
  - `functions`: Expected function names
  - `globals`: Expected global variable names
  - `includes`: Expected include statements
- `element_counts`: Expected counts of different element types across all files

#### PlantUML Assertions
- `syntax_valid`: Global syntax validation for all PlantUML files
- `files`: Per-file PlantUML validation
  - `contains_elements`: Elements that must appear in the diagram
  - `contains_lines`: Specific lines that must appear
  - `class_count`: Expected number of classes
  - `relationship_count`: Expected number of relationships
  - `classes`: Detailed class structure validation
  - `relationships`: Specific relationship validation

### Test Folder Structures

#### **Standard Tests** (Unit, Feature, Integration):
```
tests/unit/
├── test_simple_c_file_parsing.py
├── test_simple_c_file_parsing.yml
└── test-simple_c_file_parsing/          # Generated during test execution
    ├── input/
    │   ├── config.json
    │   └── simple.c
    └── output/
        ├── model.json
        ├── model_transformed.json
        └── simple.puml
```

#### **Example Tests**:
```
tests/example/
├── test_basic_example.py
├── test_basic_example.yml           # Contains ONLY assertions
├── config.json                      # External config file (tracked by git)
└── source/                          # External source folder (tracked by git)
    ├── main.c
    ├── header.h
    └── other_files.c
```

**Key Differences**:
- **Standard Tests**: Create temporary input files from YAML content
- **Example Tests**: Use external config.json and source/ folder (no temp input files)
- **Standard Tests**: YAML contains source_files and config.json sections
- **Example Tests**: YAML contains only test metadata and assertions

## Framework Components

### TestDataLoader
**Purpose**: Load and parse multi-document YAML test files
**Key Methods**:
- `load_test_data(test_id)`: Load test data from YAML file
- `create_temp_files(test_data, test_id)`: Create temporary files for testing
- `_parse_yaml_documents(documents)`: Parse multiple YAML documents

**Features**:
- Multi-document YAML parsing
- **Standard Tests**: Temporary file creation from YAML content
- **Example Tests**: Uses external config.json and source/ folder (no temp files)
- Meaningful test ID support
- **Temp Management**:
  - Standard tests: `tests/*/test-<id>/` with input/ and output/ folders
  - Example tests: `tests/example/test-<id>/` with output/ folder only

**Example Usage**:
```python
# Load test data
test_data = self.data_loader.load_test_data("simple_c_file_parsing")

# Create temporary files (standard tests)
source_dir, config_path = self.data_loader.create_temp_files(test_data, "simple_c_file_parsing")

# For example tests, no temp files are created - use external files
```

### ValidatorsProcessor
**Purpose**: Process assertions from YAML data
**Key Methods**:
- `process_assertions(assertions, model_data, puml_content, result, test_case)`: Process all assertions

**Features**:
- Model validation
- PlantUML validation
- Execution validation
- Comprehensive error reporting

**Example Usage**:
```python
# Process assertions from YAML
self.assertion_processor.process_assertions(
    test_data["assertions"], model_data, puml_content, result, self
)
```

### TestExecutor
**Purpose**: Execute c2puml via CLI interface only
**Key Methods**:
- `run_full_pipeline(config_path, working_dir)`: Run complete pipeline
- `run_parse_only(config_path, working_dir)`: Run parse step only
- `run_transform_only(config_path, working_dir)`: Run transform step only
- `run_generate_only(config_path, working_dir)`: Run generate step only

**Features**:
- CLI-only execution
- No internal API access
- **Working Directory Management**:
  - Standard tests: Uses temp input directory as working directory
  - Example tests: Uses example directory (where config.json is located)
- Error handling and timeout support

**Example Usage**:
```python
# Standard tests: Execute with temp directory as working directory
result = self.executor.run_full_pipeline(config_filename, temp_dir)

# Example tests: Execute with example directory as working directory
result = self.executor.run_full_pipeline("config.json", example_dir)
```

### Validators
**ModelValidator**: Validates model.json structure and content
**PlantUMLValidator**: Validates .puml file syntax and content
**OutputValidator**: Validates file existence and structure
**FileValidator**: Validates file system operations

### UnifiedTestCase
**Purpose**: Base class for all tests
**Features**:
- Automatic component initialization
- Complete cleanup of existing test folders in setUp()
- Common setup/teardown with output preservation
- Utility methods for assertions
- Standardized test output management

## Test Implementation Pattern

### **Recommended: Simple Test Pattern (Reuse When Possible)**

**Always try to use this simple pattern first - it covers most test scenarios:**

```python
#!/usr/bin/env python3
"""
Test Simple C File Parsing
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestSimpleCFileParsing(UnifiedTestCase):
    """Test parsing a simple C file through the CLI interface"""
    
    def test_simple_c_file_parsing(self):
        """Test parsing a simple C file through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("simple_c_file_parsing")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
```

**This pattern:**
- Uses the base class's high-level methods (`run_test`, `validate_execution_success`, `validate_test_output`)
- Handles all generic assertions through the framework
- Requires only the test name and YAML file
- Minimizes boilerplate code
- Ensures consistent test patterns

### **Custom Test Pattern (Use Only When Needed)**

Only use this detailed pattern when you need custom assertions or special handling that cannot be covered by the simple pattern:

```python
#!/usr/bin/env python3
"""
Custom Test Implementation (Use only when simple pattern is insufficient)
"""

import os
import sys
import unittest
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestCustomImplementation(UnifiedTestCase):
    """Custom test with specific assertions"""

    def test_custom_implementation(self):
        """Test with custom assertions not covered by framework"""
        # Load test data from YAML
        test_data = self.data_loader.load_test_data("custom_test")
        
        # Create temporary files
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "custom_test")
        
        # Get the temp directory (parent of source_dir)
        temp_dir = os.path.dirname(source_dir)
        
        # Make config path relative to working directory
        config_filename = os.path.basename(config_path)
        
        # Execute c2puml with temp directory as working directory
        result = self.executor.run_full_pipeline(config_filename, temp_dir)
        
        # Validate execution
        self.validate_execution_success(result)
        
        # Load output files
        output_dir = os.path.join(temp_dir, "output")
        model_file = os.path.join(output_dir, "model.json")
        puml_files = self.assert_puml_files_exist(output_dir)
        
        # Load content for validation
        with open(model_file, 'r') as f:
            model_data = json.load(f)
        
        # Load all PlantUML files into a dictionary
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files_dict[filename] = puml_content = f.read()
        
        # Process assertions from YAML
        self.validators_processor.process_assertions(
            test_data["assertions"], model_data, puml_files_dict, result, self
        )
        
        # **ADD CUSTOM ASSERTIONS HERE ONLY IF NEEDED**
        # Example: Custom validation not covered by YAML assertions
        # self.assert_something_specific(model_data)
        
        # **IMPORTANT**: Before adding custom assertions, consider:
        # 1. Could this assertion be useful for other tests?
        # 2. Can it be expressed in YAML format?
        # 3. Should it be added to the framework instead?
        # 4. Check existing validators in validators.py first


if __name__ == "__main__":
    unittest.main()
```

**Use custom pattern only when:**
- You need assertions not supported by the YAML framework
- You need special setup/teardown logic
- You need to modify test behavior based on runtime conditions
- You need to test framework internals (not recommended)

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

### **Example Test Structure (Special Case)**

**For example tests, use this pattern which leverages external files:**

```python
#!/usr/bin/env python3
"""
Example test for Basic Example
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestBasicExample(UnifiedTestCase):
    """Test Basic Example with External Source Files"""

    def test_basic_example(self):
        """Test basic example using external source folder and config"""
        # Run the complete test using high-level methods
        result = self.run_test("basic_example")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
```

**Key Differences for Example Tests**:
1. **No temp file creation**: Uses external config.json and source/ folder
2. **Working directory**: Uses example directory where config.json is located
3. **YAML content**: Contains only test metadata and assertions
4. **Output location**: Generated in test-specific output folder
5. **External files**: config.json and source/ folder are tracked by git
6. **Same simple pattern**: Uses the same high-level methods as standard tests

## Migration Strategy

### Phase 1: Foundation ✅
- Framework components implemented
- Multi-document YAML support
- Test-specific temp folders
- Git integration

### Phase 2: Pilot ✅
- First test converted and validated
- Framework patterns established
- Documentation completed

### Phase 3: Systematic Migration
- Convert unit tests (001-050)
- Convert feature tests (101-150)
- Convert integration tests (201-250)
- Convert example tests (301-350)

### Phase 4: Cleanup
- Remove old framework files
- Update .gitignore
- Clean up dependencies

## Benefits of YAML Approach

1. **Clear Separation**: Each document has a specific purpose and is clearly separated
2. **Readability**: Easy to read and understand each section independently
3. **Maintainability**: Easy to modify specific sections without affecting others
4. **Flexibility**: Optional sections (like model templates) can be included as needed
5. **Natural Formats**: Each section uses its most natural format (JSON for config, YAML for assertions)
6. **Version Control**: Clear diffs when individual sections change
7. **Meaningful Names**: Test files have descriptive names that explain their purpose
8. **Direct JSON**: Config and model files are included as direct JSON text for better readability
9. **Test Isolation**: Each test has its own temp folder for complete isolation
10. **Git Integration**: Temp folders are properly ignored, keeping repository clean

## Test Naming Convention

- **Unit Tests**: test_simple_c_file_parsing.py, test_complex_struct_parsing.py, etc.
- **Feature Tests**: test_multi_file_project.py, test_recursive_search.py, etc.
- **Integration Tests**: test_end_to_end_pipeline.py, test_error_handling.py, etc.
- **Example Tests**: test_basic_example.py, test_advanced_example.py, etc.

## YAML File Naming Convention

- **Unit Tests**: test_simple_c_file_parsing.yml, test_complex_struct_parsing.yml, etc.
- **Feature Tests**: test_multi_file_project.yml, test_recursive_search.yml, etc.
- **Integration Tests**: test_end_to_end_pipeline.yml, test_error_handling.yml, etc.
- **Example Tests**: test_basic_example.yml, test_advanced_example.yml, etc.

## Migration Guidelines

### Converting Existing Tests

1. **Extract test metadata**: Create test section with name, description, category, id
2. **Extract source files**: Move C code to source_files document
3. **Extract config**: Move config to config.json document as direct JSON
4. **Extract model template** (optional): Create model.json document for complex validation
5. **Extract assertions**: Move assertions to assertions document
6. **Create YAML file**: Create test_<meaningful_name>.yml with all documents
7. **Update test file**: Convert to use TestDataLoader and ValidatorsProcessor
8. **Verify functionality**: Ensure test still validates the same functionality

### YAML Best Practices

1. **Use meaningful test names**: Descriptive test names that explain functionality
2. **Separate documents clearly**: Use `---` to separate different sections
3. **Add comments**: Use comments to describe each document's purpose
4. **Use consistent formatting**: Follow YAML formatting standards
5. **Keep documents focused**: Each document should have a single purpose
6. **Direct JSON for config/model**: Include JSON files as direct text for readability
7. **Optional sections**: Only include model templates when needed for complex validation

## Git Integration

### Ignored Files
- `tests/*/temp/` - All temporary test folders
- `tests/*/output/` - Test output directories
- `tests/*/assert-*.json` - Old assertion files (no longer used)
- `tests/*/input-*.json` - Old input files (no longer used)

### Tracked Files
- `tests/*/test_*.yml` - YAML test data files
- `tests/*/test_*.py` - Test implementation files

## Example Implementation

The first test demonstrates this new approach:

- **test_simple_c_file_parsing.py**: Simple test implementation using the framework
- **test_simple_c_file_parsing.yml**: Contains all test data and assertions in multiple documents
- **temp/test_simple_c_file_parsing/**: Temporary files created during test execution (git ignored)

This new approach makes the testing framework much more maintainable and easier to understand while providing all the benefits of data-driven testing with clear separation of concerns and proper git integration.