"""
Test malformed anonymous structure handling.

This test verifies that the anonymous processor correctly handles malformed
anonymous structure field types like "struct { ... } field_name" where the
field name is incorrectly embedded in the type.
"""

import unittest
from c2puml.core.parser_anonymous_processor import AnonymousTypedefProcessor
from c2puml.models import FileModel, Struct, Field


class TestMalformedAnonymousStructures(unittest.TestCase):
    """Test handling of malformed anonymous structure field types."""

    def test_malformed_struct_field_type_handling(self):
        """Test that malformed struct field types are correctly processed."""
        # Create a file model with a struct containing malformed anonymous structure
        file_model = FileModel("test.c")
        
        # Create a struct with a malformed anonymous structure field
        # Field type: "struct { ... } nested_a2" (malformed)
        # Field name: "nested_a2" (should be "nested_struct_a2")
        test_struct = Struct("test_struct", [
            Field("nested_a2", "struct { ... } nested_a2")
        ])
        
        file_model.structs["test_struct"] = test_struct
        
        # Process the file model
        processor = AnonymousTypedefProcessor()
        processor.process_file_model(file_model)
        
        # Verify that the malformed field type was corrected
        self.assertIn("test_struct_nested_a2", file_model.structs)
        
        # Verify that the field type was updated to reference the extracted structure
        field = test_struct.fields[0]
        self.assertEqual(field.type, "test_struct_nested_a2")
        
        # Verify that the anonymous relationship was created
        self.assertIn("test_struct", file_model.anonymous_relationships)
        self.assertIn("test_struct_nested_a2", file_model.anonymous_relationships["test_struct"])

    def test_malformed_union_field_type_handling(self):
        """Test that malformed union field types are correctly processed."""
        # Create a file model with a struct containing malformed anonymous union
        file_model = FileModel("test.c")
        
        # Create a struct with a malformed anonymous union field
        # Field type: "union { ... } data_union" (malformed)
        # Field name: "data_union" (should be "data_union")
        test_struct = Struct("test_struct", [
            Field("data_union", "union { ... } data_union")
        ])
        
        file_model.structs["test_struct"] = test_struct
        
        # Process the file model
        processor = AnonymousTypedefProcessor()
        processor.process_file_model(file_model)
        
        # Verify that the malformed field type was corrected
        self.assertIn("test_struct_data_union", file_model.unions)
        
        # Verify that the field type was updated to reference the extracted structure
        field = test_struct.fields[0]
        self.assertEqual(field.type, "test_struct_data_union")
        
        # Verify that the anonymous relationship was created
        self.assertIn("test_struct", file_model.anonymous_relationships)
        self.assertIn("test_struct_data_union", file_model.anonymous_relationships["test_struct"])

    def test_multiple_malformed_fields_handling(self):
        """Test that multiple malformed fields are correctly processed."""
        # Create a file model with multiple malformed anonymous structure fields
        file_model = FileModel("test.c")
        
        # Create a struct with multiple malformed anonymous structure fields
        test_struct = Struct("test_struct", [
            Field("nested_a2", "struct { ... } nested_a2"),
            Field("level3_field", "struct { ... } level3_field"),
            Field("data_union", "union { ... } data_union")
        ])
        
        file_model.structs["test_struct"] = test_struct
        
        # Process the file model
        processor = AnonymousTypedefProcessor()
        processor.process_file_model(file_model)
        
        # Verify that all malformed field types were corrected
        self.assertIn("test_struct_nested_a2", file_model.structs)
        self.assertIn("test_struct_level3_field", file_model.structs)
        self.assertIn("test_struct_data_union", file_model.unions)
        
        # Verify that all field types were updated
        fields = test_struct.fields
        self.assertEqual(fields[0].type, "test_struct_nested_a2")
        self.assertEqual(fields[1].type, "test_struct_level3_field")
        self.assertEqual(fields[2].type, "test_struct_data_union")
        
        # Verify that all anonymous relationships were created
        self.assertIn("test_struct", file_model.anonymous_relationships)
        relationships = file_model.anonymous_relationships["test_struct"]
        self.assertIn("test_struct_nested_a2", relationships)
        self.assertIn("test_struct_level3_field", relationships)
        self.assertIn("test_struct_data_union", relationships)

    def test_malformed_field_with_existing_structure(self):
        """Test that malformed fields don't create duplicate structures."""
        # Create a file model with a malformed field that references an existing structure
        file_model = FileModel("test.c")
        
        # Create the target structure first
        existing_struct = Struct("test_struct_nested_a2", [])
        file_model.structs["test_struct_nested_a2"] = existing_struct
        
        # Create a struct with a malformed field that should reference the existing structure
        test_struct = Struct("test_struct", [
            Field("nested_a2", "struct { ... } nested_a2")
        ])
        
        file_model.structs["test_struct"] = test_struct
        
        # Process the file model
        processor = AnonymousTypedefProcessor()
        processor.process_file_model(file_model)
        
        # Verify that the existing structure was reused (not duplicated)
        self.assertEqual(len([s for s in file_model.structs.keys() if "nested_a2" in s]), 1)
        
        # Verify that the field type was updated to reference the existing structure
        field = test_struct.fields[0]
        self.assertEqual(field.type, "test_struct_nested_a2")
        
        # Verify that the anonymous relationship was created
        self.assertIn("test_struct", file_model.anonymous_relationships)
        self.assertIn("test_struct_nested_a2", file_model.anonymous_relationships["test_struct"])

    def test_malformed_field_pattern_matching(self):
        """Test that the malformed field pattern matching works correctly."""
        processor = AnonymousTypedefProcessor()
        
        # Test valid malformed patterns
        self.assertTrue(processor._field_contains_anonymous_struct(
            Field("test", "struct { ... } field_name")
        ))
        self.assertTrue(processor._field_contains_anonymous_struct(
            Field("test", "union { ... } field_name")
        ))
        
        # Test patterns that should match (they contain struct/union {)
        self.assertTrue(processor._field_contains_anonymous_struct(
            Field("test", "struct { ... }")
        ))
        self.assertTrue(processor._field_contains_anonymous_struct(
            Field("test", "union { ... }")
        ))
        
        # Test patterns that should also match (they contain struct/union {)
        self.assertTrue(processor._field_contains_anonymous_struct(
            Field("test", "struct { int x; } field_name")
        ))
        self.assertTrue(processor._field_contains_anonymous_struct(
            Field("test", "union { int x; } field_name")
        ))
        
        # Test invalid patterns (should not match)
        self.assertFalse(processor._field_contains_anonymous_struct(
            Field("test", "int field_name")
        ))
        self.assertFalse(processor._field_contains_anonymous_struct(
            Field("test", "char * field_name")
        ))

    def test_malformed_field_processing_integration(self):
        """Test integration of malformed field processing with the full pipeline."""
        # Create a file model that simulates the complex case from the todo
        file_model = FileModel("complex.h")
        
        # Create a struct similar to complex_naming_test_t_first_struct
        test_struct = Struct("complex_naming_test_t_first_struct", [
            Field("nested_a1", "int"),
            Field("deep_struct_a1", "complex_naming_test_t_first_struct_deep_struct_a1"),
            Field("deep_struct_a2", "complex_naming_test_t_first_struct_deep_struct_a2"),
            Field("nested_a2", "struct { ... } nested_a2")  # Malformed field
        ])
        
        file_model.structs["complex_naming_test_t_first_struct"] = test_struct
        
        # Process the file model
        processor = AnonymousTypedefProcessor()
        processor.process_file_model(file_model)
        
        # Verify that the malformed field was processed correctly
        self.assertIn("complex_naming_test_t_first_struct_nested_a2", file_model.structs)
        
        # Verify that the field type was updated
        field = test_struct.fields[3]  # nested_a2 field
        self.assertEqual(field.type, "complex_naming_test_t_first_struct_nested_a2")
        
        # Verify that the anonymous relationship was created
        self.assertIn("complex_naming_test_t_first_struct", file_model.anonymous_relationships)
        relationships = file_model.anonymous_relationships["complex_naming_test_t_first_struct"]
        self.assertIn("complex_naming_test_t_first_struct_nested_a2", relationships)


if __name__ == '__main__':
    unittest.main()