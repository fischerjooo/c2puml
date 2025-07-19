# Test Expectations System

This directory contains the test expectations system for the C to PlantUML converter. The expectations system provides a structured way to define and validate test assertions for different use cases and examples.

## Overview

The expectations system consists of:

1. **Base Expectations Class** (`base_expectations.py`) - Abstract base class defining the interface
2. **Specific Expectations Classes** - One for each use case/example
3. **Test Helper** (`../test_helper.py`) - Helper class that uses expectations to run tests
4. **Refactored Test Files** - Updated test files that use the expectations system

## Architecture

### BaseExpectations Class

The `BaseExpectations` class provides:
- Abstract methods for validation (`validate_project_structure`, `validate_file_content`, `validate_generated_output`)
- Helper methods for getting expected data (`get_expected_file_count`, `get_expected_functions`, etc.)
- Inherits from `unittest.TestCase` to provide assertion methods

### Specific Expectations Classes

Each use case has its own expectations class:

- `BasicProjectExpectations` - For basic project use case
- `ComplexTypedefExpectations` - For complex typedef use case
- `ConfigurationExpectations` - For configuration filtering use case
- `LargeCodebaseExpectations` - For large codebase use case
- `ErrorHandlingExpectations` - For error handling use case
- `IntegrationWorkflowExpectations` - For integration workflow example
- `ComplexExampleExpectations` - For complex example
- `TypedefTestExpectations` - For typedef test example
- `SampleExpectations` - For sample example

### UseCaseTestHelper Class

The `UseCaseTestHelper` class provides:
- Methods to run different types of tests using expectations
- Consistent test execution across different use cases
- Integration with the expectations system

## Benefits

1. **Separation of Concerns** - Test logic is separated from validation logic
2. **Reusability** - Expectations can be reused across different test scenarios
3. **Maintainability** - Changes to expected behavior only need to be made in one place
4. **Consistency** - All tests use the same validation patterns
5. **Readability** - Test files are much cleaner and easier to understand

## Usage

### Creating a New Expectations Class

1. Create a new file in the `expectations` directory
2. Inherit from `BaseExpectations`
3. Implement the required abstract methods
4. Add the class to `__init__.py`

Example:
```python
from .base_expectations import BaseExpectations

class MyUseCaseExpectations(BaseExpectations):
    def __init__(self):
        super().__init__("my_use_case")
    
    def validate_project_structure(self, model):
        # Validation logic here
        pass
    
    def validate_file_content(self, model):
        # Validation logic here
        pass
    
    def validate_generated_output(self, output_dir):
        # Validation logic here
        pass
```

### Using Expectations in Tests

```python
from .test_helper import UseCaseTestHelper
from .expectations import MyUseCaseExpectations

class TestMyUseCase(unittest.TestCase):
    def setUp(self):
        self.helper = UseCaseTestHelper(MyUseCaseExpectations)
    
    def test_my_use_case(self):
        self.helper.run_basic_analysis_test(self.project_dir, self)
```

## File Structure

```
tests/
├── expectations/
│   ├── __init__.py
│   ├── base_expectations.py
│   ├── basic_project_expectations.py
│   ├── complex_typedef_expectations.py
│   ├── configuration_expectations.py
│   ├── large_codebase_expectations.py
│   ├── error_handling_expectations.py
│   ├── integration_examples_expectations.py
│   └── README.md
├── test_helper.py
├── test_use_cases.py (refactored)
└── test_integration_examples.py (refactored)
```

## Migration Guide

The refactoring involved:

1. **Extracting Assertions** - Moving all assertions from test files to expectations classes
2. **Creating Helper Methods** - Adding helper methods to get expected data
3. **Updating Test Files** - Replacing inline assertions with calls to helper methods
4. **Maintaining Functionality** - Ensuring all tests still pass with the new structure

## Future Enhancements

Potential improvements to the expectations system:

1. **Data-Driven Testing** - Store expected data in JSON/YAML files
2. **Dynamic Expectations** - Generate expectations based on example content
3. **Validation Rules** - Add more sophisticated validation rules
4. **Test Generation** - Auto-generate tests from expectations
5. **Visualization** - Generate reports showing test coverage and expectations