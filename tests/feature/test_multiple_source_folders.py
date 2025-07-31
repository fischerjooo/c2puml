#!/usr/bin/env python3
"""
Multiple Source Folders tests.

Comprehensive test suite for verifying the functionality of
multiple source folders components.
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path



# Add src directory to path for new package structure
import sys
import os
from pathlib import Path

# Get the absolute path to the src directory 
current_file = Path(__file__).resolve()
test_dir = current_file.parent
project_root = test_dir.parent.parent
src_path = project_root / "src"

if src_path.exists():
    sys.path.insert(0, str(src_path))
# Also add tests directory for test utilities
tests_path = project_root / "tests"
if tests_path.exists():
    sys.path.insert(0, str(tests_path))

from c2puml.config import Config
from c2puml.main import main
from c2puml.parser import Parser
from tests.feature.base import BaseFeatureTest



class TestMultipleSourceFolders(BaseFeatureTest):
    """Test cases for multiple source folders functionality within a single project"""

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        self.source_folder1 = os.path.join(self.temp_dir, "src1")
        self.source_folder2 = os.path.join(self.temp_dir, "src2")
        self.source_folder3 = os.path.join(self.temp_dir, "src3")

        # Create source folder directories
        os.makedirs(self.source_folder1, exist_ok=True)
        os.makedirs(self.source_folder2, exist_ok=True)
        os.makedirs(self.source_folder3, exist_ok=True)

        # Create test files in each source folder
        self._create_test_files()

    def tearDown(self):
        """Clean up test fixtures"""
        super().tearDown()

    def _create_test_files(self):
        """Create test C files in each source folder"""
        # Source folder 1: Basic structures
        src1_main = os.path.join(self.source_folder1, "main.c")
        with open(src1_main, "w") as f:
            f.write(
                """
#include "utils.h"

struct Person {
    char name[50];
    int age;
};

int main() {
    struct Person p = {"John", 30};
    return 0;
}
"""
            )

        src1_utils = os.path.join(self.source_folder1, "utils.h")
        with open(src1_utils, "w") as f:
            f.write(
                """
#ifndef UTILS_H
#define UTILS_H

typedef struct {
    int x, y;
} Point;

void print_point(Point p);

#endif
"""
            )

        # Source folder 2: Enums and functions
        src2_main = os.path.join(self.source_folder2, "app.c")
        with open(src2_main, "w") as f:
            f.write(
                """
#include "types.h"

enum Color {
    RED,
    GREEN,
    BLUE
};

void process_color(enum Color c) {
    // Process color
}
"""
            )

        src2_types = os.path.join(self.source_folder2, "types.h")
        with open(src2_types, "w") as f:
            f.write(
                """
#ifndef TYPES_H
#define TYPES_H

typedef unsigned int uint32_t;
typedef struct {
    uint32_t id;
    char name[100];
} Item;

#endif
"""
            )

        # Source folder 3: Complex structures
        src3_main = os.path.join(self.source_folder3, "complex.c")
        with open(src3_main, "w") as f:
            f.write(
                """
#include "data.h"

union Data {
    int i;
    float f;
    char str[20];
};

struct Container {
    union Data data;
    int type;
};
"""
            )

        src3_data = os.path.join(self.source_folder3, "data.h")
        with open(src3_data, "w") as f:
            f.write(
                """
#ifndef DATA_H
#define DATA_H

#define MAX_SIZE 100

typedef struct {
    int values[MAX_SIZE];
    int count;
} Array;

