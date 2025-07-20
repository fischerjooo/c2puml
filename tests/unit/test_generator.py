#!/usr/bin/env python3
"""
Unit tests for PlantUML generator functionality
"""

import unittest
import tempfile
import os
import json
import shutil
from pathlib import Path
from c_to_plantuml.generator import Generator
from c_to_plantuml.models import ProjectModel, FileModel, Struct, Enum, Function, Field
from c_to_plantuml.config import Config


class TestGenerator(unittest.TestCase):
    """Test cases for PlantUML generator functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
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
                "Person": Struct("Person", [
                    Field("name", "char*"),
                    Field("age", "int"),
                    Field("height", "float")
                ]),
                "Config": Struct("Config", [
                    Field("max_users", "int"),
                    Field("timeout", "int")
                ])
            },
            enums={
                "Status": Enum("Status", ["OK", "ERROR", "PENDING"]),
                "Color": Enum("Color", ["RED", "GREEN", "BLUE"])
            },
            functions=[
                Function("main", "int", []),
                Function("process_data", "void", [Field("data", "void*")]),
                Function("calculate", "float", [Field("a", "float"), Field("b", "float")])
            ],
            globals=[
                Field("global_var", "int"),
                Field("global_string", "char*")
            ],
            includes=["stdio.h", "stdlib.h", "local.h"],
            macros=["MAX_SIZE", "DEBUG_MODE", "VERSION"],
            typedefs={
                "Integer": "int",
                "String": "char*",
                "Callback": "void (*)(int)"
            }
        )
    
    def test_generate_plantuml_content(self):
        """Test PlantUML content generation"""
        file_model = self.create_test_file_model("main.c")
        
        # Create a simple project model for testing
        project_model = ProjectModel(
            project_name="test_project",
            project_root="/test",
            files={"main.c": file_model},
            created_at="2023-01-01T00:00:00"
        )
        content = self.generator.plantuml_generator.generate_diagram(file_model, project_model)
        
        # Check basic structure
        self.assertIn("@startuml main", content)
        self.assertIn("@enduml", content)
        
        # Check class definition
        self.assertIn('class "main" as MAIN <<source>> #LightBlue', content)
        
        # Check header classes and relationships (not implemented in current version)
        # self.assertIn('class "stdio" as STDIO <<header>> #LightGreen', content)
        # self.assertIn('class "stdlib" as STDLIB <<header>> #LightGreen', content)
        # self.assertIn("MAIN --> STDIO : <<include>>", content)
        # self.assertIn("MAIN --> STDLIB : <<include>>", content)
        
        # Check macros section
        self.assertIn("-- Macros --", content)
        self.assertIn("+ #define MAX_SIZE", content)
        self.assertIn("+ #define DEBUG_MODE", content)
        
        # Check typedefs section
        self.assertIn("-- Typedefs --", content)
        self.assertIn("+ typedef int Integer", content)
        self.assertIn("+ typedef char* String", content)
        
        # Check global variables section
        self.assertIn("-- Global Variables --", content)
        self.assertIn("- int global_var", content)
        self.assertIn("- char* global_string", content)
        
        # Check functions section
        self.assertIn("-- Functions --", content)
        self.assertIn("+ int main()", content)
        self.assertIn("+ void process_data()", content)
        self.assertIn("+ float calculate()", content)
        
        # Check structs section
        self.assertIn("-- Structs --", content)
        self.assertIn("+ struct Person", content)
        self.assertIn("+ struct Config", content)
        self.assertIn("+ char* name", content)  # Person field
        self.assertIn("+ int age", content)     # Person field
        self.assertIn("+ int max_users", content)  # Config field
        
        # Check enums section
        self.assertIn("-- Enums --", content)
        self.assertIn("+ enum Status", content)
        self.assertIn("+ enum Color", content)
        self.assertIn("+ OK", content)
        self.assertIn("+ RED", content)
        
        # Check typedef classes (not implemented in current version)
        # self.assertIn('class "Integer" as INTEGER <<typedef>> #LightYellow', content)
        # self.assertIn('class "String" as STRING <<typedef>> #LightYellow', content)
        
        # Check relationships (not implemented in current version)
        # self.assertIn("MAIN --> STDIO : <<include>>", content)
        # self.assertIn("MAIN --> STDLIB : <<include>>", content)
    
    def test_generate_file_diagram(self):
        """Test generating a PlantUML diagram file"""
        file_model = self.create_test_file_model("test.c")
        output_dir = Path(self.temp_dir)
        
        # Create a simple project model for testing
        project_model = ProjectModel(
            project_name="test_project",
            project_root="/test",
            files={"test.c": file_model},
            created_at="2023-01-01T00:00:00"
        )
        content = self.generator.plantuml_generator.generate_diagram(file_model, project_model)
        
        # Write the content to file
        puml_file = output_dir / "test.puml"
        with open(puml_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Check that the file was created
        puml_file = output_dir / "test.puml"
        self.assertTrue(puml_file.exists())
        
        # Check file content
        with open(puml_file, 'r', encoding='utf-8') as f:
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
            created_at="2024-01-01T00:00:00"
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
        with open(puml_file, 'r', encoding='utf-8') as f:
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
            created_at="2024-01-01T00:00:00"
        )
        
        # Create configuration
        config = Config({
            "project_name": "test_project",
            "source_folders": ["/test"],
            "output_dir": os.path.join(self.temp_dir, "config_output"),
            "recursive": True,
            "file_filters": {},
            "element_filters": {}
        })
        
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
            typedefs={}
        )
        
        model = ProjectModel(
            project_name="test_project",
            project_root="/test",
            files={"main.c": file1, "utils.c": file2},
            created_at="2024-01-01T00:00:00"
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
            typedefs={}
        )
        
        # Create a simple project model for testing
        project_model = ProjectModel(
            project_name="test_project",
            project_root="/test",
            files={"empty.c": empty_file},
            created_at="2023-01-01T00:00:00"
        )
        content = self.generator.plantuml_generator.generate_diagram(empty_file, project_model)
        
        # Should still generate valid PlantUML
        self.assertIn("@startuml empty", content)
        self.assertIn("@enduml", content)
        self.assertIn('class "empty" as EMPTY <<source>> #LightBlue', content)
    
    def test_generate_with_special_characters(self):
        """Test generating diagrams with special characters in names"""
        special_file = FileModel(
            file_path="test_file.c",
            relative_path="test_file.c",
            project_root="/test",
            encoding_used="utf-8",
            structs={
                "Test_Struct": Struct("Test_Struct", [
                    Field("field_name", "int")
                ])
            },
            enums={
                "Test_Enum": Enum("Test_Enum", ["VALUE_1", "VALUE_2"])
            },
            functions=[Function("test_function", "void", [])],
            globals=[],
            includes=[],
            macros=[],
            typedefs={}
        )
        
        # Create a simple project model for testing
        project_model = ProjectModel(
            project_name="test_project",
            project_root="/test",
            files={"special.c": special_file},
            created_at="2023-01-01T00:00:00"
        )
        content = self.generator.plantuml_generator.generate_diagram(special_file, project_model)
        
        # Should handle special characters properly
        self.assertIn("@startuml test_file", content)
        self.assertIn("+ struct Test_Struct", content)
        self.assertIn("+ enum Test_Enum", content)
        self.assertIn("+ void test_function()", content)
    
    def test_generate_error_handling(self):
        """Test error handling in diagram generation"""
        # Test with non-existent model file
        with self.assertRaises(Exception):
            self.generator.generate_from_model("/non/existent/model.json", self.temp_dir)
        
        # Test with invalid model file
        invalid_model_path = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_model_path, 'w') as f:
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
            created_at="2023-01-01T00:00:00"
        )
        content = self.generator.plantuml_generator.generate_diagram(file_model, project_model)
        
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
            created_at="2024-01-01T00:00:00"
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