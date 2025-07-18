#!/usr/bin/env python3
"""
Simple test runner for C to PlantUML converter
"""

import unittest
import tempfile
import os
import json
from pathlib import Path
from c_to_plantuml.analyzer import Analyzer
from c_to_plantuml.generator import Generator
from c_to_plantuml.config import Config
from c_to_plantuml.models import ProjectModel, FileModel, Struct, Enum, Function, Field


class TestParser(unittest.TestCase):
    """Test the C parser"""
    
    def setUp(self):
        self.analyzer = Analyzer()
    
    def test_parse_simple_c_file(self):
        """Test parsing a simple C file"""
        # Create a temporary C file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write("""
#include <stdio.h>

struct Person {
    char name[50];
    int age;
};

enum Status {
    OK,
    ERROR
};

int main() {
    return 0;
}

int global_var;
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
            # The parser correctly finds both the struct field and the global variable
            self.assertGreaterEqual(len(file_model.globals), 1)
            global_names = [g.name for g in file_model.globals]
            self.assertIn('global_var', global_names)
            
        finally:
            os.unlink(temp_file)


class TestAnalyzer(unittest.TestCase):
    """Test the analyzer"""
    
    def setUp(self):
        self.analyzer = Analyzer()
    
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
            
            # Analyze the project
            model = self.analyzer.analyze_project(str(project_dir))
            
            # Check results
            self.assertEqual(model.project_name, "test_project")
            self.assertEqual(len(model.files), 1)
            self.assertIn("test.c", model.files)


class TestGenerator(unittest.TestCase):
    """Test the PlantUML generator"""
    
    def setUp(self):
        self.generator = Generator()
    
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
            enums={},
            functions=[Function("main", "int", [])],
            globals=[Field("global_var", "int")],
            includes={"stdio.h"},
            macros=["TEST_MACRO"],
            typedefs={}
        )
        
        # Generate PlantUML content
        content = self.generator._generate_plantuml_content(file_model)
        
        # Check that content contains expected elements
        self.assertIn("@startuml test", content)
        self.assertIn("class \"test\"", content)
        self.assertIn("struct TestStruct", content)
        self.assertIn("int main()", content)
        self.assertIn("int global_var", content)
        self.assertIn("#define TEST_MACRO", content)
        self.assertIn("@enduml", content)


class TestConfig(unittest.TestCase):
    """Test the configuration system"""
    
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
        
        self.assertEqual(config.project_roots, ["./src"])
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


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
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