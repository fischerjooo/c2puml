# C2PUML Test Refactoring - Unified Testing Framework

## Overview

This document outlines the refactoring of the C2PUML test suite to use a unified, CLI-only, public API testing framework with multi-document YAML files. The new framework provides comprehensive guidance for test developers and ensures consistent, maintainable test patterns.

## Current Test Structure

The current test suite has inconsistent patterns:
- Direct internal API imports in tests
- Mixed testing approaches (unit, integration, feature)
- Hardcoded test data scattered throughout test files
- No standardized input/output validation

## New Unified Testing Framework

### Test Structure
```
tests/
├── unit/
│   ├── test_simple_c_file_parsing.py    # Test implementation
│   ├── test_simple_c_file_parsing.yml   # Test data and assertions
│   ├── test_complex_struct_parsing.py
│   ├── test_complex_struct_parsing.yml
│   └── test-simple_c_file_parsing/      # Generated during test execution
│       ├── input/
│       │   ├── config.json
│       │   └── src/
│       │       └── simple.c
│       └── output/
│           ├── model.json
│           ├── model_transformed.json
│           └── simple.puml
├── feature/
│   ├── test_multi_file_project.py
│   ├── test_multi_file_project.yml
│   └── test-multi_file_project/         # Generated during test execution
│       ├── input/
│       └── output/
├── integration/
│   ├── test_end_to_end_pipeline.py
│   ├── test_end_to_end_pipeline.yml
│   └── test-end_to_end_pipeline/        # Generated during test execution
│       ├── input/
│       └── output/
└── example/
    ├── test_basic_example.py
    ├── test_basic_example.yml           # Contains ONLY assertions
    ├── config.json                      # External config file
    └── source/                          # External source folder
        ├── main.c
        ├── header.h
        └── other_files.c
```

### Test Types and Structures

#### **Unit, Feature, Integration Tests** (Standard Structure)
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
    # Global PlantUML assertions (applied to all files)
    syntax_valid: true
    
    # Per-file PlantUML assertions
    files:
      example.puml:
        contains_elements: ["ExampleStruct", "main"]
        contains_lines: ["class \"ExampleStruct\"", "int main()"]
        class_count: 2
        relationship_count: 0
```

**Example Test Structure**:
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

### Document Structure
Each YAML file contains different documents based on test type:

#### **Standard Tests** (Unit, Feature, Integration):
1. **Test Metadata**: Basic test information (name, description, category, id)
2. **Source Files**: C/C++ source files with their content
3. **Configuration**: config.json as direct JSON text
4. **Model Template** (optional): Expected model.json structure for complex validation
5. **Assertions**: Test assertions and validation criteria

#### **Example Tests**:
1. **Test Metadata**: Basic test information (name, description, category, id)
2. **Assertions**: Test assertions and validation criteria only

### Temporary File Structure

#### **Standard Tests** (Unit, Feature, Integration):
```
tests/<category>/test-<test_id>/
├── input/
│   ├── config.json              # Configuration file
│   └── src/                     # Source files directory
│       ├── simple.c
│       └── other_files.c
└── output/                      # Generated output files
    ├── model.json
    ├── model_transformed.json
    └── simple.puml
```

#### **Example Tests**:
```
tests/example/test-<test_id>/
└── output/                      # Generated output files only
    ├── model.json
    ├── model_transformed.json
    └── example.puml
