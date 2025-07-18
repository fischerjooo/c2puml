# Test Setup Guide

This guide explains how to use the new Python-based test suite that consolidates all GitHub workflow test logic into local Python scripts.

## Overview

The test complexity from the GitHub workflow (`test.yml`) has been moved into Python scripts that can be run locally. This provides:

- **Local Execution**: All tests can be run locally without GitHub Actions
- **Better Debugging**: Python scripts provide better error handling and debugging
- **Modular Design**: Tests can be run individually or in groups
- **Consistent Environment**: Same test logic runs locally and in CI
- **Better Reporting**: Detailed test reports and metrics

## Test Scripts

### 1. `enhanced_test_runner.py` - Main Test Suite

This is the primary test runner that consolidates all GitHub workflow logic into a comprehensive Python test suite.

**Features:**
- Environment setup (package installation, dependency management)
- Linting tests (flake8 syntax and style checks)
- Unit tests (all individual module tests)
- Integration tests (full workflow testing)
- Output validation (file creation and content verification)
- CLI tool tests (command-line interface testing)
- Performance tests (benchmarking and timing tests)
- Complex integration tests (multi-file project testing)

**Usage:**
```bash
# Run all tests (equivalent to GitHub workflow)
python enhanced_test_runner.py

# Run specific test categories
python enhanced_test_runner.py --category unit
python enhanced_test_runner.py --category integration
python enhanced_test_runner.py --category performance
python enhanced_test_runner.py --category linting
python enhanced_test_runner.py --category workflow
python enhanced_test_runner.py --category verification
python enhanced_test_runner.py --category cli
python enhanced_test_runner.py --category complex

# Available categories:
# - linting: Code quality and style checks
# - discovery: Test file discovery
# - unit: Unit tests
# - comprehensive: Full test suite
# - workflow: Complete workflow testing
# - verification: Output file validation
# - cli: Command-line interface tests
# - performance: Performance benchmarks
# - complex: Complex integration tests
# - all: All tests (default)
```

### 2. `quick_test.py` - Fast Local Testing

A simplified version for quick local testing during development.

**Features:**
- Basic syntax checks
- Core unit tests (parser and project analyzer)
- Basic integration test
- Output validation
- CLI tool test

**Usage:**
```bash
# Run quick tests for development
python quick_test.py
```

### 3. `run_tests.py` - Original Test Suite

The original comprehensive test runner (still available for backward compatibility).

**Usage:**
```bash
# Run original test suite
python run_tests.py
```

## Setup Instructions

### 1. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate     # On Windows
```

### 2. Install Dependencies

```bash
# Install package in development mode
pip install -e .

# Install additional requirements
pip install -r requirements.txt
```

### 3. Run Tests

```bash
# Quick test (recommended for development)
python quick_test.py

# Full test suite (equivalent to GitHub workflow)
python enhanced_test_runner.py

# Specific test categories
python enhanced_test_runner.py --category unit
python enhanced_test_runner.py --category integration
```

## Test Categories Explained

### Linting Tests
- **Purpose**: Code quality and style checks
- **Tools**: flake8 for syntax errors and style violations
- **GitHub Workflow Equivalent**: "Lint with flake8" step

### Unit Tests
- **Purpose**: Individual module functionality testing
- **Coverage**: Parser, Project Analyzer, Configuration modules
- **GitHub Workflow Equivalent**: "Run unit tests with verbose output" step

### Integration Tests
- **Purpose**: End-to-end workflow testing
- **Coverage**: Full analysis and generation pipeline
- **GitHub Workflow Equivalent**: "Test complete workflow" step

### Output Validation
- **Purpose**: Verify generated files and content
- **Coverage**: Model files, PlantUML diagrams, directory structure
- **GitHub Workflow Equivalent**: "Verify output files" step

### CLI Tools
- **Purpose**: Command-line interface testing
- **Coverage**: Analysis and generation commands
- **GitHub Workflow Equivalent**: "Test CLI tools" step

### Performance Tests
- **Purpose**: Performance benchmarking
- **Coverage**: Analysis speed, memory usage
- **GitHub Workflow Equivalent**: "Performance benchmark" step

### Complex Integration
- **Purpose**: Multi-file project testing
- **Coverage**: Complex project structures, multiple configurations
- **GitHub Workflow Equivalent**: "Complex integration test" step

## Output and Artifacts

### Test Output Directory
The enhanced test runner creates a `test_output` directory (configurable) containing:
- Generated test projects
- Temporary files
- Test artifacts

### Generated Files
Tests generate various files that are validated:
- `test_project_model.json`: Project analysis model
- `test_plantuml_output/`: PlantUML diagram files
- `complex_model.json`: Complex integration test model
- `complex_output/`: Complex test PlantUML files

## Troubleshooting

### Common Issues

1. **Virtual Environment Issues**
   ```bash
   # Ensure virtual environment is activated
   source venv/bin/activate
   
   # Reinstall package
   pip install -e . --force-reinstall
   ```

2. **Missing Dependencies**
   ```bash
   # Install all requirements
   pip install -r requirements.txt
   
   # Install additional tools
   pip install flake8
   ```

3. **Permission Issues**
   ```bash
   # Make scripts executable
   chmod +x enhanced_test_runner.py
   chmod +x quick_test.py
   ```

4. **Test Failures**
   ```bash
   # Run with verbose output
   python enhanced_test_runner.py --verbose
   
   # Run specific failing category
   python enhanced_test_runner.py --category unit
   ```

### Debug Mode

For detailed debugging, run tests with verbose output:
```bash
python enhanced_test_runner.py --verbose
```

## Integration with CI/CD

The enhanced test runner can be easily integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run Enhanced Tests
  run: |
    python3 -m venv venv
    source venv/bin/activate
    pip install -e .
    pip install -r requirements.txt
    python enhanced_test_runner.py
```

## Benefits of New Test Setup

1. **Local Development**: Run the same tests locally that run in CI
2. **Faster Feedback**: Quick tests for development, full suite for validation
3. **Better Debugging**: Python scripts provide detailed error information
4. **Modular Testing**: Run specific test categories as needed
5. **Consistent Results**: Same test logic across local and CI environments
6. **Maintainable**: Python code is easier to maintain than shell scripts
7. **Extensible**: Easy to add new test categories or modify existing ones

## Migration from GitHub Workflow

The enhanced test runner replicates all GitHub workflow test steps:

| GitHub Workflow Step | Enhanced Test Runner |
|---------------------|---------------------|
| Environment Setup | `setup_environment()` |
| Linting | `run_linting_tests()` |
| Unit Tests | `run_unit_tests()` |
| Integration Tests | `test_complete_workflow()` |
| Output Validation | `verify_output_files()` |
| CLI Tests | `test_cli_tools()` |
| Performance Tests | `run_performance_benchmark()` |
| Complex Integration | `run_complex_integration_test()` |

## Next Steps

1. **Update CI/CD**: Replace GitHub workflow steps with calls to enhanced test runner
2. **Add New Tests**: Extend the test suite with additional categories
3. **Customize**: Modify test parameters and thresholds as needed
4. **Document**: Add project-specific test documentation

## Support

For issues with the test setup:
1. Check the troubleshooting section above
2. Run tests with verbose output for detailed error messages
3. Review the test script source code for implementation details
4. Check the original GitHub workflow for reference