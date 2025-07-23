#!/usr/bin/env python3
"""
Feature tests for include dependency processing functionality

Tests the new functionality where the parser:
1. Only parses C code files that are included or not filtered out by configuration
2. Collects all C files that need to be parsed based on configuration
3. Looks for #includes in C files and extracts header file names
4. Adds those headers to the parsing list
5. Looks for #includes in header files and adds those to the list
6. Repeats until the configured include_depth
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

from c_to_plantuml.config import Config
from c_to_plantuml.parser import CParser


class TestIncludeDependencyProcessing(unittest.TestCase):
    """Test include dependency processing functionality"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.c_parser = CParser()

    def tearDown(self):
        """Clean up test environment"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file with given content"""
        file_path = self.project_root / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def test_basic_include_dependency_processing(self):
        """Test basic include dependency processing with depth 1"""
        # Create test files
        self.create_test_file(
            "main.c",
            """
#include "header1.h"
#include "header2.h"

int main() {
    return 0;
}
""",
        )

        self.create_test_file(
            "header1.h",
            """
#ifndef HEADER1_H
#define HEADER1_H

struct TestStruct {
    int x;
    int y;
};

#endif
""",
        )

        self.create_test_file(
            "header2.h",
            """
#ifndef HEADER2_H
#define HEADER2_H

#include "header3.h"

enum TestEnum {
    VALUE1,
    VALUE2
};

#endif
""",
        )

        self.create_test_file(
            "header3.h",
            """
#ifndef HEADER3_H
#define HEADER3_H

typedef int MyInt;

#endif
""",
        )

        # Create configuration with include_depth = 1
        config = Config(
            source_folders=[str(self.project_root)], include_depth=1, file_filters={}
        )

        # Find files with include dependencies
        files = self.c_parser._find_files_with_include_dependencies(
            self.project_root, True, config
        )

        # Should include main.c, header1.h, header2.h (header3.h is at depth 2)
        expected_files = {"main.c", "header1.h", "header2.h"}
        actual_files = {f.name for f in files}

        self.assertEqual(actual_files, expected_files)
        self.assertEqual(len(files), 3)

    def test_include_depth_limitation(self):
        """Test that include depth limitation works correctly"""
        # Create a chain of includes: main.c -> header1.h -> header2.h -> header3.h
        self.create_test_file(
            "main.c",
            """
#include "header1.h"

int main() {
    return 0;
}
""",
        )

        self.create_test_file(
            "header1.h",
            """
#ifndef HEADER1_H
#define HEADER1_H

#include "header2.h"

struct TestStruct {
    int x;
};

#endif
""",
        )

        self.create_test_file(
            "header2.h",
            """
#ifndef HEADER2_H
#define HEADER2_H

#include "header3.h"

enum TestEnum {
    VALUE1,
    VALUE2
};

#endif
""",
        )

        self.create_test_file(
            "header3.h",
            """
#ifndef HEADER3_H
#define HEADER3_H

typedef int MyInt;

#endif
""",
        )

        # Test with include_depth = 0 (no includes)
        config_depth_0 = Config(
            source_folders=[str(self.project_root)], include_depth=0, file_filters={}
        )

        files_depth_0 = self.c_parser._find_files_with_include_dependencies(
            self.project_root, True, config_depth_0
        )

        # Should only include main.c
        expected_files_depth_0 = {"main.c"}
        actual_files_depth_0 = {f.name for f in files_depth_0}
        self.assertEqual(actual_files_depth_0, expected_files_depth_0)

        # Test with include_depth = 1
        config_depth_1 = Config(
            source_folders=[str(self.project_root)], include_depth=1, file_filters={}
        )

        files_depth_1 = self.c_parser._find_files_with_include_dependencies(
            self.project_root, True, config_depth_1
        )

        # Should include main.c and header1.h
        expected_files_depth_1 = {"main.c", "header1.h"}
        actual_files_depth_1 = {f.name for f in files_depth_1}
        self.assertEqual(actual_files_depth_1, expected_files_depth_1)

        # Test with include_depth = 2
        config_depth_2 = Config(
            source_folders=[str(self.project_root)], include_depth=2, file_filters={}
        )

        files_depth_2 = self.c_parser._find_files_with_include_dependencies(
            self.project_root, True, config_depth_2
        )

        # Should include main.c, header1.h, and header2.h
        expected_files_depth_2 = {"main.c", "header1.h", "header2.h"}
        actual_files_depth_2 = {f.name for f in files_depth_2}
        self.assertEqual(actual_files_depth_2, expected_files_depth_2)

    def test_file_filtering_with_include_dependencies(self):
        """Test that file filtering works correctly with include dependencies"""
        # Create test files
        self.create_test_file(
            "main.c",
            """
#include "included.h"
#include "excluded.h"

int main() {
    return 0;
}
""",
        )

        self.create_test_file(
            "included.h",
            """
#ifndef INCLUDED_H
#define INCLUDED_H

struct IncludedStruct {
    int x;
};

#endif
""",
        )

        self.create_test_file(
            "excluded.h",
            """
#ifndef EXCLUDED_H
#define EXCLUDED_H

struct ExcludedStruct {
    int y;
};

#endif
""",
        )

        # Create configuration that excludes excluded.h
        config = Config(
            source_folders=[str(self.project_root)],
            include_depth=1,
            file_filters={"exclude": [r"excluded\.h"]},
        )

        # Find files with include dependencies
        files = self.c_parser._find_files_with_include_dependencies(
            self.project_root, True, config
        )

        # Should include main.c and included.h, but not excluded.h
        expected_files = {"main.c", "included.h"}
        actual_files = {f.name for f in files}

        self.assertEqual(actual_files, expected_files)
        self.assertEqual(len(files), 2)

    def test_circular_include_handling(self):
        """Test handling of circular include dependencies"""
        # Create circular includes: header1.h <-> header2.h
        self.create_test_file(
            "main.c",
            """
#include "header1.h"

int main() {
    return 0;
}
""",
        )

        self.create_test_file(
            "header1.h",
            """
#ifndef HEADER1_H
#define HEADER1_H

#include "header2.h"

struct Struct1 {
    int x;
};

#endif
""",
        )

        self.create_test_file(
            "header2.h",
            """
#ifndef HEADER2_H
#define HEADER2_H

#include "header1.h"

struct Struct2 {
    int y;
};

#endif
""",
        )

        # Create configuration
        config = Config(
            source_folders=[str(self.project_root)],
            include_depth=5,  # High depth to test circular handling
            file_filters={},
        )

        # Should not crash and should include all files
        files = self.c_parser._find_files_with_include_dependencies(
            self.project_root, True, config
        )

        expected_files = {"main.c", "header1.h", "header2.h"}
        actual_files = {f.name for f in files}

        self.assertEqual(actual_files, expected_files)
        self.assertEqual(len(files), 3)

    def test_system_include_handling(self):
        """Test handling of system includes (angle brackets)"""
        # Create test files with system includes
        self.create_test_file(
            "main.c",
            """
#include <stdio.h>
#include <stdlib.h>
#include "local.h"

int main() {
    return 0;
}
""",
        )

        self.create_test_file(
            "local.h",
            """
#ifndef LOCAL_H
#define LOCAL_H

struct LocalStruct {
    int x;
};

#endif
""",
        )

        # Create configuration
        config = Config(
            source_folders=[str(self.project_root)], include_depth=1, file_filters={}
        )

        # Find files with include dependencies
        files = self.c_parser._find_files_with_include_dependencies(
            self.project_root, True, config
        )

        # Should include main.c and local.h, but not system headers
        expected_files = {"main.c", "local.h"}
        actual_files = {f.name for f in files}

        self.assertEqual(actual_files, expected_files)
        self.assertEqual(len(files), 2)

    def test_mixed_include_quotes(self):
        """Test handling of different include quote styles"""
        # Create test files with mixed quote styles
        self.create_test_file(
            "main.c",
            """
#include "header1.h"
#include <system.h>
#include 'header2.h'

int main() {
    return 0;
}
""",
        )

        self.create_test_file(
            "header1.h",
            """
#ifndef HEADER1_H
#define HEADER1_H

struct Struct1 {
    int x;
};

#endif
""",
        )

        self.create_test_file(
            "header2.h",
            """
#ifndef HEADER2_H
#define HEADER2_H

struct Struct2 {
    int y;
};

#endif
""",
        )

        # Create configuration
        config = Config(
            source_folders=[str(self.project_root)], include_depth=1, file_filters={}
        )

        # Find files with include dependencies
        files = self.c_parser._find_files_with_include_dependencies(
            self.project_root, True, config
        )

        # Should include main.c, header1.h, and header2.h
        expected_files = {"main.c", "header1.h", "header2.h"}
        actual_files = {f.name for f in files}

        self.assertEqual(actual_files, expected_files)
        self.assertEqual(len(files), 3)

    def test_subdirectory_include_handling(self):
        """Test handling of includes in subdirectories"""
        # Create directory structure
        subdir = self.project_root / "include"
        subdir.mkdir()

        self.create_test_file(
            "main.c",
            """
#include "include/header1.h"
#include "include/subdir/header2.h"

int main() {
    return 0;
}
""",
        )

        self.create_test_file(
            "include/header1.h",
            """
#ifndef HEADER1_H
#define HEADER1_H

struct Struct1 {
    int x;
};

#endif
""",
        )

        subsubdir = subdir / "subdir"
        subsubdir.mkdir()
        self.create_test_file(
            "include/subdir/header2.h",
            """
#ifndef HEADER2_H
#define HEADER2_H

struct Struct2 {
    int y;
};

#endif
""",
        )

        # Create configuration
        config = Config(
            source_folders=[str(self.project_root)], include_depth=1, file_filters={}
        )

        # Find files with include dependencies
        files = self.c_parser._find_files_with_include_dependencies(
            self.project_root, True, config
        )

        # Should include main.c and both header files
        expected_files = {"main.c", "header1.h", "header2.h"}
        actual_files = {f.name for f in files}

        self.assertEqual(actual_files, expected_files)
        self.assertEqual(len(files), 3)

    def test_no_config_fallback(self):
        """Test that the parser falls back to old behavior when no config is provided"""
        # Create test files
        self.create_test_file(
            "main.c",
            """
#include "header1.h"

int main() {
    return 0;
}
""",
        )

        self.create_test_file(
            "header1.h",
            """
#ifndef HEADER1_H
#define HEADER1_H

struct TestStruct {
    int x;
};

#endif
""",
        )

        # Call without config (should use old _find_c_files method)
        files = self.c_parser._find_files_with_include_dependencies(
            self.project_root, True, None
        )

        # Should include all C files (no include processing)
        expected_files = {"main.c", "header1.h"}
        actual_files = {f.name for f in files}

        self.assertEqual(actual_files, expected_files)
        self.assertEqual(len(files), 2)

    def test_include_extraction_from_file(self):
        """Test extracting includes from a file"""
        # Create a file with various include statements
        test_file = self.create_test_file(
            "test.c",
            """
#include <stdio.h>
#include <stdlib.h>
#include "local1.h"
#include "local2.h"
#include "subdir/header.h"

// Some code
int main() {
    return 0;
}
""",
        )

        # Extract includes
        includes = self.c_parser._extract_includes_from_file(test_file)

        # Should extract all include statements
        expected_includes = [
            "stdio.h",
            "stdlib.h",
            "local1.h",
            "local2.h",
            "subdir/header.h",
        ]
        self.assertEqual(includes, expected_includes)

    def test_find_included_file(self):
        """Test finding included file paths"""
        # Create test files
        self.create_test_file("main.c", "")
        self.create_test_file("header.h", "")
        self.create_test_file("include/header2.h", "")

        # Test finding local header
        included_file = self.c_parser._find_included_file(
            "header.h", self.project_root / "main.c", self.project_root
        )
        self.assertEqual(included_file, self.project_root / "header.h")

        # Test finding header in subdirectory
        included_file = self.c_parser._find_included_file(
            "include/header2.h", self.project_root / "main.c", self.project_root
        )
        self.assertEqual(included_file, self.project_root / "include" / "header2.h")

        # Test system include (should return None)
        included_file = self.c_parser._find_included_file(
            "<stdio.h>", self.project_root / "main.c", self.project_root
        )
        self.assertIsNone(included_file)

        # Test non-existent file (should return None)
        included_file = self.c_parser._find_included_file(
            "nonexistent.h", self.project_root / "main.c", self.project_root
        )
        self.assertIsNone(included_file)


if __name__ == "__main__":
    unittest.main()
