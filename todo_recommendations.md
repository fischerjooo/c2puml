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
- **Framework Foundation:** ⏳ Pending - TestInputFactory, TestExecutor, Validators
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

### Migration Progress Tracking

📋 **Complete progress tracking for all 50 test files has been moved to `todo.md`** for centralized management.

The progress tracking includes:
- **37 Unit Tests** - With detailed input-###.json naming strategies
- **9 Feature Tests** - Using explicit files (no splits needed)
- **2 Integration Tests** - Using explicit files (no splits needed)  
- **1 Special Feature Test** - Error handling test
- **1 Example Test** - Preserved as-is

**Key Status Information:**
- ⏳ **50 files pending migration**
- 🔴 **3 critical splits required**: `test_transformer.py`, `test_tokenizer.py`, `test_parser_comprehensive.py`
- ✅ **Framework design completed** with unified `TestInputFactory`

**👀 See `todo.md` → "Complete Test Migration Progress Tracking" for the full detailed table.**

## Input Strategy Guidelines

### The Core Rule

**Feature tests and example tests ALWAYS use explicit files** as they test complete workflows and need comprehensive project structures.

**Unit tests with multiple test methods requiring different inputs MUST use input-##.json approach.**

### Critical Insight: Feature Tests Generally Do NOT Need Splitting

**Since feature tests can only use explicit files (config.json + source files), all test methods in a feature test file share the same input project.** This means:

- **Feature tests typically should NOT be split** unless they test completely different features requiring different projects
- All test methods in a feature test can use the same input/ directory with the same config.json and source files  
- Each test method validates different aspects of the same comprehensive workflow
- Splitting would only be needed if the feature test file covers multiple unrelated features that require completely different project structures

### Input Strategy Guidelines

**Use input-##.json for:**
- Small unit test cases (< 50 lines of C code total)
- Multiple test scenarios in one test file
- Tests requiring different inputs per method
- **NEVER for feature tests or example tests**

**Use explicit files for:**
- **Feature tests (ALWAYS) - typically NO split needed**
- **Example tests (ALWAYS) - typically NO split needed**
- **Integration tests - typically NO split needed**
- Large test cases (> 50 lines of C code)
- Complex project structures

## Key Migration Insights

### Feature Test Splitting Analysis

**IMPORTANT DISCOVERY:** Most feature tests do NOT need splitting because:

1. **Explicit Files Constraint**: Feature tests can only use explicit files (config.json + source files)
2. **Shared Input Project**: All test methods in a feature test file share the same input project structure  
3. **Different Validation Aspects**: Each test method validates different aspects of the same comprehensive workflow
4. **Single Output Directory**: All test methods generate output to the same local output/ directory

**When Feature Tests SHOULD Be Split:**
- Only when they test completely different features requiring entirely different project structures
- When the feature test file covers multiple unrelated features (rare)

**When Feature Tests Should NOT Be Split (Most Cases):**
- When all test methods validate different aspects of the same feature
- When all test methods can share the same input project structure
- When test methods validate different pipeline stages (parse, transform, generate) of the same feature

**Migration Impact:**
- **10 feature tests** → **Direct migration without splitting** (vs. previous assumption of potential splits)
- **2 integration tests** → **Direct migration without splitting**
- **Reduced complexity** → Focus splits only on unit tests that actually benefit from input-##.json approach

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
- **Input Files Needed:** input-rename_functions.json, input-remove_elements.json, input-add_elements.json, input-file_selection.json, input-config_validation.json, input-error_scenarios.json, input-edge_cases.json, input-integration_workflow.json
- **Overall Progress:** ⏳ Pending - Requires planning phase first

**2. test_tokenizer.py (41 methods)** 🚨 CRITICAL SPLIT REQUIRED
- **Recommended Split:** 4 separate test files by token category
  - `test_tokenizer_keywords.py` - C keywords and reserved words - **Progress:** ⏳ Pending
  - `test_tokenizer_identifiers.py` - Variable/function names and identifiers - **Progress:** ⏳ Pending
  - `test_tokenizer_operators.py` - Operators and punctuation - **Progress:** ⏳ Pending
  - `test_tokenizer_complex.py` - Complex tokenization scenarios - **Progress:** ⏳ Pending
