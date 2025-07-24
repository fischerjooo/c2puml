# C to PlantUML Converter - Testing Workflow

## Documentation Guidelines
- **Do not create new markdown files** - only edit existing markdown files
- Keep documentation concise and focused on practical usage
- Update this workflow.md file for any new workflow changes
- Use modern Python packaging with pyproject.toml

## Overview
Comprehensive testing workflow for the C to PlantUML Converter using three main scripts with distinct purposes.

## Processing Flow
1. **Parse C/C++ files** and generate model.json
2. **Verify model sanity** - perform sanity checks on parsed values
3. **Transform model** based on configuration
4. **Generate PlantUML files** from the transformed model

## Testing Workflow

### Regression Testing (Full System Test)
```bash
# Run complete regression testing - validates entire system
./run_all.sh
```
**Purpose**: Full system validation including tests, examples, and image generation. Use for:
- Final validation before releases
- Complete system regression testing
- End-to-end workflow verification

### Debugging and Development Testing
```bash
# Run debugging-focused tests with detailed output
./run_all_tests.sh
```
**Purpose**: Focused testing for debugging and development. Use for:
- Debugging specific issues
- Development iteration
- Unit and integration test validation
- Detailed error reporting

### Spiking and Integration Testing
```bash
# Run example workflow for spiking and integration testing
./run_example.sh
```
**Purpose**: Spiking new features and integration testing. Use for:
- Testing new C code preprocessing features
- Integration testing with new source files
- Validating preprocessing directives (#if, #elif, #else, #endif)
- Testing edge cases in typedefs and macros

### Standard Workflow (Manual Steps)
```bash
# 0. For debugging: Run focused tests
./run_all_tests.sh

# 1. For spiking: Run example workflow (includes cleaning and generation)
./run_example.sh

# 2. For regression: Run complete system test
./run_all.sh

# 3. Generate images from PlantUML files (optional)
./picgen.sh

# 4. Review generated output (optional)
# Examine the generated PlantUML diagrams and images

# 5. Update specification.md if needed
# Always review and update specification.md with any new findings or changes

# 6. Development or extend tests for new feature or feature change
# Add new tests or modify existing tests based on feature development

## Testing Guidelines

### Bug Fixing Workflow
- **Before fixing a bug**: Develop a test that reproduces the bug if it makes sense
- Write a failing test that demonstrates the issue
- Fix the bug to make the test pass
- This ensures the bug is properly understood and won't regress

### New Feature Development
- **After developing a new feature**: Always add comprehensive tests for it
- Include unit tests for individual components
- Add integration tests for complete workflows
- Test both normal cases and edge cases
- Ensure the feature works as expected and doesn't break existing functionality
```

## Test Structure
- **Unit Tests** (`tests/unit/`): Test individual components
- **Feature Tests** (`tests/feature/`): Test complete workflows
- **Integration Tests** (`tests/integration/`): Test comprehensive scenarios
- **Preprocessing Tests** (`example/source/preprocessed.c`): Test C preprocessing directives

## Test Coverage
- C/C++ parsing functionality
- **Model verification and sanity checks**
- PlantUML diagram generation
- Model transformation and filtering
- Configuration loading and validation
- Include header processing
- Cross-platform encoding support
- Error handling and edge cases
- **C preprocessing directives** (#if, #elif, #else, #endif)
- **Preprocessing in typedefs and macros**
- **Edge cases in conditional compilation**

## Output
- **Test Results**: Pass/fail status with detailed reporting
- **Example Output**: Generated PlantUML diagrams in `./output`
- **Images**: JPEG images generated from PlantUML files using `picgen.sh`
- **Logs**: Processing logs and error reports
- **Preprocessing Validation**: Detection of preprocessing directive issues

## Image Generation
The `picgen.sh` script converts all `.puml` files in the output directory to JPEG images:
- Requires PlantUML to be installed (`sudo apt-get install plantuml`)
- Optionally uses ImageMagick for PNG to JPEG conversion (`sudo apt-get install imagemagick`)
- Automatically cleans up temporary PNG files
- Generates high-quality JPEG images for documentation and sharing

## Preprocessing Testing
The workflow includes testing for C preprocessing directives:
- **preprocessed.c**: Contains edge cases and examples for preprocessing
- **preprocessed.h**: Header file with preprocessing directives in typedefs
- **Validation**: assertions.py includes checks for preprocessing directive processing
- **Bug Detection**: Tests designed to detect preprocessing-related issues before fixes