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
        
        content = self.generator._generate_plantuml_content(file_model)
        
        # Check basic structure
        self.assertIn("@startuml main", content)
        self.assertIn("@enduml", content)
        
        # Check class definition
        self.assertIn('class "main" as MAIN <<source>> #LightBlue', content)
        
        # Check header classes and relationships (includes are now shown as separate classes)
        self.assertIn('class "stdio" as STDIO <<header>> #LightGreen', content)
        self.assertIn('class "stdlib" as STDLIB <<header>> #LightGreen', content)
        self.assertIn("MAIN --> STDIO : <<include>>", content)
        self.assertIn("MAIN --> STDLIB : <<include>>", content)
        
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
        
        # Check typedef classes
        self.assertIn('class "Integer" as INTEGER <<typedef>> #LightYellow', content)
        self.assertIn('class "String" as STRING <<typedef>> #LightYellow', content)
        
        # Check relationships
        self.assertIn("MAIN --> STDIO : <<include>>", content)
        self.assertIn("MAIN --> STDLIB : <<include>>", content)
    
    def test_generate_file_diagram(self):
        """Test generating a PlantUML diagram file"""
        file_model = self.create_test_file_model("test.c")
        output_dir = Path(self.temp_dir)
        
        self.generator._generate_file_diagram(file_model, output_dir)
        
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
        self.generator.generate_from_model(model_path, output_dir)
        
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
            "project_roots": ["/test"],
            "output_dir": os.path.join(self.temp_dir, "config_output"),
            "model_output_path": "model.json",
            "recursive": True
        })
        
        # Generate diagrams
        self.generator.generate_with_config(model, config)
        
        # Check output directory was created
        output_dir = os.path.join(self.temp_dir, "config_output")
        self.assertTrue(os.path.exists(output_dir))
        
        # Check that diagram file was created
        puml_file = os.path.join(output_dir, "main.puml")
        self.assertTrue(os.path.exists(puml_file))
    
    def test_generate_multiple_files(self):
        """Test generating diagrams for multiple files"""
        # Create multiple file models
        file1 = self.create_test_file_model("main.c")
        file2 = self.create_test_file_model("utils.c")
        file2.structs = {"Helper": Struct("Helper", [Field("data", "void*")])}
        file2.functions = [Function("helper_func", "void", [])]
        
        model = ProjectModel(
            project_name="test_project",
            project_root="/test",
            files={
                "main.c": file1,
                "utils.c": file2
            },
            created_at="2024-01-01T00:00:00"
        )
        
        # Save model to file
        model_path = os.path.join(self.temp_dir, "test_model.json")
        model.save(model_path)
        
        # Generate diagrams
        output_dir = os.path.join(self.temp_dir, "output")
        self.generator.generate_from_model(model_path, output_dir)
        
        # Check that both diagram files were created
        main_puml = os.path.join(output_dir, "main.puml")
        utils_puml = os.path.join(output_dir, "utils.puml")
        
        self.assertTrue(os.path.exists(main_puml))
        self.assertTrue(os.path.exists(utils_puml))
        
        # Check content of utils.puml
        with open(utils_puml, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn("@startuml utils", content)
        self.assertIn("+ struct Helper", content)
        self.assertIn("+ void helper_func()", content)
    
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
        
        output_dir = Path(self.temp_dir)
        self.generator._generate_file_diagram(empty_file, output_dir)
        
        # Check that the file was created
        puml_file = output_dir / "empty.puml"
        self.assertTrue(puml_file.exists())
        
        # Check file content
        with open(puml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn("@startuml empty", content)
        self.assertIn('class "empty" as EMPTY <<source>> #LightBlue', content)
        self.assertIn("@enduml", content)
    
    def test_generate_with_special_characters(self):
        """Test generating diagram with special characters in names"""
        file_model = FileModel(
            file_path="test_file.c",
            relative_path="test_file.c",
            project_root="/test",
            encoding_used="utf-8",
            structs={
                "Test_Struct": Struct("Test_Struct", [
                    Field("field_name", "int"),
                    Field("another_field", "char*")
                ])
            },
            enums={
                "Test_Enum": Enum("Test_Enum", ["VALUE_1", "VALUE_2"])
            },
            functions=[
                Function("test_function", "void", [Field("param_name", "int")])
            ],
            globals=[],
            includes=[],
            macros=[],
            typedefs={}
        )
        
        output_dir = Path(self.temp_dir)
        self.generator._generate_file_diagram(file_model, output_dir)
        
        # Check that the file was created
        puml_file = output_dir / "test_file.puml"
        self.assertTrue(puml_file.exists())
        
        # Check file content
        with open(puml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.assertIn("@startuml test_file", content)
        self.assertIn("+ struct Test_Struct", content)
        self.assertIn("+ int field_name", content)
        self.assertIn("+ enum Test_Enum", content)
        self.assertIn("+ VALUE_1", content)
        self.assertIn("+ void test_function()", content)
    
    def test_generate_error_handling(self):
        """Test error handling during generation"""
        # Test with non-existent model file
        with self.assertRaises(ValueError):
            self.generator.generate_from_model("non_existent.json", self.temp_dir)
        
        # Test with invalid model file
        invalid_model_path = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_model_path, 'w') as f:
            f.write("invalid json content")
        
        with self.assertRaises(ValueError):
            self.generator.generate_from_model(invalid_model_path, self.temp_dir)


if __name__ == '__main__':
    unittest.main()