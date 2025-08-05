# C2PUML Test Migration Recommendations

## Executive Summary

This document provides comprehensive analysis and specific recommendations for migrating the C2PUML test suite (50 test files) to the unified testing framework defined in `todo.md`. The analysis focuses on **test-application boundary separation** and **public API testing** to ensure the application remains flexible to internal changes.

**Key Findings:**
- **50 test files analyzed** across unit, feature, and integration categories
- **42 files (84%)** require data_*.json strategy due to multiple input needs
- **8 files (16%)** can use explicit files strategy
- **3 critical files** must be split due to excessive size (80, 41, 36 methods)
- **All files** currently use internal APIs and need CLI-only conversion

## Progress Tracking

### Migration Status Overview
- **Framework Foundation:** ⏳ Pending - TestDataFactory, TestExecutor, Validators
- **Critical Splits (3 files):** ⏳ Pending - Planning phase required
- **High Priority (24 files):** ⏳ Pending - All files have detailed recommendations
- **Medium Priority (18 files):** ⏳ Pending - All files have detailed recommendations
- **Low Priority (8 files):** ⏳ Pending - All files have detailed recommendations
- **Framework Cleanup:** ⏳ Pending - Remove legacy framework files after migration

### Progress Legend
- ⏳ **Pending** - Not yet started
- 🔄 **In Progress** - Currently being worked on
- ✅ **Completed** - Migrated and verified
- 🚫 **Blocked** - Waiting for dependencies

### Update Instructions
**Important:** This document should be updated with progress as migration work proceeds. Change progress markers from ⏳ to 🔄 when starting work, and to ✅ when completed. Update `todo.md` to reference any changes in this file.

### File Coverage Verification
**All 50 test files analyzed and covered:**

**Unit Tests (37 files):** ✅ All covered with detailed recommendations
**Feature Tests (11 files):** ✅ All covered with detailed recommendations  
**Integration Tests (2 files):** ✅ All covered with detailed recommendations

**Total Coverage:** 50/50 files (100%) - Every test file has specific migration strategy, data file recommendations, and progress tracking

## Critical Decision: Input Strategy Requirements

### The Core Rule

**If a test.py file requires multiple or different inputs to run various tests, then it MUST use the data_##.json input scheme.**

This is because when explicit files are used as input, all tests in that test.py file must use the same input files, since there is only a single `input/` folder per test. The data_##.json approach allows each test method to generate its own specific input requirements dynamically.

### Input Strategy Guidelines

**Use data_##.json for:**
- Small test cases (< 50 lines of C code total)
- Simple struct/enum definitions
- Basic function declarations
- Unit tests focusing on specific features
- Tests requiring multiple similar variants
- **Any test.py file that needs multiple or different inputs for different test methods**

**Use explicit files for:**
- Large test cases (> 50 lines of C code)
- Complex project structures
- Real-world code examples
- Integration tests with multiple dependencies
- Tests requiring detailed file organization
- **Only when ALL test methods in the test.py file can use the same input files**

## Detailed File-by-File Analysis

### High Priority Files (24 files) - Immediate Attention Required

#### Files Requiring Splits (3 files - CRITICAL)

**1. test_transformer.py (80 methods)** 🚨 CRITICAL SPLIT REQUIRED
- **Recommended Split:** 9 separate test files by transformation type
  - `test_transformation_rename.py` - Function/typedef/macro renaming - **Progress:** ⏳ Pending
  - `test_transformation_remove.py` - Element removal operations - **Progress:** ⏳ Pending
  - `test_transformation_add.py` - Element addition operations - **Progress:** ⏳ Pending
  - `test_transformation_file_selection.py` - File-specific transformations - **Progress:** ⏳ Pending
  - `test_transformation_config.py` - Configuration validation - **Progress:** ⏳ Pending
  - `test_transformation_validation.py` - Transformation validation - **Progress:** ⏳ Pending
  - `test_transformation_error_handling.py` - Error scenarios - **Progress:** ⏳ Pending
  - `test_transformation_edge_cases.py` - Edge cases and complex scenarios - **Progress:** ⏳ Pending
  - `test_transformation_integration.py` - End-to-end transformation workflows - **Progress:** ⏳ Pending
- **Input Strategy:** data_*.json for each transformation type
- **Data Files Needed:** data_rename_functions.json, data_remove_elements.json, data_add_elements.json, etc.
- **Overall Progress:** ⏳ Pending - Requires planning phase first

**2. test_tokenizer.py (41 methods)** 🚨 CRITICAL SPLIT REQUIRED
- **Recommended Split:** 4 separate test files by token category
  - `test_tokenizer_keywords.py` - C keywords and reserved words - **Progress:** ⏳ Pending
  - `test_tokenizer_identifiers.py` - Variable/function names and identifiers - **Progress:** ⏳ Pending
  - `test_tokenizer_operators.py` - Operators and punctuation - **Progress:** ⏳ Pending
  - `test_tokenizer_complex.py` - Complex tokenization scenarios - **Progress:** ⏳ Pending
