#!/usr/bin/env python3
"""
Tests for public/private visibility logic in PlantUML generation.
"""

import tempfile
import unittest

from c2puml.core.generator import Generator
from c2puml.models import Field, FileModel, Function, ProjectModel


class TestGeneratorVisibilityLogic(unittest.TestCase):
    """Test the public/private visibility logic for functions and globals"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = Generator()
        self.temp_dir = tempfile.mkdtemp()

    def test_function_visibility_public_when_in_header(self):
        """Test that functions present in headers are marked as + (public)"""
        # Create source file with function
        source_function = Function(name="calculate", return_type="int", is_declaration=False)
        source_file = FileModel(
            file_path="math.c",
            name="math.c",
            functions=[source_function],
        )

        # Create header file with declaration for the same function
        header_function = Function(name="calculate", return_type="int", is_declaration=True)
        header_file = FileModel(
            file_path="math.h",
            name="math.h",
            functions=[header_function],
        )

        project_model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"math.c": source_file, "math.h": header_file},
        )

        # Generate diagram for source file
        diagram = self.generator.generate_diagram(source_file, project_model)

        # Function should be marked as public since it's in a header
        self.assertIn("+ int calculate", diagram)
        self.assertNotIn("- int calculate", diagram)

    def test_function_visibility_private_when_not_in_header(self):
        """Test that functions NOT present in headers are marked as - (private)"""
        # Create source file with function
        private_function = Function(name="internal_helper", return_type="void", is_declaration=False)
        public_function = Function(name="public_api", return_type="int", is_declaration=False)
        source_file = FileModel(
            file_path="math.c",
            name="math.c",
            functions=[private_function, public_function],
        )

        # Create header file with declaration for only one function
        header_function = Function(name="public_api", return_type="int", is_declaration=True)
        header_file = FileModel(
            file_path="math.h",
            name="math.h",
            functions=[header_function],
        )

        project_model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"math.c": source_file, "math.h": header_file},
        )

        # Generate diagram for source file
        diagram = self.generator.generate_diagram(source_file, project_model)

        # Function in header should be public
        self.assertIn("+ int public_api", diagram)
        
        # Function not in header should be private
        self.assertIn("- void internal_helper", diagram)

    def test_global_visibility_public_when_in_header(self):
        """Test that globals present in headers are marked as + (public)"""
        # Create source file with global
        source_global = Field(name="global_counter", type="int")
        source_file = FileModel(
            file_path="globals.c",
            name="globals.c",
            globals=[source_global],
        )

        # Create header file with extern declaration for the same global
        header_global = Field(name="global_counter", type="extern int")
        header_file = FileModel(
            file_path="globals.h",
            name="globals.h",
            globals=[header_global],
        )

        project_model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"globals.c": source_file, "globals.h": header_file},
        )

        # Generate diagram for source file
        diagram = self.generator.generate_diagram(source_file, project_model)

        # Global should be marked as public since it's declared in header
        self.assertIn("+ int global_counter", diagram)
        self.assertNotIn("- int global_counter", diagram)

    def test_global_visibility_private_when_not_in_header(self):
        """Test that globals NOT present in headers are marked as - (private)"""
        # Create source file with globals
        private_global = Field(name="internal_value", type="static int")
        public_global = Field(name="shared_data", type="int")
        source_file = FileModel(
            file_path="globals.c",
            name="globals.c",
            globals=[private_global, public_global],
        )

        # Create header file with extern declaration for only one global
        header_global = Field(name="shared_data", type="extern int")
        header_file = FileModel(
            file_path="globals.h",
            name="globals.h",
            globals=[header_global],
        )

        project_model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"globals.c": source_file, "globals.h": header_file},
        )

        # Generate diagram for source file
        diagram = self.generator.generate_diagram(source_file, project_model)

        # Global in header should be public
        self.assertIn("+ int shared_data", diagram)
        
        # Global not in header should be private
        self.assertIn("- static int internal_value", diagram)

    def test_mixed_visibility_comprehensive(self):
        """Test a comprehensive mix of public and private functions and globals"""
        # Create source file with mixed visibility
        public_func = Function(name="api_function", return_type="int", is_declaration=False)
        private_func = Function(name="helper_function", return_type="void", is_declaration=False)
        public_global = Field(name="api_data", type="int")
        private_global = Field(name="internal_state", type="static int")

        source_file = FileModel(
            file_path="module.c",
            name="module.c",
            functions=[public_func, private_func],
            globals=[public_global, private_global],
        )

        # Create header file with declarations for public items only
        header_func = Function(name="api_function", return_type="int", is_declaration=True)
        header_global = Field(name="api_data", type="extern int")

        header_file = FileModel(
            file_path="module.h",
            name="module.h",
            functions=[header_func],
            globals=[header_global],
        )

        project_model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"module.c": source_file, "module.h": header_file},
        )

        # Generate diagram for source file
        diagram = self.generator.generate_diagram(source_file, project_model)

        # Check public items (in headers)
        self.assertIn("+ int api_function", diagram)
        self.assertIn("+ int api_data", diagram)
        
        # Check private items (not in headers)
        self.assertIn("- void helper_function", diagram)
        self.assertIn("- static int internal_state", diagram)

    def test_no_headers_all_private(self):
        """Test that when no headers exist, all functions and globals are private"""
        # Create source file with functions and globals
        func = Function(name="lonely_function", return_type="int", is_declaration=False)
        global_var = Field(name="lonely_global", type="int")

        source_file = FileModel(
            file_path="standalone.c",
            name="standalone.c",
            functions=[func],
            globals=[global_var],
        )

        project_model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"standalone.c": source_file},
        )

        # Generate diagram for source file
        diagram = self.generator.generate_diagram(source_file, project_model)

        # All items should be private since no headers exist
        self.assertIn("- int lonely_function", diagram)
        self.assertIn("- int lonely_global", diagram)


if __name__ == "__main__":
    unittest.main()