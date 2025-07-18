# Testing Documentation

This directory contains comprehensive tests for the C to PlantUML converter project.

## Test Structure

```
tests/
├── test_parser.py          # Parser functionality tests
├── test_project_analyzer.py # Project analysis tests
├── test_config.py          # Configuration functionality tests
├── test_generator.py       # PlantUML generation tests
├── test_integration.py     # Complete workflow tests
├── test_files/             # Test input files
│   ├── sample.c
│   ├── sample.h
│   ├── complex_example.c
│   └── complex_example.h
├── test_output/            # Expected output files
│   └── expected_main.puml
├── test_config.json        # Test configuration
├── run_tests.py           # Test runner script
└── README.md              # This file
```

## Test Categories

### Unit Tests
- **test_parser.py**: Tests the C/C++ parser functionality
  - Parsing structs, enums, functions, macros, typedefs
  - Encoding detection and error handling
  - Edge cases and complex C constructs

- **test_config.py**: Tests configuration handling
  - Loading and validation of JSON configuration files
  - File and element filtering functionality
  - Configuration transformation and serialization

- **test_generator.py**: Tests PlantUML generation
  - Diagram content generation
  - File output and formatting
  - Error handling and edge cases

### Integration Tests
- **test_project_analyzer.py**: Tests project analysis workflow
  - Multi-file project analysis
  - Recursive directory scanning
  - Model serialization and deserialization

- **test_integration.py**: Tests complete end-to-end workflows
  - Manual workflow (analyze → generate)
  - Configuration-based workflow
  - Filtering and transformation workflows
  - Performance testing with larger projects

## Running Tests

### Run All Tests
```bash
python3 tests/run_tests.py
```

### Run Specific Test Module
```bash
python3 tests/run_tests.py test_config
python3 tests/run_tests.py test_parser
python3 tests/run_tests.py test_generator
python3 tests/run_tests.py test_integration
```

### Run with unittest directly
```bash
python3 -m unittest discover tests/
python3 -m unittest tests.test_config
```

## Test Data

### Input Files (test_files/)
- **sample.c/h**: Simple C file with basic constructs
- **complex_example.c/h**: More complex C file with advanced features

### Expected Output (test_output/)
- **expected_main.puml**: Expected PlantUML output for verification

### Configuration (test_config.json)
- Sample configuration file for testing configuration functionality

## Test Coverage

The test suite provides comprehensive coverage for:

1. **Parser Functionality**
   - C/C++ syntax parsing
   - Struct and enum definitions
   - Function declarations
   - Macro and typedef handling
   - Include statement parsing
   - Global variable detection

2. **Configuration System**
   - JSON configuration loading
   - Validation and error handling
   - File filtering (include/exclude patterns)
   - Element filtering (structs, enums, functions, globals)
   - Configuration serialization

3. **PlantUML Generation**
   - Diagram structure generation
   - Proper UML notation
   - File output and formatting
   - Error handling

4. **Integration Workflows**
   - Complete analysis workflows
   - Configuration-based processing
   - Model transformation and filtering
   - Performance testing

## Adding New Tests

When adding new functionality, follow these guidelines:

1. **Create unit tests** for individual components
2. **Add integration tests** for complete workflows
3. **Include test data** in test_files/ if needed
4. **Update this README** with new test categories

### Test Naming Convention
- Test methods: `test_<functionality>_<scenario>`
- Test classes: `Test<ComponentName>`

### Test Structure
```python
def test_functionality_scenario(self):
    """Test description"""
    # Setup
    # Execute
    # Verify
```

## Continuous Integration

The test suite is designed to run in CI/CD environments:
- All tests are self-contained
- No external dependencies beyond the project itself
- Tests clean up after themselves
- Exit codes indicate success/failure

## Troubleshooting

### Common Issues
1. **Import errors**: Ensure the project root is in Python path
2. **File not found**: Check that test files exist in test_files/
3. **Permission errors**: Ensure write access to temp directories

### Debug Mode
Run tests with verbose output:
```bash
python3 -m unittest discover tests/ -v
```