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
                          puml_files: Dict[str, str], cli_result: CLIResult, test_case) -> None:
        """
        Process assertions from YAML data using appropriate validators
        
        This method coordinates the validation process by:
        1. Processing execution assertions using CLIValidator
        2. Processing model assertions using ModelValidator  
        3. Processing PlantUML assertions using PlantUMLValidator
        
        Args:
            assertions: Dictionary containing assertions from YAML
            model_data: Parsed model.json content
            puml_files: Dictionary mapping PlantUML filenames to their content
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
            self._process_puml_assertions(assertions["puml"], puml_files, test_case)
    
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
                    # Process file-specific assertions directly
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
        
        # Check element counts
        if "element_counts" in model_assertions:
            for element_type, expected_count in model_assertions["element_counts"].items():
                self.model_validator.assert_model_element_count(
                    model_data, element_type, expected_count
                )
    
    def _process_puml_assertions(self, puml_assertions: Dict, 
                                puml_files: Dict[str, str], test_case) -> None:
        """
        Process PlantUML-related assertions using PlantUMLValidator
        
        Args:
            puml_assertions: PlantUML assertions from YAML
            puml_files: Dictionary mapping PlantUML filenames to their content
            test_case: Test case instance for assertions
        """
        # Process global PlantUML assertions (applied to all files)
        if puml_assertions.get("syntax_valid", False):
            self.puml_validator.assert_puml_start_end_tags_multi(puml_files)
        
        # Process global contains assertions (at least one file must contain)
        if "contains_elements" in puml_assertions:
            for element_name in puml_assertions["contains_elements"]:
                self.puml_validator.assert_puml_contains_multi(puml_files, element_name)
        
        # Process global not_contains assertions (no file should contain)
        if "not_contains_elements" in puml_assertions:
            for element_name in puml_assertions["not_contains_elements"]:
                self.puml_validator.assert_puml_not_contains_multi(puml_files, element_name)
        
        # Process global contains_lines assertions (at least one file must contain all lines)
        if "contains_lines" in puml_assertions:
            expected_lines = puml_assertions["contains_lines"]
            self.puml_validator.assert_puml_contains_lines_multi(puml_files, expected_lines)
        
        # Process global count assertions (total across all files)
        if "line_count" in puml_assertions:
            expected_count = puml_assertions["line_count"]
            self.puml_validator.assert_puml_line_count_multi(puml_files, expected_count)
        
        if "class_count" in puml_assertions:
            expected_count = puml_assertions["class_count"]
            self.puml_validator.assert_puml_class_count_multi(puml_files, expected_count)
        
        if "relationship_count" in puml_assertions:
            expected_count = puml_assertions["relationship_count"]
            self.puml_validator.assert_puml_relationship_count_multi(puml_files, expected_count)
        
        # Process per-file PlantUML assertions
        if "files" in puml_assertions:
            for filename, file_assertions in puml_assertions["files"].items():
                if filename in puml_files:
                    self._process_single_puml_file_assertions(
                        filename, puml_files[filename], file_assertions, test_case
                    )
    
    def _process_single_puml_file_assertions(self, filename: str, puml_content: str, 
                                           file_assertions: Dict, test_case) -> None:
        """
        Process assertions for a single PlantUML file
        
        Args:
            filename: Name of the PlantUML file
            puml_content: Content of the PlantUML file
            file_assertions: Assertions specific to this file
            test_case: Test case instance for assertions
        """
        # Check for specific elements in this file
        if "contains_elements" in file_assertions:
            for element_name in file_assertions["contains_elements"]:
                self.puml_validator.assert_puml_contains(puml_content, element_name)
        
        # Check for forbidden elements in this file
        if "not_contains_elements" in file_assertions:
            for element_name in file_assertions["not_contains_elements"]:
                self.puml_validator.assert_puml_not_contains(puml_content, element_name)
        
        # Check specific lines in this file
        if "contains_lines" in file_assertions:
            expected_lines = file_assertions["contains_lines"]
            self.puml_validator.assert_puml_contains_lines(puml_content, expected_lines)
        
        # Check line count for this file
        if "line_count" in file_assertions:
            expected_count = file_assertions["line_count"]
            self.puml_validator.assert_puml_line_count(puml_content, expected_count)
        
        # Check class count for this file
        if "class_count" in file_assertions:
            expected_count = file_assertions["class_count"]
            self.puml_validator.assert_puml_class_count(puml_content, expected_count)
        
        # Check relationship count for this file
        if "relationship_count" in file_assertions:
            expected_count = file_assertions["relationship_count"]
            self.puml_validator.assert_puml_relationship_count(puml_content, expected_count)
        
        # Check for specific classes in this file
        if "classes" in file_assertions:
            for class_name, class_assertions in file_assertions["classes"].items():
                stereotype = class_assertions.get("stereotype")
                self.puml_validator.assert_puml_class_exists(puml_content, class_name, stereotype)
        
        # Check for specific relationships in this file
        if "relationships" in file_assertions:
            for rel_name, rel_assertions in file_assertions["relationships"].items():
                source = rel_assertions.get("source")
                target = rel_assertions.get("target")
                rel_type = rel_assertions.get("type")
                if source and target and rel_type:
                    self.puml_validator.assert_puml_relationship(puml_content, source, target, rel_type)