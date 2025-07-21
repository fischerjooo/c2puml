# C to PlantUML Converter - Testing Workflow

## Documentation Guidelines
- **Do not create new markdown files** - only edit existing markdown files
- Keep documentation concise and focused on practical usage
- Update this workflow.md file for any new workflow changes
- Use modern Python packaging with pyproject.toml

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

### Standard Workflow (Manual Steps)
```bash
# 0. Run all tests and check for errors
./run_all_tests.sh

# 1. Run example workflow (includes cleaning and generation)
./run_example.sh

# 2. Generate images from PlantUML files (optional)
./picgen.sh
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
- **Example Output**: Generated PlantUML diagrams in `./output`
- **Images**: JPEG images generated from PlantUML files using `picgen.sh`
- **Logs**: Processing logs and error reports

## Image Generation
The `picgen.sh` script converts all `.puml` files in the output directory to JPEG images:
- Requires PlantUML to be installed (`sudo apt-get install plantuml`)
- Optionally uses ImageMagick for PNG to JPEG conversion (`sudo apt-get install imagemagick`)
- Automatically cleans up temporary PNG files
- Generates high-quality JPEG images for documentation and sharing