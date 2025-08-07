#!/usr/bin/env python3
"""
Assertion Processor for the unified testing framework

This module provides the AssertionProcessor class that handles processing
of assertions from YAML test data.
"""

from typing import Dict, Optional
from .validators import ModelValidator, PlantUMLValidator
from .executor import CLIResult


class AssertionProcessor:
    """
    Processes assertions from YAML data and applies them to test results
    
    This class handles the processing of assertions defined in YAML test files
    and applies them to actual test results using the appropriate validators.
    """
    
    def __init__(self):
        """Initialize the assertion processor with validators"""
        self.model_validator = ModelValidator()
        self.puml_validator = PlantUMLValidator()
    
    def process_assertions(self, assertions: Dict, model_data: Optional[Dict] = None, 
                          puml_content: Optional[str] = None, result: Optional[CLIResult] = None,
                          test_case=None) -> None:
        """
        Process assertions from YAML data and apply them to test results
        
        Args:
            assertions: Dictionary loaded from YAML assertions section
            model_data: Optional model data from model.json
            puml_content: Optional PlantUML content
            result: Optional CLIResult from execution
            test_case: Optional test case instance for assertions (unittest.TestCase)
        """
        if not assertions:
            return
        
        # Process execution assertions
        if "execution" in assertions and result and test_case:
            self._process_execution_assertions(assertions["execution"], result, test_case)
        
        # Process model validation assertions
        if "model" in assertions and model_data and test_case:
            self._process_model_assertions(assertions["model"], model_data, test_case)
        
        # Process PlantUML validation assertions
        if "puml" in assertions and puml_content and test_case:
            self._process_puml_assertions(assertions["puml"], puml_content, test_case)
    
    def _process_execution_assertions(self, execution_expected: Dict, result: CLIResult, test_case) -> None:
        """Process execution-related assertions"""
        if "exit_code" in execution_expected:
            test_case.assertEqual(
                result.exit_code, 
                execution_expected["exit_code"],
                f"Expected exit code {execution_expected['exit_code']}, got {result.exit_code}"
            )
    
    def _process_model_assertions(self, model_expected: Dict, model_data: Dict, test_case) -> None:
        """Process model validation assertions"""
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
                                self.model_validator.assert_model_struct_fields(
                                    model_data, struct_name, struct_expected["fields"]
                                )
                    
                    # Validate enums
                    if "enums" in file_expected:
                        for enum_name, enum_expected in file_expected["enums"].items():
                            self.model_validator.assert_model_enum_exists(model_data, enum_name)
                            if "values" in enum_expected:
                                self.model_validator.assert_model_enum_values(
                                    model_data, enum_name, enum_expected["values"]
                                )
                    
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
    
    def _process_puml_assertions(self, puml_expected: Dict, puml_content: str, test_case) -> None:
        """Process PlantUML validation assertions"""
        # Validate required elements
        if "contains_elements" in puml_expected:
            for element_name in puml_expected["contains_elements"]:
                self.puml_validator.assert_puml_contains(puml_content, element_name)
        
        # Validate syntax
        if puml_expected.get("syntax_valid", False):
            self.puml_validator.assert_puml_start_end_tags(puml_content)