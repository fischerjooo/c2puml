#!/usr/bin/env python3
"""
Feature tests for multiple source folders functionality
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from c_to_plantuml.config import Config
from c_to_plantuml.main import main
from c_to_plantuml.parser import Parser


class TestMultipleSourceFolders(unittest.TestCase):
    """Test cases for multiple source folders functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.project1_dir = os.path.join(self.temp_dir, "project1")
        self.project2_dir = os.path.join(self.temp_dir, "project2")
        self.project3_dir = os.path.join(self.temp_dir, "project3")
        
        # Create project directories
        os.makedirs(self.project1_dir, exist_ok=True)
        os.makedirs(self.project2_dir, exist_ok=True)
        os.makedirs(self.project3_dir, exist_ok=True)
        
        # Create test files in each project
        self._create_test_files()

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_test_files(self):
        """Create test C files in each project"""
        # Project 1: Basic structures
        project1_main = os.path.join(self.project1_dir, "main.c")
        with open(project1_main, "w") as f:
            f.write("""
#include "utils.h"

struct Person {
    char name[50];
    int age;
};

int main() {
    struct Person p = {"John", 30};
    return 0;
}
""")

        project1_utils = os.path.join(self.project1_dir, "utils.h")
        with open(project1_utils, "w") as f:
            f.write("""
#ifndef UTILS_H
#define UTILS_H

typedef struct {
    int x, y;
} Point;

void print_point(Point p);

#endif
""")

        # Project 2: Enums and functions
        project2_main = os.path.join(self.project2_dir, "app.c")
        with open(project2_main, "w") as f:
            f.write("""
#include "types.h"

enum Color {
    RED,
    GREEN,
    BLUE
};

void process_color(enum Color c) {
    // Process color
}
""")

        project2_types = os.path.join(self.project2_dir, "types.h")
        with open(project2_types, "w") as f:
            f.write("""
#ifndef TYPES_H
#define TYPES_H

typedef unsigned int uint32_t;
typedef struct {
    uint32_t id;
    char name[100];
} Item;

#endif
""")

        # Project 3: Complex structures
        project3_main = os.path.join(self.project3_dir, "complex.c")
        with open(project3_main, "w") as f:
            f.write("""
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
""")

        project3_data = os.path.join(self.project3_dir, "data.h")
        with open(project3_data, "w") as f:
            f.write("""
#ifndef DATA_H
#define DATA_H

#define MAX_SIZE 100

typedef struct {
    int values[MAX_SIZE];
    int count;
} Array;

#endif
""")

    def create_config_file(self, source_folders):
        """Create a configuration file with specified source folders"""
        config_data = {
            "project_name": "multi_project_test",
            "source_folders": source_folders,
            "output_dir": os.path.join(self.temp_dir, "output"),
            "recursive_search": True,
            "include_depth": 1
        }
        
        config_path = os.path.join(self.temp_dir, "config.json")
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)
        
        return config_path

    def test_multiple_source_folders_parsing(self):
        """Test that multiple source folders are parsed correctly"""
        config_path = self.create_config_file([
            self.project1_dir,
            self.project2_dir,
            self.project3_dir
        ])
        
        # Load config to verify it's correct
        config = Config.load(config_path)
        self.assertEqual(len(config.source_folders), 3)
        self.assertEqual(config.source_folders[0], self.project1_dir)
        self.assertEqual(config.source_folders[1], self.project2_dir)
        self.assertEqual(config.source_folders[2], self.project3_dir)

    def test_parser_multiple_projects_method(self):
        """Test the parse_multiple_projects method directly"""
        parser = Parser()
        output_file = os.path.join(self.temp_dir, "combined_model.json")
        
        # Test with multiple source folders
        result = parser.parse_multiple_projects(
            source_folders=[self.project1_dir, self.project2_dir, self.project3_dir],
            output_file=output_file,
            recursive_search=True
        )
        
        self.assertEqual(result, output_file)
        self.assertTrue(os.path.exists(output_file))
        
        # Load and verify the combined model
        with open(output_file, "r") as f:
            model_data = json.load(f)
        
        # Check that files from all projects are included
        files = model_data.get("files", {})
        self.assertGreater(len(files), 0)
        
        # Check for files from each project
        project1_files = [f for f in files.keys() if f.startswith("project1_")]
        project2_files = [f for f in files.keys() if f.startswith("project2_")]
        project3_files = [f for f in files.keys() if f.startswith("project3_")]
        
        self.assertGreater(len(project1_files), 0)
        self.assertGreater(len(project2_files), 0)
        self.assertGreater(len(project3_files), 0)
        
        # Verify specific files are present
        self.assertTrue(any("main.c" in f for f in project1_files))
        self.assertTrue(any("app.c" in f for f in project2_files))
        self.assertTrue(any("complex.c" in f for f in project3_files))

    def test_single_source_folder_backward_compatibility(self):
        """Test that single source folder still works (backward compatibility)"""
        parser = Parser()
        output_file = os.path.join(self.temp_dir, "single_model.json")
        
        # Test with single source folder
        result = parser.parse(
            project_root=self.project1_dir,
            output_file=output_file,
            recursive_search=True
        )
        
        self.assertEqual(result, output_file)
        self.assertTrue(os.path.exists(output_file))
        
        # Load and verify the model
        with open(output_file, "r") as f:
            model_data = json.load(f)
        
        files = model_data.get("files", {})
        self.assertGreater(len(files), 0)
        
        # Check that files are present without project prefix
        self.assertTrue(any("main.c" in f for f in files.keys()))

    def test_empty_source_folders_error(self):
        """Test that empty source folders list raises an error"""
        parser = Parser()
        output_file = os.path.join(self.temp_dir, "error_model.json")
        
        with self.assertRaises(ValueError):
            parser.parse_multiple_projects(
                source_folders=[],
                output_file=output_file,
                recursive_search=True
            )

    def test_invalid_source_folder_error(self):
        """Test that invalid source folder raises an error"""
        parser = Parser()
        output_file = os.path.join(self.temp_dir, "error_model.json")
        
        with self.assertRaises(Exception):  # Should raise some kind of error
            parser.parse_multiple_projects(
                source_folders=["/nonexistent/path"],
                output_file=output_file,
                recursive_search=True
            )

    def test_multiple_source_folders_with_config(self):
        """Test multiple source folders with configuration and filters"""
        config_path = self.create_config_file([
            self.project1_dir,
            self.project2_dir
        ])
        
        config = Config.load(config_path)
        
        # Add some filters to test they work with multiple projects
        config.file_filters = {
            "include": [".*\\.c$", ".*\\.h$"]
        }
        
        parser = Parser()
        output_file = os.path.join(self.temp_dir, "filtered_model.json")
        
        result = parser.parse_multiple_projects(
            source_folders=config.source_folders,
            output_file=output_file,
            recursive_search=config.recursive_search,
            config=config
        )
        
        self.assertEqual(result, output_file)
        self.assertTrue(os.path.exists(output_file))

    def test_project_name_collision_handling(self):
        """Test that files with same names from different projects are handled correctly"""
        # Create a file with the same name in different projects
        same_name_file1 = os.path.join(self.project1_dir, "common.h")
        same_name_file2 = os.path.join(self.project2_dir, "common.h")
        
        with open(same_name_file1, "w") as f:
            f.write("#ifndef COMMON1_H\n#define COMMON1_H\nint project1_var;\n#endif\n")
        
        with open(same_name_file2, "w") as f:
            f.write("#ifndef COMMON2_H\n#define COMMON2_H\nint project2_var;\n#endif\n")
        
        parser = Parser()
        output_file = os.path.join(self.temp_dir, "collision_model.json")
        
        result = parser.parse_multiple_projects(
            source_folders=[self.project1_dir, self.project2_dir],
            output_file=output_file,
            recursive_search=True
        )
        
        self.assertEqual(result, output_file)
        
        # Load and verify both files are present with different keys
        with open(output_file, "r") as f:
            model_data = json.load(f)
        
        files = model_data.get("files", {})
        
        # Check that both common.h files are present with project prefixes
        project1_common = [f for f in files.keys() if f.startswith("project1_") and "common.h" in f]
        project2_common = [f for f in files.keys() if f.startswith("project2_") and "common.h" in f]
        
        self.assertEqual(len(project1_common), 1)
        self.assertEqual(len(project2_common), 1)
        self.assertNotEqual(project1_common[0], project2_common[0])


if __name__ == "__main__":
    unittest.main()