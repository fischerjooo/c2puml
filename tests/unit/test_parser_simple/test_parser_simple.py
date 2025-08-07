#!/usr/bin/env python3
"""
Unit tests for the C parser using the unified testing framework

This test demonstrates the proper conversion from direct internal API access
to CLI-only execution using the unified testing framework with input-###.json approach.
"""

import os
import sys
import unittest
import json

# Add the tests directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from framework import UnifiedTestCase


class TestParserSimple(UnifiedTestCase):
    """Test the C parser functionality using the unified framework with input-###.json approach"""

    def setUp(self):
        """Set up test environment with correct test name"""
        super().setUp()
        # Override test name to match folder structure
        self.test_name = "test_parser_simple"

    def test_parse_simple_c_file(self):
        """
        Test parsing a simple C file through the CLI interface
        
        This test demonstrates the conversion from direct internal API access
        to CLI-only execution using the unified testing framework with proper
        input-###.json approach as specified in todo.md.
        """
        # Load test scenario using input-###.json approach
        input_path, config_path = self.input_factory.load_input_json_scenario(
            self.test_name, "input-simple_c_file.json"
        )
        
        # Load assertions for this scenario
        assertions = self.input_factory.load_scenario_assertions(
            self.test_name, "input-simple_c_file.json"
        )
        
        # Execute c2puml through CLI using framework
        result = self.run_c2puml_full_pipeline(config_path, input_path)
        
        # Validate execution success
        self.assert_c2puml_success(result)
        
        # The output is created in the working directory (src) + output
        actual_output_dir = os.path.join(result.working_dir, "output")
        
        # Validate output files were created
        self.assert_model_file_exists(actual_output_dir)
        self.assert_transformed_model_file_exists(actual_output_dir)
        self.assert_puml_files_exist(actual_output_dir)
        
        # Validate model content using framework helpers
        # We need to pass the actual output directory to the helper methods
        model_file = os.path.join(actual_output_dir, "model.json")
        with open(model_file, 'r') as f:
            model_data = json.load(f)
        
        # Validate struct
        self.model_validator.assert_model_struct_exists(model_data, "Person")
        self.model_validator.assert_model_struct_fields(model_data, "Person", ["name", "age"])
        
        # Validate enum
        self.model_validator.assert_model_enum_exists(model_data, "Status")
        self.model_validator.assert_model_enum_values(model_data, "Status", ["OK", "ERROR"])
        
        # Validate function
        self.model_validator.assert_model_function_exists(model_data, "main")
        
        # Validate global
        self.model_validator.assert_model_global_exists(model_data, "global_var")
        
        # Validate include
        self.model_validator.assert_model_include_exists(model_data, "stdio.h")
        
        # Validate element counts
        self.model_validator.assert_model_element_count(model_data, "structs", 1)
        self.model_validator.assert_model_element_count(model_data, "enums", 1)
        self.model_validator.assert_model_element_count(model_data, "functions", 1)
        self.model_validator.assert_model_element_count(model_data, "globals", 1)
        self.model_validator.assert_model_element_count(model_data, "includes", 1)
        
        # Validate PlantUML output using framework helpers
        puml_files = self.assert_puml_files_exist(actual_output_dir)
        
        # Check the first .puml file
        with open(puml_files[0], 'r') as f:
            puml_content = f.read()
        
        self.puml_validator.assert_puml_contains(puml_content, "Person")
        self.puml_validator.assert_puml_contains(puml_content, "Status")
        self.puml_validator.assert_puml_contains(puml_content, "main")
        self.puml_validator.assert_puml_start_end_tags(puml_content)


if __name__ == "__main__":
    unittest.main()