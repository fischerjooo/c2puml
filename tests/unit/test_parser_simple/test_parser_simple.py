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

from framework import UnifiedTestCase, AssertionProcessor


class TestParserSimple(UnifiedTestCase):
    """Test the C parser functionality using the unified framework with input-###.json approach"""

    def setUp(self):
        """Set up test environment with correct test name"""
        super().setUp()
        # Override test name to match folder structure
        self.test_name = "test_parser_simple"
        # Initialize assertion processor
        self.assertion_processor = AssertionProcessor()

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
        result = self.executor.run_full_pipeline(config_path, input_path)

        # Validate execution success
        self.assert_c2puml_success(result)

        # The output is created in the working directory (src) + output
        actual_output_dir = os.path.join(result.working_dir, "output")

        # Validate output files were created
        self.assert_model_file_exists(actual_output_dir)
        self.assert_transformed_model_file_exists(actual_output_dir)
        self.assert_puml_files_exist(actual_output_dir)

        # Load model data for assertion processing
        model_file = os.path.join(actual_output_dir, "model.json")
        with open(model_file, 'r') as f:
            model_data = json.load(f)

        # Load PlantUML content for assertion processing
        puml_files = self.assert_puml_files_exist(actual_output_dir)
        with open(puml_files[0], 'r') as f:
            puml_content = f.read()

        # Process assertions from the JSON file using the assertion processor
        self.assertion_processor.process_assertions(
            assertions, model_data, puml_content, result, self
        )


if __name__ == "__main__":
    unittest.main()