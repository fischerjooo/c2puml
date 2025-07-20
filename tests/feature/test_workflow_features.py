"""
Feature tests for complete workflow functionality

Tests the end-to-end workflow from parsing to PlantUML generation.
"""

import os
from pathlib import Path

from .base import BaseFeatureTest


class TestWorkflowFeatures(BaseFeatureTest):
    """Test complete end-to-end workflow"""

    def test_feature_complete_workflow(self):
        """Test complete end-to-end workflow"""
        from c_to_plantuml.parser import Parser
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
        parser = Parser()
        model = parser.c_parser.parse_project(self.temp_dir, recursive=True)

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
        # Check that at least one PlantUML file was generated
        self.assertGreaterEqual(
            len(puml_files),
            1,
            f"Expected at least 1 PlantUML file, got {len(puml_files)}",
        )

        # Verify the content of generated files
        for puml_file in puml_files:
            with open(puml_file, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("@startuml", content)
                self.assertIn("@enduml", content)