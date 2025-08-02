#!/usr/bin/env python3
"""
Tests for public/private grouping in PlantUML generation.
"""

import tempfile
import unittest

from c2puml.core.generator import Generator
from c2puml.models import Field, FileModel, Function, ProjectModel


class TestGeneratorGrouping(unittest.TestCase):
    """Test the public/private grouping logic with empty line separation"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = Generator()
        self.temp_dir = tempfile.mkdtemp()

    def test_function_grouping_with_empty_line_separation(self):
        """Test that public and private functions are grouped with empty line separation"""
        # Create source file with mixed public/private functions
        public_func1 = Function(name="Init", return_type="void", is_declaration=False)
        public_func2 = Function(name="Calculate", return_type="int", is_declaration=False)
        public_func3 = Function(name="Shutdown", return_type="void", is_declaration=False)
        private_func1 = Function(name="HelperFunction", return_type="void", is_declaration=False)
        private_func2 = Function(name="InternalComputation", return_type="static int", is_declaration=False)

        source_file = FileModel(
            file_path="math.c",
            name="math.c",
            functions=[public_func1, private_func1, public_func2, private_func2, public_func3],
        )

        # Create header file with public function declarations
        header_func1 = Function(name="Init", return_type="void", is_declaration=True)
        header_func2 = Function(name="Calculate", return_type="int", is_declaration=True)
        header_func3 = Function(name="Shutdown", return_type="void", is_declaration=True)

        header_file = FileModel(
            file_path="math.h",
            name="math.h",
            functions=[header_func1, header_func2, header_func3],
        )

        project_model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"math.c": source_file, "math.h": header_file},
        )

        # Generate diagram
        diagram = self.generator.generate_diagram(source_file, project_model)

        # Verify public functions are grouped together
        self.assertIn("+ void Init", diagram)
        self.assertIn("+ int Calculate", diagram)
        self.assertIn("+ void Shutdown", diagram)

        # Verify private functions are grouped together
        self.assertIn("- void HelperFunction", diagram)
        self.assertIn("- static int InternalComputation", diagram)

        # Check for empty line separation between public and private groups
        lines = diagram.split('\n')
        
        # Find the lines with functions
        function_lines = []
        in_functions_section = False
        for i, line in enumerate(lines):
            if "-- Functions --" in line:
                in_functions_section = True
                continue
            elif in_functions_section and line.strip() == "}":
                break
            elif in_functions_section and line.strip():
                function_lines.append((i, line.strip()))

        # Verify we have both public and private functions
        public_functions = [line for _, line in function_lines if line.startswith("+ ")]
        private_functions = [line for _, line in function_lines if line.startswith("- ")]
        
        self.assertGreater(len(public_functions), 0, "Should have public functions")
        self.assertGreater(len(private_functions), 0, "Should have private functions")

        # Check for empty line between groups (this will fail initially)
        # We need to find where public functions end and private functions begin
        self._verify_empty_line_between_groups(lines, function_lines)

    def test_global_grouping_with_empty_line_separation(self):
        """Test that public and private globals are grouped with empty line separation"""
        # Create source file with mixed public/private globals
        public_global1 = Field(name="api_version", type="int")
        public_global2 = Field(name="module_name", type="char*")
        private_global1 = Field(name="internal_state", type="static int")
        private_global2 = Field(name="debug_flag", type="static bool")

        source_file = FileModel(
            file_path="module.c",
            name="module.c",
            globals=[public_global1, private_global1, public_global2, private_global2],
        )

        # Create header file with public global declarations
        header_global1 = Field(name="api_version", type="extern int")
        header_global2 = Field(name="module_name", type="extern char*")

        header_file = FileModel(
            file_path="module.h",
            name="module.h",
            globals=[header_global1, header_global2],
        )

        project_model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"module.c": source_file, "module.h": header_file},
        )

        # Generate diagram
        diagram = self.generator.generate_diagram(source_file, project_model)

        # Verify public globals are grouped together
        self.assertIn("+ int api_version", diagram)
        self.assertIn("+ char* module_name", diagram)

        # Verify private globals are grouped together
        self.assertIn("- static int internal_state", diagram)
        self.assertIn("- static bool debug_flag", diagram)

        # Check for empty line separation between public and private groups
        lines = diagram.split('\n')
        
        # Find the lines with globals
        global_lines = []
        in_globals_section = False
        for i, line in enumerate(lines):
            if "-- Global Variables --" in line:
                in_globals_section = True
                continue
            elif in_globals_section and "-- Functions --" in line:
                break
            elif in_globals_section and line.strip() and not line.strip() == "}":
                global_lines.append((i, line.strip()))

        # Verify we have both public and private globals
        public_globals = [line for _, line in global_lines if line.startswith("+ ")]
        private_globals = [line for _, line in global_lines if line.startswith("- ")]
        
        self.assertGreater(len(public_globals), 0, "Should have public globals")
        self.assertGreater(len(private_globals), 0, "Should have private globals")

        # Check for empty line between groups
        self._verify_empty_line_between_groups(lines, global_lines)

    def test_mixed_grouping_comprehensive(self):
        """Test grouping works correctly with both functions and globals"""
        # Create a comprehensive test with both functions and globals
        public_func = Function(name="ProcessData", return_type="int", is_declaration=False)
        private_func = Function(name="ValidateInput", return_type="static bool", is_declaration=False)
        public_global = Field(name="error_count", type="int")
        private_global = Field(name="buffer_size", type="static size_t")

        source_file = FileModel(
            file_path="processor.c",
            name="processor.c",
            functions=[public_func, private_func],
            globals=[public_global, private_global],
        )

        # Create header file with public declarations
        header_func = Function(name="ProcessData", return_type="int", is_declaration=True)
        header_global = Field(name="error_count", type="extern int")

        header_file = FileModel(
            file_path="processor.h",
            name="processor.h",
            functions=[header_func],
            globals=[header_global],
        )

        project_model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"processor.c": source_file, "processor.h": header_file},
        )

        # Generate diagram
        diagram = self.generator.generate_diagram(source_file, project_model)

        # Verify public elements
        self.assertIn("+ int error_count", diagram)
        self.assertIn("+ int ProcessData", diagram)

        # Verify private elements
        self.assertIn("- static size_t buffer_size", diagram)
        self.assertIn("- static bool ValidateInput", diagram)

        # Verify the overall structure has proper grouping
        lines = diagram.split('\n')
        self.assertIn("-- Global Variables --", diagram)
        self.assertIn("-- Functions --", diagram)

    def _verify_empty_line_between_groups(self, lines, element_lines):
        """Helper method to verify empty line separation between public and private groups"""
        if len(element_lines) < 2:
            return  # Not enough elements to test grouping

        # Find transition from public to private
        public_indices = []
        private_indices = []
        
        for i, (line_num, line_content) in enumerate(element_lines):
            if line_content.startswith("+ "):
                public_indices.append(line_num)
            elif line_content.startswith("- "):
                private_indices.append(line_num)

        if not public_indices or not private_indices:
            return  # No mixed visibility to test

        # Check if there's an empty line between the last public and first private
        last_public_line = max(public_indices)
        first_private_line = min(private_indices)
        
        # There should be an empty line between them
        for line_num in range(last_public_line + 1, first_private_line):
            if lines[line_num].strip() == "":
                return  # Found empty line - test passes
        
        # If we get here, there's no empty line between groups
        self.fail(f"No empty line found between public and private groups. "
                 f"Last public at line {last_public_line}, first private at line {first_private_line}")


if __name__ == "__main__":
    unittest.main()