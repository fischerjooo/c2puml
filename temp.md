# Unified Testing Framework - First Test Conversion (Proper Implementation)

## Overview

This document describes the conversion of the first unit test (`test_parse_simple_c_file`) from the original direct internal API approach to the new unified testing framework that enforces CLI-only access to c2puml functionality.

**IMPORTANT**: This document has been updated to reflect the **proper implementation** that follows the todo.md specifications with input-###.json approach and proper folder structure.

## Test Files

- **Original Test**: `tests/unit/test_parser.py` (lines 35-75)
- **Converted Test**: `tests/unit/test_parser_simple/test_parser_simple.py` (lines 18-85) - **PROPER IMPLEMENTATION**

## Test Purpose

The test validates that c2puml can correctly parse a simple C file containing:
- Struct definitions (`struct Person`)
- Enum definitions (`enum Status`)
- Function declarations (`int main()`)
- Global variables (`int global_var`)
- Include statements (`#include <stdio.h>`)

## Proper Folder Structure (Following todo.md Specifications)

```
tests/unit/test_parser_simple/
├── test_parser_simple.py              # Test implementation
├── input/
│   └── input-simple_c_file.json       # Test input data (config + source files)
├── assert-simple_c_file.json          # Test assertions
└── output-simple_c_file/              # Generated during test execution (Git ignored)
    ├── model.json                     # Generated model file
    ├── model_transformed.json         # Generated transformed model
    ├── simple.puml                    # Generated PlantUML file
    └── c2puml.log                     # Execution logs
```

## Processing Steps and Flow

### 1. Test Setup (UnifiedTestCase.setUp())

**Location**: `tests/framework/base.py` (lines 30-50)

**What happens**:
```python
def setUp(self):
    # Initialize framework components
    self.executor = TestExecutor()
    self.input_factory = TestInputFactory()
    
    # Initialize validators
    self.model_validator = ModelValidator()
    self.puml_validator = PlantUMLValidator()
    self.output_validator = OutputValidator()
    self.file_validator = FileValidator()
    
    # Create temporary directories
    self.temp_dir = tempfile.mkdtemp()
    self.output_dir = os.path.join(self.temp_dir, "output")
    os.makedirs(self.output_dir, exist_ok=True)
    
    # Test metadata
    self.test_name = self.__class__.__name__
    self.test_method = self._testMethodName
```

**Functions called**:
- `tempfile.mkdtemp()` - Creates temporary directory
- `os.makedirs()` - Creates output directory
- Component constructors (TestExecutor, TestInputFactory, etc.)

### 2. Test Name Override

**Location**: `tests/unit/test_parser_simple/test_parser_simple.py` (lines 20-25)

**What happens**:
```python
def setUp(self):
    """Set up test environment with correct test name"""
    super().setUp()
    # Override test name to match folder structure
    self.test_name = "test_parser_simple"
```

**Why needed**: The TestInputFactory uses the test name to locate input files, so it must match the folder structure.

### 3. Input JSON File Structure

**Location**: `tests/unit/test_parser_simple/input/input-simple_c_file.json`

**What happens**:
```json
{
  "test_metadata": {
    "description": "Test parsing a simple C file with struct, enum, function, global, and include",
    "test_type": "unit",
    "scenario": "simple_c_file"
  },
  "c2puml_config": {
    "project_name": "test_parser_simple",
    "source_folders": ["."],
    "output_dir": "./output",
    "recursive_search": true
  },
  "source_files": {
    "simple.c": "#include <stdio.h>\n\nstruct Person {\n    char name[50];\n    int age;\n};\n\nenum Status {\n    OK,\n    ERROR\n};\n\nint main() {\n    return 0;\n}\n\nint global_var;"
  }
}
```

**Key Points**:
- **No expected_results**: Input JSON files must NOT contain expected results (forbidden by framework)
- **Complete config**: Contains all necessary c2puml configuration
- **Embedded source**: Source files are embedded in the JSON structure

### 4. Assertion File Structure

**Location**: `tests/unit/test_parser_simple/assert-simple_c_file.json`

