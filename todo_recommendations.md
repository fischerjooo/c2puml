# C2PUML Test Migration Recommendations

## Executive Summary

This document provides comprehensive analysis and specific recommendations for migrating the C2PUML test suite (50 test files) to the unified testing framework defined in `todo.md`. The analysis focuses on **test-application boundary separation** and **public API testing**.

**Key Findings:**
- **50 test files analyzed** across unit, feature, and integration categories
- **42 files (84%)** require input-##.json strategy due to multiple input needs
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
**Important:** Update progress markers from ⏳ to 🔄 when starting work, and to ✅ when completed. Update `todo.md` to reference any changes in this file.

## Input Strategy Guidelines

### The Core Rule

**Feature tests ALWAYS use explicit files** as they test complete workflows and need comprehensive project structures.

**Unit tests with multiple test methods requiring different inputs MUST use input-##.json approach.**

### Input Strategy Guidelines

**Use input-##.json for:**
- Small unit test cases (< 50 lines of C code total)
- Multiple test scenarios in one test file
- Tests requiring different inputs per method

**Use explicit files for:**
- **Feature tests (ALWAYS)**
- Large test cases (> 50 lines of C code)
- Complex project structures
- Integration tests with multiple dependencies

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
- **Input Strategy:** input-##.json for each transformation type
- **Input Files Needed:** input-01.json (rename functions), input-02.json (remove elements), input-03.json (add elements), etc.
- **Overall Progress:** ⏳ Pending - Requires planning phase first

**2. test_tokenizer.py (41 methods)** 🚨 CRITICAL SPLIT REQUIRED
- **Recommended Split:** 4 separate test files by token category
  - `test_tokenizer_keywords.py` - C keywords and reserved words - **Progress:** ⏳ Pending
  - `test_tokenizer_identifiers.py` - Variable/function names and identifiers - **Progress:** ⏳ Pending
  - `test_tokenizer_operators.py` - Operators and punctuation - **Progress:** ⏳ Pending
  - `test_tokenizer_complex.py` - Complex tokenization scenarios - **Progress:** ⏳ Pending
- **Input Strategy:** input-##.json for each token category
- **Input Files Needed:** input-01.json (keywords), input-02.json (identifiers), input-03.json (operators), input-04.json (complex tokens)
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
- **Input Strategy:** input-##.json for each language construct
- **Input Files Needed:** input-01.json (simple struct), input-02.json (nested struct), input-03.json (anonymous struct), etc.
- **Overall Progress:** ⏳ Pending - Requires planning phase first

#### High Priority Unit Tests Using Input JSON Strategy (21 files)

**test_generator.py (20 methods)**
- **Strategy:** Use input-##.json for different output scenarios
- **Recommended Input Files:**
  - input-01.json - Simple PlantUML generation
  - input-02.json - Complex diagrams with relationships
  - input-03.json - Formatting compliance tests
  - input-04.json - Include/typedef relationships
- **Progress:** ⏳ Pending

**test_preprocessor_bug.py (19 methods)**
- **Strategy:** Use input-##.json for different directive types
- **Recommended Input Files:**
  - input-01.json - #ifdef/#ifndef testing
  - input-02.json - #define macro testing
  - input-03.json - #include directive testing
  - input-04.json - Complex conditional compilation
- **Progress:** ⏳ Pending

**test_invalid_source_paths.py (17 methods)**
- **Strategy:** Use input-##.json for different error scenarios
- **Recommended Input Files:**
  - input-01.json - Missing source files
  - input-02.json - Invalid path formats
  - input-03.json - Permission-related errors
- **Progress:** ⏳ Pending

**test_anonymous_processor_extended.py (14 methods)**
- **Strategy:** Use input-##.json for complexity levels
- **Recommended Input Files:**
  - input-01.json - Basic anonymous structures
  - input-02.json - Nested anonymous structures
  - input-03.json - Complex hierarchies
- **Progress:** ⏳ Pending

**test_preprocessor_handling.py (14 methods)**
- **Strategy:** Use input-##.json by directive type
- **Recommended Input Files:**
  - input-01.json - Conditional compilation testing
  - input-02.json - Macro expansion scenarios
