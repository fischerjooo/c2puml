# Unified Testing Framework - First Test Conversion

## Overview

This document describes the conversion of the first unit test (`test_parse_simple_c_file`) from the original direct internal API approach to the new unified testing framework that enforces CLI-only access to c2puml functionality.

## Test Files

- **Original Test**: `tests/unit/test_parser.py` (lines 35-75)
- **Converted Test**: `tests/unit/test_parser_unified.py` (lines 18-150)

## Test Purpose

The test validates that c2puml can correctly parse a simple C file containing:
- Struct definitions (`struct Person`)
- Enum definitions (`enum Status`)
- Function declarations (`int main()`)
- Global variables (`int global_var`)
- Include statements (`#include <stdio.h>`)

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

### 2. Test Data Creation

**Location**: `tests/unit/test_parser_unified.py` (lines 25-45)

**What happens**:
```python
# Create test source files using the framework
source_files = {
    "simple.c": """
#include <stdio.h>

struct Person {
    char name[50];
    int age;
};

enum Status {
    OK,
    ERROR
};

int main() {
    return 0;
}

int global_var;
    """
}

# Create test configuration
config_data = {
    "project_name": "test_parser_simple",
    "source_folders": ["."],
    "output_dir": self.output_dir,
    "recursive_search": True
}
```

**Functions called**: None (just data preparation)

### 3. File Creation Using Framework Helpers

**Location**: `tests/unit/test_parser_unified.py` (lines 47-49)

**What happens**:
```python
# Create test files using framework helpers
source_dir = self.create_test_source_files(source_files)
config_path = self.create_test_config(config_data)
```

**Functions called**:

#### 3.1 `self.create_test_source_files(source_files)`

**Location**: `tests/framework/base.py` (lines 95-115)

**What happens**:
```python
def create_test_source_files(self, source_files: Dict[str, str], temp_dir: str = None) -> str:
    if temp_dir is None:
        temp_dir = self.temp_dir
    
    input_data = {
        "test_metadata": {
            "description": f"Test {self.test_name}.{self.test_method}",
            "test_type": "unit"
        },
        "c2puml_config": {
            "project_name": f"{self.test_name}_{self.test_method}",
            "source_folders": ["."],
            "output_dir": self.output_dir
        },
        "source_files": source_files
    }
    
    return self.input_factory._create_temp_source_files(input_data, temp_dir)
```

**Functions called**:
- `self.input_factory._create_temp_source_files()` - Creates source files in temp directory

#### 3.2 `self.create_test_config(config_data)`

**Location**: `tests/framework/base.py` (lines 75-95)

**What happens**:
```python
def create_test_config(self, config_data: Dict[str, Any], temp_dir: str = None) -> str:
    if temp_dir is None:
        temp_dir = self.temp_dir
    
    # Create a copy to avoid modifying the original
    config = config_data.copy()
    
    # Ensure required fields are present (only if not already provided)
    if "source_folders" not in config:
        config["source_folders"] = ["."]
    if "output_dir" not in config:
        config["output_dir"] = self.output_dir
    if "project_name" not in config:
        config["project_name"] = f"{self.test_name}_{self.test_method}"
    if "recursive_search" not in config:
        config["recursive_search"] = True
    
    # Create the config file directly
    config_path = os.path.join(temp_dir, "config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    return config_path
```

**Functions called**:
- `config_data.copy()` - Creates copy of config data
- `os.path.join()` - Creates config file path
- `json.dump()` - Writes config to JSON file

### 4. c2puml Execution

**Location**: `tests/unit/test_parser_unified.py` (line 51)

**What happens**:
```python
# Execute c2puml through CLI using framework
result = self.run_c2puml_full_pipeline(config_path, source_dir)
```

**Functions called**:

#### 4.1 `self.run_c2puml_full_pipeline(config_path, source_dir)`

**Location**: `tests/framework/base.py` (lines 55-65)

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

#### 4.2 `self._build_command(["--config", config_path])`

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

#### 4.3 `self._execute_command(command, working_dir)`

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

### 5. c2puml CLI Execution

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

### 6. Result Validation

**Location**: `tests/unit/test_parser_unified.py` (lines 53-150)

**What happens**:

#### 6.1 Execution Success Validation
```python
# Validate execution success
self.assert_c2puml_success(result)
```

**Functions called**:
- `self.assert_c2puml_success(result)` - Validates exit code is 0

#### 6.2 Output File Validation
```python
# Validate output files were created
model_file = self.assert_model_file_exists()
transformed_model_file = self.assert_transformed_model_file_exists()
puml_files = self.assert_puml_files_exist()
```

**Functions called**:
- `self.assert_model_file_exists()` - Validates model.json exists
- `self.assert_transformed_model_file_exists()` - Validates model_transformed.json exists
- `self.assert_puml_files_exist()` - Validates .puml files exist

