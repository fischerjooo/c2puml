# Examples Summary

This directory contains example use cases for the C to PlantUML converter.

## Available Examples

### ✅ use_case_complex_example
- **Description**: Complex C code with nested structs, unions, enums, function pointers, and multi-line macros
- **Input**: 2 files (complex_example.c, complex_example.h)
- **Output**: 1 file (complex_example.puml)
- **Configuration**: config.json

### ✅ use_case_sample
- **Description**: Basic sample project with structs, enums, typedefs, and utility macros
- **Input**: 2 files (sample.c, sample.h)
- **Output**: 1 file (sample.puml)
- **Configuration**: config.json

### ✅ use_case_large_codebase
- **Description**: Multi-module large codebase with core and utils modules
- **Input**: 5 files (main.c, core.h/c, utils.h/c)
- **Output**: 3 files (main.puml, core.puml, utils.puml)
- **Configuration**: config.json

### ✅ use_case_typedef_complex
- **Description**: Complex typedef chains and relationships with anonymous structs/enums/unions
- **Input**: 2 files (main.c, types.h)
- **Output**: 1 file (main.puml)
- **Configuration**: config.json

### ✅ use_case_error_handling
- **Description**: Error handling scenarios with invalid files, missing includes, and encoding issues
- **Input**: 3 files (valid_file.c, invalid_file.c, missing_include.c)
- **Output**: 3 files (valid_file.puml, invalid_file.puml, missing_include.puml)
- **Configuration**: config.json

### ✅ use_case_typedef_test
- **Description**: Comprehensive typedef testing with various type aliases, function pointers, and complex types
- **Input**: 3 files (typedef_test.c, typedef_test.h, sample.h)
- **Output**: 1 file (typedef_test.puml)
- **Configuration**: config.json

### ✅ large_codebase
- **Description**: Large codebase example with multiple modules and complex relationships
- **Input**: 5 files (main.c, core.h/c, utils.h/c)
- **Output**: 3 files (main.puml, core.puml, utils.puml)
- **Configuration**: config.json

### ✅ typedef_example
- **Description**: Typedef examples with struct, enum, and union type aliases
- **Input**: 3 files (main.c, types.h, utils.h)
- **Output**: 1 file (main.puml)
- **Configuration**: config.json

### ✅ basic_project
- **Description**: Basic C project structure with simple structs, functions, and includes
- **Input**: 3 files (main.c, utils.h, types.h)
- **Output**: 1 file (main.puml)
- **Configuration**: config.json

### ✅ use_case_configuration
- **Description**: Configuration-based filtering example with public/internal element separation
- **Input**: 3 files (main.c, public.h, internal.h)
- **Output**: 1 file (main.puml)
- **Configuration**: config.json

### ✅ use_case_basic_project
- **Description**: Basic project use case with structs, enums, unions, and typedefs
- **Input**: 3 files (main.c, utils.h, types.h)
- **Output**: 1 file (main.puml)
- **Configuration**: config.json

### ✅ use_case_integration_workflow
- **Description**: Complete integration workflow example with main application, config, and utils
- **Input**: 3 files (main.c, config.h, utils.c)
- **Output**: 1 file (main.puml)
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