- **Progress:** ⏳ Pending

**Other High Priority Unit Tests:**

**test_include_processing_features.py (12 methods)** - **FEATURE TEST: Use explicit files**
- **Strategy:** Use explicit files with config.json + source files
- **Input Files:** main.c, utils.h, includes/, config.json
- **Progress:** ⏳ Pending

**test_parser.py (10 methods)** - Core parser functionality
- **Strategy:** Use input-##.json for different parsing scenarios
- **Input Files:** input-01.json (basic parsing), input-02.json (complex parsing), input-03.json (error handling)
- **Progress:** ⏳ Pending

**test_global_parsing.py (9 methods)** - Global variable parsing
- **Strategy:** Use input-##.json for different global variable scenarios
- **Input Files:** input-01.json (simple globals), input-02.json (complex globals), input-03.json (initialized globals)
- **Progress:** ⏳ Pending

**test_component_features.py (9 methods)** - **FEATURE TEST: Use explicit files**
- **Strategy:** Use explicit files for component integration tests
- **Input Files:** main.c, headers/, config.json, project structure
- **Progress:** ⏳ Pending

**test_transformer_features.py (9 methods)** - **FEATURE TEST: Use explicit files**
- **Strategy:** Use explicit files for transformer feature testing
- **Input Files:** source files with transformation config.json
- **Progress:** ⏳ Pending

**test_comprehensive.py (9 methods)** - **INTEGRATION TEST: Use explicit files**
- **Strategy:** Use explicit files for complete workflows
- **Input Files:** realistic_project/, config.json
- **Progress:** ⏳ Pending

**test_multi_pass_anonymous_processing.py (8 methods)** - Multi-pass processing
- **Strategy:** Use input-##.json for multi-pass scenarios
- **Input Files:** input-01.json (simple), input-02.json (complex), input-03.json (nested)
- **Progress:** ⏳ Pending

**test_crypto_filter_usecase.py (8 methods)** - **FEATURE TEST: Use explicit files**
- **Strategy:** Use explicit files for crypto filtering use cases
- **Input Files:** crypto project structure, config.json with filters
- **Progress:** ⏳ Pending

**test_parser_filtering.py (8 methods)** - Parser filtering logic
- **Strategy:** Use input-##.json for different filtering patterns
- **Input Files:** input-01.json (include filters), input-02.json (exclude filters), input-03.json (mixed filters)
- **Progress:** ⏳ Pending

**test_multiple_source_folders.py (7 methods)** - **FEATURE TEST: Use explicit files**
- **Strategy:** Use explicit files for multiple folder handling
- **Input Files:** folder1/, folder2/, folder3/, config.json
- **Progress:** ⏳ Pending

**test_generator_new_formatting.py (7 methods)** - New formatting features
- **Strategy:** Use input-##.json for formatting tests
- **Input Files:** input-01.json (new stereotypes), input-02.json (visibility formatting), input-03.json (relationship formatting)
- **Progress:** ⏳ Pending

**test_generator_visibility_logic.py (6 methods)** - Visibility detection logic
- **Strategy:** Use input-##.json for visibility tests
- **Input Files:** input-01.json (public/private), input-02.json (header detection), input-03.json (visibility edge cases)
- **Progress:** ⏳ Pending

### Medium Priority Files (18 files)

#### Configuration and Setup Files

**test_config.py (13 methods)** - Configuration handling
- **Strategy:** Use input-##.json for different config scenarios
- **Input Files:** input-01.json (basic config), input-02.json (advanced config), input-03.json (invalid config), input-04.json (file-specific config)
- **Progress:** ⏳ Pending

#### Generator Related Files

**test_include_filtering_bugs.py (12 methods)** - Include filtering edge cases
- **Strategy:** Use input-##.json for different bug scenarios
- **Input Files:** input-01.json (filter edge cases), input-02.json (regex patterns), input-03.json (performance issues)
- **Progress:** ⏳ Pending

**test_verifier.py (12 methods)** - Model verification logic
- **Strategy:** Use input-##.json for different validation scenarios
- **Input Files:** input-01.json (valid models), input-02.json (invalid models), input-03.json (edge case models)
- **Progress:** ⏳ Pending

