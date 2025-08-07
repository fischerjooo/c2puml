# C2PUML Test Suite

This directory contains the comprehensive test suite for the C2PUML tool, organized using a unified testing framework with YAML-based test data.

## Test Organization

Tests are organized into four categories:

- **Unit Tests** (`tests/unit/`): Test ID 001-050, focused on individual components
- **Feature Tests** (`tests/feature/`): Test ID 051-150, focused on feature functionality  
- **Integration Tests** (`tests/integration/`): Test ID 151-250, focused on end-to-end workflows
- **Example Tests** (`tests/example/`): Test ID 251+, focused on real-world usage examples

## Test File Structure

Each test consists of two files:
- `test_<name>.py`: Test implementation using the unified framework
- `test_<name>.yml`: Test data and assertions in YAML format

## YAML Test Data Structure

The YAML files use a multi-document format separated by `---` to organize different types of data:

### 1. Test Metadata Document
```yaml
test:
  name: "Test Name"
  description: "Detailed test description"
  category: "unit|feature|integration|example"
  id: "001"
```

### 2. Source Files Document
```yaml
source_files:
  filename.c: |
    #include <stdio.h>
    
    struct MyStruct {
        int field1;
        char field2;
    };
    
    int main() {
        return 0;
    }
  
  filename.h: |
    #ifndef FILENAME_H
    #define FILENAME_H
    
    extern int global_var;
    
    #endif
```

### 3. Configuration Document
```yaml
config.json: |
  {
    "project_name": "test_project",
    "source_folders": ["."],
    "output_dir": "./output",
    "recursive_search": true,
    "include_patterns": ["*.c", "*.h"],
    "exclude_patterns": ["*_test.c"],
    "transformations": {
      "remove_functions": ["test_*"],
      "rename_structs": {"old_name": "new_name"}
    }
  }
```

### 4. Model Template Document (Optional)
```yaml
model.json: |
  {
    "files": {
      "filename.c": {
        "structs": {
          "MyStruct": {
            "fields": ["field1", "field2"]
          }
        },
        "functions": ["main"],
        "globals": ["global_var"],
        "includes": ["stdio.h"]
      }
    },
    "element_counts": {
      "structs": 1,
      "functions": 1,
      "globals": 1,
      "includes": 1
    }
  }
```

### 5. Assertions Document
```yaml
assertions:
  # Execution assertions
  execution:
    exit_code: 0
    output_files: ["model.json", "model_transformed.json", "filename.puml"]
    stdout_contains: "Parsing complete"
    stderr_contains: ""
    max_execution_time: 30.0
  
  # Model validation assertions
  model:
    files:
      filename.c:
        structs:
          MyStruct:
            fields: ["field1", "field2"]
        functions: ["main"]
        globals: ["global_var"]
        includes: ["stdio.h"]
    element_counts:
      structs: 1
      functions: 1
      globals: 1
      includes: 1
  
  # PlantUML validation assertions
  puml:
    # Global assertions (applied to all PlantUML files)
    syntax_valid: true
    
    # Per-file assertions
    files:
      filename.puml:
        contains_elements: ["MyStruct", "main", "global_var"]
        contains_lines: ["class \"MyStruct\" as TYPEDEF_MYSTRUCT", "int main()"]
        class_count: 3
        relationship_count: 2
        classes:
          MyStruct:
            fields: ["field1", "field2"]
        relationships:
          - type: "composition"
            from: "main"
            to: "MyStruct"
```

## Assertion Types

### Execution Assertions
- `exit_code`: Expected CLI exit code (0 for success)
- `output_files`: List of expected output files
- `stdout_contains`: Text that must appear in stdout
- `stderr_contains`: Text that must appear in stderr
- `max_execution_time`: Maximum allowed execution time in seconds

### Model Assertions
- `files`: Per-file model validation
  - `structs`: Expected struct definitions with fields
  - `enums`: Expected enum definitions with values
  - `functions`: Expected function names
  - `globals`: Expected global variable names
  - `includes`: Expected include statements
- `element_counts`: Expected counts of different element types

### PlantUML Assertions
- `syntax_valid`: Whether PlantUML syntax should be valid
- `files`: Per-file PlantUML validation
  - `contains_elements`: Elements that must appear in the diagram
  - `contains_lines`: Specific lines that must appear
  - `class_count`: Expected number of classes
  - `relationship_count`: Expected number of relationships
  - `classes`: Detailed class structure validation
  - `relationships`: Specific relationship validation

## Example Test Structure

### Standard Test (Unit/Feature/Integration)
```yaml
# Complete YAML with all sections
test:
  name: "My Test"
  description: "Test description"
  category: "unit"
  id: "001"

---
source_files:
  main.c: |
    // Source code here

---
config.json: |
  {
    "project_name": "test",
    "source_folders": ["."],
    "output_dir": "./output"
  }

---
assertions:
  execution:
    exit_code: 0
  model:
    files:
      main.c:
        structs: {}
        functions: ["main"]
  puml:
    syntax_valid: true
```

### Example Test
```yaml
# Only assertions (uses external config.json and source/ folder)
test:
  name: "Example Test"
  description: "Example test using external files"
  category: "example"
  id: "251"

---
assertions:
  execution:
    exit_code: 0
  model:
    files:
      main.c:
        functions: ["main"]
  puml:
    syntax_valid: true
```

## Running Tests

### Individual Test
```bash
python3 tests/unit/test_simple_c_file_parsing.py
```

### All Tests
```bash
./scripts/run_all.sh
```

### Specific Category
```bash
python3 -m pytest tests/unit/
python3 -m pytest tests/feature/
python3 -m pytest tests/integration/
python3 -m pytest tests/example/
```

## Framework Components

- **UnifiedTestCase**: Base class for all tests
- **TestDataLoader**: Loads and parses YAML test data
- **TestExecutor**: Executes c2puml CLI commands
- **ValidatorsProcessor**: Coordinates validation of outputs
- **Validators**: Individual validation classes (ModelValidator, PlantUMLValidator, etc.)

## Test Development Guidelines

1. **Use meaningful test names**: `test_simple_c_file_parsing` not `test_001`
2. **Organize by category**: Place tests in appropriate directories
3. **Use YAML for data**: Keep test data separate from test logic
4. **Validate comprehensively**: Include execution, model, and PlantUML assertions
5. **Follow naming conventions**: Use consistent file and test naming patterns

## Temporary File Management

During test execution, temporary files are created in:
- `tests/<category>/test-<name>/input/`: Source files and config
- `tests/<category>/test-<name>/output/`: Generated model and PlantUML files

These directories are automatically cleaned up between test runs and are ignored by git.