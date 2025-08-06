# C2PUML Test Framework Unification - Todo

## Executive Summary

This document outlines the comprehensive work required to transform the current c2puml test suite (58 test files across unit, feature, integration, and example categories) into a unified, maintainable, and robust testing framework. The primary focus is on **test-application boundary separation** and **public API testing** to ensure the application remains flexible to internal changes.

**Progress Tracking**: This document serves as the central workflow description to track migration progress. All milestones, completion status, and blocking issues should be updated directly in this file.

**📋 Detailed Recommendations**: See `todo_recommendations.md` for comprehensive file-by-file analysis and progress tracking for all 50 test files.

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
- **`TestDataFactory`**: Generates test C/C++ projects and configurations, handles input-##.json files
- **`ResultValidator`**: Validates outputs (model.json, .puml files, logs)
- **`TestProjectBuilder`**: Builds temporary test projects with complex structures

```python
# Framework structure
tests/framework/
├── __init__.py
├── executor.py      # TestExecutor class
├── data_factory.py  # TestDataFactory class  
├── validator.py     # ResultValidator class
├── builder.py       # TestProjectBuilder class
└── fixtures.py      # Common test fixtures
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
        self.data_factory = TestDataFactory()
        self.input_factory = InputFactory()  # For processing input-###.json files
        self.model_validator = ModelValidator()
        self.puml_validator = PlantUMLValidator()
        self.output_validator = OutputValidator()
        self.file_validator = FileValidator()
        self.config_validator = ConfigValidator()
        self.test_name = self.__class__.__name__.lower().replace('test', 'test_')
        self.output_dir = tempfile.mkdtemp()
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

##### TestDataFactory - Input Management (Explicit Files)
```python
class TestDataFactory:
    """Manages test input data for explicit files approach (feature/example tests)"""
    
    # Core Input Loading (Explicit Files)
    def load_test_input(self, test_name: str) -> str
    def load_test_config(self, test_name: str) -> str
    def load_test_assertions(self, test_name: str) -> dict
    
    # Project Building (Explicit Files)
    def create_temp_project(self, files: Dict[str, str], config: dict = None) -> str
    def create_project_from_template(self, template_name: str, variables: dict = None) -> str
    def create_nested_project(self, structure: dict) -> str
    
    # Utility Methods
    def get_test_data_path(self, test_name: str, subpath: str = "") -> str
    def copy_test_files(self, source_path: str, dest_path: str) -> None
    def merge_configs(self, base_config: dict, override_config: dict) -> dict
    def list_input_json_files(self, test_name: str) -> List[str]  # For finding available input-###.json files
    
    # Output Directory Management
    def get_output_dir_for_scenario(self, test_name: str, input_file: str = None) -> str:
        """Returns output directory path: output/ or output-<scenario_name>/"""
    
    def get_example_output_dir(self, test_name: str) -> str:
        """Returns artifacts/examples/<name>/ for example tests"""
    
    def ensure_output_dir_clean(self, output_dir: str) -> None:
        """Ensures output directory exists and is clean before test execution"""
```

##### InputFactory - Input JSON Management (Unit Tests)
```python
class InputFactory:
    """Factory for loading and processing input-###.json files (unit tests only)"""
    
    # Core Input JSON Processing
    def load_input_json(self, input_file_path: str) -> dict:
        """Load and parse input-###.json file from filesystem"""
    
    def validate_input_json_structure(self, input_data: dict) -> bool:
        """Validate that input-###.json has required sections: test_metadata, c2puml_config, source_files"""
    
    # Section Extraction
    def extract_config(self, input_data: dict) -> dict:
        """Extract c2puml_config section from input-###.json"""
    
    def extract_source_files(self, input_data: dict) -> Dict[str, str]:
        """Extract source_files section from input-###.json"""
    
    def extract_expected_results(self, input_data: dict) -> dict:
        """Extract expected_results section from input-###.json"""
    
    def extract_test_metadata(self, input_data: dict) -> dict:
        """Extract test_metadata section from input-###.json"""
    
    # Temporary File Creation
    def create_temp_config_file(self, input_data: dict, temp_dir: str) -> str:
        """Create temporary config.json from input-###.json c2puml_config section"""
    
    def create_temp_source_files(self, input_data: dict, temp_dir: str) -> str:
        """Create temporary source files from input-###.json source_files section"""
