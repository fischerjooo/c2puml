#!/usr/bin/env python3
"""
Validators Processor for the unified testing framework

This module provides the ValidatorsProcessor class that coordinates the execution
of various validators from validators.py to process assertions from YAML data.
Now enhanced with unified access to all validator methods with meaningful names.
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
    
    Enhanced with unified access to all validator methods with meaningful names,
    organized by validation type for improved test development experience.
    """
    
    def __init__(self):
        """Initialize the validators processor with validator instances"""
        self.model_validator = ModelValidator()
        self.puml_validator = PlantUMLValidator()
        self.cli_validator = CLIValidator()
        self.output_validator = OutputValidator()
        self.file_validator = FileValidator()
    
    # =====================================================
    # YAML-BASED ASSERTION PROCESSING (Original functionality)
    # =====================================================
    
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
    
    # =====================================================
    # PARSER VALIDATION METHODS (For parser tests)
    # =====================================================
    
    def validate_parser_output_exists(self, output_dir: str) -> str:
        """
        Validate that parser generated a model.json file
        
        This is typically the first validation for parser-only tests.
        Recommendation: Use this for parser tests that only run parsing step.
        
        Returns:
            Path to the model.json file
        """
        return self.output_validator.assert_model_file_exists(output_dir)
    
    def validate_parser_project_structure(self, model_data: Dict, project_name: str = None, 
                                        expected_files: List[str] = None) -> None:
        """
        Validate basic parser output structure
        
        Recommendation: Use this as a foundation validation for all parser tests.
        
        Args:
            model_data: Parsed model.json content
            project_name: Expected project name (optional)
            expected_files: List of files that should be parsed (optional)
        """
        self.model_validator.assert_model_structure_valid(model_data)
        self.model_validator.assert_model_schema_compliant(model_data)
        
        if project_name:
            self.model_validator.assert_model_project_name(model_data, project_name)
        
        if expected_files:
            self.model_validator.assert_model_files_parsed(model_data, expected_files)
    
    def validate_c_structures_parsed(self, model_data: Dict, structs: List[str] = None, 
                                   enums: List[str] = None, unions: List[str] = None,
                                   typedefs: List[str] = None) -> None:
        """
        Validate that C structures were correctly parsed
        
        Recommendation: Use this for parser tests focusing on C structure parsing.
        
        Args:
            model_data: Parsed model.json content
            structs: List of struct names that should exist
            enums: List of enum names that should exist
            unions: List of union names that should exist
            typedefs: List of typedef names that should exist
        """
        if structs:
            for struct_name in structs:
                self.model_validator.assert_model_struct_exists(model_data, struct_name)
        
        if enums:
            for enum_name in enums:
                self.model_validator.assert_model_enum_exists(model_data, enum_name)
        
        if typedefs:
            for typedef_name in typedefs:
                self.model_validator.assert_model_typedef_exists(model_data, typedef_name)
    
    def validate_c_functions_parsed(self, model_data: Dict, functions: List[str]) -> None:
        """
        Validate that C functions were correctly parsed
        
        Recommendation: Use this for parser tests focusing on function parsing.
        
        Args:
            model_data: Parsed model.json content
            functions: List of function names that should exist
        """
        for func_name in functions:
            self.model_validator.assert_model_function_exists(model_data, func_name)
    
    def validate_c_globals_parsed(self, model_data: Dict, globals_list: List[str]) -> None:
        """
        Validate that global variables were correctly parsed
        
        Recommendation: Use this for parser tests focusing on global variable parsing.
        
        Args:
            model_data: Parsed model.json content
            globals_list: List of global variable names that should exist
        """
        for global_name in globals_list:
            self.model_validator.assert_model_global_exists(model_data, global_name)
    
    def validate_c_includes_parsed(self, model_data: Dict, includes: List[str]) -> None:
        """
        Validate that include statements were correctly parsed
        
        Recommendation: Use this for parser tests focusing on include processing.
        
        Args:
            model_data: Parsed model.json content
            includes: List of include names that should exist
        """
        self.model_validator.assert_model_includes_exist(model_data, includes)
    
    def validate_c_macros_parsed(self, model_data: Dict, macros: List[str]) -> None:
        """
        Validate that macros were correctly parsed
        
        Recommendation: Use this for parser tests focusing on macro processing.
        
        Args:
            model_data: Parsed model.json content
            macros: List of macro names that should exist
        """
        for macro_name in macros:
            self.model_validator.assert_model_macro_exists(model_data, macro_name)
    
    def validate_struct_details(self, model_data: Dict, struct_name: str, expected_fields: List[str]) -> None:
        """
        Validate detailed structure of a parsed struct
        
        Recommendation: Use this for parser tests that need to verify struct field details.
        
        Args:
            model_data: Parsed model.json content
            struct_name: Name of the struct to validate
            expected_fields: List of field names the struct should have
        """
        self.model_validator.assert_model_struct_fields(model_data, struct_name, expected_fields)
    
    def validate_enum_details(self, model_data: Dict, enum_name: str, expected_values: List[str]) -> None:
        """
        Validate detailed structure of a parsed enum
        
        Recommendation: Use this for parser tests that need to verify enum value details.
        
        Args:
            model_data: Parsed model.json content
            enum_name: Name of the enum to validate
            expected_values: List of values the enum should have
        """
        self.model_validator.assert_model_enum_values(model_data, enum_name, expected_values)
    
    def validate_parsing_element_counts(self, model_data: Dict, expected_counts: Dict[str, int]) -> None:
        """
        Validate element counts across all parsed files
        
        Recommendation: Use this for comprehensive parser tests to verify parsing completeness.
        
        Args:
            model_data: Parsed model.json content
            expected_counts: Dictionary mapping element types to expected counts
                           (e.g., {'structs': 3, 'functions': 5, 'enums': 2})
        """
        for element_type, expected_count in expected_counts.items():
            self.model_validator.assert_model_element_count(model_data, element_type, expected_count)
    
    # =====================================================
    # TRANSFORMER VALIDATION METHODS (For transformer tests)
    # =====================================================
    
    def validate_transformer_output_exists(self, output_dir: str) -> str:
        """
        Validate that transformer generated a model_transformed.json file
        
        Recommendation: Use this for transformer tests that verify transformation occurred.
        
        Returns:
            Path to the model_transformed.json file
        """
        return self.output_validator.assert_transformed_model_file_exists(output_dir)
    
    def validate_elements_removed(self, model_data: Dict, removed_functions: List[str] = None,
                                removed_structs: List[str] = None, removed_enums: List[str] = None) -> None:
        """
        Validate that specific elements were removed during transformation
        
        Recommendation: Use this for transformer tests that verify element removal.
        
        Args:
            model_data: Parsed model.json content (transformed)
            removed_functions: List of function names that should NOT exist
            removed_structs: List of struct names that should NOT exist
            removed_enums: List of enum names that should NOT exist
        """
        if removed_functions:
            for func_name in removed_functions:
                self.model_validator.assert_model_function_not_exists(model_data, func_name)
        
        if removed_structs:
            for struct_name in removed_structs:
                self.model_validator.assert_model_struct_not_exists(model_data, struct_name)
        
        if removed_enums:
            for enum_name in removed_enums:
                self.model_validator.assert_model_enum_not_exists(model_data, enum_name)
    
    def validate_elements_preserved(self, model_data: Dict, preserved_functions: List[str] = None,
                                  preserved_structs: List[str] = None, preserved_enums: List[str] = None) -> None:
        """
        Validate that specific elements were preserved during transformation
        
        Recommendation: Use this for transformer tests that verify elements were not incorrectly removed.
        
        Args:
            model_data: Parsed model.json content (transformed)
            preserved_functions: List of function names that should still exist
            preserved_structs: List of struct names that should still exist
            preserved_enums: List of enum names that should still exist
        """
        if preserved_functions:
            for func_name in preserved_functions:
                self.model_validator.assert_model_function_exists(model_data, func_name)
        
        if preserved_structs:
            for struct_name in preserved_structs:
                self.model_validator.assert_model_struct_exists(model_data, struct_name)
        
        if preserved_enums:
            for enum_name in preserved_enums:
                self.model_validator.assert_model_enum_exists(model_data, enum_name)
    
    def validate_transformation_counts(self, original_model: Dict, transformed_model: Dict,
                                     expected_reductions: Dict[str, int] = None) -> None:
        """
        Validate that element counts changed as expected during transformation
        
        Recommendation: Use this for transformer tests that verify quantitative changes.
        
        Args:
            original_model: Original model.json content (before transformation)
            transformed_model: Transformed model.json content (after transformation)
            expected_reductions: Dictionary mapping element types to expected count reductions
                                (e.g., {'functions': 2, 'structs': 1} means 2 fewer functions, 1 fewer struct)
        """
        if expected_reductions:
            for element_type, expected_reduction in expected_reductions.items():
                # Calculate original count
                original_count = 0
                for file_data in original_model.get("files", {}).values():
                    if element_type == "functions":
                        original_count += len(file_data.get("functions", []))
                    elif element_type == "structs":
                        original_count += len(file_data.get("structs", {}))
                    elif element_type == "enums":
                        original_count += len(file_data.get("enums", {}))
                    # Add more element types as needed
                
                # Calculate transformed count
                transformed_count = 0
                for file_data in transformed_model.get("files", {}).values():
                    if element_type == "functions":
                        transformed_count += len(file_data.get("functions", []))
                    elif element_type == "structs":
                        transformed_count += len(file_data.get("structs", {}))
                    elif element_type == "enums":
                        transformed_count += len(file_data.get("enums", {}))
                
                expected_final_count = original_count - expected_reduction
                if transformed_count != expected_final_count:
                    raise AssertionError(
                        f"Expected {expected_final_count} {element_type} after transformation "
                        f"(original: {original_count}, reduction: {expected_reduction}), "
                        f"got {transformed_count}"
                    )
    
    # =====================================================
    # GENERATOR VALIDATION METHODS (For generator/PlantUML tests)
    # =====================================================
    
    def validate_generator_output_exists(self, output_dir: str, min_puml_files: int = 1) -> List[str]:
        """
        Validate that generator created PlantUML files
        
        Recommendation: Use this as the first validation for generator tests.
        
        Args:
            output_dir: Output directory to check
            min_puml_files: Minimum number of .puml files expected
            
        Returns:
            List of paths to .puml files
        """
        return self.output_validator.assert_puml_files_exist(output_dir, min_puml_files)
    
    def validate_plantuml_syntax(self, puml_files: Dict[str, str]) -> None:
        """
        Validate that all PlantUML files have valid syntax
        
        Recommendation: Use this for all generator tests to ensure valid PlantUML output.
        
        Args:
            puml_files: Dictionary mapping PlantUML filenames to their content
        """
        self.puml_validator.assert_puml_start_end_tags_multi(puml_files)
    
    def validate_plantuml_contains_elements(self, puml_files: Dict[str, str], elements: List[str]) -> None:
        """
        Validate that PlantUML files contain expected elements
        
        Recommendation: Use this for generator tests that verify specific elements appear in diagrams.
        
        Args:
            puml_files: Dictionary mapping PlantUML filenames to their content
            elements: List of element names that should appear in at least one diagram
        """
        for element in elements:
            self.puml_validator.assert_puml_contains_multi(puml_files, element)
    
    def validate_plantuml_excludes_elements(self, puml_files: Dict[str, str], forbidden_elements: List[str]) -> None:
        """
        Validate that PlantUML files don't contain forbidden elements
        
        Recommendation: Use this for generator tests that verify specific elements are excluded from diagrams.
        
        Args:
            puml_files: Dictionary mapping PlantUML filenames to their content
            forbidden_elements: List of element names that should NOT appear in any diagram
        """
        for element in forbidden_elements:
            self.puml_validator.assert_puml_not_contains_multi(puml_files, element)
    
    def validate_plantuml_classes(self, puml_files: Dict[str, str], expected_classes: List[str],
                                expected_total_classes: int = None) -> None:
        """
        Validate PlantUML class definitions
        
        Recommendation: Use this for generator tests that focus on class generation.
        
        Args:
            puml_files: Dictionary mapping PlantUML filenames to their content
            expected_classes: List of class names that should exist
            expected_total_classes: Expected total number of classes across all files
        """
        for class_name in expected_classes:
            self.puml_validator.assert_puml_class_exists_multi(puml_files, class_name)
        
        if expected_total_classes is not None:
            self.puml_validator.assert_puml_class_count_multi(puml_files, expected_total_classes)
    
    def validate_plantuml_relationships(self, puml_files: Dict[str, str], expected_relationships: List[Dict],
                                      expected_total_relationships: int = None) -> None:
        """
        Validate PlantUML relationships
        
        Recommendation: Use this for generator tests that focus on relationship generation.
        
        Args:
            puml_files: Dictionary mapping PlantUML filenames to their content
            expected_relationships: List of relationship dictionaries with 'source', 'target', 'type'
            expected_total_relationships: Expected total number of relationships across all files
        """
        for rel in expected_relationships:
            source = rel.get('source')
            target = rel.get('target')
            rel_type = rel.get('type')
            if source and target and rel_type:
                self.puml_validator.assert_puml_relationship_multi(puml_files, source, target, rel_type)
        
        if expected_total_relationships is not None:
            self.puml_validator.assert_puml_relationship_count_multi(puml_files, expected_total_relationships)
    
    def validate_plantuml_file_content(self, puml_content: str, expected_lines: List[str] = None,
                                     forbidden_lines: List[str] = None) -> None:
        """
        Validate specific content in a single PlantUML file
        
        Recommendation: Use this for generator tests that need to verify specific PlantUML formatting.
        
        Args:
            puml_content: Content of a single PlantUML file
            expected_lines: List of lines that should be present
            forbidden_lines: List of lines that should NOT be present
        """
        if expected_lines:
            self.puml_validator.assert_puml_contains_lines(puml_content, expected_lines)
        
        if forbidden_lines:
            for forbidden_line in forbidden_lines:
                self.puml_validator.assert_puml_not_contains(puml_content, forbidden_line)
    
    # =====================================================
    # CLI EXECUTION VALIDATION METHODS (For all test types)
    # =====================================================
    
    def validate_successful_execution(self, cli_result: CLIResult, expected_stdout: str = None) -> None:
        """
        Validate that CLI execution was successful
        
        Recommendation: Use this for all tests as a basic execution validation.
        
        Args:
            cli_result: CLI execution result
            expected_stdout: Optional expected text in stdout
        """
        self.cli_validator.assert_cli_success(cli_result)
        
        if expected_stdout:
            self.cli_validator.assert_cli_stdout_contains(cli_result, expected_stdout)
    
    def validate_failed_execution(self, cli_result: CLIResult, expected_error: str = None) -> None:
        """
        Validate that CLI execution failed as expected
        
        Recommendation: Use this for error handling tests.
        
        Args:
            cli_result: CLI execution result
            expected_error: Optional expected error message
        """
        self.cli_validator.assert_cli_failure(cli_result, expected_error)
    
    def validate_execution_performance(self, cli_result: CLIResult, max_time: float) -> None:
        """
        Validate that CLI execution completed within time limit
        
        Recommendation: Use this for performance tests.
        
        Args:
            cli_result: CLI execution result
            max_time: Maximum allowed execution time in seconds
        """
        self.cli_validator.assert_cli_execution_time_under(cli_result, max_time)
    
    # =====================================================
    # FILE SYSTEM VALIDATION METHODS (For all test types)
    # =====================================================
    
    def validate_output_files_exist(self, output_dir: str, expected_files: List[str]) -> None:
        """
        Validate that expected output files were created
        
        Recommendation: Use this to verify all expected outputs were generated.
        
        Args:
            output_dir: Output directory to check
            expected_files: List of filenames that should exist
        """
        self.output_validator.assert_output_dir_exists(output_dir)
        
        for filename in expected_files:
            file_path = os.path.join(output_dir, filename)
            self.output_validator.assert_file_exists(file_path)
    
    def validate_json_files_valid(self, output_dir: str, json_files: List[str] = None) -> None:
        """
        Validate that JSON files contain valid JSON
        
        Recommendation: Use this for tests that generate JSON outputs.
        
        Args:
            output_dir: Output directory containing JSON files
            json_files: List of JSON filenames to validate (defaults to model.json and model_transformed.json)
        """
        if json_files is None:
            json_files = ["model.json", "model_transformed.json"]
        
        for filename in json_files:
            file_path = os.path.join(output_dir, filename)
            if os.path.exists(file_path):  # Only validate if file exists
                self.file_validator.assert_json_valid(file_path)
    
    def validate_file_encoding(self, file_path: str) -> None:
        """
        Validate that a file has valid UTF-8 encoding
        
        Recommendation: Use this for tests that verify output file quality.
        
        Args:
            file_path: Path to file to validate
        """
        self.file_validator.assert_file_valid_utf8(file_path)
    
    # =====================================================
    # COMPREHENSIVE VALIDATION METHODS (For complete workflow tests)
    # =====================================================
    
    def validate_complete_parsing_workflow(self, output_dir: str, model_data: Dict, 
                                        expected_files: List[str], expected_elements: Dict[str, List[str]]) -> None:
        """
        Validate complete parsing workflow from input to model output
        
        Recommendation: Use this for comprehensive parser integration tests.
        
        Args:
            output_dir: Output directory
            model_data: Parsed model.json content
            expected_files: List of files that should be parsed
            expected_elements: Dictionary mapping element types to expected element lists
                             (e.g., {'functions': ['main', 'helper'], 'structs': ['Person']})
        """
        # Validate output exists
        self.validate_parser_output_exists(output_dir)
        
        # Validate project structure
        self.validate_parser_project_structure(model_data, expected_files=expected_files)
        
        # Validate specific elements
        if 'functions' in expected_elements:
            self.validate_c_functions_parsed(model_data, expected_elements['functions'])
        
        if 'structs' in expected_elements:
            self.validate_c_structures_parsed(model_data, structs=expected_elements['structs'])
        
        if 'enums' in expected_elements:
            self.validate_c_structures_parsed(model_data, enums=expected_elements['enums'])
        
        if 'globals' in expected_elements:
            self.validate_c_globals_parsed(model_data, expected_elements['globals'])
        
        if 'includes' in expected_elements:
            self.validate_c_includes_parsed(model_data, expected_elements['includes'])
        
        if 'macros' in expected_elements:
            self.validate_c_macros_parsed(model_data, expected_elements['macros'])
    
    def validate_complete_generation_workflow(self, output_dir: str, puml_files: Dict[str, str],
                                           expected_elements: List[str], expected_classes: int = None,
                                           expected_relationships: int = None) -> None:
        """
        Validate complete generation workflow from model to PlantUML output
        
        Recommendation: Use this for comprehensive generator integration tests.
        
        Args:
            output_dir: Output directory
            puml_files: Dictionary mapping PlantUML filenames to their content
            expected_elements: List of elements that should appear in diagrams
            expected_classes: Expected total number of classes
            expected_relationships: Expected total number of relationships
        """
        # Validate output exists
        self.validate_generator_output_exists(output_dir)
        
        # Validate syntax
        self.validate_plantuml_syntax(puml_files)
        
        # Validate content
        self.validate_plantuml_contains_elements(puml_files, expected_elements)
        
        # Validate structure
        if expected_classes is not None:
            self.puml_validator.assert_puml_class_count_multi(puml_files, expected_classes)
        
        if expected_relationships is not None:
            self.puml_validator.assert_puml_relationship_count_multi(puml_files, expected_relationships)
    
    # =====================================================
    # PRIVATE METHODS (Original YAML processing - preserved for backward compatibility)
    # =====================================================
    
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