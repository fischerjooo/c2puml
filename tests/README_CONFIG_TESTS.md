# Configuration Model Manipulation Tests

This directory contains comprehensive automated tests for the configuration-based model manipulation system in the C to PlantUML converter.

## Overview

The configuration system allows users to:
- Filter files and code elements using regex patterns
- Transform element names using regex-based renaming
- Add new elements (structs, enums, functions) to the model
- Combine multiple configuration files

## Test Files

### 1. `test_config_manipulations.py`
**Unit tests for the core configuration functionality**

Tests the `ModelTransformer` and `JSONManipulator` classes with synthetic test data:

- **File Filter Tests**: Verify that files are correctly included/excluded based on regex patterns
- **Element Filter Tests**: Test filtering of structs, enums, functions, and globals
- **Transformation Tests**: Verify regex-based renaming of elements
- **Addition Tests**: Test adding new elements to the model
- **Multiple Config Tests**: Test loading and merging multiple configuration files
- **Error Handling Tests**: Test invalid configurations and error conditions
- **Performance Tests**: Verify performance with large configurations
- **Pattern Compilation Tests**: Test regex pattern compilation and caching

### 2. `test_config_integration.py`
**Integration tests using real configuration files**

Tests the configuration system with actual configuration files from the `config/` directory:

- **Real Config Tests**: Use actual `file_filters.json`, `element_filters.json`, etc.
- **Complete Workflow Tests**: Test the full analysis → transformation → generation pipeline
- **Multiple Config Integration**: Test combining multiple real configuration files
- **Serialization Tests**: Verify that transformed models can be saved and loaded
- **Performance Integration**: Test performance with real configuration files

### 3. `test_config_cli.py`
**CLI interface tests**

Tests the command-line interface for configuration operations:

- **Config Command Tests**: Test the `config` subcommand
- **Filter Command Tests**: Test the `filter` subcommand
- **Subprocess Tests**: Test CLI through subprocess calls
- **Error Handling**: Test CLI error conditions
- **Help Output**: Verify help documentation

### 4. `test_config.json`
**Test configuration file**

A comprehensive test configuration file that includes:
- File filtering patterns
- Element filtering patterns
- Transformation rules
- Addition definitions

## Running the Tests

### Run All Configuration Tests
```bash
python3 run_tests.py
```

### Run Individual Test Suites
```bash
# Unit tests
python3 -m unittest tests.test_config_manipulations -v

# Integration tests
python3 -m unittest tests.test_config_integration -v

# CLI tests
python3 -m unittest tests.test_config_cli -v
```

### Run Specific Test Methods
```bash
# Test file filtering
python3 -m unittest tests.test_config_manipulations.TestConfigurationManipulations.test_file_filter_configuration -v

# Test transformations
python3 -m unittest tests.test_config_manipulations.TestConfigurationManipulations.test_transformation_configuration -v

# Test CLI filter command
python3 -m unittest tests.test_config_cli.TestConfigurationCLI.test_filter_command_with_test_config -v
```

## Test Coverage

### Configuration Features Tested

#### File Filtering
- ✅ Include patterns (e.g., `.*\.c$`, `.*\.h$`)
- ✅ Exclude patterns (e.g., `.*test.*`, `.*temp.*`)
- ✅ Pattern compilation and caching
- ✅ Multiple pattern matching

#### Element Filtering
- ✅ Struct filtering with include/exclude patterns
- ✅ Enum filtering with include/exclude patterns
- ✅ Function filtering with include/exclude patterns
- ✅ Global variable filtering with include/exclude patterns
- ✅ Regex pattern matching for element names

#### Transformations
- ✅ Struct renaming with regex patterns
- ✅ Enum renaming with regex patterns
- ✅ Function renaming with regex patterns
- ✅ Capture group usage in replacement strings
- ✅ Multiple transformation rules
- ✅ Order of transformation application

