#!/usr/bin/env python3
"""
Unit test for Simple C File Parsing

This test demonstrates the new unified testing framework with YAML-based
test data and assertions.
"""

import os
import sys
import unittest
import json

# Add the tests directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.framework import UnifiedTestCase


class TestSimpleCFileParsing(UnifiedTestCase):
    """Test Simple C File Parsing"""

    def test_simple_c_file_parsing(self):
        """Test parsing a simple C file through the CLI interface"""
        # Load test data from YAML
        test_data = self.data_loader.load_test_data("simple_c_file_parsing")
        
        # Create temporary files in test-specific folder structure
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "simple_c_file_parsing")
        
        # Get the test folder (parent of source_dir which is now input/)
        test_folder = os.path.dirname(source_dir)  # This is the input/ folder
        test_dir = os.path.dirname(test_folder)    # This is the test-simple_c_file_parsing/ folder
        
        # Make config path relative to working directory (input folder)
        config_filename = os.path.basename(config_path)
        
        # Execute c2puml with input directory as working directory
        # The config.json is in the input/ folder, so use that as working directory
        result = self.executor.run_full_pipeline(config_filename, test_folder)
        
        # Validate execution using CLI validator
        self.cli_validator.assert_cli_success(result)
        
        # Load output files (output is created in the output/ subfolder)
        output_dir = os.path.join(test_dir, "output")
        model_file = self.output_validator.assert_model_file_exists(output_dir)
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        
        # Load content for validation
        with open(model_file, 'r') as f:
            model_data = json.load(f)
        
        with open(puml_files[0], 'r') as f:
            puml_content = f.read()
        
        # Process assertions from YAML
        self.assertion_processor.process_assertions(
            test_data["assertions"], model_data, puml_content, result, self
        )


if __name__ == "__main__":
    unittest.main()