#endif
"""
            )

    def create_config_file(self, source_folders):
        """Create a configuration file with specified source folders"""
        config_data = {
            "project_name": "multi_source_test",
            "source_folders": source_folders,
            "output_dir": os.path.join(self.temp_dir, "output"),
            "recursive_search": True,
            "include_depth": 1,
        }

        config_path = os.path.join(self.temp_dir, "config.json")
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)

        return config_path

    def test_multiple_source_folders_parsing(self):
        """Test that multiple source folders are parsed correctly"""
        config_path = self.create_config_file(
            [self.source_folder1, self.source_folder2, self.source_folder3]
        )

        # Load config to verify it's correct
        config = Config.load(config_path)
        self.assertEqual(len(config.source_folders), 3)
        self.assertEqual(config.source_folders[0], self.source_folder1)
        self.assertEqual(config.source_folders[1], self.source_folder2)
        self.assertEqual(config.source_folders[2], self.source_folder3)

    def test_parser_multiple_source_folders_method(self):
        """Test the parse method with multiple source folders"""
        parser = Parser()
        output_file = os.path.join(self.temp_dir, "combined_model.json")

        # Test with multiple source folders
        result = parser.parse(
            source_folders=[
                self.source_folder1,
                self.source_folder2,
                self.source_folder3,
            ],
            output_file=output_file,
            recursive_search=True,
        )

        self.assertEqual(result, output_file)
        self.assertTrue(os.path.exists(output_file))

        # Load and verify the combined model
        with open(output_file, "r") as f:
            model_data = json.load(f)

        # Check that files from all source folders are included
        files = model_data.get("files", {})
        self.assertGreater(len(files), 0)

        # Verify specific files are present
        self.assertTrue(any("main.c" in f for f in files))
        self.assertTrue(any("app.c" in f for f in files))
        self.assertTrue(any("complex.c" in f for f in files))

    def test_single_source_folder_backward_compatibility(self):
        """Test that single source folder still works (backward compatibility)"""
        parser = Parser()
        output_file = os.path.join(self.temp_dir, "single_model.json")

        # Test with single source folder (list with one element)
        result = parser.parse(
            source_folders=[self.source_folder1],
            output_file=output_file,
            recursive_search=True,
        )

        self.assertEqual(result, output_file)
        self.assertTrue(os.path.exists(output_file))

        # Load and verify the model
        with open(output_file, "r") as f:
            model_data = json.load(f)

        files = model_data.get("files", {})
        self.assertGreater(len(files), 0)

        # Check that files are present without source folder prefix
        self.assertTrue(any("main.c" in f for f in files.keys()))

    def test_empty_source_folders_error(self):
        """Test that empty source_folders list raises an error"""
        parser = Parser()
        output_file = os.path.join(self.temp_dir, "error_model.json")

        with self.assertRaises(ValueError):
            parser.parse(
                source_folders=[], output_file=output_file, recursive_search=True
            )

    def test_invalid_source_folder_error(self):
        """Test that invalid source folder raises an error"""
        parser = Parser()
        output_file = os.path.join(self.temp_dir, "error_model.json")

        with self.assertRaises(Exception):  # Should raise some kind of error
            parser.parse(
                source_folders=["/nonexistent/path"],
                output_file=output_file,
                recursive_search=True,
            )

    def test_multiple_source_folders_with_config(self):
        """Test multiple source folders with configuration and filters"""
        config_path = self.create_config_file(
            [self.source_folder1, self.source_folder2]
        )

        config = Config.load(config_path)

        # Add some filters to test they work with multiple source folders
        config.file_filters = {"include": [".*\\.c$", ".*\\.h$"]}

        parser = Parser()
        output_file = os.path.join(self.temp_dir, "filtered_model.json")

        result = parser.parse(
            source_folders=config.source_folders,
            output_file=output_file,
            recursive_search=config.recursive_search,
            config=config,
        )

        self.assertEqual(result, output_file)
        self.assertTrue(os.path.exists(output_file))

    def test_project_name_from_config(self):
        """Test that project name is taken from configuration"""
        config_path = self.create_config_file(
            [self.source_folder1, self.source_folder2]
        )

        config = Config.load(config_path)
        config.project_name = "TestProject"

        parser = Parser()
        output_file = os.path.join(self.temp_dir, "named_model.json")

        result = parser.parse(
            source_folders=config.source_folders,
            output_file=output_file,
            recursive_search=True,
            config=config,
        )

        self.assertEqual(result, output_file)

        # Load and verify the project name is correct
        with open(output_file, "r") as f:
            model_data = json.load(f)

        self.assertEqual(model_data.get("project_name"), "TestProject")


if __name__ == "__main__":
    unittest.main()
