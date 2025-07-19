# Examples Summary

This directory contains example use cases for the C to PlantUML converter.

## Available Examples

### ✅ large_codebase
- **Description**: No description available
- **Input**: 5 files
- **Output**: 0 files
- **Configuration**: config.json

### ✅ typedef_example
- **Description**: No description available
- **Input**: 3 files
- **Output**: 0 files
- **Configuration**: config.json

### ✅ basic_project
- **Description**: No description available
- **Input**: 3 files
- **Output**: 0 files
- **Configuration**: config.json

## Running Examples

To run all examples:
```bash
python run_examples.py
```

To run with verbose output:
```bash
python run_examples.py --verbose
```

To run a specific example:
```bash
python run_examples.py --example <example_name>
```

## Example Structure

Each example directory contains:
- `input/` - Source C/C++ files
- `config.json` - Configuration file
- `expected_output/` - Expected PlantUML output (for reference)
- `generated_output/` - Generated output (created by running the example)
- `README.md` - Example-specific documentation

