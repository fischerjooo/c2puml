# Examples Summary

This directory contains example use cases for the C to PlantUML converter.

## Available Examples

### ❌ basic_project
- **Description**: Basic Project Example
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