- **Input Strategy:** input-##.json for each token category
- **Input Files Needed:** input-keywords.json, input-identifiers.json, input-operators.json, input-complex_tokens.json
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
- **Input Files Needed:** input-simple_struct.json, input-nested_struct.json, input-anonymous_struct.json, input-simple_enum.json, input-function_decl.json, input-global_vars.json, input-include_processing.json, input-macro_processing.json, input-typedef_processing.json
- **Overall Progress:** ⏳ Pending - Requires planning phase first

#### High Priority Unit Tests Using Input JSON Strategy (21 files)

**test_generator.py (20 methods)**
- **Strategy:** Use input-##.json for different output scenarios
- **Recommended Input Files:**
  - input-simple_generation.json - Simple PlantUML generation
  - input-complex_diagrams.json - Complex diagrams with relationships
  - input-format_compliance.json - Formatting compliance tests
  - input-relationship_generation.json - Include/typedef relationships
- **Progress:** ⏳ Pending

**test_preprocessor_bug.py (19 methods)**
- **Strategy:** Use input-##.json for different directive types
- **Recommended Input Files:**
  - input-ifdef_testing.json - #ifdef/#ifndef testing
  - input-define_macros.json - #define macro testing
  - input-include_directives.json - #include directive testing
  - input-conditional_compilation.json - Complex conditional compilation
- **Progress:** ⏳ Pending

**test_invalid_source_paths.py (17 methods)**
- **Strategy:** Use input-##.json for different error scenarios
- **Recommended Input Files:**
  - input-missing_files.json - Missing source files
  - input-invalid_paths.json - Invalid path formats
  - input-permission_errors.json - Permission-related errors
- **Progress:** ⏳ Pending

**test_anonymous_processor_extended.py (14 methods)**
- **Strategy:** Use input-##.json for complexity levels
- **Recommended Input Files:**
  - input-basic_anonymous.json - Basic anonymous structures
  - input-nested_anonymous.json - Nested anonymous structures
  - input-complex_hierarchies.json - Complex hierarchies
- **Progress:** ⏳ Pending

**test_preprocessor_handling.py (14 methods)**
- **Strategy:** Use input-##.json by directive type
- **Recommended Input Files:**
  - input-conditional_compilation.json - Conditional compilation testing
  - input-macro_expansion.json - Macro expansion scenarios
- **Progress:** ⏳ Pending

**Other High Priority Unit Tests:**

**test_include_processing_features.py (12 methods)** - **FEATURE TEST: NO SPLIT NEEDED**
- **Strategy:** Use explicit files with config.json + source files - single comprehensive test suite
- **Rationale:** Feature tests can only use explicit files, so all 12 methods share the same input project structure
- **Input Files:** main.c, utils.h, includes/, config.json - ONE set for all test methods
- **Progress:** ⏳ Pending - Direct migration without splitting

**test_parser.py (10 methods)** - Core parser functionality
- **Strategy:** Use input-##.json for different parsing scenarios
- **Input Files:** input-basic_parsing.json, input-complex_parsing.json, input-error_handling.json
- **Progress:** ⏳ Pending

**test_global_parsing.py (9 methods)** - Global variable parsing
- **Strategy:** Use input-##.json for different global variable scenarios
- **Input Files:** input-simple_globals.json, input-complex_globals.json, input-initialized_globals.json
- **Progress:** ⏳ Pending

**test_component_features.py (9 methods)** - **FEATURE TEST: NO SPLIT NEEDED**
- **Strategy:** Use explicit files for component integration tests - single comprehensive test suite
- **Rationale:** Feature tests can only use explicit files, so all 9 methods share the same input project
- **Input Files:** main.c, headers/, config.json, project structure - ONE set for all test methods
- **Progress:** ⏳ Pending - Direct migration without splitting

