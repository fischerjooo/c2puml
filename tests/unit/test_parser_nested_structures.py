"""
Unit tests for nested structure preservation.

This test file addresses Issue 1.2 from TODO.md:
"Struct Field Order and Structure Issues - Nested Union/Struct Flattening"
"""

import unittest
from pathlib import Path
import tempfile
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.parser import CParser
from src.c2puml.core.generator import Generator
from src.c2puml.models import ProjectModel, FileModel, Struct, Field


class TestNestedStructurePreservation(unittest.TestCase):
    """Test that nested structures maintain their hierarchy."""

    def setUp(self):
        self.parser = CParser()
        self.generator = Generator()

    def test_nested_union_preservation(self):
        """Test that nested unions maintain their structure."""
        source_code = """
        typedef union {
            int primary_int;
            union {
                float nested_float;
                double nested_double;
                union {
                    char deep_char;
                    short deep_short;
                } deep_union;
            } nested_union;
            char primary_bytes[32];
        } union_with_union_t;
        """
        
        # Create a temporary file with the test code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(source_code)
            temp_file = f.name
        
        try:
            # Parse the file
            file_model = self.parser.parse_file(Path(temp_file), "test.c")
            
            # Check that the union was parsed
            print(f"Available unions: {list(file_model.unions.keys())}")
            self.assertIn("union_with_union_t", file_model.unions)
            union = file_model.unions["union_with_union_t"]
            
            print(f"Union fields: {[(f.name, f.type) for f in union.fields]}")
            
            # Verify that nested structures are preserved (not flattened)
            # The union should have 4 top-level fields, not flattened nested fields
            expected_fields = ["primary_int", "nested_union", "primary_bytes"]
            actual_fields = [field.name for field in union.fields]
            
            # Check that we have the expected number of top-level fields
            self.assertEqual(len(actual_fields), 3, 
                           f"Should have 3 top-level fields, got {len(actual_fields)}: {actual_fields}")
            
            # Check that nested_union is preserved as a field
            self.assertIn("nested_union", actual_fields, 
                         "nested_union should be preserved as a field")
            
        finally:
            # Clean up
            Path(temp_file).unlink()

    def test_nested_struct_preservation(self):
        """Test that nested structs maintain their structure."""
        source_code = """
        typedef struct {
            int outer_id;
            char outer_name[32];
            struct {
                int inner_x;
                int inner_y;
                char inner_label[16];
            } inner_struct;
            int outer_flags;
        } struct_with_struct_t;
        """
        
        # Create a temporary file with the test code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(source_code)
            temp_file = f.name
        
        try:
            # Parse the file
            file_model = self.parser.parse_file(Path(temp_file), "test.c")
            
            # Check that the struct was parsed
            print(f"Available structs: {list(file_model.structs.keys())}")
            self.assertIn("struct_with_struct_t", file_model.structs)
            struct = file_model.structs["struct_with_struct_t"]
            
            print(f"Struct fields: {[(f.name, f.type) for f in struct.fields]}")
            
            # Verify that nested structures are preserved
            expected_fields = ["outer_id", "outer_name", "inner_struct", "outer_flags"]
            actual_fields = [field.name for field in struct.fields]
            
            # Check that we have the expected number of top-level fields
            self.assertEqual(len(actual_fields), 4, 
                           f"Should have 4 top-level fields, got {len(actual_fields)}: {actual_fields}")
            
            # Check that inner_struct is preserved as a field
            self.assertIn("inner_struct", actual_fields, 
                         "inner_struct should be preserved as a field")
            
        finally:
            # Clean up
            Path(temp_file).unlink()

    def test_nested_structures_in_generated_puml(self):
        """Test that generated PlantUML preserves nested structure hierarchy."""
        source_code = """
        typedef union {
            int primary_int;
            union {
                float nested_float;
                double nested_double;
            } nested_union;
            char primary_bytes[32];
        } test_union_t;
        """
        
        # Create a temporary file with the test code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(source_code)
            temp_file = f.name
        
        try:
            # Parse the file
            file_model = self.parser.parse_file(Path(temp_file), "test.c")
            
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
            
            # Check that the nested structure is preserved in the generated PlantUML
            # The union should show nested_union as a field, not flattened fields
            nested_union_index = puml_content.find("+ union { ... } nested_union")
            primary_int_index = puml_content.find("+ int primary_int")
            primary_bytes_index = puml_content.find("+ char[32] primary_bytes")
            
            # All fields should be found
            self.assertNotEqual(nested_union_index, -1, "nested_union field should be found in PlantUML")
            self.assertNotEqual(primary_int_index, -1, "primary_int field should be found in PlantUML")
            self.assertNotEqual(primary_bytes_index, -1, "primary_bytes field should be found in PlantUML")
            
            # Check that we have exactly 3 fields (not flattened)
            field_count = puml_content.count("+ int primary_int") + puml_content.count("+ union { ... } nested_union") + puml_content.count("+ char[32] primary_bytes")
            self.assertEqual(field_count, 3, f"Should have exactly 3 fields, found {field_count}")
            
        finally:
            # Clean up
            Path(temp_file).unlink()


if __name__ == '__main__':
    unittest.main()