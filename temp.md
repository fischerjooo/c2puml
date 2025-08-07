# Test Refactoring: New YAML-Based Unified Testing Framework

This document describes the new unified testing framework approach using YAML files for test data and assertions.

## Overview

The new unified testing framework uses a **single YAML file per test** that contains both inputs and assertions, making the testing approach much simpler and more maintainable.

## New Test Structure

### File Structure
```
tests/
├── unit/
│   ├── test_simple_c_file_parsing.py    # Test implementation
│   ├── test_simple_c_file_parsing.yml   # Test data and assertions
│   ├── test_complex_struct_parsing.py
│   ├── test_complex_struct_parsing.yml
│   └── ...
├── feature/
│   ├── test_multi_file_project.py
│   ├── test_multi_file_project.yml
│   └── ...
├── integration/
│   ├── test_end_to_end_pipeline.py
│   ├── test_end_to_end_pipeline.yml
│   └── ...
└── example/
    ├── test_basic_example.py
    ├── test_basic_example.yml
    └── ...
```

### YAML File Structure
Each `test_<meaningful_name>.yml` file contains:

```yaml
test:
  name: "Simple C File Parsing"
  description: "Test parsing a simple C file with struct, enum, function, global, and include"
  category: "unit"
  id: "001"

inputs:
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

    config.json: |
      {
        "project_name": "test_parser_simple",
        "source_folders": ["."],
        "output_dir": "./output",
        "recursive_search": true
      }

assertions:
  execution:
    exit_code: 0
    output_files: ["model.json", "model_transformed.json", "simple.puml"]
  
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
    contains_elements: ["Person", "Status", "main"]
    syntax_valid: true
```

## Framework Components

### 1. TestDataLoader
- **Purpose**: Load and parse YAML test files
- **Methods**: `load_test_data(test_id)`, `create_temp_files(test_data)`
- **Features**: YAML parsing, temporary file creation, meaningful test ID support

### 2. AssertionProcessor
- **Purpose**: Process assertions from YAML data
- **Methods**: `process_assertions(assertions, model_data, puml_content, result, test_case)`
- **Features**: Model validation, PlantUML validation, execution validation

### 3. TestExecutor
- **Purpose**: Execute c2puml via CLI interface
- **Methods**: `run_full_pipeline(config_path, working_dir)`
- **Interface**: CLI-only, no internal API access

### 4. Validators
- **ModelValidator**: Validate model.json content
- **PlantUMLValidator**: Validate .puml file content
- **OutputValidator**: Validate file existence and structure

### 5. UnifiedTestCase
- **Purpose**: Base class for all tests
- **Features**: Setup/teardown, component initialization, basic utilities

## Test Implementation Pattern

### Standard Test Structure
```python
#!/usr/bin/env python3
"""
Unit test for Simple C File Parsing
"""

import os
import sys
import unittest
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.framework import UnifiedTestCase


class TestSimpleCFileParsing(UnifiedTestCase):
    """Test Simple C File Parsing"""

    def test_simple_c_file_parsing(self):
        """Test parsing a simple C file through the CLI interface"""
        # Load test data from YAML
        test_data = self.data_loader.load_test_data("simple_c_file_parsing")
        
        # Create temporary files
        source_dir, config_path = self.data_loader.create_temp_files(test_data)
        
        # Execute c2puml
        result = self.executor.run_full_pipeline(config_path, source_dir)
        
        # Validate execution
        self.assert_c2puml_success(result)
        
        # Load output files
        output_dir = os.path.join(source_dir, "output")
        model_file = os.path.join(output_dir, "model.json")
        puml_files = self.assert_puml_files_exist(output_dir)
        
        # Load content for validation
        with open(model_file, 'r') as f:
            model_data = json.load(f)
        
        with open(puml_files[0], 'r') as f:
            puml_content = f.read()
        
        # Process assertions from YAML
        self.assertion_processor.process_assertions(
            test_data["assertions"], model_data, puml_content, result, self
        )


if __name__ == "__main__":
    unittest.main()
```

## Benefits of YAML Approach

1. **Simplicity**: Single file contains both inputs and assertions
2. **Readability**: YAML is human-readable and self-documenting
3. **Maintainability**: Easy to modify test data without touching code
4. **Standardization**: All tests follow the same structure
5. **Version Control**: YAML files are easily tracked and diffed
6. **Flexibility**: Easy to add new test scenarios
7. **Meaningful Names**: Test files have descriptive names that explain their purpose
8. **Direct JSON**: Config files are included as direct JSON text for better readability

## Test Naming Convention

- **Unit Tests**: test_simple_c_file_parsing.py, test_complex_struct_parsing.py, etc.
- **Feature Tests**: test_multi_file_project.py, test_recursive_search.py, etc.
- **Integration Tests**: test_end_to_end_pipeline.py, test_error_handling.py, etc.
- **Example Tests**: test_basic_example.py, test_advanced_example.py, etc.

## Migration Guidelines

### Converting Existing Tests

1. **Extract test data**: Move hardcoded C code to YAML source_files section
2. **Extract config**: Move config to config.json as direct JSON text
3. **Extract assertions**: Move hardcoded assertions to YAML assertions section
4. **Create YAML file**: Create test_<meaningful_name>.yml with extracted data
5. **Update test file**: Convert to use TestDataLoader and AssertionProcessor
6. **Verify functionality**: Ensure test still validates the same functionality

### YAML Best Practices

1. **Use meaningful test names**: Descriptive test names that explain functionality
2. **Organize assertions logically**: Group by execution, model, puml
3. **Use consistent formatting**: Follow YAML formatting standards
4. **Document complex scenarios**: Add comments for complex test cases
5. **Keep files focused**: One main test scenario per YAML file
6. **Direct JSON for config**: Include config.json as direct JSON text for readability

## Example Implementation

The first test demonstrates this new approach:

- **test_simple_c_file_parsing.py**: Simple test implementation using the framework
- **test_simple_c_file_parsing.yml**: Contains all test data and assertions in a single file

This new approach makes the testing framework much more maintainable and easier to understand while providing all the benefits of data-driven testing.