- **Input Strategy:** data_*.json for each token category
- **Data Files Needed:** data_keywords.json, data_identifiers.json, data_operators.json, data_complex_tokens.json
- **Overall Progress:** ⏳ Pending - Requires planning phase first

**3. test_parser_comprehensive.py (36 methods)** 🚨 CRITICAL SPLIT REQUIRED
- **Recommended Split:** 7 separate test files by C language construct
  - `test_parser_struct.py` - Structure parsing (simple, nested, anonymous) - **Progress:** ⏳ Pending
  - `test_parser_enum.py` - Enumeration parsing - **Progress:** ⏳ Pending
  - `test_parser_function.py` - Function declarations and definitions - **Progress:** ⏳ Pending
  - `test_parser_global.py` - Global variables and declarations - **Progress:** ⏳ Pending
  - `test_parser_include.py` - Include processing - **Progress:** ⏳ Pending
  - `test_parser_macro.py` - Macro processing - **Progress:** ⏳ Pending
  - `test_parser_typedef.py` - Typedef processing - **Progress:** ⏳ Pending
- **Input Strategy:** data_*.json for each language construct
- **Data Files Needed:** data_simple_struct.json, data_nested_struct.json, data_anonymous_struct.json, etc.
- **Overall Progress:** ⏳ Pending - Requires planning phase first

#### High Priority Files Using Data JSON Strategy (21 files)

**test_generator.py (20 methods)**
- **Strategy:** Use data_generation_*.json for different output scenarios
- **Recommended Data Files:**
  - data_basic_generation.json - Simple PlantUML generation
  - data_complex_generation.json - Complex diagrams with relationships
  - data_formatting_test.json - Formatting compliance tests
  - data_relationship_generation.json - Include/typedef relationships
- **Progress:** ⏳ Pending

**test_preprocessor_bug.py (19 methods)**
- **Strategy:** Use data_preprocessor_*.json for different directive types
- **Recommended Data Files:**
  - data_ifdef.json - #ifdef/#ifndef testing
  - data_define.json - #define macro testing
  - data_include.json - #include directive testing
  - data_conditional.json - Complex conditional compilation
- **Progress:** ⏳ Pending

**test_invalid_source_paths.py (17 methods)**
- **Strategy:** Use data_path_error_*.json for different error scenarios
- **Recommended Data Files:**
  - data_missing_files.json - Missing source files
  - data_invalid_paths.json - Invalid path formats
  - data_permission_errors.json - Permission-related errors
- **Progress:** ⏳ Pending

**test_anonymous_processor_extended.py (14 methods)**
- **Strategy:** Use data_anonymous_*.json for complexity levels
- **Recommended Data Files:**
  - data_simple_anonymous.json - Basic anonymous structures
  - data_nested_anonymous.json - Nested anonymous structures
  - data_complex_anonymous.json - Complex hierarchies
- **Progress:** ⏳ Pending

**test_preprocessor_handling.py (14 methods)**
- **Strategy:** Use data_preprocessor_handling_*.json by directive type
- **Recommended Data Files:**
  - data_conditional_compilation.json - Conditional compilation testing
  - data_macro_expansion.json - Macro expansion scenarios
- **Progress:** ⏳ Pending

**Other High Priority Files:**

**test_include_processing_features.py (12 methods)** - Include processing features
- **Strategy:** Use data_include_*.json for different include scenarios
- **Data Files:** data_basic_includes.json, data_nested_includes.json, data_circular_includes.json
- **Progress:** ⏳ Pending

**test_parser.py (10 methods)** - Core parser functionality
- **Strategy:** Use data_parser_*.json for different parsing scenarios
- **Data Files:** data_basic_parsing.json, data_complex_parsing.json, data_error_handling.json
- **Progress:** ⏳ Pending

**test_global_parsing.py (9 methods)** - Global variable parsing
- **Strategy:** Use data_global_*.json for different global variable scenarios
- **Data Files:** data_simple_globals.json, data_complex_globals.json, data_initialized_globals.json
- **Progress:** ⏳ Pending

**test_component_features.py (9 methods)** - Component integration features
- **Strategy:** Use data_component_*.json for different integration tests
- **Data Files:** data_parser_integration.json, data_generator_integration.json, data_full_workflow.json
- **Progress:** ⏳ Pending

**test_transformer_features.py (9 methods)** - Transformer feature testing
- **Strategy:** Use data_transform_feature_*.json for feature testing
- **Data Files:** data_basic_transforms.json, data_advanced_transforms.json, data_edge_cases.json
- **Progress:** ⏳ Pending