```

**Key Usage Pattern:**
```python
# For Unit Tests with input-###.json files:
input_factory = InputFactory()
input_data = input_factory.load_input_json("test_struct/input/input-simple_struct.json")
temp_dir = self.create_temp_dir()
input_path = input_factory.create_temp_source_files(input_data, temp_dir)
config_path = input_factory.create_temp_config_file(input_data, temp_dir)

# For Feature Tests with explicit files:
input_path = self.data_factory.load_test_input(self.test_name)  # Returns test_struct/input/
config_path = self.data_factory.load_test_config(self.test_name)  # Returns test_struct/input/config.json
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

# Common Test Mixins and Helpers
class TestAssertionMixin:
    """Common assertion patterns for c2puml tests"""
    
    def assertCLISuccess(self, result: CLIResult, message: str = None) -> None:
        """Assert CLI execution succeeded"""
        self.assertEqual(result.exit_code, 0, 
            f"CLI failed: {result.stderr}\nCommand: {' '.join(result.command)}\n{message or ''}")
    
    def assertCLIFailure(self, result: CLIResult, expected_error: str = None) -> None:
        """Assert CLI execution failed with optional error message check"""
        self.assertNotEqual(result.exit_code, 0, "Expected CLI to fail but it succeeded")
        if expected_error:
            self.assertIn(expected_error, result.stderr)
    
    def assertFilesGenerated(self, output_dir: str, expected_files: List[str]) -> None:
        """Assert expected files were generated"""
        for filename in expected_files:
            file_path = os.path.join(output_dir, filename)
            self.assertTrue(os.path.exists(file_path), f"Expected file not generated: {filename}")
    
    def assertValidModelGenerated(self, output_dir: str) -> dict:
        """Assert valid model.json was generated and return parsed content"""
        model_file = os.path.join(output_dir, "model.json")
        self.assertTrue(os.path.exists(model_file), "model.json not generated")
        
        with open(model_file, 'r') as f:
            model = json.load(f)
        
        self.model_validator.assert_model_structure_valid(model)
        return model
    
    def assertValidPlantUMLGenerated(self, output_dir: str) -> List[str]:
        """Assert valid PlantUML files were generated and return file contents"""
        puml_files = glob.glob(os.path.join(output_dir, "*.puml"))
        self.assertGreater(len(puml_files), 0, "No PlantUML files generated")
        
        contents = []
        for puml_file in puml_files:
            with open(puml_file, 'r') as f:
                content = f.read()
            self.puml_validator.assert_puml_file_syntax_valid(content)
            contents.append(content)
        
        return contents
    
    def loadInputJsonAndValidate(self, input_file_path: str) -> dict:
        """Load and validate input-###.json file structure"""
        input_factory = InputFactory()
        input_data = input_factory.load_input_json(input_file_path)
        self.assertTrue(
            input_factory.validate_input_json_structure(input_data),
            f"Invalid input-###.json structure in {input_file_path}"
        )
        return input_data

