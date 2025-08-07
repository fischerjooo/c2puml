#!/usr/bin/env python3
"""
Unified Test Case Base Class

This module provides the UnifiedTestCase base class that all c2puml tests
should inherit from, providing common setup, teardown, and basic assertion methods.
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
    - Automatic setup of TestExecutor, TestDataLoader, and validators
    - Basic assertion methods for common test scenarios
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
    
    # === Basic Assertion Methods ===
    
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