**test_comprehensive.py (9 methods)** - End-to-end scenarios
- **Strategy:** Use data_comprehensive_*.json for complete workflows
- **Data Files:** data_full_project.json, data_complex_project.json, data_real_world.json
- **Progress:** ⏳ Pending

**test_multi_pass_anonymous_processing.py (8 methods)** - Multi-pass processing
- **Strategy:** Use data_multipass_*.json for multi-pass scenarios
- **Data Files:** data_simple_multipass.json, data_complex_multipass.json, data_nested_multipass.json
- **Progress:** ⏳ Pending

**test_crypto_filter_usecase.py (8 methods)** - Crypto filtering use cases
- **Strategy:** Use data_crypto_*.json for different filtering scenarios
- **Data Files:** data_crypto_basic.json, data_crypto_advanced.json, data_crypto_edge_cases.json
- **Progress:** ⏳ Pending

**test_parser_filtering.py (8 methods)** - Parser filtering logic
- **Strategy:** Use data_filter_*.json for different filtering patterns
- **Data Files:** data_include_filters.json, data_exclude_filters.json, data_mixed_filters.json
- **Progress:** ⏳ Pending

**test_multiple_source_folders.py (7 methods)** - Multiple source folder handling
- **Strategy:** Use data_multifolder_*.json for folder scenarios
- **Data Files:** data_two_folders.json, data_many_folders.json, data_nested_folders.json
- **Progress:** ⏳ Pending

**test_generator_new_formatting.py (7 methods)** - New formatting features
- **Strategy:** Use data_formatting_*.json for formatting tests
- **Data Files:** data_new_stereotypes.json, data_visibility_formatting.json, data_relationship_formatting.json
- **Progress:** ⏳ Pending

**test_generator_visibility_logic.py (6 methods)** - Visibility detection logic
- **Strategy:** Use data_visibility_*.json for visibility tests
- **Data Files:** data_public_private.json, data_header_detection.json, data_visibility_edge_cases.json
- **Progress:** ⏳ Pending

### Medium Priority Files (18 files)

#### Configuration and Setup Files

**test_config.py (13 methods)** - Configuration handling
- **Strategy:** Use data_config_*.json for different config scenarios
- **Data Files:** data_basic_config.json, data_advanced_config.json, data_invalid_config.json, data_file_specific_config.json
- **Progress:** ⏳ Pending

#### Generator Related Files

**test_include_filtering_bugs.py (12 methods)** - Include filtering edge cases
- **Strategy:** Use data_include_bug_*.json for different bug scenarios
- **Data Files:** data_filter_edge_cases.json, data_regex_patterns.json, data_performance_issues.json
- **Progress:** ⏳ Pending

**test_verifier.py (12 methods)** - Model verification logic
- **Strategy:** Use data_verification_*.json for different validation scenarios
- **Data Files:** data_valid_models.json, data_invalid_models.json, data_edge_case_models.json
- **Progress:** ⏳ Pending

**test_typedef_extraction.py (9 methods)** - Typedef extraction logic
- **Strategy:** Use data_typedef_*.json for different typedef scenarios
- **Data Files:** data_simple_typedefs.json, data_complex_typedefs.json, data_nested_typedefs.json
- **Progress:** ⏳ Pending

**test_utils.py (7 methods)** - Utility function testing
- **Strategy:** Use data_utils_*.json for utility testing
- **Data Files:** data_file_utils.json, data_string_utils.json, data_path_utils.json
- **Progress:** ⏳ Pending

#### Parser Specific Files

**test_anonymous_structure_handling.py (5 methods)** - Anonymous structure handling
- **Strategy:** Use data_anonymous_handling_*.json for different handling scenarios
- **Data Files:** data_simple_anonymous.json, data_nested_anonymous.json, data_complex_anonymous.json
- **Progress:** ⏳ Pending

**test_transformation_system.py (5 methods)** - Transformation system
- **Strategy:** Use data_transform_system_*.json for system testing
- **Data Files:** data_system_config.json, data_system_validation.json, data_system_integration.json
- **Progress:** ⏳ Pending

**test_crypto_filter_pattern.py (5 methods)** - Crypto filtering patterns
- **Strategy:** Use data_crypto_pattern_*.json for pattern testing
- **Data Files:** data_basic_patterns.json, data_complex_patterns.json, data_edge_patterns.json
- **Progress:** ⏳ Pending

**test_function_parameters.py (4 methods)** - Function parameter parsing
- **Strategy:** Use data_function_param_*.json for parameter scenarios
- **Data Files:** data_simple_params.json, data_complex_params.json, data_variadic_params.json
- **Progress:** ⏳ Pending

**test_file_specific_configuration.py (4 methods)** - File-specific config handling
- **Strategy:** Use data_file_config_*.json for file-specific scenarios
- **Data Files:** data_single_file_config.json, data_multiple_file_config.json, data_override_config.json
- **Progress:** ⏳ Pending

