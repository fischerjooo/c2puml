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
            test_id: Test ID (e.g., "001", "101", "201")
            
        Returns:
            Dictionary containing test data from YAML file
            
        Raises:
            FileNotFoundError: If YAML file doesn't exist
            yaml.YAMLError: If YAML file is invalid
        """
        # Determine test category based on ID
        category = self._get_test_category(test_id)
        
        # Construct YAML file path
        yaml_file = f"tests/{category}/test-{test_id}.yml"
        
        if not os.path.exists(yaml_file):
            raise FileNotFoundError(f"Test data file not found: {yaml_file}")
        
        with open(yaml_file, 'r') as f:
            test_data = yaml.safe_load(f)
        
        # Validate YAML structure
        self._validate_test_data(test_data)
        
        return test_data
    
    def create_temp_files(self, test_data: Dict) -> Tuple[str, str]:
        """
        Create temporary source files and config from YAML data
        
        Args:
            test_data: Test data loaded from YAML file
            
        Returns:
            Tuple of (source_dir_path, config_file_path)
        """
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Create source files
        source_dir = self._create_source_files(test_data, temp_dir)
        
        # Create config file
        config_path = self._create_config_file(test_data, temp_dir)
        
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
        
        if "config" not in inputs_section:
            raise ValueError("Missing config in inputs section")
        
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
        
        # Create each source file
        for filename, content in source_files.items():
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
        config = test_data["inputs"]["config"]
        
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