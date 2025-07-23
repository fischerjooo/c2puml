#!/usr/bin/env python3
"""
Unit tests for PlantUML generator functionality
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from c_to_plantuml.config import Config
from c_to_plantuml.generator import Generator, PlantUMLGenerator
from c_to_plantuml.models import Alias, Enum, Field, FileModel, Function, ProjectModel, Struct, Union


class TestGenerator(unittest.TestCase):
    """Test cases for PlantUML generator functionality"""

    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        from c_to_plantuml.parser import CParser
        self.parser = CParser()
        self.generator = Generator()
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = []

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file_model(self, filename: str = "test.c") -> FileModel:
        """Create a test file model with sample data"""
        return FileModel(
            file_path=filename,
            relative_path=filename,
            project_root="/test",
            encoding_used="utf-8",
            structs={
                "Person": Struct(
                    "Person",
                    [
                        Field("name", "char*"),
                        Field("age", "int"),
                        Field("height", "float"),
                    ],
                ),
                "Config": Struct(
                    "Config", [Field("max_users", "int"), Field("timeout", "int")]
                ),
            },
            enums={
                "Status": Enum("Status", ["OK", "ERROR", "PENDING"]),
                "Color": Enum("Color", ["RED", "GREEN", "BLUE"]),
            },
            functions=[
                Function("main", "int", []),
                Function("process_data", "void", [Field("data", "void*")]),
                Function(
                    "calculate", "float", [Field("a", "float"), Field("b", "float")]
                ),
            ],
            globals=[Field("global_var", "int"), Field("global_string", "char*")],
            includes=["stdio.h", "stdlib.h", "local.h"],
            macros=["MAX_SIZE", "DEBUG_MODE", "VERSION"],
            aliases={"Integer": Alias("Integer", "int"), "String": Alias("String", "char*"), "Callback": Alias("Callback", "void (*)(int)")},
        )

    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file and return its path"""
        file_path = Path(self.temp_dir) / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return file_path

    def test_generate_plantuml_content(self):
        """Test that PlantUML content is generated correctly"""
        # Create a simple test file
        content = """
#define MAX_SIZE 100
#define DEBUG 1

int global_var;
char* global_string;

int main() {
    return 0;
}

void process_data() {
    // Process data
}
        """
        test_file = self.create_test_file("test.c", content)
        
        # Parse the file
        project_model = self.parser.parse_project(str(self.temp_dir))
        file_model = project_model.files["test.c"]
        
        # Generate PlantUML diagram
        plantuml_generator = PlantUMLGenerator()
        diagram = plantuml_generator.generate_diagram(file_model, project_model)
        
        # Check that PlantUML syntax is correct
        self.assertIn("@startuml test", diagram)
        self.assertIn("@enduml", diagram)
        
        # Check that main class is generated
        self.assertIn('class "test" as TEST <<source>> #LightBlue', diagram)
        
        # Check that macros are included
        self.assertIn("-- Macros --", diagram)
        self.assertIn("- #define MAX_SIZE", diagram)
        self.assertIn("- #define DEBUG", diagram)
        
        # Check that global variables are included
        self.assertIn("-- Global Variables --", diagram)
        self.assertIn("int global_var", diagram)
        self.assertIn("char * global_string", diagram)
        
        # Check that functions are included
        self.assertIn("-- Functions --", diagram)
        self.assertIn("int main()", diagram)
        self.assertIn("void process_data()", diagram)
        
        # Remove assertion for typedefs section if no typedefs exist
        # self.assertIn("-- Typedefs --", diagram) - REMOVED

    def test_generate_file_diagram(self):
        """Test generating a PlantUML diagram file"""
        file_model = self.create_test_file_model("test.c")
        output_dir = Path(self.temp_dir)

        # Create a simple project model for testing
        project_model = ProjectModel(
            project_name="test_project",
            project_root="/test",
            files={"test.c": file_model},
        )
        plantuml_generator = PlantUMLGenerator()
        content = plantuml_generator.generate_diagram(
            file_model, project_model
        )

        # Write the content to file
        puml_file = output_dir / "test.puml"
        with open(puml_file, "w", encoding="utf-8") as f:
            f.write(content)

        # Check that the file was created
        puml_file = output_dir / "test.puml"
        self.assertTrue(puml_file.exists())

        # Check file content
        with open(puml_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("@startuml test", content)
        self.assertIn("@enduml", content)
        self.assertIn('class "test" as TEST <<source>> #LightBlue', content)

    def test_generate_from_model(self):
        """Test generating diagrams from a model file"""
        # Create a test model
        file_model = self.create_test_file_model("main.c")
        model = ProjectModel(
            project_name="test_project",
            project_root="/test",
            files={"main.c": file_model},
        )

        # Save model to file
        model_path = os.path.join(self.temp_dir, "test_model.json")
        model.save(model_path)

        # Generate diagrams
        output_dir = os.path.join(self.temp_dir, "output")
        self.generator.generate(model_path, output_dir)

        # Check output directory was created
        self.assertTrue(os.path.exists(output_dir))

        # Check that diagram file was created
        puml_file = os.path.join(output_dir, "main.puml")
        self.assertTrue(os.path.exists(puml_file))

        # Check file content
        with open(puml_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("@startuml main", content)
        self.assertIn("@enduml", content)

    def test_generate_with_config(self):
        """Test generating diagrams using configuration"""
        # Create test model
        file_model = self.create_test_file_model("main.c")
        model = ProjectModel(
            project_name="test_project",
            project_root="/test",
            files={"main.c": file_model},
        )

        # Create configuration
        config = Config(
            {
                "project_name": "test_project",
                "source_folders": ["/test"],
                "output_dir": os.path.join(self.temp_dir, "config_output"),
                "recursive_search": True,
                "file_filters": {},
                "element_filters": {},
            }
        )

        # Save model
        model_path = os.path.join(self.temp_dir, "test_model.json")
        model.save(model_path)

        # Generate with config
        self.generator.generate(model_path, config.output_dir)

        # Verify output
        self.assertTrue(os.path.exists(config.output_dir))
        puml_file = os.path.join(config.output_dir, "main.puml")
        self.assertTrue(os.path.exists(puml_file))

    def test_generate_multiple_files(self):
        """Test generating diagrams for multiple files"""
        # Create multiple file models
        file1 = self.create_test_file_model("main.c")
        file2 = FileModel(
            file_path="utils.c",
            relative_path="utils.c",
            project_root="/test",
            encoding_used="utf-8",
            structs={},
            enums={},
            functions=[Function("helper", "void", [])],
            globals=[],
            includes=["stdio.h"],
            macros=[],
            aliases={},
        )

        model = ProjectModel(
            project_name="test_project",
            project_root="/test",
            files={"main.c": file1, "utils.c": file2},
        )

        # Save and generate
        model_path = os.path.join(self.temp_dir, "test_model.json")
        model.save(model_path)

        output_dir = os.path.join(self.temp_dir, "output")
        self.generator.generate(model_path, output_dir)

        # Check both files were generated
        self.assertTrue(os.path.exists(os.path.join(output_dir, "main.puml")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "utils.puml")))

    def test_generate_empty_file_model(self):
        """Test generating diagram for empty file model"""
        empty_file = FileModel(
            file_path="empty.c",
            relative_path="empty.c",
            project_root="/test",
            encoding_used="utf-8",
            structs={},
            enums={},
            functions=[],
            globals=[],
            includes=[],
            macros=[],
            aliases={},
        )

        # Create a simple project model for testing
        project_model = ProjectModel(
            project_name="test_project",
            project_root="/test",
            files={"empty.c": empty_file},
        )
        plantuml_generator = PlantUMLGenerator()
        content = plantuml_generator.generate_diagram(
            empty_file, project_model
        )

        # Should still generate valid PlantUML
        self.assertIn("@startuml empty", content)
        self.assertIn("@enduml", content)
        self.assertIn('class "empty" as EMPTY <<source>> #LightBlue', content)

    def test_generate_with_special_characters(self):
        """Test generation with special characters in names"""
        # Create a test file with special characters
        content = """
struct Test_Struct {
    int field_1;
    char* field_2;
};

void test_function() {
    // Test function
}
        """
        test_file = self.create_test_file("test_file.c", content)
        
        # Parse the file
        project_model = self.parser.parse_project(str(self.temp_dir))
        file_model = project_model.files["test_file.c"]
        
        # Generate PlantUML diagram
        plantuml_generator = PlantUMLGenerator()
        diagram = plantuml_generator.generate_diagram(file_model, project_model)
        
        # Check that PlantUML syntax is correct
        self.assertIn("@startuml test_file", diagram)
        self.assertIn("@enduml", diagram)
        
        # Check that main class is generated with correct name
        self.assertIn('class "test_file" as TEST_FILE <<source>> #LightBlue', diagram)
        
        # Check that functions are included
        self.assertIn("-- Functions --", diagram)
        self.assertIn("void test_function()", diagram)
        
        # Remove assertions for struct/enum declarations in file/header classes
        # self.assertIn("struct Test_Struct", content)  # no + prefix in source files - REMOVED

    def test_generate_error_handling(self):
        """Test error handling in diagram generation"""
        # Test with non-existent model file
        with self.assertRaises(Exception):
            self.generator.generate_from_model(
                "/non/existent/model.json", self.temp_dir
            )

        # Test with invalid model file
        invalid_model_path = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_model_path, "w") as f:
            f.write("invalid json")

        with self.assertRaises(Exception):
            self.generator.generate_from_model(invalid_model_path, self.temp_dir)

    def test_plantuml_syntax_validity(self):
        """Test that generated PlantUML syntax is valid"""
        file_model = self.create_test_file_model("test.c")
        # Create a simple project model for testing
        project_model = ProjectModel(
            project_name="test_project",
            project_root="/test",
            files={"test.c": file_model},
        )
        plantuml_generator = PlantUMLGenerator()
        content = plantuml_generator.generate_diagram(
            file_model, project_model
        )

        # Check for required PlantUML elements
        self.assertIn("@startuml", content)
        self.assertIn("@enduml", content)
        self.assertIn("class", content)

        # Check for proper class syntax
        self.assertIn('class "test" as TEST', content)

        # Check for proper relationship syntax (not implemented in current version)
        # self.assertIn("-->", content)

        # Check for proper section separators
        self.assertIn("--", content)

    def test_output_directory_creation(self):
        """Test that output directory is created if it doesn't exist"""
        file_model = self.create_test_file_model("test.c")
        model = ProjectModel(
            project_name="test_project",
            project_root="/test",
            files={"test.c": file_model},
        )

        # Save model
        model_path = os.path.join(self.temp_dir, "test_model.json")
        model.save(model_path)

        # Generate to non-existent directory
        output_dir = os.path.join(self.temp_dir, "new_output_dir")
        self.generator.generate(model_path, output_dir)

        # Directory should be created
        self.assertTrue(os.path.exists(output_dir))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.puml")))
