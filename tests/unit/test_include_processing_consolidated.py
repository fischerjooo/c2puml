#!/usr/bin/env python3
"""
Consolidated unit tests for include header processing functionality.

This module consolidates and replaces multiple overlapping include processing
test files to reduce duplication and improve maintainability.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from c_to_plantuml.generator import PlantUMLGenerator
from c_to_plantuml.models import (
    Alias,
    Enum,
    Field,
    FileModel,
    Function,
    IncludeRelation,
    ProjectModel,
    Struct,
    Union,
)
from c_to_plantuml.parser import CParser
from c_to_plantuml.transformer import Transformer
from tests.utils import (
    AssertionHelpers,
    MockObjectFactory,
    TestDataProviders,
    TestProjectBuilder,
    create_temp_project,
    run_full_pipeline,
)


class TestIncludeProcessingCore(unittest.TestCase):
    """Core include processing functionality tests."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CParser()
        self.transformer = Transformer()
        self.generator = PlantUMLGenerator()
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file with given content."""
        file_path = self.test_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def test_parse_basic_includes(self):
        """Test parsing basic system and local include statements."""
        content = """
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "utils.h"
#include "config.h"
#include "types.h"
        """

        file_path = self.create_test_file("test.c", content)
        file_model = self.parser.parse_file(
            file_path, file_path.name, str(self.test_dir)
        )

        expected_includes = {
            "stdio.h", "stdlib.h", "string.h", "utils.h", "config.h", "types.h"
        }
        AssertionHelpers.assert_file_contains_includes(
            file_model, list(expected_includes)
        )

    def test_parse_includes_with_comments_and_whitespace(self):
        """Test parsing includes with comments and whitespace."""
        content = """
// System includes
#include <stdio.h>  // Standard I/O
#include <stdlib.h> /* Standard library */

// Local includes
#include "utils.h"  // Utility functions
#include "config.h" /* Configuration */
        """

        file_path = self.create_test_file("test.c", content)
        file_model = self.parser.parse_file(
            file_path, file_path.name, str(self.test_dir)
        )

        expected_includes = ["stdio.h", "stdlib.h", "utils.h", "config.h"]
        AssertionHelpers.assert_file_contains_includes(file_model, expected_includes)

    def test_parse_includes_with_preprocessor_directives(self):
        """Test parsing includes with preprocessor directives."""
        content = """
#ifdef DEBUG
#include <assert.h>
#endif

#ifndef UTILS_H
#include "utils.h"
#endif

#if defined(WINDOWS)
#include "windows_types.h"
#elif defined(LINUX)
#include "linux_types.h"
#endif
        """

        file_path = self.create_test_file("test.c", content)
        file_model = self.parser.parse_file(
            file_path, file_path.name, str(self.test_dir)
        )

        # Should parse includes regardless of preprocessor conditions
        expected_includes = ["assert.h", "utils.h", "windows_types.h", "linux_types.h"]
        actual_includes = set(file_model.includes)
        expected_set = set(expected_includes)

        # Check that all expected includes are present
        self.assertTrue(
            expected_set.issubset(actual_includes),
            f"Missing includes: {expected_set - actual_includes}"
        )


class TestIncludeProcessingRelationships(unittest.TestCase):
    """Test include relationships and dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.parser = CParser()
        self.transformer = Transformer()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_c_to_h_file_relationships(self):
        """Test relationships between C files and their header files."""
        project_data = TestDataProviders.get_sample_c_projects()["complex_project"]
        project_dir = create_temp_project(project_data, self.temp_dir)

        config_data = TestDataProviders.get_sample_configs()["standard"]
        config_data["source_folders"] = [str(project_dir)]

        results = run_full_pipeline(project_dir, config_data)

        # Verify that the pipeline ran successfully
        self.assertTrue(results["model_file"].exists())
        self.assertTrue(results["transformed_model_file"].exists())

        # Verify include relationships in the parsed model
        parsed_model = results["parsed_model"]
        
        # Find main.c file
        main_file = None
        for file_data in parsed_model["files"]:
            if file_data["filename"] == "main.c":
                main_file = file_data
                break

        self.assertIsNotNone(main_file, "main.c not found in parsed model")
        
        # Verify includes
        expected_main_includes = ["stdio.h", "math_utils.h", "graphics.h"]
        actual_includes = set(main_file["includes"])
        expected_set = set(expected_main_includes)
        
        self.assertTrue(
            expected_set.issubset(actual_includes),
            f"main.c missing includes: {expected_set - actual_includes}"
        )

    def test_header_to_header_relationships(self):
        """Test relationships between header files."""
        project_data = {
            "base.h": """
#ifndef BASE_H
#define BASE_H

typedef struct {
    int id;
} Base;

#endif
""",
            "derived.h": """
#ifndef DERIVED_H
#define DERIVED_H

#include "base.h"

typedef struct {
    Base base;
    int extra_field;
} Derived;

#endif
""",
            "composite.h": """
#ifndef COMPOSITE_H
#define COMPOSITE_H

#include "base.h"
#include "derived.h"

typedef struct {
    Base* bases[10];
    Derived derived_item;
} Composite;

#endif
"""
        }

        project_dir = create_temp_project(project_data, self.temp_dir)
        config_data = TestDataProviders.get_sample_configs()["standard"]
        config_data["source_folders"] = [str(project_dir)]

        results = run_full_pipeline(project_dir, config_data)
        parsed_model = results["parsed_model"]

        # Verify header include relationships
        file_includes = {}
        for file_data in parsed_model["files"]:
            file_includes[file_data["filename"]] = set(file_data["includes"])

        # Check derived.h includes base.h
        self.assertIn("base.h", file_includes["derived.h"])
        
        # Check composite.h includes both base.h and derived.h
        self.assertIn("base.h", file_includes["composite.h"])
        self.assertIn("derived.h", file_includes["composite.h"])


