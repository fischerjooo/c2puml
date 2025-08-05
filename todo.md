# C2PUML Test Framework Unification - Todo

## Executive Summary

This document outlines the comprehensive work required to transform the current c2puml test suite (58 test files across unit, feature, integration, and example categories) into a unified, maintainable, and robust testing framework. The primary focus is on **test-application boundary separation** and **public API testing** to ensure the application remains flexible to internal changes. The existing `tests/example/` structure will be preserved and enhanced with standardized expectations.

## Current State Analysis

### Current Test Structure
- **58 test files** across 4 categories:
  - `tests/unit/` (37 files) - Individual component tests
  - `tests/feature/` (12 files) - Complete workflow tests  
  - `tests/integration/` (2 files) - End-to-end scenarios
  - `tests/example/` (1 file) - Example project test (to be preserved)
- **Mixed testing approaches**: Some tests use internal functions, others use public APIs
- **Inconsistent patterns**: Different test classes use different setup/teardown approaches
- **Direct internal access**: Many tests directly import and test internal components

### Public API Surface (Target for Testing)
Based on analysis of the codebase, the public APIs are:

1. **CLI Interface** (`main.py`):
   ```bash
   c2puml --config config.json [parse|transform|generate]
   python3 main.py --config config.json [parse|transform|generate]
   ```

2. **Package Interface** (`src/c2puml/__init__.py`):
   ```python
   from c2puml import Parser, Transformer, Generator
   ```

3. **Configuration Interface**:
   - JSON configuration files with standardized schema
   - Input: C/C++ source files and headers
   - Output: model.json, transformed_model.json, .puml files

## Work Items

### 1. Unified Testing Framework Design

#### 1.1 Core Testing Framework (`tests/framework/`)
**Priority: HIGH**

Create a new unified framework with these components:

- **`TestExecutor`**: Runs c2puml through public APIs only
- **`TestDataFactory`**: Generates test C/C++ projects and configurations
- **`ResultValidator`**: Validates outputs (model.json, .puml files, logs)
- **`TestProjectBuilder`**: Builds temporary test projects with complex structures

```python
# Example structure
tests/framework/
├── __init__.py
├── executor.py      # TestExecutor class
├── data_factory.py  # TestDataFactory class  
├── validator.py     # ResultValidator class
├── builder.py       # TestProjectBuilder class
└── fixtures.py      # Common test fixtures
```

#### 1.2 Test Execution Patterns
**Priority: HIGH**

Standardize how tests execute c2puml:

```python
class UnifiedTestCase(unittest.TestCase):
    def setUp(self):
        self.executor = TestExecutor()
        self.data_factory = TestDataFactory()
        self.validator = ResultValidator()
        # Get test name from class name (e.g., TestParsing -> test_parsing)
        self.test_name = self.__class__.__name__.lower().replace('test', 'test_')
    
    def test_feature(self):
        # 1. Load test data from self-contained folders
        test_input = self.data_factory.load_test_input(self.test_name)
        config = self.data_factory.load_test_config(self.test_name)
        
        # 2. Execute through public API
        result = self.executor.run_full_pipeline(test_input, config)
        
        # 3. Validate results
        self.validator.assert_model_valid(result.model)
        self.validator.assert_puml_contains(result.puml, expected_elements)
```

### 2. Public API Testing Strategy

#### 2.1 CLI Interface Testing
**Priority: HIGH**

All tests should execute c2puml through:
- Direct CLI calls using `subprocess`
- Package imports using the public `c2puml` module interface

**Forbidden**: Direct imports of internal modules like:
- `from c2puml.core.parser import CParser` ❌
- `from c2puml.core.tokenizer import CTokenizer` ❌

**Allowed**: Public interfaces only:
- `from c2puml import Parser, Transformer, Generator` ✅
- CLI execution: `subprocess.run(['python3', 'main.py', '--config', ...])` ✅

#### 2.2 Test Input/Output Validation
**Priority: HIGH**

Tests should validate:
- **Input validation**: Configuration files, C/C++ source structure
- **Output validation**: Generated model.json structure, PlantUML syntax, file organization
- **Log validation**: Error messages, warning patterns, execution flow

### 3. Test Data Management

#### 3.1 Standardized Test Data Factory
**Priority: MEDIUM**

