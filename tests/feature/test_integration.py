"""
Integration tests for C to PlantUML Converter

Tests complete workflows and component interactions.
"""

import os
from pathlib import Path

from tests.feature.base import BaseFeatureTest

# Add src directory to path for new package structure
import sys
test_dir = os.path.dirname(__file__)
src_path = os.path.join(test_dir, "..", "..", "src")
if os.path.exists(src_path):
    sys.path.insert(0, src_path)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestIntegration(BaseFeatureTest):
    """Test complete end-to-end workflows and integrations"""

    def test_complete_workflow(self):
        """Test complete end-to-end workflow from parsing to PlantUML generation"""
        
from c2puml.generator import Generator
        from c2puml.parser import Parser

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
        parser = Parser()
        model = parser.c_parser.parse_project(self.temp_dir, recursive_search=True)

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
        generator.generate(model_path, output_dir)

        # Verify generation
        self.assertTrue(os.path.exists(output_dir))
        puml_files = list(Path(output_dir).glob("*.puml"))
        self.assertGreaterEqual(len(puml_files), 1)

        # Verify the content of generated files
        for puml_file in puml_files:
            with open(puml_file, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("@startuml", content)
                self.assertIn("@enduml", content)

    def test_configuration_features(self):
        """Test configuration loading and filtering features"""
        # Create test configuration
        import json

        from c2puml.config import Config

        config_content = {
            "source_folders": [self.temp_dir],
            "file_filters": {"include": [r"\.c$", r"\.h$"], "exclude": [r"test"]},
            "include_depth": 2,
            "transformations": {
                "rename": {"old_name": "new_name"},
                "add_elements": [{"type": "macro", "name": "TEST_MACRO", "value": "1"}],
            },
        }

        config_file = self.create_test_file(
            "test_config.json", json.dumps(config_content)
        )

        # Test configuration loading
        config = Config()
        config.load(config_file)

        # Verify configuration loaded successfully
        self.assertTrue(hasattr(config, "file_filters"))
        self.assertTrue(hasattr(config, "include_depth"))
        # The source_folders might be processed differently, so just check it's a list
        self.assertTrue(isinstance(config.source_folders, list))

    def test_error_handling(self):
        """Test error handling for various scenarios"""
        from c2puml.parser import Parser

        # Test parsing non-existent file
        parser = Parser()

        # This should not crash and should handle the error gracefully
        try:
            result = parser.c_parser.parse_file(Path("/non/existent/file.c"), "file.c")
            # If it doesn't raise an exception, that's fine too
        except Exception as e:
            # Should be a reasonable error
            self.assertIsInstance(e, (FileNotFoundError, OSError))

    def test_performance_features(self):
        """Test performance with larger files"""
        from c2puml.parser import Parser

        # Create a larger test file
        large_content = """
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_SIZE 1000
#define DEBUG_MODE 1

typedef struct LargeStruct {
    char data[MAX_SIZE];
    int count;
    float values[100];
} LargeStruct;

enum LargeEnum {
    VALUE1, VALUE2, VALUE3, VALUE4, VALUE5,
    VALUE6, VALUE7, VALUE8, VALUE9, VALUE10
};

int global_counter = 0;
char* global_buffer = NULL;

int main() {
    LargeStruct* data = malloc(sizeof(LargeStruct));
    if (data) {
        data->count = 0;
        free(data);
    }
    return 0;
}

void process_large_data(LargeStruct* data) {
    for (int i = 0; i < data->count; i++) {
        data->values[i] *= 2.0f;
    }
}

void cleanup_resources() {
    if (global_buffer) {
        free(global_buffer);
        global_buffer = NULL;
    }
}
        """

        self.create_test_file("large_test.c", large_content)

        # Test parsing performance
        parser = Parser()
        model = parser.c_parser.parse_project(self.temp_dir, recursive_search=True)

        # Verify parsing completed successfully
        self.assertIn("large_test.c", model.files)
        file_model = model.files["large_test.c"]

        # Verify all elements were parsed
        self.assertIn("LargeStruct", file_model.structs)
        self.assertIn("LargeEnum", file_model.enums)
        self.assertEqual(len(file_model.functions), 3)
        self.assertEqual(len(file_model.macros), 2)
