# Testing Documentation for C to PlantUML Converter

This document provides comprehensive information about the testing infrastructure, patterns, and best practices for the C to PlantUML Converter project.

## Overview

The test suite has been modernized and consolidated to provide:
- **Consistent patterns** across all test modules
- **Reduced duplication** through shared utilities
- **Better organization** with clear separation of concerns
- **Enhanced reporting** with coverage and detailed output
- **Multiple test runners** supporting both unittest and pytest

## Test Structure

### Directory Organization

```
tests/
├── conftest.py                    # Pytest fixtures and configuration
├── utils.py                       # Shared test utilities and helpers
├── unit/                          # Unit tests - test individual components
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_parser.py
│   ├── test_include_processing_consolidated.py  # Consolidated include tests
│   └── ...
├── feature/                       # Feature tests - test complete workflows
│   ├── __init__.py
│   ├── base.py                    # Base class for feature tests
│   ├── test_cli_feature.py
│   └── ...
└── integration/                   # Integration tests - test comprehensive scenarios
    ├── __init__.py
    ├── test_include_processing_comprehensive.py
    └── ...
```

### Test Categories

#### Unit Tests (`tests/unit/`)
- Test individual components in isolation
- Fast execution (< 1 second per test)
- Mock external dependencies
- Focus on edge cases and error conditions

#### Feature Tests (`tests/feature/`)
- Test complete feature workflows
- End-to-end functionality testing
- Integration with external tools and files
- User-facing functionality validation

#### Integration Tests (`tests/integration/`)
- Test comprehensive scenarios
- Multiple component interactions
- Full pipeline testing
- Performance and scalability testing

## Running Tests

### Quick Start

```bash
# Run all tests with basic reporting
python run_all_tests.py

# Show test statistics
python run_all_tests.py --stats

# Run with verbose output
python run_all_tests.py --verbosity 3
```

### Advanced Usage

```bash
# Use pytest for enhanced features
python run_all_tests.py --pytest

# Run with coverage analysis
python run_all_tests.py --coverage

# Run only unit tests
python run_all_tests.py --pytest --category unit

# Run only feature tests
python run_all_tests.py --pytest --category feature

# Run coverage analysis only
python run_all_tests.py --coverage-only
```

### Using pytest directly

```bash
# Install testing dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=c_to_plantuml --cov-report=html

# Run specific categories
pytest -m unit          # Unit tests only
pytest -m feature       # Feature tests only
pytest -m integration   # Integration tests only

# Run with parallel execution
pytest -n auto

# Generate HTML report
pytest --html=test-report.html
```

## Test Infrastructure

### Shared Utilities (`tests/utils.py`)

The shared utilities module provides common functionality:

#### TestProjectBuilder
Creates test project structures fluently:

```python
from tests.utils import TestProjectBuilder

builder = TestProjectBuilder(temp_dir)
project_dir = (builder
    .add_c_file("main", "int main() { return 0; }")
    .add_h_file("types", "typedef struct { int x; } Point;")
    .add_config({"project_name": "test"})
    .build())
```

#### MockObjectFactory
Creates mock objects for testing:

```python
from tests.utils import MockObjectFactory

file_model = MockObjectFactory.create_file_model(
    filename="test.c",
    includes=["stdio.h", "types.h"]
)
```

#### AssertionHelpers
Provides specialized assertions:

```python
from tests.utils import AssertionHelpers

AssertionHelpers.assert_file_contains_includes(file_model, ["stdio.h"])
AssertionHelpers.assert_struct_exists(file_model, "Point")
```

#### TestDataProviders
Provides sample data for testing:

```python
from tests.utils import TestDataProviders

# Get sample C project
project_data = TestDataProviders.get_sample_c_projects()["complex_project"]

# Get sample configuration
config_data = TestDataProviders.get_sample_configs()["standard"]
```

### Pytest Fixtures (`tests/conftest.py`)

Common fixtures available in all tests:

```python
def test_example(temp_dir, file_factory, sample_config):
    # temp_dir: Temporary directory (auto-cleanup)
    # file_factory: Function to create test files
    # sample_config: Sample configuration data
    
    config_file = file_factory("config.json", json.dumps(sample_config))
    test_file = file_factory("test.c", "int main() { return 0; }")
```

### Base Classes

#### BaseFeatureTest
Base class for feature tests with common functionality:

```python
from tests.feature.base import BaseFeatureTest

class TestMyFeature(BaseFeatureTest):
    def test_something(self):
        project_data = self.get_sample_project("complex_project")
        config_data = self.get_sample_config("standard")
        # Test implementation...
```

## Test Patterns

### Unit Test Pattern

```python
import unittest
from unittest.mock import Mock, patch

from tests.utils import MockObjectFactory, AssertionHelpers

class TestMyComponent(unittest.TestCase):
    def setUp(self):
        self.component = MyComponent()
    
    def test_basic_functionality(self):
        # Arrange
        input_data = MockObjectFactory.create_file_model()
        
        # Act
        result = self.component.process(input_data)
        
        # Assert
        self.assertIsNotNone(result)
        AssertionHelpers.assert_struct_exists(result, "ExpectedStruct")
```

### Feature Test Pattern