Create reusable test data generators:

```python
class TestDataFactory:
    def load_test_input(self, test_name: str) -> TestInput:
        """Loads test input from test_<name>/input/ directory (C files, model.json, etc.)"""
    
    def load_test_config(self, test_name: str) -> ConfigData:
        """Loads configuration from test_<name>/config.json"""
    
    def create_temp_project(self, input_files: dict) -> TestProject:
        """Creates temporary project for dynamic test generation"""
    
    def get_test_data_path(self, test_name: str, subpath: str = "") -> Path:
        """Returns path to test data: test_<name>/input/ or test_<name>/config.json"""
```

#### 3.2 Self-Contained Test Data
**Priority: MEDIUM**

Each test folder contains its own project and configuration data:

**Test Folder Structure Pattern:**
```
test_<name>/
├── test_<name>.py      # Test implementation
├── input/              # Test input files (C/C++ source, model.json, etc.)
│   ├── main.c          # For unit tests: C files, model.json, etc.
│   ├── utils.h         # For feature/integration: C/C++ source files
│   └── subdir/         # Nested directories if needed
└── config.json        # Test configuration
```

**Benefits of Self-Contained Structure:**
- **Isolation**: Each test has its own data, preventing cross-test interference
- **Clarity**: Test data is co-located with test logic for easy understanding
- **Maintainability**: Changes to one test don't affect others
- **Versioning**: Test data and logic evolve together
- **Debugging**: Easier to reproduce issues with self-contained test environments

### 4. Result Validation Framework

#### 4.1 Model Validation
**Priority: HIGH**

Structured validation of generated models:

```python
class ModelValidator:
    def assert_model_structure_valid(self, model: dict)
    def assert_files_parsed(self, model: dict, expected_files: list)
    def assert_struct_exists(self, model: dict, struct_name: str)
    def assert_function_exists(self, model: dict, func_name: str)
    def assert_function_declared(self, model: dict, func_name: str)
    def assert_include_relationship(self, model: dict, source: str, target: str)
    def assert_transformation_applied(self, before: dict, after: dict, transformation: dict)
    def assert_enum_exists(self, model: dict, enum_name: str)
    def assert_typedef_exists(self, model: dict, typedef_name: str)
```

#### 4.2 PlantUML Validation
**Priority: HIGH**

Validation of generated PlantUML files:

```python
class PlantUMLValidator:
    def assert_class_exists(self, puml_content: str, class_name: str, stereotype: str)
    def assert_relationship(self, puml_content: str, source: str, target: str, rel_type: str)
    def assert_formatting_compliant(self, puml_content: str)
    def assert_no_duplicate_elements(self, puml_content: str)
```

#### 4.3 Example Test Validation
**Priority: MEDIUM**

The `tests/example/` directory should be preserved with its current structure but enhanced with a standardized expectations file. **Note**: The example test has a different structure than other tests:

**Example Test Structure (preserved as-is):**
```
tests/example/
├── source/             # C/C++ source files (different from other tests' input/)
├── config.json         # Existing configuration (different from test-specific structure)
├── test-example.py     # Example workflow test
└── test-example.json   # NEW - Expected outputs specification
```

**Proposed test-example.json for validation:**
```json
// tests/example/test-example.json
{
  "description": "Expected outputs for example project test",
  "note": "This test uses source/ folder and existing config.json, unlike other tests that use input/ and test-specific config.json",
  "model_expectations": {
    "files_count": 3,
    "required_files": ["sample.c", "sample.h", "config.h"],
    "structs": ["Point", "Rectangle", "User"],
    "functions": ["main", "calculate_area", "init_config"],
    "enums": ["Color", "Status"],
    "typedefs": ["int32_t", "point_t"]
  },
  "puml_expectations": {
    "generated_files": ["sample.puml"],
    "required_classes": [
      {"name": "sample", "stereotype": "source"},
      {"name": "sample.h", "stereotype": "header"},
      {"name": "Point", "stereotype": "struct"}
    ],
    "required_relationships": [
      {"source": "SAMPLE", "target": "HEADER_SAMPLE", "type": "include"}
    ]
  },
  "transformation_expectations": {
    "renamed_functions": {"deprecated_print_info": "legacy_print_info"},
    "removed_elements": ["test_debug_function", "LEGACY_MACRO"]
  }
}
```