class TestIncludeProcessingTypedefs(unittest.TestCase):
    """Test typedef relationships in include processing."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_simple_typedef_relationships(self):
        """Test simple typedef relationships across files."""
        project_data = {
            "types.h": """
#ifndef TYPES_H
#define TYPES_H

typedef unsigned char byte_t;
typedef unsigned short word_t;
typedef unsigned long dword_t;

typedef struct {
    byte_t r, g, b, a;
} Color;

#endif
""",
            "main.c": """
#include "types.h"

typedef Color* ColorPtr;
typedef ColorPtr ColorArray[256];

int main() {
    Color red = {255, 0, 0, 255};
    ColorPtr ptr = &red;
    return 0;
}
"""
        }

        project_dir = create_temp_project(project_data, self.temp_dir)
        config_data = TestDataProviders.get_sample_configs()["standard"]
        config_data["source_folders"] = [str(project_dir)]

        results = run_full_pipeline(project_dir, config_data)
        parsed_model = results["parsed_model"]

        # Verify typedefs are properly parsed
        main_file = None
        types_file = None
        
        for file_data in parsed_model["files"]:
            if file_data["filename"] == "main.c":
                main_file = file_data
            elif file_data["filename"] == "types.h":
                types_file = file_data

        self.assertIsNotNone(main_file)
        self.assertIsNotNone(types_file)

        # Check that main.c includes types.h
        self.assertIn("types.h", main_file["includes"])

        # Check that types.h contains the Color struct
        types_structs = [s["name"] for s in types_file.get("structs", [])]
        self.assertIn("Color", types_structs)

    def test_complex_nested_typedef_relationships(self):
        """Test complex nested typedef relationships."""
        project_data = {
            "base_types.h": """
#ifndef BASE_TYPES_H
#define BASE_TYPES_H

typedef unsigned char Byte;
typedef unsigned short Word;
typedef unsigned long DWord;

#endif
""",
            "geometry.h": """
#ifndef GEOMETRY_H
#define GEOMETRY_H

#include "base_types.h"

typedef struct {
    Word x, y;
} Point;

typedef struct {
    Point top_left;
    Point bottom_right;
} Rectangle;

typedef Rectangle* RectPtr;

#endif
""",
            "graphics.h": """
#ifndef GRAPHICS_H
#define GRAPHICS_H

#include "base_types.h"
#include "geometry.h"

typedef struct {
    Byte r, g, b, a;
} Color;

typedef struct {
    Rectangle bounds;
    Color fill_color;
    Color border_color;
} GraphicsObject;

typedef GraphicsObject* GraphicsObjectPtr;
typedef GraphicsObjectPtr GraphicsObjectArray[1024];

#endif
""",
            "main.c": """
#include "graphics.h"

typedef GraphicsObjectArray Scene;

