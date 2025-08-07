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
        
        # Create temporary files
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "simple_c_file_parsing")
        
        # Get the temp directory (parent of source_dir)
        temp_dir = os.path.dirname(source_dir)
        
        # Make config path relative to working directory
        config_filename = os.path.basename(config_path)
        
        # Execute c2puml with temp directory as working directory
        result = self.executor.run_full_pipeline(config_filename, temp_dir)
        
        # Validate execution
        self.assert_c2puml_success(result)
        
        # Load output files (output is created in temp directory, not src)
        output_dir = os.path.join(temp_dir, "output")
        model_file = os.path.join(output_dir, "model.json")
        puml_files = self.assert_puml_files_exist(output_dir)
        
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