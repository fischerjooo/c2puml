#!/usr/bin/env python3
"""
Unit tests for the parser filtering functionality
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from c_to_plantuml.models import ProjectModel
from c_to_plantuml.parser import CParser, Parser


class TestParserFiltering(unittest.TestCase):
    """Test cases for parser filtering functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.parser = Parser()
        self.c_parser = CParser()
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = []

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, filename: str, content: str) -> str:
        """Create a test file and return its path"""
        file_path = os.path.join(self.temp_dir, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.test_files.append(file_path)
        return file_path

    def test_file_extension_filtering(self):
        """Test that only C/C++ files are included"""
        # Create files with different extensions
        c_file = self.create_test_file("test.c", "int main() { return 0; }")
        h_file = self.create_test_file("header.h", "#define MAX 100")
        cpp_file = self.create_test_file("test.cpp", "int main() { return 0; }")
        txt_file = self.create_test_file("readme.txt", "This is a text file")
        py_file = self.create_test_file("script.py", "print('Hello')")

        # Parse the project
        model = self.c_parser.parse_project(self.temp_dir, recursive=False)

        # Verify only C/C++ files are included
        self.assertEqual(len(model.files), 3)
        self.assertIn("test.c", model.files)
        self.assertIn("header.h", model.files)
        self.assertIn("test.cpp", model.files)
        self.assertNotIn("readme.txt", model.files)
        self.assertNotIn("script.py", model.files)

    def test_hidden_file_exclusion(self):
        """Test that hidden files and directories are excluded"""
        # Create hidden files and directories
        hidden_file = self.create_test_file(".hidden.c", "int hidden() { return 0; }")
        hidden_dir = os.path.join(self.temp_dir, ".hidden_dir")
        os.makedirs(hidden_dir)
        hidden_in_dir = os.path.join(hidden_dir, "test.c")
        with open(hidden_in_dir, "w") as f:
            f.write("int test() { return 0; }")

        # Create visible files
        visible_file = self.create_test_file("visible.c", "int visible() { return 0; }")

        # Parse the project
        model = self.c_parser.parse_project(self.temp_dir, recursive=True)

        # Verify hidden files are excluded
        self.assertEqual(len(model.files), 1)
        self.assertIn("visible.c", model.files)
        self.assertNotIn(".hidden.c", model.files)
        self.assertNotIn(".hidden_dir/test.c", model.files)

    def test_exclude_patterns(self):
        """Test that common exclude patterns are filtered out"""
        # Create directories that should be excluded
        git_dir = os.path.join(self.temp_dir, ".git")
        os.makedirs(git_dir)
        git_file = os.path.join(git_dir, "config.c")
        with open(git_file, "w") as f:
            f.write("int git_config() { return 0; }")

        cache_dir = os.path.join(self.temp_dir, "__pycache__")
        os.makedirs(cache_dir)
        cache_file = os.path.join(cache_dir, "test.c")
        with open(cache_file, "w") as f:
            f.write("int cache_test() { return 0; }")

        vscode_dir = os.path.join(self.temp_dir, ".vscode")
        os.makedirs(vscode_dir)
        vscode_file = os.path.join(vscode_dir, "settings.c")
        with open(vscode_file, "w") as f:
            f.write("int vscode_settings() { return 0; }")

        # Create visible files
        visible_file = self.create_test_file("main.c", "int main() { return 0; }")

        # Parse the project
        model = self.c_parser.parse_project(self.temp_dir, recursive=True)

        # Verify excluded patterns are filtered out
        self.assertEqual(len(model.files), 1)
        self.assertIn("main.c", model.files)
        self.assertNotIn(".git/config.c", model.files)
        self.assertNotIn("__pycache__/test.c", model.files)
        self.assertNotIn(".vscode/settings.c", model.files)

    def test_recursive_vs_non_recursive_scanning(self):
        """Test recursive vs non-recursive directory scanning"""
        # Create subdirectory structure
        subdir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(subdir)
        
        root_file = self.create_test_file("root.c", "int root() { return 0; }")
        sub_file = os.path.join(subdir, "sub.c")
        with open(sub_file, "w") as f:
            f.write("int sub() { return 0; }")

        # Test non-recursive scanning
        model_non_recursive = self.c_parser.parse_project(self.temp_dir, recursive=False)
        self.assertEqual(len(model_non_recursive.files), 1)
        self.assertIn("root.c", model_non_recursive.files)
        self.assertNotIn("subdir/sub.c", model_non_recursive.files)

        # Test recursive scanning
        model_recursive = self.c_parser.parse_project(self.temp_dir, recursive=True)
        self.assertEqual(len(model_recursive.files), 2)
        self.assertIn("root.c", model_recursive.files)
        self.assertIn("subdir/sub.c", model_recursive.files)

    def test_multiple_c_extensions(self):
        """Test that all C/C++ file extensions are supported"""
        extensions = [".c", ".h", ".cpp", ".cc", ".cxx", ".hpp", ".hxx"]
        
        for ext in extensions:
            filename = f"test{ext}"
            content = f"int test_{ext[1:]}() {{ return 0; }}"
            self.create_test_file(filename, content)

        # Parse the project
        model = self.c_parser.parse_project(self.temp_dir, recursive=False)

        # Verify all extensions are included
        self.assertEqual(len(model.files), len(extensions))
        for ext in extensions:
            filename = f"test{ext}"
            self.assertIn(filename, model.files)

    def test_nested_directory_structure(self):
        """Test parsing with complex nested directory structure"""
        # Create nested structure
        level1 = os.path.join(self.temp_dir, "level1")
        level2 = os.path.join(level1, "level2")
        level3 = os.path.join(level2, "level3")
        
        os.makedirs(level3)
        
        # Create files at different levels
        root_file = self.create_test_file("root.c", "int root() { return 0; }")
        level1_file = os.path.join(level1, "level1.c")
        with open(level1_file, "w") as f:
            f.write("int level1_func() { return 0; }")
        
        level2_file = os.path.join(level2, "level2.c")
        with open(level2_file, "w") as f:
            f.write("int level2_func() { return 0; }")
        
        level3_file = os.path.join(level3, "level3.c")
        with open(level3_file, "w") as f:
            f.write("int level3_func() { return 0; }")

        # Parse recursively
        model = self.c_parser.parse_project(self.temp_dir, recursive=True)

        # Verify all files are found
        self.assertEqual(len(model.files), 4)
        self.assertIn("root.c", model.files)
        self.assertIn("level1/level1.c", model.files)
        self.assertIn("level1/level2/level2.c", model.files)
        self.assertIn("level1/level2/level3/level3.c", model.files)

    def test_file_encoding_handling(self):
        """Test that files with different encodings are handled properly"""
        # Create files with different content
        simple_file = self.create_test_file("simple.c", "int simple() { return 0; }")
        
        # Create file with special characters
        special_file = self.create_test_file("special.c", "// Comment with émojis 🚀\nint special() { return 0; }")

        # Parse the project
        model = self.c_parser.parse_project(self.temp_dir, recursive=False)

        # Verify both files are parsed successfully
        self.assertEqual(len(model.files), 2)
        self.assertIn("simple.c", model.files)
        self.assertIn("special.c", model.files)

        # Verify encoding information is captured
        simple_model = model.files["simple.c"]
        special_model = model.files["special.c"]
        self.assertIsNotNone(simple_model.encoding_used)
        self.assertIsNotNone(special_model.encoding_used)

    def test_empty_directory_handling(self):
        """Test handling of empty directories"""
        # Create empty subdirectory
        empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(empty_dir)

        # Parse the project
        model = self.c_parser.parse_project(self.temp_dir, recursive=True)

        # Verify empty directory doesn't cause issues
        self.assertEqual(len(model.files), 0)
        self.assertEqual(model.project_name, os.path.basename(self.temp_dir))

    def test_invalid_project_root_handling(self):
        """Test error handling for invalid project roots"""
        # Test non-existent directory
        with self.assertRaises(ValueError):
            self.c_parser.parse_project("/non/existent/path")

        # Test file instead of directory
        test_file = self.create_test_file("test.txt", "This is a file")
        with self.assertRaises(ValueError):
            self.c_parser.parse_project(test_file)

    def test_parser_integration_with_filtering(self):
        """Test the main Parser class integration with filtering"""
        # Create test files
        self.create_test_file("main.c", "int main() { return 0; }")
        self.create_test_file("header.h", "#define MAX 100")
        
        # Create file that should be excluded
        hidden_file = self.create_test_file(".hidden.c", "int hidden() { return 0; }")

        # Use the main Parser class
        output_file = os.path.join(self.temp_dir, "model.json")
        result = self.parser.parse(self.temp_dir, output_file, recursive=False)

        # Verify output file was created
        self.assertEqual(result, output_file)
        self.assertTrue(os.path.exists(output_file))

        # Load and verify the model
        model = ProjectModel.load(output_file)
        self.assertEqual(len(model.files), 2)
        self.assertIn("main.c", model.files)
        self.assertIn("header.h", model.files)
        self.assertNotIn(".hidden.c", model.files)

    def test_filtering_performance(self):
        """Test that filtering doesn't significantly impact performance"""
        import time
        
        # Create many files with different patterns
        c_file_count = 0
        for i in range(50):
            if i % 5 == 0:
                # Create hidden files
                self.create_test_file(f".hidden_{i}.c", f"int hidden_{i}() {{ return {i}; }}")
            elif i % 3 == 0:
                # Create non-C files
                self.create_test_file(f"file_{i}.txt", f"Text file {i}")
            else:
                # Create C files
                self.create_test_file(f"file_{i}.c", f"int func_{i}() {{ return {i}; }}")
                c_file_count += 1

        # Measure parsing time
        start_time = time.time()
        model = self.c_parser.parse_project(self.temp_dir, recursive=False)
        end_time = time.time()

        # Verify filtering worked correctly
        self.assertEqual(len(model.files), c_file_count)
        
        # Verify performance is reasonable (should complete in under 1 second)
        self.assertLess(end_time - start_time, 1.0)


if __name__ == "__main__":
    unittest.main()