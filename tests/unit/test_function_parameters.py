#!/usr/bin/env python3
"""
Test function parameter parsing and display in PlantUML generation
"""

import os
import tempfile
import unittest
from pathlib import Path

from c_to_plantuml.generator import PlantUMLGenerator
from c_to_plantuml.models import ProjectModel
from c_to_plantuml.parser import CParser


class TestFunctionParameters(unittest.TestCase):
    """Test that function parameters are correctly parsed and displayed"""

    def setUp(self):
        self.parser = CParser()
        self.generator = PlantUMLGenerator()

    def test_function_parameter_parsing(self):
        """Test that function parameters are correctly parsed"""
        # Test C code with various function signatures
        test_code = """
        int add(int a, int b);
        void process_point(point_t * p);
        real_t average(const int * arr, size_t len);
        int main(int argc, char * argv[]);
        """

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(test_code)
            temp_file = f.name

        try:
            # Parse the file
            file_model = self.parser.parse_file(
                Path(temp_file), os.path.basename(temp_file), os.path.dirname(temp_file)
            )

            # Check that functions have parameters
            self.assertEqual(len(file_model.functions), 4)

            # Check specific function parameters
            add_func = next(f for f in file_model.functions if f.name == "add")
            self.assertEqual(len(add_func.parameters), 2)
            self.assertEqual(add_func.parameters[0].name, "a")
            self.assertEqual(add_func.parameters[0].type, "int")
            self.assertEqual(add_func.parameters[1].name, "b")
            self.assertEqual(add_func.parameters[1].type, "int")

            process_func = next(
                f for f in file_model.functions if f.name == "process_point"
            )
            self.assertEqual(len(process_func.parameters), 1)
            self.assertEqual(process_func.parameters[0].name, "p")
            self.assertEqual(process_func.parameters[0].type, "point_t *")

        finally:
            os.unlink(temp_file)

    def test_function_parameter_display(self):
        """Test that function parameters are correctly displayed in PlantUML"""
        # Create a simple project model with functions that have parameters
        from c_to_plantuml.models import Field, FileModel, Function

        # Create a file model with functions that have parameters
        file_model = FileModel(
            file_path="/test/sample.c",
            relative_path="sample.c",
            project_root="/test",
            encoding_used="utf-8",
            functions=[
                Function("add", "int", [Field("a", "int"), Field("b", "int")]),
                Function("process_point", "void", [Field("p", "point_t *")]),
                Function(
                    "average",
                    "real_t",
                    [Field("arr", "const int *"), Field("len", "size_t")],
                ),
            ],
        )

        project_model = ProjectModel(
            project_name="test", project_root="/test", files={"sample.c": file_model}
        )

        # Generate PlantUML diagram
        diagram = self.generator.generate_diagram(file_model, project_model)

        # Check that function signatures include parameters
        self.assertIn("int add(int a, int b)", diagram)
        self.assertIn("void process_point(point_t * p)", diagram)
        self.assertIn("real_t average(const int * arr, size_t len)", diagram)

        # Check that old format without parameters is NOT present
        self.assertNotIn("int add()", diagram)
        self.assertNotIn("void process_point()", diagram)
        self.assertNotIn("real_t average()", diagram)

    def test_empty_parameter_list(self):
        """Test functions with no parameters (void)"""
        from c_to_plantuml.models import FileModel, Function

        file_model = FileModel(
            file_path="/test/empty.c",
            relative_path="empty.c",
            project_root="/test",
            encoding_used="utf-8",
            functions=[Function("init", "void", []), Function("cleanup", "void", [])],
        )

        project_model = ProjectModel(
            project_name="test", project_root="/test", files={"empty.c": file_model}
        )

        diagram = self.generator.generate_diagram(file_model, project_model)

        # Check that functions with no parameters are displayed correctly
        self.assertIn("void init()", diagram)
        self.assertIn("void cleanup()", diagram)

    def test_complex_parameter_types(self):
        """Test functions with complex parameter types"""
        from c_to_plantuml.models import Field, FileModel, Function

        file_model = FileModel(
            file_path="/test/complex.c",
            relative_path="complex.c",
            project_root="/test",
            encoding_used="utf-8",
            functions=[
                Function(
                    "callback",
                    "int",
                    [Field("data", "void *"), Field("user_data", "void *")],
                ),
                Function(
                    "array_func",
                    "void",
                    [Field("arr", "int[10]"), Field("size", "size_t")],
                ),
                Function("const_func", "const char *", [Field("str", "const char *")]),
            ],
        )

        project_model = ProjectModel(
            project_name="test", project_root="/test", files={"complex.c": file_model}
        )

        diagram = self.generator.generate_diagram(file_model, project_model)

        # Check that complex parameter types are displayed correctly
        self.assertIn("int callback(void * data, void * user_data)", diagram)
        self.assertIn("void array_func(int[10] arr, size_t size)", diagram)
        self.assertIn("const char * const_func(const char * str)", diagram)


if __name__ == "__main__":
    unittest.main()