**test_typedef_extraction.py (9 methods)** - Typedef extraction logic
- **Strategy:** Use input-##.json for different typedef scenarios
- **Input Files:** input-01.json (simple typedefs), input-02.json (complex typedefs), input-03.json (nested typedefs)
- **Progress:** ⏳ Pending

**test_utils.py (7 methods)** - Utility function testing
- **Strategy:** Use input-##.json for utility testing
- **Input Files:** input-01.json (file utils), input-02.json (string utils), input-03.json (path utils)
- **Progress:** ⏳ Pending

#### Parser Specific Files

**test_anonymous_structure_handling.py (5 methods)** - Anonymous structure handling
- **Strategy:** Use input-##.json for different handling scenarios
- **Input Files:** input-01.json (simple anonymous), input-02.json (nested anonymous), input-03.json (complex anonymous)
- **Progress:** ⏳ Pending

**test_transformation_system.py (5 methods)** - Transformation system
- **Strategy:** Use input-##.json for system testing
- **Input Files:** input-01.json (system config), input-02.json (system validation), input-03.json (system integration)
- **Progress:** ⏳ Pending

**test_crypto_filter_pattern.py (5 methods)** - Crypto filtering patterns
- **Strategy:** Use input-##.json for pattern testing
- **Input Files:** input-01.json (basic patterns), input-02.json (complex patterns), input-03.json (edge patterns)
- **Progress:** ⏳ Pending

**test_function_parameters.py (4 methods)** - Function parameter parsing
- **Strategy:** Use input-##.json for parameter scenarios
- **Input Files:** input-01.json (simple params), input-02.json (complex params), input-03.json (variadic params)
- **Progress:** ⏳ Pending

**test_file_specific_configuration.py (4 methods)** - File-specific config handling
- **Strategy:** Use input-##.json for file-specific scenarios
- **Input Files:** input-01.json (single file config), input-02.json (multiple file config), input-03.json (override config)
- **Progress:** ⏳ Pending

**test_absolute_path_bug_detection.py (4 methods)** - Path handling validation
- **Strategy:** Use input-##.json for path testing
- **Input Files:** input-01.json (absolute paths), input-02.json (relative paths), input-03.json (invalid paths)
- **Progress:** ⏳ Pending

#### Generator Testing Files

**test_generator_include_tree_bug.py (4 methods)** - Include tree validation
- **Strategy:** Use input-##.json for tree testing
- **Input Files:** input-01.json (simple tree), input-02.json (complex tree), input-03.json (circular tree)
- **Progress:** ⏳ Pending

**test_generator_naming_conventions.py (4 methods)** - Naming convention compliance
- **Strategy:** Use input-##.json for naming tests
- **Input Files:** input-01.json (class naming), input-02.json (relationship naming), input-03.json (stereotype naming)
- **Progress:** ⏳ Pending

**test_integration.py (4 methods)** - **FEATURE TEST: Use explicit files**
- **Strategy:** Use explicit files for integration scenarios
- **Input Files:** integration_project/, config.json
- **Progress:** ⏳ Pending

**test_generator_grouping.py (3 methods)** - Element grouping in output
- **Strategy:** Use input-##.json for grouping tests
- **Input Files:** input-01.json (public/private grouping), input-02.json (element grouping), input-03.json (visibility grouping)
- **Progress:** ⏳ Pending

**test_include_processing.py (3 methods)** - Include processing logic
- **Strategy:** Use input-##.json for processing tests
- **Input Files:** input-01.json (basic includes), input-02.json (nested includes), input-03.json (depth includes)
- **Progress:** ⏳ Pending

**test_parser_nested_structures.py (3 methods)** - Nested structure parsing
- **Strategy:** Use input-##.json for nested scenarios
- **Input Files:** input-01.json (simple nested), input-02.json (deep nested), input-03.json (complex nested)
- **Progress:** ⏳ Pending

**test_parser_struct_order.py (3 methods)** - Struct field order preservation
- **Strategy:** Use input-##.json for ordering tests
- **Input Files:** input-01.json (simple order), input-02.json (complex order), input-03.json (mixed order)
- **Progress:** ⏳ Pending

### Low Priority Files (8 files)

