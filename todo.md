# C2PUML Test Framework Unification - Todo

## Executive Summary

This document outlines the comprehensive work required to transform the current c2puml test suite (58 test files across unit, feature, integration, and example categories) into a unified, maintainable, and robust testing framework. The primary focus is on **test-application boundary separation** and **public API testing** to ensure the application remains flexible to internal changes. The existing `tests/example/` structure will be preserved and enhanced with standardized expectations.

**Progress Tracking**: This document serves as the central workflow description to track migration progress. All milestones, completion status, and blocking issues should be updated directly in this file to maintain a clear record of the transformation progress.

**📋 Detailed Recommendations**: See `todo_recommendations.md` for comprehensive file-by-file analysis, specific migration strategies, data file recommendations, and progress tracking for all 50 test files. **Important:** Update both `todo.md` and `todo_recommendations.md` as migration work progresses.

**🗑️ Framework Cleanup**: The existing framework files (`tests/utils.py`, `tests/feature/base.py`) use internal APIs and will be completely removed after migration. These legacy files were not adapted as they conflict with the CLI-only approach required for proper test-application boundary separation.

## Current State Analysis

### Current Test Structure
- **58 test files** across 4 categories:
  - `tests/unit/` (37 files) - Individual component tests
  - `tests/feature/` (12 files) - Complete workflow tests  
  - `tests/integration/` (2 files) - End-to-end scenarios
  - `tests/example/` (1 file) - Example project test (to be preserved)
- **Mixed testing approaches**: Some tests use internal functions, others use public APIs
- **Inconsistent patterns**: Different test classes use different setup/teardown approaches
- **Direct internal access**: Many tests directly import and test internal components

**Note on Test Restructuring**: The refactoring of existing tests may require splitting up or restructuring test cases differently than their current organization. Some large test files may be broken down into multiple focused test cases, while related tests may be consolidated. This restructuring is necessary to align with the public API testing approach and improve test maintainability.

### Public API Surface (Target for Testing)
Based on analysis of the codebase, the public APIs are:

1. **CLI Interface** (`main.py`):
   ```bash
   c2puml --config config.json [parse|transform|generate]
   python3 main.py --config config.json [parse|transform|generate]
   ```

2. **Configuration Interface**:
   - JSON configuration files with standardized schema
   - Input: C/C++ source files and headers
   - Output: model.json, transformed_model.json, .puml files

## Work Items

### 1. Unified Testing Framework Design

#### 1.1 Core Testing Framework (`tests/framework/`)
**Priority: HIGH**

Create a new unified framework with these components:

- **`TestExecutor`**: Runs c2puml through public APIs only
- **`TestDataFactory`**: Generates test C/C++ projects and configurations, handles data.json files for dynamic input generation
- **`ResultValidator`**: Validates outputs (model.json, .puml files, logs)
- **`TestProjectBuilder`**: Builds temporary test projects with complex structures

```python
# Example structure
tests/framework/
├── __init__.py
├── executor.py      # TestExecutor class
├── data_factory.py  # TestDataFactory class  
├── validator.py     # ResultValidator class
├── builder.py       # TestProjectBuilder class
└── fixtures.py      # Common test fixtures
```

#### 1.2 Test Execution Patterns
**Priority: HIGH**

Standardize how tests execute c2puml:

```python
class UnifiedTestCase(unittest.TestCase):
    def setUp(self):
        self.executor = TestExecutor()
        self.data_factory = TestDataFactory()
        # Specialized validators for different aspects
        self.model_validator = ModelValidator()
        self.puml_validator = PlantUMLValidator()
        self.output_validator = OutputValidator()
        # Get test name from class name (e.g., TestParsing -> test_parsing)
        self.test_name = self.__class__.__name__.lower().replace('test', 'test_')
        # Create temporary output directory for this test
        self.output_dir = tempfile.mkdtemp()
        # Load assertion data if available - full dictionary access
        self.assertions = self.data_factory.load_test_assertions(self.test_name) if self.data_factory.has_test_assertions(self.test_name) else {}
    
    def test_feature(self):
        # 1. Get paths to test data for CLI execution
        input_path = self.data_factory.load_test_input(self.test_name)
        config_path = self.data_factory.load_test_config(self.test_name)  # Points to input/config.json
        
        # 2. Execute through CLI interface only
        result = self.executor.run_full_pipeline(input_path, config_path, self.output_dir)
        
        # 3. Validate CLI execution and results
        self.assertEqual(result.exit_code, 0, f"CLI failed: {result.stderr}")
        self.output_validator.assert_output_dir_exists(self.output_dir)
        self.output_validator.assert_log_no_errors(result.stdout)
        
        # 4. Load and validate generated files
        model_file = f"{self.output_dir}/model.json"
        self.model_validator.assert_model_json_syntax_valid(model_file)
        
        puml_files = glob.glob(f"{self.output_dir}/*.puml")
        self.assertGreater(len(puml_files), 0, "No PlantUML files generated")
        
        for puml_file in puml_files:
            self.puml_validator.assert_puml_file_syntax_valid(puml_file)
    
    def test_with_assertion_data(self):
        """Example of using assertions.json for large validation data"""
        input_path = self.data_factory.load_test_input(self.test_name)
        config_path = self.data_factory.load_test_config(self.test_name)  # Points to input/config.json
        
        result = self.executor.run_full_pipeline(input_path, config_path, self.output_dir)
        self.assertEqual(result.exit_code, 0)
        
        # Load model
        with open(f"{self.output_dir}/model.json", 'r') as f:
            model = json.load(f)
        
        # Use assertion data for validation (if assertions.json exists)
        if self.assertions:
            # Direct access to test-specific assertion data
            # Test can name its assertion sections however it wants
            
            # Example: Validate expected functions
            if "critical_functions" in self.assertions:
                for func_name in self.assertions["critical_functions"]:
                    self.model_validator.assert_model_function_exists(model, func_name)
            
            # Example: Validate forbidden elements  
            if "should_not_exist" in self.assertions:
                for func_name in self.assertions["should_not_exist"]:
                    self.model_validator.assert_model_function_not_exists(model, func_name)
            
            # Example: Validate PlantUML content with custom naming
            if "expected_main_puml_content" in self.assertions:
                main_puml_file = f"{self.output_dir}/main.puml"
                self.output_validator.assert_file_contains_lines(main_puml_file, self.assertions["expected_main_puml_content"])
            
            # Example: Test-specific validation with custom structure
            if "parser_validation" in self.assertions:
                parser_data = self.assertions["parser_validation"]
                if "required_structs" in parser_data:
                    for struct_name in parser_data["required_structs"]:
                        self.model_validator.assert_model_struct_exists(model, struct_name)
                if "include_chain" in parser_data:
                    self.model_validator.assert_model_include_relationships_exist(model, parser_data["include_chain"])
        else:
            # Fallback to inline assertions when no assertions.json
            self.model_validator.assert_model_function_exists(model, "main")
            self.model_validator.assert_model_struct_exists(model, "Point")
    
    def test_with_data_json_source_generation(self):
        """Example of using data.json for dynamic source file generation"""
        # Load test data and use structured sections
        data = self.data_factory.load_test_data_json(self.test_name, "data_struct_test.json")
        
        # Generate source files from 'source_files' section
        input_path = self.data_factory.generate_source_files_from_data(self.test_name, "data_struct_test.json")
        
        # Extract config from 'c2puml_config' section
        config_path = self.data_factory.extract_config_from_data(self.test_name, "data_struct_test.json")
        
        result = self.executor.run_full_pipeline(input_path, config_path, self.output_dir)
        self.assertEqual(result.exit_code, 0)
        
        # Validate against 'expected_results' section
        expected = data["expected_results"]["model_elements"]
        model_file = f"{self.output_dir}/model.json"
        with open(model_file, 'r') as f:
            model = json.load(f)
        
        for struct_name in expected["structs"]:
            self.model_validator.assert_model_struct_exists(model, struct_name)
    
    def test_multiple_data_cases(self):
        """Example of using multiple data.json files for different test cases"""
        # List all available data files for this test
        data_files = self.data_factory.list_data_json_files(self.test_name)
        
        for data_file in data_files:
            with self.subTest(data_case=data_file):
                # Load specific data case with structured sections
                data = self.data_factory.load_test_data_json(self.test_name, data_file)
                test_metadata = data["test_metadata"]
                
                # Generate appropriate input based on available sections
                if "source_files" in data:
                    input_path = self.data_factory.generate_source_files_from_data(self.test_name, data_file)
                elif "input_model" in data:
                    input_path = self.data_factory.generate_model_from_data(self.test_name, data_file)
                else:
                    input_path = self.data_factory.load_test_input(self.test_name)
                
                # Extract config from 'c2puml_config' section or use explicit config
                if "c2puml_config" in data:
                    config_path = self.data_factory.extract_config_from_data(self.test_name, data_file)
                else:
                    config_path = self.data_factory.load_test_config(self.test_name)
                
                # Execute pipeline
                result = self.executor.run_full_pipeline(input_path, config_path, self.output_dir)
                self.assertEqual(result.exit_code, 0, f"Failed for data case: {data_file}")
                
                # Validate results using 'expected_results' section
                if "expected_results" in data:
                    expected = data["expected_results"]
                    model_file = f"{self.output_dir}/model.json"
                    with open(model_file, 'r') as f:
                        model = json.load(f)
                    
                    # Validate model elements if specified
                    if "model_elements" in expected:
                        model_elements = expected["model_elements"]
                        for struct_name in model_elements.get("structs", []):
                            self.model_validator.assert_model_struct_exists(model, struct_name)
                        for func_name in model_elements.get("functions", []):
                            self.model_validator.assert_model_function_exists(model, func_name)
    
    def test_preferred_validation_approach(self):
        """Example showing the preferred validation approach using data.json expected_results"""
        # Load data.json with expected_results section (preferred approach)
        data = self.data_factory.load_test_data_json(self.test_name, "data_simple_test.json")
        input_path = self.data_factory.generate_source_files_from_data(self.test_name, "data_simple_test.json")
        config_path = self.data_factory.extract_config_from_data(self.test_name, "data_simple_test.json")
        
        result = self.executor.run_full_pipeline(input_path, config_path, self.output_dir)
        self.assertEqual(result.exit_code, 0)
        
        # Simple validation using expected_results from data.json - no complex structures needed
        expected = data["expected_results"]["model_elements"]
        with open(f"{self.output_dir}/model.json", 'r') as f:
            model = json.load(f)
        
        # Simple checks - exactly what the user specified is sufficient for any modification/transformation
        for struct_name in expected.get("structs", []):
            self.model_validator.assert_model_struct_exists(model, struct_name)
        for func_name in expected.get("functions", []):
            self.model_validator.assert_model_function_exists(model, func_name)
        
        # PlantUML validation using expected_results 
        if "plantuml_elements" in data["expected_results"]:
            puml_expected = data["expected_results"]["plantuml_elements"]
            for class_name in puml_expected.get("classes", []):
                puml_file = f"{self.output_dir}/main.puml"
                self.output_validator.assert_file_contains(puml_file, class_name)
        
        # Option 2 (Data.json): Use assertions section within data.json file
        if "assertions" in data:
            assertions = data["assertions"]
            if "large_function_list" in assertions:
                for func_name in assertions["large_function_list"]:
                    self.model_validator.assert_model_function_exists(model, func_name)
    
    def test_explicit_files_with_assertions_json(self):
        """Example using Option 1: explicit files + assertions.json"""
        input_path = self.data_factory.load_test_input(self.test_name)
        config_path = self.data_factory.load_test_config(self.test_name)
        
        result = self.executor.run_full_pipeline(input_path, config_path, self.output_dir)
        self.assertEqual(result.exit_code, 0)
        
        # Option 1 (Explicit files): Use external assertions.json file
        if self.data_factory.has_test_assertions(self.test_name):
            assertions = self.data_factory.load_test_assertions(self.test_name)
            if "critical_functions" in assertions:
                with open(f"{self.output_dir}/model.json", 'r') as f:
                    model = json.load(f)
                for func_name in assertions["critical_functions"]:
                    self.model_validator.assert_model_function_exists(model, func_name)
    
    def test_individual_steps(self):
        """Example of testing individual pipeline steps via CLI"""
        input_path = self.data_factory.load_test_input(self.test_name)
        config_path = self.data_factory.load_test_config(self.test_name)  # Points to input/config.json
        
        # Step 1: Parse only
        parse_result = self.executor.run_parse_only(input_path, config_path, self.output_dir)
        self.assertEqual(parse_result.exit_code, 0, f"Parse step failed: {parse_result.stderr}")
        
        model_file = f"{self.output_dir}/model.json"
        self.output_validator.assert_file_exists(model_file)
        self.model_validator.assert_model_json_syntax_valid(model_file)
        
        # Step 2: Transform only (operates on existing model.json)
        transform_result = self.executor.run_transform_only(config_path, self.output_dir)
        self.assertEqual(transform_result.exit_code, 0, f"Transform step failed: {transform_result.stderr}")
        
        # Step 3: Generate only (operates on transformed model)
        generate_result = self.executor.run_generate_only(config_path, self.output_dir)
        self.assertEqual(generate_result.exit_code, 0, f"Generate step failed: {generate_result.stderr}")
        
        # Validate final output
        puml_files = glob.glob(f"{self.output_dir}/*.puml")
        self.assertGreater(len(puml_files), 0, "No PlantUML files generated")
```

