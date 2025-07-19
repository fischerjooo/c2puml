#!/usr/bin/env python3
"""
Test helper for use case tests

This module provides a helper class that uses expectation classes
to run tests with consistent validation across different use cases.
"""

import unittest
import os
import tempfile
from pathlib import Path
from typing import Type
from c_to_plantuml.parser import CParser
from c_to_plantuml.analyzer import Analyzer
from c_to_plantuml.generator import Generator
from c_to_plantuml.config import Config
from c_to_plantuml.models import ProjectModel
from tests.expectations import BaseExpectations


class UseCaseTestHelper:
    """Helper class for running use case tests with expectations"""
    
    def __init__(self, expectations_class: Type[BaseExpectations]):
        """
        Initialize the test helper with a specific expectations class
        
        Args:
            expectations_class: The expectations class to use for validation
        """
        self.expectations = expectations_class()
        self.parser = CParser()
        self.analyzer = Analyzer()
        self.generator = Generator()
    
    def run_basic_analysis_test(self, project_dir: Path, test_case: unittest.TestCase) -> None:
        """Run basic project analysis test using expectations"""
        # Analyze the project
        model = self.analyzer.analyze_project(
            project_root=str(project_dir),
            recursive=True
        )
        
        # Validate using expectations
        self.expectations.validate_project_structure(model)
        self.expectations.validate_file_content(model)
    
    def run_generation_test(self, project_dir: Path, test_case: unittest.TestCase) -> None:
        """Run PlantUML generation test using expectations"""
        # Analyze the project
        model = self.analyzer.analyze_project(
            project_root=str(project_dir),
            recursive=True
        )
        
        # Create output directory
        output_dir = project_dir.parent / "generated_output"
        output_dir.mkdir(exist_ok=True)
        
        # Generate PlantUML
        self.generator.generate_from_project_model(model, str(output_dir))
        
        # Validate using expectations
        self.expectations.validate_generated_output(output_dir)
    
    def run_configuration_test(self, project_dir: Path, config_file: Path, test_case: unittest.TestCase) -> None:
        """Run configuration-based test using expectations"""
        # Change to the configuration directory to handle relative paths
        config_dir = config_file.parent
        original_cwd = os.getcwd()
        
        try:
            os.chdir(str(config_dir))
            
            # Load configuration
            config = Config.load(str(config_file.name))
            
            # Analyze with configuration
            model = self.analyzer.analyze_project(str(project_dir), recursive=True)
            
            # Apply filters manually
            model = config.apply_filters(model)
            
            # Validate using expectations
            self.expectations.validate_project_structure(model)
            self.expectations.validate_file_content(model)
        finally:
            os.chdir(original_cwd)
    
    def run_error_handling_test(self, project_dir: Path, test_case: unittest.TestCase) -> None:
        """Run error handling test using expectations"""
        # Test missing file handling
        self.expectations.validate_missing_file_handling(self.analyzer, project_dir)
        
        # Test partial parsing on errors
        invalid_file = project_dir / "invalid_file.c"
        self.expectations.validate_partial_parsing_on_errors(self.parser, invalid_file)
    
    def run_encoding_test(self, test_case: unittest.TestCase) -> None:
        """Run encoding detection test using expectations"""
        # This test uses a temporary file with specific encoding
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False, encoding='utf-8') as f:
            f.write(self.expectations.create_test_file_content())
            temp_file = f.name
        
        try:
            # Validate using expectations
            self.expectations.validate_encoding_detection_and_recovery(self.parser, temp_file)
        finally:
            os.unlink(temp_file)
    
    def run_integration_test(self, example_dir: Path, test_case: unittest.TestCase) -> None:
        """Run complete integration test using expectations"""
        project_dir = example_dir / "input"
        config_file = example_dir / "config.json"
        
        # Change to the configuration directory to handle relative paths
        original_cwd = os.getcwd()
        
        try:
            os.chdir(str(example_dir))
            
            # Load configuration
            config = Config.load(str(config_file.name))
            
            # Step 1: Analyze project and generate model
            model = self.analyzer.analyze_with_config(config)
        finally:
            os.chdir(original_cwd)
        
        # Validate model structure
        self.expectations.validate_project_structure(model)
        self.expectations.validate_file_content(model)
        
        # Save model
        model_path = example_dir / "test_model.json"
        model.save(str(model_path))
        test_case.assertTrue(model_path.exists())
        
        # Step 3: Generate PlantUML diagrams
        output_dir = example_dir / "test_output"
        self.generator.generate_from_project_model(model, str(output_dir))
        
        # Validate output
        self.expectations.validate_generated_output(output_dir)
        
        # Cleanup
        if model_path.exists():
            model_path.unlink()
        if output_dir.exists():
            import shutil
            shutil.rmtree(output_dir)