#### CLI Testing Files

**test_cli_modes.py (6 methods)** - **FEATURE TEST: Use explicit files**
- **Strategy:** Use explicit files - CLI mode switching tests complete workflows
- **Input Files:** test_project/, config.json
- **Progress:** ⏳ Pending

**test_cli_feature.py (5 methods)** - **FEATURE TEST: Use explicit files**
- **Strategy:** Use explicit files - focused on CLI interface validation
- **Input Files:** feature_test.c, feature_config.json, test_project/
- **Progress:** ⏳ Pending

#### Simple Unit Tests (Can use input-##.json or explicit files)

**test_generator_duplicate_includes.py (2 methods)** - Include duplication handling
- **Strategy:** Use explicit files - simple duplication scenario
- **Input Files:** duplicate_test.c, duplicate_includes.h, config.json
- **Progress:** ⏳ Pending

**test_generator_exact_format.py (2 methods)** - PlantUML formatting validation
- **Strategy:** Can use input-##.json for different format tests
- **Input Files:** input-01.json (basic format), input-02.json (advanced format)
- **Progress:** ⏳ Pending

**test_new_formatting_comprehensive.py (2 methods)** - **INTEGRATION TEST: Use explicit files**
- **Strategy:** Use explicit files for formatting integration tests
- **Input Files:** comprehensive_project/, config.json
- **Progress:** ⏳ Pending

**test_parser_function_params.py (2 methods)** - Function parameter parsing
- **Strategy:** Use input-##.json for parameter scenarios
- **Input Files:** input-01.json (simple params), input-02.json (complex params)
- **Progress:** ⏳ Pending

**test_parser_macro_duplicates.py (2 methods)** - Macro duplication handling
- **Strategy:** Use input-##.json for duplication scenarios
- **Input Files:** input-01.json (simple duplicates), input-02.json (complex duplicates)
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

## Input JSON File Examples

### Simple Struct Parsing Example
**File:** `input-01.json`
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
**File:** `input-02.json`
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

## Recommended Folder Structures

### Simple Unit Test (Input JSON Strategy)
```
test_parser_filtering/
├── test_parser_filtering.py
└── input/
    ├── input-01.json  # Self-contained: config + source + expected results
    ├── input-02.json  # Self-contained: config + source + expected results
    └── input-03.json  # Self-contained: config + source + expected results
```

### Feature Test (Explicit Files Strategy)
```
test_include_processing_features/
├── test_include_processing_features.py
├── input/
│   ├── config.json     # Required for explicit files approach
│   ├── main.c
│   ├── utils.h
│   ├── includes/
│   │   ├── level1.h
│   │   └── level2.h
│   └── types.h
└── assertions.json     # Required for Option 1 (explicit files approach)
```

### Split Large Test Example
```
test_struct_parsing/
├── test_struct_parsing.py
└── input/
    ├── input-01.json     # Simple struct parsing
    ├── input-02.json     # Nested struct parsing
    └── input-03.json     # Anonymous struct parsing

test_enum_parsing/
├── test_enum_parsing.py
└── input/
    ├── input-01.json       # Simple enum parsing
    └── input-02.json       # Typedef enum parsing
```

## Extended TestDataFactory Requirements

The TestDataFactory must support the following functionality for the input-##.json approach:

### Core Methods

```python
class TestDataFactory:
    def load_test_input(self, test_name: str) -> str:
        """Returns path to test_<n>/input/ directory for CLI execution"""
    
    def load_test_config(self, test_name: str, input_file: str = None) -> str:
        """Returns path to config.json (explicit) or extracts config from input_file for CLI execution"""
    
    def load_test_input_json(self, test_name: str, input_file: str = "input-01.json") -> dict:
        """Loads input-##.json from test_<n>/input/<input_file> and returns parsed content"""
    
    def generate_source_files_from_input(self, test_name: str, input_file: str = "input-01.json") -> str:
        """Generates source files from 'source_files' section and returns input path for CLI"""
    
    def generate_model_from_input(self, test_name: str, input_file: str = "input-01.json") -> str:
        """Generates model.json from 'input_model' section and returns input path for CLI"""
    
    def has_input_json(self, test_name: str, input_file: str = "input-01.json") -> bool:
        """Returns True if test_<n>/input/<input_file> exists"""
    
    def list_input_json_files(self, test_name: str) -> list:
        """Returns list of all input-##.json files in test_<n>/input/ directory"""
    
    def extract_config_from_input(self, test_name: str, input_file: str) -> str:
        """Extracts 'c2puml_config' section from input_file and creates temp config.json for CLI execution"""
```

