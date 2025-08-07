"""
TestInputFactory - Unified Input Management for C2PUML Tests

This module provides a unified factory for managing all test input data,
supporting both file-based approaches (feature/example tests) and input-###.json
approaches (unit tests) as specified in the test refactoring plan.
"""

import os
import json
import tempfile
import shutil
from typing import Tuple, List, Dict, Optional
from pathlib import Path


class TestInputFactory:
    """
    Unified factory for managing all test input data (both explicit files and input-###.json)
    
    This class provides a single interface for loading test data regardless of whether
    the test uses file-based approach (config.json + source files) or input-###.json
    approach (JSON files with embedded config and source content).
    """
    
    def __init__(self):
        """Initialize the TestInputFactory"""
        pass
    
    # === File-Based Approach (Feature/Example/Integration Tests) ===
    
    def load_test_files(self, test_name: str) -> Tuple[str, str]:
        """
        Load test files and return (input_path, config_path)
        
        Args:
            test_name: Name of the test (e.g., 'test_include_processing_features')
            
        Returns:
            Tuple of (input_path, config_path) where input_path is the directory
            containing source files and config_path is the path to config.json
            
        Raises:
            FileNotFoundError: If required files don't exist
        """
        input_path = self.get_test_data_path(test_name, "input")
        config_path = os.path.join(input_path, "config.json")
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        return input_path, config_path
    
    def load_test_assertions(self, test_name: str) -> dict:
        """
        Load assertions.json for file-based approach (Option 1)
        
        Args:
            test_name: Name of the test
            
        Returns:
            Dictionary containing assertions for all test methods
        """
        assertions_path = self.get_test_data_path(test_name, "assertions.json")
        if os.path.exists(assertions_path):
            with open(assertions_path, 'r') as f:
                return json.load(f)
        return {}
    
    def load_test_method_assertions(self, test_name: str, method_name: str) -> dict:
        """
        Load assertions for specific test method from assertions.json (Option 1)
        
        Args:
            test_name: Name of the test
            method_name: Name of the test method
            
        Returns:
            Dictionary containing assertions for the specific test method
        """
        all_assertions = self.load_test_assertions(test_name)
        return all_assertions.get(method_name, {})
    
    # === Input JSON Approach (Unit Tests) ===
    
    def load_input_json_scenario(self, test_name: str, input_file: str) -> Tuple[str, str]:
        """
        Load input-###.json and return (input_path, config_path)
        
        Args:
            test_name: Name of the test
            input_file: Name of the input file (e.g., 'input-simple_struct.json')
            
        Returns:
            Tuple of (input_path, config_path) where input_path is a temporary
            directory containing the source files and config_path is the path
            to the temporary config.json
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If input file has invalid structure
        """
        # Load input-###.json file
        input_file_path = self.get_test_data_path(test_name, f"input/{input_file}")
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"Input file not found: {input_file_path}")
            
        with open(input_file_path, 'r') as f:
            input_data = json.load(f)
        
        # Validate structure
        self._validate_input_json_structure(input_data)
        
        # Create temporary files
        temp_dir = tempfile.mkdtemp()
        input_path = self._create_temp_source_files(input_data, temp_dir)
        config_path = self._create_temp_config_file(input_data, temp_dir)
        
        return input_path, config_path
    
    def load_scenario_assertions(self, test_name: str, input_file: str) -> dict:
        """
        Load assert-###.json for specific input scenario (Option 2)
        
        Args:
            test_name: Name of the test
            input_file: Name of the input file (e.g., 'input-simple_struct.json')
            
        Returns:
            Dictionary containing assertions for the specific scenario
        """
        # Convert input-simple_struct.json -> assert-simple_struct.json
        assert_file = input_file.replace("input-", "assert-")
        assertions_path = self.get_test_data_path(test_name, assert_file)
        if os.path.exists(assertions_path):
            with open(assertions_path, 'r') as f:
                return json.load(f)
        return {}
    
    def list_input_json_files(self, test_name: str) -> List[str]:
        """
        List all input-###.json files for a test
        
        Args:
            test_name: Name of the test
            
        Returns:
            List of input-###.json file names
        """
        input_dir = self.get_test_data_path(test_name, "input")
        if not os.path.exists(input_dir):
            return []
        return [f for f in os.listdir(input_dir) if f.startswith("input-") and f.endswith(".json")]
    
    # === Output Directory Management ===
    
    def get_output_dir_for_scenario(self, test_name: str, scenario_name: str = None) -> str:
        """
        Get output directory: output/ or output-<scenario>/
        
        Args:
            test_name: Name of the test
            scenario_name: Optional scenario name (e.g., 'input-simple_struct.json')
            
        Returns:
            Path to the output directory
        """
        test_dir = self.get_test_data_path(test_name).replace("/input", "")
        if scenario_name:
            # Extract meaningful name from input file
            clean_name = scenario_name.replace("input-", "").replace(".json", "")
            return os.path.join(test_dir, f"output-{clean_name}")
        else:
            return os.path.join(test_dir, "output")
    
    def get_example_output_dir(self, test_name: str) -> str:
        """
        Returns artifacts/examples/<name>/ for example tests
        
        Args:
            test_name: Name of the test (e.g., 'test_example_basic')
            
        Returns:
            Path to the example output directory
        """
        return f"artifacts/examples/{test_name.replace('test_example_', '')}"
    
    def ensure_output_dir_clean(self, output_dir: str) -> None:
        """
        Ensure output directory exists and is clean
        
        Args:
            output_dir: Path to the output directory
        """
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)
    
    # === Utility Methods ===
    
    def get_test_data_path(self, test_name: str, subpath: str = "") -> str:
        """
        Get path to test data directory or file
        
        Args:
            test_name: Name of the test
            subpath: Optional subpath within the test directory
            
        Returns:
            Path to the test data directory or file
        """
        base_path = f"tests/{self._get_test_category(test_name)}/{test_name}"
        return os.path.join(base_path, subpath) if subpath else base_path
    
    def _get_test_category(self, test_name: str) -> str:
        """
        Determine test category from test name
        
        Args:
            test_name: Name of the test
            
        Returns:
            Test category ('unit', 'feature', 'integration', or 'example')
        """
        if test_name.startswith("test_example_"):
            return "example"
        elif "feature" in test_name or "integration" in test_name or "comprehensive" in test_name:
            return "feature"
        else:
            return "unit"
    
    # === Private Helper Methods ===
    
    def _validate_input_json_structure(self, input_data: dict) -> None:
        """
        Validate input-###.json structure (no expected_results allowed)
        
        Args:
            input_data: The loaded input data dictionary
            
        Raises:
            ValueError: If the structure is invalid
        """
        required_sections = ["test_metadata", "c2puml_config", "source_files"]
        forbidden_sections = ["expected_results"]
        
        missing = [s for s in required_sections if s not in input_data]
        if missing:
            raise ValueError(f"Missing required sections in input JSON: {missing}")
        
        forbidden_found = [s for s in forbidden_sections if s in input_data]
        if forbidden_found:
            raise ValueError(f"Forbidden sections in input JSON (use assertion files instead): {forbidden_found}")
    
    def _create_temp_config_file(self, input_data: dict, temp_dir: str) -> str:
        """
        Create temporary config.json from input data
        
        Args:
            input_data: The input data dictionary
            temp_dir: Temporary directory path
            
        Returns:
            Path to the created config.json file
        """
        config = input_data.get("c2puml_config", {})
        
        # Ensure the config has the required fields for CLI
        if "source_folders" not in config:
            # Default to current directory if no source folders specified
            config["source_folders"] = ["."]
        
        if "output_dir" not in config:
            # Default to ./output if no output directory specified
            config["output_dir"] = "./output"
        
        # Ensure project_name is set
        if "project_name" not in config:
            config["project_name"] = "test_project"
        
        # Ensure recursive_search is set (default to True)
        if "recursive_search" not in config:
            config["recursive_search"] = True
        
        config_path = os.path.join(temp_dir, "config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return config_path
    
    def _create_temp_source_files(self, input_data: dict, temp_dir: str) -> str:
        """
        Create temporary source files from input data
        
        Args:
            input_data: The input data dictionary
            temp_dir: Temporary directory path
            
        Returns:
            Path to the directory containing source files
        """
        source_files = input_data.get("source_files", {})
        
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