### 2. Public API Testing Strategy

#### 2.1 CLI Interface Testing
**Priority: HIGH**

All tests should execute c2puml through the CLI interface only:
- **CLI execution**: `subprocess.run(['python3', 'main.py', '--config', ...])` ✅
- **Individual steps**: `python3 main.py --config config.json [parse|transform|generate]` ✅

**Forbidden**: Direct imports of any internal modules:
- `from c2puml.core.parser import CParser` ❌
- `from c2puml.core.tokenizer import CTokenizer` ❌
- `from c2puml import Parser, Transformer, Generator` ❌

**Only Allowed**: CLI interface through main.py:
- `python3 main.py --config config.json` - Full pipeline
- `python3 main.py --config config.json parse` - Parse only
- `python3 main.py --config config.json transform` - Transform only  
- `python3 main.py --config config.json generate` - Generate only

#### 2.2 Test Input/Output Validation
**Priority: HIGH**

Tests should validate:
- **Input validation**: Configuration files, C/C++ source structure
- **Output validation**: Generated model.json structure, PlantUML syntax, file organization
- **Log validation**: Error messages, warning patterns, execution flow

### 3. Test Data Management

#### 3.1 Standardized Test Data Factory
**Priority: MEDIUM**

Create reusable test data generators:

```python
class TestDataFactory:
    def load_test_input(self, test_name: str) -> str:
        """Returns path to test_<name>/input/ directory for CLI execution"""
    
    def load_test_config(self, test_name: str, data_file: str = None) -> str:
        """Returns path to config.json (explicit) or extracts config from data_file for CLI execution"""
    
    def load_test_assertions(self, test_name: str, data_file: str = None) -> dict:
        """Loads assertion data from test_<n>/assertions.json (Option 1) or from data_file.assertions (Option 2)"""
    
    def has_test_assertions(self, test_name: str, data_file: str = None) -> bool:
        """Returns True if assertions exist in assertions.json (Option 1) or in data_file.assertions (Option 2)"""
    
    def create_temp_project(self, input_files: dict) -> str:
        """Creates temporary project and returns path for CLI execution"""
    
    def get_test_data_path(self, test_name: str, subpath: str = "") -> str:
        """Returns absolute path to test data for CLI arguments"""
    
    def load_test_data_json(self, test_name: str, data_file: str = "data.json") -> dict:
        """Loads data.json from test_<n>/input/<data_file> and returns parsed content"""
    
    def generate_source_files_from_data(self, test_name: str, data_file: str = "data.json") -> str:
        """Generates source files from data.json 'source_files' section and returns input path for CLI"""
    
    def generate_model_from_data(self, test_name: str, data_file: str = "data.json") -> str:
        """Generates model.json from data.json 'input_model' section and returns input path for CLI"""
    
    def has_data_json(self, test_name: str, data_file: str = "data.json") -> bool:
        """Returns True if test_<n>/input/<data_file> exists"""
    
    def list_data_json_files(self, test_name: str) -> list:
        """Returns list of all data*.json files in test_<n>/input/ directory"""
    
    def extract_config_from_data(self, test_name: str, data_file: str) -> str:
        """Extracts 'c2puml_config' section from data_file and creates temp config.json for CLI execution"""


class TestExecutor:
    def run_cli_command(self, command: list, cwd: str = None) -> CLIResult:
        """Executes CLI command and returns result with output, logs, and exit code"""
    
    def run_full_pipeline(self, input_path: str, config_path: str, output_dir: str) -> CLIResult:
        """Runs complete pipeline: python3 main.py --config <config>"""
    
    def run_parse_only(self, input_path: str, config_path: str, output_dir: str) -> CLIResult:
        """Runs parse step only: python3 main.py --config <config> parse"""
    
    def run_transform_only(self, config_path: str, output_dir: str) -> CLIResult:
        """Runs transform step only: python3 main.py --config <config> transform"""
    
    def run_generate_only(self, config_path: str, output_dir: str) -> CLIResult:
        """Runs generate step only: python3 main.py --config <config> generate"""
```

