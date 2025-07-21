# C to PlantUML Converter - Workflow Guide

## Overview
The C to PlantUML Converter follows a simple 3-step workflow for converting C/C++ source code to PlantUML diagrams with advanced filtering and transformation capabilities.

## Documentation Guidelines
- **Do not create new markdown files** - only edit existing markdown files
- Keep documentation concise and focused on practical usage
- Update this workflow.md file for any new workflow changes
- Use modern Python packaging with pyproject.toml

## Processing Workflow

### Step 1: Parse
Parse C/C++ source files and generate a JSON model (`model.json`).

**Important**: The parser performs essential file filtering (hidden files, common exclude patterns) but does NOT perform model element filtering. All model elements are preserved for the transformer step.

```bash
python3 main.py parse ./src
```

### Step 2: Transform (Optional)
Transform the model based on configuration rules. This step handles:
- User-configured file filtering
- Model element filtering (structs, enums, unions, functions, etc.)
- Model transformations (rename, add, remove elements)
- File selection for transformer actions (apply to all files or selected ones)
- Include depth processing

```bash
python3 main.py transform model.json config.json
```

### Step 3: Generate
Generate PlantUML diagrams from the model.

```bash
python3 main.py generate model.json ./output
```

### Complete Workflow
Run all steps in sequence using a configuration file:

```bash
python3 main.py workflow ./src config.json
```

## Configuration Features

### File Selection for Transformer Actions
The transformer supports applying actions to all model files or only selected ones:

```json
{
  "transformations": {
    "file_selection": {
      "selected_files": [".*main\\.c$", ".*utils\\.c$"]
    },
    "rename": {
      "structs": {
        "old_name": "new_name"
      }
    }
  }
}
```

- **`selected_files`**: List of regex patterns for files to apply transformations to
- **Empty list or missing field**: Applies transformations to all files
- **Non-empty list**: Applies transformations only to files matching the patterns

#### File Selection Examples

**Apply to all files (default):**
```json
{
  "transformations": {
    "rename": {
      "structs": {
        "old_name": "new_name"
      }
    }
  }
}
```

**Apply to specific files:**
```json
{
  "transformations": {
    "file_selection": {
      "selected_files": [".*main\\.c$", ".*utils\\.c$"]
    },
    "rename": {
      "structs": {
        "old_name": "new_name"
      }
    }
  }
}
```

**Apply to files in a directory:**
```json
{
  "transformations": {
    "file_selection": {
      "selected_files": [".*src/core/.*\\.c$"]
    },
    "rename": {
      "structs": {
        "old_name": "new_name"
      }
    }
  }
}
```

### Filtering Separation
- **Parser Step**: Essential file filtering (hidden files, common exclude patterns)
- **Transformer Step**: User-configured file filtering and model element filtering

## Testing Workflow

### Running Tests
```bash
# Run all tests (recommended)
python run_all_tests.py

# Run with shell script
./run_all_tests.sh

# Run specific test categories
python run_all_tests.py unit
python run_all_tests.py feature
python run_all_tests.py integration

# Run with shell script for specific categories
./run_all_tests.sh unit
./run_all_tests.sh feature
./run_all_tests.sh integration

# Run individual test modules
python -m unittest tests.unit.test_parser
python -m unittest tests.unit.test_generator
python -m unittest tests.feature.test_integration
```

### Test Runner
The `run_all_tests.py` script provides a simple and elegant test execution:
- Uses unittest discovery to automatically find all test files
- Runs both unit and feature tests
- Provides clear test summary with pass/fail status
- Works consistently across different environments

### Test Structure
- **Unit Tests** (`tests/unit/`): Test individual components in isolation
  - **Parser Tests**: Test C/C++ parsing functionality
  - **User Configurable Filtering Tests**: Test user-configurable filtering via config.json
  - **Generator Tests**: Test PlantUML diagram generation
  - **Transformer Tests**: Test model transformation and filtering
  - **Config Tests**: Test configuration loading and validation
  - **Include Processing Tests**: Test include header processing and relationship generation
- **Feature Tests** (`tests/feature/`): Test complete workflows and integrations
  - **Integration Tests**: Test complete workflows from parsing to diagram generation
  - **Parser Feature Tests**: Test parser features and edge cases
  - **Generator Feature Tests**: Test generator features and output quality
  - **Transformer Feature Tests**: Test transformer features and transformations
  - **Project Analysis Tests**: Test project-wide analysis features
  - **Include Processing Feature Tests**: Test end-to-end include processing scenarios
- **Integration Tests** (`tests/integration/`): Test comprehensive integration scenarios
  - **Include Processing Integration Tests**: Test complex include processing workflows
- **Test Files**: Sample C/C++ files for testing

### Include Processing Test Coverage
The test suite includes comprehensive coverage for include header processing:

**Unit Tests** (`tests/unit/test_include_processing*.py`):
- Include parsing and relationship extraction
- Typedef relationship processing
- Circular dependency handling
- Complex nested include scenarios
- Edge cases and error conditions

**Feature Tests** (`tests/feature/test_include_processing*.py`):
- End-to-end include processing workflows
- Header-to-header relationship verification
- C-to-header relationship verification
- Typedef relationship verification in PlantUML output
- Include depth limitation testing
- Circular include handling verification

**Integration Tests** (`tests/integration/test_include_processing*.py`):
- Complex project structures with multiple include layers
- Comprehensive verification of C-to-H, H-to-H, and typedef relationships
- Real-world scenario testing with complex include hierarchies

**Key Verification Points**:
1. **C to H file relationships** are correctly processed and represented
2. **H to H file relationships** are properly processed and represented  
3. **Typedef relationships** are correctly parsed and shown in their PlantUML objects

## Configuration
The system uses JSON configuration files to control:
- File filtering patterns
- Element inclusion/exclusion rules
- Transformation and renaming rules
- Output directory structure
- Include depth configuration
- File selection for transformer actions
- Typedef relationship processing
- Union field display

## Output
- **PlantUML Files**: `.puml` files for each `.c` source file with proper UML notation
- **Model Files**: JSON models representing parsed code structure
- **Typedef Relationships**: Proper UML stereotypes («defines», «alias») for typedef relationships
- **Union Support**: Full parsing and display of union definitions with fields
- **Header Content**: All referenced include files shown as classes with their actual content
- **Header Relationships**: Include relationships between headers displayed with arrows
- **Logs**: Processing logs and error reports