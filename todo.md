# C2PUML Test Refactoring - Unified Testing Framework

## Overview

This document outlines the refactoring of the c2puml test suite to use a unified testing framework that enforces CLI-only access to c2puml functionality, ensuring tests validate the actual user interface.

## Current Test Structure

The current test suite has several issues:
- Direct internal API usage in tests
- Inconsistent test patterns
- Mixed testing approaches (unit, integration, feature)
- No clear separation between test logic and test data

## New Unified Testing Framework

### Core Principles

1. **CLI-Only Access**: Tests can only interact with c2puml through its public CLI interface
2. **No Internal API Imports**: Tests are forbidden from importing internal c2puml modules
3. **Data-Driven Testing**: Test data and assertions are externalized to YAML files
4. **Standardized Structure**: All tests follow the same pattern

### Test Structure

Each test follows this standardized structure:

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

### 1. TestExecutor
- **Purpose**: Execute c2puml via CLI interface
- **Methods**: `run_full_pipeline()`, `run_parse_only()`, `run_transform_only()`, `run_generate_only()`
- **Interface**: CLI-only, no internal API access

### 2. TestDataLoader
- **Purpose**: Load test data from YAML files
- **Methods**: `load_test_data(test_id)`, `create_temp_files(test_data)`
- **Features**: YAML parsing, temporary file creation

### 3. AssertionProcessor
- **Purpose**: Process assertions from YAML data
- **Methods**: `process_assertions(assertions, model_data, puml_content, result)`
- **Features**: Model validation, PlantUML validation, execution validation

### 4. Validators
- **ModelValidator**: Validate model.json content
- **PlantUMLValidator**: Validate .puml file content
- **OutputValidator**: Validate file existence and structure

### 5. UnifiedTestCase
- **Purpose**: Base class for all tests
- **Features**: Setup/teardown, component initialization, basic utilities

## Implementation Plan

### Phase 1: Framework Foundation ✅
- [x] Create TestExecutor for CLI execution
- [x] Create TestDataLoader for YAML file loading
- [x] Create AssertionProcessor for assertion processing
- [x] Create Validators for output validation
- [x] Create UnifiedTestCase base class

### Phase 2: Pilot Migration
- [x] Convert first test (test-001: Simple C File Parsing)
- [ ] Validate framework with first test
- [ ] Refine framework based on pilot experience

### Phase 3: Systematic Migration
- [ ] Convert unit tests (test-002 to test-050)
- [ ] Convert feature tests (test-101 to test-150)
- [ ] Convert integration tests (test-201 to test-250)
- [ ] Convert example tests (test-301 to test-350)

### Phase 4: Framework Cleanup
- [ ] Remove old framework files
- [ ] Update documentation
- [ ] Clean up .gitignore
- [ ] Remove conftest.py dependencies

## Migration Tracking

### Completed Tests
- [x] test-001: Simple C File Parsing (unit)

### Pending Tests
- [ ] test-002: Complex Struct Parsing (unit)
- [ ] test-003: Enum with Values (unit)
- [ ] test-004: Function Parameters (unit)
- [ ] test-005: Include Dependencies (unit)
- [ ] test-101: Multi-file Project (feature)
- [ ] test-102: Recursive Directory Search (feature)
- [ ] test-201: End-to-End Pipeline (integration)
- [ ] test-202: Error Handling (integration)
- [ ] test-301: Basic Example (example)
- [ ] test-302: Advanced Example (example)

## Benefits

1. **Standardization**: All tests follow the same structure
2. **Maintainability**: Test data is separate from test logic
3. **Readability**: YAML files are human-readable and self-documenting
4. **Flexibility**: Easy to modify test data without touching code
5. **CLI Compliance**: Enforces testing of the actual user interface
6. **Framework Independence**: Tests are not tied to internal implementation details