#### 3.2 Self-Contained Test Data
**Priority: MEDIUM**

Each test folder contains its own project and configuration data:

**Test Folder Structure Pattern:**
```
test_<n>/
├── test_<n>.py         # Test implementation
├── input/              # Test input files - choose ONE approach per test
│   # Option 1: Explicit files approach (all test methods use same input)
│   ├── config.json     # c2puml configuration
│   ├── main.c          # Source files for testing
│   ├── utils.h         # Header files
│   ├── model.json      # Optional: Pre-parsed model for transformation testing
│   └── subdir/         # Optional: Nested directories
│   # Option 2: Data.json approach (NO config.json or source files)
│   ├── data_case1.json # Test case 1: complete config + source + expected results + assertions
│   ├── data_case2.json # Test case 2: complete config + content + expected results + assertions
│   └── data_case3.json # Test case 3: complete config + scenarios + expected results + assertions
└── assertions.json     # Used ONLY with Option 1 (explicit files approach)
```

**Input Data Options:**

**Configuration Flexibility:** Tests can use either:
- Explicit `config.json` file for single-use-case scenarios
- Configuration embedded within `data_case#.json` files for multi-use-case scenarios
- Mixed approach: default `config.json` with overrides in `data_case#.json`

**Content Specification:**
For **smaller source inputs**, tests can specify source file structure and content in `data.json` files found in the input folder. This allows generating the required source files or model.json files dynamically based on the test case needs.

For **larger inputs**, it is recommended to use explicit input files (actual .c/.h files) rather than data.json specifications for better readability and maintainability.

**Input Structure per Use Case:**
- **Option 1 (Explicit files):** config.json + source files + assertions.json - NO data.json files
- **Option 2 (Data.json):** ONLY data_*.json files (completely self-contained including assertions) - NO config.json, source files, or assertions.json

**Data.json Structure Guidelines:**

**Clear Section Organization:**
- `test_metadata`: Test description, type, expected duration, focus area
- `c2puml_config`: Complete c2puml configuration (equivalent to config.json content)
- `source_files`: C/C++ source code content (for source generation tests)
- `input_model`: Pre-parsed model data (for transformation/generation-only tests)
- `expected_results`: Expected outputs for validation
- `assertions`: Large assertion data (equivalent to assertions.json content) - optional

**Multiple Test Cases per File:**
Per test.py file which contains multiple test cases, there can be multiple data.json files with different names (e.g., `data_case1.json`, `data_case2.json`) for each test case which can be individually loaded. The TestDataFactory shall have extended functionality to handle these data.json files and generate the inputs needed for testing.

**Important Input Strategy Decision:**
If a test.py file requires **multiple or different inputs** to run various tests, then it **must use the data_##.json input scheme**. This is because when explicit files are used as input, all tests in that test.py file must use the same input files, since there is only a single `input/` folder per test. The data_##.json approach allows each test method to generate its own specific input requirements dynamically.

**Example data.json Structure for Source Generation:**
```json
{
  "test_metadata": {
    "description": "Source file specification for smaller test inputs",
    "test_type": "unit",
    "expected_duration": "fast"
  },
  "c2puml_config": {
    "project_name": "test_small_project",
    "source_folders": ["."],
    "output_dir": "./output",
    "recursive_search": true,
    "include_depth": 2,
    "file_extensions": [".c", ".h"]
  },
  "source_files": {
    "main.c": "#include <stdio.h>\n#include \"types.h\"\n\nint main() {\n    Point p = {10, 20};\n    return 0;\n}",
    "types.h": "#ifndef TYPES_H\n#define TYPES_H\n\ntypedef struct {\n    int x;\n    int y;\n} Point;\n\n#endif"
  },
  "expected_results": {
    "model_elements": {
      "structs": ["Point"],
      "functions": ["main"],
      "includes": ["stdio.h", "types.h"]
    },
    "plantuml_elements": {
      "classes": ["Point"],
      "relationships": []
    }
  },
  "assertions": {
    "large_function_list": ["func1", "func2", "func3"],
    "complex_validation_data": {
      "nested_structures": ["Point", "Rectangle", "Circle"]
    }
  }
}
```

**Example data_case1.json for Model Generation:**
```json
{
  "test_metadata": {
    "description": "Pre-parsed model for transformation testing",
    "test_type": "integration",
    "focus": "transformation_pipeline"
  },
  "c2puml_config": {
    "project_name": "test_transformation",
    "source_folders": ["."],
    "output_dir": "./output",
    "transformations": {
      "rename": {
        "functions": {"^deprecated_(.*)": "legacy_\\1"}
      },
      "remove": {
        "macros": ["LEGACY_MACRO"],
        "includes": ["time.h"]
      }
    }
  },
  "input_model": {
    "project_name": "test_transformation",
    "files": {
      "main.c": {
        "functions": [
          {"name": "deprecated_print_info", "return_type": "void", "parameters": []},
          {"name": "main", "return_type": "int", "parameters": []}
        ],
        "macros": ["LEGACY_MACRO", "VERSION"],
        "includes": ["stdio.h", "time.h", "config.h"]
      }
    }
  },
  "expected_results": {
    "transformed_model": {
      "functions": [
        {"name": "legacy_print_info", "return_type": "void"},
        {"name": "main", "return_type": "int"}
      ],
      "macros": ["VERSION"],
      "includes": ["stdio.h", "config.h"]
    }
  },
  "assertions": {
    "transformation_validation": {
      "removed_functions": ["deprecated_print_info"],
      "renamed_functions": {"deprecated_print_info": "legacy_print_info"},
      "removed_includes": ["time.h"]
    }
  }
}
```

**Example assertions.json Structure (Simple, Optional):**
```json
{
  "description": "Optional large assertion data - only when data.json expected_results are insufficient",
  
  "large_string_lists": [
    "very_long_function_name_1", "very_long_function_name_2", 
    "very_long_function_name_3", "...", "very_long_function_name_100"
  ],
  
  "complex_nested_data": {
    "large_include_hierarchy": {
      "level1": ["stdio.h", "stdlib.h", "string.h"],
      "level2": ["custom_header1.h", "custom_header2.h"],
      "level3": ["deep_nested_header.h"]
    }
  },
  
  "bulky_test_data": {
    "large_expected_output": "...very long PlantUML content or large JSON structures that would clutter data.json..."
  }
}
```

**Note:** Most tests should use `expected_results` in data.json files instead of assertions.json. Use assertions.json only for:
- Large lists that would clutter data.json
- Complex nested validation data
- Bulky expected outputs (long PlantUML content, large JSON structures)

**Benefits of Self-Contained Structure:**
- **Isolation**: Each test has its own data, preventing cross-test interference
- **Clarity**: Test data is co-located with test logic for easy understanding
- **Maintainability**: Changes to one test don't affect others
- **Versioning**: Test data and logic evolve together
- **Debugging**: Easier to reproduce issues with self-contained test environments
- **Clean Test Code**: Large assertion data is externalized, keeping test methods focused
- **Unified Input Location**: All application inputs (config, source, model files) are in one place
- **Consistent CLI Arguments**: CLI input path points to folder containing all necessary files
- **Logical Grouping**: Configuration naturally belongs with the files it configures
- **Flexible Assertion Data**: Tests can structure assertions.json with any naming and organization
- **Test-Specific Validation**: Each test defines its own assertion structure and validation logic
- **Dynamic Input Generation**: Support for data.json files allows flexible input generation for smaller test cases
- **Multiple Test Cases**: Single test.py files can handle multiple scenarios using different data files

**Input Size Guidelines:**

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

**Validation Approach:**
- **Primary:** Use `expected_results` section in data.json files - simple model and PlantUML expectations are sufficient for any modification/transformation validation
- **Optional:** Use assertions.json only for large data lists that would clutter data.json files (rarely needed)

**Key Constraint:** Each test folder can use ONE approach only:
- **Option 1 (Explicit files):** input/ contains config.json + source files + model.json, PLUS assertions.json (all test methods share same input)
- **Option 2 (Data.json):** input/ contains ONLY data_*.json files (each completely self-contained including assertions) - NO config.json, source files, or assertions.json

**Example Scenarios:**

