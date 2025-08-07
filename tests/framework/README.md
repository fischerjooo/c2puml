# C2PUML Test Framework - Component Responsibilities

This document outlines the responsibilities of each component in the unified testing framework to ensure clear separation of concerns and avoid duplication.

## Framework Components

### 1. `base.py` - UnifiedTestCase Base Class
**Primary Responsibility**: Test setup, teardown, and component initialization

**Responsibilities**:
- ✅ Initialize framework components (executor, data_loader, assertion_processor, validators)
- ✅ Create temporary directories for test execution
- ✅ Provide component access to all validators and framework components

**What it does NOT do**:
- ❌ Create test files (handled by `data_loader.py`)
- ❌ Process complex assertions (handled by `assertion_processor.py`)
- ❌ Execute c2puml (handled by `executor.py`)
- ❌ Validate specific content (handled by `validators.py`)
- ❌ Provide assertion methods (handled by validators)

### 2. `data_loader.py` - TestDataLoader
**Primary Responsibility**: Load test data from YAML and create temporary files

**Responsibilities**:
- ✅ Load multi-document YAML test files
- ✅ Parse YAML documents into structured test data
- ✅ Validate YAML structure and content
- ✅ Create temporary source files from YAML content
- ✅ Create temporary config.json files from YAML content
- ✅ Manage test-specific temp directories (`tests/*/temp/test_<id>/`)
- ✅ Support meaningful test IDs and file discovery

**What it does NOT do**:
- ❌ Execute tests (handled by test classes)
- ❌ Process assertions (handled by `assertion_processor.py`)
- ❌ Validate output (handled by `validators.py`)

### 3. `executor.py` - TestExecutor
**Primary Responsibility**: Execute c2puml via CLI interface

**Responsibilities**:
- ✅ Execute c2puml through CLI interface only (no internal API access)
- ✅ Support different execution modes:
  - `run_full_pipeline()` - Complete workflow
  - `run_parse_only()` - Parse step only
  - `run_transform_only()` - Transform step only
  - `run_generate_only()` - Generate step only
- ✅ Handle working directory management
- ✅ Provide execution results (CLIResult)
- ✅ Support verbose output and environment variables
- ✅ Manage command building and execution

**What it does NOT do**:
- ❌ Load test data (handled by `data_loader.py`)
- ❌ Create files (handled by `data_loader.py`)
- ❌ Process assertions (handled by `assertion_processor.py`)
- ❌ Validate output (handled by `validators.py`)

### 4. `assertion_processor.py` - AssertionProcessor
**Primary Responsibility**: Process assertions from YAML data

**Responsibilities**:
- ✅ Process execution assertions (exit codes, output files)
- ✅ Process model validation assertions (structs, enums, functions, etc.)
- ✅ Process PlantUML validation assertions (content, syntax)
- ✅ Apply assertions using appropriate validators
- ✅ Handle YAML assertion structure (execution, model, puml sections)

**What it does NOT do**:
- ❌ Load test data (handled by `data_loader.py`)
- ❌ Execute c2puml (handled by `executor.py`)
- ✅ Provide basic assertions (handled by validators)
- ❌ Validate specific content (handled by `validators.py`)

### 5. `validators.py` - Validation Classes
**Primary Responsibility**: Validate specific types of content and files

**Responsibilities**:
- ✅ **ModelValidator**: Validate model.json structure and content
  - Struct existence and fields
  - Enum existence and values
  - Function existence
  - Global variable existence
  - Include file existence
  - Element counts
- ✅ **PlantUMLValidator**: Validate .puml files and content
  - File existence and syntax
  - Content validation
  - Class and relationship validation
- ✅ **OutputValidator**: Validate general output files and directories
  - File existence and content
  - Directory structure
  - Log validation
  - **C2PUML-specific output validation**:
    - `assert_model_file_exists()` - Check for model.json
    - `assert_transformed_model_file_exists()` - Check for model_transformed.json
    - `assert_puml_files_exist()` - Check for .puml files
