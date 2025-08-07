#!/usr/bin/env python3
"""
Unit tests for the C parser using the unified testing framework

This test demonstrates how to convert existing tests to use the unified framework
that enforces CLI-only access to c2puml functionality.
"""

import json
import os
import sys
import unittest

# Add the tests directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from framework import UnifiedTestCase


class TestCParserUnified(UnifiedTestCase):
    """Test the C parser functionality using the unified framework"""

    def test_parse_simple_c_file(self):
        """
        Test parsing a simple C file through the CLI interface
        
        This test demonstrates the conversion from direct internal API access
        to CLI-only execution using the unified testing framework.
        """
        # Create test source files using the framework
        source_files = {
            "simple.c": """
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
        }
        
        # Create test configuration
        config_data = {
            "project_name": "test_parser_simple",
            "source_folders": ["."],
            "output_dir": self.output_dir,
            "recursive_search": True
        }
        
        # Create test files using framework helpers
        source_dir = self.create_test_source_files(source_files)
        config_path = self.create_test_config(config_data)
        
        # Execute c2puml through CLI using framework
        result = self.run_c2puml_full_pipeline(config_path, source_dir)
        
        # Validate execution success
        self.assert_c2puml_success(result)
        
        # Validate output files were created
        model_file = self.assert_model_file_exists()
        transformed_model_file = self.assert_transformed_model_file_exists()
        puml_files = self.assert_puml_files_exist()
        
        # Load and validate the model.json content
        with open(model_file, 'r') as f:
            model_data = json.load(f)
        
        # Verify the model structure
        self.assertIn("files", model_data)
        self.assertGreater(len(model_data["files"]), 0)
        
        # Find our simple.c file in the model
        simple_c_file = model_data["files"].get("simple.c")
        self.assertIsNotNone(simple_c_file, "simple.c should be in the model")
        
        # Validate struct parsing
        structs = simple_c_file.get("structs", {})
        self.assertGreater(len(structs), 0, "Should find at least one struct")
        
        # Find Person struct
        person_struct = structs.get("Person")
        self.assertIsNotNone(person_struct, "Person struct should be found")
        
        # Validate Person struct fields
        fields = person_struct.get("fields", [])
        self.assertEqual(len(fields), 2, "Person struct should have 2 fields")
        
        field_names = [field.get("name") for field in fields]
        self.assertIn("name", field_names)
        self.assertIn("age", field_names)
        
        # Validate enum parsing
        enums = simple_c_file.get("enums", {})
        self.assertGreater(len(enums), 0, "Should find at least one enum")
        
        # Find Status enum
        status_enum = enums.get("Status")
        self.assertIsNotNone(status_enum, "Status enum should be found")
        
        # Validate Status enum values
        values = status_enum.get("values", [])
        self.assertEqual(len(values), 2, "Status enum should have 2 values")
        
        value_names = [value.get("name") for value in values]
        self.assertIn("OK", value_names)
        self.assertIn("ERROR", value_names)
        
        # Validate function parsing
        functions = simple_c_file.get("functions", [])
        self.assertGreater(len(functions), 0, "Should find at least one function")
        
        # Find main function
        main_function = None
        for func in functions:
            if func.get("name") == "main":
                main_function = func
                break
        
        self.assertIsNotNone(main_function, "main function should be found")
        
        # Validate global variable parsing
        globals_list = simple_c_file.get("globals", [])
        self.assertGreater(len(globals_list), 0, "Should find at least one global variable")
        
        # Find global_var
        global_var_found = False
        for global_var in globals_list:
            if global_var.get("name") == "global_var":
                global_var_found = True
                break
        
        self.assertTrue(global_var_found, "global_var should be found")
        
        # Validate include parsing
        includes = simple_c_file.get("includes", [])
        self.assertGreater(len(includes), 0, "Should find at least one include")
        
        # Check for stdio.h include
        self.assertIn("stdio.h", includes, "stdio.h include should be found")
        
        # Validate PlantUML file content
        self.assertGreater(len(puml_files), 0, "Should have at least one .puml file")
        
        # Check that the first .puml file contains expected content
        with open(puml_files[0], 'r') as f:
            puml_content = f.read()
        
        # Verify PlantUML contains our struct and enum
        self.assertIn("Person", puml_content, "PlantUML should contain Person struct")
        self.assertIn("Status", puml_content, "PlantUML should contain Status enum")
        self.assertIn("main", puml_content, "PlantUML should contain main function")
        
        # Verify PlantUML syntax
        self.assertIn("@startuml", puml_content, "PlantUML should start with @startuml")
        self.assertIn("@enduml", puml_content, "PlantUML should end with @enduml")


if __name__ == "__main__":
    unittest.main()