### 5. Test Organization and Refactoring

#### 5.1 Test Categorization
**Priority: MEDIUM**

Reorganize 58 test files into clear categories with self-contained test folders:

```
tests/
├── framework/           # New unified testing framework
├── unit/               # Refactored unit tests (public API only)
│   ├── test_parsing/              # Self-contained test folder
│   │   ├── test_parsing.py        # Test implementation
│   │   ├── input/                 # Test input files (C/C++ source, model.json, etc.)
│   │   └── config.json            # Test configuration
│   ├── test_transformation/       # Self-contained test folder
│   │   ├── test_transformation.py # Test implementation
│   │   ├── input/                 # Test input files (C/C++ source, model.json, etc.)
│   │   └── config.json            # Test configuration
│   ├── test_generation/           # Self-contained test folder
│   │   ├── test_generation.py     # Test implementation
│   │   ├── input/                 # Test input files (C/C++ source, model.json, etc.)
│   │   └── config.json            # Test configuration
│   └── test_configuration/        # Self-contained test folder
│       ├── test_configuration.py  # Test implementation
│       ├── input/                 # Test input files (if needed)
│       └── config.json            # Test configuration
├── feature/            # Refactored feature tests
│   ├── test_full_workflow/        # Self-contained test folder
│   │   ├── test_full_workflow.py  # Test implementation
│   │   ├── input/                 # Test input files (C/C++ source, model.json, etc.)
│   │   └── config.json            # Test configuration
│   ├── test_include_processing/   # Self-contained test folder
│   │   ├── test_include_processing.py # Test implementation
│   │   ├── input/                 # Test input files (C/C++ source, model.json, etc.)
│   │   └── config.json            # Test configuration
│   └── test_transformations/      # Self-contained test folder
│       ├── test_transformations.py # Test implementation
│       ├── input/                 # Test input files (C/C++ source, model.json, etc.)
│       └── config.json            # Test configuration
├── integration/        # Integration tests
│   ├── test_real_projects/        # Self-contained test folder
│   │   ├── test_real_projects.py  # Test implementation
│   │   ├── input/                 # Test input files (C/C++ source, model.json, etc.)
│   │   └── config.json            # Test configuration
│   └── test_performance/          # Self-contained test folder
│       ├── test_performance.py    # Test implementation
│       ├── input/                 # Test input files (C/C++ source, model.json, etc.)
│       └── config.json            # Test configuration
└── example/            # Keep existing example test (preserved as-is)
    ├── source/         # Example C/C++ source files
    ├── config.json     # Example configuration
    ├── test-example.py # Example workflow test
    └── test-example.json # Expected outputs specification
```

### 6. Boundary Separation and Component Isolation

#### 6.1 Test-Application Boundaries
**Priority: HIGH**

Ensure clean separation:
- **Tests only interact with public APIs**
- **No direct access to internal classes/functions**  
- **No mocking of internal components**
- **Tests validate behavior, not implementation**

#### 6.2 Component Boundary Testing
**Priority: MEDIUM**

Test component integration through public interfaces:
- Parser → Transformer → Generator pipeline
- Configuration loading and validation
- Error propagation and handling
- File I/O and output organization

### 7. Test Readability and Maintainability

#### 7.1 Standardized Test Patterns
**Priority: MEDIUM**

Common patterns for all tests:

```python
class TestFeatureName(UnifiedTestCase):
    def setUp(self):
        super().setUp()
        # Feature-specific setup
    
    def test_scenario_name(self):
        """Clear description of what this test validates"""
        # Arrange - Load from self-contained test folder
        test_input = self.data_factory.load_test_input(self.test_name)
        config = self.data_factory.load_test_config(self.test_name)
        
        # Act  
        result = self.executor.run_full_pipeline(test_input, config)
        
        # Assert - Model validation
        self.validator.assert_model_structure_valid(result.model)
        self.validator.assert_files_parsed(result.model, ["main.c", "utils.h"])
        self.validator.assert_struct_exists(result.model, "Point")
        self.validator.assert_function_exists(result.model, "main")
        
        # Assert - PlantUML validation
        self.validator.assert_puml_contains(result.puml, expected_elements)
        self.validator.assert_class_exists(result.puml, "MAIN", "source")
        self.validator.assert_relationship(result.puml, "MAIN", "HEADER_UTILS", "include")
```