**What happens**:
```json
{
  "test_metadata": {
    "description": "Assertions for simple C file parsing test",
    "test_type": "unit",
    "scenario": "simple_c_file"
  },
  "expected_results": {
    "model_validation": {
      "files": {
        "simple.c": {
          "structs": {
            "Person": {
              "fields": ["name", "age"]
            }
          },
          "enums": {
            "Status": {
              "values": ["OK", "ERROR"]
            }
          },
          "functions": ["main"],
          "globals": ["global_var"],
          "includes": ["stdio.h"]
        }
      },
      "element_counts": {
        "structs": 1,
        "enums": 1,
        "functions": 1,
        "globals": 1,
        "includes": 1
      }
    },
    "puml_validation": {
      "contains_elements": ["Person", "Status", "main"],
      "syntax_valid": true
    },
    "execution": {
      "exit_code": 0,
      "output_files": ["model.json", "model_transformed.json", "simple.puml"]
    }
  }
}
```

**Key Points**:
- **Separate from input**: Assertions are in a separate file
- **Comprehensive validation**: Covers model content, element counts, and PlantUML output
- **Execution validation**: Validates exit codes and output files

### 5. Test Execution Using Input-###.json Approach

**Location**: `tests/unit/test_parser_simple/test_parser_simple.py` (lines 35-45)

**What happens**:
```python
# Load test scenario using input-###.json approach
input_path, config_path = self.input_factory.load_input_json_scenario(
    self.test_name, "input-simple_c_file.json"
)

# Load assertions for this scenario
assertions = self.input_factory.load_scenario_assertions(
    self.test_name, "input-simple_c_file.json"
)
```

**Functions called**:

#### 5.1 `self.input_factory.load_input_json_scenario()`

**Location**: `tests/framework/input_factory.py` (lines 86-120)

**What happens**:
```python
def load_input_json_scenario(self, test_name: str, input_file: str) -> Tuple[str, str]:
    # Load input-###.json file
    input_file_path = self.get_test_data_path(test_name, f"input/{input_file}")
    if not os.path.exists(input_file_path):
        raise FileNotFoundError(f"Input file not found: {input_file_path}")
        
    with open(input_file_path, 'r') as f:
        input_data = json.load(f)
    
    # Validate structure
    self._validate_input_json_structure(input_data)
    
    # Create temporary files
    temp_dir = tempfile.mkdtemp()
    input_path = self._create_temp_source_files(input_data, temp_dir)
    config_path = self._create_temp_config_file(input_data, temp_dir)
    
    return input_path, config_path
```

**Functions called**:
- `self.get_test_data_path()` - Gets path to test data directory
- `json.load()` - Loads input JSON file
- `self._validate_input_json_structure()` - Validates JSON structure
- `tempfile.mkdtemp()` - Creates temporary directory
- `self._create_temp_source_files()` - Creates source files in temp directory
- `self._create_temp_config_file()` - Creates config.json in temp directory

#### 5.2 `self.input_factory.load_scenario_assertions()`

**Location**: `tests/framework/input_factory.py` (lines 121-140)

**What happens**:
```python
def load_scenario_assertions(self, test_name: str, input_file: str) -> dict:
    # Convert input-simple_struct.json -> assert-simple_struct.json
    assert_file = input_file.replace("input-", "assert-")
    assertions_path = self.get_test_data_path(test_name, assert_file)
    if os.path.exists(assertions_path):
        with open(assertions_path, 'r') as f:
            return json.load(f)
    return {}
```

**Functions called**:
- `input_file.replace()` - Converts input filename to assertion filename
- `self.get_test_data_path()` - Gets path to assertion file
- `json.load()` - Loads assertion JSON file

### 6. c2puml Execution

**Location**: `tests/unit/test_parser_simple/test_parser_simple.py` (line 47)

**What happens**:
```python
# Execute c2puml through CLI using framework
result = self.run_c2puml_full_pipeline(config_path, input_path)
```

**Functions called**:

#### 6.1 `self.run_c2puml_full_pipeline(config_path, input_path)`

**Location**: `tests/framework/base.py` (lines 62-70)

**What happens**:
```python
def run_c2puml_full_pipeline(self, config_path: str, working_dir: str = None) -> CLIResult:
    if working_dir is None:
        working_dir = os.path.dirname(config_path) if os.path.isfile(config_path) else config_path
    
    command = self._build_command(["--config", config_path])
    return self._execute_command(command, working_dir)
```

