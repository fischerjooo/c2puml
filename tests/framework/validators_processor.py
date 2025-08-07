#!/usr/bin/env python3
"""
Validators Processor for the unified testing framework

This module provides the ValidatorsProcessor class that coordinates the execution
of various validators from validators.py to process assertions from YAML data.
"""

import json
from typing import Dict, Any
from .executor import CLIResult
from .validators import ModelValidator, PlantUMLValidator, CLIValidator


class ValidatorsProcessor:
    """
    Coordinates the execution of validators to process assertions from YAML data
    
    This class orchestrates the validation process by delegating specific validation
    tasks to the appropriate validator classes from validators.py.
    """
    
    def __init__(self):
        """Initialize the validators processor with validator instances"""
        self.model_validator = ModelValidator()
        self.puml_validator = PlantUMLValidator()
        self.cli_validator = CLIValidator()
    
    def process_assertions(self, assertions: Dict[str, Any], model_data: Dict, 
                          puml_content: str, cli_result: CLIResult, test_case) -> None:
        """
        Process assertions from YAML data using appropriate validators
        
        This method coordinates the validation process by:
        1. Processing execution assertions using CLIValidator
        2. Processing model assertions using ModelValidator  
        3. Processing PlantUML assertions using PlantUMLValidator
        
        Args:
            assertions: Dictionary containing assertions from YAML
            model_data: Parsed model.json content
            puml_content: PlantUML file content
            cli_result: CLI execution result
            test_case: Test case instance for assertions
        """
        # Process execution assertions
        if "execution" in assertions:
            self._process_execution_assertions(assertions["execution"], cli_result, test_case)
        
        # Process model assertions
        if "model" in assertions:
            self._process_model_assertions(assertions["model"], model_data, test_case)
        
        # Process PlantUML assertions
        if "puml" in assertions:
            self._process_puml_assertions(assertions["puml"], puml_content, test_case)
    
    def _process_execution_assertions(self, execution_assertions: Dict, 
                                    cli_result: CLIResult, test_case) -> None:
        """
        Process execution-related assertions using CLIValidator
        
        Args:
            execution_assertions: Execution assertions from YAML
            cli_result: CLI execution result
            test_case: Test case instance for assertions
        """
        # Check exit code
        if "exit_code" in execution_assertions:
            expected_exit_code = execution_assertions["exit_code"]
            if expected_exit_code == 0:
                self.cli_validator.assert_cli_success(cli_result)
            else:
                self.cli_validator.assert_cli_exit_code(cli_result, expected_exit_code)
        
        # Check stdout content
        if "stdout_contains" in execution_assertions:
            expected_text = execution_assertions["stdout_contains"]
            self.cli_validator.assert_cli_stdout_contains(cli_result, expected_text)
        
        # Check stderr content
        if "stderr_contains" in execution_assertions:
            expected_text = execution_assertions["stderr_contains"]
            self.cli_validator.assert_cli_stderr_contains(cli_result, expected_text)
        
        # Check execution time
        if "max_execution_time" in execution_assertions:
            max_time = execution_assertions["max_execution_time"]
            self.cli_validator.assert_cli_execution_time_under(cli_result, max_time)
    
    def _process_model_assertions(self, model_assertions: Dict, 
                                model_data: Dict, test_case) -> None:
        """
        Process model-related assertions using ModelValidator
        
        Args:
            model_assertions: Model assertions from YAML
            model_data: Parsed model.json content
            test_case: Test case instance for assertions
        """
        # Check files
        if "files" in model_assertions:
            for filename, file_assertions in model_assertions["files"].items():
                if filename in model_data.get("files", {}):
                    self._process_file_assertions(file_assertions, model_data, test_case)
        
        # Check element counts
        if "element_counts" in model_assertions:
            for element_type, expected_count in model_assertions["element_counts"].items():
                self.model_validator.assert_model_element_count(
                    model_data, element_type, expected_count
                )
    
    def _process_file_assertions(self, file_assertions: Dict, 
                               model_data: Dict, test_case) -> None:
        """
        Process assertions for a specific file using ModelValidator
        
        Args:
            file_assertions: File-specific assertions from YAML
            model_data: Complete model data
            test_case: Test case instance for assertions
        """
        # Check structs
        if "structs" in file_assertions:
            for struct_name, struct_assertions in file_assertions["structs"].items():
                self.model_validator.assert_model_struct_exists(model_data, struct_name)
                
                # Check struct fields
                if "fields" in struct_assertions:
                    expected_fields = struct_assertions["fields"]
                    self.model_validator.assert_model_struct_fields(
                        model_data, struct_name, expected_fields
                    )
        
        # Check enums
        if "enums" in file_assertions:
            for enum_name, enum_assertions in file_assertions["enums"].items():
                self.model_validator.assert_model_enum_exists(model_data, enum_name)
                
                # Check enum values
                if "values" in enum_assertions:
                    expected_values = enum_assertions["values"]
                    self.model_validator.assert_model_enum_values(
                        model_data, enum_name, expected_values
                    )
        
        # Check functions
        if "functions" in file_assertions:
            for func_name in file_assertions["functions"]:
                self.model_validator.assert_model_function_exists(model_data, func_name)
        
        # Check globals
        if "globals" in file_assertions:
            for global_name in file_assertions["globals"]:
                self.model_validator.assert_model_global_exists(model_data, global_name)
        
        # Check includes
        if "includes" in file_assertions:
            for include_name in file_assertions["includes"]:
                self.model_validator.assert_model_include_exists(model_data, include_name)
    
    def _process_puml_assertions(self, puml_assertions: Dict, 
                               puml_content: str, test_case) -> None:
        """
        Process PlantUML-related assertions using PlantUMLValidator
        
        Args:
            puml_assertions: PlantUML assertions from YAML
            puml_content: PlantUML file content
            test_case: Test case instance for assertions
        """
        # Check syntax validity
        if puml_assertions.get("syntax_valid", False):
            self.puml_validator.assert_puml_start_end_tags(puml_content)
        
        # Check for specific elements
        if "contains_elements" in puml_assertions:
            for element_name in puml_assertions["contains_elements"]:
                self.puml_validator.assert_puml_contains(puml_content, element_name)
        
        # Check for forbidden elements
        if "not_contains_elements" in puml_assertions:
            for element_name in puml_assertions["not_contains_elements"]:
                self.puml_validator.assert_puml_not_contains(puml_content, element_name)
        
        # Check specific lines
        if "contains_lines" in puml_assertions:
            expected_lines = puml_assertions["contains_lines"]
            self.puml_validator.assert_puml_contains_lines(puml_content, expected_lines)
        
        # Check line count
        if "line_count" in puml_assertions:
            expected_count = puml_assertions["line_count"]
            self.puml_validator.assert_puml_line_count(puml_content, expected_count)
        
        # Check class count
        if "class_count" in puml_assertions:
            expected_count = puml_assertions["class_count"]
            self.puml_validator.assert_puml_class_count(puml_content, expected_count)
        
        # Check relationship count
        if "relationship_count" in puml_assertions:
            expected_count = puml_assertions["relationship_count"]
            self.puml_validator.assert_puml_relationship_count(puml_content, expected_count)