**test_transformer_features.py (9 methods)** - **FEATURE TEST: NO SPLIT NEEDED**
- **Strategy:** Use explicit files for transformer feature testing - single comprehensive test suite
- **Rationale:** Feature tests can only use explicit files, so all 9 methods share the same transformation config
- **Input Files:** source files with transformation config.json - ONE set for all test methods
- **Progress:** ⏳ Pending - Direct migration without splitting

**test_comprehensive.py (9 methods)** - **INTEGRATION TEST: NO SPLIT NEEDED**
- **Strategy:** Use explicit files for complete workflows - single comprehensive test suite
- **Rationale:** Integration tests use explicit files like feature tests, single realistic project for all tests
- **Input Files:** realistic_project/, config.json - ONE set for all test methods
- **Progress:** ⏳ Pending - Direct migration without splitting

**test_multi_pass_anonymous_processing.py (8 methods)** - Multi-pass processing
- **Strategy:** Use input-##.json for multi-pass scenarios
- **Input Files:** input-simple_multipass.json, input-complex_multipass.json, input-nested_multipass.json
- **Progress:** ⏳ Pending

**test_crypto_filter_usecase.py (8 methods)** - **FEATURE TEST: NO SPLIT NEEDED**
- **Strategy:** Use explicit files for crypto filtering use cases - single comprehensive test suite
- **Rationale:** Feature tests can only use explicit files, so all 8 methods share the same crypto project
- **Input Files:** crypto project structure, config.json with filters - ONE set for all test methods
- **Progress:** ⏳ Pending - Direct migration without splitting

**test_parser_filtering.py (8 methods)** - Parser filtering logic
- **Strategy:** Use input-##.json for different filtering patterns
- **Input Files:** input-include_filters.json, input-exclude_filters.json, input-mixed_filters.json
- **Progress:** ⏳ Pending

**test_multiple_source_folders.py (7 methods)** - **FEATURE TEST: NO SPLIT NEEDED**
- **Strategy:** Use explicit files for multiple folder handling - single comprehensive test suite
- **Rationale:** Feature tests can only use explicit files, so all 7 methods share the same multi-folder project
- **Input Files:** folder1/, folder2/, folder3/, config.json - ONE set for all test methods
- **Progress:** ⏳ Pending - Direct migration without splitting

**test_generator_new_formatting.py (7 methods)** - New formatting features
- **Strategy:** Use input-##.json for formatting tests
- **Input Files:** input-new_stereotypes.json, input-visibility_formatting.json, input-relationship_formatting.json
- **Progress:** ⏳ Pending

**test_generator_visibility_logic.py (6 methods)** - Visibility detection logic
- **Strategy:** Use input-##.json for visibility tests
- **Input Files:** input-public_private.json, input-header_detection.json, input-visibility_edge_cases.json
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
**File:** `input-simple_struct.json`
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
**File:** `input-conditional_compilation.json`
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
    ├── input-include_filters.json  # Self-contained: config + source + expected results
    ├── input-exclude_filters.json  # Self-contained: config + source + expected results
    └── input-mixed_filters.json    # Self-contained: config + source + expected results
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
    ├── input-simple_struct.json     # Simple struct parsing
    ├── input-nested_struct.json     # Nested struct parsing
    └── input-anonymous_struct.json  # Anonymous struct parsing

test_enum_parsing/
├── test_enum_parsing.py
└── input/
    ├── input-simple_enum.json       # Simple enum parsing
    └── input-typedef_enum.json      # Typedef enum parsing
