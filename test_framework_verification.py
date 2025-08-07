#!/usr/bin/env python3
"""
Framework Verification Test

This test verifies that the unified testing framework works correctly
with the actual c2puml CLI interface.
"""

import os
import json
import tempfile
import unittest
import sys

# Add the tests directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

try:
    from framework import TestInputFactory, TestExecutor, UnifiedTestCase
    FRAMEWORK_AVAILABLE = True
except ImportError as e:
    print(f"Framework not available: {e}")
    FRAMEWORK_AVAILABLE = False


class TestFrameworkVerification(unittest.TestCase):
    """Test to verify the unified framework works correctly"""
    
    def setUp(self):
        """Set up test environment"""
        if not FRAMEWORK_AVAILABLE:
            self.skipTest("Framework not available")
        
        self.input_factory = TestInputFactory()
        self.executor = TestExecutor()
        self.test_name = "test_framework_verification"
        
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.output_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_input_factory_config_creation(self):
        """Test that TestInputFactory creates proper config files"""
        # Test input data
        input_data = {
            "test_metadata": {
                "description": "Test config creation",
                "test_type": "unit"
            },
            "c2puml_config": {
                "project_name": "test_project",
                "source_folders": ["."],
                "output_dir": "./output"
            },
            "source_files": {
                "main.c": "int main() { return 0; }"
            }
        }
        
        # Create temporary files
        temp_dir = tempfile.mkdtemp()
        try:
            input_path = self.input_factory._create_temp_source_files(input_data, temp_dir)
            config_path = self.input_factory._create_temp_config_file(input_data, temp_dir)
            
            # Verify source files were created
            self.assertTrue(os.path.exists(os.path.join(input_path, "main.c")))
            
            # Verify config file was created and has correct structure
            self.assertTrue(os.path.exists(config_path))
            
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Check required fields
            self.assertIn("project_name", config)
            self.assertIn("source_folders", config)
            self.assertIn("output_dir", config)
            
            self.assertEqual(config["project_name"], "test_project")
            self.assertEqual(config["source_folders"], ["."])
            self.assertEqual(config["output_dir"], "./output")
            
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_executor_command_building(self):
        """Test that TestExecutor builds correct commands"""
        # Test command building
        args = ["--config", "test.json"]
        command = self.executor._build_command(args)
        
        # Should start with c2puml command
        self.assertEqual(command[0], "c2puml")
        self.assertEqual(command[1:], args)
    
    def test_cli_execution_basic(self):
        """Test basic CLI execution through the framework"""
        # Create a simple test configuration
        config = {
            "project_name": "test_project",
            "source_folders": ["."],
            "output_dir": self.output_dir
        }
        
        # Create a simple C source file
        source_content = """
        #include <stdio.h>
        
        struct Point {
            int x;
            int y;
        };
        
        int main() {
            struct Point p = {10, 20};
            return 0;
        }
        """
        
        # Create temporary files
        temp_dir = tempfile.mkdtemp()
        try:
            source_file = os.path.join(temp_dir, "main.c")
            config_file = os.path.join(temp_dir, "config.json")
            
            with open(source_file, 'w') as f:
                f.write(source_content)
            
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Execute c2puml through CLI
            result = self.executor.run_full_pipeline(temp_dir, config_file, self.output_dir)
            
            # Verify execution (this might fail if c2puml has issues, but we're testing the framework)
            # We don't assert success here since we're just testing the framework, not c2puml itself
            self.assertIsNotNone(result)
            self.assertIsInstance(result.exit_code, int)
            self.assertIsInstance(result.stdout, str)
            self.assertIsInstance(result.stderr, str)
            self.assertIsInstance(result.execution_time, float)
            
            # Verify command was built correctly
            self.assertIn("c2puml", result.command[0])
            self.assertIn("--config", result.command)
            self.assertIn(config_file, result.command)
            
        finally:
            import shutil
            shutil.rmtree(temp_dir)
    
    def test_input_factory_validation(self):
        """Test input factory validation"""
        # Test valid input data
        valid_input_data = {
            "test_metadata": {
                "description": "Test input",
                "test_type": "unit"
            },
            "c2puml_config": {
                "project_name": "test_project",
                "source_folders": ["."]
            },
            "source_files": {
                "main.c": "int main() { return 0; }"
            }
        }
        
        # This should not raise an exception
        self.input_factory._validate_input_json_structure(valid_input_data)
        
        # Test invalid structure (missing required sections)
        invalid_input_data = {
            "test_metadata": {
                "description": "Test input"
            }
            # Missing c2puml_config and source_files
        }
        
        with self.assertRaises(ValueError):
            self.input_factory._validate_input_json_structure(invalid_input_data)
        
        # Test forbidden sections
        invalid_input_data_with_results = {
            "test_metadata": {
                "description": "Test input",
                "test_type": "unit"
            },
            "c2puml_config": {
                "project_name": "test_project",
                "source_folders": ["."]
            },
            "source_files": {
                "main.c": "int main() { return 0; }"
            },
            "expected_results": {
                "should": "not be here"
            }
        }
        
        with self.assertRaises(ValueError):
            self.input_factory._validate_input_json_structure(invalid_input_data_with_results)
    
    def test_output_directory_management(self):
        """Test output directory management"""
        # Test basic output directory
        output_dir = self.input_factory.get_output_dir_for_scenario("test_example")
        self.assertIn("test_example", output_dir)
        self.assertIn("output", output_dir)
        
        # Test scenario-specific output directory
        scenario_output_dir = self.input_factory.get_output_dir_for_scenario(
            "test_example", "input-simple_struct.json"
        )
        self.assertIn("output-simple_struct", scenario_output_dir)
        
        # Test example output directory
        example_output_dir = self.input_factory.get_example_output_dir("test_example_basic")
        self.assertIn("artifacts/examples/basic", example_output_dir)
    
    def test_test_category_detection(self):
        """Test test category detection"""
        # Test unit tests
        category = self.input_factory._get_test_category("test_parser")
        self.assertEqual(category, "unit")
        
        # Test feature tests
        category = self.input_factory._get_test_category("test_include_processing_features")
        self.assertEqual(category, "feature")
        
        # Test integration tests
        category = self.input_factory._get_test_category("test_comprehensive")
        self.assertEqual(category, "feature")  # comprehensive is treated as feature
        
        # Test example tests
        category = self.input_factory._get_test_category("test_example_basic")
        self.assertEqual(category, "example")


if __name__ == '__main__':
    unittest.main()