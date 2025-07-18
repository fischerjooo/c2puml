#!/usr/bin/env python3
"""
Integration tests for complete C to PlantUML workflow
"""

import unittest
import tempfile
import os
import json
import shutil
from pathlib import Path
from c_to_plantuml.analyzer import Analyzer
from c_to_plantuml.generator import Generator
from c_to_plantuml.config import Config
from c_to_plantuml.models import ProjectModel


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflow"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = Analyzer()
        self.generator = Generator()
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = []
    
    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_project(self, project_name: str = "test_project") -> str:
        """Create a test project structure"""
        project_dir = os.path.join(self.temp_dir, project_name)
        os.makedirs(project_dir, exist_ok=True)
        
        # Create main.c
        main_c_content = '''
#include <stdio.h>
#include <stdlib.h>
#include "config.h"

#define MAX_SIZE 100
#define DEBUG_MODE 1

typedef int Integer;
typedef char* String;

struct Person {
    char name[50];
    int age;
    float height;
};

struct Config {
    int max_users;
    int timeout;
    String server_name;
};

enum Status {
    OK,
    ERROR,
    PENDING
};

int global_var = 42;
String global_string = "test";

int main() {
    printf("Hello, World!\\n");
    return 0;
}

void process_data(void* data) {
    // Process data
}

float calculate(float a, float b) {
    return a + b;
}
'''
        
        # Create config.h
        config_h_content = '''
#ifndef CONFIG_H
#define CONFIG_H

#define CONFIG_VERSION "1.0.0"
#define DEFAULT_TIMEOUT 30

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
int validate_config(void);

#endif
'''
        
        # Create utils.c
        utils_c_content = '''
#include "config.h"

static int internal_var = 0;

static void debug_log(const char* message) {
    // Debug logging
}

void init_config(void) {
    // Initialize configuration
}

int validate_config(void) {
    return 1;
}

void helper_function(void) {
    // Helper function
}
'''
        
        # Write files
        with open(os.path.join(project_dir, "main.c"), 'w') as f:
            f.write(main_c_content)
        
        with open(os.path.join(project_dir, "config.h"), 'w') as f:
            f.write(config_h_content)
        
        with open(os.path.join(project_dir, "utils.c"), 'w') as f:
            f.write(utils_c_content)
        
        return project_dir
    
    def test_complete_workflow_manual(self):
        """Test complete workflow using manual steps"""
        project_dir = self.create_test_project("manual_workflow")
        
        # Step 1: Analyze project and generate model
        model = self.analyzer.analyze_project(project_dir, recursive=True)
        
        # Verify model structure
        self.assertEqual(model.project_name, "manual_workflow")
        self.assertEqual(len(model.files), 3)  # main.c, config.h, utils.c
        
        # Check that all files are present
        file_names = list(model.files.keys())
        self.assertIn("main.c", file_names)
        self.assertIn("config.h", file_names)
        self.assertIn("utils.c", file_names)
        
        # Check main.c content
        main_file = model.files["main.c"]
        self.assertIn("Person", main_file.structs)
        self.assertIn("Config", main_file.structs)
        self.assertIn("Status", main_file.enums)
        self.assertIn("main", [f.name for f in main_file.functions])
        self.assertIn("process_data", [f.name for f in main_file.functions])
        self.assertIn("calculate", [f.name for f in main_file.functions])
        self.assertIn("stdio.h", main_file.includes)
        self.assertIn("stdlib.h", main_file.includes)
        self.assertIn("config.h", main_file.includes)
        self.assertIn("MAX_SIZE", main_file.macros)
        self.assertIn("DEBUG_MODE", main_file.macros)
        self.assertIn("Integer", main_file.typedefs)
        self.assertIn("String", main_file.typedefs)
        
        # Check config.h content
        config_file = model.files["config.h"]
        self.assertIn("User", config_file.structs)  # This should now be parsed as a typedef struct
        self.assertIn("Color", config_file.enums)
        self.assertIn("init_config", [f.name for f in config_file.functions])
        self.assertIn("validate_config", [f.name for f in config_file.functions])
        self.assertIn("CONFIG_VERSION", config_file.macros)
        self.assertIn("DEFAULT_TIMEOUT", config_file.macros)
        
        # Check utils.c content
        utils_file = model.files["utils.c"]
        self.assertIn("init_config", [f.name for f in utils_file.functions])
        self.assertIn("validate_config", [f.name for f in utils_file.functions])
        self.assertIn("helper_function", [f.name for f in utils_file.functions])
        self.assertIn("debug_log", [f.name for f in utils_file.functions])
        
        # Save model
        model_path = os.path.join(self.temp_dir, "manual_model.json")
        model.save(model_path)
        self.assertTrue(os.path.exists(model_path))
        
        # Step 3: Generate PlantUML diagrams
        output_dir = os.path.join(self.temp_dir, "manual_output")
        self.generator.generate_from_model(model_path, output_dir)
        
        # Check output files
        self.assertTrue(os.path.exists(output_dir))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "main.c.puml")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "utils.c.puml")))
        
        # Check main.c.puml content
        with open(os.path.join(output_dir, "main.c.puml"), 'r') as f:
            main_puml = f.read()
        
        self.assertIn("@startuml main", main_puml)
        self.assertIn("+ struct Person", main_puml)
        self.assertIn("+ struct Config", main_puml)
        self.assertIn("+ enum Status", main_puml)
        self.assertIn("+ int main()", main_puml)
        self.assertIn("+ void process_data()", main_puml)
        self.assertIn("+ float calculate()", main_puml)
        self.assertIn("+ #include <stdio.h>", main_puml)
        self.assertIn("+ #include <stdlib.h>", main_puml)
        self.assertIn("+ #include <config.h>", main_puml)
        self.assertIn("+ #define MAX_SIZE", main_puml)
        self.assertIn("+ typedef int Integer", main_puml)
        self.assertIn("+ typedef char* String", main_puml)
    
    def test_complete_workflow_with_config(self):
        """Test complete workflow using configuration file"""
        project_dir = self.create_test_project("config_workflow")
        
        # Create configuration file
        config_data = {
            "project_name": "config_workflow",
            "project_roots": [project_dir],
            "output_dir": os.path.join(self.temp_dir, "config_output"),
            "model_output_path": os.path.join(self.temp_dir, "config_model.json"),
            "recursive": True,
            "file_filters": {
                "include": [".*\\.c$", ".*\\.h$"],
                "exclude": []
            },
            "element_filters": {
                "structs": {
                    "include": ["Person", "Config", "User"],
                    "exclude": []
                },
                "functions": {
                    "include": ["main", "process_data", "calculate", "init_config"],
                    "exclude": ["debug_.*"]
                }
            }
        }
        
        config_path = os.path.join(self.temp_dir, "test_config.json")
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Load configuration
        config = Config.load(config_path)
        
        # Step 1: Analyze with configuration
        model = self.analyzer.analyze_with_config(config)
        
        # Verify model
        self.assertEqual(model.project_name, "config_workflow")
        self.assertEqual(len(model.files), 3)
        
        # Step 2: Configuration/transformers applied during analysis
        # (handled in analyze_with_config)
        
        # Save model manually since analyze_with_config doesn't save it
        model.save(config.model_output_path)
        
        # Step 3: Generate with configuration
        self.generator.generate_with_config(model, config)
        
        # Check output
        output_dir = os.path.join(self.temp_dir, "config_output")
        self.assertTrue(os.path.exists(output_dir))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "main.c.puml")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "utils.c.puml")))
        
        # Check that model was saved
        model_path = os.path.join(self.temp_dir, "config_model.json")
        self.assertTrue(os.path.exists(model_path))
    
    def test_workflow_with_filtering(self):
        """Test workflow with file and element filtering"""
        project_dir = self.create_test_project("filter_workflow")
        
        # Create configuration with aggressive filtering
        config_data = {
            "project_name": "filter_workflow",
            "project_roots": [project_dir],
            "output_dir": os.path.join(self.temp_dir, "filter_output"),
            "model_output_path": os.path.join(self.temp_dir, "filter_model.json"),
            "recursive": True,
            "file_filters": {
                "include": [".*\\.c$"],  # Only .c files
                "exclude": []
            },
            "element_filters": {
                "structs": {
                    "include": ["Person"],  # Only Person struct
                    "exclude": []
                },
                "functions": {
                    "include": ["main"],  # Only main function
                    "exclude": []
                }
            }
        }
        
        config_path = os.path.join(self.temp_dir, "filter_config.json")
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        config = Config.load(config_path)
        
        # Analyze with filtering
        model = self.analyzer.analyze_with_config(config)
        
        # Should only have .c files
        self.assertEqual(len(model.files), 2)  # main.c and utils.c
        self.assertIn("main.c", model.files)
        self.assertIn("utils.c", model.files)
        self.assertNotIn("config.h", model.files)
        
        # Check main.c filtering
        main_file = model.files["main.c"]
        self.assertIn("Person", main_file.structs)
        self.assertNotIn("Config", main_file.structs)  # Filtered out
        self.assertIn("main", [f.name for f in main_file.functions])
        self.assertNotIn("process_data", [f.name for f in main_file.functions])  # Filtered out
        self.assertNotIn("calculate", [f.name for f in main_file.functions])  # Filtered out
        
        # Generate diagrams
        self.generator.generate_with_config(model, config)
        
        # Check output
        output_dir = os.path.join(self.temp_dir, "filter_output")
        self.assertTrue(os.path.exists(output_dir))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "main.c.puml")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "utils.c.puml")))
        self.assertFalse(os.path.exists(os.path.join(output_dir, "config.h.puml")))
    
    def test_workflow_error_handling(self):
        """Test workflow error handling"""
        # Test with non-existent project
        with self.assertRaises(ValueError):
            self.analyzer.analyze_project("/non/existent/path")
        
        # Test with empty project
        empty_dir = os.path.join(self.temp_dir, "empty_project")
        os.makedirs(empty_dir, exist_ok=True)
        
        model = self.analyzer.analyze_project(empty_dir, recursive=True)
        self.assertEqual(len(model.files), 0)
        
        # Test with invalid configuration
        invalid_config_path = os.path.join(self.temp_dir, "invalid_config.json")
        with open(invalid_config_path, 'w') as f:
            f.write("invalid json")
        
        with self.assertRaises(ValueError):
            Config.load(invalid_config_path)
    
    def test_model_serialization(self):
        """Test model serialization and deserialization"""
        project_dir = self.create_test_project("serialization_test")
        
        # Create model
        model = self.analyzer.analyze_project(project_dir, recursive=True)
        
        # Save model
        model_path = os.path.join(self.temp_dir, "serialization_model.json")
        model.save(model_path)
        
        # Load model
        with open(model_path, 'r') as f:
            loaded_data = json.load(f)
        
        loaded_model = ProjectModel.from_dict(loaded_data)
        
        # Verify loaded model matches original
        self.assertEqual(loaded_model.project_name, model.project_name)
        self.assertEqual(loaded_model.project_root, model.project_root)
        self.assertEqual(len(loaded_model.files), len(model.files))
        
        # Check file content
        original_main = model.files["main.c"]
        loaded_main = loaded_model.files["main.c"]
        
        self.assertEqual(len(original_main.structs), len(loaded_main.structs))
        self.assertEqual(len(original_main.functions), len(loaded_main.functions))
        self.assertEqual(len(original_main.includes), len(loaded_main.includes))
        
        # Verify specific elements
        self.assertIn("Person", loaded_main.structs)
        self.assertIn("main", [f.name for f in loaded_main.functions])
        self.assertIn("stdio.h", loaded_main.includes)
    
    def test_workflow_performance(self):
        """Test workflow performance with larger project"""
        # Create a larger test project
        project_dir = os.path.join(self.temp_dir, "performance_test")
        os.makedirs(project_dir, exist_ok=True)
        
        # Create multiple files
        for i in range(10):
            file_content = f'''
#include <stdio.h>

struct TestStruct{i} {{
    int id;
    char name[50];
}};

enum TestEnum{i} {{
    VALUE1_{i},
    VALUE2_{i}
}};

int test_function_{i}() {{
    return {i};
}}

int global_var_{i} = {i};
'''
            
            with open(os.path.join(project_dir, f"file_{i}.c"), 'w') as f:
                f.write(file_content)
        
        # Test analysis performance
        model = self.analyzer.analyze_project(project_dir, recursive=True)
        
        # Should process all files
        self.assertEqual(len(model.files), 10)
        
        # Test generation performance
        output_dir = os.path.join(self.temp_dir, "performance_output")
        self.generator.generate_with_config(model, Config({
            "project_name": "performance_test",
            "project_roots": [project_dir],
            "output_dir": output_dir,
            "model_output_path": os.path.join(self.temp_dir, "performance_model.json"),
            "recursive": True
        }))
        
        # Should generate all diagrams
        self.assertTrue(os.path.exists(output_dir))
        for i in range(10):
            self.assertTrue(os.path.exists(os.path.join(output_dir, f"file_{i}.c.puml")))


if __name__ == '__main__':
    unittest.main()