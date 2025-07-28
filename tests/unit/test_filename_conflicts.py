#!/usr/bin/env python3
"""
Test filename conflict handling in the parser
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from c_to_plantuml.parser import CParser
from c_to_plantuml.models import FileModel


class TestFilenameConflicts(unittest.TestCase):
    """Test that filename conflicts are handled correctly"""

    def setUp(self):
        self.parser = CParser()
        self.temp_dir = TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_filename_conflicts_handled(self):
        """Test that files with the same name in different directories are handled correctly"""
        # Create test directory structure
        dir1 = self.test_dir / "dir1"
        dir2 = self.test_dir / "dir2"
        dir1.mkdir()
        dir2.mkdir()

        # Create files with the same name in different directories
        file1 = dir1 / "test.h"
        file2 = dir2 / "test.h"

        with open(file1, "w") as f:
            f.write("// test.h in dir1\nstruct Test1 { int x; };\n")

        with open(file2, "w") as f:
            f.write("// test.h in dir2\nstruct Test2 { int y; };\n")

        # Parse the project
        project_model = self.parser.parse_project(str(self.test_dir), recursive_search=True)

        # Check that both files are present with different keys
        file_keys = list(project_model.files.keys())
        self.assertEqual(len(file_keys), 2, f"Expected 2 files, got {len(file_keys)}: {file_keys}")

        # Check that one key is just the filename and the other has a hash
        filename_keys = [key for key in file_keys if key == "test.h"]
        hash_keys = [key for key in file_keys if key.startswith("test.h_") and len(key) > 8]

        self.assertEqual(len(filename_keys), 1, f"Expected 1 plain filename key, got {len(filename_keys)}")
        self.assertEqual(len(hash_keys), 1, f"Expected 1 hash key, got {len(hash_keys)}")

        # Verify that both files have the correct content
        plain_file = project_model.files[filename_keys[0]]
        hash_file = project_model.files[hash_keys[0]]

        # Check that both files have structs (indicating they were parsed correctly)
        self.assertTrue(len(plain_file.structs) > 0 or len(hash_file.structs) > 0)
        self.assertTrue(len(plain_file.structs) + len(hash_file.structs) == 2)

    def test_no_filename_conflicts(self):
        """Test that files with different names work normally"""
        # Create files with different names
        file1 = self.test_dir / "test1.h"
        file2 = self.test_dir / "test2.h"

        with open(file1, "w") as f:
            f.write("// test1.h\nstruct Test1 { int x; };\n")

        with open(file2, "w") as f:
            f.write("// test2.h\nstruct Test2 { int y; };\n")

        # Parse the project
        project_model = self.parser.parse_project(str(self.test_dir), recursive_search=True)

        # Check that both files are present with simple filename keys
        file_keys = list(project_model.files.keys())
        self.assertEqual(len(file_keys), 2, f"Expected 2 files, got {len(file_keys)}: {file_keys}")
        self.assertIn("test1.h", file_keys)
        self.assertIn("test2.h", file_keys)

        # Verify that both files have the correct content
        file1_model = project_model.files["test1.h"]
        file2_model = project_model.files["test2.h"]

        self.assertEqual(len(file1_model.structs), 1)
        self.assertEqual(len(file2_model.structs), 1)


if __name__ == "__main__":
    unittest.main()