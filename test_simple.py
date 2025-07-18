#!/usr/bin/env python3
"""
Simple test runner for C to PlantUML converter
"""

import unittest
import tempfile
import os
import json
import logging
from pathlib import Path
from c_to_plantuml.analyzer import Analyzer
from c_to_plantuml.generator import Generator
from c_to_plantuml.config import Config
from c_to_plantuml.models import ProjectModel, FileModel, Struct, Enum, Function, Field


class TestParser(unittest.TestCase):
    """Test the C parser"""
    
    def setUp(self):
        self.analyzer = Analyzer()
        # Setup logging for tests
        logging.basicConfig(level=logging.DEBUG)
    
    def test_parse_simple_c_file(self):
        """Test parsing a simple C file"""
        # Create a temporary C file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write("""
#include <stdio.h>
#include <stdlib.h>

struct Person {
    char name[50];
    int age;
    float height;
};

enum Status {
    OK,
    ERROR,
    PENDING
};

int main() {
    return 0;
}

int global_var;
float global_float = 3.14;
            """)
            temp_file = f.name
        
        try:
            # Parse the file
            file_model = self.analyzer.parser.parse_file(Path(temp_file))
            
            # Debug output
            print(f"Found globals: {[g.name for g in file_model.globals]}")
            
            # Check results
            self.assertIn('Person', file_model.structs)
            self.assertIn('Status', file_model.enums)
            self.assertEqual(len(file_model.functions), 1)
            self.assertEqual(file_model.functions[0].name, 'main')
            
            # Check struct fields
            person_struct = file_model.structs['Person']
            self.assertEqual(len(person_struct.fields), 3)
            field_names = [f.name for f in person_struct.fields]
            self.assertIn('name', field_names)
            self.assertIn('age', field_names)
            self.assertIn('height', field_names)
            
            # Check enum values
            status_enum = file_model.enums['Status']
            self.assertEqual(len(status_enum.values), 3)
            self.assertIn('OK', status_enum.values)
            self.assertIn('ERROR', status_enum.values)
            self.assertIn('PENDING', status_enum.values)
            
            # Check globals
            self.assertGreaterEqual(len(file_model.globals), 1)
            global_names = [g.name for g in file_model.globals]
            self.assertIn('global_var', global_names)
            
            # Check includes
            self.assertIn('stdio.h', file_model.includes)
            self.assertIn('stdlib.h', file_model.includes)
            
        finally:
            os.unlink(temp_file)
    
    def test_parse_complex_c_file(self):
        """Test parsing a more complex C file with typedefs and macros"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write("""
#include <stdio.h>

#define MAX_SIZE 100
#define DEBUG_MODE 1

typedef int Integer;
typedef char* String;

struct ComplexStruct {
    Integer id;
    String name;
    void* data;
};

enum Color {
    RED = 0,
    GREEN = 1,
    BLUE = 2
};

static int helper_function() {
    return 0;
}

int public_function(Integer param) {
    return param * 2;
}

Integer global_integer = 42;
String global_string = "test";
            """)
            temp_file = f.name
        
        try:
            file_model = self.analyzer.parser.parse_file(Path(temp_file))
            
            # Check typedefs
            self.assertIn('Integer', file_model.typedefs)
            self.assertIn('String', file_model.typedefs)
            self.assertEqual(file_model.typedefs['Integer'], 'int')
            self.assertEqual(file_model.typedefs['String'], 'char*')
            
            # Check macros
            self.assertIn('MAX_SIZE', file_model.macros)
            self.assertIn('DEBUG_MODE', file_model.macros)
            
            # Check struct
            self.assertIn('ComplexStruct', file_model.structs)
            complex_struct = file_model.structs['ComplexStruct']
            self.assertEqual(len(complex_struct.fields), 3)
            
            # Check enum
            self.assertIn('Color', file_model.enums)
            color_enum = file_model.enums['Color']
            self.assertEqual(len(color_enum.values), 3)
            
            # Check functions (should include both static and public functions)
            function_names = [f.name for f in file_model.functions]
            self.assertIn('public_function', function_names)
            self.assertIn('helper_function', function_names)
            self.assertEqual(len(file_model.functions), 2)
            
        finally:
            os.unlink(temp_file)


class TestAnalyzer(unittest.TestCase):
    """Test the analyzer"""
    
    def setUp(self):
        self.analyzer = Analyzer()
        logging.basicConfig(level=logging.DEBUG)
    
    def test_analyze_project(self):
        """Test analyzing a project"""
        # Create a temporary project structure
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "test_project"
            project_dir.mkdir()
            
            # Create a test C file
            c_file = project_dir / "test.c"
            c_file.write_text("""
