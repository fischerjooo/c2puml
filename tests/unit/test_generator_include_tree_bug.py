#!/usr/bin/env python3
"""
Unit tests for generator include tree bug detection
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

# Add src directory to path for new package structure
test_dir = os.path.dirname(__file__)
src_path = os.path.join(test_dir, "..", "..", "src")
if os.path.exists(src_path):
    sys.path.insert(0, src_path)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from c2puml.generator import Generator
from c2puml.models import (
    FileModel,
    ProjectModel,
)


class TestGeneratorIncludeTreeBug(unittest.TestCase):
    """Test the bug in _build_include_tree method with absolute paths"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = Generator()
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_build_include_tree_with_absolute_paths(self):
        """Test that _build_include_tree works correctly with absolute paths"""
        # Create test files with absolute paths
        main_c_path = self.test_dir / "main.c"
        utils_h_path = self.test_dir / "utils.h"

        # Create the actual files
        with open(main_c_path, "w") as f:
            f.write('#include "utils.h"\n')

        with open(utils_h_path, "w") as f:
            f.write("// utils.h content\n")

        # Create FileModel instances with absolute paths
        main_file_model = FileModel(file_path=str(main_c_path), includes={"utils.h"})

        utils_file_model = FileModel(file_path=str(utils_h_path), includes=set())

        # Create ProjectModel with filenames as keys (consistent with parser behavior)
        project_model = ProjectModel(
            project_name="test_project",
            source_folder=str(self.test_dir),
            files={"main.c": main_file_model, "utils.h": utils_file_model},
        )

        # Test the _build_include_tree method
        include_tree = self.generator._build_include_tree(
            main_file_model, project_model, include_depth=1
        )

        # The method should find both files using the correct keys from project_model.files
        expected_files = {"main.c", "utils.h"}
        actual_files = set(include_tree.keys())

        # This test should now pass with the fix
        self.assertEqual(
            actual_files,
            expected_files,
            f"Expected to find {expected_files}, but found {actual_files}",
        )

    def test_build_include_tree_with_relative_paths(self):
        """Test that _build_include_tree works correctly with relative paths (control test)"""
        # Create test files with relative paths
        main_c_path = self.test_dir / "main.c"
        utils_h_path = self.test_dir / "utils.h"

        # Create the actual files
        with open(main_c_path, "w") as f:
            f.write('#include "utils.h"\n')

        with open(utils_h_path, "w") as f:
            f.write("// utils.h content\n")

        # Create FileModel instances with relative paths
        main_file_model = FileModel(file_path="main.c", includes={"utils.h"})

        utils_file_model = FileModel(file_path="utils.h", includes=set())

        # Create ProjectModel with filenames as keys (new behavior)
        project_model = ProjectModel(
            project_name="test_project",
            source_folder=str(self.test_dir),
            files={"main.c": main_file_model, "utils.h": utils_file_model},
        )

        # Test the _build_include_tree method
        include_tree = self.generator._build_include_tree(
            main_file_model, project_model, include_depth=1
        )

        # The method should find both files using the correct keys from project_model.files
        expected_files = {"main.c", "utils.h"}
        actual_files = set(include_tree.keys())

        # This test should now pass with the fix
        self.assertEqual(
            actual_files,
            expected_files,
            f"Expected to find {expected_files}, but found {actual_files}",
        )

    def test_build_include_tree_mixed_paths(self):
        """Test the bug with mixed absolute and relative paths"""
        # Create test files
        main_c_path = self.test_dir / "main.c"
        utils_h_path = self.test_dir / "utils.h"

        # Create the actual files
        with open(main_c_path, "w") as f:
            f.write('#include "utils.h"\n')

        with open(utils_h_path, "w") as f:
            f.write("// utils.h content\n")

        # Create FileModel instances - main.c with absolute path, utils.h with relative
        main_file_model = FileModel(file_path=str(main_c_path), includes={"utils.h"})

        utils_file_model = FileModel(file_path="utils.h", includes=set())

        # Create ProjectModel with filenames as keys (new behavior)
        project_model = ProjectModel(
            project_name="test_project",
            source_folder=str(self.test_dir),
            files={"main.c": main_file_model, "utils.h": utils_file_model},
        )

        # Test the _build_include_tree method
        include_tree = self.generator._build_include_tree(
            main_file_model, project_model, include_depth=1
        )

        # This should now work correctly with the fix
        expected_files = {"main.c", "utils.h"}
        actual_files = set(include_tree.keys())

        self.assertEqual(
            actual_files,
            expected_files,
            f"Expected to find {expected_files}, but found {actual_files}",
        )

    def test_build_include_tree_debug_info(self):
        """Test to provide debug information about the bug"""
        # Create test files
        main_c_path = self.test_dir / "main.c"
        utils_h_path = self.test_dir / "utils.h"

        # Create the actual files
        with open(main_c_path, "w") as f:
            f.write('#include "utils.h"\n')

        with open(utils_h_path, "w") as f:
            f.write("// utils.h content\n")

        # Create FileModel instances with absolute paths
        main_file_model = FileModel(file_path=str(main_c_path), includes={"utils.h"})

        utils_file_model = FileModel(file_path=str(utils_h_path), includes=set())

        # Create ProjectModel with filenames as keys (new behavior)
        project_model = ProjectModel(
            project_name="test_project",
            source_folder=str(self.test_dir),
            files={"main.c": main_file_model, "utils.h": utils_file_model},
        )

        # Debug: Print the keys in project_model.files
        print(f"Project model files keys: {list(project_model.files.keys())}")
        print(f"Root file path: {main_file_model.file_path}")
        print(f"Root file name: {Path(main_file_model.file_path).name}")
        print(f"Root file key used: {Path(main_file_model.file_path).name}")

        # Test the _build_include_tree method
        include_tree = self.generator._build_include_tree(
            main_file_model, project_model, include_depth=1
        )

        print(f"Include tree keys: {list(include_tree.keys())}")
        print(f"Expected keys: {['main.c', 'utils.h']}")

        # This test should now pass with the fix
        expected_files = {"main.c", "utils.h"}
        actual_files = set(include_tree.keys())

        self.assertEqual(
            actual_files,
            expected_files,
            f"Expected to find {expected_files}, but found {actual_files}",
        )


if __name__ == "__main__":
    unittest.main()
