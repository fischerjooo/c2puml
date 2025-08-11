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

    def _get_steps_from_metadata(self, test_data: Dict[str, Any]) -> List[str]:
        meta = test_data.get("test", {}) or {}
        steps = meta.get("steps")
        if steps:
            # Normalize to list of lower-case strings
            steps = [str(s).strip().lower() for s in steps]
        else:
            steps = ["parse", "transform", "generate"]
        # Basic validation
        valid = {"parse", "transform", "generate"}
        if any(s not in valid for s in steps):
            raise ValueError(f"Unsupported steps in test metadata: {steps}")
        return steps

    def _ensure_model_for_partial_pipeline(self, source_dir: str, output_dir: str) -> None:
        os.makedirs(output_dir, exist_ok=True)
        src_model = os.path.join(source_dir, "model.json")
        dst_model = os.path.join(output_dir, "model.json")
        if os.path.exists(src_model):
            shutil.copy2(src_model, dst_model)

    def run_test(self, test_id: str) -> TestResult:
        """
        Run a test according to YAML metadata and return results.
        
        This method now supports partial pipelines defined in YAML metadata:
        test.steps: ["parse"|"transform"|"generate" ...]
        Defaults to full pipeline [parse, transform, generate].
        """
        # Load test data from YAML
        test_data = self.data_loader.load_test_data(test_id)
        steps = self._get_steps_from_metadata(test_data)
        
        # Create temporary files
        source_dir, config_path = self.data_loader.create_temp_files(test_data, test_id)
        
        # Calculate paths
        test_folder = os.path.dirname(source_dir)  # input/ folder
        test_dir = os.path.dirname(test_folder)    # test-###/ folder
        output_dir = os.path.join(test_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        config_filename = os.path.basename(config_path)
        
        # Execute according to steps
        cli_result: CLIResult
        if steps == ["parse", "transform", "generate"]:
            cli_result = self.executor.run_full_pipeline(config_filename, test_folder)
        elif steps == ["parse"]:
            cli_result = self.executor.run_parse_only(config_filename, test_folder)
        elif steps == ["transform"]:
            self._ensure_model_for_partial_pipeline(source_dir, output_dir)
            cli_result = self.executor.run_transform_only(config_filename, test_folder)
        elif steps == ["generate"]:
            self._ensure_model_for_partial_pipeline(source_dir, output_dir)
            cli_result = self.executor.run_generate_only(config_filename, test_folder)
        elif steps == ["parse", "transform"]:
            r1 = self.executor.run_parse_only(config_filename, test_folder)
            self.cli_validator.assert_cli_success(r1)
            cli_result = self.executor.run_transform_only(config_filename, test_folder)
        elif steps == ["transform", "generate"]:
            self._ensure_model_for_partial_pipeline(source_dir, output_dir)
            r1 = self.executor.run_transform_only(config_filename, test_folder)
            self.cli_validator.assert_cli_success(r1)
            cli_result = self.executor.run_generate_only(config_filename, test_folder)
        else:
            raise ValueError(f"Unsupported steps sequence: {steps}")
        
        # Collect outputs based on last step
        last = steps[-1]
        model_file = None
        puml_files: List[str] = []
        if last == "generate":
            # Generate produces PUML files; also ensure model.json is available for validation
            model_file = os.path.join(output_dir, "model.json")
            if os.path.exists(model_file):
                self.output_validator.assert_file_exists(model_file)
            puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        elif last == "transform":
            model_file = os.path.join(output_dir, "model_transformed.json")
            self.output_validator.assert_file_exists(model_file)
        elif last == "parse":
            model_file = os.path.join(output_dir, "model.json")
            self.output_validator.assert_file_exists(model_file)
        
        return TestResult(cli_result, test_dir, output_dir, model_file, puml_files)

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
        meta = test_data.get("test", {}) or {}
        steps = meta.get("steps") or ["parse", "transform", "generate"]
        last = steps[-1] if steps else "generate"
        
        # Load content for validation
        model_data: Dict[str, Any] = {}
        # Prefer transformed model if present when validating
        transformed_path = os.path.join(result.output_dir, "model_transformed.json")
        candidate_model = None
        if os.path.exists(transformed_path):
            candidate_model = transformed_path
        elif result.model_file and os.path.exists(result.model_file):
            candidate_model = result.model_file
        if candidate_model:
            with open(candidate_model, 'r') as f:
                model_data = json.load(f)
        
        # Expose paths for validators to normalize relative file assertions
        self.current_validation_base_dir = result.test_dir
        self.current_validation_output_dir = result.output_dir

        # Load all PlantUML files into a dictionary
        puml_files: Dict[str, str] = {}
        for puml_file_path in result.puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files[filename] = f.read()
        
        # Process assertions from YAML
        self.validators_processor.process_assertions(
            test_data["assertions"], model_data, puml_files, result.cli_result, self
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