```python
# ❌ PROBLEMATIC: This test class needs different inputs per method
class TestParserFeatures(UnifiedTestCase):
    def test_simple_struct_parsing(self):
        # Needs: simple.c with basic struct
        
    def test_complex_nested_parsing(self):
        # Needs: complex.c with nested structures
        
    def test_macro_expansion_parsing(self):
        # Needs: macros.c with complex macro definitions
```

**Solution: Use data_##.json files:**
```
test_parser_features/
├── test_parser_features.py
└── input/
    ├── data_simple.json      # Self-contained: config + source + expected results + assertions
    ├── data_complex.json     # Self-contained: config + source + expected results + assertions
    └── data_macros.json      # Self-contained: config + source + expected results + assertions
```

```python
# ✅ CORRECT: Each test method gets its own input via data files
class TestParserFeatures(UnifiedTestCase):
    def test_simple_struct_parsing(self):
        input_path = self.data_factory.generate_source_files_from_data(self.test_name, "data_simple.json")
        
    def test_complex_nested_parsing(self):
        input_path = self.data_factory.generate_source_files_from_data(self.test_name, "data_complex.json")
        
    def test_macro_expansion_parsing(self):
        input_path = self.data_factory.generate_source_files_from_data(self.test_name, "data_macros.json")
```

### 4. Result Validation Framework

#### 4.1 Generic vs Custom Validation Strategy
**Priority: HIGH**

The validation framework provides two approaches for test validation:

**🔧 Generic Framework Validation (Recommended for most cases):**
- Use `ModelValidator`, `PlantUMLValidator`, `OutputValidator`
- Covers 90% of common validation scenarios
- Consistent, reusable, and maintainable
- Well-tested validation logic

**🎯 Custom Validation (For complex edge cases):**
- Implement custom validation methods within test cases
- Handle complex algorithms, edge cases, or domain-specific validation
- Use when generic framework limitations are encountered
- Combine with generic validation for comprehensive coverage

#### 4.2 Model Validation
**Priority: HIGH**

Structured validation of generated models:

**Example Usage:**
```python
def test_transformations_via_normal_model_validation(self):
    # Execute pipeline with transformations configured in input/config.json
    input_path = self.data_factory.load_test_input(self.test_name)
    config_path = self.data_factory.load_test_config(self.test_name)  # Points to input/config.json
    result = self.executor.run_full_pipeline(input_path, config_path, self.output_dir)
    self.assertEqual(result.exit_code, 0)
    
    # Load the final model (after transformations have been applied)
    with open(f"{self.output_dir}/model.json", 'r') as f:
        model = json.load(f)
    
    # Validate model structure (standard validation)
    self.model_validator.assert_model_structure_valid(model)
    self.model_validator.assert_model_files_parsed(model, ["main.c", "utils.h"])
    
    # Validate transformation results using normal model assertions
    # ✅ Renamed function should exist in final model
    self.model_validator.assert_model_function_exists(model, "legacy_print_info")
    
    # ❌ Original function should NOT exist in final model
    self.model_validator.assert_model_function_not_exists(model, "deprecated_print_info")
    
    # ❌ Removed elements should NOT exist in final model
    self.model_validator.assert_model_function_not_exists(model, "test_debug_function")
    self.model_validator.assert_model_macro_not_exists(model, "LEGACY_MACRO")
    
    # ✅ Preserved elements should still exist
    expected_includes = ["stdio.h", "sample.h", "config.h"]
    self.model_validator.assert_model_includes_exist(model, expected_includes)
    
    # ❌ Removed includes should NOT exist
    self.model_validator.assert_model_include_not_exists(model, "time.h")  # Removed by config
    
    # Validate file content reflects transformations
    expected_model_lines = [
        '"name": "legacy_print_info"',  # Renamed function appears
        '"includes": ["stdio.h", "sample.h", "config.h"]'  # Expected includes
    ]
    forbidden_model_lines = [
        '"deprecated_print_info"',  # Original function name should not appear
        '"test_debug_function"',    # Removed function should not appear
        '"LEGACY_MACRO"',           # Removed macro should not appear
        '"time.h"'                  # Removed include should not appear
    ]
    
    model_file_path = f"{self.output_dir}/model.json"
    self.model_validator.assert_model_file_contains_lines(model_file_path, expected_model_lines)
    self.model_validator.assert_model_file_not_contains_lines(model_file_path, forbidden_model_lines)
```

```python
class ModelValidator:
    # Model structure and content validation
    def assert_model_structure_valid(self, model: dict)
    def assert_model_files_parsed(self, model: dict, expected_files: list)
    def assert_model_file_count(self, model: dict, expected_count: int)
    def assert_model_project_name(self, model: dict, expected_name: str)
    
    # Model element existence validation
    def assert_model_struct_exists(self, model: dict, struct_name: str)
    def assert_model_struct_not_exists(self, model: dict, struct_name: str)
    def assert_model_function_exists(self, model: dict, func_name: str)
    def assert_model_function_not_exists(self, model: dict, func_name: str)
    def assert_model_function_declared(self, model: dict, func_name: str)
    def assert_model_enum_exists(self, model: dict, enum_name: str)
    def assert_model_enum_not_exists(self, model: dict, enum_name: str)
    def assert_model_typedef_exists(self, model: dict, typedef_name: str)
    def assert_model_typedef_not_exists(self, model: dict, typedef_name: str)
    def assert_model_global_exists(self, model: dict, global_name: str)
    def assert_model_global_not_exists(self, model: dict, global_name: str)
    def assert_model_macro_exists(self, model: dict, macro_name: str)
    def assert_model_macro_not_exists(self, model: dict, macro_name: str)
    
    # Model includes validation
    def assert_model_includes_exist(self, model: dict, expected_includes: list)
    def assert_model_include_exists(self, model: dict, include_name: str)
    def assert_model_include_not_exists(self, model: dict, include_name: str)
    
    # Model relationship validation
    def assert_model_include_relationship(self, model: dict, source: str, target: str)
    def assert_model_include_relationships_exist(self, model: dict, expected_relations: list)
    def assert_model_typedef_relationship(self, model: dict, typedef: str, original: str)
    
    # Model file validation
    def assert_model_file_contains_lines(self, model_file_path: str, expected_lines: list)
    def assert_model_file_not_contains_lines(self, model_file_path: str, forbidden_lines: list)
    def assert_model_file_structure_valid(self, model_file_path: str)
    def assert_model_json_syntax_valid(self, model_file_path: str)
```

#### 4.3 PlantUML Validation
**Priority: HIGH**

Validation of generated PlantUML files:

