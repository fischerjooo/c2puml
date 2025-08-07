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
        # Create temp directory within the test case folder
        test_categories = ["unit", "feature", "integration", "example"]
        temp_dir = None
        
        for category in test_categories:
            test_dir = f"tests/{category}"
            if os.path.exists(test_dir):
                temp_dir = os.path.join(test_dir, "temp")
                break
        
        if not temp_dir:
            raise ValueError(f"Could not find test directory for test ID: {test_id}")
        
        # Create temp directory if it doesn't exist
        os.makedirs(temp_dir, exist_ok=True)
        
        # Create test-specific temp directory
        test_temp_dir = os.path.join(temp_dir, f"test_{test_id}")
        os.makedirs(test_temp_dir, exist_ok=True)
        
        # Create source files
        source_dir = self._create_source_files(test_data, test_temp_dir)
        
        # Create config file
        config_path = self._create_config_file(test_data, test_temp_dir)
        
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
        Validate test data structure
        
        Args:
            test_data: Test data to validate
            
        Raises:
            ValueError: If test data structure is invalid
        """
        required_sections = ["test", "inputs", "assertions"]
        
        for section in required_sections:
            if section not in test_data:
                raise ValueError(f"Missing required section in test data: {section}")
        
        # Validate test section
        test_section = test_data["test"]
        required_test_fields = ["name", "description", "category", "id"]
        
        for field in required_test_fields:
            if field not in test_section:
                raise ValueError(f"Missing required field in test section: {field}")
        
        # Validate inputs section
        inputs_section = test_data["inputs"]
        if "source_files" not in inputs_section:
            raise ValueError("Missing source_files in inputs section")
        
        # Check that config.json is included in source_files (optional)
        source_files = inputs_section["source_files"]
        if "config.json" not in source_files:
            # Add default config if not provided
            inputs_section["source_files"]["config.json"] = json.dumps({
                "project_name": f"test_{test_data['test']['id']}",
                "source_folders": ["."],
                "output_dir": "./output",
                "recursive_search": True
            }, indent=2)
        
        # Validate assertions section
        assertions_section = test_data["assertions"]
        if not isinstance(assertions_section, dict):
            raise ValueError("Assertions section must be a dictionary")
    
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
        
        if "output_dir" not in config:
            config["output_dir"] = "./output"
        
        if "project_name" not in config:
            config["project_name"] = f"test_{test_data['test']['id']}"
        
        if "recursive_search" not in config:
            config["recursive_search"] = True
        
        # Create config file
        config_path = os.path.join(temp_dir, "config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return config_path