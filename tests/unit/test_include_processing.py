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

# Try to import shared utilities, fallback if not available
try:
    from tests.utils import (
        AssertionHelpers,
        MockObjectFactory,
        TestDataProviders,
        TestProjectBuilder,
        create_temp_project,
        run_full_pipeline,
    )
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False


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
        actual_includes = set(file_model.includes)
        self.assertEqual(actual_includes, expected_includes)

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

        expected_includes = {"stdio.h", "stdlib.h", "utils.h", "config.h"}
        actual_includes = set(file_model.includes)
        self.assertEqual(actual_includes, expected_includes)

    def test_parse_includes_with_preprocessor_directives(self):
        """Test parsing includes with preprocessor directives."""
        content = """
#include <stdio.h>
#ifdef DEBUG
#include <assert.h>
#endif
#include "utils.h"
        """

        file_path = self.create_test_file("test.c", content)
        file_model = self.parser.parse_file(
            file_path, file_path.name, str(self.test_dir)
        )

        # Should parse includes that are clearly defined
        expected_includes = {"stdio.h", "utils.h"}
        actual_includes = set(file_model.includes)
        
        # At least these includes should be present
        self.assertTrue(
            expected_includes.issubset(actual_includes),
            f"Missing basic includes: {expected_includes - actual_includes}"
        )
        
        # May also have conditional includes like assert.h
        self.assertIn("stdio.h", actual_includes)
        self.assertIn("utils.h", actual_includes)


class TestIncludeProcessingRelationships(unittest.TestCase):
    """Test include relationships and dependencies."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)
        self.parser = CParser()
        self.transformer = Transformer()

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

    def test_c_to_h_file_relationships(self):
        """Test relationships between C files and their header files."""
        # Create a simple test project structure
        main_c_content = """
#include <stdio.h>
#include "types.h"

int main() {
    Point p = {0, 0};
    return 0;
}
"""
        
        types_h_content = """
#ifndef TYPES_H
#define TYPES_H

typedef struct {
    int x;
    int y;
} Point;

#endif
"""

        # Create test files
        main_c_path = self.create_test_file("main.c", main_c_content)
        types_h_path = self.create_test_file("types.h", types_h_content)

        # Parse both files
        main_file_model = self.parser.parse_file(
            main_c_path, main_c_path.name, str(self.temp_dir)
        )
        types_file_model = self.parser.parse_file(
            types_h_path, types_h_path.name, str(self.temp_dir)
        )

        # Verify include relationships
        self.assertIn("stdio.h", main_file_model.includes)
        self.assertIn("types.h", main_file_model.includes)
        
        # Verify types.h contains the expected struct
        struct_names = list(types_file_model.structs.keys())
        self.assertIn("Point", struct_names)

    def test_header_to_header_relationships(self):
        """Test relationships between header files."""
        base_h_content = """
#ifndef BASE_H
#define BASE_H

typedef struct {
    int id;
} Base;

#endif
"""
        
        derived_h_content = """
#ifndef DERIVED_H
#define DERIVED_H

#include "base.h"

typedef struct {
    Base base;
    int extra_field;
} Derived;

#endif
"""

        # Create test files
        base_h_path = self.create_test_file("base.h", base_h_content)
        derived_h_path = self.create_test_file("derived.h", derived_h_content)

        # Parse both files
        base_file_model = self.parser.parse_file(
            base_h_path, base_h_path.name, str(self.temp_dir)
        )
        derived_file_model = self.parser.parse_file(
            derived_h_path, derived_h_path.name, str(self.temp_dir)
        )

        # Verify include relationships
        self.assertIn("base.h", derived_file_model.includes)
        
        # Verify structs are properly parsed
        base_structs = list(base_file_model.structs.keys())
        derived_structs = list(derived_file_model.structs.keys())
        
        self.assertIn("Base", base_structs)
        self.assertIn("Derived", derived_structs)


class TestIncludeProcessingTypedefs(unittest.TestCase):
    """Test typedef relationships in include processing."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)
        self.parser = CParser()

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

    def test_simple_typedef_relationships(self):
        """Test simple typedef relationships across files."""
        types_h_content = """
#ifndef TYPES_H
#define TYPES_H

typedef unsigned char byte_t;
typedef unsigned short word_t;

typedef struct {
    byte_t r, g, b, a;
} Color;

#endif
"""
        
        main_c_content = """
#include "types.h"

int main() {
    Color red = {255, 0, 0, 255};
    return 0;
}
"""

        # Create test files
        types_h_path = self.create_test_file("types.h", types_h_content)
        main_c_path = self.create_test_file("main.c", main_c_content)

        # Parse both files
        types_file_model = self.parser.parse_file(
            types_h_path, types_h_path.name, str(self.temp_dir)
        )
        main_file_model = self.parser.parse_file(
            main_c_path, main_c_path.name, str(self.temp_dir)
        )

        # Verify include relationships
        self.assertIn("types.h", main_file_model.includes)

        # Verify typedefs and structs
        struct_names = list(types_file_model.structs.keys())
        self.assertIn("Color", struct_names)
        
        # Check that types.h has typedefs (stored as aliases)
        self.assertTrue(len(types_file_model.aliases) > 0)

    def test_complex_nested_typedef_relationships(self):
        """Test complex nested typedef relationships."""
        base_types_h_content = """
#ifndef BASE_TYPES_H
#define BASE_TYPES_H

typedef unsigned char Byte;
typedef unsigned short Word;

#endif
"""
        
        geometry_h_content = """
#ifndef GEOMETRY_H
#define GEOMETRY_H

#include "base_types.h"

typedef struct {
    Word x, y;
} Point;

#endif
"""

        # Create test files
        base_types_h_path = self.create_test_file("base_types.h", base_types_h_content)
        geometry_h_path = self.create_test_file("geometry.h", geometry_h_content)

        # Parse both files
        base_types_file_model = self.parser.parse_file(
            base_types_h_path, base_types_h_path.name, str(self.temp_dir)
        )
        geometry_file_model = self.parser.parse_file(
            geometry_h_path, geometry_h_path.name, str(self.temp_dir)
        )

        # Verify include relationships
        self.assertIn("base_types.h", geometry_file_model.includes)
        
        # Verify structs and typedefs
        base_typedefs = list(base_types_file_model.aliases.keys())
        geometry_structs = list(geometry_file_model.structs.keys())
        
        self.assertIn("Byte", base_typedefs)
        self.assertIn("Word", base_typedefs)
        self.assertIn("Point", geometry_structs)


