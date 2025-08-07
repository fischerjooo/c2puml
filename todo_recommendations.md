# C2PUML Test Refactoring - Recommendations

## Overview

This document provides detailed recommendations and guidance for test developers working with the new unified testing framework. It includes practical examples, best practices, and step-by-step instructions for creating and maintaining tests.

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
```

#### **Example Tests** (Special Structure)
Example tests use external source folders and config files, with YAML containing ONLY assertions:

```yaml
# Test metadata
test:
  name: "Basic Example"
  description: "Test basic example with external source folder and config"
  category: "example"
  id: "001"

---
# Assertions only (no source_files or config.json sections)
assertions:
  execution:
    exit_code: 0
    output_files: ["model.json", "model_transformed.json", "example.puml"]
  
  model:
    files:
      main.c:
        structs:
          ExampleStruct:
            fields: ["value", "name"]
        functions: ["main", "helper_function"]
        includes: ["header.h"]
  
  puml:
    contains_elements: ["ExampleStruct", "main"]
    syntax_valid: true
```

### Test Folder Structures

#### **Standard Tests** (Unit, Feature, Integration):
```
tests/unit/
├── test_simple_c_file_parsing.py
├── test_simple_c_file_parsing.yml
└── test-simple_c_file_parsing/          # Generated during test execution
    ├── input/
    │   ├── config.json
    │   └── src/
    │       └── simple.c
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
- Common setup/teardown
- Utility methods for assertions
- Standardized test output management

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

### Example Test Structure
```python
#!/usr/bin/env python3
"""
Example test for Basic Example
"""

import os
import sys
import unittest
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.framework import UnifiedTestCase


class TestBasicExample(UnifiedTestCase):
    """Test Basic Example with External Source Files"""

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
        
        # Process assertions from YAML
        self.assertion_processor.process_assertions(
            test_data["assertions"], model_data, puml_content, result, self
        )


if __name__ == "__main__":
    unittest.main()
```

**Key Differences for Example Tests**:
1. **No temp file creation**: Uses external config.json and source/ folder
2. **Working directory**: Uses example directory where config.json is located
3. **YAML content**: Contains only test metadata and assertions
4. **Output location**: Generated in test-specific output folder
5. **External files**: config.json and source/ folder are tracked by git

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