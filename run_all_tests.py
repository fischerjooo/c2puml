#!/usr/bin/env python3
"""
Comprehensive Test Runner for C to PlantUML Converter
Single entry point for all test executions - both local and CI/CD
"""

import unittest
import sys
import os
import tempfile
import json
import shutil
from pathlib import Path

# Add the current directory to the path so we can import the module
sys.path.insert(0, str(Path(__file__).parent))

def run_feature_tests():
    """Run all feature-based tests and return the test result"""
    
    class FeatureTestSuite(unittest.TestCase):
        """Comprehensive feature test suite"""
        
        def setUp(self):
            """Set up test fixtures"""
            self.temp_dir = tempfile.mkdtemp()
            self.test_files = []
            
        def tearDown(self):
            """Clean up test fixtures"""
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            
        def create_test_file(self, filename: str, content: str) -> str:
            """Create a test file and return its path"""
            file_path = os.path.join(self.temp_dir, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.test_files.append(file_path)
            return file_path
        
        def test_feature_parser_basic_parsing(self):
            """Test basic C parsing functionality"""
            from c_to_plantuml.parser import CParser
            
            test_content = """
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
            """
            
            c_file = self.create_test_file("test.c", test_content)
            parser = CParser()
            file_model = parser.parse_file(Path(c_file))
            
            # Verify parsing results
            self.assertIn('Person', file_model.structs)
            self.assertIn('Status', file_model.enums)
            self.assertEqual(len(file_model.functions), 1)
            self.assertEqual(file_model.functions[0].name, 'main')
            self.assertGreaterEqual(len(file_model.globals), 1)
            self.assertIn('stdio.h', file_model.includes)
        
        def test_feature_project_analysis(self):
            """Test project analysis functionality"""
            from c_to_plantuml.analyzer import Analyzer
            
            # Create test project
            file1_content = """
#include <stdio.h>

typedef struct User {
    int id;
    char name[50];
} User;

void print_user(User* user) {
    printf("User: %s\\n", user->name);
}
            """
            
            file2_content = """
#include <stdlib.h>

typedef struct Config {
    int max_users;
    int timeout;
} Config;

Config* create_config(int max_users) {
    return malloc(sizeof(Config));
}
            """
            
            self.create_test_file("user.c", file1_content)
            self.create_test_file("config.c", file2_content)
            
            analyzer = Analyzer()
            model = analyzer.analyze_project(self.temp_dir, recursive=True)
            
            # Verify analysis results
            self.assertEqual(len(model.files), 2)
            file_names = [os.path.basename(fp) for fp in model.files.keys()]
            self.assertIn('user.c', file_names)
            self.assertIn('config.c', file_names)
        
        def test_feature_plantuml_generation(self):
            """Test PlantUML diagram generation"""
            from c_to_plantuml.generator import Generator
            from c_to_plantuml.models import FileModel, Struct, Enum, Function, Field
            
            # Create test file model
            file_model = FileModel(
                file_path="test.c",
                relative_path="test.c",
                project_root="/test",
                encoding_used="utf-8",
                structs={
                    "Person": Struct("Person", [
                        Field("name", "char*"),
                        Field("age", "int")
                    ])
                },
                enums={
                    "Status": Enum("Status", ["OK", "ERROR"])
                },
                functions=[
                    Function("main", "int", [])
                ],
                globals=[],
                includes=["stdio.h"],
                macros=[],
                typedefs={}
            )
            
            generator = Generator()
            content = generator._generate_plantuml_content(file_model, None)
            
            # Verify PlantUML generation
            self.assertIn("@startuml test", content)
            self.assertIn("@enduml", content)
            self.assertIn('class "test" as TEST <<source>> #LightBlue', content)
            self.assertIn('class "stdio" as STDIO <<header>> #LightGreen', content)
            self.assertIn("+ struct Person", content)
            self.assertIn("+ enum Status", content)
        
        def test_feature_configuration_loading(self):
            """Test configuration loading and validation"""
            from c_to_plantuml.config import Config
            
            config_data = {
                "project_name": "test_project",
                "project_roots": [self.temp_dir],  # Use actual existing directory
                "output_dir": "./output",
                "model_output_path": "model.json",
                "recursive": True
            }
            
            config_path = os.path.join(self.temp_dir, "test_config.json")
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            
            config = Config.load(config_path)
            
            # Verify configuration loading
            self.assertEqual(config.project_name, "test_project")
            self.assertEqual(config.project_roots, [self.temp_dir])
            self.assertEqual(config.output_dir, "./output")
            self.assertEqual(config.model_output_path, "model.json")
            self.assertTrue(config.recursive)
        
        def test_feature_complete_workflow(self):
            """Test complete end-to-end workflow"""
            from c_to_plantuml.analyzer import Analyzer
            from c_to_plantuml.generator import Generator
            
            # Create test project
            project_content = """
#include <stdio.h>
#include "config.h"

#define MAX_SIZE 100

typedef struct Person {
    char name[50];
    int age;
} Person;

enum Status {
    OK,
    ERROR
};

int global_var = 42;

int main() {
    printf("Hello, World!\\n");
    return 0;
}

void process_data(void* data) {
    // Process data
}
            """
            
            header_content = """
#ifndef CONFIG_H
#define CONFIG_H

#define CONFIG_VERSION "1.0.0"

typedef struct {
    int id;
    char name[100];
} User;

enum Color {
    RED,
    GREEN,
    BLUE
};

void init_config(void);

#endif
            """
            
            self.create_test_file("main.c", project_content)
            self.create_test_file("config.h", header_content)
            
            # Step 1: Analyze project
            analyzer = Analyzer()
            model = analyzer.analyze_project(self.temp_dir, recursive=True)
            
            # Verify analysis
            self.assertEqual(len(model.files), 2)
            self.assertIn("main.c", model.files)
            self.assertIn("config.h", model.files)
            
            # Step 2: Save model
            model_path = os.path.join(self.temp_dir, "test_model.json")
            model.save(model_path)
            self.assertTrue(os.path.exists(model_path))
            
            # Step 3: Generate PlantUML diagrams
            generator = Generator()
            output_dir = os.path.join(self.temp_dir, "output")
            generator.generate_from_model(model_path, output_dir)
            
            # Verify generation
            self.assertTrue(os.path.exists(output_dir))
            puml_files = list(Path(output_dir).glob("*.puml"))
            # Check that at least one PlantUML file was generated
            self.assertGreaterEqual(len(puml_files), 1, f"Expected at least 1 PlantUML file, got {len(puml_files)}")
            
            # Verify the content of generated files
            for puml_file in puml_files:
                with open(puml_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.assertIn("@startuml", content)
                    self.assertIn("@enduml", content)
        
        def test_feature_error_handling(self):
            """Test error handling in various scenarios"""
            from c_to_plantuml.analyzer import Analyzer
            
            # Test with non-existent directory
            analyzer = Analyzer()
            with self.assertRaises(Exception):
                analyzer.analyze_project("/non/existent/path", recursive=True)
            
            # Test with empty directory
            empty_dir = os.path.join(self.temp_dir, "empty")
            os.makedirs(empty_dir, exist_ok=True)
            model = analyzer.analyze_project(empty_dir, recursive=True)
            self.assertEqual(len(model.files), 0)
        
        def test_feature_performance(self):
            """Test performance with reasonable limits"""
            import time
            from c_to_plantuml.analyzer import Analyzer
            
            # Create a moderately complex test project
            for i in range(5):
                content = f"""
#include <stdio.h>

struct Data{i} {{
    int value{i};
    char name{i}[50];
}};

int process{i}(int input) {{
    return input * {i};
}}
                """
                self.create_test_file(f"file{i}.c", content)
            
            # Measure analysis time
            analyzer = Analyzer()
            start_time = time.perf_counter()
            model = analyzer.analyze_project(self.temp_dir, recursive=True)
            end_time = time.perf_counter()
            
            duration = end_time - start_time
            
            # Verify performance (should complete within 10 seconds for test files)
            self.assertLess(duration, 10.0, f"Analysis took {duration:.2f} seconds, expected < 10 seconds")
            self.assertEqual(len(model.files), 5)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(FeatureTestSuite)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

def main():
    """Main test runner function"""
    print("🧪 Running C to PlantUML Converter Feature Tests")
    print("=" * 60)
    
    # Run all feature tests
    result = run_feature_tests()
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\n❌ ERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    # Return appropriate exit code
    if result.wasSuccessful():
        print("\n✅ All feature tests passed!")
        return 0
    else:
        print("\n❌ Some feature tests failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())