class InputFactory:
    """Factory for loading and processing input-###.json files"""
    
    def __init__(self):
        pass
    
    def load_input_json(self, input_file_path: str) -> dict:
        """Load and parse input-###.json file"""
        with open(input_file_path, 'r') as f:
            return json.load(f)
    
    def extract_config(self, input_data: dict) -> dict:
        """Extract c2puml_config section from input-###.json"""
        return input_data.get("c2puml_config", {})
    
    def extract_source_files(self, input_data: dict) -> Dict[str, str]:
        """Extract source_files section from input-###.json"""
        return input_data.get("source_files", {})
    
    def extract_expected_results(self, input_data: dict) -> dict:
        """Extract expected_results section from input-###.json"""
        return input_data.get("expected_results", {})
    
    def extract_test_metadata(self, input_data: dict) -> dict:
        """Extract test_metadata section from input-###.json"""
        return input_data.get("test_metadata", {})
    
    def create_temp_config_file(self, input_data: dict, temp_dir: str) -> str:
        """Create temporary config.json from input-###.json data"""
        config = self.extract_config(input_data)
        config_path = os.path.join(temp_dir, "config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return config_path
    
    def create_temp_source_files(self, input_data: dict, temp_dir: str) -> str:
        """Create temporary source files from input-###.json data"""
        source_files = self.extract_source_files(input_data)
        for filename, content in source_files.items():
            file_path = os.path.join(temp_dir, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                f.write(content)
        return temp_dir
    
    def validate_input_json_structure(self, input_data: dict) -> bool:
        """Validate that input-###.json has required structure"""
        required_sections = ["test_metadata", "c2puml_config", "source_files"]
        return all(section in input_data for section in required_sections)

class ProjectTemplates:
    """Pre-built input-###.json templates for common test scenarios"""
    
    @staticmethod
    def simple_struct_template(struct_name: str = "Point") -> dict:
        """Creates input-simple_struct.json template"""
        return {
            "test_metadata": {
                "description": f"Simple {struct_name} struct test",
                "test_type": "unit",
                "expected_duration": "fast"
            },
            "c2puml_config": {
                "project_name": f"test_{struct_name.lower()}",
                "source_folders": ["."],
                "output_dir": "./output",
                "recursive_search": True,
                "file_extensions": [".c", ".h"]
            },
            "source_files": {
                "main.c": f"""#include <stdio.h>

struct {struct_name} {{
    int x;
    int y;
}};

int main() {{
    struct {struct_name} p = {{10, 20}};
    return 0;
}}"""
            },
            "expected_results": {
                "model_elements": {
                    "structs": [struct_name],
                    "functions": ["main"]
                },
                "plantuml_elements": {
                    "classes": [struct_name]
                }
            }
        }
    
    @staticmethod
    def enum_template(enum_name: str = "Color") -> dict:
        """Creates input-enum_test.json template"""
        return {
            "test_metadata": {
                "description": f"Simple {enum_name} enum test", 
                "test_type": "unit",
                "expected_duration": "fast"
            },
            "c2puml_config": {
                "project_name": f"test_{enum_name.lower()}",
                "source_folders": ["."],
                "output_dir": "./output",
                "recursive_search": True,
                "file_extensions": [".c", ".h"]
            },
            "source_files": {
                "main.c": f"""#include <stdio.h>

enum {enum_name} {{
    RED,
    GREEN,
    BLUE
}};

int main() {{
    enum {enum_name} c = RED;
    return 0;
}}"""
            },
            "expected_results": {
                "model_elements": {
                    "enums": [enum_name],
                    "functions": ["main"]
                },
                "plantuml_elements": {
                    "enums": [enum_name]
                }
            }
        }
    
    @staticmethod
    def include_hierarchy_template() -> dict:
        """Creates input-include_hierarchy.json template"""
        return {
            "test_metadata": {
                "description": "Include hierarchy test",
                "test_type": "unit", 
                "expected_duration": "fast"
            },
            "c2puml_config": {
                "project_name": "test_includes",
                "source_folders": ["."],
                "output_dir": "./output",
                "recursive_search": True,
                "file_extensions": [".c", ".h"]
            },
            "source_files": {
                "main.c": """#include <stdio.h>
#include "utils.h"

int main() {
    return process_data();
}""",
                "utils.h": """#ifndef UTILS_H
#define UTILS_H

#include "types.h"

int process_data();

#endif""",
                "types.h": """#ifndef TYPES_H  
#define TYPES_H

typedef struct {
    int value;
} Data;

#endif"""
            },
            "expected_results": {
                "model_elements": {
                    "structs": ["Data"],
                    "functions": ["main", "process_data"],
                    "includes": ["stdio.h", "utils.h", "types.h"]
                },
                "plantuml_elements": {
                    "classes": ["Data"],
                    "relationships": [
                        {"from": "main.c", "to": "utils.h", "type": "include"},
                        {"from": "utils.h", "to": "types.h", "type": "include"}
                    ]
                }
            }
        }
```

#### 3.2 Test Folder Structure and Output Management
**Priority: MEDIUM**

**Test Folder Structure Pattern (with Output Management):**
```
test_<n>/
├── test_<n>.py         # Test implementation
├── input/              # Test input files - choose ONE approach per test
│   # Option 1: Explicit files approach (feature tests ALWAYS use this)
│   ├── config.json     # c2puml configuration
│   ├── main.c          # Source files for testing
│   ├── utils.h         # Header files
│   ├── model.json      # Optional: Pre-parsed model for transformation testing
│   └── subdir/         # Optional: Nested directories
│   # Option 2: Input.json approach (NO config.json or source files)
│   ├── input-simple_struct.json   # Test case 1: complete config + source + expected results
│   ├── input-nested_struct.json   # Test case 2: complete config + content + expected results
│   └── input-error_case.json      # Test case 3: complete config + scenarios + expected results
├── assertions.json     # Used ONLY with Option 1 (explicit files approach)
└── output/             # Generated during test execution (Git ignored except for examples)
    ├── model.json      # Generated model file
    ├── diagram.puml    # Generated PlantUML files
    └── logs/           # Execution logs and debug output
```

**Multiple Use-Case Output Structure:**
```
test_<n>/
├── test_<n>.py
├── input/
│   ├── input-simple_struct.json
│   ├── input-nested_struct.json
│   └── input-error_case.json
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

**FEATURE TESTS and EXAMPLE TESTS ALWAYS use Option 1 (explicit files)** as they test complete workflows and need comprehensive project structures.

**Use input-##.json for:**
- Small unit test cases (< 50 lines of C code total)
- Multiple test scenarios in one test file
- Tests requiring different inputs per method

**Use explicit files for:**
- Feature tests (ALWAYS)
- Example tests (ALWAYS)
- Large test cases (> 50 lines of C code)
- Complex project structures
- Real-world code examples

**Input JSON Structure (meaningful names):**
```json
// Example: input-simple_struct.json
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
  },
  "expected_results": {
    "model_elements": {
      "structs": ["Point"],
      "functions": ["main"]
    },
    "plantuml_elements": {
      "classes": ["Point"]
    }
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

#### 3.3 Complete Test Framework Usage Example
**Priority: HIGH**

```python
class TestStructParsing(UnifiedTestCase, TestAssertionMixin):
    """Example showing comprehensive framework usage"""
    
    def test_simple_struct_explicit_files(self):
        """Example using explicit files approach (feature tests)"""
        # Load test data using explicit files
        input_path = self.data_factory.load_test_input(self.test_name)
        config_path = self.data_factory.load_test_config(self.test_name)
        
        # Get output directory next to test file (e.g., test_struct/output/)
        output_dir = self.data_factory.get_output_dir_for_scenario(self.test_name)
        self.data_factory.ensure_output_dir_clean(output_dir)
        
        # Execute through CLI
        result = self.executor.run_full_pipeline(input_path, config_path, output_dir)
        
        # Use assertion mixin for common validations
        self.assertCLISuccess(result)
        model = self.assertValidModelGenerated(output_dir)
        puml_contents = self.assertValidPlantUMLGenerated(output_dir)
        
        # Specific model validations
        self.model_validator.assert_model_struct_exists(model, "Point")
        self.model_validator.assert_model_function_exists(model, "main")
        self.model_validator.assert_model_struct_fields(model, "Point", ["x", "y"])
        
        # PlantUML validations
        self.puml_validator.assert_puml_class_exists(puml_contents[0], "Point", "struct")
        self.puml_validator.assert_puml_contains(puml_contents[0], "+ int x")
        
    def test_multiple_structs_with_input_json(self):
        """Example using input JSON approach (unit tests with multiple scenarios)"""
        # Load input-###.json file using InputFactory
        input_file_path = self.data_factory.get_test_data_path(
            self.test_name, "input/input-multiple_structs.json"
        )
        
        # Use InputFactory to process the input-###.json file
        input_factory = InputFactory()
        input_data = input_factory.load_input_json(input_file_path)
        input_factory.validate_input_json_structure(input_data)
        
        # Create temporary files from input-###.json data
        temp_dir = self.create_temp_dir()
        input_path = input_factory.create_temp_source_files(input_data, temp_dir)
        config_path = input_factory.create_temp_config_file(input_data, temp_dir)
        
        # Execute and validate
        result = self.executor.run_full_pipeline(input_path, config_path, self.output_dir)
        self.assertCLISuccess(result)
        
        model = self.assertValidModelGenerated(self.output_dir)
        self.model_validator.assert_model_struct_exists(model, "Point")
        self.model_validator.assert_model_struct_exists(model, "Rectangle")
        
    def test_error_handling_scenario(self):
        """Example testing error conditions"""
        # Create invalid source using project template
        invalid_data = ProjectTemplates.simple_struct_template("InvalidStruct")
        invalid_data["source_files"]["main.c"] = "invalid C syntax here"
        
        # Use InputFactory to create temporary files
        input_factory = InputFactory()
        temp_dir = self.create_temp_dir()
        input_path = input_factory.create_temp_source_files(invalid_data, temp_dir)
        config_path = input_factory.create_temp_config_file(invalid_data, temp_dir)
        
        # Execute expecting failure
        result = self.executor.run_expecting_failure(input_path, config_path, self.output_dir)
        self.assertCLIFailure(result, "syntax error")
        
    def test_performance_monitoring(self):
        """Example with performance testing"""
        input_path = self.data_factory.load_test_input(self.test_name)
        config_path = self.data_factory.load_test_config(self.test_name)
        
        # Execute with timing
        result = self.executor.run_with_timing(input_path, config_path, self.output_dir)
        
        self.assertCLISuccess(result)
        self.assertLess(result.total_time, 5.0, "Execution took too long")
        self.assertLess(result.parse_time, 2.0, "Parsing took too long")
        
    def test_complex_validation_with_custom_logic(self):
        """Example showing custom validation combined with framework"""
        input_path = self.data_factory.load_test_input(self.test_name)
        config_path = self.data_factory.load_test_config(self.test_name)
        
        result = self.executor.run_full_pipeline(input_path, config_path, self.output_dir)
        self.assertCLISuccess(result)
        
        # Framework validations
        model = self.assertValidModelGenerated(self.output_dir)
        puml_contents = self.assertValidPlantUMLGenerated(self.output_dir)
        
        # Custom validation logic
        self._validate_specific_business_logic(model, puml_contents)
        
        # Advanced file validations
        model_file = os.path.join(self.output_dir, "model.json")
        self.file_validator.assert_json_valid(model_file)
        self.file_validator.assert_file_valid_utf8(model_file)
        self.file_validator.assert_file_no_trailing_whitespace(model_file)
        
        # Configuration validation
        config = self.data_factory.load_test_config_dict(self.test_name)
        self.config_validator.assert_config_schema_valid(config)
        self.config_validator.assert_config_project_name(config, "expected_project_name")
        
    def _validate_specific_business_logic(self, model: dict, puml_contents: List[str]):
        """Custom validation for complex scenarios"""
        # Pattern matching for specific naming conventions
        struct_names = self.model_validator.assert_model_structs_match_pattern(
            model, r"^[A-Z][a-zA-Z0-9]*$"
        )
        self.assertGreater(len(struct_names), 0, "No properly named structs found")
        
        # Complex PlantUML validation
        for puml_content in puml_contents:
            self.puml_validator.assert_puml_proper_stereotypes(puml_content)
            self.puml_validator.assert_puml_no_duplicate_elements(puml_content)
            
        # Business rule: All structs should have at least one field
        for struct_name in struct_names:
            # This would be a custom validation method you implement
            self._assert_struct_has_fields(model, struct_name)
    
    def test_using_subtest_for_multiple_scenarios(self):
        """Example using subTest for multiple input files"""
        input_files = self.data_factory.list_input_json_files(self.test_name)
        
        for input_file in input_files:
            with self.subTest(scenario=input_file):
                # Get scenario-specific output directory (e.g., output-simple_struct/)
                output_dir = self.data_factory.get_output_dir_for_scenario(self.test_name, input_file)
                self.data_factory.ensure_output_dir_clean(output_dir)
                
                input_path = self.data_factory.generate_source_files_from_input(
                    self.test_name, input_file
                )
                config_path = self.data_factory.generate_config_from_input(
                    self.test_name, input_file
                )
                
                result = self.executor.run_full_pipeline(input_path, config_path, output_dir)
                self.assertCLISuccess(result, f"Failed for scenario: {input_file}")
                
                # Scenario-specific validation based on input file data
                test_data = self.data_factory.load_test_input_json(self.test_name, input_file)
                expected_results = test_data.get("expected_results", {})
                
                if "model_elements" in expected_results:
                    model = self.assertValidModelGenerated(output_dir)
                    model_elements = expected_results["model_elements"]
                    
                    for struct_name in model_elements.get("structs", []):
                        self.model_validator.assert_model_struct_exists(model, struct_name)
                    
                    for func_name in model_elements.get("functions", []):
                        self.model_validator.assert_model_function_exists(model, func_name)
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

##### ConfigValidator - Configuration File Validation
```python
class ConfigValidator:
    """Validates c2puml configuration files and settings"""
    
    # Configuration Structure Validation
    def assert_config_file_exists(self, config_path: str) -> None
    def assert_config_json_valid(self, config_content: str) -> None
    def assert_config_schema_valid(self, config: dict) -> None
    def assert_config_required_fields(self, config: dict, required_fields: List[str]) -> None
    
    # Configuration Content Validation
    def assert_config_project_name(self, config: dict, expected_name: str) -> None
    def assert_config_source_folders(self, config: dict, expected_folders: List[str]) -> None
    def assert_config_output_dir(self, config: dict, expected_dir: str) -> None
    def assert_config_transformations(self, config: dict, expected_transformations: dict) -> None
    
    # Advanced Configuration Validation
    def assert_config_file_filters(self, config: dict, expected_filters: dict) -> None
    def assert_config_include_depth(self, config: dict, expected_depth: int) -> None
    def assert_config_file_specific_settings(self, config: dict, file_name: str, expected_settings: dict) -> None
    def assert_config_merge_result(self, base_config: dict, override_config: dict, expected_result: dict) -> None
```

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
3. Implement `TestDataFactory` with input-##.json support
4. Implement `ResultValidator` for models and PlantUML
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

### Unit Tests Progress Tracking (37 files)

| Test File | Status | Priority | Input Strategy | Notes |
|-----------|--------|----------|----------------|-------|
| `test_absolute_path_bug_detection.py` | ⏳ | Medium | input-path_*.json | Path handling validation |
| `test_anonymous_processor_extended.py` | ⏳ | High | input-anonymous_*.json | Core anonymous structure processing |
| `test_anonymous_structure_handling.py` | ⏳ | Medium | input-anonymous_*.json | Anonymous structure handling |
| `test_config.py` | ⏳ | Medium | input-config_*.json | Configuration loading/validation |
| `test_debug_actual_parsing.py` | ⏳ | Low | Explicit files | Debug functionality |
| `test_debug_field_parsing.py` | ⏳ | Low | Explicit files | Debug functionality |
| `test_debug_field_parsing_detailed.py` | ⏳ | Low | Explicit files | Debug functionality |
| `test_debug_field_processing.py` | ⏳ | Low | Explicit files | Debug functionality |
| `test_debug_tokens.py` | ⏳ | Low | Explicit files | Debug functionality |
| `test_file_specific_configuration.py` | ⏳ | Medium | input-fileconfig_*.json | File-specific config handling |
| `test_function_parameters.py` | ⏳ | Medium | input-params_*.json | Function parameter parsing |
| `test_generator.py` | ⏳ | High | input-generation_*.json | Core PlantUML generation |
| `test_generator_duplicate_includes.py` | ⏳ | Low | Explicit files | Include duplication handling |
| `test_generator_exact_format.py` | ⏳ | Low | input-format_*.json | PlantUML formatting validation |
| `test_generator_grouping.py` | ⏳ | Medium | input-grouping_*.json | Element grouping in output |
| `test_generator_include_tree_bug.py` | ⏳ | Medium | input-tree_*.json | Include tree validation |
| `test_generator_naming_conventions.py` | ⏳ | Medium | input-naming_*.json | Naming convention compliance |
| `test_generator_new_formatting.py` | ⏳ | Medium | input-newformat_*.json | New formatting features |
| `test_generator_visibility_logic.py` | ⏳ | Medium | input-visibility_*.json | Visibility detection logic |
| `test_global_parsing.py` | ⏳ | High | input-globals_*.json | Global variable parsing |
| `test_include_filtering_bugs.py` | ⏳ | Medium | input-filterbug_*.json | Include filtering edge cases |
| `test_include_processing.py` | ⏳ | Medium | input-includes_*.json | Include processing logic |
| `test_multi_pass_anonymous_processing.py` | ⏳ | High | input-multipass_*.json | Multi-pass anonymous processing |
| `test_parser.py` | ⏳ | High | input-parsing_*.json | Core parser functionality |
| `test_parser_comprehensive.py` | ⏳ | High | **SPLIT REQUIRED** | Split into 7 files by C construct |
| `test_parser_filtering.py` | ⏳ | High | input-filter_*.json | Parser filtering logic |
| `test_parser_function_params.py` | ⏳ | Low | input-funcparams_*.json | Function parameter parsing |
| `test_parser_macro_duplicates.py` | ⏳ | Low | input-macrodup_*.json | Macro duplication handling |
| `test_parser_nested_structures.py` | ⏳ | Medium | input-nested_*.json | Nested structure parsing |
| `test_parser_struct_order.py` | ⏳ | Medium | input-structorder_*.json | Struct field order preservation |
| `test_preprocessor_bug.py` | ⏳ | High | input-prepbug_*.json | Preprocessor bug fixes |
| `test_preprocessor_handling.py` | ⏳ | High | input-preproc_*.json | Core preprocessor functionality |
| `test_tokenizer.py` | ⏳ | High | **SPLIT REQUIRED** | Split into 4 files by token category |
| `test_transformation_system.py` | ⏳ | Medium | input-transsys_*.json | Transformation system |
| `test_transformer.py` | ⏳ | High | **SPLIT REQUIRED** | Split into 9 files by transformation type |
| `test_typedef_extraction.py` | ⏳ | Medium | input-typedef_*.json | Typedef extraction logic |
| `test_utils.py` | ⏳ | Low | input-utils_*.json | Utility function testing |
| `test_verifier.py` | ⏳ | Medium | input-verify_*.json | Model verification logic |

### Feature Tests Progress Tracking (10 files) - NO SPLITS NEEDED

| Test File | Status | Priority | Input Strategy | Split Needed? | Notes |
|-----------|--------|----------|----------------|---------------|-------|
| `test_cli_feature.py` | ⏳ | Low | Explicit files | ❌ NO | CLI interface testing - single CLI project |
| `test_cli_modes.py` | ⏳ | Low | Explicit files | ❌ NO | CLI mode switching - single CLI project |
| `test_component_features.py` | ⏳ | High | Explicit files | ❌ NO | Component integration - single project structure |
| `test_crypto_filter_pattern.py` | ⏳ | Medium | Explicit files | ❌ NO | Crypto filtering - single crypto project |
| `test_crypto_filter_usecase.py` | ⏳ | High | Explicit files | ❌ NO | Crypto use cases - single crypto project |
| `test_include_processing_features.py` | ⏳ | High | Explicit files | ❌ NO | Include processing - single project with includes |
| `test_integration.py` | ⏳ | Medium | Explicit files | ❌ NO | Integration testing - single integration project |
| `test_multiple_source_folders.py` | ⏳ | High | Explicit files | ❌ NO | Multi-folder handling - single multi-folder project |
| `test_transformer_features.py` | ⏳ | High | Explicit files | ❌ NO | Transformer features - single project with transformations |

**Key Insight:** Feature tests use explicit files, so all test methods share the same input project. No splitting needed unless testing completely different features requiring different projects.

### Integration Tests Progress Tracking (2 files) - NO SPLITS NEEDED

| Test File | Status | Priority | Input Strategy | Split Needed? | Notes |
|-----------|--------|----------|----------------|---------------|-------|
| `test_comprehensive.py` | ⏳ | High | Explicit files | ❌ NO | Comprehensive testing - single realistic project |
| `test_new_formatting_comprehensive.py` | ⏳ | Low | Explicit files | ❌ NO | Formatting integration - single project |

### Example Tests Progress Tracking (1 file)

| Test File | Status | Priority | Input Strategy | Notes |
|-----------|--------|----------|----------------|-------|
| `test-example.py` | 🚫 | N/A | Explicit files | Preserved as-is with existing structure |

---

## Next Steps

1. **Review and approve** this plan with the development team
2. **Create framework foundation** in `tests/framework/`
3. **Start with pilot migration** of 5-10 representative test files
4. **Execute full migration** following the phase plan

This unified testing approach ensures that c2puml remains flexible to internal changes while providing comprehensive validation of its public API functionality. Feature tests and example tests will always use explicit files to support comprehensive workflow testing, while unit tests can leverage input-##.json files for multiple test scenarios.