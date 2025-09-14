#!/usr/bin/env python3
"""
Test Error Handling Through CLI Interface
"""

import os
import sys
import unittest
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tests.framework import UnifiedTestCase


class TestErrorHandlingComprehensive(UnifiedTestCase):
    """Test error handling scenarios through the CLI interface"""

    def test_invalid_source_folder_errors(self):
        """Test various invalid source folder scenarios"""
        # Load test data from YAML
        test_data = self.data_loader.load_test_data("204_errors_invalid_source")

        # Create temporary files
        source_dir, config_path = self.data_loader.create_temp_files(
            test_data, "204_errors_invalid_source"
        )

        # Get the temp directory (parent of source_dir)
        temp_dir = os.path.dirname(source_dir)

        # Make config path relative to working directory
        config_filename = os.path.basename(config_path)

        # Execute c2puml with temp directory as working directory - expect failure
        result = self.executor.run_full_pipeline(config_filename, temp_dir)

        # Process assertions from YAML - for error tests, we expect different behavior
        self.validators_processor.process_assertions(test_data["assertions"], {}, {}, result, self)

    def test_invalid_config_errors(self):
        """Test various invalid configuration scenarios"""
        # Load test data from YAML
        test_data = self.data_loader.load_test_data("204_errors_invalid_config")

        # Create temporary files
        source_dir, config_path = self.data_loader.create_temp_files(
            test_data, "204_errors_invalid_config"
        )

        # Get the temp directory (parent of source_dir)
        temp_dir = os.path.dirname(source_dir)

        # Make config path relative to working directory
        config_filename = os.path.basename(config_path)

        # Execute c2puml with temp directory as working directory - expect failure
        result = self.executor.run_full_pipeline(config_filename, temp_dir)

        # Process assertions from YAML - for error tests, we expect different behavior
        self.validators_processor.process_assertions(test_data["assertions"], {}, {}, result, self)

    def test_partial_failure_scenarios(self):
        """Test scenarios where some operations fail but others succeed"""
        # Load test data from YAML
        test_data = self.data_loader.load_test_data("204_errors_partial")

        # Create temporary files
        source_dir, config_path = self.data_loader.create_temp_files(
            test_data, "204_errors_partial"
        )

        # Get the temp directory (parent of source_dir)
        temp_dir = os.path.dirname(source_dir)

        # Make config path relative to working directory
        config_filename = os.path.basename(config_path)

        # Execute c2puml with temp directory as working directory
        result = self.executor.run_full_pipeline(config_filename, temp_dir)

        # Validate execution success
        self.cli_validator.assert_cli_success(result)

        # Load output files - output is at the same level as temp_dir
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")

        # For partial failure test, we expect success with some files generated
        model_file = self.output_validator.assert_model_file_exists(output_dir)
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)

        # Load content for validation
        with open(model_file, "r") as f:
            model_data = json.load(f)

        # Load all PlantUML files into a dictionary
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, "r") as f:
                puml_files_dict[filename] = f.read()

        # Process assertions from YAML
        self.validators_processor.process_assertions(
            test_data["assertions"], model_data, puml_files_dict, result, self
        )


if __name__ == "__main__":
    unittest.main()