```

## Test Framework Public APIs

The unified test framework provides comprehensive public APIs for all testing scenarios. Here are the complete APIs organized by component:

### Core Framework Classes

```python
# Base Test Class
class UnifiedTestCase(unittest.TestCase, TestAssertionMixin):
    """Base class for all c2puml tests with built-in validation helpers"""
    
    def setUp(self) -> None:
        # Initialize all framework components
        self.executor = TestExecutor()
        self.input_factory = TestInputFactory()  # Unified input management
        self.model_validator = ModelValidator()
        self.puml_validator = PlantUMLValidator()
        self.output_validator = OutputValidator()
        self.file_validator = FileValidator()
        # Note: No ConfigValidator - we test c2puml's behavior with configs, not config structure
        
    def tearDown(self) -> None
    def create_temp_dir(self) -> str

# CLI Execution Engine  
class TestExecutor:
    """Executes c2puml through CLI interface only"""
    
    # Core Pipeline Execution
    def run_full_pipeline(self, input_path: str, config_path: str, output_dir: str) -> CLIResult
    def run_parse_only(self, input_path: str, config_path: str, output_dir: str) -> CLIResult
    def run_transform_only(self, config_path: str, output_dir: str) -> CLIResult  
    def run_generate_only(self, config_path: str, output_dir: str) -> CLIResult
    
    # Advanced Execution
    def run_with_verbose(self, input_path: str, config_path: str, output_dir: str) -> CLIResult
    def run_with_timeout(self, input_path: str, config_path: str, output_dir: str, timeout: int) -> CLIResult
    def run_expecting_failure(self, input_path: str, config_path: str, output_dir: str) -> CLIResult
    def run_with_timing(self, input_path: str, config_path: str, output_dir: str) -> TimedCLIResult
    def run_with_memory_tracking(self, input_path: str, config_path: str, output_dir: str) -> MemoryCLIResult
    
    # Output Management
    def get_test_output_dir(self, test_name: str, scenario: str = None) -> str:
        """Returns output directory path next to test file (output/ or output-<scenario>/)"""
    
    def cleanup_output_dir(self, output_dir: str) -> None:
        """Cleans output directory before test execution"""
    
    def preserve_output_for_review(self, output_dir: str) -> None:
        """Marks output directory to be preserved for manual review"""

# Test Data Management
class TestInputFactory:
    """Unified factory for managing all test input data (both explicit files and input-###.json)"""
    
    # Core Input Loading (Explicit Files Only)
    def load_test_input(self, test_name: str) -> str
    def load_test_config(self, test_name: str) -> str
    def load_test_assertions(self, test_name: str) -> dict
    def load_test_config_dict(self, test_name: str) -> dict
    
    # Input JSON File Discovery  
    def list_input_json_files(self, test_name: str) -> List[str]  # For finding available input-###.json files
    
    # Project Building
    def create_temp_project(self, files: Dict[str, str], config: dict = None) -> str
    def create_project_from_template(self, template_name: str, variables: dict = None) -> str
    def create_nested_project(self, structure: dict) -> str
    
    # Utility Methods
    def get_test_data_path(self, test_name: str, subpath: str = "") -> str
    def copy_test_files(self, source_path: str, dest_path: str) -> None
    def merge_configs(self, base_config: dict, override_config: dict) -> dict
    
    # Output Directory Management
    def get_output_dir_for_scenario(self, test_name: str, input_file: str = None) -> str:
        """Returns output directory path: output/ or output-<scenario_name>/"""
    
    def get_example_output_dir(self, test_name: str) -> str:
        """Returns artifacts/examples/<name>/ for example tests"""
    
    def ensure_output_dir_clean(self, output_dir: str) -> None:
        """Ensures output directory exists and is clean before test execution"""
