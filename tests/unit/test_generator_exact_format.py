#!/usr/bin/env python3
"""
Tests for the exact PlantUML formatting as requested by the user.
"""

import tempfile
import unittest

from c2puml.core.generator import Generator
from c2puml.models import Field, FileModel, Function, ProjectModel


class TestExactFormatting(unittest.TestCase):
    """Test the exact formatting requested by the user"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = Generator()
        self.temp_dir = tempfile.mkdtemp()

    def test_exact_requested_format(self):
        """Test the exact format requested: public functions, empty line, private functions"""
        # Create the exact functions from the user's example
        init_func = Function(name="Init", return_type="void", is_declaration=False)
        calculate_func = Function(name="Calculate", return_type="int", is_declaration=False)
        shutdown_func = Function(name="Shutdown", return_type="void", is_declaration=False)
        helper_func = Function(name="HelperFunction", return_type="void", is_declaration=False)
        internal_func = Function(name="InternalComputation", return_type="static int", is_declaration=False)

        source_file = FileModel(
            file_path="example.c",
            name="example.c",
            functions=[init_func, helper_func, calculate_func, internal_func, shutdown_func],
        )

        # Create header with public function declarations
        init_decl = Function(name="Init", return_type="void", is_declaration=True)
        calculate_decl = Function(name="Calculate", return_type="int", is_declaration=True)
        shutdown_decl = Function(name="Shutdown", return_type="void", is_declaration=True)

        header_file = FileModel(
            file_path="example.h",
            name="example.h",
            functions=[init_decl, calculate_decl, shutdown_decl],
        )

        project_model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"example.c": source_file, "example.h": header_file},
        )

        # Generate diagram
        diagram = self.generator.generate_diagram(source_file, project_model)

        # Split into lines for detailed analysis
        lines = diagram.split('\n')

        # Find the functions section
        function_start = -1
        function_end = -1
        for i, line in enumerate(lines):
            if "-- Functions --" in line:
                function_start = i + 1
            elif function_start != -1 and line.strip() == "}":
                function_end = i
                break

        self.assertNotEqual(function_start, -1, "Functions section not found")
        self.assertNotEqual(function_end, -1, "Functions section end not found")

        # Extract function lines (keep empty lines for analysis)
        function_lines = lines[function_start:function_end]
        
        # Verify the exact format
        public_functions_found = []
        private_functions_found = []
        empty_line_found = False
        in_private_section = False

        for line in function_lines:
            line_stripped = line.strip()
            if line_stripped == "":
                empty_line_found = True
                in_private_section = True
            elif line_stripped.startswith("+ ") and not in_private_section:
                public_functions_found.append(line_stripped)
            elif line_stripped.startswith("- "):
                private_functions_found.append(line_stripped)

        # Verify we have the expected functions
        expected_public = [
            "+ void Init()",
            "+ int Calculate()",
            "+ void Shutdown()"
        ]

        expected_private = [
            "- void HelperFunction()",
            "- static int InternalComputation()"
        ]

        # Check each expected public function is present
        for expected in expected_public:
            found = any(expected in actual for actual in public_functions_found)
            self.assertTrue(found, f"Expected public function '{expected}' not found in {public_functions_found}")

        # Check each expected private function is present
        for expected in expected_private:
            found = any(expected in actual for actual in private_functions_found)
            self.assertTrue(found, f"Expected private function '{expected}' not found in {private_functions_found}")

        # Verify empty line separation exists
        self.assertTrue(empty_line_found, "Empty line between public and private functions not found")

        # Verify the exact sequence: public functions, empty line, private functions
        self._verify_exact_sequence(function_lines, expected_public, expected_private)

    def _verify_exact_sequence(self, function_lines, expected_public, expected_private):
        """Verify the exact sequence of public functions, empty line, private functions"""
        
        # Find the actual empty line position
        empty_line_index = -1
        for i, line in enumerate(function_lines):
            if line.strip() == "":
                empty_line_index = i
                break

        self.assertNotEqual(empty_line_index, -1, "Empty line not found in function section")

        # Check that public functions come before empty line
        # and private functions come after empty line
        before_empty = function_lines[:empty_line_index]
        after_empty = function_lines[empty_line_index + 1:]

        public_before = [line.strip() for line in before_empty if line.strip().startswith("+ ")]
        private_after = [line.strip() for line in after_empty if line.strip().startswith("- ")]

        self.assertGreater(len(public_before), 0, "Should have public functions before empty line")
        self.assertGreater(len(private_after), 0, "Should have private functions after empty line")

        # Verify no private functions before empty line and no public functions after
        private_before = [line.strip() for line in before_empty if line.strip().startswith("- ")]
        public_after = [line.strip() for line in after_empty if line.strip().startswith("+ ")]

        self.assertEqual(len(private_before), 0, "Should have no private functions before empty line")
        self.assertEqual(len(public_after), 0, "Should have no public functions after empty line")

    def test_format_with_parameters(self):
        """Test the format works correctly with function parameters"""
        # Test with the Calculate function that has parameters
        calculate_func = Function(name="Calculate", return_type="int", is_declaration=False)
        calculate_func.parameters = [
            Field(name="value", type="int")
        ]

        helper_func = Function(name="HelperFunction", return_type="void", is_declaration=False)

        source_file = FileModel(
            file_path="calc.c",
            name="calc.c",
            functions=[calculate_func, helper_func],
        )

        # Create header with Calculate declaration
        calculate_decl = Function(name="Calculate", return_type="int", is_declaration=True)
        calculate_decl.parameters = [
            Field(name="value", type="int")
        ]

        header_file = FileModel(
            file_path="calc.h",
            name="calc.h",
            functions=[calculate_decl],
        )

        project_model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"calc.c": source_file, "calc.h": header_file},
        )

        # Generate diagram
        diagram = self.generator.generate_diagram(source_file, project_model)

        # Verify functions with parameters are correctly formatted
        self.assertIn("+ int Calculate(int value)", diagram)
        self.assertIn("- void HelperFunction()", diagram)

        # Verify grouping still works with parameters
        lines = diagram.split('\n')
        function_lines = []
        in_functions = False
        
        for line in lines:
            if "-- Functions --" in line:
                in_functions = True
                continue
            elif in_functions and line.strip() == "}":
                break
            elif in_functions:
                function_lines.append(line.strip())

        # Should have public function, empty line, private function
        public_found = False
        empty_found = False
        private_found = False
        
        for line in function_lines:
            if line.startswith("+ int Calculate"):
                public_found = True
            elif line == "" and public_found:
                empty_found = True
            elif line.startswith("- void HelperFunction") and empty_found:
                private_found = True

        self.assertTrue(public_found and empty_found and private_found, 
                       "Expected sequence: public function, empty line, private function")


if __name__ == "__main__":
    unittest.main()