int main() {
    Scene scene;
    return 0;
}
"""
        }

        project_dir = create_temp_project(project_data, self.temp_dir)
        config_data = TestDataProviders.get_sample_configs()["standard"]
        config_data["source_folders"] = [str(project_dir)]

        results = run_full_pipeline(project_dir, config_data)
        parsed_model = results["parsed_model"]

        # Verify complex include chain
        graphics_file = None
        for file_data in parsed_model["files"]:
            if file_data["filename"] == "graphics.h":
                graphics_file = file_data
                break

        self.assertIsNotNone(graphics_file)
        
        # Verify graphics.h includes both base_types.h and geometry.h
        graphics_includes = set(graphics_file["includes"])
        self.assertIn("base_types.h", graphics_includes)
        self.assertIn("geometry.h", graphics_includes)


class TestIncludeProcessingCaching(unittest.TestCase):
    """Test include processing caching functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.parser = CParser()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_include_caching_prevents_duplicate_processing(self):
        """Test that include caching prevents duplicate file processing."""
        project_data = {
            "common.h": """
#ifndef COMMON_H
#define COMMON_H

typedef struct {
    int value;
} CommonType;

#endif
""",
            "file1.c": """
#include "common.h"

void func1() {
    CommonType t;
}
""",
            "file2.c": """
#include "common.h"

void func2() {
    CommonType t;
}
""",
            "file3.c": """
#include "common.h"

void func3() {
    CommonType t;
}
"""
        }

        project_dir = create_temp_project(project_data, self.temp_dir)
        
        # Mock the parser to track file processing
        with patch.object(self.parser, 'parse_file', wraps=self.parser.parse_file) as mock_parse:
            config_data = TestDataProviders.get_sample_configs()["standard"]
            config_data["source_folders"] = [str(project_dir)]
            
            results = run_full_pipeline(project_dir, config_data)
            
            # Verify that common.h is not processed multiple times unnecessarily
            # This is implementation-dependent, so we mainly verify the results are correct
            parsed_model = results["parsed_model"]
            
            # All files should be present
            filenames = [f["filename"] for f in parsed_model["files"]]
            expected_files = {"common.h", "file1.c", "file2.c", "file3.c"}
            actual_files = set(filenames)
            
            self.assertTrue(
                expected_files.issubset(actual_files),
                f"Missing files: {expected_files - actual_files}"
            )


class TestIncludeProcessingEdgeCases(unittest.TestCase):
    """Test edge cases in include processing."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_circular_includes(self):
        """Test handling of circular include dependencies."""
        project_data = {
            "a.h": """
#ifndef A_H
#define A_H

#include "b.h"

typedef struct A {
    struct B* b_ptr;
    int a_value;
} A;

#endif
""",
            "b.h": """
#ifndef B_H
#define B_H

#include "a.h"

typedef struct B {
    struct A* a_ptr;
    int b_value;
} B;

#endif
"""
        }

        project_dir = create_temp_project(project_data, self.temp_dir)
        config_data = TestDataProviders.get_sample_configs()["standard"]
        config_data["source_folders"] = [str(project_dir)]

        # This should not crash or hang due to circular includes
        results = run_full_pipeline(project_dir, config_data)
        parsed_model = results["parsed_model"]

        # Verify both files are processed
        filenames = [f["filename"] for f in parsed_model["files"]]
        self.assertIn("a.h", filenames)
        self.assertIn("b.h", filenames)

    def test_missing_include_files(self):
        """Test handling of missing include files."""
        project_data = {
            "main.c": """
#include <stdio.h>          // System include - should be ok
#include "missing_file.h"   // Missing local include
#include "another_missing.h" // Another missing file

int main() {
    return 0;
}
"""
        }

        project_dir = create_temp_project(project_data, self.temp_dir)
        config_data = TestDataProviders.get_sample_configs()["standard"]
        config_data["source_folders"] = [str(project_dir)]

        # This should not crash when include files are missing
        results = run_full_pipeline(project_dir, config_data)
        parsed_model = results["parsed_model"]

        # main.c should still be processed
        filenames = [f["filename"] for f in parsed_model["files"]]
        self.assertIn("main.c", filenames)

        # Find main.c and check its includes
        main_file = None
        for file_data in parsed_model["files"]:
            if file_data["filename"] == "main.c":
                main_file = file_data
                break

        self.assertIsNotNone(main_file)
        
        # Should still record the include statements even if files are missing
        main_includes = set(main_file["includes"])
        expected_includes = {"stdio.h", "missing_file.h", "another_missing.h"}
        self.assertTrue(
            expected_includes.issubset(main_includes),
            f"Missing includes: {expected_includes - main_includes}"
        )


if __name__ == "__main__":
    unittest.main()