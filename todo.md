# C2PUML Test Framework Unification - Todo

## Executive Summary

This document outlines the comprehensive work required to transform the current c2puml test suite (58 test files across unit, feature, integration, and example categories) into a unified, maintainable, and robust testing framework. The primary focus is on **test-application boundary separation** and **public API testing** to ensure the application remains flexible to internal changes.

**Progress Tracking**: This document serves as the central workflow description to track migration progress. All milestones, completion status, and blocking issues should be updated directly in this file.

**📋 Detailed Recommendations**: See `todo_recommendations.md` for comprehensive file-by-file analysis and input strategy guidelines.

**🗑️ Framework Cleanup**: The existing framework files (`tests/utils.py`, `tests/feature/base.py`) use internal APIs and will be completely removed after migration.

## Current State Analysis

### Current Test Structure
- **58 test files** across 4 categories:
  - `tests/unit/` (37 files) - Individual component tests
  - `tests/feature/` (12 files) - Complete workflow tests  
  - `tests/integration/` (2 files) - End-to-end scenarios
  - `tests/example/` (1 file) - Example project test (to be preserved)
- **Mixed testing approaches**: Some tests use internal functions, others use public APIs
- **Direct internal access**: Many tests directly import and test internal components

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
- **`TestInputFactory`**: Unified factory for managing all test input data (both explicit files and input-###.json)
- **`ModelValidator`, `PlantUMLValidator`, `OutputValidator`, `FileValidator`**: Validates outputs (model.json, .puml files, logs)

```python
# Framework structure
tests/framework/
├── __init__.py
├── executor.py         # TestExecutor class
├── input_factory.py    # TestInputFactory class (unified input management)
├── validators.py       # ModelValidator, PlantUMLValidator, OutputValidator, FileValidator classes
└── fixtures.py        # Common test fixtures and helper utilities
```

#### 1.2 Test Framework Public APIs
**Priority: HIGH**

The unified test framework provides comprehensive public APIs for all testing scenarios:

##### Core Test Base Class
```python
class UnifiedTestCase(unittest.TestCase):
    """Base class for all c2puml tests - provides standard setup and utilities"""
    
    def setUp(self):
        self.executor = TestExecutor()
        self.input_factory = TestInputFactory()  # Unified input management
        self.model_validator = ModelValidator()
        self.puml_validator = PlantUMLValidator()
        self.output_validator = OutputValidator()
        self.file_validator = FileValidator()
        self.test_name = self.__class__.__name__.lower().replace('test', 'test_')
        self.temp_dirs = []  # Track temporary directories for cleanup
        
    def tearDown(self):
        """Clean up temporary directories and files"""
        for temp_dir in self.temp_dirs:
            shutil.rmtree(temp_dir, ignore_errors=True)
        shutil.rmtree(self.output_dir, ignore_errors=True)
    
    def create_temp_dir(self) -> str:
        """Create and track a temporary directory"""
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        return temp_dir
```

##### TestExecutor - CLI Execution Engine
```python
class TestExecutor:
    """Executes c2puml through CLI interface only - no internal API access"""
    
    # Core Pipeline Execution
    def run_full_pipeline(self, input_path: str, config_path: str, output_dir: str) -> CLIResult
    def run_parse_only(self, input_path: str, config_path: str, output_dir: str) -> CLIResult
    def run_transform_only(self, config_path: str, output_dir: str) -> CLIResult  
    def run_generate_only(self, config_path: str, output_dir: str) -> CLIResult
    
    # Advanced Pipeline Control
    def run_with_verbose(self, input_path: str, config_path: str, output_dir: str) -> CLIResult
    def run_with_timeout(self, input_path: str, config_path: str, output_dir: str, timeout: int) -> CLIResult
    def run_with_env_vars(self, input_path: str, config_path: str, output_dir: str, env: dict) -> CLIResult
    
    # Error Testing Support
    def run_expecting_failure(self, input_path: str, config_path: str, output_dir: str) -> CLIResult
    def run_and_capture_stderr(self, input_path: str, config_path: str, output_dir: str) -> CLIResult
    
    # Performance Testing  
    def run_with_timing(self, input_path: str, config_path: str, output_dir: str) -> TimedCLIResult
    def run_with_memory_tracking(self, input_path: str, config_path: str, output_dir: str) -> MemoryCLIResult
    
    # Output Management
    def get_test_output_dir(self, test_name: str, scenario: str = None) -> str:
        """Returns output directory path next to test file (output/ or output-<scenario>/)"""
    
    def cleanup_output_dir(self, output_dir: str) -> None:
        """Cleans output directory before test execution"""
    
    def preserve_output_for_review(self, output_dir: str) -> None:
        """Marks output directory to be preserved for manual review"""
```

##### TestInputFactory - Unified Input Management
```python
class TestInputFactory:
    """Unified factory for managing all test input data (both explicit files and input-###.json)"""
    
    def __init__(self):
        pass
    
    # === File-Based Approach (Feature/Example/Integration Tests) ===
    
    def load_test_files(self, test_name: str) -> Tuple[str, str]:
        """Load test files and return (input_path, config_path)"""
        input_path = self.get_test_data_path(test_name, "input")
        config_path = os.path.join(input_path, "config.json")
        return input_path, config_path
    
    def load_test_assertions(self, test_name: str) -> dict:
        """Load assertions.json for file-based approach (Option 1)"""
        assertions_path = self.get_test_data_path(test_name, "assertions.json")
        if os.path.exists(assertions_path):
            with open(assertions_path, 'r') as f:
                return json.load(f)
        return {}
    
    def load_scenario_assertions(self, test_name: str, input_file: str) -> dict:
        """Load assert-###.json for specific input scenario (Option 2)"""
        # Convert input-simple_struct.json -> assert-simple_struct.json
        assert_file = input_file.replace("input-", "assert-")
        assertions_path = self.get_test_data_path(test_name, assert_file)
        if os.path.exists(assertions_path):
            with open(assertions_path, 'r') as f:
                return json.load(f)
        return {}
    
    def load_test_method_assertions(self, test_name: str, method_name: str) -> dict:
        """Load assertions for specific test method from assertions.json (Option 1)"""
        all_assertions = self.load_test_assertions(test_name)
        return all_assertions.get(method_name, {})
    
    # === Input JSON Approach (Unit Tests) ===
    
    def load_input_json_scenario(self, test_name: str, input_file: str) -> Tuple[str, str]:
        """Load input-###.json and return (input_path, config_path)"""
        # Load input-###.json file
        input_file_path = self.get_test_data_path(test_name, f"input/{input_file}")
        with open(input_file_path, 'r') as f:
            input_data = json.load(f)
        
        # Validate structure
        self._validate_input_json_structure(input_data)
        
        # Create temporary files
        temp_dir = tempfile.mkdtemp()
        input_path = self._create_temp_source_files(input_data, temp_dir)
        config_path = self._create_temp_config_file(input_data, temp_dir)
        
        return input_path, config_path
    
    def list_input_json_files(self, test_name: str) -> List[str]:
        """List all input-###.json files for a test"""
        input_dir = self.get_test_data_path(test_name, "input")
        if not os.path.exists(input_dir):
            return []
        return [f for f in os.listdir(input_dir) if f.startswith("input-") and f.endswith(".json")]
    
    # === Output Directory Management ===
    
    def get_output_dir_for_scenario(self, test_name: str, scenario_name: str = None) -> str:
        """Get output directory: output/ or output-<scenario>/"""
        test_dir = self.get_test_data_path(test_name).replace("/input", "")
        if scenario_name:
            # Extract meaningful name from input file
            clean_name = scenario_name.replace("input-", "").replace(".json", "")
            return os.path.join(test_dir, f"output-{clean_name}")
        else:
            return os.path.join(test_dir, "output")
    
    def get_example_output_dir(self, test_name: str) -> str:
        """Returns artifacts/examples/<name>/ for example tests"""
        return f"artifacts/examples/{test_name.replace('test_example_', '')}"
    
    def ensure_output_dir_clean(self, output_dir: str) -> None:
        """Ensure output directory exists and is clean"""
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)
    
    # === Utility Methods ===
    
    def get_test_data_path(self, test_name: str, subpath: str = "") -> str:
        """Get path to test data directory or file"""
        base_path = f"tests/{self._get_test_category(test_name)}/{test_name}"
        return os.path.join(base_path, subpath) if subpath else base_path
    
    def _get_test_category(self, test_name: str) -> str:
        """Determine test category from test name"""
        if test_name.startswith("test_example_"):
            return "example"
        elif "feature" in test_name or "integration" in test_name or "comprehensive" in test_name:
            return "feature"
        else:
            return "unit"
    
    # === Private Helper Methods ===
    
    def _validate_input_json_structure(self, input_data: dict) -> None:
        """Validate input-###.json structure (no expected_results allowed)"""
        required_sections = ["test_metadata", "c2puml_config", "source_files"]
        forbidden_sections = ["expected_results"]
        
        missing = [s for s in required_sections if s not in input_data]
        if missing:
            raise ValueError(f"Missing required sections in input JSON: {missing}")
        
        forbidden_found = [s for s in forbidden_sections if s in input_data]
        if forbidden_found:
            raise ValueError(f"Forbidden sections in input JSON (use assertion files instead): {forbidden_found}")
    
    def _create_temp_config_file(self, input_data: dict, temp_dir: str) -> str:
        """Create temporary config.json from input data"""
        config = input_data.get("c2puml_config", {})
        config_path = os.path.join(temp_dir, "config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return config_path
    
    def _create_temp_source_files(self, input_data: dict, temp_dir: str) -> str:
        """Create temporary source files from input data"""
        source_files = input_data.get("source_files", {})
        for filename, content in source_files.items():
            file_path = os.path.join(temp_dir, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
        return temp_dir
```

**Unified Usage Pattern (with Assertion Files):**
```python
# For Feature Tests (file-based): 
input_path, config_path = self.input_factory.load_test_files(self.test_name)
assertions = self.input_factory.load_test_assertions(self.test_name)
# Returns: ("test_feature/input/", "test_feature/input/config.json", assertions_dict)

# For Unit Tests (single input-###.json scenario):
input_path, config_path = self.input_factory.load_input_json_scenario(
    self.test_name, "input-simple_struct.json"
)
assertions = self.input_factory.load_scenario_assertions(self.test_name, "input-simple_struct.json")
# Returns: (temp_dir_path, temp_config_path) + assertions from assert-simple_struct.json

# For Unit Tests (multiple input-###.json scenarios):
input_files = self.input_factory.list_input_json_files(self.test_name)
for input_file in input_files:
    with self.subTest(scenario=input_file):
        input_path, config_path = self.input_factory.load_input_json_scenario(
            self.test_name, input_file
        )
        assertions = self.input_factory.load_scenario_assertions(self.test_name, input_file)
        # Test with this scenario using data-driven assertions...
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

**Only Allowed**: CLI interface through main.py

### 3. Test Data Management and Helper Classes

#### 3.1 Common Usage Patterns and Result Types
**Priority: MEDIUM**

```python
# Result Types for CLI Execution
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
    memory_timeline: List[tuple]  # (timestamp, memory_mb)

# Test Usage Example using individual validators directly
class TestStructParsing(UnifiedTestCase):
    """Example test class using the framework components directly"""
```

#### 3.2 Test Folder Structure and Output Management
**Priority: MEDIUM**

**Test Folder Structure Pattern (with Output Management and Assertions):**
```
test_<n>/
├── test_<n>.py         # Test implementation
├── input/              # Test input files - choose ONE approach per test
│   # Option 1: File-based approach (feature tests ALWAYS use this)
│   ├── config.json     # c2puml configuration
│   ├── main.c          # Source files for testing
│   ├── utils.h         # Header files
│   ├── model.json      # Optional: Pre-parsed model for transformation testing
│   └── subdir/         # Optional: Nested directories
│   # Option 2: Input JSON approach (NO config.json or source files)
│   ├── input-simple_struct.json   # Test case 1: complete config + source (NO expected results)
│   ├── input-nested_struct.json   # Test case 2: complete config + content (NO expected results)
│   └── input-error_case.json      # Test case 3: complete config + scenarios (NO expected results)
├── assertions.json     # Used with Option 1: contains all test method assertions
├── assert-simple_struct.json      # Used with Option 2: assertions for input-simple_struct.json
├── assert-nested_struct.json      # Used with Option 2: assertions for input-nested_struct.json  
├── assert-error_case.json         # Used with Option 2: assertions for input-error_case.json
└── output/             # Generated during test execution (Git ignored except for examples)
    ├── model.json      # Generated model file
    ├── diagram.puml    # Generated PlantUML files
    └── logs/           # Execution logs and debug output
```

**Multiple Use-Case Output Structure (with Assertion Files):**
```
test_<n>/
├── test_<n>.py
├── input/
│   ├── input-simple_struct.json
│   ├── input-nested_struct.json
│   └── input-error_case.json
├── assert-simple_struct.json   # Assertions for input-simple_struct.json
├── assert-nested_struct.json   # Assertions for input-nested_struct.json
├── assert-error_case.json      # Assertions for input-error_case.json
├── output-simple_struct/       # Generated for input-simple_struct.json (Git ignored)
│   ├── model.json
│   ├── diagram.puml
│   └── c2puml.log
├── output-nested_struct/       # Generated for input-nested_struct.json (Git ignored)
│   ├── model.json
│   ├── diagram.puml
│   └── c2puml.log
└── output-error_case/          # Generated for input-error_case.json (Git ignored)
    ├── error.log
    └── stderr.txt
```

**Exception - Example Tests (Use Artifacts Folder):**
```
test_example_<name>/
├── test_example_<name>.py
├── input/
│   ├── config.json     # Example configuration
│   └── src/            # Example source code
└── # NO local output/ folder - outputs to artifacts/examples/<name>/ instead
```

**Git Ignore Configuration:**
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

**Input Strategy Guidelines:**

**FEATURE TESTS and EXAMPLE TESTS ALWAYS use Option 1 (file-based approach)** as they test complete workflows and need comprehensive project structures.

**Use input-##.json for:**
- Small unit test cases (< 50 lines of C code total)
- Multiple test scenarios in one test file
- Tests requiring different inputs per method

**Use file-based approach for:**
- Feature tests (ALWAYS)
- Example tests (ALWAYS)
- Large test cases (> 50 lines of C code)
- Complex project structures
- Real-world code examples

**Input JSON Structure (meaningful names, NO expected results):**
```json
// Example: input-simple_struct.json (input data only)
{
  "test_metadata": {
    "description": "Basic struct parsing test",
    "test_type": "unit",
    "expected_duration": "fast"
  },
  "c2puml_config": {
    "project_name": "test_struct_parsing",
    "source_folders": ["."],
    "output_dir": "./output"
  },
  "source_files": {
    "main.c": "C source code content",
    "utils.h": "Header file content"
  }
}
```

**Assertion JSON Structure (meaningful keys, data-driven validation):**
```json
// Example: assert-simple_struct.json (validation criteria only)
{
  "cli_execution": {
    "expected_exit_code": 0,
    "should_succeed": true,
    "max_execution_time_seconds": 10
  },
  "expected_files": {
    "must_exist": ["model.json", "diagram.puml"],
    "must_not_exist": ["error.log"],
    "file_count_in_output": 2
  },
  "model_validation": {
    "required_structs": [
      {
        "name": "Point",
        "fields": ["x", "y"],
        "field_types": {"x": "int", "y": "int"}
      }
    ],
    "required_functions": [
      {
        "name": "main",
        "return_type": "int",
        "parameters": []
      }
    ],
    "required_includes": ["stdio.h"],
    "total_struct_count": 1,
    "total_function_count": 1
  },
  "plantuml_validation": {
    "required_classes": [
      {
        "name": "Point",
        "stereotype": "struct",
        "visibility": "public"
      }
    ],
    "required_fields_in_puml": [
      "+ int x",
      "+ int y"
    ],
    "forbidden_content": ["ERROR", "INVALID"],
    "must_contain_text": ["@startuml", "@enduml"]
  },
  "console_output": {
    "success_indicators": ["Processing completed", "Generated model.json"],
    "forbidden_errors": ["ERROR", "FATAL", "Exception"],
    "forbidden_warnings": [],
    "log_level": "INFO"
  }
}
```

**Meaningful Input File Naming Examples:**
- `input-simple_struct.json` - Basic structure parsing
- `input-nested_struct.json` - Nested structure handling
- `input-basic_generation.json` - Simple PlantUML generation
- `input-complex_filters.json` - Complex filtering scenarios
- `input-error_handling.json` - Error condition testing
- `input-multipass_anonymous.json` - Multi-pass anonymous processing

**Corresponding Assertion File Naming Examples:**
- `assert-simple_struct.json` - Validation criteria for simple struct test
- `assert-nested_struct.json` - Validation criteria for nested struct test
- `assert-basic_generation.json` - PlantUML generation validation
- `assert-complex_filters.json` - Filter behavior validation
- `assert-error_handling.json` - Error condition validation
- `assert-multipass_anonymous.json` - Multi-pass processing validation

**Example assertions.json for Feature Tests:**
```json
{
  "test_include_parsing": {
    "cli_execution": {
      "expected_exit_code": 0,
      "should_succeed": true,
      "max_execution_time_seconds": 15
    },
    "expected_files": {
      "must_exist": ["model.json", "include_diagram.puml"],
      "must_not_exist": ["error.log"]
    },
    "model_validation": {
      "required_includes": ["stdio.h", "utils.h", "types.h"],
      "required_structs": [{"name": "Data", "fields": ["value"]}],
      "required_functions": [{"name": "main"}, {"name": "process_data"}]
    }
  },
  "test_nested_includes": {
    "cli_execution": {"expected_exit_code": 0},
    "model_validation": {
      "include_relationships": [
        {"from": "main.c", "to": "utils.h"},
        {"from": "utils.h", "to": "types.h"}
      ]
    },
    "plantuml_validation": {
      "required_relationships": [
        {"type": "include", "from": "main.c", "to": "utils.h"}
      ]
    }
  }
}
```

#### 3.3 Complete Test Framework Usage Example
**Priority: HIGH**

```python
class TestStructParsing(UnifiedTestCase):
    """Example showing comprehensive framework usage"""
    
    def test_simple_struct_file_based(self):
        """Example using file-based approach with data-driven assertions"""
        # Load test files and assertions
        input_path, config_path = self.input_factory.load_test_files(self.test_name)
        assertions = self.input_factory.load_test_assertions(self.test_name)
        
        # Get output directory next to test file
        output_dir = self.input_factory.get_output_dir_for_scenario(self.test_name)
        self.input_factory.ensure_output_dir_clean(output_dir)
        
        # Execute through CLI
        result = self.executor.run_full_pipeline(input_path, config_path, output_dir)
        
        # Data-driven CLI validation
        cli_assertions = assertions.get("cli_execution", {})
        expected_exit_code = cli_assertions.get("expected_exit_code", 0)
        self.assertEqual(result.exit_code, expected_exit_code, f"CLI failed: {result.stderr}")
        
        if cli_assertions.get("max_execution_time_seconds"):
            self.assertLess(result.execution_time, cli_assertions["max_execution_time_seconds"])
        
        # Data-driven file validation
        file_assertions = assertions.get("expected_files", {})
        for required_file in file_assertions.get("must_exist", []):
            file_path = os.path.join(output_dir, required_file)
            self.assertTrue(os.path.exists(file_path), f"Required file not found: {required_file}")
        
        for forbidden_file in file_assertions.get("must_not_exist", []):
            file_path = os.path.join(output_dir, forbidden_file)
            self.assertFalse(os.path.exists(file_path), f"Forbidden file found: {forbidden_file}")
        
        # Data-driven model validation
        model_file = os.path.join(output_dir, "model.json")
        with open(model_file, 'r') as f:
            model = json.load(f)
        
        model_assertions = assertions.get("model_validation", {})
        for struct_spec in model_assertions.get("required_structs", []):
            self.model_validator.assert_model_struct_exists(model, struct_spec["name"])
            if "fields" in struct_spec:
                self.model_validator.assert_model_struct_fields(model, struct_spec["name"], struct_spec["fields"])
        
        for func_spec in model_assertions.get("required_functions", []):
            self.model_validator.assert_model_function_exists(model, func_spec["name"])
        
        # Data-driven PlantUML validation
        puml_files = glob.glob(os.path.join(output_dir, "*.puml"))
        self.assertGreater(len(puml_files), 0, "No PlantUML files generated")
        
        with open(puml_files[0], 'r') as f:
            puml_content = f.read()
        
        puml_assertions = assertions.get("plantuml_validation", {})
        for class_spec in puml_assertions.get("required_classes", []):
            self.puml_validator.assert_puml_class_exists(puml_content, class_spec["name"], class_spec.get("stereotype"))
        
        for required_text in puml_assertions.get("required_fields_in_puml", []):
            self.puml_validator.assert_puml_contains(puml_content, required_text)
        
    def test_multiple_structs_with_input_json(self):
        """Example using input JSON approach with separate assertion file"""
        # Load input-###.json scenario and corresponding assertions
        input_path, config_path = self.input_factory.load_input_json_scenario(
            self.test_name, "input-multiple_structs.json"
        )
        assertions = self.input_factory.load_scenario_assertions(self.test_name, "input-multiple_structs.json")
        
        # Get output directory for this scenario
        output_dir = self.input_factory.get_output_dir_for_scenario(self.test_name, "input-multiple_structs.json")
        self.input_factory.ensure_output_dir_clean(output_dir)
        
        # Execute and validate
        result = self.executor.run_full_pipeline(input_path, config_path, output_dir)
        
        # Data-driven CLI validation
        cli_assertions = assertions.get("cli_execution", {})
        expected_exit_code = cli_assertions.get("expected_exit_code", 0)
        self.assertEqual(result.exit_code, expected_exit_code, f"CLI failed: {result.stderr}")
        
        # Data-driven model validation
        model_file = os.path.join(output_dir, "model.json")
        with open(model_file, 'r') as f:
            model = json.load(f)
        
        # Use assertions from assert-multiple_structs.json
        model_assertions = assertions.get("model_validation", {})
        for struct_spec in model_assertions.get("required_structs", []):
            self.model_validator.assert_model_struct_exists(model, struct_spec["name"])
        
        # Validate total counts if specified
        if "total_struct_count" in model_assertions:
            self.model_validator.assert_model_element_count(model, "structs", model_assertions["total_struct_count"])
        
    def test_error_handling_scenario(self):
        """Example testing error conditions"""
        # Create invalid source files manually
        temp_dir = self.create_temp_dir()
        
        # Create invalid C source
        invalid_c_content = "struct InvalidStruct { invalid syntax here"
        source_file = os.path.join(temp_dir, "invalid.c")
        with open(source_file, 'w') as f:
            f.write(invalid_c_content)
        
        # Create basic config
        config_data = {
            "project_name": "test_invalid",
            "source_folders": ["."],
            "output_dir": "./output"
        }
        config_file = os.path.join(temp_dir, "config.json")
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        # Execute expecting failure
        output_dir = self.input_factory.get_output_dir_for_scenario(self.test_name)
        result = self.executor.run_expecting_failure(temp_dir, config_file, output_dir)
        
        # Validate failure
        self.assertNotEqual(result.exit_code, 0, "Expected CLI to fail but it succeeded")
        self.assertIn("syntax error", result.stderr)
        
    def test_performance_monitoring(self):
        """Example with performance testing"""
        input_path, config_path = self.input_factory.load_test_files(self.test_name)
        
        # Execute with timing
        output_dir = self.input_factory.get_output_dir_for_scenario(self.test_name)
        result = self.executor.run_with_timing(input_path, config_path, output_dir)
        
        self.assertCLISuccess(result)
        self.assertLess(result.total_time, 5.0, "Execution took too long")
        self.assertLess(result.parse_time, 2.0, "Parsing took too long")
        
    def test_complex_validation_with_custom_logic(self):
        """Example showing custom validation combined with framework"""
        input_path, config_path = self.input_factory.load_test_files(self.test_name)
        
        output_dir = self.input_factory.get_output_dir_for_scenario(self.test_name)
        result = self.executor.run_full_pipeline(input_path, config_path, output_dir)
        self.assertCLISuccess(result)
        
        # Framework validations
        model_file = os.path.join(output_dir, "model.json")
        self.assertTrue(os.path.exists(model_file), "model.json not generated")
        
        with open(model_file, 'r') as f:
            model = json.load(f)
        
        # Validate PlantUML generation
        puml_files = glob.glob(os.path.join(output_dir, "*.puml"))
        self.assertGreater(len(puml_files), 0, "No PlantUML files generated")
        
        # Custom validation logic
        with open(puml_files[0], 'r') as f:
            puml_content = f.read()
        self._validate_specific_business_logic(model, puml_content)
        
        # Advanced file validations
        model_file = os.path.join(output_dir, "model.json")
        self.file_validator.assert_json_valid(model_file)
        self.file_validator.assert_file_valid_utf8(model_file)
        self.file_validator.assert_file_no_trailing_whitespace(model_file)
        
        # Test configuration behavior instead of structure validation
        # Example: Test that file filtering configuration works by creating test scenario manually
        temp_dir = self.create_temp_dir()
        
        # Create test files 
        test_files = {
            "main.c": "int main() { return 0; }",
            "utils.c": "void utils() {}",
            "test.test.c": "// This should be excluded"
        }
        
        for filename, content in test_files.items():
            with open(os.path.join(temp_dir, filename), 'w') as f:
                f.write(content)
        
        # Create config with filters
        config_with_filters = {
            "project_name": "test_filters",
            "source_folders": ["."],
            "file_filters": {"exclude": ["*.test.c"]}
        }
        
        config_file = os.path.join(temp_dir, "config.json")
        with open(config_file, 'w') as f:
            json.dump(config_with_filters, f)
        
        # Test that filtering works
        filter_output_dir = self.input_factory.get_output_dir_for_scenario(self.test_name, "filter_test")
        result = self.executor.run_full_pipeline(temp_dir, config_file, filter_output_dir)
        self.assertEqual(result.exit_code, 0)
        
        # Validate that only 2 files were processed (excluding *.test.c)
        model_file = os.path.join(filter_output_dir, "model.json")
        with open(model_file, 'r') as f:
            model = json.load(f)
        self.model_validator.assert_model_file_count(model, 2)
        
    def _validate_specific_business_logic(self, model: dict, puml_content: str):
        """Custom validation for complex scenarios"""
        # Pattern matching for specific naming conventions
        struct_names = self.model_validator.assert_model_structs_match_pattern(
            model, r"^[A-Z][a-zA-Z0-9]*$"
        )
        self.assertGreater(len(struct_names), 0, "No properly named structs found")
        
        # Complex PlantUML validation
        self.puml_validator.assert_puml_proper_stereotypes(puml_content)
        self.puml_validator.assert_puml_no_duplicate_elements(puml_content)
            
        # Business rule: All structs should have at least one field
        for struct_name in struct_names:
            # This would be a custom validation method you implement
            self._assert_struct_has_fields(model, struct_name)
    
    def test_using_subtest_for_multiple_scenarios(self):
        """Example using subTest for multiple input files"""
        input_files = self.input_factory.list_input_json_files(self.test_name)
        
        for input_file in input_files:
            with self.subTest(scenario=input_file):
                # Get scenario-specific output directory (e.g., output-simple_struct/)
                output_dir = self.input_factory.get_output_dir_for_scenario(self.test_name, input_file)
                self.input_factory.ensure_output_dir_clean(output_dir)
                
                # Load input-###.json file and create temporary files
                input_path, config_path, expected_results = self.input_factory.load_input_json_scenario(
                    self.test_name, input_file
                )
                
                result = self.executor.run_full_pipeline(input_path, config_path, output_dir)
                self.assertCLISuccess(result, f"Failed for scenario: {input_file}")
                
                        # Data-driven validation using assertion files
        
        # Use assertions specific to this input file
        model_assertions = assertions.get("model_validation", {})
        if model_assertions:
            model_file = os.path.join(output_dir, "model.json")
            with open(model_file, 'r') as f:
                model = json.load(f)
            
            for struct_spec in model_assertions.get("required_structs", []):
                self.model_validator.assert_model_struct_exists(model, struct_spec["name"])
            
            for func_spec in model_assertions.get("required_functions", []):
                self.model_validator.assert_model_function_exists(model, func_spec["name"])
```

### 4. Result Validation Framework

#### 4.1 Comprehensive Validation Framework
**Priority: HIGH**

##### ModelValidator - Model Structure and Content Validation
```python
class ModelValidator:
    """Validates c2puml generated model.json files and content"""
    
    # Core Model Structure Validation
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
    def assert_model_enum_not_exists(self, model: dict, enum_name: str) -> None
    def assert_model_typedef_exists(self, model: dict, typedef_name: str) -> None
    def assert_model_typedef_not_exists(self, model: dict, typedef_name: str) -> None
    def assert_model_global_exists(self, model: dict, global_name: str) -> None
    def assert_model_global_not_exists(self, model: dict, global_name: str) -> None
    def assert_model_macro_exists(self, model: dict, macro_name: str) -> None
    def assert_model_macro_not_exists(self, model: dict, macro_name: str) -> None
    
    # Include and Relationship Validation
    def assert_model_includes_exist(self, model: dict, expected_includes: List[str]) -> None
    def assert_model_include_exists(self, model: dict, include_name: str) -> None
    def assert_model_include_not_exists(self, model: dict, include_name: str) -> None
    def assert_model_include_relationship(self, model: dict, source: str, target: str) -> None
    def assert_model_include_relationships_exist(self, model: dict, expected_relations: List[dict]) -> None
    
    # Advanced Element Validation
    def assert_model_function_signature(self, model: dict, func_name: str, return_type: str, params: List[str]) -> None
    def assert_model_struct_fields(self, model: dict, struct_name: str, expected_fields: List[str]) -> None
    def assert_model_enum_values(self, model: dict, enum_name: str, expected_values: List[str]) -> None
    def assert_model_macro_definition(self, model: dict, macro_name: str, expected_value: str) -> None
    
    # File Content Validation
    def assert_model_file_contains_lines(self, model_file_path: str, expected_lines: List[str]) -> None
    def assert_model_file_not_contains_lines(self, model_file_path: str, forbidden_lines: List[str]) -> None
    def assert_model_json_syntax_valid(self, model_file_path: str) -> None
    def assert_model_element_count(self, model: dict, element_type: str, expected_count: int) -> None
    
    # Pattern Matching Validation
    def assert_model_functions_match_pattern(self, model: dict, pattern: str) -> List[str]
    def assert_model_structs_match_pattern(self, model: dict, pattern: str) -> List[str]
    def assert_model_includes_match_pattern(self, model: dict, pattern: str) -> List[str]
```

##### PlantUMLValidator - PlantUML File and Content Validation
```python
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
    def assert_puml_not_contains_lines(self, puml_content: str, forbidden_lines: List[str]) -> None
    def assert_puml_line_count(self, puml_content: str, expected_count: int) -> None
    
    # Element Validation
    def assert_puml_class_exists(self, puml_content: str, class_name: str, stereotype: str = None) -> None
    def assert_puml_class_not_exists(self, puml_content: str, class_name: str) -> None
    def assert_puml_class_count(self, puml_content: str, expected_count: int) -> None
    def assert_puml_method_exists(self, puml_content: str, class_name: str, method_name: str) -> None
    def assert_puml_field_exists(self, puml_content: str, class_name: str, field_name: str) -> None
    
    # Relationship Validation
    def assert_puml_relationship(self, puml_content: str, source: str, target: str, rel_type: str) -> None
    def assert_puml_relationship_count(self, puml_content: str, expected_count: int) -> None
    def assert_puml_includes_arrow(self, puml_content: str, source: str, target: str) -> None
    def assert_puml_declares_relationship(self, puml_content: str, file: str, typedef: str) -> None
    def assert_puml_no_duplicate_relationships(self, puml_content: str) -> None
    
    # Formatting and Style Validation
    def assert_puml_formatting_compliant(self, puml_content: str) -> None
    def assert_puml_proper_stereotypes(self, puml_content: str) -> None
    def assert_puml_color_scheme(self, puml_content: str, expected_colors: dict) -> None
    def assert_puml_visibility_notation(self, puml_content: str) -> None
    def assert_puml_proper_grouping(self, puml_content: str) -> None
    def assert_puml_no_syntax_errors(self, puml_content: str) -> None
    def assert_puml_no_duplicate_elements(self, puml_content: str) -> None
    
    # Advanced Validation
    def assert_puml_diagram_title(self, puml_content: str, expected_title: str) -> None
    def assert_puml_namespace_usage(self, puml_content: str, expected_namespaces: List[str]) -> None
    def assert_puml_note_exists(self, puml_content: str, note_text: str) -> None
```

##### OutputValidator - General Output and File Validation
```python
class OutputValidator:
    """Validates general output files, directories, and content"""
    
    # Directory and File System Validation
    def assert_output_dir_exists(self, output_path: str) -> None
    def assert_output_dir_structure(self, output_path: str, expected_structure: dict) -> None
    def assert_output_file_count(self, output_path: str, expected_count: int) -> None
    def assert_file_exists(self, file_path: str) -> None
    def assert_file_not_exists(self, file_path: str) -> None
    def assert_directory_empty(self, dir_path: str) -> None
    def assert_directory_not_empty(self, dir_path: str) -> None
    
    # File Content Validation
    def assert_file_contains(self, file_path: str, expected_text: str) -> None
    def assert_file_not_contains(self, file_path: str, forbidden_text: str) -> None
    def assert_file_contains_lines(self, file_path: str, expected_lines: List[str]) -> None
    def assert_file_not_contains_lines(self, file_path: str, forbidden_lines: List[str]) -> None
    def assert_file_line_count(self, file_path: str, expected_count: int) -> None
    def assert_file_empty(self, file_path: str) -> None
    def assert_file_not_empty(self, file_path: str) -> None
    def assert_file_size_under(self, file_path: str, max_size: int) -> None
    def assert_file_encoding(self, file_path: str, expected_encoding: str) -> None
    
    # Pattern Matching
    def assert_file_matches_pattern(self, file_path: str, pattern: str) -> None
    def assert_file_not_matches_pattern(self, file_path: str, pattern: str) -> None
    def assert_files_match_glob(self, dir_path: str, glob_pattern: str, expected_count: int) -> None
    
    # Log and Output Validation
    def assert_log_contains(self, log_content: str, expected_message: str) -> None
    def assert_log_contains_lines(self, log_content: str, expected_lines: List[str]) -> None
    def assert_log_no_errors(self, log_content: str) -> None
    def assert_log_no_warnings(self, log_content: str) -> None
    def assert_log_error_count(self, log_content: str, expected_count: int) -> None
    def assert_log_warning_count(self, log_content: str, expected_count: int) -> None
    def assert_log_execution_time(self, log_content: str, max_seconds: int) -> None
    def assert_log_level(self, log_content: str, expected_level: str) -> None
```

##### FileValidator - Advanced File Operations and Validation
```python
class FileValidator:
    """Advanced file validation and manipulation utilities"""
    
    # File Comparison
    def assert_files_equal(self, file1_path: str, file2_path: str) -> None
    def assert_files_not_equal(self, file1_path: str, file2_path: str) -> None
    def assert_file_matches_template(self, file_path: str, template_path: str, variables: dict) -> None
    
    # JSON File Validation
    def assert_json_valid(self, json_file_path: str) -> None
    def assert_json_schema_valid(self, json_file_path: str, schema: dict) -> None
    def assert_json_contains_key(self, json_file_path: str, key_path: str) -> None
    def assert_json_value_equals(self, json_file_path: str, key_path: str, expected_value: any) -> None
    
    # Advanced Content Validation
    def assert_file_valid_utf8(self, file_path: str) -> None
    def assert_file_no_trailing_whitespace(self, file_path: str) -> None
    def assert_file_unix_line_endings(self, file_path: str) -> None
    def assert_file_max_line_length(self, file_path: str, max_length: int) -> None
    
    # Performance Validation
    def assert_execution_time_under(self, actual_time: float, max_time: float) -> None
    def assert_memory_usage_under(self, actual_memory: int, max_memory: int) -> None
    def assert_file_creation_time_recent(self, file_path: str, max_age_seconds: int) -> None
```

##### CLI Behavior Validation


### 5. Test Organization and Refactoring

#### 5.1 Test Categorization
**Priority: MEDIUM**

Reorganize 58 test files into clear categories with self-contained test folders:

```
tests/
├── framework/           # New unified testing framework
├── unit/               # Refactored unit tests (public API only)
│   ├── test_parsing/   # Self-contained test folder
│   ├── test_transformation/
│   └── test_generation/
├── feature/            # Refactored feature tests (ALWAYS use explicit files)
│   ├── test_full_workflow/
│   ├── test_include_processing/
│   └── test_transformations/
├── integration/        # Integration tests
│   ├── test_real_projects/
│   └── test_performance/
└── example/            # Keep existing example test (preserved as-is)
```

### 6. Implementation Plan

#### Phase 1: Framework Foundation (Week 1-2)
1. Create `tests/framework/` structure
2. Implement `TestExecutor` with CLI interface
3. Implement `TestInputFactory` with unified input management (both explicit files and input-###.json)
4. Implement validation framework: `ModelValidator`, `PlantUMLValidator`, `OutputValidator`, `FileValidator`
5. **Verify baseline**: Run `run_all.sh` to establish current test suite baseline

#### Phase 2: Public API Migration (Week 3-4)
1. Refactor high-priority unit tests to use CLI-only interface
2. Convert appropriate tests to use input-##.json files
3. **Verify migration**: Run `run_all.sh` after each test file migration

#### Phase 3: Test Reorganization (Week 5-6)
1. Create self-contained test folders
2. Migrate test data into respective test folders (preserve `tests/example/`)
3. **Verify reorganization**: Run `run_all.sh` after test structure changes

#### Phase 4: Validation and Cleanup (Week 7-8)
1. Ensure all tests pass with new framework
2. Performance testing of new test suite
3. Remove deprecated test utilities
4. **Final validation**: Run `run_all.sh` for comprehensive verification

### 7. Success Criteria

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

### Key Migration Constraints

**Feature Tests and Example Tests Strategy:**
- **ALWAYS use Option 1 (explicit files)** - Feature and example tests require comprehensive project structures
- **No input-##.json files** for feature or example tests - they test complete workflows
- All feature and example test files use single `input/` folder with config.json and source files
- **Generally NO SPLITTING NEEDED** - since all test methods share the same input project, splitting is rarely necessary unless testing completely different features

**Unit Tests Strategy:**
- Use input-##.json for multiple test scenarios
- Use explicit files only when all test methods can share same input

### Critical Split Requirements
1. **test_transformer.py** (80 methods) → 9 files by transformation type
2. **test_tokenizer.py** (41 methods) → 4 files by token category
3. **test_parser_comprehensive.py** (36 methods) → 7 files by C language construct

### Migration Progress Summary

**Analysis Phase Complete**: ✅ Analyzed all 50 test files with detailed recommendations

- **High Priority**: 24 files (including 3 requiring splits)
- **Medium Priority**: 18 files  
- **Low Priority**: 8 files
- **Input JSON Strategy**: 42 files (unit tests only)
- **Explicit Files Strategy**: 8 files (includes all feature tests)

### Complete Test Migration Progress Tracking (50 files)

| Test File | Category | Status | Priority | Input Strategy | Meaningful Input Names | Notes |
|-----------|----------|--------|----------|----------------|----------------------|-------|
| **UNIT TESTS (37 files)** | | | | | | |
| `test_absolute_path_bug_detection.py` | Unit | ⏳ | Medium | input-path_*.json | input-absolute_paths.json, input-relative_paths.json, input-invalid_paths.json | Path handling validation |
| `test_anonymous_processor_extended.py` | Unit | ⏳ | High | input-anonymous_*.json | input-basic_anonymous.json, input-nested_anonymous.json, input-complex_hierarchies.json | Core anonymous structure processing |
| `test_anonymous_structure_handling.py` | Unit | ⏳ | Medium | input-anonymous_*.json | input-simple_anonymous.json, input-nested_anonymous.json, input-complex_anonymous.json | Anonymous structure handling |
| `test_config.py` | Unit | ⏳ | Medium | input-config_*.json | input-basic_config.json, input-advanced_config.json, input-invalid_config.json, input-file_specific_config.json | Configuration loading/validation |
| `test_debug_actual_parsing.py` | Unit | ⏳ | Low | Explicit files | debug_simple.c, debug_config.json | Debug functionality |
| `test_debug_field_parsing.py` | Unit | ⏳ | Low | Explicit files | debug_fields.c, debug_config.json | Debug functionality |
| `test_debug_field_parsing_detailed.py` | Unit | ⏳ | Low | Explicit files | debug_detailed.c, debug_config.json | Debug functionality |
| `test_debug_field_processing.py` | Unit | ⏳ | Low | Explicit files | debug_processing.c, debug_config.json | Debug functionality |
| `test_debug_tokens.py` | Unit | ⏳ | Low | Explicit files | debug_tokens.c, debug_config.json | Debug functionality |
| `test_file_specific_configuration.py` | Unit | ⏳ | Medium | input-fileconfig_*.json | input-single_file_config.json, input-multiple_file_config.json, input-override_config.json | File-specific config handling |
| `test_function_parameters.py` | Unit | ⏳ | Medium | input-params_*.json | input-simple_params.json, input-complex_params.json, input-variadic_params.json | Function parameter parsing |
| `test_generator.py` | Unit | ⏳ | High | input-generation_*.json | input-simple_generation.json, input-complex_diagrams.json, input-format_compliance.json, input-relationship_generation.json | Core PlantUML generation |
| `test_generator_duplicate_includes.py` | Unit | ⏳ | Low | Explicit files | duplicate_test.c, duplicate_includes.h, config.json | Include duplication handling |
| `test_generator_exact_format.py` | Unit | ⏳ | Low | input-format_*.json | input-basic_format.json, input-advanced_format.json | PlantUML formatting validation |
| `test_generator_grouping.py` | Unit | ⏳ | Medium | input-grouping_*.json | input-public_private_grouping.json, input-element_grouping.json, input-visibility_grouping.json | Element grouping in output |
| `test_generator_include_tree_bug.py` | Unit | ⏳ | Medium | input-tree_*.json | input-simple_tree.json, input-complex_tree.json, input-circular_tree.json | Include tree validation |
| `test_generator_naming_conventions.py` | Unit | ⏳ | Medium | input-naming_*.json | input-class_naming.json, input-relationship_naming.json, input-stereotype_naming.json | Naming convention compliance |
| `test_generator_new_formatting.py` | Unit | ⏳ | Medium | input-newformat_*.json | input-new_stereotypes.json, input-visibility_formatting.json, input-relationship_formatting.json | New formatting features |
| `test_generator_visibility_logic.py` | Unit | ⏳ | Medium | input-visibility_*.json | input-public_private.json, input-header_detection.json, input-visibility_edge_cases.json | Visibility detection logic |
| `test_global_parsing.py` | Unit | ⏳ | High | input-globals_*.json | input-simple_globals.json, input-complex_globals.json, input-initialized_globals.json | Global variable parsing |
| `test_include_filtering_bugs.py` | Unit | ⏳ | Medium | input-filterbug_*.json | input-filter_edge_cases.json, input-regex_patterns.json, input-performance_issues.json | Include filtering edge cases |
| `test_include_processing.py` | Unit | ⏳ | Medium | input-includes_*.json | input-basic_includes.json, input-nested_includes.json, input-depth_includes.json | Include processing logic |
| `test_multi_pass_anonymous_processing.py` | Unit | ⏳ | High | input-multipass_*.json | input-simple_multipass.json, input-complex_multipass.json, input-nested_multipass.json | Multi-pass anonymous processing |
| `test_parser.py` | Unit | ⏳ | High | input-parsing_*.json | input-basic_parsing.json, input-complex_parsing.json, input-error_handling.json | Core parser functionality |
| `test_parser_comprehensive.py` | Unit | ⏳ | High | **SPLIT REQUIRED** | Split into 7 files by C construct | Comprehensive parser testing |
| `test_parser_filtering.py` | Unit | ⏳ | High | input-filter_*.json | input-include_filters.json, input-exclude_filters.json, input-mixed_filters.json | Parser filtering logic |
| `test_parser_function_params.py` | Unit | ⏳ | Low | input-funcparams_*.json | input-simple_params.json, input-complex_params.json | Function parameter parsing |
| `test_parser_macro_duplicates.py` | Unit | ⏳ | Low | input-macrodup_*.json | input-simple_duplicates.json, input-complex_duplicates.json | Macro duplication handling |
| `test_parser_nested_structures.py` | Unit | ⏳ | Medium | input-nested_*.json | input-simple_nested.json, input-deep_nested.json, input-complex_nested.json | Nested structure parsing |
| `test_parser_struct_order.py` | Unit | ⏳ | Medium | input-structorder_*.json | input-simple_order.json, input-complex_order.json, input-mixed_order.json | Struct field order preservation |
| `test_preprocessor_bug.py` | Unit | ⏳ | High | input-prepbug_*.json | input-ifdef_testing.json, input-define_macros.json, input-include_directives.json, input-conditional_compilation.json | Preprocessor bug fixes |
| `test_preprocessor_handling.py` | Unit | ⏳ | High | input-preproc_*.json | input-conditional_compilation.json, input-macro_expansion.json | Core preprocessor functionality |
| `test_tokenizer.py` | Unit | ⏳ | High | **SPLIT REQUIRED** | Split into 4 files by token category | Core tokenizer functionality |
| `test_transformation_system.py` | Unit | ⏳ | Medium | input-transsys_*.json | input-system_config.json, input-system_validation.json, input-system_integration.json | Transformation system |
| `test_transformer.py` | Unit | ⏳ | High | **SPLIT REQUIRED** | Split into 9 files by transformation type | Core transformer functionality |
| `test_typedef_extraction.py` | Unit | ⏳ | Medium | input-typedef_*.json | input-simple_typedefs.json, input-complex_typedefs.json, input-nested_typedefs.json | Typedef extraction logic |
| `test_utils.py` | Unit | ⏳ | Low | input-utils_*.json | input-file_utils.json, input-string_utils.json, input-path_utils.json | Utility function testing |
| `test_verifier.py` | Unit | ⏳ | Medium | input-verify_*.json | input-valid_models.json, input-invalid_models.json, input-edge_case_models.json | Model verification logic |
| **FEATURE TESTS (9 files) - NO SPLITS NEEDED** | | | | | | |
| `test_cli_feature.py` | Feature | ⏳ | Low | Explicit files | feature_test.c, feature_config.json, test_project/ | CLI interface testing - single CLI project |
| `test_cli_modes.py` | Feature | ⏳ | Low | Explicit files | test_project/, config.json | CLI mode switching - single CLI project |
| `test_component_features.py` | Feature | ⏳ | High | Explicit files | main.c, headers/, config.json, project structure | Component integration - single project structure |
| `test_crypto_filter_pattern.py` | Feature | ⏳ | Medium | Explicit files | crypto patterns project/, config.json | Crypto filtering - single crypto project |
| `test_crypto_filter_usecase.py` | Feature | ⏳ | High | Explicit files | crypto project structure, config.json with filters | Crypto use cases - single crypto project |
| `test_include_processing_features.py` | Feature | ⏳ | High | Explicit files | main.c, utils.h, includes/, config.json | Include processing - single project with includes |
| `test_integration.py` | Feature | ⏳ | Medium | Explicit files | integration_project/, config.json | Integration testing - single integration project |
| `test_multiple_source_folders.py` | Feature | ⏳ | High | Explicit files | folder1/, folder2/, folder3/, config.json | Multi-folder handling - single multi-folder project |
| `test_transformer_features.py` | Feature | ⏳ | High | Explicit files | source files with transformation config.json | Transformer features - single project with transformations |
| **INTEGRATION TESTS (2 files) - NO SPLITS NEEDED** | | | | | | |
| `test_comprehensive.py` | Integration | ⏳ | High | Explicit files | realistic_project/, config.json | Comprehensive testing - single realistic project |
| `test_new_formatting_comprehensive.py` | Integration | ⏳ | Low | Explicit files | comprehensive_project/, config.json | Formatting integration - single project |
| **FEATURE TEST (SPECIAL)** | | | | | | |
| `test_invalid_source_paths.py` | Feature | ⏳ | High | Explicit files | Missing/invalid source project structures | Error handling for invalid paths |
| **EXAMPLE TESTS (1 file) - PRESERVED** | | | | | | |
| `test-example.py` | Example | 🚫 | N/A | Explicit files | source/, config.json (preserved as-is) | Preserved example test |

**Legend:**
- ⏳ **Pending** - Not yet started
- 🔄 **In Progress** - Currently being worked on  
- ✅ **Completed** - Migrated and verified
- 🚫 **Preserved** - Kept as-is
- **SPLIT REQUIRED** - File must be split before migration

**Key Insights:**
- **Feature tests use explicit files** - All test methods share the same input project, no splitting needed
- **Unit tests use input-###.json** - Multiple scenarios per test file, meaningful input names required
- **3 Critical splits required**: test_transformer.py, test_tokenizer.py, test_parser_comprehensive.py

---

## Next Steps

1. **Review and approve** this plan with the development team
2. **Create framework foundation** in `tests/framework/`
3. **Start with pilot migration** of 5-10 representative test files
4. **Execute full migration** following the phase plan

## Data-Driven Testing with Assertion Files

### Key Benefits of Assertion File Approach

1. **📋 Separation of Concerns**: Test logic is separated from validation criteria
2. **🔧 Maintainability**: Assertions can be updated without touching test code
3. **📊 Clarity**: Expected results are explicitly documented in JSON format
4. **🔄 Reusability**: Assertion patterns can be standardized across tests
5. **🎯 Self-Documenting**: Meaningful keys make tests easy to understand

### Assertion File Patterns

- **Option 1 (Feature Tests)**: `assertions.json` with test method keys
- **Option 2 (Unit Tests)**: `assert-###.json` matching `input-###.json` files

### Test Implementation Pattern

```python
# Load test data and assertions separately
input_path, config_path = self.input_factory.load_test_files(self.test_name)
assertions = self.input_factory.load_test_method_assertions(self.test_name, "test_include_parsing")

# Execute c2puml
result = self.executor.run_full_pipeline(input_path, config_path, output_dir)

# Data-driven validation using assertion criteria
cli_criteria = assertions.get("cli_execution", {})
self.assertEqual(result.exit_code, cli_criteria.get("expected_exit_code", 0))

model_criteria = assertions.get("model_validation", {})
for struct_spec in model_criteria.get("required_structs", []):
    self.model_validator.assert_model_struct_exists(model, struct_spec["name"])
```

This unified testing approach ensures that c2puml remains flexible to internal changes while providing comprehensive validation of its public API functionality. The **data-driven assertion files** make tests more maintainable and validation criteria explicit, while feature tests and unit tests use consistent patterns for their respective input strategies.