#### Additions
- ✅ Adding structs with fields
- ✅ Adding enums with values
- ✅ Adding functions with parameters
- ✅ Target file pattern matching
- ✅ Field type and array size specifications

#### Multiple Configuration Files
- ✅ Loading multiple config files
- ✅ Merging configurations
- ✅ Conflict resolution
- ✅ Performance with multiple files

#### Error Handling
- ✅ Invalid JSON files
- ✅ Missing configuration files
- ✅ Empty configurations
- ✅ Malformed patterns
- ✅ CLI error conditions

#### Performance
- ✅ Large configuration loading time
- ✅ Model transformation time
- ✅ Pattern compilation caching
- ✅ Memory usage with large models

### CLI Interface Tested

#### Commands
- ✅ `config` command with configuration files
- ✅ `filter` command with single config file
- ✅ `filter` command with multiple config files
- ✅ `filter` command with output file specification
- ✅ Help output for all commands

#### Error Conditions
- ✅ Non-existent model files
- ✅ Non-existent configuration files
- ✅ Invalid JSON in configuration files
- ✅ Missing required arguments

#### Subprocess Integration
- ✅ CLI execution through subprocess
- ✅ Command-line argument parsing
- ✅ Output file generation
- ✅ Return code handling

## Test Data

### Synthetic Test Models
The tests create comprehensive test models with:
- Multiple structs with various naming patterns
- Multiple enums with different naming conventions
- Functions with different prefixes and suffixes
- Global variables with different naming patterns
- Files with different extensions and naming patterns

### Test Configuration Files
- `tests/test_config.json`: Comprehensive test configuration
- Real configuration files from `config/` directory
- Temporary configuration files created during tests

## Test Utilities

### Helper Methods
- `_create_test_model()`: Creates synthetic test models
- `_create_temp_config()`: Creates temporary configuration files
- `_create_temp_output()`: Creates temporary output files
- `_create_test_model_file()`: Creates test model files for CLI testing

### Mock Objects
- Mock arguments for CLI testing
- Mock models for integration testing
- Mock file system operations

## Continuous Integration

The tests are designed to run in CI/CD environments:
- No external dependencies beyond the project itself
- Temporary file cleanup in tearDown methods
- Skip tests when required files are not available
- Timeout handling for long-running operations
- Comprehensive error reporting

## Debugging Tests

### Common Issues
1. **Import Errors**: Ensure the project is in the Python path
2. **File Not Found**: Check that configuration files exist
3. **Permission Errors**: Ensure write permissions for temporary files
4. **Timeout Errors**: Increase timeout values for slow systems

### Debug Mode
Run tests with verbose output:
```bash
python3 -m unittest tests.test_config_manipulations -v -f
```

### Isolated Testing
Test individual components:
```bash
# Test only the ModelTransformer
python3 -c "
from c_to_plantuml.manipulators.model_transformer import ModelTransformer
transformer = ModelTransformer()
print('ModelTransformer imported successfully')
"
```

## Extending the Tests

### Adding New Test Cases
1. Add test methods to existing test classes
2. Use descriptive method names starting with `test_`
3. Include comprehensive assertions
4. Clean up temporary files in tearDown

### Adding New Test Files
1. Create new test file with `test_` prefix
2. Inherit from `unittest.TestCase`
3. Add to the test runner in `run_tests.py`
4. Update this documentation

### Test Configuration Patterns
When adding new tests, consider:
- Edge cases and boundary conditions
- Error conditions and exception handling
- Performance implications
- Integration with existing functionality
- CLI interface compatibility

## Performance Benchmarks

The tests include performance benchmarks:
- Configuration loading: < 2 seconds for multiple files
- Model transformation: < 1 second for typical models
- Pattern compilation: < 0.1 seconds for 100+ patterns
- Memory usage: < 100MB for large models

## Contributing

When contributing to the configuration system:
1. Add tests for new features
2. Update existing tests for changed functionality
3. Ensure all tests pass before submitting
4. Update this documentation
5. Consider performance implications
6. Test with real configuration files