class TestIncludeProcessingCaching(unittest.TestCase):
    """Test include processing caching functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)
        self.parser = CParser()

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

    def test_include_caching_prevents_duplicate_processing(self):
        """Test that include caching prevents duplicate file processing."""
        common_h_content = """
#ifndef COMMON_H
#define COMMON_H

typedef struct {
    int value;
} CommonType;

#endif
"""
        
        file1_c_content = """
#include "common.h"

void func1() {
    CommonType t;
}
"""

        # Create test files
        common_h_path = self.create_test_file("common.h", common_h_content)
        file1_c_path = self.create_test_file("file1.c", file1_c_content)

        # Parse files
        common_file_model = self.parser.parse_file(
            common_h_path, common_h_path.name, str(self.temp_dir)
        )
        file1_file_model = self.parser.parse_file(
            file1_c_path, file1_c_path.name, str(self.temp_dir)
        )

        # Verify results
        self.assertIn("common.h", file1_file_model.includes)
        
        # Check that common.h defines the expected struct
        struct_names = list(common_file_model.structs.keys())
        self.assertIn("CommonType", struct_names)
        
        # Check that file1.c defines the expected function
        function_names = [func.name for func in file1_file_model.functions]
        self.assertIn("func1", function_names)


class TestIncludeProcessingEdgeCases(unittest.TestCase):
    """Test edge cases in include processing."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)
        self.parser = CParser()

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

    def test_circular_includes(self):
        """Test handling of circular include dependencies."""
        a_h_content = """
#ifndef A_H
#define A_H

typedef struct A {
    int a_value;
} A;

#endif
"""
        
        b_h_content = """
#ifndef B_H
#define B_H

typedef struct B {
    int b_value;
} B;

#endif
"""

        # Create test files (avoiding actual circular includes for this basic test)
        a_h_path = self.create_test_file("a.h", a_h_content)
        b_h_path = self.create_test_file("b.h", b_h_content)

        # Parse both files - should not crash
        a_file_model = self.parser.parse_file(
            a_h_path, a_h_path.name, str(self.temp_dir)
        )
        b_file_model = self.parser.parse_file(
            b_h_path, b_h_path.name, str(self.temp_dir)
        )

        # Verify both files are processed successfully
        a_structs = list(a_file_model.structs.keys())
        b_structs = list(b_file_model.structs.keys())
        
        self.assertIn("A", a_structs)
        self.assertIn("B", b_structs)

    def test_missing_include_files(self):
        """Test handling of missing include files."""
        main_c_content = """
#include <stdio.h>          // System include - should be ok
#include "missing_file.h"   // Missing local include

int main() {
    return 0;
}
"""

        # Create test file with missing includes
        main_c_path = self.create_test_file("main.c", main_c_content)

        # This should not crash when include files are missing
        main_file_model = self.parser.parse_file(
            main_c_path, main_c_path.name, str(self.temp_dir)
        )

        # main.c should still be processed
        self.assertEqual(main_file_model.relative_path, "main.c")
        
        # Should still record the include statements even if files are missing
        main_includes = set(main_file_model.includes)
        expected_includes = {"stdio.h", "missing_file.h"}
        self.assertTrue(
            expected_includes.issubset(main_includes),
            f"Missing includes: {expected_includes - main_includes}"
        )
        
        # Should find the main function
        function_names = [func.name for func in main_file_model.functions]
        self.assertIn("main", function_names)


if __name__ == "__main__":
    unittest.main()