- ✅ **FileValidator**: Advanced file operations
  - File comparison
  - JSON validation
  - UTF-8 validation
  - Whitespace validation
- ✅ **CLIValidator**: Validate CLI execution results
  - `assert_cli_success()` - Verify successful execution
  - `assert_cli_failure()` - Verify expected failures
  - `assert_cli_exit_code()` - Check specific exit codes
  - `assert_cli_stdout_contains()` - Check stdout content
  - `assert_cli_stderr_contains()` - Check stderr content
  - `assert_cli_execution_time_under()` - Check execution time

**What it does NOT do**:
- ❌ Load test data (handled by `data_loader.py`)
- ❌ Execute c2puml (handled by `executor.py`)
- ❌ Process assertions (handled by `assertion_processor.py`)
- ❌ Provide test setup (handled by `base.py`)

### 6. `__init__.py` - Package Initialization
**Primary Responsibility**: Package setup and exports

**Responsibilities**:
- ✅ Import all framework components
- ✅ Define `__all__` for package exports
- ✅ Provide clean import interface for tests

## Responsibility Separation Rules

### ✅ **Good Separation**
- Each component has a single, well-defined responsibility
- Components use other components through their public interfaces
- No circular dependencies between components
- Clear data flow: data_loader → executor → assertion_processor → validators

### ❌ **Avoided Overlaps**
- **File Creation**: Only `data_loader.py` creates files
- **Assertion Processing**: Only `assertion_processor.py` processes complex assertions
- **Execution**: Only `executor.py` executes c2puml
- **Validation**: Only `validators.py` validates specific content
- **Test Setup**: Only `base.py` handles test setup and component initialization

### 🔄 **Data Flow**
```
Test Class
    ↓
base.py (setup) → data_loader.py (load data) → executor.py (execute) → validators.py (validate) → assertion_processor.py (process assertions)
```

## Usage Pattern

```python
class TestExample(UnifiedTestCase):
    def test_something(self):
        # 1. Load test data (data_loader.py responsibility)
        test_data = self.data_loader.load_test_data("test_id")
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "test_id")
        
        # 2. Execute c2puml (executor.py responsibility)
        result = self.executor.run_full_pipeline(config_filename, temp_dir)
        
        # 3. Basic CLI validation (CLIValidator responsibility)
        self.cli_validator.assert_cli_success(result)
        
        # 4. Load output for validation (OutputValidator responsibility)
        model_file = self.output_validator.assert_model_file_exists(output_dir)
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        
        # 5. Load content for validation
        model_data = json.load(open(model_file))
        puml_content = open(puml_files[0]).read()
        
        # 6. Process assertions (assertion_processor.py responsibility)
        self.assertion_processor.process_assertions(
            test_data["assertions"], model_data, puml_content, result, self
        )
```

## Validator Usage Examples

### CLIValidator
```python
# Check successful execution
self.cli_validator.assert_cli_success(result)

# Check expected failure
self.cli_validator.assert_cli_failure(result, expected_error="Config file not found")

# Check specific exit code
self.cli_validator.assert_cli_exit_code(result, 1)

# Check stdout/stderr content
self.cli_validator.assert_cli_stdout_contains(result, "Processing complete")
self.cli_validator.assert_cli_stderr_contains(result, "Warning")
```

### OutputValidator
```python
# Check C2PUML output files
model_file = self.output_validator.assert_model_file_exists(output_dir)
transformed_file = self.output_validator.assert_transformed_model_file_exists(output_dir)
puml_files = self.output_validator.assert_puml_files_exist(output_dir, min_count=2)

# Check general files
self.output_validator.assert_file_exists("some_file.txt")
self.output_validator.assert_file_contains("log.txt", "Success")
```

This clear separation ensures maintainability, testability, and prevents duplication of responsibilities across the framework.