**test_absolute_path_bug_detection.py (4 methods)** - Path handling validation
- **Strategy:** Use data_path_bug_*.json for path testing
- **Data Files:** data_absolute_paths.json, data_relative_paths.json, data_invalid_paths.json
- **Progress:** ⏳ Pending

#### Generator Testing Files

**test_generator_include_tree_bug.py (4 methods)** - Include tree validation
- **Strategy:** Use data_include_tree_*.json for tree testing
- **Data Files:** data_simple_tree.json, data_complex_tree.json, data_circular_tree.json
- **Progress:** ⏳ Pending

**test_generator_naming_conventions.py (4 methods)** - Naming convention compliance
- **Strategy:** Use data_naming_*.json for naming tests
- **Data Files:** data_class_naming.json, data_relationship_naming.json, data_stereotype_naming.json
- **Progress:** ⏳ Pending

**test_integration.py (4 methods)** - Integration testing
- **Strategy:** Use data_integration_*.json for integration scenarios
- **Data Files:** data_basic_integration.json, data_complex_integration.json, data_error_integration.json
- **Progress:** ⏳ Pending

**test_generator_grouping.py (3 methods)** - Element grouping in output
- **Strategy:** Use data_grouping_*.json for grouping tests
- **Data Files:** data_public_private_grouping.json, data_element_grouping.json, data_visibility_grouping.json
- **Progress:** ⏳ Pending

**test_include_processing.py (3 methods)** - Include processing logic
- **Strategy:** Use data_include_proc_*.json for processing tests
- **Data Files:** data_basic_includes.json, data_nested_includes.json, data_depth_includes.json
- **Progress:** ⏳ Pending

**test_parser_nested_structures.py (3 methods)** - Nested structure parsing
- **Strategy:** Use data_nested_*.json for nested scenarios
- **Data Files:** data_simple_nested.json, data_deep_nested.json, data_complex_nested.json
- **Progress:** ⏳ Pending

**test_parser_struct_order.py (3 methods)** - Struct field order preservation
- **Strategy:** Use data_struct_order_*.json for ordering tests
- **Data Files:** data_simple_order.json, data_complex_order.json, data_mixed_order.json
- **Progress:** ⏳ Pending

### Low Priority Files (8 files)

#### Explicit Files Strategy (Suitable for single input approach)

**test_cli_modes.py (6 methods)** - CLI mode switching
- **Strategy:** Use data_mode_*.json - different CLI modes need different configurations
- **Data Files:** data_parse_only.json, data_transform_only.json, data_generate_only.json, data_full_pipeline.json
- **Progress:** ⏳ Pending

**test_cli_feature.py (5 methods)** - CLI interface testing
- **Strategy:** Use explicit files - focused on CLI interface validation
- **Input Files:** feature_test.c, feature_config.json, test_project/
- **Progress:** ⏳ Pending

**test_generator_duplicate_includes.py (2 methods)** - Include duplication handling
- **Strategy:** Use explicit files - simple duplication scenario
- **Input Files:** duplicate_test.c, duplicate_includes.h, config.json
- **Progress:** ⏳ Pending

**test_generator_exact_format.py (2 methods)** - PlantUML formatting validation
- **Strategy:** Can use data_format_*.json for different format tests
- **Data Files:** data_basic_format.json, data_advanced_format.json
- **Progress:** ⏳ Pending

**test_new_formatting_comprehensive.py (2 methods)** - New formatting integration
- **Strategy:** Can use data_new_format_*.json for formatting tests
- **Data Files:** data_stereotype_format.json, data_relationship_format.json
- **Progress:** ⏳ Pending

**test_parser_function_params.py (2 methods)** - Function parameter parsing
- **Strategy:** Use data_func_params_*.json for parameter scenarios
- **Data Files:** data_simple_params.json, data_complex_params.json
- **Progress:** ⏳ Pending

**test_parser_macro_duplicates.py (2 methods)** - Macro duplication handling
- **Strategy:** Use data_macro_dup_*.json for duplication scenarios
- **Data Files:** data_simple_duplicates.json, data_complex_duplicates.json
- **Progress:** ⏳ Pending

#### Debug Files (Minimal priority)

**test_debug_actual_parsing.py (1 method)** - Debug functionality
- **Strategy:** Use explicit files - simple debug test
- **Input Files:** debug_simple.c, debug_config.json
- **Progress:** ⏳ Pending

**test_debug_field_parsing.py (1 method)** - Debug functionality
- **Strategy:** Use explicit files - field parsing debug
- **Input Files:** debug_fields.c, debug_config.json
- **Progress:** ⏳ Pending

**test_debug_field_processing.py (1 method)** - Debug functionality
- **Strategy:** Use explicit files - field processing debug
- **Input Files:** debug_processing.c, debug_config.json
- **Progress:** ⏳ Pending