```

### Validation Framework APIs

```python
# Model Validation
class ModelValidator:
    """Validates c2puml generated model.json files and content"""
    
    # Core Structure Validation
    def assert_model_structure_valid(self, model: dict) -> None
    def assert_model_schema_compliant(self, model: dict) -> None
    def assert_model_project_name(self, model: dict, expected_name: str) -> None
    def assert_model_file_count(self, model: dict, expected_count: int) -> None
    def assert_model_files_parsed(self, model: dict, expected_files: List[str]) -> None
    
    # Element Existence Validation
    def assert_model_function_exists(self, model: dict, func_name: str) -> None
    def assert_model_function_not_exists(self, model: dict, func_name: str) -> None
    def assert_model_struct_exists(self, model: dict, struct_name: str) -> None
    def assert_model_struct_not_exists(self, model: dict, struct_name: str) -> None
    def assert_model_enum_exists(self, model: dict, enum_name: str) -> None
    def assert_model_typedef_exists(self, model: dict, typedef_name: str) -> None
    def assert_model_global_exists(self, model: dict, global_name: str) -> None
    def assert_model_macro_exists(self, model: dict, macro_name: str) -> None
    
    # Include and Relationship Validation
    def assert_model_includes_exist(self, model: dict, expected_includes: List[str]) -> None
    def assert_model_include_exists(self, model: dict, include_name: str) -> None
    def assert_model_include_relationship(self, model: dict, source: str, target: str) -> None
    def assert_model_include_relationships_exist(self, model: dict, expected_relations: List[dict]) -> None
    
    # Advanced Element Validation
    def assert_model_function_signature(self, model: dict, func_name: str, return_type: str, params: List[str]) -> None
    def assert_model_struct_fields(self, model: dict, struct_name: str, expected_fields: List[str]) -> None
    def assert_model_enum_values(self, model: dict, enum_name: str, expected_values: List[str]) -> None
    def assert_model_macro_definition(self, model: dict, macro_name: str, expected_value: str) -> None
    
    # Pattern Matching and Advanced Validation
    def assert_model_functions_match_pattern(self, model: dict, pattern: str) -> List[str]
    def assert_model_structs_match_pattern(self, model: dict, pattern: str) -> List[str]
    def assert_model_includes_match_pattern(self, model: dict, pattern: str) -> List[str]
    def assert_model_element_count(self, model: dict, element_type: str, expected_count: int) -> None
    def assert_model_json_syntax_valid(self, model_file_path: str) -> None

# PlantUML Validation
class PlantUMLValidator:
    """Validates generated PlantUML files and diagram content"""
    
    # File Structure Validation
    def assert_puml_file_exists(self, output_dir: str, filename: str) -> None
    def assert_puml_file_count(self, output_dir: str, expected_count: int) -> None
    def assert_puml_file_syntax_valid(self, puml_content: str) -> None
    def assert_puml_start_end_tags(self, puml_content: str) -> None
    
    # Content Validation
    def assert_puml_contains(self, puml_content: str, expected_text: str) -> None
    def assert_puml_not_contains(self, puml_content: str, forbidden_text: str) -> None
    def assert_puml_contains_lines(self, puml_content: str, expected_lines: List[str]) -> None
    def assert_puml_line_count(self, puml_content: str, expected_count: int) -> None
    
    # Element Validation
    def assert_puml_class_exists(self, puml_content: str, class_name: str, stereotype: str = None) -> None
    def assert_puml_class_count(self, puml_content: str, expected_count: int) -> None
    def assert_puml_method_exists(self, puml_content: str, class_name: str, method_name: str) -> None
    def assert_puml_field_exists(self, puml_content: str, class_name: str, field_name: str) -> None
    
    # Relationship Validation
    def assert_puml_relationship(self, puml_content: str, source: str, target: str, rel_type: str) -> None
    def assert_puml_relationship_count(self, puml_content: str, expected_count: int) -> None
    def assert_puml_includes_arrow(self, puml_content: str, source: str, target: str) -> None
    def assert_puml_no_duplicate_relationships(self, puml_content: str) -> None
    
    # Formatting and Style Validation
    def assert_puml_formatting_compliant(self, puml_content: str) -> None
    def assert_puml_proper_stereotypes(self, puml_content: str) -> None
    def assert_puml_color_scheme(self, puml_content: str, expected_colors: dict) -> None
    def assert_puml_no_duplicate_elements(self, puml_content: str) -> None

