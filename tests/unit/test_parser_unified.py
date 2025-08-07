#!/usr/bin/env python3
"""
Unit tests for the C parser using the unified testing framework

This test demonstrates how to convert existing tests to use the unified framework
that enforces CLI-only access to c2puml functionality.
"""

import os
import sys
import unittest

# Add the tests directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from framework import UnifiedTestCase


class TestCParserUnified(UnifiedTestCase):
    """Test the C parser functionality using the unified framework"""

    def test_parse_simple_c_file(self):
        """
        Test parsing a simple C file through the CLI interface
        
        This test demonstrates the conversion from direct internal API access
        to CLI-only execution using the unified testing framework.
        """
        # Create test source files using the framework
        source_files = {
            "simple.c": """
#include <stdio.h>

struct Person {
    char name[50];
    int age;
};

enum Status {
    OK,
    ERROR
};

int main() {
    return 0;
}

int global_var;
            """
        }
        
        # Create test configuration
        config_data = {
            "project_name": "test_parser_simple",
            "source_folders": ["."],
            "output_dir": self.output_dir,
            "recursive_search": True
        }
        
        # Create test files using framework helpers
        source_dir = self.create_test_source_files(source_files)
        config_path = self.create_test_config(config_data)
        
        # Execute c2puml through CLI using framework
        result = self.run_c2puml_full_pipeline(config_path, source_dir)
        
        # Validate execution success
        self.assert_c2puml_success(result)
        
        # Validate output files were created
        self.assert_model_file_exists()
        self.assert_transformed_model_file_exists()
        self.assert_puml_files_exist()
        
        # Validate model content using framework helpers
        self.assert_model_contains_struct("Person", ["name", "age"])
        self.assert_model_contains_enum("Status", ["OK", "ERROR"])
        self.assert_model_contains_function("main")
        self.assert_model_contains_global("global_var")
        self.assert_model_contains_include("stdio.h")
        
        # Validate element counts
        self.assert_model_element_count("structs", 1)
        self.assert_model_element_count("enums", 1)
        self.assert_model_element_count("functions", 1)
        self.assert_model_element_count("globals", 1)
        self.assert_model_element_count("includes", 1)
        
        # Validate PlantUML output using framework helpers
        self.assert_puml_contains_element("Person")
        self.assert_puml_contains_element("Status")
        self.assert_puml_contains_element("main")
        self.assert_puml_contains_syntax()


if __name__ == "__main__":
    unittest.main()