**test_debug_tokens.py (1 method)** - Debug functionality
- **Strategy:** Use explicit files - token debug
- **Input Files:** debug_tokens.c, debug_config.json
- **Progress:** ⏳ Pending

**test_debug_field_parsing_detailed.py (0 methods)** - Debug functionality
- **Strategy:** Use explicit files - detailed debug (may need investigation)
- **Input Files:** debug_detailed.c, debug_config.json
- **Progress:** ⏳ Pending - Investigate if this file has actual tests

## Data JSON File Examples

### Simple Struct Parsing Example
**File:** `data_simple_struct.json`
```json
{
  "test_metadata": {
    "description": "Basic struct parsing test",
    "test_type": "unit",
    "focus": "struct_parsing",
    "expected_duration": "fast"
  },
  "c2puml_config": {
    "project_name": "test_struct_parsing",
    "source_folders": ["."],
    "output_dir": "./output",
    "recursive_search": true,
    "file_extensions": [".c", ".h"]
  },
  "source_files": {
    "test.c": "#include <stdio.h>\n\nstruct Point {\n    int x;\n    int y;\n};\n\nint main() {\n    struct Point p = {10, 20};\n    return 0;\n}"
  },
  "expected_results": {
    "model_elements": {
      "structs": ["Point"],
      "functions": ["main"],
      "includes": ["stdio.h"]
    },
    "plantuml_elements": {
      "classes": ["Point"],
      "relationships": []
    }
  }
}
```

### Preprocessor Conditional Example
**File:** `data_ifdef_test.json`
```json
{
  "test_metadata": {
    "description": "Conditional compilation test",
    "test_type": "unit",
    "focus": "preprocessor_conditionals",
    "expected_duration": "fast"
  },
  "c2puml_config": {
    "project_name": "test_preprocessor",
    "source_folders": ["."],
    "output_dir": "./output",
    "preprocessor_defines": ["DEBUG"],
    "include_preprocessor_conditionals": true
  },
  "source_files": {
    "conditional.c": "#ifdef DEBUG\n#define LOG(x) printf(x)\n#else\n#define LOG(x)\n#endif\n\nint main() {\n    LOG(\"Debug mode\");\n    return 0;\n}"
  },
  "expected_results": {
    "model_elements": {
      "functions": ["main"],
      "macros": ["LOG"],
      "preprocessor_branches": ["DEBUG"]
    }
  }
}
```

### Complex Transformation Example
**File:** `data_rename_functions.json`
```json
{
  "test_metadata": {
    "description": "Function renaming transformation test",
    "test_type": "integration",
    "focus": "transformation_pipeline",
    "expected_duration": "medium"
  },
  "c2puml_config": {
    "project_name": "test_transformation",
    "source_folders": ["."],
    "output_dir": "./output",
    "transformations": {
      "rename": {
        "functions": {
          "^deprecated_(.*)": "legacy_\\1",
          "^old_(.*)": "legacy_\\1"
        }
      }
    }
  },
  "input_model": {
    "project_name": "test_transformation",
    "files": {
      "main.c": {
        "functions": [
          {"name": "deprecated_init", "return_type": "void", "parameters": []},
          {"name": "old_cleanup", "return_type": "void", "parameters": []},
          {"name": "main", "return_type": "int", "parameters": []}
        ]
      }
    }
  },
  "expected_results": {
    "transformed_model": {
      "functions": [
        {"name": "legacy_init", "return_type": "void"},
        {"name": "legacy_cleanup", "return_type": "void"},
        {"name": "main", "return_type": "int"}
      ]
    },
    "plantuml_elements": {
      "classes": [],
      "functions": ["legacy_init", "legacy_cleanup", "main"]
    }
  }
}
```

## Recommended Folder Structures

### Simple Test (Single Input) - Explicit Files Strategy
```
test_generator_duplicate_includes/
├── test_generator_duplicate_includes.py
├── input/
│   ├── config.json     # Optional: can be embedded in data.json instead
│   ├── main.c
│   ├── utils.h
│   └── types.h
└── assertions.json
```

### Multiple Scenarios (Data JSON Strategy)
```
test_parser_filtering/
├── test_parser_filtering.py
├── input/
│   ├── config.json                 # Optional: default config (can be overridden per data file)
│   ├── data_include_patterns.json  # Contains own config section
│   ├── data_exclude_patterns.json  # Contains own config section
│   └── data_mixed_filters.json     # Contains own config section
└── assertions.json
```