```python
from tests.feature.base import BaseFeatureTest
from tests.utils import create_temp_project, run_full_pipeline

class TestMyFeature(BaseFeatureTest):
    def test_end_to_end_workflow(self):
        # Arrange
        project_data = self.get_sample_project("complex_project")
        config_data = self.get_sample_config("standard")
        
        project_dir = create_temp_project(project_data, self.temp_dir)
        
        # Act
        results = run_full_pipeline(project_dir, config_data)
        
        # Assert
        self.assertTrue(results["model_file"].exists())
        self.assertIsNotNone(results["parsed_model"])
```

### Integration Test Pattern

```python
import unittest
from tests.utils import TestDataProviders, run_full_pipeline, create_temp_project

class TestIntegration(unittest.TestCase):
    def test_comprehensive_scenario(self):
        # Test complex scenarios with multiple components
        project_data = TestDataProviders.get_sample_c_projects()["complex_project"]
        config_data = TestDataProviders.get_sample_configs()["advanced"]
        
        # Run full pipeline and verify results
        results = run_full_pipeline(project_dir, config_data)
        
        # Comprehensive assertions
        self.verify_parsing_results(results)
        self.verify_transformation_results(results)
        self.verify_generation_results(results)
```

## Coverage and Reporting

### Coverage Configuration

Coverage is configured in `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["c_to_plantuml"]
omit = ["*/tests/*", "*/test_*"]

[tool.coverage.report]
exclude_lines = ["pragma: no cover", "def __repr__"]
```

### Running Coverage

```bash
# With unittest
python run_all_tests.py --coverage-only

# With pytest
python run_all_tests.py --pytest --coverage

# Direct coverage command
coverage run -m unittest discover tests
coverage report -m
coverage html
```

### Test Reports

Multiple report formats are available:

- **Terminal output**: Standard test results
- **HTML coverage**: `htmlcov/index.html`
- **JUnit XML**: `test-results.xml`
- **HTML test report**: `test-report.html`

## Test Markers

Tests can be marked with pytest markers:

```python
import pytest

@pytest.mark.unit
def test_unit_functionality():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass

@pytest.mark.integration
def test_integration_scenario():
    pass
```

Available markers:
- `unit`: Unit tests
- `feature`: Feature tests
- `integration`: Integration tests
- `slow`: Tests taking > 5 seconds
- `network`: Tests requiring network access
- `external`: Tests depending on external resources
- `performance`: Performance and benchmark tests

## Best Practices

### Test Organization

1. **Keep tests focused**: One test should verify one specific behavior
2. **Use descriptive names**: Test names should describe what is being tested
3. **Follow AAA pattern**: Arrange, Act, Assert
4. **Use shared utilities**: Leverage the common test infrastructure
5. **Mock external dependencies**: Keep tests isolated and fast

### Test Data

1. **Use TestDataProviders**: For consistent sample data
2. **Create minimal test cases**: Only include necessary data
3. **Use factories**: For creating test objects
4. **Clean up resources**: Always clean up temporary files

### Performance

1. **Keep unit tests fast**: < 1 second per test
2. **Mark slow tests**: Use `@pytest.mark.slow`
3. **Use parallel execution**: `pytest -n auto`
4. **Mock expensive operations**: Database, network, file I/O

### Maintenance

1. **Regular cleanup**: Remove obsolete tests
2. **Update shared utilities**: When patterns emerge
3. **Maintain coverage**: Keep above 80%
4. **Review test failures**: Fix flaky tests promptly

## Migration Guide

### From Old Test Structure

If you have old test files that need updating:

1. **Import shared utilities**:
   ```python
   from tests.utils import TestProjectBuilder, AssertionHelpers
   ```

2. **Use base classes**:
   ```python
   from tests.feature.base import BaseFeatureTest
   ```

3. **Replace duplicated code**:
   ```python
   # Old way
   temp_dir = tempfile.mkdtemp()
   
   # New way
   project_dir = self.temp_dir  # From base class
   ```

4. **Use factories for test data**:
   ```python
   # Old way
   file_model = FileModel()
   file_model.filename = "test.c"
   
   # New way
   file_model = MockObjectFactory.create_file_model("test.c")
   ```

### Cleanup Process

Use the cleanup script to remove redundant tests:

```bash
python cleanup_redundant_tests.py
```

This will:
- Identify redundant test files
- Create backups before deletion
- Generate a cleanup report
- Remove consolidated files safely

## Troubleshooting

### Common Issues

1. **Import errors**:
   - Ensure `requirements-dev.txt` is installed
   - Check Python path configuration

2. **Test failures**:
   - Run with verbose output: `python run_all_tests.py -v 3`
   - Check temporary directory permissions
   - Verify test data setup

3. **Coverage issues**:
   - Ensure source code is in the correct location
   - Check coverage configuration in `pyproject.toml`
   - Verify file patterns are correct

4. **Performance issues**:
   - Use parallel execution: `pytest -n auto`
   - Profile slow tests: `pytest --durations=10`
   - Mock expensive operations

### Getting Help

1. Check the test output for detailed error messages
2. Run with maximum verbosity for debugging
3. Review the test cleanup report if you removed files
4. Check the backup directory for original test files

## Future Improvements

Planned enhancements to the test suite:

1. **Property-based testing** with Hypothesis
2. **Performance benchmarking** with pytest-benchmark
3. **Mutation testing** for test quality assessment
4. **Continuous integration** pipeline optimization
5. **Test result trending** and analysis