struct TestStruct {
    int field1;
    char field2;
};

int main() {
    return 0;
}
            """)
            
            # Create a header file
            h_file = project_dir / "test.h"
            h_file.write_text("""
#ifndef TEST_H
#define TEST_H

typedef int MyInt;
#define TEST_MACRO 42

#endif
            """)
            
            # Analyze the project
            model = self.analyzer.analyze_project(str(project_dir))
            
            # Check results
            self.assertEqual(model.project_name, "test_project")
            self.assertEqual(len(model.files), 2)
            self.assertIn("test.c", model.files)
            self.assertIn("test.h", model.files)
            
            # Check file contents
            test_c = model.files["test.c"]
            self.assertIn("TestStruct", test_c.structs)
            self.assertEqual(len(test_c.functions), 1)
            
            test_h = model.files["test.h"]
            self.assertIn("MyInt", test_h.typedefs)
            self.assertIn("TEST_MACRO", test_h.macros)
    
    def test_analyze_empty_project(self):
        """Test analyzing an empty project"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "empty_project"
            project_dir.mkdir()
            
            model = self.analyzer.analyze_project(str(project_dir))
            
            self.assertEqual(model.project_name, "empty_project")
            self.assertEqual(len(model.files), 0)
    
    def test_analyze_with_invalid_files(self):
        """Test analyzing a project with some invalid files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "mixed_project"
            project_dir.mkdir()
            
            # Create valid C file
            valid_file = project_dir / "valid.c"
            valid_file.write_text("int main() { return 0; }")
            
            # Create invalid file (binary)
            invalid_file = project_dir / "invalid.c"
            invalid_file.write_bytes(b'\x00\x01\x02\x03')
            
            # Create non-C file
            text_file = project_dir / "readme.txt"
            text_file.write_text("This is not a C file")
            
            model = self.analyzer.analyze_project(str(project_dir))
            
            # Should have both C files (valid and invalid are both .c files)
            self.assertEqual(len(model.files), 2)
            self.assertIn("valid.c", model.files)
            self.assertIn("invalid.c", model.files)
            
            # The invalid file should be parsed but empty
            invalid_model = model.files["invalid.c"]
            self.assertEqual(len(invalid_model.functions), 0)
            self.assertEqual(len(invalid_model.structs), 0)


class TestGenerator(unittest.TestCase):
    """Test the PlantUML generator"""
    
    def setUp(self):
        self.generator = Generator()
        logging.basicConfig(level=logging.DEBUG)
    
    def test_generate_plantuml(self):
        """Test generating PlantUML content"""
        # Create a test file model
        file_model = FileModel(
            file_path="test.c",
            relative_path="test.c",
            project_root=".",
            encoding_used="utf-8",
            structs={
                "TestStruct": Struct("TestStruct", [
                    Field("field1", "int"),
                    Field("field2", "char")
                ], [])
            },
            enums={
                "TestEnum": Enum("TestEnum", ["VALUE1", "VALUE2"])
            },
            functions=[Function("main", "int", [])],
            globals=[Field("global_var", "int")],
            includes={"stdio.h", "stdlib.h"},
            macros=["TEST_MACRO", "DEBUG_MODE"],
            typedefs={"MyInt": "int", "MyString": "char*"}
        )
        
        # Generate PlantUML content
        content = self.generator._generate_plantuml_content(file_model)
        
        # Check that content contains expected elements
        self.assertIn("@startuml test", content)
        self.assertIn("class \"test\" as TEST <<source>> #LightBlue", content)
        self.assertIn("struct TestStruct", content)
        self.assertIn("int main()", content)
        self.assertIn("int global_var", content)
        self.assertIn("#define TEST_MACRO", content)
        self.assertIn("#include <stdio.h>", content)
        self.assertIn("typedef int MyInt", content)
        self.assertIn("enum TestEnum", content)
        self.assertIn("VALUE1", content)
        self.assertIn("@enduml", content)
    
    def test_generate_diagram_file(self):
        """Test generating actual PlantUML diagram files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file model
            file_model = FileModel(
                file_path="test.c",
                relative_path="test.c",
                project_root=".",
                encoding_used="utf-8",
                structs={
                    "TestStruct": Struct("TestStruct", [
                        Field("field1", "int"),
                        Field("field2", "char")
                    ], [])
                },
                enums={},
                functions=[Function("main", "int", [])],
                globals=[Field("global_var", "int")],
                includes={"stdio.h"},
                macros=["TEST_MACRO"],
                typedefs={}
            )
            
            # Generate diagram
            output_dir = Path(temp_dir) / "output"
            self.generator._generate_file_diagram(file_model, output_dir)
            
            # Check that file was created
            puml_file = output_dir / "test.puml"
            self.assertTrue(puml_file.exists())
            
            # Check file content
            content = puml_file.read_text()
            self.assertIn("@startuml test", content)
            self.assertIn("@enduml", content)