**Functions called**:
- `self._build_command()` - Builds CLI command
- `self._execute_command()` - Executes the command

#### 6.2 `self._build_command(["--config", config_path])`

**Location**: `tests/framework/executor.py` (lines 200-215)

**What happens**:
```python
def _build_command(self, args: List[str]) -> List[str]:
    # Try different ways to run c2puml
    commands_to_try = [
        self.main_script_command + args,  # Try python main.py first (most reliable)
        [self.c2puml_command] + args,  # Try installed c2puml command
        self.python_module_command + args,  # Try python -m c2puml.main
    ]
    
    # Return the first command that should work
    return commands_to_try[0]
```

**Result**: `["python3", "/workspace/main.py", "--config", "/tmp/tmpXXXXXX/config.json"]`

#### 6.3 `self._execute_command(command, working_dir)`

**Location**: `tests/framework/executor.py` (lines 217-280)

**What happens**:
```python
def _execute_command(self, command: List[str], working_dir: str, 
                    timeout: Optional[int] = None, env: Optional[Dict[str, str]] = None) -> CLIResult:
    start_time = time.time()
    
    # Try different command variations if the first one fails
    commands_to_try = [
        command,
        self.main_script_command + command[1:] if command[0] == self.c2puml_command else command,
        self.python_module_command + command[1:] if command[0] == self.c2puml_command else command,
    ]
    
    for cmd in commands_to_try:
        try:
            # Prepare environment
            process_env = os.environ.copy()
            if env:
                process_env.update(env)
            
            # Execute command
            result = subprocess.run(
                cmd,
                cwd=working_dir,
                env=process_env,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            return CLIResult(
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=execution_time,
                command=cmd,
                working_dir=working_dir
            )
        except Exception as e:
            continue
```

**Functions called**:
- `time.time()` - Start timing
- `os.environ.copy()` - Copy environment variables
- `subprocess.run()` - Execute c2puml CLI command
- `time.time()` - End timing
- `CLIResult()` - Create result object

### 7. c2puml CLI Execution

**Location**: `src/c2puml/main.py` (lines 50-225)

**What happens**:
```python
# Command executed: python3 /workspace/main.py --config /tmp/tmpXXXXXX/config.json

def main() -> int:
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-c", type=str, default=None)
    parser.add_argument("command", nargs="?", choices=["parse", "transform", "generate"])
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    
    # Load configuration
    config_path = args.config or os.getcwd()
    config_data = load_config_from_path(config_path)
    config = Config(**config_data)
    
    # Determine output folder
    output_folder = getattr(config, "output_dir", None) or os.path.join(os.getcwd(), "output")
    output_folder = os.path.abspath(output_folder)
    os.makedirs(output_folder, exist_ok=True)
    
    # Full workflow execution
    # Step 1: Parse
    parser_obj = Parser()
    parser_obj.parse(
        source_folders=config.source_folders,
        output_file=model_file,
        recursive_search=getattr(config, "recursive_search", True),
        config=config,
    )
    
    # Step 2: Transform
    transformer = Transformer()
    transformer.transform(
        model_file=model_file,
        config_file=config_path,
        output_file=transformed_model_file,
    )
    
    # Step 3: Generate
    generator = Generator()
    generator.generate(
        model_file=transformed_model_file,
        output_dir=output_folder,
    )
```

**Functions called**:
- `argparse.ArgumentParser()` - Parse CLI arguments
- `load_config_from_path()` - Load JSON configuration
- `Config()` - Create configuration object
- `Parser().parse()` - Parse C source files
- `Transformer().transform()` - Transform parsed model
- `Generator().generate()` - Generate PlantUML files

### 8. Result Validation (Proper Implementation)

**Location**: `tests/unit/test_parser_simple/test_parser_simple.py` (lines 49-85)

**What happens**:

#### 8.1 Execution Success Validation
```python
# Validate execution success
self.assert_c2puml_success(result)
```

**Functions called**:
- `self.assert_c2puml_success(result)` - Validates exit code is 0

#### 8.2 Output Directory Determination
```python
# The output is created in the working directory (src) + output
actual_output_dir = os.path.join(result.working_dir, "output")
```