### Split Large Test Example
```
test_struct_parsing/
├── test_struct_parsing.py
├── input/
│   ├── config.json                 # Optional: default config
│   ├── data_simple_struct.json     # Contains config + source content
│   ├── data_nested_struct.json     # Contains config + source content
│   └── data_anonymous_struct.json  # Contains config + source content
└── assertions.json

test_enum_parsing/
├── test_enum_parsing.py
├── input/
│   ├── data_simple_enum.json       # Contains config + source content
│   └── data_typedef_enum.json      # Contains config + source content
└── assertions.json

... (additional split test folders)
```

## Migration Implementation Phases

### Phase 1: Framework Foundation (Weeks 1-2)
**Priority: CRITICAL**

1. **Implement Extended TestDataFactory**
   - `load_test_data_json(test_name, data_file)` - Load specific data files
   - `generate_source_files_from_data(test_name, data_file)` - Generate source files from data.json
   - `generate_model_from_data(test_name, data_file)` - Generate model.json from data.json
   - `has_data_json(test_name, data_file)` - Check if data files exist
   - `list_data_json_files(test_name)` - List all data files for a test

2. **Implement TestExecutor for CLI-Only Interface**
   - `run_full_pipeline(input_path, config_path, output_dir)` - Complete workflow
   - `run_parse_only(input_path, config_path, output_dir)` - Parse step only
   - `run_transform_only(config_path, output_dir)` - Transform step only
   - `run_generate_only(config_path, output_dir)` - Generate step only

3. **Create Validation Framework**
   - `ModelValidator` - Model structure and content validation
   - `PlantUMLValidator` - PlantUML file validation
   - `OutputValidator` - General output file validation

4. **Establish Baseline**
   - Run `./run_all.sh > baseline_results.log`
   - Verify foundation works with existing tests

### Phase 2: Quick Wins (Weeks 3-4)
**Priority: HIGH - 21 files with manageable effort**

Start with smallest files and progress to larger ones:

1. **test_parser_function_params.py (2 methods)**
   - Convert to data_function_params.json approach
   - Test CLI-only interface implementation

2. **test_parser_macro_duplicates.py (2 methods)**
   - Use data_macro_duplicates.json

3. **test_parser_nested_structures.py (3 methods)**
   - Use data_nested_*.json files

4. **test_parser_struct_order.py (3 methods)**
   - Use data_struct_order.json

5. Continue with progressively larger files...

**Verification Process for Each File:**
- Develop new structure → `pytest test_file.py` → `./run_all.sh`
- Ensure no regressions in existing functionality

### Phase 3: Major Refactoring (Weeks 5-8)
**Priority: CRITICAL - 3 large files requiring splits**

**Week 5-6: test_transformer.py (80 methods → 9 files)**
- Plan split strategy by transformation type
- Create 9 separate test folders with data_*.json files
- Implement and test each split file individually

**Week 7: test_tokenizer.py (41 methods → 4 files)**
- Split by token category
- Use data_*.json for each token type

**Week 8: test_parser_comprehensive.py (36 methods → 7 files)**
- Split by C language construct
- Create comprehensive data_*.json for each construct type

### Phase 4: Medium Priority (Weeks 9-10)
**18 files - Most using data_json strategy**

Focus on configuration, generator, and parser-specific files.

### Phase 5: Low Priority (Weeks 11-12)
**8 files - Mostly explicit files strategy**

Complete remaining files, including debug files and simple CLI tests.

## Extended TestDataFactory Requirements

The TestDataFactory must support the following functionality for the data_*.json approach:

### Core Methods

```
load_test_input(test_name: str) -> str
    Returns path to test_<n>/input/ directory for CLI execution

load_test_config(test_name: str, data_file: str = None) -> str
    Returns path to config.json (explicit) or extracts config from data_file for CLI execution

load_test_data_json(test_name: str, data_file: str = "data.json") -> dict
    Loads data.json from test_<n>/input/<data_file> and returns parsed content

generate_source_files_from_data(test_name: str, data_file: str = "data.json") -> str
    Generates source files from 'source_files' section and returns input path for CLI

generate_model_from_data(test_name: str, data_file: str = "data.json") -> str
    Generates model.json from 'input_model' section and returns input path for CLI

has_data_json(test_name: str, data_file: str = "data.json") -> bool
    Returns True if test_<n>/input/<data_file> exists

list_data_json_files(test_name: str) -> list
    Returns list of all data*.json files in test_<n>/input/ directory

extract_config_from_data(test_name: str, data_file: str) -> str
    Extracts 'c2puml_config' section from data_file and creates temp config.json for CLI execution

validate_expected_results(test_name: str, data_file: str, actual_results: dict) -> bool
    Validates actual results against 'expected_results' section in data_file
```

### Data.json Structure Definition

**Standardized Section Organization:**

