# C to PlantUML Converter - Workflow Guide

## Overview
The C to PlantUML Converter follows a simple 3-step workflow for converting C/C++ source code to PlantUML diagrams.

## Processing Workflow

### Step 1: Parse
Parse C/C++ source files and generate a JSON model (`model.json`).

```bash
python3 main.py parse ./src
```

### Step 2: Transform (Optional)
Transform the model based on configuration rules.

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

## Testing Workflow

### Running Tests
```bash
# Run all tests
python3 run_all_tests.py

# Run with shell script
./test.sh

# Run specific test categories
python3 -m unittest tests.unit.test_parser
python3 -m unittest tests.unit.test_generator
```

### Test Structure
- **Unit Tests**: Test individual components in isolation
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

## Output
- **PlantUML Files**: `.puml` files for each `.c` source file
- **Model Files**: JSON models representing parsed code structure
- **Logs**: Processing logs and error reports