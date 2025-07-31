#!/usr/bin/env python3
"""
Consolidated unit tests for include header processing functionality.

This module consolidates and replaces multiple overlapping include processing
test files to reduce duplication and improve maintainability.
"""

import os
import shutil

# We need to add the parent directory to Python path for imports
import sys
import tempfile
from pathlib import Path
from unittest import TestCase

# Add src directory to path for new package structure
test_dir = os.path.dirname(__file__)
src_path = os.path.join(test_dir, "..", "..", "src")
if os.path.exists(src_path):
    sys.path.insert(0, src_path)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from c2puml.generator import Generator
from c2puml.parser import CParser


class TestIncludeProcessingBug(TestCase):
    """Test suite to verify include processing bug has been fixed.

    This test specifically verifies that include files are properly resolved
    and that the include tree generation works correctly.
    """

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.parser = CParser()
        self.generator = Generator()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file with given content."""
        file_path = self.temp_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def test_include_tree_generation_bug(self):
        """Test that include tree is correctly generated for files with includes."""

        # Create header file
        self.create_test_file(
            "header.h",
            """
            #ifndef HEADER_H
            #define HEADER_H

            typedef struct {
                int id;
                char name[50];
            } my_struct_t;

            void my_function(void);

            #endif
            """,
        )

        # Create source file that includes the header
        self.create_test_file(
            "main.c",
            """
            #include "header.h"

            void main() {
                my_struct_t instance;
                my_function();
            }
            """,
        )

        # Parse the project
        project_model = self.parser.parse_project(str(self.temp_dir))

        # Get the main.c file model
        main_file = project_model.files["main.c"]

        # Generate the PlantUML diagram
        diagram = self.generator.generate_diagram(main_file, project_model)

        # Verify that the diagram contains both files
        self.assertIn("@startuml main", diagram)
        self.assertIn("@enduml", diagram)

        # Check that main.c is referenced
        self.assertIn('class "main"', diagram)

        # Check that header.h is included in the include tree
        self.assertIn('class "header"', diagram)

        # Check that the struct from header is included
        self.assertIn("my_struct_t", diagram)

    def test_include_depth_control(self):
        """Test that include depth parameter controls how deep includes are processed."""

        # Create a chain of includes: main.c -> level1.h -> level2.h

        self.create_test_file(
            "level2.h",
            """
            #ifndef LEVEL2_H
            #define LEVEL2_H
            
            typedef struct {
                int deep_field;
            } deep_struct_t;
            
            #endif
            """,
        )

        self.create_test_file(
            "level1.h",
            """
            #ifndef LEVEL1_H
            #define LEVEL1_H
            
            #include "level2.h"
            
            typedef struct {
                int mid_field;
                deep_struct_t deep;
            } mid_struct_t;
            
            #endif
            """,
        )

        self.create_test_file(
            "main.c",
            """
            #include "level1.h"

            void main() {
                mid_struct_t instance;
            }
            """,
        )

        # Parse the project
        project_model = self.parser.parse_project(str(self.temp_dir))
        main_file = project_model.files["main.c"]

        # Test with include depth = 1 (should only include level1.h)
        diagram_depth_1 = self.generator.generate_diagram(
            main_file, project_model, include_depth=1
        )

        # Test with include depth = 2 (should include both level1.h and level2.h)
        diagram_depth_2 = self.generator.generate_diagram(
            main_file, project_model, include_depth=2
        )

        # Both should include main.c and level1.h
        self.assertIn('class "main"', diagram_depth_1)
        self.assertIn('class "level1"', diagram_depth_1)

        self.assertIn('class "main"', diagram_depth_2)
        self.assertIn('class "level1"', diagram_depth_2)

        # Only depth 2 should include level2.h
        self.assertNotIn('class "level2"', diagram_depth_1)
        self.assertIn('class "level2"', diagram_depth_2)

    def test_circular_includes_handling(self):
        """Test that circular includes are handled gracefully."""

        # Create circular includes: a.h <-> b.h
        self.create_test_file(
            "a.h",
            """
            #ifndef A_H
            #define A_H
            
            #include "b.h"
            
            typedef struct {
                int field_a;
                struct_b_t b_ref;
            } struct_a_t;
            
            #endif
            """,
        )

        self.create_test_file(
            "b.h",
            """
            #ifndef B_H
            #define B_H
            
            #include "a.h"
            
            typedef struct {
                int field_b;
            } struct_b_t;
            
            #endif
            """,
        )

        self.create_test_file(
            "main.c",
            """
            #include "a.h"

            void main() {
                struct_a_t instance;
            }
            """,
        )

        # Parse the project
        project_model = self.parser.parse_project(str(self.temp_dir))
        main_file = project_model.files["main.c"]

        # This should not crash due to circular includes
        diagram = self.generator.generate_diagram(
            main_file, project_model, include_depth=3
        )

        # Verify basic structure
        self.assertIn("@startuml main", diagram)
        self.assertIn("@enduml", diagram)
        self.assertIn('class "main"', diagram)
        self.assertIn('class "a"', diagram)
        self.assertIn('class "b"', diagram)
