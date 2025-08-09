# C2PUML Test Suite

This directory contains the comprehensive test suite for the C2PUML tool, organized using a unified testing framework with YAML-based test data.

## Test Organization

Tests are organized into four categories:

- **Unit Tests** (`tests/unit/`): Test ID 0001-1000, focused on individual components
- **Feature Tests** (`tests/feature/`): Test ID 1001-2000, focused on feature functionality  
- **Integration Tests** (`tests/integration/`): Test ID 2001-3000, focused on end-to-end workflows
- **Example Tests** (`tests/example/`): Test ID 3001-4000, focused on real-world usage examples

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
  id: "0001"
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
  id: "0001"

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
  id: "3001"

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

---

## Quick Guidelines
- Prefer the simple pattern: `result = self.run_test("<id>"); self.validate_execution_success(result); self.validate_test_output(result)`
- Use CLI-only via TestExecutor methods: `run_parse_only`, `run_transform_only`, `run_generate_only`, `run_full_pipeline`.
- Keep YAML as the source of truth for assertions; avoid custom asserts unless necessary.
- For file path assertions in YAML, use `./output/...`; paths are normalized by the framework.
- Maintain 1:1 pairing: every `test_*.py` has a matching `test_*.yml`.
- For transform/generate-only tests, copy required `model.json`/`model_transformed.json` into `./output/` before invoking the step.
- Organize by category and IDs: unit (0001-1000), feature (1001-2000), integration (2001-3000), example (3001-4000).
- Default performance budget: 30s for unit/feature tests unless a test requires more.

## Simple Test Pattern (Recommended)
```python
from tests.framework import UnifiedTestCase

class TestSimpleCFileParsing(UnifiedTestCase):
    def test_simple_c_file_parsing(self):
        result = self.run_test("simple_c_file_parsing")
        self.validate_execution_success(result)
        self.validate_test_output(result)
```

## CLI Steps and Inputs
- `run_parse_only(config_path, working_dir)`: input C/C++ sources → outputs `model.json`.
- `run_transform_only(config_path, working_dir)`: input `model.json` → outputs `model_transformed.json`.
- `run_generate_only(config_path, working_dir)`: input `model.json` or `model_transformed.json` → outputs `.puml` files.
- `run_full_pipeline(config_path, working_dir)`: parse → transform → generate.

## Pairing Rules and Multiple YAMLs
- 1:1 base-name pairing is required: `test_foo.py` ↔ `test_foo.yml`.
- For multiple scenarios in one Python file, use suffixes in YAML names and call by suffix id:
  - Python: `test_absolute_path_bug_comprehensive.py`
  - YAMLs: `test_absolute_path_bug_comprehensive_relative_path.yml`, `..._subdirectory.yml`, `..._mixed_paths.yml`, `..._consistency.yml`
  - Calls: `self.run_test("absolute_path_bug_comprehensive_relative_path")`, etc.

## Additional Assertion Patterns (Useful Snippets)

### File system assertions
```yaml
assertions:
  files:
    output_dir_exists: "./output"
    files_exist:
      - "./output/model.json"
      - "./output/main.puml"
    files_not_exist:
      - "./output/debug.puml"
    json_files_valid:
      - "./output/model.json"
    utf8_files:
      - "./output/main.puml"
    file_content:
      "./output/main.puml":
        contains: ["@startuml", "@enduml"]
        not_contains: ["ERROR"]
        contains_lines: ["@startuml main", "@enduml"]
        not_empty: true
```

### Parser/Transformer/Generator highlights
```yaml
assertions:
  model:
    functions_exist: ["main"]
    structs_exist: ["Person"]
    enums_exist: ["Status"]
    functions_not_exist: ["deprecated_function"]
    element_counts:
      functions: 1
  puml:
    syntax_valid: true
    contains_elements: ["Person", "main"]
    class_count: 3
    relationships_exist:
      - source: "MAIN"
        target: "HEADER_STDIO"
        type: "-->"
```

### Error handling and performance
```yaml
assertions:
  execution:
    success_expected: false
    expected_error: "Invalid source path"
    exit_code: 1
    stderr_contains: "Error: File not found"
    max_execution_time: 10.0
```

## Example Tests (Special Structure)
- YAML contains ONLY `test` and `assertions`; sources and `config.json` live beside the test and are tracked in git.
- Working directory is the example folder where `config.json` resides.
- Output is still written to a test-specific `output/` directory.