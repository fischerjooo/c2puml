# Testing Documentation

## Overview

This project uses a comprehensive testing approach with a single entry point for all test executions. The test suite includes both unit tests and feature tests, all consolidated into one comprehensive test runner that can be executed both locally and in CI/CD environments.

## Test Structure

### Single Entry Point: `run_all_tests.py`

The main test runner is located at the project root: `run_all_tests.py`

This file orchestrates both unit tests and feature tests:

#### Unit Tests (from `tests/` directory):
- **Parser Tests** (`test_parser.py`): C file parsing (structs, enums, functions, globals, includes, macros, typedefs)
- **Project Analyzer Tests** (`test_project_analyzer.py`): Project analysis, model generation, file filtering
- **Generator Tests** (`test_generator.py`): PlantUML diagram generation and output validation
- **Configuration Tests** (`test_config.py`): Configuration loading, validation, and filtering

#### Feature Tests (integrated in `run_all_tests.py`):
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

## Test Coverage

### Unit Tests (41 tests)
Detailed testing of individual components:

#### 1. Parser Functionality (11 tests)
- C file parsing (structs, enums, functions, globals, includes, macros, typedefs)
- Encoding detection and handling
- Complete file parsing with all elements
- Error handling for malformed files

#### 2. Project Analysis (10 tests)
- Single and multiple file analysis
- Recursive directory scanning
- Model generation and serialization
- File filtering and error handling
- Relative path calculation

#### 3. PlantUML Generation (12 tests)
- Diagram content generation
- File output creation
- Configuration-based generation
- Multiple file generation
- Error handling and syntax validation
- Special character handling

#### 4. Configuration Management (8 tests)
- JSON configuration loading and validation
- File and element filtering
- Save/load functionality
- Default value handling
- Error handling for invalid patterns

### Feature Tests (7 tests)
High-level testing of user-facing functionality:

#### 1. Parser Functionality
- Basic C parsing functionality

#### 2. Project Analysis
- Project analysis and model generation

#### 3. PlantUML Generation
- Diagram generation functionality

#### 4. Configuration Management
- Configuration loading and validation

#### 5. Complete Workflow
- End-to-end testing from C files to PlantUML diagrams
- Model saving and loading
- Output verification

#### 6. Error Handling
- Non-existent paths
- Empty directories
- Invalid configurations

#### 7. Performance
- Analysis time measurement
- Reasonable performance limits
- Scalability testing

## Test Output

The test runner provides:

- **Comprehensive Output**: Both unit tests and feature tests with detailed execution information
- **Separate Sections**: Clear separation between unit tests and feature tests
- **Summary Report**: Total test counts, failures, and errors for both test types
- **Clear Status**: ✅ for success, ❌ for failures
- **Exit Codes**: 0 for success, 1 for failures

## Benefits of Comprehensive Approach

1. **Single Entry Point**: One command to run all tests (unit + feature)
2. **Comprehensive Coverage**: Both detailed unit tests and high-level feature tests
3. **Consistent Execution**: Same behavior locally and in CI/CD
4. **Maintainable**: Organized test structure with clear separation
5. **Fast Execution**: Efficient test discovery and execution
6. **Clear Results**: Detailed reporting with separate unit and feature test results

## Test Files

The `tests/` directory contains:
- `README.md` - This documentation
- `test_files/` - Test data files used by the test runner
- `test_parser.py` - Unit tests for C parser functionality
- `test_project_analyzer.py` - Unit tests for project analysis
- `test_generator.py` - Unit tests for PlantUML generation
- `test_config.py` - Unit tests for configuration management

The `run_all_tests.py` file at the project root orchestrates both unit tests and feature tests.

## Adding New Tests

### Adding Feature Tests:
1. Add a new test method to the `FeatureTestSuite` class in `run_all_tests.py`
2. Follow the naming convention: `test_feature_<feature_name>`
3. Include proper setup/teardown in the test method
4. Add descriptive docstrings
5. Ensure the test is self-contained and doesn't depend on external state

### Adding Unit Tests:
1. Add a new test method to the appropriate test class in the `tests/` directory
2. Follow the naming convention: `test_<functionality>_<scenario>`
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