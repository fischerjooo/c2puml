#!/usr/bin/env python3
"""
Test Data Loader for the unified testing framework

This module provides the TestDataLoader class that handles loading
test data from YAML files and creating temporary files for testing.
"""

import os
import yaml
import tempfile
import json
from typing import Dict, Tuple, Optional


class TestDataLoader:
    """
    Loads test data from YAML files and creates temporary files for testing
    
    This class handles the loading of test data defined in test-###.yml
    files and creates temporary source files and configuration files.
    """
    
    def __init__(self):
        """Initialize the test data loader"""
        pass
    
    def load_test_data(self, test_id: str) -> Dict:
        """
        Load test data from test-###.yml file
        
        Args:
            test_id: Test ID (e.g., "simple_c_file_parsing", "complex_struct_parsing")
            
        Returns:
            Dictionary containing test data from YAML file
            
        Raises:
            FileNotFoundError: If YAML file doesn't exist
            yaml.YAMLError: If YAML file is invalid
        """
        # Try to find the YAML file in different test categories
        test_categories = ["unit", "feature", "integration", "example"]
        
        for category in test_categories:
            yaml_file = f"tests/{category}/test_{test_id}.yml"
            if os.path.exists(yaml_file):
                with open(yaml_file, 'r') as f:
                    # Load all YAML documents
                    documents = list(yaml.safe_load_all(f))
                
                # Parse documents into structured test data
                test_data = self._parse_yaml_documents(documents)
                
                # Validate YAML structure
                self._validate_test_data(test_data)
                
                return test_data
        
        # If not found, try with the old numeric format
        try:
            test_num = int(test_id)
            category = self._get_test_category(test_id)
            yaml_file = f"tests/{category}/test-{test_id:03d}.yml"
            
            if os.path.exists(yaml_file):
                with open(yaml_file, 'r') as f:
                    # Load all YAML documents
                    documents = list(yaml.safe_load_all(f))
                
                # Parse documents into structured test data
                test_data = self._parse_yaml_documents(documents)
                
                # Validate YAML structure
                self._validate_test_data(test_data)
                
                return test_data
        except ValueError:
            pass
        
        raise FileNotFoundError(f"Test data file not found for test ID: {test_id}")

    def _parse_yaml_documents(self, documents: list) -> Dict:
        """
        Parse multiple YAML documents into structured test data
        
        Args:
            documents: List of YAML documents
            
        Returns:
            Structured test data dictionary
        """
        test_data = {}
        
        for doc in documents:
            if not doc:  # Skip empty documents
                continue
                
            # Test metadata
            if "test" in doc:
                test_data["test"] = doc["test"]
            
            # Source files
            if "source_files" in doc:
                if "inputs" not in test_data:
                    test_data["inputs"] = {}
                test_data["inputs"]["source_files"] = doc["source_files"]
            
            # Config file
            if "config.json" in doc:
                if "inputs" not in test_data:
                    test_data["inputs"] = {}
                if "source_files" not in test_data["inputs"]:
                    test_data["inputs"]["source_files"] = {}
                test_data["inputs"]["source_files"]["config.json"] = doc["config.json"]
            
            # Model template
            if "model.json" in doc:
                test_data["model_template"] = doc["model.json"]
            
            # Assertions
            if "assertions" in doc:
                test_data["assertions"] = doc["assertions"]
        
        return test_data
    
    def create_temp_files(self, test_data: Dict, test_id: str) -> Tuple[str, str]:
        """
        Create temporary source files and config from YAML data
        
        Args:
            test_data: Test data loaded from YAML file
            test_id: Test ID for creating test-specific temp directory
            
        Returns:
            Tuple of (source_dir_path, config_file_path)
        """
        # Find the test category and create test-specific folder
        test_categories = ["unit", "feature", "integration", "example"]
        test_dir = None
        
        for category in test_categories:
            category_dir = f"tests/{category}"
            if os.path.exists(category_dir):
                # Create test-specific folder: tests/unit/test-001/
                test_dir = os.path.join(category_dir, f"test-{test_id}")
                break
        
        if not test_dir:
            raise ValueError(f"Could not find test directory for test ID: {test_id}")
        
        # Clean up existing test folder if it exists
        if os.path.exists(test_dir):
            import shutil
            shutil.rmtree(test_dir)
        
        # Create test-specific folder structure
        os.makedirs(test_dir, exist_ok=True)
        
        # Create input and output subfolders
        input_dir = os.path.join(test_dir, "input")
        output_dir = os.path.join(test_dir, "output")
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Create source files in input directory
        source_dir = self._create_source_files(test_data, input_dir)
        
        # Create config file in input directory
        config_path = self._create_config_file(test_data, input_dir)
        
        return source_dir, config_path
    
    def _get_test_category(self, test_id: str) -> str:
        """
        Determine test category based on test ID
        
        Args:
            test_id: Test ID (e.g., "001", "101", "201")
            
        Returns:
            Test category (unit, feature, integration, example)
        """
        test_num = int(test_id)
        
        if test_num <= 50:
            return "unit"
        elif test_num <= 150:
            return "feature"
        elif test_num <= 250:
            return "integration"
        else:
            return "example"
    
    def _validate_test_data(self, test_data: Dict) -> None:
        """
        Validate test data structure against schema
        
        Args:
            test_data: Test data dictionary to validate
            
        Raises:
            ValueError: If test data doesn't match expected schema
        """
        # Define required sections
        required_sections = ["source_files", "config"]
        optional_sections = ["model", "assertions"]
        
        # Check required sections
        for section in required_sections:
            if section not in test_data:
                raise ValueError(f"Missing required section '{section}' in test data")
        
        # Validate source_files section
        if not isinstance(test_data["source_files"], dict):
            raise ValueError("'source_files' must be a dictionary")
        
        if not test_data["source_files"]:
            raise ValueError("'source_files' cannot be empty")
        
        # Validate config section
        if not isinstance(test_data["config"], dict):
            raise ValueError("'config' must be a dictionary")
        
        required_config_keys = ["project_name", "source_folders", "output_dir"]
        for key in required_config_keys:
            if key not in test_data["config"]:
                raise ValueError(f"Missing required config key '{key}'")
        
        # Validate assertions section if present
        if "assertions" in test_data:
            if not isinstance(test_data["assertions"], dict):
                raise ValueError("'assertions' must be a dictionary")
            
            # Validate assertion structure
            valid_assertion_keys = ["execution", "model", "puml"]
            for key in test_data["assertions"]:
                if key not in valid_assertion_keys:
                    raise ValueError(f"Invalid assertion key '{key}'. Valid keys: {valid_assertion_keys}")
        
        # Validate model section if present
        if "model" in test_data:
            if not isinstance(test_data["model"], dict):
                raise ValueError("'model' must be a dictionary")
    
    def _create_source_files(self, test_data: Dict, temp_dir: str) -> str:
        """
        Create temporary source files from YAML data
        
        Args:
            test_data: Test data containing source files
            temp_dir: Temporary directory to create files in
            
        Returns:
            Path to directory containing source files
        """
        source_files = test_data["inputs"]["source_files"]
        
        # Create source directory
        source_dir = os.path.join(temp_dir, "src")
        os.makedirs(source_dir, exist_ok=True)
        
        # Create each source file (excluding config.json which is handled separately)
        for filename, content in source_files.items():
            if filename == "config.json":
                continue  # Skip config.json as it's handled separately
            
            file_path = os.path.join(source_dir, filename)
            
            # Ensure directory exists for nested files
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(content)
        
        return source_dir
    
    def _create_config_file(self, test_data: Dict, temp_dir: str) -> str:
        """
        Create temporary config file from YAML data
        
        Args:
            test_data: Test data containing config
            temp_dir: Temporary directory to create config in
            
        Returns:
            Path to the created config file
        """
        source_files = test_data["inputs"]["source_files"]
        
        # Extract config.json content
        if "config.json" not in source_files:
            raise ValueError("Missing config.json in source_files")
        
        config_content = source_files["config.json"]
        
        # Parse JSON to validate it
        try:
            config = json.loads(config_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config.json: {e}")
        
        # Ensure required config fields are present
        if "source_folders" not in config:
            config["source_folders"] = ["."]
        
        # Set output_dir to point to the output subfolder in the test directory
        # temp_dir is the input/ folder, so output is ../output/
        config["output_dir"] = "../output"
        
        if "project_name" not in config:
            config["project_name"] = f"test_{test_data['test']['id']}"
        
        if "recursive_search" not in config:
            config["recursive_search"] = True
        
        # Create config file
        config_path = os.path.join(temp_dir, "config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config_path