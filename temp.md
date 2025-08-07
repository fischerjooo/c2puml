# Test Refactoring: New YAML-Based Unified Testing Framework

This document describes the new unified testing framework approach using YAML files with document separators for test data and assertions.

## Overview

The new unified testing framework uses a **single YAML file per test** with multiple documents separated by `---` that contains test metadata, source files, configuration, model templates, and assertions, making the testing approach much simpler and more maintainable.

## New Test Structure

### File Structure
```
tests/
├── unit/
│   ├── test_simple_c_file_parsing.py    # Test implementation
│   ├── test_simple_c_file_parsing.yml   # Test data and assertions
│   ├── test_complex_struct_parsing.py
│   ├── test_complex_struct_parsing.yml
│   ├── temp/                             # Temporary files (git ignored)
│   │   ├── test_simple_c_file_parsing/
│   │   │   ├── config.json
│   │   │   ├── src/
│   │   │   │   └── simple.c
│   │   │   └── output/
│   │   │       ├── model.json
│   │   │       ├── model_transformed.json
│   │   │       └── simple.puml
│   │   └── test_complex_struct_parsing/
│   └── ...
├── feature/
│   ├── test_multi_file_project.py
│   ├── test_multi_file_project.yml
│   ├── temp/
│   └── ...
├── integration/
│   ├── test_end_to_end_pipeline.py
│   ├── test_end_to_end_pipeline.yml
│   ├── temp/
│   └── ...
└── example/
    ├── test_basic_example.py
    ├── test_basic_example.yml
    ├── temp/
    └── ...
```

### YAML File Structure
Each `test_<meaningful_name>.yml` file contains multiple YAML documents separated by `---`:

```yaml
# Test metadata
test:
  name: "Simple C File Parsing"
  description: "Test parsing a simple C file with struct, enum, function, global, and include"
  category: "unit"
  id: "001"

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
    "recursive_search": true
  }

---
# Model template (optional - for complex model validation)
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

### Document Structure
Each YAML file contains up to 5 separate documents:

1. **Test Metadata**: Basic test information (name, description, category, id)
2. **Source Files**: C/C++ source files with their content
3. **Configuration**: config.json as direct JSON text
4. **Model Template** (optional): Expected model.json structure for complex validation
5. **Assertions**: Test assertions and validation criteria

### Temporary File Structure
Each test creates a temporary directory structure:

```
tests/<category>/temp/test_<test_id>/
├── config.json              # Configuration file
├── src/                     # Source files directory
│   ├── simple.c
│   └── other_files.c
└── output/                  # Generated output files
    ├── model.json
    ├── model_transformed.json
    └── simple.puml
```

## Framework Components

### 1. TestDataLoader
- **Purpose**: Load and parse multi-document YAML test files
- **Methods**: `load_test_data(test_id)`, `create_temp_files(test_data, test_id)`, `_parse_yaml_documents(documents)`
- **Features**: Multi-document YAML parsing, temporary file creation, meaningful test ID support
- **Temp Management**: Creates test-specific temp folders in `tests/*/temp/test_<id>/`

### 2. AssertionProcessor
- **Purpose**: Process assertions from YAML data
- **Methods**: `process_assertions(assertions, model_data, puml_content, result, test_case)`
- **Features**: Model validation, PlantUML validation, execution validation

### 3. TestExecutor
- **Purpose**: Execute c2puml via CLI interface
- **Methods**: `run_full_pipeline(config_path, working_dir)`
- **Interface**: CLI-only, no internal API access
- **Working Directory**: Uses temp directory as working directory for proper file resolution

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
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "simple_c_file_parsing")
        
        # Get the temp directory (parent of source_dir)
        temp_dir = os.path.dirname(source_dir)
        
        # Make config path relative to working directory
        config_filename = os.path.basename(config_path)
        
        # Execute c2puml with temp directory as working directory
        result = self.executor.run_full_pipeline(config_filename, temp_dir)
        
        # Validate execution
        self.assert_c2puml_success(result)
        
        # Load output files (output is created in temp directory, not src)
        output_dir = os.path.join(temp_dir, "output")
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

## Benefits of Multi-Document YAML Approach

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

## Git Integration

### Ignored Files
- `tests/*/temp/` - All temporary test folders
- `tests/*/output/` - Test output directories
- `tests/*/assert-*.json` - Old assertion files (no longer used)
- `tests/*/input-*.json` - Old input files (no longer used)

### Tracked Files
- `tests/*/test_*.yml` - YAML test data files
- `tests/*/test_*.py` - Test implementation files

## Migration Guidelines

### Converting Existing Tests

1. **Extract test metadata**: Create test section with name, description, category, id
2. **Extract source files**: Move C code to source_files document
3. **Extract config**: Move config to config.json document as direct JSON
4. **Extract model template** (optional): Create model.json document for complex validation
5. **Extract assertions**: Move assertions to assertions document
6. **Create YAML file**: Create test_<meaningful_name>.yml with all documents
7. **Update test file**: Convert to use TestDataLoader and AssertionProcessor
8. **Verify functionality**: Ensure test still validates the same functionality

### YAML Best Practices

1. **Use meaningful test names**: Descriptive test names that explain functionality
2. **Separate documents clearly**: Use `---` to separate different sections
3. **Add comments**: Use comments to describe each document's purpose
4. **Use consistent formatting**: Follow YAML formatting standards
5. **Keep documents focused**: Each document should have a single purpose
6. **Direct JSON for config/model**: Include JSON files as direct text for readability
7. **Optional sections**: Only include model templates when needed for complex validation

## Example Implementation

The first test demonstrates this new approach:

- **test_simple_c_file_parsing.py**: Simple test implementation using the framework
- **test_simple_c_file_parsing.yml**: Contains all test data and assertions in multiple documents
- **temp/test_simple_c_file_parsing/**: Temporary files created during test execution (git ignored)

This new approach makes the testing framework much more maintainable and easier to understand while providing all the benefits of data-driven testing with clear separation of concerns and proper git integration.