# Output and File Validation
class OutputValidator:
    """Validates general output files, directories, and content"""
    
    # Directory and File System Validation
    def assert_output_dir_exists(self, output_path: str) -> None
    def assert_output_dir_structure(self, output_path: str, expected_structure: dict) -> None
    def assert_file_exists(self, file_path: str) -> None
    def assert_file_not_exists(self, file_path: str) -> None
    def assert_directory_empty(self, dir_path: str) -> None
    
    # File Content Validation
    def assert_file_contains(self, file_path: str, expected_text: str) -> None
    def assert_file_not_contains(self, file_path: str, forbidden_text: str) -> None
    def assert_file_contains_lines(self, file_path: str, expected_lines: List[str]) -> None
    def assert_file_line_count(self, file_path: str, expected_count: int) -> None
    def assert_file_empty(self, file_path: str) -> None
    def assert_file_size_under(self, file_path: str, max_size: int) -> None
    
    # Log and Output Validation
    def assert_log_contains(self, log_content: str, expected_message: str) -> None
    def assert_log_no_errors(self, log_content: str) -> None
    def assert_log_no_warnings(self, log_content: str) -> None
    def assert_log_error_count(self, log_content: str, expected_count: int) -> None
    def assert_log_execution_time(self, log_content: str, max_seconds: int) -> None

# Advanced File Operations
class FileValidator:
    """Advanced file validation and manipulation utilities"""
    
    # File Comparison and JSON Validation
    def assert_files_equal(self, file1_path: str, file2_path: str) -> None
    def assert_json_valid(self, json_file_path: str) -> None
    def assert_json_schema_valid(self, json_file_path: str, schema: dict) -> None
    def assert_json_contains_key(self, json_file_path: str, key_path: str) -> None
    
    # Advanced Content Validation
    def assert_file_valid_utf8(self, file_path: str) -> None
    def assert_file_no_trailing_whitespace(self, file_path: str) -> None
    def assert_file_unix_line_endings(self, file_path: str) -> None
    
    # Performance Validation
    def assert_execution_time_under(self, actual_time: float, max_time: float) -> None
    def assert_memory_usage_under(self, actual_memory: int, max_memory: int) -> None

# Configuration Behavior Testing (not structure validation)
# Note: We test c2puml's behavior with different configs, not the config structure itself
# c2puml validates its own configuration - we test the resulting behavior
```

### Helper Classes and Mixins

```python
# Common Test Assertion Patterns
class TestAssertionMixin:
    """Common assertion patterns for c2puml tests"""
    
    def assertCLISuccess(self, result: CLIResult, message: str = None) -> None
    def assertCLIFailure(self, result: CLIResult, expected_error: str = None) -> None
    def assertFilesGenerated(self, output_dir: str, expected_files: List[str]) -> None
    def assertValidModelGenerated(self, output_dir: str) -> dict
    def assertValidPlantUMLGenerated(self, output_dir: str) -> List[str]
    def loadInputJsonAndValidate(self, input_file_path: str) -> dict  # Load and validate input-###.json
    def assertConfigurationRejected(self, config_data: dict, expected_error: str = None) -> None  # Test invalid config handling
    def assertConfigurationAccepted(self, config_data: dict) -> CLIResult  # Test valid config acceptance
    def assertConfigBehavior(self, config_data: dict, expected_model_properties: dict) -> None  # Test config behavior

# Note: Input JSON functionality is now unified in TestInputFactory above

# Project Templates for Input JSON
class ProjectTemplates:
    """Pre-built input-###.json templates for common test scenarios"""
    
    @staticmethod
    def simple_struct_template(struct_name: str = "Point") -> dict
    
    @staticmethod
    def enum_template(enum_name: str = "Color") -> dict
    
    @staticmethod
    def include_hierarchy_template() -> dict

# Result Types
@dataclass
class CLIResult:
    """Standard result from CLI execution"""
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    command: List[str]
    working_dir: str

