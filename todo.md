# C2PUML Test Refactoring - Unified Testing Framework

## Overview

This document outlines the refactoring of the C2PUML test suite to use a unified, CLI-only, public API testing framework with multi-document YAML files.

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
│   ├── test_simple_c_file_parsing.py
│   ├── test_simple_c_file_parsing.yml
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
Each test uses a single YAML file with multiple documents separated by `---`:

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

## Framework Components

### TestDataLoader
- Loads multi-document YAML files
- Creates temporary source and config files
- Supports meaningful test IDs
- Handles optional model templates

### AssertionProcessor
- Processes assertions from YAML data
- Validates model content
- Validates PlantUML output
- Validates execution results

### TestExecutor
- Executes c2puml via CLI interface only
- No direct internal API access
- Supports verbose output and error handling

### Validators
- ModelValidator: Validates model.json structure and content
- PlantUMLValidator: Validates .puml file syntax and content
- OutputValidator: Validates file existence and structure

### UnifiedTestCase
- Base class for all tests
- Provides common setup/teardown
- Initializes framework components

## Implementation Plan

### Phase 1: Foundation ✅
- [x] Create framework components
- [x] Implement TestDataLoader with multi-document support
- [x] Implement AssertionProcessor
- [x] Implement TestExecutor
- [x] Create UnifiedTestCase base class

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

| Test Category | Status | Notes |
|---------------|--------|-------|
| test_simple_c_file_parsing | ✅ Complete | First pilot test with multi-document YAML |
| Unit Tests (001-050) | 🔄 Pending | |
| Feature Tests (101-150) | 🔄 Pending | |
| Integration Tests (201-250) | 🔄 Pending | |
| Example Tests (301-350) | 🔄 Pending | |

## Benefits

1. **Clear Separation**: Each document has a specific purpose and is clearly separated
2. **Readability**: Easy to read and understand each section independently
3. **Maintainability**: Easy to modify specific sections without affecting others
4. **Flexibility**: Optional sections (like model templates) can be included as needed
5. **Natural Formats**: Each section uses its most natural format (JSON for config, YAML for assertions)
6. **Version Control**: Clear diffs when individual sections change
7. **Meaningful Names**: Test files have descriptive names that explain their purpose
8. **Direct JSON**: Config and model files are included as direct text for better readability

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