#### 6.3 Model Content Validation
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
```

**Functions called**:
- `open()` - Open model.json file
- `json.load()` - Parse JSON content
- `model_data["files"].get()` - Get file data

#### 6.4 Struct Validation
```python
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
```

**Functions called**:
- `simple_c_file.get()` - Get structs dictionary
- `structs.get()` - Get Person struct
- `person_struct.get()` - Get fields list
- List comprehension - Extract field names

#### 6.5 Enum Validation
```python
# Validate enum parsing
enums = simple_c_file.get("enums", {})
self.assertGreater(len(enums), 0, "Should find at least one enum")

# Find Status enum
status_enum = enums.get("Status")
self.assertIsNotNone(status_enum, "Status enum should be found")

# Validate Status enum values
values = status_enum.get("values", [])
self.assertEqual(len(values), 2, "Status enum should have 2 values")

value_names = [value.get("name") for value in values]
self.assertIn("OK", value_names)
self.assertIn("ERROR", value_names)
```

**Functions called**:
- `simple_c_file.get()` - Get enums dictionary
- `enums.get()` - Get Status enum
- `status_enum.get()` - Get values list
- List comprehension - Extract value names

#### 6.6 Function Validation
```python
# Validate function parsing
functions = simple_c_file.get("functions", [])
self.assertGreater(len(functions), 0, "Should find at least one function")

# Find main function
main_function = None
for func in functions:
    if func.get("name") == "main":
        main_function = func
        break

self.assertIsNotNone(main_function, "main function should be found")
```

**Functions called**:
- `simple_c_file.get()` - Get functions list
- Loop through functions - Find main function
- `func.get()` - Get function name

#### 6.7 Global Variable Validation
```python
# Validate global variable parsing
globals_list = simple_c_file.get("globals", [])
self.assertGreater(len(globals_list), 0, "Should find at least one global variable")

# Find global_var
global_var_found = False
for global_var in globals_list:
    if global_var.get("name") == "global_var":
        global_var_found = True
        break

self.assertTrue(global_var_found, "global_var should be found")
```

**Functions called**:
- `simple_c_file.get()` - Get globals list
- Loop through globals - Find global_var
- `global_var.get()` - Get global variable name

#### 6.8 Include Validation
```python
# Validate include parsing
includes = simple_c_file.get("includes", [])
self.assertGreater(len(includes), 0, "Should find at least one include")

# Check for stdio.h include
self.assertIn("stdio.h", includes, "stdio.h include should be found")
```

**Functions called**:
- `simple_c_file.get()` - Get includes list
- `self.assertIn()` - Check for stdio.h

#### 6.9 PlantUML Validation
```python
# Validate PlantUML file content
self.assertGreater(len(puml_files), 0, "Should have at least one .puml file")

# Check that the first .puml file contains expected content
with open(puml_files[0], 'r') as f:
    puml_content = f.read()

# Verify PlantUML contains our struct and enum
self.assertIn("Person", puml_content, "PlantUML should contain Person struct")
self.assertIn("Status", puml_content, "PlantUML should contain Status enum")
self.assertIn("main", puml_content, "PlantUML should contain main function")

# Verify PlantUML syntax
self.assertIn("@startuml", puml_content, "PlantUML should start with @startuml")
self.assertIn("@enduml", puml_content, "PlantUML should end with @enduml")
```

**Functions called**:
- `open()` - Open .puml file
- `f.read()` - Read PlantUML content
- `self.assertIn()` - Validate content contains expected elements

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

### Unified Framework Approach (CLI-Only)
```python
# CLI-only execution
result = self.run_c2puml_full_pipeline(config_path, source_dir)
self.assert_c2puml_success(result)

# JSON file validation
with open(model_file, 'r') as f:
    model_data = json.load(f)
simple_c_file = model_data["files"].get("simple.c")
person_struct = simple_c_file["structs"].get("Person")
```

## Benefits of the Unified Approach

1. **Enforces CLI-Only Access** - Tests cannot accidentally use internal APIs
2. **Real-World Testing** - Tests the actual CLI interface that users will use
3. **Comprehensive Validation** - Tests the complete pipeline (parse → transform → generate)
4. **Output Validation** - Validates actual output files (model.json, .puml files)
5. **Framework Consistency** - All tests use the same patterns and helpers
6. **Better Debugging** - Output files are preserved for manual inspection

## File Structure Created

```
/tmp/tmpXXXXXX/
├── config.json                    # Test configuration
├── src/
│   └── simple.c                   # Test source file
└── output/                        # c2puml output directory
    ├── model.json                 # Parsed model
    ├── model_transformed.json     # Transformed model
    └── simple.puml               # Generated PlantUML file
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

This conversion demonstrates the complete workflow of the unified testing framework and serves as a template for converting all remaining tests.