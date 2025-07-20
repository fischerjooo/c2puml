# Testing Documentation

## Overview

This project uses a streamlined testing approach with a single entry point for all test executions. All feature-based tests are consolidated into one comprehensive test runner that can be executed both locally and in CI/CD environments.

## Test Structure

### Single Entry Point: `run_all_tests.py`

The main test runner is located at the project root: `run_all_tests.py`

This file contains all feature-based tests organized into a single test suite:

- **Parser Tests**: Basic C parsing functionality
- **Project Analysis Tests**: Project analysis and model generation
- **PlantUML Generation Tests**: Diagram generation functionality
- **Configuration Tests**: Configuration loading and validation
- **Workflow Tests**: Complete end-to-end workflow testing
- **Error Handling Tests**: Error scenarios and edge cases
- **Performance Tests**: Performance benchmarks with reasonable limits

## Running Tests

### Local Execution

```bash
# Run all feature tests
python run_all_tests.py

# Run with verbose output (default)
python run_all_tests.py
```

### CI/CD Execution

The GitHub workflow automatically runs the same command:

```yaml
- name: Run comprehensive feature tests
  run: |
    python run_all_tests.py
```

## Test Features

### 1. Parser Functionality
- C file parsing (structs, enums, functions, globals, includes, macros)
- Encoding detection
- Error handling for malformed files

### 2. Project Analysis
- Single and multiple file analysis
- Recursive directory scanning
- Model generation and serialization

### 3. PlantUML Generation
- Diagram content generation
- File output creation
- Configuration-based generation

### 4. Configuration Management
- JSON configuration loading
- Validation and error handling
- Filter application

### 5. Complete Workflow
- End-to-end testing from C files to PlantUML diagrams
- Model saving and loading
- Output verification

### 6. Error Handling
- Non-existent paths
- Empty directories
- Invalid configurations

### 7. Performance
- Analysis time measurement
- Reasonable performance limits
- Scalability testing

## Test Output

The test runner provides:

- **Verbose Output**: Detailed test execution information
- **Summary Report**: Test counts, failures, and errors
- **Clear Status**: ✅ for success, ❌ for failures
- **Exit Codes**: 0 for success, 1 for failures

## Benefits of Streamlined Approach

1. **Single Entry Point**: One command to run all tests
2. **Consistent Execution**: Same behavior locally and in CI/CD
3. **Feature-Focused**: Tests focus on user-facing functionality
4. **Maintainable**: All tests in one place, easy to understand
5. **Fast Execution**: No redundant test discovery or setup
6. **Clear Results**: Simple pass/fail reporting

## Test Files

The `tests/` directory now contains only:
- `README.md` - This documentation
- `test_files/` - Test data files used by the test runner

All test logic is consolidated in `run_all_tests.py` at the project root.

## Adding New Tests

To add new feature tests:

1. Add a new test method to the `FeatureTestSuite` class in `run_all_tests.py`
2. Follow the naming convention: `test_feature_<feature_name>`
3. Include proper setup/teardown in the test method
4. Add descriptive docstrings
5. Ensure the test is self-contained and doesn't depend on external state

## Example Test Structure

```python
def test_feature_new_functionality(self):
    """Test new feature functionality"""
    # Setup
    test_data = self.create_test_file("test.c", "int main() { return 0; }")
    
    # Execute
    result = some_function(test_data)
    
    # Verify
    self.assertEqual(result, expected_value)
    self.assertTrue(condition)
```