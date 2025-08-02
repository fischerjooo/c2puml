#!/usr/bin/env python3
"""
Test invalid source path handling and error messages.
"""

import os
import tempfile
import unittest
from pathlib import Path

from src.c2puml.core.parser import Parser, CParser
from src.c2puml.config import Config


class TestInvalidSourcePaths(unittest.TestCase):
    """Test handling of invalid source paths with enhanced error messages."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.parser = Parser()
        self.c_parser = CParser()

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_nonexistent_source_folder(self):
        """Test error handling for nonexistent source folder."""
        nonexistent_path = "/nonexistent/path/that/does/not/exist"
        
        with self.assertRaises(ValueError) as cm:
            self.c_parser.parse_project(nonexistent_path)
        
        error_msg = str(cm.exception)
        self.assertIn("Source folder not found", error_msg)
        self.assertIn(nonexistent_path, error_msg)

    def test_file_as_source_folder(self):
        """Test error handling when source folder is actually a file."""
        # Create a file
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")
        
        with self.assertRaises(ValueError) as cm:
            self.c_parser.parse_project(test_file)
        
        error_msg = str(cm.exception)
        self.assertIn("Source folder must be a directory", error_msg)
        self.assertIn("is_file: True", error_msg)

    def test_empty_source_folder_string(self):
        """Test error handling for empty source folder string."""
        with self.assertRaises(ValueError) as cm:
            self.c_parser.parse_project("")
        
        error_msg = str(cm.exception)
        self.assertIn("Source folder must be a non-empty string", error_msg)

    def test_whitespace_source_folder_string(self):
        """Test error handling for whitespace-only source folder string."""
        with self.assertRaises(ValueError) as cm:
            self.c_parser.parse_project("   \t\n   ")
        
        error_msg = str(cm.exception)
        self.assertIn("Source folder cannot be empty or whitespace", error_msg)

    def test_non_string_source_folder(self):
        """Test error handling for non-string source folder."""
        with self.assertRaises(ValueError) as cm:
            self.c_parser.parse_project(123)
        
        error_msg = str(cm.exception)
        self.assertIn("Source folder must be a non-empty string", error_msg)

    def test_none_source_folder(self):
        """Test error handling for None source folder."""
        with self.assertRaises(ValueError) as cm:
            self.c_parser.parse_project(None)
        
        error_msg = str(cm.exception)
        self.assertIn("Source folder must be a non-empty string", error_msg)

    def test_relative_path_helpful_message(self):
        """Test that relative path errors provide helpful information."""
        relative_path = "nonexistent/relative/path"
        
        with self.assertRaises(ValueError) as cm:
            self.c_parser.parse_project(relative_path)
        
        error_msg = str(cm.exception)
        self.assertIn("Source folder not found", error_msg)
        self.assertIn("Current working directory", error_msg)
        self.assertIn("Tried to resolve relative path", error_msg)

    def test_parent_directory_exists_message(self):
        """Test that parent directory information is provided."""
        # Create a parent directory but not the target
        parent_dir = os.path.join(self.temp_dir, "parent")
        os.makedirs(parent_dir)
        
        # Create some subdirectories in parent
        os.makedirs(os.path.join(parent_dir, "subdir1"))
        os.makedirs(os.path.join(parent_dir, "subdir2"))
        
        target_path = os.path.join(parent_dir, "nonexistent")
        
        with self.assertRaises(ValueError) as cm:
            self.c_parser.parse_project(target_path)
        
        error_msg = str(cm.exception)
        self.assertIn("Source folder not found", error_msg)
        self.assertIn("Parent directory exists", error_msg)
        self.assertIn("Available directories in parent", error_msg)

    def test_permission_denied_handling(self):
        """Test handling of permission denied errors."""
        # This test might not work on all systems, so we'll make it conditional
        try:
            # Try to access a system directory that might be restricted
            system_path = "/root"
            if os.path.exists(system_path) and not os.access(system_path, os.R_OK):
                with self.assertRaises(ValueError) as cm:
                    self.c_parser.parse_project(system_path)
                
                error_msg = str(cm.exception)
                self.assertIn("Permission denied", error_msg)
        except (OSError, PermissionError):
            # Skip this test if we can't test it
            self.skipTest("Cannot test permission denied scenario on this system")

    def test_parser_empty_source_folders_list(self):
        """Test Parser.parse with empty source_folders list."""
        with self.assertRaises(ValueError) as cm:
            self.parser.parse(source_folders=[])
        
        error_msg = str(cm.exception)
        self.assertIn("At least one source folder must be provided", error_msg)

    def test_parser_non_list_source_folders(self):
        """Test Parser.parse with non-list source_folders."""
        with self.assertRaises(TypeError) as cm:
            self.parser.parse(source_folders="not_a_list")
        
        error_msg = str(cm.exception)
        self.assertIn("source_folders must be a list of strings", error_msg)

    def test_parser_empty_string_in_source_folders(self):
        """Test Parser.parse with empty string in source_folders list."""
        with self.assertRaises(ValueError) as cm:
            self.parser.parse(source_folders=["valid_path", ""])
        
        error_msg = str(cm.exception)
        self.assertIn("cannot be empty or whitespace", error_msg)

    def test_parser_non_string_in_source_folders(self):
        """Test Parser.parse with non-string in source_folders list."""
        with self.assertRaises(TypeError) as cm:
            self.parser.parse(source_folders=["valid_path", 123])
        
        error_msg = str(cm.exception)
        self.assertIn("must be strings", error_msg)

    def test_config_empty_source_folders(self):
        """Test Config.load with empty source_folders."""
        import tempfile
        import json
        import os
        
        # Create a temporary config file with empty source_folders
        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "test_config.json")
        config_data = {
            "source_folders": [],
            "project_name": "test"
        }
        
        with open(config_path, "w") as f:
            json.dump(config_data, f)
        
        # Empty source_folders list should raise an error when loading
        with self.assertRaises(ValueError) as cm:
            Config.load(config_path)
        
        error_msg = str(cm.exception)
        self.assertIn("cannot be empty", error_msg)
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)

    def test_config_non_list_source_folders(self):
        """Test Config.load with non-list source_folders."""
        import tempfile
        import json
        import os
        
        # Create a temporary config file with non-list source_folders
        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "test_config.json")
        config_data = {
            "source_folders": "not_a_list",
            "project_name": "test"
        }
        
        with open(config_path, "w") as f:
            json.dump(config_data, f)
        
        # Non-list source_folders should raise an error when loading
        with self.assertRaises(ValueError) as cm:
            Config.load(config_path)
        
        error_msg = str(cm.exception)
        self.assertIn("must be a list", error_msg)
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)

    def test_config_missing_source_folders(self):
        """Test Config.load with missing source_folders."""
        import tempfile
        import json
        import os
        
        # Create a temporary config file without source_folders
        temp_dir = tempfile.mkdtemp()
        config_path = os.path.join(temp_dir, "test_config.json")
        config_data = {
            "project_name": "test"
        }
        
        with open(config_path, "w") as f:
            json.dump(config_data, f)
        
        # Missing source_folders should raise an error when loading
        with self.assertRaises(ValueError) as cm:
            Config.load(config_path)
        
        error_msg = str(cm.exception)
        self.assertIn("must contain 'source_folders' field", error_msg)
        
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)

    def test_multiple_source_folders_partial_failure(self):
        """Test handling when some source folders fail but others succeed."""
        # Create a valid source folder
        valid_dir = os.path.join(self.temp_dir, "valid")
        os.makedirs(valid_dir)
        
        # Create a test file in the valid directory
        test_file = os.path.join(valid_dir, "test.c")
        with open(test_file, "w") as f:
            f.write("int main() { return 0; }")
        
        # Test with one valid and one invalid folder
        source_folders = [valid_dir, "/nonexistent/path"]
        
        # This should not raise an exception, but should log warnings
        output_file = os.path.join(self.temp_dir, "model.json")
        result = self.parser.parse(source_folders=source_folders, output_file=output_file)
        
        # Should return the output file path
        self.assertEqual(result, output_file)
        
        # Should create the model file
        self.assertTrue(os.path.exists(output_file))

    def test_all_source_folders_fail(self):
        """Test handling when all source folders fail."""
        source_folders = ["/nonexistent/path1", "/nonexistent/path2"]
        
        with self.assertRaises(RuntimeError) as cm:
            self.parser.parse(source_folders=source_folders, output_file="model.json")
        
        error_msg = str(cm.exception)
        self.assertIn("All source folders failed to parse", error_msg)
        self.assertIn("/nonexistent/path1", error_msg)
        self.assertIn("/nonexistent/path2", error_msg)


if __name__ == "__main__":
    unittest.main()