```python
class PlantUMLValidator:
    # PlantUML file validation
    def assert_puml_file_exists(self, output_dir: str, filename: str)
    def assert_puml_file_count(self, output_dir: str, expected_count: int)
    def assert_puml_file_syntax_valid(self, puml_content: str)
    
    # PlantUML content validation
    def assert_puml_contains(self, puml_content: str, expected_text: str)
    def assert_puml_not_contains(self, puml_content: str, forbidden_text: str)
    def assert_puml_contains_lines(self, puml_content: str, expected_lines: list)
    def assert_puml_not_contains_lines(self, puml_content: str, forbidden_lines: list)
    def assert_puml_class_exists(self, puml_content: str, class_name: str, stereotype: str)
    def assert_puml_class_count(self, puml_content: str, expected_count: int)
    
    # PlantUML relationship validation
    def assert_puml_relationship(self, puml_content: str, source: str, target: str, rel_type: str)
    def assert_puml_relationship_count(self, puml_content: str, expected_count: int)
    def assert_puml_includes_arrow(self, puml_content: str, source: str, target: str)
    def assert_puml_declares_relationship(self, puml_content: str, file: str, typedef: str)
    
    # PlantUML formatting validation
    def assert_puml_formatting_compliant(self, puml_content: str)
    def assert_puml_no_duplicate_elements(self, puml_content: str)
    def assert_puml_proper_stereotypes(self, puml_content: str)
    def assert_puml_color_scheme(self, puml_content: str)
    def assert_puml_visibility_notation(self, puml_content: str)
    
    # PlantUML structure validation
    def assert_puml_start_end_tags(self, puml_content: str)
    def assert_puml_proper_grouping(self, puml_content: str)
    def assert_puml_no_syntax_errors(self, puml_content: str)


class OutputValidator:
    # Configuration file validation
    def assert_config_file_exists(self, config_path: str)
    def assert_config_json_valid(self, config_content: str)
    def assert_config_schema_valid(self, config: dict)
    
    # Output directory validation
    def assert_output_dir_exists(self, output_path: str)
    def assert_output_dir_structure(self, output_path: str, expected_structure: dict)
    def assert_output_file_count(self, output_path: str, expected_count: int)
    
    # File content validation
    def assert_file_exists(self, file_path: str)
    def assert_file_contains(self, file_path: str, expected_text: str)
    def assert_file_not_contains(self, file_path: str, forbidden_text: str)
    def assert_file_contains_lines(self, file_path: str, expected_lines: list)
    def assert_file_not_contains_lines(self, file_path: str, forbidden_lines: list)
    def assert_file_line_count(self, file_path: str, expected_count: int)
    def assert_file_empty(self, file_path: str)
    def assert_file_not_empty(self, file_path: str)
    
    # Log validation
    def assert_log_contains(self, log_content: str, expected_message: str)
    def assert_log_contains_lines(self, log_content: str, expected_lines: list)
    def assert_log_no_errors(self, log_content: str)
    def assert_log_warning_count(self, log_content: str, expected_count: int)
    def assert_log_execution_time(self, log_content: str, max_seconds: int)
    
    # Performance validation
    def assert_execution_time_under(self, actual_time: float, max_time: float)
    def assert_memory_usage_under(self, actual_memory: int, max_memory: int)
    def assert_file_size_under(self, file_path: str, max_size: int)


class CustomValidationMixin:
    """Mixin for tests that need custom validation beyond the generic framework"""
    
    def validate_with_custom_logic(self, model: dict, puml_files: list, test_specific_checks: callable):
        """
        Template method for combining generic validation with custom edge case validation.
        
        Args:
            model: Parsed model.json content
            puml_files: List of generated PlantUML files
            test_specific_checks: Callable that performs test-specific validation
        """
        # First run standard generic validations
        self.model_validator.assert_model_structure_valid(model)
        
        for puml_file in puml_files:
            self.puml_validator.assert_puml_file_syntax_valid(puml_file)
        
        # Then run custom validation logic
        test_specific_checks(model, puml_files)
    
    def build_include_dependency_graph(self, model: dict) -> dict:
        """Helper method to build include dependency graph for custom analysis"""
        include_graph = {}
        for filename, file_data in model['files'].items():
            include_graph[filename] = file_data.get('includes', [])
        return include_graph
    
    def extract_elements_by_pattern(self, model: dict, element_type: str, pattern: str) -> list:
        """Helper method to extract elements matching specific patterns"""
        import re
        elements = []
        regex = re.compile(pattern)
        
        for file_data in model['files'].values():
            for element in file_data.get(element_type, []):
                element_name = element if isinstance(element, str) else element.get('name', '')
                if regex.match(element_name):
                    elements.append(element)
        return elements
```

#### 4.4 Custom Validation for Edge Cases
**Priority: MEDIUM**

When the generic validation framework cannot handle specific edge cases, implement custom validation logic:

**Common Edge Cases Requiring Custom Validation:**
- **Complex Anonymous Structure Hierarchies**: Multi-level nested anonymous structures with complex naming
- **Circular Include Detection**: Custom algorithms to detect and validate circular dependencies
- **Conditional Compilation Logic**: Macro expansion consistency and preprocessor directive handling
- **Complex Transformation Patterns**: Multi-step transformations with interdependencies
- **Performance Characteristics**: Memory usage, parsing time, or output file size validation
- **Domain-Specific Algorithms**: Custom C language feature handling or specialized parsing logic

**Example Custom Validation Pattern:**
```python
class TestComplexFeature(UnifiedTestCase, CustomValidationMixin):
    def test_complex_edge_case(self):
        # 1. Standard CLI execution
        result = self.executor.run_full_pipeline(input_path, config_path, self.output_dir)
        self.assertEqual(result.exit_code, 0)
        
        # 2. Load generated files
        with open(f"{self.output_dir}/model.json", 'r') as f:
            model = json.load(f)
        puml_files = glob.glob(f"{self.output_dir}/*.puml")
        
        # 3. Generic validation first
        self.model_validator.assert_model_structure_valid(model)
        for puml_file in puml_files:
            self.puml_validator.assert_puml_file_syntax_valid(puml_file)
        
        # 4. Custom validation for edge cases
        self._validate_complex_algorithm_specific_behavior(model, puml_files)
    
    def _validate_complex_algorithm_specific_behavior(self, model: dict, puml_files: list):
        # Custom validation logic that generic framework cannot handle
        # Example: validate complex anonymous struct naming patterns
        anonymous_structs = self.extract_elements_by_pattern(
            model, 'structs', r'.*Container_.*_config_.*'
        )
        self.assertGreater(len(anonymous_structs), 0, "Complex anonymous patterns not found")
        
        # Example: validate custom include dependency resolution
        include_graph = self.build_include_dependency_graph(model)
        self._assert_no_circular_dependencies(include_graph)
```

#### 4.5 Example Test Validation
**Priority: MEDIUM**

The `tests/example/` directory should be preserved with its current structure but enhanced with a standardized expectations file. **Note**: The example test has a different structure than other tests:

**Example Test Structure (preserved as-is):**
```
tests/example/
├── source/             # C/C++ source files (different from other tests' input/)
├── config.json         # Existing configuration (different from test-specific structure)
├── test-example.py     # Example workflow test
└── test-example.json   # NEW - Expected outputs specification
```

**Proposed test-example.json for validation:**
```json
// tests/example/test-example.json
{
  "description": "Expected outputs for example project test",
  "note": "This test uses source/ folder with config.json at root level, unlike other tests that use input/ folder with config.json inside input/",
  "model_expectations": {
    "files_count": 3,
    "required_files": ["sample.c", "sample.h", "config.h"],
    "structs": ["Point", "Rectangle", "User"],
    "functions": ["main", "calculate_area", "init_config", "legacy_print_info"],
    "enums": ["Color", "Status"],
    "typedefs": ["int32_t", "point_t"],
    "includes": ["stdio.h", "stdlib.h", "sample.h", "config.h"],
    "include_relations": [
      {"source": "sample.c", "target": "stdio.h"},
      {"source": "sample.c", "target": "sample.h"},
      {"source": "sample.h", "target": "config.h"}
    ],
    "forbidden_elements": ["deprecated_print_info", "test_debug_function", "LEGACY_MACRO"]
  },
  "puml_expectations": {
    "generated_files": ["sample.puml"],
    "required_classes": [
      {"name": "sample", "stereotype": "source"},
      {"name": "sample.h", "stereotype": "header"},
      {"name": "Point", "stereotype": "struct"}
    ],
    "required_relationships": [
      {"source": "SAMPLE", "target": "HEADER_SAMPLE", "type": "include"}
    ],
    "required_content_lines": [
      "class \"sample\" as SAMPLE <<source>> #LightBlue",
      "+ void legacy_print_info()",
      "class \"Point\" as TYPEDEF_POINT <<struct>> #LightYellow"
    ],
    "forbidden_content_lines": [
      "deprecated_print_info",
      "test_debug_function",
      "LEGACY_MACRO"
    ]
  }
}
```

### 5. Test Organization and Refactoring

#### 5.1 Test Categorization
**Priority: MEDIUM**

Reorganize 58 test files into clear categories with self-contained test folders:

```
tests/
├── framework/           # New unified testing framework
├── unit/               # Refactored unit tests (public API only)
│   ├── test_parsing/              # Self-contained test folder
│   │   ├── test_parsing.py        # Test implementation
│   │   ├── input/                 # All test input files
│   │   │   ├── config.json        # Test configuration
│   │   │   ├── main.c             # C/C++ source files
│   │   │   └── utils.h            # Header files
│   │   └── assertions.json        # Optional: Large assertion data
│   ├── test_transformation/       # Self-contained test folder
│   │   ├── test_transformation.py # Test implementation
│   │   ├── input/                 # All test input files
│   │   │   ├── config.json        # Test configuration
│   │   │   └── model.json         # Pre-parsed model for transformation tests
│   │   └── assertions.json        # Optional: Large assertion data
│   ├── test_generation/           # Self-contained test folder
│   │   ├── test_generation.py     # Test implementation
│   │   ├── input/                 # All test input files
│   │   │   ├── config.json        # Test configuration
│   │   │   └── model.json         # Pre-parsed model for generation tests
│   │   └── assertions.json        # Optional: Large assertion data
│   └── test_configuration/        # Self-contained test folder
│       ├── test_configuration.py  # Test implementation
│       ├── input/                 # All test input files
│       │   └── config.json        # Test configuration to validate
│       └── assertions.json        # Optional: Large assertion data
├── feature/            # Refactored feature tests
│   ├── test_full_workflow/        # Self-contained test folder
│   │   ├── test_full_workflow.py  # Test implementation
│   │   ├── input/                 # All test input files
│   │   │   ├── config.json        # Test configuration
│   │   │   ├── main.c             # C/C++ source files
│   │   │   ├── utils.h            # Header files
│   │   │   └── subdir/            # Nested directories if needed
│   │   └── assertions.json        # Optional: Large assertion data
│   ├── test_include_processing/   # Self-contained test folder
│   │   ├── test_include_processing.py # Test implementation
│   │   ├── input/                 # All test input files
│   │   │   ├── config.json        # Test configuration
│   │   │   ├── main.c             # C/C++ source files
│   │   │   └── includes/          # Include hierarchy
│   │   └── assertions.json        # Optional: Large assertion data
│   └── test_transformations/      # Self-contained test folder
│       ├── test_transformations.py # Test implementation
│       ├── input/                 # All test input files
│       │   ├── config.json        # Test configuration with transformations
│       │   ├── main.c             # C/C++ source files
│       │   └── headers/           # Header files
│       └── assertions.json        # Optional: Large assertion data
├── integration/        # Integration tests
│   ├── test_real_projects/        # Self-contained test folder
│   │   ├── test_real_projects.py  # Test implementation
│   │   ├── input/                 # All test input files
│   │   │   ├── config.json        # Test configuration
│   │   │   └── realistic_project/ # Real C/C++ project structure
│   │   │       ├── src/           # Source files
│   │   │       ├── include/       # Header files
│   │   │       └── lib/           # Library files
│   │   └── assertions.json        # Optional: Large assertion data
│   └── test_performance/          # Self-contained test folder
│       ├── test_performance.py    # Test implementation
│       ├── input/                 # All test input files
│       │   ├── config.json        # Test configuration
│       │   └── large_project/     # Large C/C++ project for performance testing
│       └── assertions.json        # Optional: Large assertion data
└── example/            # Keep existing example test (preserved as-is)
    ├── source/         # Example C/C++ source files
    ├── config.json     # Example configuration
    ├── test-example.py # Example workflow test
    └── test-example.json # Expected outputs specification
```

### 6. Boundary Separation and Component Isolation

#### 6.1 Test-Application Boundaries
**Priority: HIGH**

Ensure clean separation:
- **Tests only interact with public APIs**
- **No direct access to internal classes/functions**  
- **No mocking of internal components**
- **Tests validate behavior, not implementation**

#### 6.2 Component Boundary Testing
**Priority: MEDIUM**

Test component integration through public interfaces:
- Parser → Transformer → Generator pipeline
- Configuration loading and validation
- Error propagation and handling
- File I/O and output organization

### 7. Test Development and Verification Workflow

#### 7.1 Individual Test Development Process
**Priority: HIGH**

For each test file migration, follow this workflow:

```bash
# 1. Individual test development and verification
python -m pytest tests/unit/test_parsing/test_parsing.py -v

# 2. Verify individual test passes
# Make changes and iterate until test passes

# 3. Run full test suite to ensure no regressions
./run_all.sh

# 4. Analyze run_all.sh results
# - Check for any new failures
# - Verify performance hasn't degraded
# - Ensure all tests still pass
```

**Key Benefits:**
- **Fast iteration**: Individual test execution for rapid development
- **Regression detection**: Full suite verification catches unexpected interactions
- **Performance monitoring**: Track execution time changes
- **Integration validation**: Ensure changes don't break other tests

#### 7.2 Continuous Verification Strategy
**Priority: HIGH**

**During Development:**
```bash
# Quick feedback loop for active development
python -m pytest tests/unit/test_<name>/test_<name>.py -v --tb=short
```

**Before Committing:**
```bash
# Comprehensive verification before code commit
./run_all.sh > test_results.log 2>&1
# Review test_results.log for any issues
```

**Weekly Integration:**
```bash
# Full suite with performance analysis
time ./run_all.sh
# Compare execution times to baseline
```

### 8. Test Readability and Maintainability

#### 8.1 Standardized Test Patterns
**Priority: MEDIUM**

Common patterns for all tests:

```python
class TestFeatureName(UnifiedTestCase):
    def setUp(self):
        super().setUp()
        # Feature-specific setup
    
    def test_scenario_name(self):
        """Clear description of what this test validates"""
        # Arrange - Get paths to self-contained test data
        input_path = self.data_factory.load_test_input(self.test_name)
        config_path = self.data_factory.load_test_config(self.test_name)  # Points to input/config.json
        
        # Act - Execute through CLI interface only
        result = self.executor.run_full_pipeline(input_path, config_path, self.output_dir)
        
        # Assert - CLI execution validation
        self.assertEqual(result.exit_code, 0, f"CLI execution failed: {result.stderr}")
        self.output_validator.assert_log_no_errors(result.stdout)
        
        # Assert - Output file validation
        model_file = f"{self.output_dir}/model.json"
        main_puml_file = f"{self.output_dir}/main.puml"
        
        self.output_validator.assert_file_exists(model_file)
        self.output_validator.assert_file_exists(main_puml_file)
        
        # Assert - Model file validation (via file content)
        with open(model_file, 'r') as f:
            model_content = json.load(f)
        
        self.model_validator.assert_model_structure_valid(model_content)
        self.model_validator.assert_model_function_exists(model_content, "main")
        self.model_validator.assert_model_struct_exists(model_content, "Point")
        
        # Assert - Include validation
        expected_includes = ["stdio.h", "stdlib.h", "sample.h", "config.h"]
        self.model_validator.assert_model_includes_exist(model_content, expected_includes)
        
        # Assert - Include relationships validation
        expected_relations = [
            {"source": "sample.c", "target": "stdio.h"},
            {"source": "sample.c", "target": "sample.h"},
            {"source": "sample.h", "target": "config.h"}
        ]
        self.model_validator.assert_model_include_relationships_exist(model_content, expected_relations)
        
        # Assert - PlantUML file validation (via file content)
        with open(main_puml_file, 'r') as f:
            puml_content = f.read()
        
        self.puml_validator.assert_puml_file_syntax_valid(puml_content)
        self.puml_validator.assert_puml_formatting_compliant(puml_content)
        
        # Assert - File content validation with specific lines
        expected_puml_lines = [
            'class "main" as MAIN <<source>> #LightBlue',
            'class "utils.h" as HEADER_UTILS <<header>> #LightGreen',
            'MAIN --> HEADER_UTILS : <<include>>',
            '+ void main()',
            '+ struct Point',
            '@startuml main',
            '@enduml'
        ]
        self.output_validator.assert_file_contains_lines(main_puml_file, expected_puml_lines)
    
    def test_custom_edge_case_validation(self):
        """Example of custom validation for complex edge cases"""
        input_path = self.data_factory.load_test_input(self.test_name)
        config_path = self.data_factory.load_test_config(self.test_name)  # Points to input/config.json
        
        result = self.executor.run_full_pipeline(input_path, config_path, self.output_dir)
        self.assertEqual(result.exit_code, 0)
        
        # Standard validation using generic framework
        model_file = f"{self.output_dir}/model.json"
        with open(model_file, 'r') as f:
            model_content = json.load(f)
        
        self.model_validator.assert_model_structure_valid(model_content)
        
        # Custom validation for complex edge cases that generic framework can't handle
        self._validate_complex_anonymous_struct_hierarchy(model_content)
        self._validate_circular_include_detection(model_content)
        self._validate_macro_expansion_consistency(model_content)
        
    def _validate_complex_anonymous_struct_hierarchy(self, model: dict):
        """Custom validation for complex anonymous struct processing"""
        # Generic framework might not handle deeply nested anonymous structures
        # with multiple levels and complex naming patterns
        
        # Find the parent struct
        parent_struct = None
        for file_data in model['files'].values():
            if 'ComplexContainer' in file_data.get('structs', {}):
                parent_struct = file_data['structs']['ComplexContainer']
                break
        
        self.assertIsNotNone(parent_struct, "ComplexContainer struct not found")
        
        # Validate that anonymous structure extraction created proper hierarchy
        expected_anonymous_names = [
            'ComplexContainer_settings',
            'ComplexContainer_settings_config',
            'ComplexContainer_settings_config_data'
        ]
        
        # Check that all levels of anonymous structures were properly extracted
        for anonymous_name in expected_anonymous_names:
            found = False
            for file_data in model['files'].values():
                if anonymous_name in file_data.get('structs', {}):
                    found = True
                    break
            self.assertTrue(found, f"Anonymous struct {anonymous_name} not properly extracted")
        
        # Validate composition relationships exist in the model
        if 'anonymous_relationships' in model:
            relationships = model['anonymous_relationships']
            self.assertIn('ComplexContainer', relationships)
            self.assertIn('ComplexContainer_settings', relationships['ComplexContainer'])
    
    def _validate_circular_include_detection(self, model: dict):
        """Custom validation for circular include detection logic"""
        # Generic framework can't validate complex circular dependency logic
        
        include_graph = {}
        
        # Build include dependency graph from model
        for filename, file_data in model['files'].items():
            include_graph[filename] = file_data.get('includes', [])
        
        # Custom algorithm to detect circular includes
        def has_circular_dependency(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in include_graph.get(node, []):
                if neighbor in include_graph:  # Only check files in our project
                    if neighbor not in visited:
                        if has_circular_dependency(neighbor, visited, rec_stack):
                            return True
                    elif neighbor in rec_stack:
                        return True
            
            rec_stack.remove(node)
            return False
        
        # Validate no circular dependencies exist
        visited = set()
        for filename in include_graph:
            if filename not in visited:
                self.assertFalse(
                    has_circular_dependency(filename, visited, set()),
                    f"Circular include dependency detected involving {filename}"
                )
    
    def _validate_macro_expansion_consistency(self, model: dict):
        """Custom validation for macro expansion edge cases"""
        # Validate that conditional compilation macros are handled correctly
        
        macro_definitions = {}
        conditional_blocks = {}
        
        # Extract all macro definitions and conditional compilation info
        for filename, file_data in model['files'].items():
            macros = file_data.get('macros', [])
            for macro in macros:
                if isinstance(macro, dict) and 'name' in macro:
                    macro_definitions[macro['name']] = macro.get('value', '')
            
            # Look for conditional compilation information (if available in model)
            if 'conditional_compilation' in file_data:
                conditional_blocks[filename] = file_data['conditional_compilation']
        
        # Custom validation: ensure DEBUG macros are consistently handled
        if 'DEBUG' in macro_definitions:
            # If DEBUG is defined, ensure debug functions are included
            debug_functions = []
            for file_data in model['files'].values():
                for func in file_data.get('functions', []):
                    if isinstance(func, dict) and func.get('name', '').startswith('debug_'):
                        debug_functions.append(func['name'])
            
            if macro_definitions['DEBUG']:
                self.assertGreater(len(debug_functions), 0, 
                    "DEBUG macro defined but no debug functions found")
            else:
                # If DEBUG is explicitly undefined, debug functions should be filtered out
                self.assertEqual(len(debug_functions), 0,
                    "DEBUG macro undefined but debug functions still present")
```

