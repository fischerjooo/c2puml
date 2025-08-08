#!/usr/bin/env python3
"""
Validators Processor for the unified testing framework

This module provides the ValidatorsProcessor class that coordinates the execution
of various validators from validators.py to process assertions from YAML data.
Enhanced with comprehensive internal processing methods for all validator capabilities.
"""

import json
import glob
import os
from typing import Dict, Any, List
from .executor import CLIResult
from .validators import ModelValidator, PlantUMLValidator, CLIValidator, OutputValidator, FileValidator


class ValidatorsProcessor:
    """
    Coordinates the execution of validators to process assertions from YAML data
    
    This class orchestrates the validation process by delegating specific validation
    tasks to the appropriate validator classes from validators.py.
    
    Enhanced with comprehensive internal processing methods that provide access to
    all validator capabilities through the existing YAML-based assertion framework.
    """
    
    def __init__(self):
        """Initialize the validators processor with validator instances"""
        self.model_validator = ModelValidator()
        self.puml_validator = PlantUMLValidator()
        self.cli_validator = CLIValidator()
        self.output_validator = OutputValidator()
        self.file_validator = FileValidator()
    
    def process_assertions(self, assertions: Dict[str, Any], model_data: Dict, 
                          puml_files: Dict[str, str], cli_result: CLIResult, test_case) -> None:
        """
        Process assertions from YAML data using appropriate validators
        
        This method coordinates the validation process by:
        1. Processing execution assertions using CLIValidator
        2. Processing model assertions using ModelValidator  
        3. Processing PlantUML assertions using PlantUMLValidator
        4. Processing file system assertions using OutputValidator and FileValidator
        
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
        
        # Process model assertions (enhanced)
        if "model" in assertions:
            self._process_model_assertions(assertions["model"], model_data, test_case)
        
        # Process PlantUML assertions (enhanced)
        if "puml" in assertions:
            self._process_puml_assertions(assertions["puml"], puml_files, test_case)
        
        # Process file system assertions (new)
        if "files" in assertions:
            self._process_file_assertions(assertions["files"], test_case)
        
        # Process validation workflow assertions (new)
        if "workflow" in assertions:
            self._process_workflow_assertions(assertions["workflow"], model_data, puml_files, cli_result, test_case)

    def _process_execution_assertions(self, execution_assertions: Dict, 
                                    cli_result: CLIResult, test_case) -> None:
        """
        Process execution-related assertions using CLIValidator
        Enhanced with comprehensive CLI validation capabilities.
        
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
        
        # Enhanced execution validations
        if "success_expected" in execution_assertions:
            if execution_assertions["success_expected"]:
                self.cli_validator.assert_cli_success(cli_result)
            else:
                expected_error = execution_assertions.get("expected_error")
                self.cli_validator.assert_cli_failure(cli_result, expected_error)

    def _process_model_assertions(self, model_assertions: Dict, 
                                model_data: Dict, test_case) -> None:
        """
        Process model-related assertions using ModelValidator
        Enhanced with comprehensive model validation capabilities.
        
        Args:
            model_assertions: Model assertions from YAML
            model_data: Parsed model.json content
            test_case: Test case instance for assertions
        """
        # Basic model structure validation
        if "validate_structure" in model_assertions and model_assertions["validate_structure"]:
            self.model_validator.assert_model_structure_valid(model_data)
            self.model_validator.assert_model_schema_compliant(model_data)
        
        # Project-level assertions
        if "project_name" in model_assertions:
            self.model_validator.assert_model_project_name(model_data, model_assertions["project_name"])
        
        if "file_count" in model_assertions:
            self.model_validator.assert_model_file_count(model_data, model_assertions["file_count"])
        
        if "expected_files" in model_assertions:
            self.model_validator.assert_model_files_parsed(model_data, model_assertions["expected_files"])
        
        # Enhanced element existence checks
        if "functions_exist" in model_assertions:
            for func_name in model_assertions["functions_exist"]:
                self.model_validator.assert_model_function_exists(model_data, func_name)
        
        if "functions_not_exist" in model_assertions:
            for func_name in model_assertions["functions_not_exist"]:
                self.model_validator.assert_model_function_not_exists(model_data, func_name)
        
        if "structs_exist" in model_assertions:
            for struct_name in model_assertions["structs_exist"]:
                self.model_validator.assert_model_struct_exists(model_data, struct_name)
        
        if "structs_not_exist" in model_assertions:
            for struct_name in model_assertions["structs_not_exist"]:
                self.model_validator.assert_model_struct_not_exists(model_data, struct_name)
        
        if "enums_exist" in model_assertions:
            for enum_name in model_assertions["enums_exist"]:
                self.model_validator.assert_model_enum_exists(model_data, enum_name)
        
        if "enums_not_exist" in model_assertions:
            for enum_name in model_assertions["enums_not_exist"]:
                self.model_validator.assert_model_enum_not_exists(model_data, enum_name)
        
        if "typedefs_exist" in model_assertions:
            for typedef_name in model_assertions["typedefs_exist"]:
                self.model_validator.assert_model_typedef_exists(model_data, typedef_name)
        
        if "globals_exist" in model_assertions:
            for global_name in model_assertions["globals_exist"]:
                self.model_validator.assert_model_global_exists(model_data, global_name)
        
        if "macros_exist" in model_assertions:
            for macro_name in model_assertions["macros_exist"]:
                self.model_validator.assert_model_macro_exists(model_data, macro_name)
        
        if "includes_exist" in model_assertions:
            for include_name in model_assertions["includes_exist"]:
                self.model_validator.assert_model_include_exists(model_data, include_name)
        
        # Enhanced struct and enum detail validation
        if "struct_details" in model_assertions:
            for struct_name, struct_details in model_assertions["struct_details"].items():
                if "fields" in struct_details:
                    self.model_validator.assert_model_struct_fields(
                        model_data, struct_name, struct_details["fields"]
                    )
        
        if "enum_details" in model_assertions:
            for enum_name, enum_details in model_assertions["enum_details"].items():
                if "values" in enum_details:
                    self.model_validator.assert_model_enum_values(
                        model_data, enum_name, enum_details["values"]
                    )
        
        # Check files (existing functionality preserved)
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
        Enhanced with comprehensive PlantUML validation capabilities.
        
        Args:
            puml_assertions: PlantUML assertions from YAML
            puml_files: Dictionary mapping PlantUML filenames to their content
            test_case: Test case instance for assertions
        """
        # Process global PlantUML assertions (applied to all files)
        if puml_assertions.get("syntax_valid", False):
            self.puml_validator.assert_puml_start_end_tags_multi(puml_files)
        
        # Enhanced global assertions
        if "file_count" in puml_assertions:
            expected_count = puml_assertions["file_count"]
            actual_count = len(puml_files)
            if actual_count != expected_count:
                raise AssertionError(f"Expected {expected_count} PlantUML files, got {actual_count}")
        
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
        
        # Enhanced class validation
        if "classes_exist" in puml_assertions:
            for class_info in puml_assertions["classes_exist"]:
                if isinstance(class_info, str):
                    class_name = class_info
                    stereotype = None
                else:
                    class_name = class_info.get("name")
                    stereotype = class_info.get("stereotype")
                self.puml_validator.assert_puml_class_exists_multi(puml_files, class_name, stereotype)
        
        # Enhanced relationship validation
        if "relationships_exist" in puml_assertions:
            for rel_info in puml_assertions["relationships_exist"]:
                source = rel_info.get("source")
                target = rel_info.get("target")
                rel_type = rel_info.get("type")
                if source and target and rel_type:
                    self.puml_validator.assert_puml_relationship_multi(puml_files, source, target, rel_type)
        
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
        Enhanced with comprehensive single-file validation capabilities.
        
        Args:
            filename: Name of the PlantUML file
            puml_content: Content of the PlantUML file
            file_assertions: Assertions specific to this file
            test_case: Test case instance for assertions
        """
        # Basic syntax validation
        if file_assertions.get("syntax_valid", False):
            self.puml_validator.assert_puml_start_end_tags(puml_content)
        
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
        
        # Check forbidden lines in this file
        if "not_contains_lines" in file_assertions:
            forbidden_lines = file_assertions["not_contains_lines"]
            for forbidden_line in forbidden_lines:
                self.puml_validator.assert_puml_not_contains(puml_content, forbidden_line)
        
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
        
        # Enhanced class validation
        if "classes_exist" in file_assertions:
            for class_info in file_assertions["classes_exist"]:
                if isinstance(class_info, str):
                    class_name = class_info
                    stereotype = None
                else:
                    class_name = class_info.get("name")
                    stereotype = class_info.get("stereotype")
                self.puml_validator.assert_puml_class_exists(puml_content, class_name, stereotype)
        
        # Check for specific relationships in this file
        if "relationships" in file_assertions:
            for rel_name, rel_assertions in file_assertions["relationships"].items():
                source = rel_assertions.get("source")
                target = rel_assertions.get("target")
                rel_type = rel_assertions.get("type")
                if source and target and rel_type:
                    self.puml_validator.assert_puml_relationship(puml_content, source, target, rel_type)
        
        # Enhanced relationship validation
        if "relationships_exist" in file_assertions:
            for rel_info in file_assertions["relationships_exist"]:
                source = rel_info.get("source")
                target = rel_info.get("target")
                rel_type = rel_info.get("type")
                if source and target and rel_type:
                    self.puml_validator.assert_puml_relationship(puml_content, source, target, rel_type)

    def _process_file_assertions(self, file_assertions: Dict, test_case) -> None:
        """
        Process file system-related assertions using OutputValidator and FileValidator
        New functionality for comprehensive file system validation.
        
        Args:
            file_assertions: File assertions from YAML
            test_case: Test case instance for assertions
        """
        # Check output directory existence
        if "output_dir_exists" in file_assertions:
            output_dir = file_assertions["output_dir_exists"]
            self.output_validator.assert_output_dir_exists(output_dir)
        
        # Check specific files exist
        if "files_exist" in file_assertions:
            for file_path in file_assertions["files_exist"]:
                self.output_validator.assert_file_exists(file_path)
        
        # Check specific files don't exist
        if "files_not_exist" in file_assertions:
            for file_path in file_assertions["files_not_exist"]:
                self.output_validator.assert_file_not_exists(file_path)
        
        # Validate JSON files
        if "json_files_valid" in file_assertions:
            for json_file in file_assertions["json_files_valid"]:
                self.file_validator.assert_json_valid(json_file)
        
        # Validate file encoding
        if "utf8_files" in file_assertions:
            for file_path in file_assertions["utf8_files"]:
                self.file_validator.assert_file_valid_utf8(file_path)
        
        # Check file content
        if "file_content" in file_assertions:
            for file_path, content_assertions in file_assertions["file_content"].items():
                if "contains" in content_assertions:
                    for expected_text in content_assertions["contains"]:
                        self.output_validator.assert_file_contains(file_path, expected_text)
                
                if "not_contains" in content_assertions:
                    for forbidden_text in content_assertions["not_contains"]:
                        self.output_validator.assert_file_not_contains(file_path, forbidden_text)
                
                if "contains_lines" in content_assertions:
                    self.output_validator.assert_file_contains_lines(
                        file_path, content_assertions["contains_lines"]
                    )
                
                if "line_count" in content_assertions:
                    self.output_validator.assert_file_line_count(
                        file_path, content_assertions["line_count"]
                    )
                
                if "empty" in content_assertions and content_assertions["empty"]:
                    self.output_validator.assert_file_empty(file_path)
                
                if "not_empty" in content_assertions and content_assertions["not_empty"]:
                    self.output_validator.assert_file_not_empty(file_path)

    def _process_workflow_assertions(self, workflow_assertions: Dict, model_data: Dict,
                                   puml_files: Dict[str, str], cli_result: CLIResult, test_case) -> None:
        """
        Process workflow-related assertions for comprehensive testing scenarios
        New functionality for validating complete workflows and test patterns.
        
        Args:
            workflow_assertions: Workflow assertions from YAML
            model_data: Parsed model.json content
            puml_files: Dictionary mapping PlantUML filenames to their content
            cli_result: CLI execution result
            test_case: Test case instance for assertions
        """
        # Parser workflow validation
        if "parser_workflow" in workflow_assertions:
            parser_workflow = workflow_assertions["parser_workflow"]
            
            # Validate parser output exists
            if "output_exists" in parser_workflow and parser_workflow["output_exists"]:
                # This is implicit - model_data being passed means model.json was loaded
                pass
            
            # Validate parsing completeness
            if "expected_elements" in parser_workflow:
                expected_elements = parser_workflow["expected_elements"]
                
                if "functions" in expected_elements:
                    for func_name in expected_elements["functions"]:
                        self.model_validator.assert_model_function_exists(model_data, func_name)
                
                if "structs" in expected_elements:
                    for struct_name in expected_elements["structs"]:
                        self.model_validator.assert_model_struct_exists(model_data, struct_name)
                
                if "enums" in expected_elements:
                    for enum_name in expected_elements["enums"]:
                        self.model_validator.assert_model_enum_exists(model_data, enum_name)
        
        # Transformer workflow validation
        if "transformer_workflow" in workflow_assertions:
            transformer_workflow = workflow_assertions["transformer_workflow"]
            
            # Validate elements were removed
            if "elements_removed" in transformer_workflow:
                removed = transformer_workflow["elements_removed"]
                
                if "functions" in removed:
                    for func_name in removed["functions"]:
                        self.model_validator.assert_model_function_not_exists(model_data, func_name)
                
                if "structs" in removed:
                    for struct_name in removed["structs"]:
                        self.model_validator.assert_model_struct_not_exists(model_data, struct_name)
            
            # Validate elements were preserved
            if "elements_preserved" in transformer_workflow:
                preserved = transformer_workflow["elements_preserved"]
                
                if "functions" in preserved:
                    for func_name in preserved["functions"]:
                        self.model_validator.assert_model_function_exists(model_data, func_name)
                
                if "structs" in preserved:
                    for struct_name in preserved["structs"]:
                        self.model_validator.assert_model_struct_exists(model_data, struct_name)
        
        # Generator workflow validation
        if "generator_workflow" in workflow_assertions:
            generator_workflow = workflow_assertions["generator_workflow"]
            
            # Validate PlantUML output exists
            if "output_exists" in generator_workflow and generator_workflow["output_exists"]:
                if not puml_files:
                    raise AssertionError("Expected PlantUML files but none were found")
            
            # Validate syntax
            if "syntax_valid" in generator_workflow and generator_workflow["syntax_valid"]:
                self.puml_validator.assert_puml_start_end_tags_multi(puml_files)
            
            # Validate content elements
            if "expected_elements" in generator_workflow:
                for element in generator_workflow["expected_elements"]:
                    self.puml_validator.assert_puml_contains_multi(puml_files, element)
        
        # Performance validation
        if "performance" in workflow_assertions:
            performance = workflow_assertions["performance"]
            
            if "max_execution_time" in performance:
                max_time = performance["max_execution_time"]
                self.cli_validator.assert_cli_execution_time_under(cli_result, max_time)