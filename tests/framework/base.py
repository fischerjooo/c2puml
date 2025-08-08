#!/usr/bin/env python3
"""
Unified Test Case Base Class

This module provides the UnifiedTestCase base class that all c2puml tests
should inherit from, providing common setup, teardown, and component initialization.
"""

import os
import sys
import unittest
import tempfile
import json
import shutil
from typing import Dict, Any, List

from .executor import TestExecutor, CLIResult
from .data_loader import TestDataLoader
from .validators_processor import ValidatorsProcessor
from .validators import ModelValidator, PlantUMLValidator, OutputValidator, FileValidator, CLIValidator


class TestResult:
    """Result object containing test execution results and metadata"""
    def __init__(self, cli_result: CLIResult, test_dir: str, output_dir: str, model_file: str = None, puml_files: List[str] = None):
        self.cli_result = cli_result
        self.test_dir = test_dir
        self.output_dir = output_dir
        self.model_file = model_file
        self.puml_files = puml_files or []


class UnifiedTestCase(unittest.TestCase):
    """
    Base class for all tests using the unified testing framework.
    
    This class provides:
    - Automatic setup of TestExecutor, TestDataLoader, and validators
    - Component initialization for all framework components
    - Standardized test output management
    - Integration with the unified testing framework components
    - High-level convenience methods for common test patterns
    - Enhanced validator access with meaningful names organized by validation type
    """
    
    def setUp(self):
        """Set up test environment"""
        # Initialize framework components
        self.executor = TestExecutor()
        self.data_loader = TestDataLoader()
        self.validators_processor = ValidatorsProcessor()
        
        # Initialize validators
        self.model_validator = ModelValidator()
        self.puml_validator = PlantUMLValidator()
        self.output_validator = OutputValidator()
        self.file_validator = FileValidator()
        self.cli_validator = CLIValidator()
        
        # Clean up any existing test folders to ensure clean slate
        self._cleanup_existing_test_folders()
        
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Test metadata
        self.test_name = self.__class__.__name__
        self.test_method = self._testMethodName
    
    def tearDown(self):
        """Clean up after each test"""
        # Note: temp_dir is NOT automatically cleaned to preserve output for debugging
        pass

    def run_test(self, test_id: str) -> TestResult:
        """
        Run a complete test and return results.
        
        This high-level method encapsulates the common test pattern:
        1. Load test data from YAML
        2. Create temporary files
        3. Execute c2puml
        4. Validate outputs
        5. Return comprehensive results
        
        Args:
            test_id: The test identifier (used for YAML file name and temp folder)
            
        Returns:
            TestResult: Object containing all test execution results and metadata
        """
        # Load test data from YAML
        test_data = self.data_loader.load_test_data(test_id)
        
        # Create temporary files
        source_dir, config_path = self.data_loader.create_temp_files(test_data, test_id)
        
        # Calculate paths
        test_folder = os.path.dirname(source_dir)  # input/ folder
        temp_dir = os.path.dirname(test_folder)    # test-name/ folder
        config_filename = os.path.basename(config_path)
        
        # Execute c2puml with temp directory as working directory
        result = self.executor.run_full_pipeline(config_filename, temp_dir)
        
        # Load output files
        output_dir = os.path.join(temp_dir, "output")
        model_file = self.output_validator.assert_model_file_exists(output_dir)
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        
        return TestResult(result, temp_dir, output_dir, model_file, puml_files)

    def validate_execution_success(self, result: TestResult):
        """
        Assert test execution was successful.
        
        Args:
            result: TestResult object from run_test()
        """
        self.cli_validator.assert_cli_success(result.cli_result)

    def validate_test_output(self, result: TestResult):
        """
        Validate all test outputs using assertions from YAML.
        
        Args:
            result: TestResult object from run_test()
        """
        # Load test data to get assertions
        test_id = os.path.basename(result.test_dir).replace('test-', '')
        test_data = self.data_loader.load_test_data(test_id)
        
        # Load content for validation
        with open(result.model_file, 'r') as f:
            model_data = json.load(f)
        
        # Load all PlantUML files into a dictionary
        puml_files = {}
        for puml_file_path in result.puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files[filename] = f.read()
        
        # Process assertions from YAML
        self.validators_processor.process_assertions(
            test_data["assertions"], model_data, puml_files, result.cli_result, self
        )

    # =====================================================
    # ENHANCED VALIDATOR ACCESS METHODS
    # =====================================================
    # These methods provide convenient access to the enhanced validation framework
    # with meaningful names, organized by validation type for improved test development.
    
    # Parser Validation Methods
    def validate_parser_output_exists(self, output_dir: str) -> str:
        """Validate that parser generated a model.json file"""
        return self.validators_processor.validate_parser_output_exists(output_dir)
    
    def validate_parser_project_structure(self, model_data: Dict, project_name: str = None, 
                                        expected_files: List[str] = None) -> None:
        """Validate basic parser output structure"""
        return self.validators_processor.validate_parser_project_structure(
            model_data, project_name, expected_files
        )
    
    def validate_c_structures_parsed(self, model_data: Dict, structs: List[str] = None, 
                                   enums: List[str] = None, unions: List[str] = None,
                                   typedefs: List[str] = None) -> None:
        """Validate that C structures were correctly parsed"""
        return self.validators_processor.validate_c_structures_parsed(
            model_data, structs, enums, unions, typedefs
        )
    
    def validate_c_functions_parsed(self, model_data: Dict, functions: List[str]) -> None:
        """Validate that C functions were correctly parsed"""
        return self.validators_processor.validate_c_functions_parsed(model_data, functions)
    
    def validate_c_globals_parsed(self, model_data: Dict, globals_list: List[str]) -> None:
        """Validate that global variables were correctly parsed"""
        return self.validators_processor.validate_c_globals_parsed(model_data, globals_list)
    
    def validate_c_includes_parsed(self, model_data: Dict, includes: List[str]) -> None:
        """Validate that include statements were correctly parsed"""
        return self.validators_processor.validate_c_includes_parsed(model_data, includes)
    
    def validate_c_macros_parsed(self, model_data: Dict, macros: List[str]) -> None:
        """Validate that macros were correctly parsed"""
        return self.validators_processor.validate_c_macros_parsed(model_data, macros)
    
    def validate_struct_details(self, model_data: Dict, struct_name: str, expected_fields: List[str]) -> None:
        """Validate detailed structure of a parsed struct"""
        return self.validators_processor.validate_struct_details(model_data, struct_name, expected_fields)
    
    def validate_enum_details(self, model_data: Dict, enum_name: str, expected_values: List[str]) -> None:
        """Validate detailed structure of a parsed enum"""
        return self.validators_processor.validate_enum_details(model_data, enum_name, expected_values)
    
    def validate_parsing_element_counts(self, model_data: Dict, expected_counts: Dict[str, int]) -> None:
        """Validate element counts across all parsed files"""
        return self.validators_processor.validate_parsing_element_counts(model_data, expected_counts)
    
    # Transformer Validation Methods
    def validate_transformer_output_exists(self, output_dir: str) -> str:
        """Validate that transformer generated a model_transformed.json file"""
        return self.validators_processor.validate_transformer_output_exists(output_dir)
    
    def validate_elements_removed(self, model_data: Dict, removed_functions: List[str] = None,
                                removed_structs: List[str] = None, removed_enums: List[str] = None) -> None:
        """Validate that specific elements were removed during transformation"""
        return self.validators_processor.validate_elements_removed(
            model_data, removed_functions, removed_structs, removed_enums
        )
    
    def validate_elements_preserved(self, model_data: Dict, preserved_functions: List[str] = None,
                                  preserved_structs: List[str] = None, preserved_enums: List[str] = None) -> None:
        """Validate that specific elements were preserved during transformation"""
        return self.validators_processor.validate_elements_preserved(
            model_data, preserved_functions, preserved_structs, preserved_enums
        )
    
    def validate_transformation_counts(self, original_model: Dict, transformed_model: Dict,
                                     expected_reductions: Dict[str, int] = None) -> None:
        """Validate that element counts changed as expected during transformation"""
        return self.validators_processor.validate_transformation_counts(
            original_model, transformed_model, expected_reductions
        )
    
    # Generator Validation Methods
    def validate_generator_output_exists(self, output_dir: str, min_puml_files: int = 1) -> List[str]:
        """Validate that generator created PlantUML files"""
        return self.validators_processor.validate_generator_output_exists(output_dir, min_puml_files)
    
    def validate_plantuml_syntax(self, puml_files: Dict[str, str]) -> None:
        """Validate that all PlantUML files have valid syntax"""
        return self.validators_processor.validate_plantuml_syntax(puml_files)
    
    def validate_plantuml_contains_elements(self, puml_files: Dict[str, str], elements: List[str]) -> None:
        """Validate that PlantUML files contain expected elements"""
        return self.validators_processor.validate_plantuml_contains_elements(puml_files, elements)
    
    def validate_plantuml_excludes_elements(self, puml_files: Dict[str, str], forbidden_elements: List[str]) -> None:
        """Validate that PlantUML files don't contain forbidden elements"""
        return self.validators_processor.validate_plantuml_excludes_elements(puml_files, forbidden_elements)
    
    def validate_plantuml_classes(self, puml_files: Dict[str, str], expected_classes: List[str],
                                expected_total_classes: int = None) -> None:
        """Validate PlantUML class definitions"""
        return self.validators_processor.validate_plantuml_classes(
            puml_files, expected_classes, expected_total_classes
        )
    
    def validate_plantuml_relationships(self, puml_files: Dict[str, str], expected_relationships: List[Dict],
                                      expected_total_relationships: int = None) -> None:
        """Validate PlantUML relationships"""
        return self.validators_processor.validate_plantuml_relationships(
            puml_files, expected_relationships, expected_total_relationships
        )
    
    def validate_plantuml_file_content(self, puml_content: str, expected_lines: List[str] = None,
                                     forbidden_lines: List[str] = None) -> None:
        """Validate specific content in a single PlantUML file"""
        return self.validators_processor.validate_plantuml_file_content(
            puml_content, expected_lines, forbidden_lines
        )
    
    # CLI Execution Validation Methods
    def validate_successful_execution(self, cli_result: CLIResult, expected_stdout: str = None) -> None:
        """Validate that CLI execution was successful"""
        return self.validators_processor.validate_successful_execution(cli_result, expected_stdout)
    
    def validate_failed_execution(self, cli_result: CLIResult, expected_error: str = None) -> None:
        """Validate that CLI execution failed as expected"""
        return self.validators_processor.validate_failed_execution(cli_result, expected_error)
    
    def validate_execution_performance(self, cli_result: CLIResult, max_time: float) -> None:
        """Validate that CLI execution completed within time limit"""
        return self.validators_processor.validate_execution_performance(cli_result, max_time)
    
    # File System Validation Methods
    def validate_output_files_exist(self, output_dir: str, expected_files: List[str]) -> None:
        """Validate that expected output files were created"""
        return self.validators_processor.validate_output_files_exist(output_dir, expected_files)
    
    def validate_json_files_valid(self, output_dir: str, json_files: List[str] = None) -> None:
        """Validate that JSON files contain valid JSON"""
        return self.validators_processor.validate_json_files_valid(output_dir, json_files)
    
    def validate_file_encoding(self, file_path: str) -> None:
        """Validate that a file has valid UTF-8 encoding"""
        return self.validators_processor.validate_file_encoding(file_path)
    
    # Comprehensive Validation Methods
    def validate_complete_parsing_workflow(self, output_dir: str, model_data: Dict, 
                                        expected_files: List[str], expected_elements: Dict[str, List[str]]) -> None:
        """Validate complete parsing workflow from input to model output"""
        return self.validators_processor.validate_complete_parsing_workflow(
            output_dir, model_data, expected_files, expected_elements
        )
    
    def validate_complete_generation_workflow(self, output_dir: str, puml_files: Dict[str, str],
                                           expected_elements: List[str], expected_classes: int = None,
                                           expected_relationships: int = None) -> None:
        """Validate complete generation workflow from model to PlantUML output"""
        return self.validators_processor.validate_complete_generation_workflow(
            output_dir, puml_files, expected_elements, expected_classes, expected_relationships
        )

    def _cleanup_existing_test_folders(self):
        """Clean up any existing test-* folders in test directories"""
        test_categories = ['unit', 'feature', 'integration', 'example']
        
        for category in test_categories:
            category_path = os.path.join(os.path.dirname(__file__), '..', category)
            if os.path.exists(category_path):
                for item in os.listdir(category_path):
                    item_path = os.path.join(category_path, item)
                    if os.path.isdir(item_path) and item.startswith('test-'):
                        try:
                            import shutil
                            shutil.rmtree(item_path)
                        except Exception as e:
                            # Log warning but don't fail the test
                            print(f"Warning: Could not clean up {item_path}: {e}")