@dataclass  
class TimedCLIResult(CLIResult):
    """CLI result with detailed timing information"""
    parse_time: float
    transform_time: float  
    generate_time: float
    total_time: float

@dataclass
class MemoryCLIResult(CLIResult):
    """CLI result with memory usage tracking"""
    peak_memory_mb: int
    memory_samples: List[int]
    memory_timeline: List[tuple]
```

### Test Output Management and Git Configuration

**Test Folder Structure with Output Management:**
```
test_<name>/
├── test_<name>.py         # Test implementation
├── input/                 # Test input files
│   ├── config.json        # Option 1: Explicit config (feature/example tests)
│   ├── main.c             # Option 1: Source files
│   ├── input-scenario1.json # Option 2: JSON input files (unit tests)
│   └── input-scenario2.json
├── output/                # Single scenario output (Git ignored except examples)
│   ├── model.json
│   ├── diagram.puml
│   └── c2puml.log
├── output-scenario1/      # Multi-scenario output (Git ignored except examples)
│   ├── model.json
│   ├── diagram.puml
│   └── c2puml.log
└── output-scenario2/      # Multi-scenario output (Git ignored except examples)
    ├── model.json
    ├── diagram.puml
    └── c2puml.log
```

**Key Output Management Rules:**
1. **Local Output Review**: All test outputs are generated next to the test file for easy manual review
2. **Scenario-Specific Outputs**: Multiple input files create separate `output-<scenario>/` directories
3. **Git Ignore**: All test outputs are ignored except example test outputs (which serve as documentation)
4. **Example Test Exception**: Example tests output to `artifacts/examples/<name>/` instead of local directories

**Required .gitignore Updates:**
```gitignore
# Test output directories (except examples)
tests/unit/*/output/
tests/unit/*/output-*/
tests/feature/*/output/  
tests/feature/*/output-*/
tests/integration/*/output/
tests/integration/*/output-*/

# Keep example outputs for documentation
!tests/example/*/output/

# Temporary test files
*.tmp
*.temp
test_temp_*
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

1. **Implement TestInputFactory for Unified Input Management**
   - `load_explicit_files(test_name)` - Load explicit files (feature/example tests)
   - `load_input_json_scenario(test_name, input_file)` - Load input-###.json scenarios (unit tests)
   - `list_input_json_files(test_name)` - Discover available input-###.json files
   - `get_output_dir_for_scenario(test_name, scenario_name)` - Get output directory management
   - `ensure_output_dir_clean(output_dir)` - Clean output directories before test execution

2. **Implement TestExecutor for CLI-Only Interface**
   - `run_full_pipeline(input_path, config_path, output_dir)` - Complete workflow
   - `run_parse_only(input_path, config_path, output_dir)` - Parse step only
   - `run_transform_only(config_path, output_dir)` - Transform step only
   - `run_generate_only(config_path, output_dir)` - Generate step only

3. **Create Validation Framework**
   - `ModelValidator` - Model structure and content validation
   - `PlantUMLValidator` - PlantUML file validation
   - `OutputValidator` - General output file validation
   - `FileValidator` - Advanced file operations and validation
   - **Note**: No ConfigValidator - c2puml validates its own configuration

4. **Implement Helper Classes**
   - `TestAssertionMixin` - Common assertion patterns
   - `ProjectTemplates` - Pre-built input-###.json templates

5. **Establish Baseline**
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
   - **Replaced by:** New `TestInputFactory` with CLI-only approach
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
   - Ensure all 50 test files use new `TestInputFactory` and `TestExecutor`
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
3. **Implement framework first**: TestInputFactory and validation tools are critical
4. **Verify continuously**: Run full test suite after each migration
5. **Track progress**: Update todo.md with migration status

The detailed recommendations ensure that the migration will result in a robust, maintainable test suite that validates public API behavior while remaining flexible to internal implementation changes. Feature tests and example tests will always use explicit files to support comprehensive workflow testing, while unit tests can leverage input-##.json files for multiple test scenarios.