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
from typing import Dict, Any, List, Tuple

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
        test_dir = os.path.dirname(test_folder)    # test-###/ folder
        config_filename = os.path.basename(config_path)
        
        # Execute c2puml
        result = self.executor.run_full_pipeline(config_filename, test_folder)
        
        # Validate outputs
        output_dir = os.path.join(test_dir, "output")
        model_file = self.output_validator.assert_model_file_exists(output_dir)
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        
        return TestResult(result, test_dir, output_dir, model_file, puml_files)

    def validate_execution_success(self, result: TestResult):
        """
        Assert that test execution was successful.
        
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

    # --- Helper methods to reduce duplication in CLI feature/mode tests ---

    def prepare_test_environment(self, test_id: str) -> Tuple[Dict[str, Any], str, str, str, str, str]:
        """Load YAML, create files, and return handy paths.
        
        Returns tuple: (test_data, source_dir, config_filename, test_folder, test_dir, output_dir)
        """
        test_data = self.data_loader.load_test_data(test_id)
        source_dir, config_path = self.data_loader.create_temp_files(test_data, test_id)
        test_folder = os.path.dirname(source_dir)
        test_dir = os.path.dirname(test_folder)
        config_filename = os.path.basename(config_path)
        output_dir = os.path.join(test_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        return test_data, source_dir, config_filename, test_folder, test_dir, output_dir

    def normalize_file_assertions_paths(self, assertions: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """Convert relative ./output paths in file assertions to absolute paths under output_dir."""
        if not assertions:
            return {}
        # Deep copy without importing copy at top-level each time
        import copy as _copy
        normalized = _copy.deepcopy(assertions)
        files_section = normalized.get("files")
        if not files_section:
            return normalized
        
        def _fix_path(path: str) -> str:
            if not isinstance(path, str):
                return path
            if path == "./output" or path == "./output/":
                return output_dir
            if path.startswith("./output/"):
                return os.path.join(output_dir, path[len("./output/"):])
            return path
        
        # Keys containing lists of paths
        for key in ("files_exist", "files_not_exist", "json_files_valid", "utf8_files"):
            if key in files_section and isinstance(files_section[key], list):
                files_section[key] = [_fix_path(p) for p in files_section[key]]
        
        # Single path fields
        if "output_dir_exists" in files_section:
            files_section["output_dir_exists"] = _fix_path(files_section["output_dir_exists"]) or output_dir
        
        # file_content maps file->assertions; rewrite keys
        if "file_content" in files_section and isinstance(files_section["file_content"], dict):
            new_map = {}
            for file_path, content_assertions in files_section["file_content"].items():
                new_map[_fix_path(file_path)] = content_assertions
            files_section["file_content"] = new_map
        
        return normalized


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