#### 8.2 Documentation Standards
**Priority: LOW**

- **Clear test descriptions**: Each test explains what it validates
- **Setup documentation**: Complex test setups are well-documented
- **Expected behavior**: Tests clearly state expected outcomes
- **Failure diagnostics**: Useful error messages for test failures

### 9. Implementation Plan

#### Phase 1: Framework Foundation (Week 1-2)
1. Create `tests/framework/` structure
2. Implement `TestExecutor` with CLI interface
3. Implement basic `TestDataFactory` with data.json support
4. Implement extended `TestDataFactory` methods for source/model generation
5. Implement `ResultValidator` for models and PlantUML
6. Create `test-example.json` specification for the existing example test
7. **Verify baseline**: Run `run_all.sh` to establish current test suite baseline

#### Phase 2: Public API Migration (Week 3-4)
1. Identify tests using internal APIs (audit all 57 files, excluding preserved example)
2. Refactor high-priority unit tests to use CLI-only interface
3. Create conversion utilities for existing test patterns
4. Update example test to use new validation framework while preserving its structure
5. **Verify migration**: Run `run_all.sh` after each test file migration to ensure no regressions

#### Phase 3: Test Reorganization (Week 5-6)
1. Create self-contained test folders for each test file with `input/` subdirectory and `config.json`
2. Migrate test data into respective test folders (preserve `tests/example/` as-is)
3. Convert appropriate small tests to use data.json for source generation
4. Create multiple data_case*.json files for tests with multiple scenarios
5. Update test implementations to use `TestDataFactory.load_test_input()` and `load_test_config()`
6. Consolidate duplicate test logic and standardize naming conventions
7. Validate example test works with new framework
8. **Verify reorganization**: Run `run_all.sh` after test structure changes to ensure consistency

#### Phase 4: Validation and Cleanup (Week 7-8)
1. Ensure all tests pass with new framework
2. Performance testing of new test suite
3. Documentation updates and test coverage analysis
4. Remove deprecated test utilities
5. **Final validation**: Run `run_all.sh` for comprehensive test suite verification
6. **Performance analysis**: Compare `run_all.sh` execution times before/after migration

### 10. Success Criteria

#### Technical Criteria
- **Zero internal API usage**: All tests use only CLI interface (main.py)
- **100% test pass rate**: All migrated tests pass consistently via `run_all.sh`
- **Maintainable boundaries**: Clear separation between test and application code
- **Consistent patterns**: All tests follow unified structure and naming

#### Quality Criteria
- **Test readability**: Tests are easy to understand and modify
- **Failure diagnostics**: Test failures provide clear guidance
- **Coverage preservation**: No reduction in test coverage during migration
- **Performance**: Test suite execution time via `run_all.sh` remains reasonable

#### Validation Criteria
- **Flexible to changes**: Tests continue passing when internal implementation changes
- **Comprehensive validation**: Tests validate all aspects of public API behavior
- **Realistic scenarios**: Tests cover real-world usage patterns
- **Error handling**: Tests validate error conditions and edge cases

### 11. Risk Mitigation

#### Migration Risks
- **Breaking existing tests**: Gradual migration with parallel test execution
- **Coverage gaps**: Careful mapping of existing test coverage to new structure
- **Performance degradation**: Monitoring test execution times during migration

#### Maintenance Risks  
- **Framework complexity**: Keep framework simple and well-documented
- **Over-abstraction**: Balance reusability with test clarity
- **Dependency management**: Minimize external dependencies in test framework

---

## Test Migration Tracking

### Overview
- **Total Test Files**: 48 test files to migrate (excluding preserved example)
- **Unit Tests**: 37 files
- **Feature Tests**: 10 files  
- **Integration Tests**: 2 files
- **Preserved**: 1 file (`tests/example/test-example.py`)

### Migration Status Legend
- ✅ **Completed** - Migrated to unified framework with self-contained structure
- 🔄 **In Progress** - Currently being migrated
- ⏳ **Pending** - Not yet started
- 🚫 **Skipped** - Preserved as-is or deprecated

### Input Strategy Assessment
During migration, each test file must be assessed for its input requirements:
- **Single Input**: Can use explicit files in `input/` folder (all test methods share same input)
- **Multiple Inputs**: Must use data_##.json files (each test method can have different input)
- **Mixed Requirements**: Split into separate test files or convert to data_##.json approach

### Unit Tests (37 files)

| Test File | Status | Priority | Notes |
|-----------|--------|----------|-------|
| `test_absolute_path_bug_detection.py` | ⏳ | Medium | Path handling validation |
| `test_anonymous_processor_extended.py` | ⏳ | High | Core anonymous structure processing |
| `test_anonymous_structure_handling.py` | ⏳ | High | Anonymous structure handling |
| `test_config.py` | ⏳ | High | Configuration loading/validation |
| `test_debug_actual_parsing.py` | ⏳ | Low | Debug functionality |
| `test_debug_field_parsing.py` | ⏳ | Low | Debug functionality |
| `test_debug_field_parsing_detailed.py` | ⏳ | Low | Debug functionality |
| `test_debug_field_processing.py` | ⏳ | Low | Debug functionality |
| `test_debug_tokens.py` | ⏳ | Low | Debug functionality |
| `test_file_specific_configuration.py` | ⏳ | Medium | File-specific config handling |
| `test_function_parameters.py` | ⏳ | Medium | Function parameter parsing |
| `test_generator.py` | ⏳ | High | Core PlantUML generation |
| `test_generator_duplicate_includes.py` | ⏳ | Medium | Include duplication handling |
| `test_generator_exact_format.py` | ⏳ | Medium | PlantUML formatting validation |
| `test_generator_grouping.py` | ⏳ | Medium | Element grouping in output |
| `test_generator_include_tree_bug.py` | ⏳ | Medium | Include tree validation |
| `test_generator_naming_conventions.py` | ⏳ | Medium | Naming convention compliance |
| `test_generator_new_formatting.py` | ⏳ | Medium | New formatting features |
| `test_generator_visibility_logic.py` | ⏳ | Medium | Visibility detection logic |
| `test_global_parsing.py` | ⏳ | Medium | Global variable parsing |
| `test_include_filtering_bugs.py` | ⏳ | Medium | Include filtering edge cases |
| `test_include_processing.py` | ⏳ | Medium | Include processing logic |
| `test_multi_pass_anonymous_processing.py` | ⏳ | High | Multi-pass anonymous processing |
| `test_parser.py` | ⏳ | High | Core parser functionality |
| `test_parser_comprehensive.py` | ⏳ | High | Comprehensive parser testing |
| `test_parser_filtering.py` | ⏳ | High | Parser filtering logic |
| `test_parser_function_params.py` | ⏳ | Medium | Function parameter parsing |
| `test_parser_macro_duplicates.py` | ⏳ | Medium | Macro duplication handling |
| `test_parser_nested_structures.py` | ⏳ | Medium | Nested structure parsing |
| `test_parser_struct_order.py` | ⏳ | Medium | Struct field order preservation |
| `test_preprocessor_bug.py` | ⏳ | Medium | Preprocessor bug fixes |
| `test_preprocessor_handling.py` | ⏳ | High | Core preprocessor functionality |
| `test_tokenizer.py` | ⏳ | High | Core tokenizer functionality |
| `test_transformation_system.py` | ⏳ | High | Transformation system |
| `test_transformer.py` | ⏳ | High | Core transformer functionality |
| `test_typedef_extraction.py` | ⏳ | Medium | Typedef extraction logic |
| `test_utils.py` | ⏳ | Low | Utility function testing |
| `test_verifier.py` | ⏳ | Medium | Model verification logic |

