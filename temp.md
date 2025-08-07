# Test Refactoring: New YAML-Based Unified Testing Framework

This document describes the new unified testing framework approach using YAML files for test data and assertions.

## Overview

The new unified testing framework uses a **single YAML file per test** that contains both inputs and assertions, making the testing approach much simpler and more maintainable.

## New Test Structure

### File Structure
```
tests/
├── unit/
│   ├── test-001.py          # Test implementation
│   ├── test-001.yml         # Test data and assertions
│   ├── test-002.py
│   ├── test-002.yml
│   └── ...
├── feature/
│   ├── test-101.py
│   ├── test-101.yml
│   └── ...
├── integration/
│   ├── test-201.py
│   ├── test-201.yml
│   └── ...
└── example/
    ├── test-301.py
    ├── test-301.yml
    └── ...
```

### YAML File Structure
Each `test-###.yml` file contains:

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

  config:
    project_name: "test_parser_simple"
    source_folders: ["."]
    output_dir: "./output"
    recursive_search: true

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
- **Features**: YAML parsing, temporary file creation

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
Unit test for [specific functionality]
"""

import os
import sys
import unittest
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.framework import UnifiedTestCase


class Test001(UnifiedTestCase):
    """Test [specific functionality]"""

    def test_functionality(self):
        """Test [specific functionality]"""
        # Load test data from YAML
        test_data = self.data_loader.load_test_data("001")
        
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

## Test Naming Convention

- **Unit Tests**: test-001.py to test-050.yml
- **Feature Tests**: test-101.py to test-150.yml
- **Integration Tests**: test-201.py to test-250.yml
- **Example Tests**: test-301.py to test-350.yml

## Migration Guidelines

### Converting Existing Tests

1. **Extract test data**: Move hardcoded C code to YAML source_files section
2. **Extract assertions**: Move hardcoded assertions to YAML assertions section
3. **Create YAML file**: Create test-###.yml with extracted data
4. **Update test file**: Convert to use TestDataLoader and AssertionProcessor
5. **Verify functionality**: Ensure test still validates the same functionality

### YAML Best Practices

1. **Use meaningful test names**: Descriptive test names in YAML
2. **Organize assertions logically**: Group by execution, model, puml
3. **Use consistent formatting**: Follow YAML formatting standards
4. **Document complex scenarios**: Add comments for complex test cases
5. **Keep files focused**: One main test scenario per YAML file

## Example Implementation

The first test (test-001) demonstrates this new approach:

- **test-001.py**: Simple test implementation using the framework
- **test-001.yml**: Contains all test data and assertions in a single file

This new approach makes the testing framework much more maintainable and easier to understand while providing all the benefits of data-driven testing.