class TestConfig(unittest.TestCase):
    """Test the configuration system"""
    
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
    
    def test_load_config(self):
        """Test loading configuration from JSON"""
        config_data = {
            "project_roots": ["./src"],
            "project_name": "TestProject",
            "output_dir": "./output",
            "file_filters": {
                "include": [".*\\.c$"],
                "exclude": [".*test.*"]
            }
        }
        
        config = Config(config_data)
        
        self.assertEqual(config.project_roots, [str(Path("./src").resolve())])
        self.assertEqual(config.project_name, "TestProject")
        self.assertEqual(config.output_dir, "./output")
        self.assertTrue(config.has_filters())
    
    def test_file_filtering(self):
        """Test file filtering"""
        config_data = {
            "file_filters": {
                "include": [".*\\.c$"],
                "exclude": [".*test.*"]
            }
        }
        
        config = Config(config_data)
        
        # Test include filter
        self.assertTrue(config._should_include_file("main.c"))
        self.assertFalse(config._should_include_file("main.h"))
        
        # Test exclude filter
        self.assertFalse(config._should_include_file("test_main.c"))
        self.assertTrue(config._should_include_file("main.c"))
    
    def test_config_validation(self):
        """Test configuration validation"""
        # Test invalid project roots
        with self.assertRaises(ValueError):
            Config({"project_roots": "not_a_list"})
        
        # Test invalid project root type
        with self.assertRaises(ValueError):
            Config({"project_roots": [123]})
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"
            
            # Create config
            original_config = Config({
                "project_roots": ["./src"],
                "project_name": "TestProject",
                "output_dir": "./output"
            })
            
            # Save config
            original_config.save(str(config_file))
            
            # Load config
            loaded_config = Config.load(str(config_file))
            
            # Compare
            self.assertEqual(original_config.project_name, loaded_config.project_name)
            self.assertEqual(original_config.output_dir, loaded_config.output_dir)


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
    
    def test_full_workflow(self):
        """Test the complete workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test project
            project_dir = Path(temp_dir) / "test_project"
            project_dir.mkdir()
            
            # Create test C file
            c_file = project_dir / "main.c"
            c_file.write_text("""
#include <stdio.h>

struct Person {
    char name[50];
    int age;
};

int main() {
    return 0;
}
            """)
            
            # Create config
            config_data = {
                "project_roots": [str(project_dir)],
                "project_name": "TestProject",
                "output_dir": str(Path(temp_dir) / "output"),
                "recursive": True
            }
            
            config = Config(config_data)
            
            # Run analysis
            analyzer = Analyzer()
            model = analyzer.analyze_with_config(config)
            
            # Run generation
            generator = Generator()
            generator.generate_with_config(model, config)
            
            # Check output
            output_dir = Path(temp_dir) / "output"
            self.assertTrue(output_dir.exists())
            self.assertTrue((output_dir / "main.puml").exists())
            
            # Check generated content
            puml_content = (output_dir / "main.puml").read_text()
            self.assertIn("@startuml main", puml_content)
            self.assertIn("struct Person", puml_content)
            self.assertIn("int main()", puml_content)
    
    def test_model_serialization(self):
        """Test model serialization and deserialization"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test model
            file_model = FileModel(
                file_path="test.c",
                relative_path="test.c",
                project_root=".",
                encoding_used="utf-8",
                structs={
                    "TestStruct": Struct("TestStruct", [
                        Field("field1", "int"),
                        Field("field2", "char")
                    ], [])
                },
                enums={},
                functions=[Function("main", "int", [])],
                globals=[Field("global_var", "int")],
                includes={"stdio.h"},
                macros=["TEST_MACRO"],
                typedefs={}
            )
            
            model = ProjectModel(
                project_name="TestProject",
                project_root=".",
                files={"test.c": file_model}
            )
            
            # Save model
            model_file = Path(temp_dir) / "test_model.json"
            model.save(str(model_file))
            
            # Load model
            loaded_model = ProjectModel.load(str(model_file))
            
            # Compare
            self.assertEqual(model.project_name, loaded_model.project_name)
            self.assertEqual(len(model.files), len(loaded_model.files))
            self.assertIn("test.c", loaded_model.files)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestParser,
        TestAnalyzer,
        TestGenerator,
        TestConfig,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)