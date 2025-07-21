# C to PlantUML Converter - Testing Workflow

## Overview
Simple testing workflow for the C to PlantUML Converter using two main scripts.

## Testing Workflow

### Running Tests
```bash
# Run all tests
./run_all_tests.sh
```

### Running Examples
```bash
# Run example workflow
./run_example.sh
```

## Test Structure
- **Unit Tests** (`tests/unit/`): Test individual components
- **Feature Tests** (`tests/feature/`): Test complete workflows
- **Integration Tests** (`tests/integration/`): Test comprehensive scenarios

## Test Coverage
- C/C++ parsing functionality
- PlantUML diagram generation
- Model transformation and filtering
- Configuration loading and validation
- Include header processing
- Cross-platform encoding support
- Error handling and edge cases

## Output
- **Test Results**: Pass/fail status with detailed reporting
- **Example Output**: Generated PlantUML diagrams in `./plantuml_output`
- **Logs**: Processing logs and error reports