#### 7.2 Documentation Standards
**Priority: LOW**

- **Clear test descriptions**: Each test explains what it validates
- **Setup documentation**: Complex test setups are well-documented
- **Expected behavior**: Tests clearly state expected outcomes
- **Failure diagnostics**: Useful error messages for test failures

### 8. Implementation Plan

#### Phase 1: Framework Foundation (Week 1-2)
1. Create `tests/framework/` structure
2. Implement `TestExecutor` with CLI interface
3. Implement basic `TestDataFactory`
4. Implement `ResultValidator` for models and PlantUML
5. Create `test-example.json` specification for the existing example test

#### Phase 2: Public API Migration (Week 3-4)
1. Identify tests using internal APIs (audit all 57 files, excluding preserved example)
2. Refactor high-priority unit tests to use public APIs
3. Create conversion utilities for existing test patterns
4. Update example test to use new validation framework while preserving its structure

#### Phase 3: Test Reorganization (Week 5-6)
1. Create self-contained test folders for each test file with `input/` subdirectory and `config.json`
2. Migrate test data into respective test folders (preserve `tests/example/` as-is)
3. Update test implementations to use `TestDataFactory.load_test_input()` and `load_test_config()`
4. Consolidate duplicate test logic and standardize naming conventions
5. Validate example test works with new framework

#### Phase 4: Validation and Cleanup (Week 7-8)
1. Ensure all tests pass with new framework
2. Performance testing of new test suite
3. Documentation updates and test coverage analysis
4. Remove deprecated test utilities

### 9. Success Criteria

#### Technical Criteria
- **Zero internal API usage**: All tests use only public APIs
- **100% test pass rate**: All migrated tests pass consistently  
- **Maintainable boundaries**: Clear separation between test and application code
- **Consistent patterns**: All tests follow unified structure and naming

#### Quality Criteria
- **Test readability**: Tests are easy to understand and modify
- **Failure diagnostics**: Test failures provide clear guidance
- **Coverage preservation**: No reduction in test coverage during migration
- **Performance**: Test suite execution time remains reasonable

#### Validation Criteria
- **Flexible to changes**: Tests continue passing when internal implementation changes
- **Comprehensive validation**: Tests validate all aspects of public API behavior
- **Realistic scenarios**: Tests cover real-world usage patterns
- **Error handling**: Tests validate error conditions and edge cases

### 10. Risk Mitigation

#### Migration Risks
- **Breaking existing tests**: Gradual migration with parallel test execution
- **Coverage gaps**: Careful mapping of existing test coverage to new structure
- **Performance degradation**: Monitoring test execution times during migration

#### Maintenance Risks  
- **Framework complexity**: Keep framework simple and well-documented
- **Over-abstraction**: Balance reusability with test clarity
- **Dependency management**: Minimize external dependencies in test framework

---

## Next Steps

1. **Review and approve** this plan with the development team
2. **Create `test-example.json`** specification for the existing example test
3. **Create framework foundation** in `tests/framework/`
4. **Start with pilot migration** of 5-10 representative test files (excluding the preserved example)
5. **Iterate and refine** framework based on pilot results
6. **Execute full migration** following the phase plan

This unified testing approach will ensure that c2puml remains flexible to internal changes while providing comprehensive validation of its public API functionality. The self-contained test structure with individual `input/` folders and `config.json` files provides excellent isolation and maintainability, while the preserved `tests/example/` serves as a reference implementation and comprehensive end-to-end test case.

## 🎯 Key Benefits of Self-Contained Test Structure

1. **Perfect Isolation**: Each test has its own `input/` folder and `config.json`, ensuring no cross-test interference
2. **Clear Organization**: Test data is co-located with test logic, making it easy to understand and maintain  
3. **Version Control Friendly**: Test data and logic evolve together, making changes easier to track and review
4. **Debugging Simplicity**: Each test environment is self-contained, making issue reproduction straightforward
5. **Maintainability**: Changes to one test's data cannot affect other tests, reducing maintenance overhead
6. **Framework Integration**: Tests use standardized `TestDataFactory` methods to load their data consistently