```json
{
  "test_metadata": {
    "description": "Human-readable test description",
    "test_type": "unit|integration|feature",
    "focus": "struct_parsing|transformation|generation",
    "expected_duration": "fast|medium|slow"
  },
  "c2puml_config": {
    "project_name": "test_project_name",
    "source_folders": ["."],
    "output_dir": "./output",
    "...": "complete c2puml configuration (equivalent to config.json)"
  },
  "source_files": {
    "filename.c": "complete C source code content",
    "filename.h": "complete header file content"
  },
  "input_model": {
    "project_name": "model_name",
    "files": {
      "filename.c": {
        "functions": [...],
        "structs": [...],
        "...": "pre-parsed model data"
      }
    }
  },
  "expected_results": {
    "model_elements": {
      "structs": ["StructName"],
      "functions": ["function_name"],
      "includes": ["stdio.h"]
    },
    "plantuml_elements": {
      "classes": ["ClassName"],
      "relationships": ["dependency", "inheritance"]
    },
    "transformed_model": {
      "...": "expected transformation results"
    }
  }
}
```

**Section Usage Rules:**
- **test_metadata**: Always required - provides test context and classification
- **c2puml_config**: Required if no explicit config.json - complete c2puml configuration
- **source_files**: Use for tests that generate C source files (parsing tests)
- **input_model**: Use for tests that skip parsing (transformation/generation tests)
- **expected_results**: Always recommended - enables automatic validation

**Validation Philosophy:**
Simple model elements and PlantUML expectations in `expected_results` are sufficient for validating any modification, transformation, or generation. No complex assertion structures are needed - basic lists of expected structs, functions, and includes are enough.

### Configuration Handling

**Flexible Configuration Options:**
- **Explicit config.json**: Use standalone config.json for single-use-case tests
- **Embedded config**: Include "c2puml_config" section within data_*.json files
- **Mixed approach**: Default config.json with per-test-case overrides in data files
- **Configuration precedence**: data_file.c2puml_config > explicit config.json > default values

### Data Generation Types

**Source Files Generation (`"generate_type": "source_files"`):**
- Generate .c/.h files from content specifications
- Support includes, structs, functions, macros, etc.
- Include complete configuration within data file

**Model JSON Generation (`"generate_type": "model_json"`):**
- Generate pre-parsed model.json for transformation testing
- Skip parsing step, go directly to transformation
- Useful for testing transformation logic in isolation

**Hybrid Generation:**
- Support both approaches in same test file
- Different test methods can use different generation types

## Success Criteria

### Technical Criteria
- **Zero internal API usage**: All tests use only CLI interface (main.py)
- **100% test pass rate**: All migrated tests pass consistently via `./run_all.sh`
- **Maintainable boundaries**: Clear separation between test and application code
- **Consistent patterns**: All tests follow unified structure and naming

### Quality Criteria
- **Test readability**: Tests are easy to understand and modify
- **Failure diagnostics**: Test failures provide clear guidance
- **Coverage preservation**: No reduction in test coverage during migration
- **Performance**: Test suite execution time via `./run_all.sh` remains reasonable

### Migration Criteria
- **Flexible to changes**: Tests continue passing when internal implementation changes
- **Comprehensive validation**: Tests validate all aspects of public API behavior
- **Realistic scenarios**: Tests cover real-world usage patterns
- **Error handling**: Tests validate error conditions and edge cases

## Risk Mitigation

### Migration Risks
- **Breaking existing tests**: Gradual migration with parallel test execution
- **Coverage gaps**: Careful mapping of existing test coverage to new structure
- **Performance degradation**: Monitoring test execution times during migration

### Technical Risks
- **Framework complexity**: Keep framework simple and well-documented
- **Over-abstraction**: Balance reusability with test clarity
- **Data file management**: Ensure data_*.json files remain maintainable

### Process Risks
- **Scope creep**: Focus on migration goals, avoid feature additions
- **Coordination**: Clear phases prevent conflicts during development
- **Quality control**: Each phase includes verification steps

## Conclusion

This migration plan provides a comprehensive roadmap for transforming all 50 test files from internal API usage to a unified, maintainable, CLI-only testing framework. The analysis identifies specific strategies for each file, provides concrete examples of data structures and folder layouts, and establishes clear implementation phases.

**Key Success Factors:**
1. **Follow the input strategy rule**: Multiple inputs = data_*.json approach
2. **Split large files early**: Don't attempt to migrate 80-method files as-is
3. **Implement framework first**: TestDataFactory and validation tools are critical
4. **Verify continuously**: Run full test suite after each migration
5. **Track progress**: Update todo.md with migration status

The detailed recommendations ensure that the migration will result in a robust, maintainable test suite that validates public API behavior while remaining flexible to internal implementation changes.

## Existing Test Framework Cleanup

### Current Framework Files to Be Replaced/Removed

The following existing test framework files are currently used but will be replaced by the new unified framework:

**🗑️ Files to be REMOVED after migration completion:**

