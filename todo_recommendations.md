# C2PUML Test Refactoring - Recommendations

## Overview

This document provides detailed recommendations for the unified testing framework implementation, focusing on the new YAML-based approach.

## New Unified Testing Approach

### Core Concept

Instead of the previous complex JSON-based approach, we now use a **single YAML file per test** that contains both inputs and assertions:

```
tests/
├── unit/
│   ├── test-001.py          # Test implementation
│   ├── test-001.yml         # Test data and assertions
│   ├── test-002.py
│   ├── test-002.yml
│   └── ...
```

### YAML File Structure

Each `test-###.yml` file contains:

```yaml
test:
  name: "Test Name"
  description: "Test description"
  category: "unit|feature|integration|example"
  id: "001"

inputs:
  source_files:
    filename.c: |
      C source code content here
    filename.h: |
      Header file content here
  
  config:
    project_name: "test_name"
    source_folders: ["."]
    output_dir: "./output"
    recursive_search: true

assertions:
  execution:
    exit_code: 0
    output_files: ["model.json", "model_transformed.json", "diagram.puml"]
  
  model:
    files:
      filename.c:
        structs:
          StructName:
            fields: ["field1", "field2"]
        enums:
          EnumName:
            values: ["value1", "value2"]
        functions: ["function1", "function2"]
        globals: ["global1", "global2"]
        includes: ["header1.h", "header2.h"]
    element_counts:
      structs: 1
      enums: 1
      functions: 1
      globals: 1
      includes: 1
  
  puml:
    contains_elements: ["StructName", "EnumName", "function1"]
    syntax_valid: true
```

## Framework Components

### 1. TestDataLoader

**Purpose**: Load and parse YAML test files

```python
class TestDataLoader:
    def load_test_data(self, test_id: str) -> dict:
        """Load test data from test-###.yml file"""
        
    def create_temp_files(self, test_data: dict) -> tuple[str, str]:
        """Create temporary source files and config from YAML data"""
        # Returns: (source_dir_path, config_file_path)
```

### 2. AssertionProcessor

**Purpose**: Process assertions from YAML data

```python
class AssertionProcessor:
    def process_assertions(self, assertions: dict, model_data: dict, 
                          puml_content: str, result: CLIResult, test_case) -> None:
        """Process all assertions from YAML data"""
```

### 3. TestExecutor

**Purpose**: Execute c2puml via CLI interface

```python
class TestExecutor:
    def run_full_pipeline(self, config_path: str, working_dir: str = None) -> CLIResult:
        """Execute complete c2puml pipeline"""
```

### 4. Validators

**Purpose**: Validate specific output types

- **ModelValidator**: Validate model.json content
- **PlantUMLValidator**: Validate .puml file content
- **OutputValidator**: Validate file existence and structure

### 5. UnifiedTestCase

**Purpose**: Base class for all tests

```python
class UnifiedTestCase(unittest.TestCase):
    def setUp(self):
        """Initialize framework components"""
        self.executor = TestExecutor()
        self.data_loader = TestDataLoader()
        self.assertion_processor = AssertionProcessor()
        self.model_validator = ModelValidator()
        self.puml_validator = PlantUMLValidator()
```

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

from framework import UnifiedTestCase


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

## Migration Strategy

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

## YAML File Naming Convention

- **Unit Tests**: test-001.yml, test-002.yml, etc.
- **Feature Tests**: test-101.yml, test-102.yml, etc.
- **Integration Tests**: test-201.yml, test-202.yml, etc.
- **Example Tests**: test-301.yml, test-302.yml, etc.

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

This simplified approach makes the testing framework much more maintainable and easier to understand while providing all the benefits of data-driven testing.