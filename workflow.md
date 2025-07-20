# C to PlantUML Converter - Workflow Guide

## Overview
The C to PlantUML Converter follows a simple 3-step workflow for converting C/C++ source code to PlantUML diagrams.

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
- Model element filtering (structs, enums, functions, etc.)
- Model transformations (rename, add, remove elements)
- File selection for transformer actions (apply to all files or selected ones)

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
python3 run_all_tests.py

# Run with shell script
./test.sh

# Run specific test categories
python3 -m unittest tests.unit.test_parser
python3 -m unittest tests.unit.test_generator
```

### Test Runner
The `run_all_tests.py` script provides a simple and elegant test execution:
- Uses unittest discovery to automatically find all test files
- Runs both unit and feature tests
- Provides clear test summary with pass/fail status
- Works consistently across different environments

### Test Structure
- **Unit Tests**: Test individual components in isolation
  - **Parser Tests**: Test C/C++ parsing functionality
  - **User Configurable Filtering Tests**: Test user-configurable filtering via config.json
  - **Generator Tests**: Test PlantUML diagram generation
  - **Transformer Tests**: Test model transformation and filtering
  - **Config Tests**: Test configuration loading and validation
- **Feature Tests**: Test complete workflows and integrations
- **Test Files**: Sample C/C++ files for testing
- **Test Output**: Expected output files for verification

## Configuration
The system uses JSON configuration files to control:
- File filtering patterns
- Element inclusion/exclusion rules
- Transformation and renaming rules
- Output directory structure
- Include depth configuration
- File selection for transformer actions

## Output
- **PlantUML Files**: `.puml` files for each `.c` source file
- **Model Files**: JSON models representing parsed code structure
- **Logs**: Processing logs and error reports