**Why needed**: The TestInputFactory creates source files in a `src` subdirectory, and c2puml creates output in `./output` relative to the working directory (which is the `src` directory).

#### 8.3 Output File Validation
```python
# Validate output files were created
self.assert_model_file_exists(actual_output_dir)
self.assert_transformed_model_file_exists(actual_output_dir)
self.assert_puml_files_exist(actual_output_dir)
```

**Functions called**:
- `self.assert_model_file_exists()` - Validates model.json exists
- `self.assert_transformed_model_file_exists()` - Validates model_transformed.json exists
- `self.assert_puml_files_exist()` - Validates .puml files exist

#### 8.4 Model Content Validation (Direct Validator Usage)
```python
# Load model data for assertion processing
model_file = os.path.join(actual_output_dir, "model.json")
with open(model_file, 'r') as f:
    model_data = json.load(f)

# Load PlantUML content for assertion processing
puml_files = self.assert_puml_files_exist(actual_output_dir)
with open(puml_files[0], 'r') as f:
    puml_content = f.read()

# Process assertions from the JSON file
self.process_assertions(assertions, model_data, puml_content, result)
```

**Functions called**:
- `open()` - Open model.json file
- `json.load()` - Parse JSON content
- `self.assert_puml_files_exist()` - Get PlantUML files
- `open()` - Open .puml file
- `f.read()` - Read PlantUML content
- `self.process_assertions()` - Process assertions from JSON file

#### 8.5 Assertion Processing (NEW - Using JSON Assertions)

**Location**: `tests/framework/base.py` (lines 470-540)

**What happens**:
```python
def process_assertions(self, assertions: dict, model_data: dict = None, puml_content: str = None, result: CLIResult = None) -> None:
    if not assertions or "expected_results" not in assertions:
        return
    
    expected = assertions["expected_results"]
    
    # Process execution assertions
    if "execution" in expected and result:
        execution_expected = expected["execution"]
        if "exit_code" in execution_expected:
            self.assertEqual(result.exit_code, execution_expected["exit_code"])
    
    # Process model validation assertions
    if "model_validation" in expected and model_data:
        model_expected = expected["model_validation"]
        
        # Process file-specific assertions
        if "files" in model_expected:
            for filename, file_expected in model_expected["files"].items():
                if filename in model_data.get("files", {}):
                    file_data = model_data["files"][filename]
                    
                    # Validate structs
                    if "structs" in file_expected:
                        for struct_name, struct_expected in file_expected["structs"].items():
                            self.model_validator.assert_model_struct_exists(model_data, struct_name)
                            if "fields" in struct_expected:
                                self.model_validator.assert_model_struct_fields(model_data, struct_name, struct_expected["fields"])
                    
                    # Validate enums
                    if "enums" in file_expected:
                        for enum_name, enum_expected in file_expected["enums"].items():
                            self.model_validator.assert_model_enum_exists(model_data, enum_name)
                            if "values" in enum_expected:
                                self.model_validator.assert_model_enum_values(model_data, enum_name, enum_expected["values"])
                    
                    # Validate functions
                    if "functions" in file_expected:
                        for func_name in file_expected["functions"]:
                            self.model_validator.assert_model_function_exists(model_data, func_name)
                    
                    # Validate globals
                    if "globals" in file_expected:
                        for global_name in file_expected["globals"]:
                            self.model_validator.assert_model_global_exists(model_data, global_name)
                    
                    # Validate includes
                    if "includes" in file_expected:
                        for include_name in file_expected["includes"]:
                            self.model_validator.assert_model_include_exists(model_data, include_name)
        
        # Process element count assertions
        if "element_counts" in model_expected:
            for element_type, expected_count in model_expected["element_counts"].items():
                self.model_validator.assert_model_element_count(model_data, element_type, expected_count)
    
    # Process PlantUML validation assertions
    if "puml_validation" in expected and puml_content:
        puml_expected = expected["puml_validation"]
        
        # Validate required elements
        if "contains_elements" in puml_expected:
            for element_name in puml_expected["contains_elements"]:
                self.puml_validator.assert_puml_contains(puml_content, element_name)
        
        # Validate syntax
        if puml_expected.get("syntax_valid", False):
            self.puml_validator.assert_puml_start_end_tags(puml_content)
```

