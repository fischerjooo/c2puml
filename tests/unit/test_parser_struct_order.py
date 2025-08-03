"""
Unit tests for struct field order preservation.

This test file addresses Issue 1.1 from TODO.md:
"Struct Field Order and Structure Issues - Incorrect Field Order in triangle_t"
"""

import unittest
from pathlib import Path
import tempfile
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.parser import CParser
from src.c2puml.core.generator import Generator
from src.c2puml.models import ProjectModel, FileModel, Struct, Field


class TestStructFieldOrderPreservation(unittest.TestCase):
    """Test that struct fields maintain their original order."""

    def setUp(self):
        self.parser = CParser()
        self.generator = Generator()

    def test_struct_field_order_preservation(self):
        """Test that struct fields maintain their original order."""
        source_code = """
        typedef struct triangle_tag {
            point_t vertices[3];
            char label[MAX_LABEL_LEN];
        } triangle_t;
        """
        
        # Create a temporary file with the test code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False) as f:
            f.write(source_code)
            temp_file = f.name
        
        try:
            # Parse the file
            file_model = self.parser.parse_file(Path(temp_file), "test.h")
            
            # Check that the struct was parsed
            print(f"Available structs: {list(file_model.structs.keys())}")
            self.assertIn("triangle_t", file_model.structs)
            struct = file_model.structs["triangle_t"]
            
            print(f"Struct fields: {[(f.name, f.type) for f in struct.fields]}")
            
            # Verify field order is preserved
            self.assertEqual(len(struct.fields), 2, "Should have exactly 2 fields")
            self.assertEqual(struct.fields[0].name, "vertices", "First field should be 'vertices'")
            self.assertEqual(struct.fields[1].name, "label", "Second field should be 'label'")
            
        finally:
            # Clean up
            Path(temp_file).unlink()

    def test_struct_field_order_in_generated_puml(self):
        """Test that generated PlantUML preserves field order."""
        source_code = """
        typedef struct triangle_tag {
            point_t vertices[3];
            char label[MAX_LABEL_LEN];
        } triangle_t;
        """
        
        # Create a temporary file with the test code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(source_code)
            temp_file = f.name
        
        try:
            # Parse the file
            file_model = self.parser.parse_file(Path(temp_file), "test.h")
            
            # Create a project model
            project_model = ProjectModel(
                project_name="test_project",
                source_folder="/tmp",
                files={file_model.name: file_model}
            )
            
            # Generate PlantUML
            puml_content = self.generator.generate_diagram(file_model, project_model)
            
            # Debug: Print the generated content
            print("Generated PlantUML content:")
            print(puml_content)
            
            # Debug: Check what's in the include tree
            print(f"Project model files: {list(project_model.files.keys())}")
            include_tree = self.generator._build_include_tree(file_model, project_model, 1)
            print(f"Include tree keys: {list(include_tree.keys())}")
            print(f"File model name: {file_model.name}")
            print(f"File model structs: {list(file_model.structs.keys())}")
            
            # Check that the field order is preserved in the generated PlantUML
            # The first field should appear before the second field in the output
            vertices_index = puml_content.find("+ point_t[3] vertices")
            label_index = puml_content.find("+ char[MAX_LABEL_LEN] label")
            
            print(f"vertices_index: {vertices_index}")
            print(f"label_index: {label_index}")
            
            self.assertNotEqual(vertices_index, -1, "vertices field should be found in PlantUML")
            self.assertNotEqual(label_index, -1, "label field should be found in PlantUML")
            self.assertLess(vertices_index, label_index, "vertices field should appear before label field in PlantUML")
            
        finally:
            # Clean up
            Path(temp_file).unlink()

    def test_complex_struct_field_order(self):
        """Test field order preservation in complex structs."""
        source_code = """
        typedef struct complex_struct {
            int id;
            char name[32];
            float value;
            struct {
                int x;
                int y;
            } position;
            union {
                int int_data;
                float float_data;
            } data;
        } complex_struct_t;
        """
        
        # Create a temporary file with the test code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False) as f:
            f.write(source_code)
            temp_file = f.name
        
        try:
            # Parse the file
            file_model = self.parser.parse_file(Path(temp_file), "test.h")
            
            # Check that the struct was parsed
            self.assertIn("complex_struct_t", file_model.structs)
            struct = file_model.structs["complex_struct_t"]
            
            # Verify field order is preserved
            expected_fields = ["id", "name", "value", "position", "data"]
            actual_fields = [field.name for field in struct.fields]
            
            self.assertEqual(actual_fields, expected_fields, 
                           f"Field order should be preserved. Expected: {expected_fields}, Got: {actual_fields}")
            
        finally:
            # Clean up
            Path(temp_file).unlink()


if __name__ == '__main__':
    unittest.main()