### Input-##.json Structure Definition

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
    }
  }
}
```

## Migration Implementation Phases

### Phase 1: Framework Foundation (Weeks 1-2)
**Priority: CRITICAL**

1. **Implement Extended TestDataFactory**
   - `load_test_input_json(test_name, input_file)` - Load specific input files
   - `generate_source_files_from_input(test_name, input_file)` - Generate source files from input-##.json
   - `generate_model_from_input(test_name, input_file)` - Generate model.json from input-##.json
   - `has_input_json(test_name, input_file)` - Check if input files exist
   - `list_input_json_files(test_name)` - List all input files for a test

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
   - Convert to input-##.json approach
   - Test CLI-only interface implementation

2. **test_parser_macro_duplicates.py (2 methods)**
   - Use input-##.json files

3. **test_parser_nested_structures.py (3 methods)**
   - Use input-##.json files

**Verification Process for Each File:**
- Develop new structure → `pytest test_file.py` → `./run_all.sh`
- Ensure no regressions in existing functionality

### Phase 3: Major Refactoring (Weeks 5-8)
**Priority: CRITICAL - 3 large files requiring splits**

**Week 5-6: test_transformer.py (80 methods → 9 files)**
- Plan split strategy by transformation type
- Create 9 separate test folders with input-##.json files
- Implement and test each split file individually

**Week 7: test_tokenizer.py (41 methods → 4 files)**
- Split by token category
- Use input-##.json for each token type

**Week 8: test_parser_comprehensive.py (36 methods → 7 files)**
- Split by C language construct
- Create comprehensive input-##.json for each construct type

### Phase 4: Medium Priority (Weeks 9-10)
**18 files - Most using input-##.json strategy**

Focus on configuration, generator, and parser-specific files.

### Phase 5: Low Priority (Weeks 11-12)
**8 files - Mix of explicit files and input-##.json strategies**

Complete remaining files, including debug files and feature tests.

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

## Framework Cleanup

### Current Framework Files to Be Replaced/Removed

**🗑️ Files to be REMOVED after migration completion:**

1. **`/tests/utils.py` (374 lines)** - Existing test utilities
   - **Why remove:** Uses internal API imports (`from c2puml.generator import Generator`, etc.)
   - **Replaced by:** New `TestDataFactory` with CLI-only approach
   - **Progress:** ⏳ Pending - Remove after all tests migrated

2. **`/tests/feature/base.py` (189 lines)** - Feature test base class
   - **Why remove:** Uses internal API and direct pipeline calls
   - **Replaced by:** New `UnifiedTestCase` with CLI-only execution
   - **Progress:** ⏳ Pending - Remove after all tests migrated

3. **`/tests/conftest.py` (129 lines)** - pytest configuration
   - **Status:** **EVALUATE** - May be partially reusable for basic fixtures
   - **Decision needed:** Keep basic fixtures, remove any internal API dependencies
   - **Progress:** ⏳ Pending - Clean up after framework implementation

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

## Conclusion

This migration plan provides a comprehensive roadmap for transforming all 50 test files from internal API usage to a unified, maintainable, CLI-only testing framework. The analysis identifies specific strategies for each file, provides concrete examples of input structures and folder layouts, and establishes clear implementation phases.

**Key Success Factors:**
1. **Follow the strategy rule**: Feature tests = explicit files, Unit tests with multiple inputs = input-##.json
2. **Split large files early**: Don't attempt to migrate 80-method files as-is
3. **Implement framework first**: TestDataFactory and validation tools are critical
4. **Verify continuously**: Run full test suite after each migration
5. **Track progress**: Update todo.md with migration status

The detailed recommendations ensure that the migration will result in a robust, maintainable test suite that validates public API behavior while remaining flexible to internal implementation changes.