**Functions called**:
- `self.assertEqual()` - Validate exit code
- `self.model_validator.assert_model_struct_exists()` - Validate struct exists
- `self.model_validator.assert_model_struct_fields()` - Validate struct fields
- `self.model_validator.assert_model_enum_exists()` - Validate enum exists
- `self.model_validator.assert_model_enum_values()` - Validate enum values
- `self.model_validator.assert_model_function_exists()` - Validate function exists
- `self.model_validator.assert_model_global_exists()` - Validate global variable exists
- `self.model_validator.assert_model_include_exists()` - Validate include exists
- `self.model_validator.assert_model_element_count()` - Validate element counts
- `self.puml_validator.assert_puml_contains()` - Validate PlantUML content
- `self.puml_validator.assert_puml_start_end_tags()` - Validate PlantUML syntax

## Key Differences from Original Test

### Original Approach (Direct Internal API)
```python
# Direct internal API access
from c2puml.parser import CParser
parser = CParser()
file_model = parser.parse_file(Path(temp_file), Path(temp_file).name)

# Direct object access
self.assertIn("Person", file_model.structs)
self.assertIn("Status", file_model.enums)
```

### Unified Framework Approach (CLI-Only) - PROPER IMPLEMENTATION
```python
# CLI-only execution with input-###.json approach
input_path, config_path = self.input_factory.load_input_json_scenario(
    self.test_name, "input-simple_c_file.json"
)
result = self.run_c2puml_full_pipeline(config_path, input_path)
self.assert_c2puml_success(result)

# Direct validator usage with correct output directory
actual_output_dir = os.path.join(result.working_dir, "output")
model_file = os.path.join(actual_output_dir, "model.json")
with open(model_file, 'r') as f:
    model_data = json.load(f)

self.model_validator.assert_model_struct_exists(model_data, "Person")
self.model_validator.assert_model_struct_fields(model_data, "Person", ["name", "age"])
self.model_validator.assert_model_enum_exists(model_data, "Status")
self.model_validator.assert_model_enum_values(model_data, "Status", ["OK", "ERROR"])
```

## Benefits of the Proper Implementation

1. **Enforces CLI-Only Access** - Tests cannot accidentally use internal APIs
2. **Real-World Testing** - Tests the actual CLI interface that users will use
3. **Comprehensive Validation** - Tests the complete pipeline (parse → transform → generate)
4. **Output Validation** - Validates actual output files (model.json, .puml files)
5. **Framework Consistency** - All tests use the same patterns and helpers
6. **Better Debugging** - Output files are preserved for manual inspection
7. **Proper Structure** - Follows todo.md specifications exactly
8. **Input-###.json Approach** - Uses the recommended approach for unit tests
9. **Separate Assertions** - Assertions are in separate files as specified
10. **Maintainable** - Changes to model structure only require framework updates
11. **Data-Driven Testing** - Assertions are processed from JSON files, not hardcoded
12. **Flexible Validation** - Easy to modify test expectations by changing JSON files

## Code Comparison

### Before Proper Implementation (Manual JSON Parsing)
```python
# Load and validate the model.json content
with open(model_file, 'r') as f:
    model_data = json.load(f)

# Verify the model structure
self.assertIn("files", model_data)
self.assertGreater(len(model_data["files"]), 0)

# Find our simple.c file in the model
simple_c_file = model_data["files"].get("simple.c")
self.assertIsNotNone(simple_c_file, "simple.c should be in the model")

# Validate struct parsing
structs = simple_c_file.get("structs", {})
self.assertGreater(len(structs), 0, "Should find at least one struct")

# Find Person struct
person_struct = structs.get("Person")
self.assertIsNotNone(person_struct, "Person struct should be found")

# Validate Person struct fields
fields = person_struct.get("fields", [])
self.assertEqual(len(fields), 2, "Person struct should have 2 fields")

field_names = [field.get("name") for field in fields]
self.assertIn("name", field_names)
self.assertIn("age", field_names)

# ... 50+ more lines of manual validation
```