```

**Note**: Example tests use external `config.json` and `source/` folder, so no temporary input files are created.

## Framework Components

### TestDataLoader
- Loads multi-document YAML test files
- **Standard Tests**: Creates temporary source and config files from YAML content (after cleanup by setUp)
- **Example Tests**: Uses external config.json and source/ folder (no temp files created)
- Supports meaningful test IDs
- Handles optional model templates
- **Temp Management**: 
  - Standard tests: Creates test-specific temp folders in `tests/*/test-<id>/`
  - Example tests: Creates only output folder in `tests/example/test-<id>/`

### ValidatorsProcessor
- Processes assertions from YAML data
- Validates model content
- Validates PlantUML output
- Validates execution results

### TestExecutor
- Executes c2puml via CLI interface only
- No direct internal API access
- Supports verbose output and error handling
- **Working Directory**: 
  - Standard tests: Uses temp input directory as working directory
  - Example tests: Uses example directory (where config.json is located)

### Validators
- ModelValidator: Validates model.json structure and content
- PlantUMLValidator: Validates .puml file syntax and content
- OutputValidator: Validates file existence and structure

### UnifiedTestCase
- Base class for all tests
- Provides common setup/teardown with complete cleanup
- **setUp()**: Cleans up any existing test-* folders before creating new ones
- **tearDown()**: Preserves output for debugging (no automatic cleanup)
- Initializes framework components

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

## Implementation Plan

### Phase 1: Foundation ✅
- [x] Create framework components
- [x] Implement TestDataLoader with multi-document support
- [x] Implement ValidatorsProcessor
- [x] Implement TestExecutor
- [x] Create UnifiedTestCase base class
- [x] Remove old input_factory and references

### Phase 2: Pilot ✅
- [x] Convert first unit test (test_simple_c_file_parsing)
- [x] Validate framework functionality
- [x] Document approach and patterns

### Phase 3: Systematic Migration
- [ ] Convert remaining unit tests
- [ ] Convert feature tests
- [ ] Convert integration tests
- [ ] Convert example tests

### Phase 4: Cleanup
- [ ] Remove old framework files
- [ ] Update .gitignore
- [ ] Clean up conftest.py dependencies

## Migration Tracking

### Unit Tests (001-050)

| Test File | Status | New Name | YAML File | Notes |
|-----------|--------|----------|-----------|-------|
| test_simple_c_file_parsing.py | ✅ Complete | test_simple_c_file_parsing | test_simple_c_file_parsing.yml | First pilot test - Enhanced with high-level methods |
| test_parser.py | 🔄 Pending | test_parser_comprehensive | test_parser_comprehensive.yml | Complex parser test |
| test_parser_comprehensive.py | 🔄 Pending | test_parser_comprehensive | test_parser_comprehensive.yml | Comprehensive parsing |
| test_parser_filtering.py | 🔄 Pending | test_parser_filtering | test_parser_filtering.yml | Filtering functionality |
| test_parser_function_params.py | 🔄 Pending | test_parser_function_params | test_parser_function_params.yml | Function parameters |
| test_parser_macro_duplicates.py | 🔄 Pending | test_parser_macro_duplicates | test_parser_macro_duplicates.yml | Macro handling |
| test_parser_nested_structures.py | 🔄 Pending | test_parser_nested_structures | test_parser_nested_structures.yml | Nested structures |
| test_parser_struct_order.py | 🔄 Pending | test_parser_struct_order | test_parser_struct_order.yml | Struct ordering |
| test_global_parsing.py | 🔄 Pending | test_global_parsing | test_global_parsing.yml | Global variable parsing |
| test_include_processing.py | 🔄 Pending | test_include_processing | test_include_processing.yml | Include processing |
| test_include_filtering_bugs.py | 🔄 Pending | test_include_filtering_bugs | test_include_filtering_bugs.yml | Include filtering |
| test_function_parameters.py | 🔄 Pending | test_function_parameters | test_function_parameters.yml | Function parameters |
| test_typedef_extraction.py | 🔄 Pending | test_typedef_extraction | test_typedef_extraction.yml | Typedef extraction |
| test_anonymous_structure_handling.py | 🔄 Pending | test_anonymous_structure_handling | test_anonymous_structure_handling.yml | Anonymous structures |
| test_anonymous_processor_extended.py | 🔄 Pending | test_anonymous_processor_extended | test_anonymous_processor_extended.yml | Extended anonymous processing |
| test_multi_pass_anonymous_processing.py | 🔄 Pending | test_multi_pass_anonymous_processing | test_multi_pass_anonymous_processing.yml | Multi-pass processing |
| test_debug_actual_parsing.py | 🔄 Pending | test_debug_actual_parsing | test_debug_actual_parsing.yml | Debug parsing |
| test_debug_field_parsing.py | 🔄 Pending | test_debug_field_parsing | test_debug_field_parsing.yml | Field parsing debug |
| test_debug_field_parsing_detailed.py | 🔄 Pending | test_debug_field_parsing_detailed | test_debug_field_parsing_detailed.yml | Detailed field parsing |
| test_debug_field_processing.py | 🔄 Pending | test_debug_field_processing | test_debug_field_processing.yml | Field processing debug |
| test_debug_tokens.py | 🔄 Pending | test_debug_tokens | test_debug_tokens.yml | Token debugging |
| test_absolute_path_bug_detection.py | 🔄 Pending | test_absolute_path_bug_detection | test_absolute_path_bug_detection.yml | Absolute path bugs |
| test_config.py | 🔄 Pending | test_config | test_config.yml | Configuration handling |
| test_file_specific_configuration.py | 🔄 Pending | test_file_specific_configuration | test_file_specific_configuration.yml | File-specific config |
| test_utils.py | 🔄 Pending | test_utils | test_utils.yml | Utility functions |
| test_verifier.py | 🔄 Pending | test_verifier | test_verifier.yml | Verification logic |

### Feature Tests (101-150)

| Test File | Status | New Name | YAML File | Notes |
|-----------|--------|----------|-----------|-------|
| test_generator.py | 🔄 Pending | test_generator | test_generator.yml | Main generator test |
| test_generator_exact_format.py | 🔄 Pending | test_generator_exact_format | test_generator_exact_format.yml | Exact format generation |
| test_generator_grouping.py | 🔄 Pending | test_generator_grouping | test_generator_grouping.yml | Grouping functionality |
| test_generator_include_tree_bug.py | 🔄 Pending | test_generator_include_tree_bug | test_generator_include_tree_bug.yml | Include tree bugs |
| test_generator_naming_conventions.py | 🔄 Pending | test_generator_naming_conventions | test_generator_naming_conventions.yml | Naming conventions |
| test_generator_new_formatting.py | 🔄 Pending | test_generator_new_formatting | test_generator_new_formatting.yml | New formatting |
| test_generator_visibility_logic.py | 🔄 Pending | test_generator_visibility_logic | test_generator_visibility_logic.yml | Visibility logic |
| test_generator_duplicate_includes.py | 🔄 Pending | test_generator_duplicate_includes | test_generator_duplicate_includes.yml | Duplicate includes |
| test_transformer.py | 🔄 Pending | test_transformer | test_transformer.yml | Main transformer test |
| test_transformation_system.py | 🔄 Pending | test_transformation_system | test_transformation_system.yml | Transformation system |
| test_preprocessor_handling.py | 🔄 Pending | test_preprocessor_handling | test_preprocessor_handling.yml | Preprocessor handling |
| test_preprocessor_bug.py | 🔄 Pending | test_preprocessor_bug | test_preprocessor_bug.yml | Preprocessor bugs |
| test_tokenizer.py | 🔄 Pending | test_tokenizer | test_tokenizer.yml | Tokenizer functionality |

### Integration Tests (201-250)

| Test File | Status | New Name | YAML File | Notes |
|-----------|--------|----------|-----------|-------|
| test_end_to_end_pipeline.py | 🔄 Pending | test_end_to_end_pipeline | test_end_to_end_pipeline.yml | End-to-end pipeline |
| test_error_handling.py | 🔄 Pending | test_error_handling | test_error_handling.yml | Error handling |

### Example Tests (301-350)

| Test File | Status | New Name | YAML File | Notes |
|-----------|--------|----------|-----------|-------|
| test_basic_example.py | 🔄 Pending | test_basic_example | test_basic_example.yml | Basic example |
| test_advanced_example.py | 🔄 Pending | test_advanced_example | test_advanced_example.yml | Advanced example |

## Framework Enhancements Completed ✅

The framework has been enhanced with the following improvements:

### High-Level Test Methods
- **`run_test(test_id)`**: Encapsulates the complete test execution pattern
- **`assert_test_success(result)`**: Validates CLI execution success
- **`validate_test_output(result)`**: Processes all assertions from YAML

### Enhanced Error Handling
- **`TestError` class**: Provides context-rich error messages with test metadata
- **Better debugging**: Enhanced error messages include relevant context information

### Schema Validation
- **YAML structure validation**: Ensures test data follows expected schema
- **Required field validation**: Validates all required sections and fields
- **Type checking**: Validates data types for each section

### Simplified Test Implementation
The first test (`test_simple_c_file_parsing.py`) now uses the simplified 3-line pattern:
```python
result = self.run_test("simple_c_file_parsing")
self.assert_test_success(result)
self.validate_test_output(result)
```

## Benefits
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

## Example Implementation

The first test demonstrates this new approach:

- **test_simple_c_file_parsing.py**: Simple test implementation using the framework
- **test_simple_c_file_parsing.yml**: Contains all test data and assertions in multiple documents
- **temp/test_simple_c_file_parsing/**: Temporary files created during test execution (git ignored)

This new approach makes the testing framework much more maintainable and easier to understand while providing all the benefits of data-driven testing with clear separation of concerns and proper git integration.