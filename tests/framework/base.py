#!/usr/bin/env python3
"""
Unified Test Case Base Class

This module provides the UnifiedTestCase base class that all c2puml tests
should inherit from, providing common setup, teardown, and utility methods.
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
from .assertion_processor import AssertionProcessor
from .validators import ModelValidator, PlantUMLValidator, OutputValidator, FileValidator


class UnifiedTestCase(unittest.TestCase):
    """
    Base class for all tests using the unified testing framework.
    
    This class provides:
    - Automatic setup of TestExecutor, TestInputFactory, and validators
    - Common test utilities and helper methods
    - Standardized test output management
    - Integration with the unified testing framework components
    """
    
    def setUp(self):
        """Set up test environment"""
        # Initialize framework components
        self.executor = TestExecutor()
        self.data_loader = TestDataLoader()
        self.assertion_processor = AssertionProcessor()
        
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
    
    def tearDown(self):
        """Clean up after each test"""
        # Note: temp_dir is NOT automatically cleaned to preserve output for debugging
        pass
    
    # === Input Factory Helpers ===
    
    def create_test_config(self, config_data: Dict[str, Any], temp_dir: str = None) -> str:
        """
        Create a test configuration file
        
        Args:
            config_data: Configuration data dictionary
            temp_dir: Temporary directory (defaults to self.temp_dir)
            
        Returns:
            Path to the created config.json file
        """
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
        
        # Create the config file directly without going through input_factory
        config_path = os.path.join(temp_dir, "config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return config_path
    
    def create_test_source_files(self, source_files: Dict[str, str], temp_dir: str = None) -> str:
        """
        Create test source files
        
        Args:
            source_files: Dictionary mapping filenames to content
            temp_dir: Temporary directory (defaults to self.temp_dir)
            
        Returns:
            Path to the directory containing source files
        """
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
    
    def create_test_input_data(self, source_files: Dict[str, str], 
                              config_overrides: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create complete test input data structure
        
        Args:
            source_files: Dictionary mapping filenames to content
            config_overrides: Optional configuration overrides
            
        Returns:
            Complete input data dictionary
        """
        config = {
            "project_name": f"{self.test_name}_{self.test_method}",
            "source_folders": ["."],
            "output_dir": self.output_dir,
            "recursive_search": True
        }
        
        if config_overrides:
            config.update(config_overrides)
        
        return {
            "test_metadata": {
                "description": f"Test {self.test_name}.{self.test_method}",
                "test_type": "unit"
            },
            "c2puml_config": config,
            "source_files": source_files
        }
    
    # === Validation Helpers ===
    
    def assert_c2puml_success(self, result: CLIResult, message: str = None) -> None:
        """
        Assert that c2puml execution was successful
        
        Args:
            result: CLIResult from c2puml execution
            message: Optional custom error message
        """
        if message is None:
            message = f"c2puml execution failed with exit code {result.exit_code}"
        
        self.assertEqual(result.exit_code, 0, f"{message}\nstdout: {result.stdout}\nstderr: {result.stderr}")
    
    def assert_c2puml_failure(self, result: CLIResult, expected_error: str = None, message: str = None) -> None:
        """
        Assert that c2puml execution failed
        
        Args:
            result: CLIResult from c2puml execution
            expected_error: Optional expected error message to check for
            message: Optional custom error message
        """
        if message is None:
            message = "Expected c2puml to fail but it succeeded"
        
        self.assertNotEqual(result.exit_code, 0, message)
        
        if expected_error:
            self.assertIn(expected_error, result.stderr, 
                         f"Expected error '{expected_error}' not found in stderr: {result.stderr}")
    
    def assert_model_file_exists(self, output_dir: str = None) -> str:
        """
        Assert that model.json file exists and return its path
        
        Args:
            output_dir: Output directory to check (defaults to self.output_dir)
            
        Returns:
            Path to the model.json file
        """
        if output_dir is None:
            output_dir = self.output_dir
        
        model_file = os.path.join(output_dir, "model.json")
        self.assertTrue(os.path.exists(model_file), f"model.json not found in {output_dir}")
        return model_file
    
    def assert_transformed_model_file_exists(self, output_dir: str = None) -> str:
        """
        Assert that model_transformed.json file exists and return its path
        
        Args:
            output_dir: Output directory to check (defaults to self.output_dir)
            
        Returns:
            Path to the model_transformed.json file
        """
        if output_dir is None:
            output_dir = self.output_dir
        
        transformed_model_file = os.path.join(output_dir, "model_transformed.json")
        self.assertTrue(os.path.exists(transformed_model_file), 
                       f"model_transformed.json not found in {output_dir}")
        return transformed_model_file
    
    def assert_puml_files_exist(self, output_dir: str = None, min_count: int = 1) -> list:
        """
        Assert that PlantUML files exist and return their paths
        
        Args:
            output_dir: Output directory to check (defaults to self.output_dir)
            min_count: Minimum number of .puml files expected
            
        Returns:
            List of paths to .puml files
        """
        if output_dir is None:
            output_dir = self.output_dir
        
        puml_files = [f for f in os.listdir(output_dir) if f.endswith('.puml')]
        self.assertGreaterEqual(len(puml_files), min_count, 
                               f"Expected at least {min_count} .puml files, found {len(puml_files)}")
        
        return [os.path.join(output_dir, f) for f in puml_files]
    
    def assert_puml_contains_syntax(self) -> None:
        """Assert that the PlantUML output contains proper syntax"""
        puml_files = self.assert_puml_files_exist()
        
        # Check the first .puml file
        with open(puml_files[0], 'r') as f:
            puml_content = f.read()
        
        self.puml_validator.assert_puml_start_end_tags(puml_content)
    
    # === Utility Methods ===
    
    def create_simple_c_struct_test(self, struct_name: str = "TestStruct", 
                                   fields: Dict[str, str] = None) -> str:
        """
        Create a simple C source file with a struct for testing
        
        Args:
            struct_name: Name of the struct
            fields: Dictionary mapping field names to types
            
        Returns:
            C source code string
        """
        if fields is None:
            fields = {"value": "int"}
        
        field_declarations = []
        for field_name, field_type in fields.items():
            field_declarations.append(f"            {field_type} {field_name};")
        
        return f"""
        struct {struct_name} {{
{chr(10).join(field_declarations)}
        }};
        """
    
    def create_simple_c_enum_test(self, enum_name: str = "TestEnum", 
                                 values: list = None) -> str:
        """
        Create a simple C source file with an enum for testing
        
        Args:
            enum_name: Name of the enum
            values: List of enum values
            
        Returns:
            C source code string
        """
        if values is None:
            values = ["VALUE1", "VALUE2", "VALUE3"]
        
        value_declarations = []
        for i, value in enumerate(values):
            if i == 0:
                value_declarations.append(f"            {value} = 0")
            else:
                value_declarations.append(f"            {value}")
        
        return f"""
        enum {enum_name} {{
{chr(10).join(value_declarations)}
        }};
        """