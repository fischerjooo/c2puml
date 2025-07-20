"""
Feature tests for generator functionality

Tests advanced PlantUML generation features.
"""

import os
from tests.feature.base import BaseFeatureTest


class TestGeneratorFeatures(BaseFeatureTest):
    """Test advanced generator features"""

    def test_generate_with_typedefs(self):
        """Test PlantUML generation with typedef relationships"""
        from c_to_plantuml.generator import Generator
        from c_to_plantuml.parser import Parser

        content = """
#include <stdio.h>

typedef struct {
    int id;
    char name[100];
} User;

typedef User* UserPtr;

struct Container {
    UserPtr users;
    int count;
};
        """

        self.create_test_file("typedef_test.c", content)
        
        # Parse and generate
        parser = Parser()
        model = parser.c_parser.parse_project(self.temp_dir, recursive=True)
        
        model_path = os.path.join(self.temp_dir, "test_model.json")
        model.save(model_path)
        
        generator = Generator()
        output_dir = self.temp_dir + "/output"
        generator.generate(model_path, output_dir)
        
        # Verify generation
        from pathlib import Path
        puml_files = list(Path(output_dir).glob("*.puml"))
        self.assertGreaterEqual(len(puml_files), 1)

    def test_generate_with_unions(self):
        """Test PlantUML generation with union definitions"""
        from c_to_plantuml.generator import Generator
        from c_to_plantuml.parser import Parser

        content = """
union Data {
    int i;
    float f;
    char str[20];
};

struct Container {
    union Data data;
    int type;
};
        """

        self.create_test_file("union_test.c", content)
        
        # Parse and generate
        parser = Parser()
        model = parser.c_parser.parse_project(self.temp_dir, recursive=True)
        
        model_path = os.path.join(self.temp_dir, "test_model.json")
        model.save(model_path)
        
        generator = Generator()
        output_dir = self.temp_dir + "/output"
        generator.generate(model_path, output_dir)
        
        # Verify generation
        from pathlib import Path
        puml_files = list(Path(output_dir).glob("*.puml"))
        self.assertGreaterEqual(len(puml_files), 1)