1. **`/tests/utils.py` (374 lines)** - Existing test utilities
   - Contains: `ProjectBuilder`, `MockObjectFactory`, `AssertionHelpers`, `TestDataProviders`
   - **Why remove:** Uses internal API imports (`from c2puml.generator import Generator`, etc.)
   - **Replaced by:** New `TestDataFactory` with CLI-only approach
   - **Progress:** ⏳ Pending - Remove after all tests migrated

2. **`/tests/feature/base.py` (189 lines)** - Feature test base class
   - Contains: `BaseFeatureTest` class with internal API usage
   - **Why remove:** Inherits from `unittest.TestCase` and uses internal pipeline calls
   - **Replaced by:** New `UnifiedTestCase` with CLI-only execution
   - **Progress:** ⏳ Pending - Remove after all tests migrated

3. **`/tests/conftest.py` (129 lines)** - pytest configuration
   - Contains: Basic fixtures like `temp_dir`, `config_factory`, `file_factory`
   - **Status:** **EVALUATE** - May be partially reusable for basic fixtures
   - **Decision needed:** Keep basic fixtures, remove any internal API dependencies
   - **Progress:** ⏳ Pending - Clean up after framework implementation

### Framework Analysis

**Existing Internal API Usage (to be eliminated):**
```python
# From tests/utils.py - PROBLEMATIC
from c2puml.generator import Generator
from c2puml.parser import Parser  
from c2puml.transformer import Transformer

# From tests/feature/base.py - PROBLEMATIC  
parser = Parser()
transformer = Transformer()
generator = Generator()
```

**Existing Good Patterns (to be preserved):**
```python
# From conftest.py - REUSABLE
@pytest.fixture(scope="function")
def temp_dir():
    """Create a temporary directory that gets cleaned up after each test."""
    
# From utils.py - CONCEPT REUSABLE
def create_temp_project(project_data: Dict[str, str], base_dir: Optional[str] = None) -> Path:
```

### Migration Cleanup Phase

**After unified framework implementation is complete:**

1. **Phase 1: Verify No Dependencies**
   - Ensure all 50 test files use new `TestDataFactory` and `TestExecutor`
   - Confirm no imports from old framework files
   - **Progress:** ⏳ Pending

2. **Phase 2: Remove Old Framework Files**
   - Delete `/tests/utils.py` ✅ Safe to remove
   - Delete `/tests/feature/base.py` ✅ Safe to remove  
   - **Progress:** ⏳ Pending

3. **Phase 3: Clean conftest.py**
   - Keep basic fixtures (`temp_dir`, file creation helpers)
   - Remove any internal API dependencies
   - Ensure compatibility with new unified framework
   - **Progress:** ⏳ Pending

### Size Reduction Benefits

**Lines of Code Reduction:**
- Current framework: ~692 lines (utils.py + base.py + conftest.py)
- New framework: Estimated ~400-500 lines (focused, CLI-only)
- **Net reduction:** ~200-300 lines of cleaner, maintainable code

**Key Improvement:** Elimination of internal API dependencies makes the entire test suite resilient to internal refactoring.

### Important Note for Migration Planning

The existing framework files were **NOT considered** in the initial analysis since they use internal APIs and conflict with the CLI-only approach. These files must be treated as **legacy code** that will be completely replaced, not adapted. This ensures a clean break from internal API dependencies and establishes the proper test-application boundary separation.

## Key Configuration Updates

### Important Changes Made

**Data.json Structure Standardization:**
- **Clear section organization**: `test_metadata`, `c2puml_config`, `source_files`, `input_model`, `expected_results`
- **Semantic naming**: Replaced generic "config", "files", "model" with descriptive section names
- **Validation support**: `expected_results` section enables automatic test validation
- **Test classification**: `test_metadata` provides context and categorization

**Configuration Flexibility Enhancement:**
- **config.json is now OPTIONAL** - can be embedded as `c2puml_config` in data_*.json files
- **Three configuration approaches supported:**
  1. Explicit config.json for single-use-case tests
  2. Embedded `c2puml_config` sections in data_*.json files  
  3. Mixed approach with defaults + per-case overrides

**Updated Input Structure:**
- **Option 1:** Single use case with explicit files (main.c, utils.h, optional config.json)
- **Option 2:** Multiple use cases with data_case#.json files (each containing structured sections)

**Enhanced TestDataFactory Methods:**
- `load_test_config(test_name, data_file=None)` - handles both explicit and embedded config
- `extract_config_from_data(test_name, data_file)` - extracts `c2puml_config` from data files
- `validate_expected_results(test_name, data_file, actual_results)` - validates against expected results

**Strategy Refinements:**
- **Improved data.json examples** with clear section organization and better grouping
- **Test method examples** updated to use structured sections properly
- **Validation integration** using `expected_results` for automatic test verification

This enhancement provides maximum flexibility and clarity while maintaining the CLI-only approach and proper test-application boundary separation.