### After Proper Implementation (Direct Validator Usage)
```python
# Direct validator usage with correct output directory
actual_output_dir = os.path.join(result.working_dir, "output")
model_file = os.path.join(actual_output_dir, "model.json")
with open(model_file, 'r') as f:
    model_data = json.load(f)

# Load PlantUML content for assertion processing
puml_files = self.assert_puml_files_exist(actual_output_dir)
with open(puml_files[0], 'r') as f:
    puml_content = f.read()

# Process assertions from the JSON file
self.process_assertions(assertions, model_data, puml_content, result)
```

**Key Improvement**: The test now processes assertions from the JSON file instead of hardcoding them, making it truly data-driven and maintainable.

## Framework Helper Methods Used

The proper implementation uses these framework components:

### TestInputFactory Methods
- `load_input_json_scenario()` - Loads input-###.json and creates temp files
- `load_scenario_assertions()` - Loads assert-###.json for validation

### TestExecutor Methods
- `run_full_pipeline()` - Executes complete c2puml workflow

### Validator Methods (Direct Usage)
- `ModelValidator.assert_model_struct_exists()` - Validates struct exists
- `ModelValidator.assert_model_struct_fields()` - Validates struct fields
- `ModelValidator.assert_model_enum_exists()` - Validates enum exists
- `ModelValidator.assert_model_enum_values()` - Validates enum values
- `ModelValidator.assert_model_function_exists()` - Validates function exists
- `ModelValidator.assert_model_global_exists()` - Validates global variable exists
- `ModelValidator.assert_model_include_exists()` - Validates include exists
- `ModelValidator.assert_model_element_count()` - Validates element counts
- `PlantUMLValidator.assert_puml_contains()` - Validates PlantUML content
- `PlantUMLValidator.assert_puml_start_end_tags()` - Validates PlantUML syntax

### Updated Validators
The `ModelValidator` class was updated to work with the actual model structure:
- Structs and enums are dictionaries, not arrays
- Proper field and value validation
- Element counting across all files

## File Structure Created

```
/tmp/tmpXXXXXX/                          # Temporary directory created by TestInputFactory
├── config.json                          # Temporary config.json
└── src/                                 # Source files directory
    ├── simple.c                         # Test source file
    └── output/                          # c2puml output directory
        ├── model.json                   # Parsed model
        ├── model_transformed.json       # Transformed model
        └── simple.puml                  # Generated PlantUML file
```

## Model.json Structure

```json
{
  "files": {
    "simple.c": {
      "aliases": {},
      "anonymous_relationships": {},
      "enums": {
        "Status": {
          "name": "Status",
          "tag_name": "",
          "values": [
            {"name": "OK", "value": null},
            {"name": "ERROR", "value": null}
          ]
        }
      },
      "file_path": "/tmp/tmpXXXXXX/src/simple.c",
      "functions": [
        {
          "is_declaration": false,
          "is_static": false,
          "name": "main",
          "parameters": [],
          "return_type": "int"
        }
      ],
      "globals": [
        {
          "name": "global_var",
          "type": "int",
          "value": null
        }
      ],
      "include_relations": [],
      "includes": ["stdio.h"],
      "macros": [],
      "name": "simple.c",
      "structs": {
        "Person": {
          "fields": [
            {"name": "name", "type": "char[50]", "value": null},
            {"name": "age", "type": "int", "value": null}
          ],
          "methods": [],
          "name": "Person",
          "tag_name": "",
          "uses": []
        }
      },
      "unions": {}
    }
  },
  "project_name": "test_parser_simple",
  "source_folder": "."
}
```

## Conclusion

The proper implementation demonstrates the true power of the unified testing framework:

1. **Follows Specifications**: Exactly follows the todo.md and todo_recommendations.md specifications
2. **Input-###.json Approach**: Uses the recommended approach for unit tests
3. **Proper Structure**: Creates the correct folder structure with input/ and assertion files
4. **Direct Validator Usage**: Uses validators directly for maximum flexibility
5. **Correct Output Handling**: Properly handles the output directory structure
6. **Comprehensive**: Tests the complete pipeline and validates all outputs
7. **Maintainable**: Changes to model structure only require framework updates
8. **Data-Driven**: Assertions are processed from JSON files, making tests truly data-driven
9. **Flexible**: Easy to modify test expectations by changing JSON files without touching code

This proper implementation serves as the ideal template for converting all remaining tests to use the unified framework effectively according to the specifications.