### Feature Tests (10 files)

| Test File | Status | Priority | Notes |
|-----------|--------|----------|-------|
| `test_cli_feature.py` | ⏳ | High | CLI interface testing |
| `test_cli_modes.py` | ⏳ | High | CLI mode switching |
| `test_component_features.py` | ⏳ | High | Component integration features |
| `test_crypto_filter_pattern.py` | ⏳ | Medium | Crypto filtering patterns |
| `test_crypto_filter_usecase.py` | ⏳ | Medium | Crypto filtering use cases |
| `test_include_processing_features.py` | ⏳ | High | Include processing features |
| `test_integration.py` | ⏳ | High | Feature integration testing |
| `test_invalid_source_paths.py` | ⏳ | Medium | Error handling for invalid paths |
| `test_multiple_source_folders.py` | ⏳ | Medium | Multiple source folder handling |
| `test_transformer_features.py` | ⏳ | High | Transformer feature testing |

### Integration Tests (2 files)

| Test File | Status | Priority | Notes |
|-----------|--------|----------|-------|
| `test_comprehensive.py` | ⏳ | High | Comprehensive end-to-end testing |
| `test_new_formatting_comprehensive.py` | ⏳ | Medium | New formatting integration |

### Preserved Tests (1 file)

| Test File | Status | Priority | Notes |
|-----------|--------|----------|-------|
| `test-example.py` | 🚫 | N/A | Preserved as-is, enhanced with test-example.json |

### Supporting Files to Update

| File | Status | Priority | Notes |
|------|--------|----------|-------|
| `tests/conftest.py` | ⏳ | High | Update pytest configuration for new framework |
| `tests/utils.py` | ⏳ | High | Migrate to new framework utilities |
| `tests/feature/base.py` | ⏳ | Medium | Update base feature test class |
| `tests/__init__.py` | ⏳ | Low | Update package initialization |
| `tests/unit/__init__.py` | ⏳ | Low | Update unit test package |
| `tests/feature/__init__.py` | ⏳ | Low | Update feature test package |
| `tests/integration/__init__.py` | ⏳ | Low | Update integration test package |

### Migration Progress Summary

**Analysis Phase Complete**: ✅ Analyzed all 50 test files with detailed recommendations

- **Analysis Completed**: 50/50 (100%) - Generated comprehensive migration plan
- **Implementation Pending**: 50/50 (100%) - Ready for framework development
- **High Priority**: 24 files (including 3 requiring splits)
- **Medium Priority**: 18 files  
- **Low Priority**: 8 files
- **Data JSON Strategy**: 42 files
- **Explicit Files Strategy**: 8 files
- **Files Requiring Split**: 3 files (test_transformer.py, test_tokenizer.py, test_parser_comprehensive.py)

### Next Migration Targets (Based on Analysis Results)

**📊 Analysis Complete**: Detailed recommendations for all 50 files generated in `todo_recommendations.json`

1. **Framework Foundation** (Week 1-2):
   - Establish baseline: `./run_all.sh > baseline_results.log`
   - Implement TestDataFactory with data.json support (load_test_data_json, generate_source_files_from_data, etc.)
   - Implement TestExecutor for CLI-only interface
   - Create validation framework (ModelValidator, PlantUMLValidator, OutputValidator)
   - Create `tests/framework/` structure
   - Verify foundation: `./run_all.sh` (should match baseline)

2. **Phase 1 - Quick Wins** (Week 3-4):
   - **21 high priority files with manageable effort**
   - Start with smallest: `test_parser_function_params.py` (2 methods)
   - Progress through: `test_parser_macro_duplicates.py`, `test_parser_nested_structures.py`
   - For each test file: develop → `pytest test_file.py` → `./run_all.sh`

3. **Phase 2 - Major Refactoring** (Week 5-8):
   - **3 large files requiring splits** (80, 41, 36 methods respectively)
   - `test_transformer.py` → Split into 9 files by transformation type
   - `test_tokenizer.py` → Split into 4 files by token category  
   - `test_parser_comprehensive.py` → Split into 7 files by C language construct
   - Use data_*.json files extensively for different test scenarios

4. **Phase 3 & 4 - Medium/Low Priority** (Week 9-12):
   - Medium priority: 18 files (most using data_json strategy)
   - Low priority: 8 files (mostly explicit files strategy)
   - Final verification: `time ./run_all.sh > final_results.log`
   - Performance comparison: baseline vs final execution times

---

## Next Steps

1. **Review and approve** this plan with the development team
2. **Create `test-example.json`** specification for the existing example test
3. **Create framework foundation** in `tests/framework/`
4. **Start with pilot migration** of 5-10 representative test files (excluding the preserved example)
5. **Iterate and refine** framework based on pilot results
6. **Execute full migration** following the phase plan

This unified testing approach will ensure that c2puml remains flexible to internal changes while providing comprehensive validation of its public API functionality. The self-contained test structure with individual `input/` folders and `config.json` files provides excellent isolation and maintainability, while the preserved `tests/example/` serves as a reference implementation and comprehensive end-to-end test case.

---

## 📊 Analysis Results Summary (Generated by todo_recommendations.py)

### Executive Summary
- **50 test files analyzed** with detailed migration strategies
- **24 high priority** files requiring immediate attention
- **3 critical files** need splitting due to size (80, 41, 36 methods)
- **42 files** should use data_*.json strategy for multiple test scenarios
- **8 files** can use explicit files strategy for single scenarios

### Critical Split Requirements
1. **test_transformer.py** (80 methods) → 9 files by transformation type
2. **test_tokenizer.py** (41 methods) → 4 files by token category
3. **test_parser_comprehensive.py** (36 methods) → 7 files by C language construct

### Implementation Strategy
- **84% of files** need data_*.json approach due to multiple input requirements
- **16% of files** can use simple explicit file approach
- **All files** currently use internal APIs and need CLI-only conversion

### Key Features Implemented in Recommendations
- Automatic analysis of method complexity and input diversity
- Smart categorization by C language constructs (struct, enum, function, etc.)
- Effort estimation based on method count and complexity
- Dependency tracking for framework implementation order
- Specific data.json file suggestions for each test scenario

**Detailed recommendations available in:**
- `todo_recommendations.md` - Complete migration documentation with file-by-file analysis
- Specific strategies for all 50 test files with progress tracking
- Examples of folder structures and data.json formats provided
- Migration phases and implementation guidelines

## 🎯 Key Benefits of Self-Contained Test Structure

1. **Perfect Isolation**: Each test has its own `input/` folder and `config.json`, ensuring no cross-test interference
2. **Clear Organization**: Test data is co-located with test logic, making it easy to understand and maintain  
3. **Version Control Friendly**: Test data and logic evolve together, making changes easier to track and review
4. **Debugging Simplicity**: Each test environment is self-contained, making issue reproduction straightforward
5. **Maintainability**: Changes to one test's data cannot affect other tests, reducing maintenance overhead
6. **Framework Integration**: Tests use standardized `TestDataFactory` methods to load their data consistently