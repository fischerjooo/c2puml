"""Extended unit tests for the AnonymousTypedefProcessor class."""

import unittest
import sys
import os
from pathlib import Path

# Add the correct paths for imports
current_file = Path(__file__).resolve()
test_dir = current_file.parent
project_root = test_dir.parent.parent
src_path = project_root / "src"

if src_path.exists():
    sys.path.insert(0, str(src_path))

from c2puml.models import FileModel, Alias, Struct, Field, Union
from c2puml.core.parser_anonymous_processor import AnonymousTypedefProcessor


class TestAnonymousTypedefProcessorExtended(unittest.TestCase):
    """Extended tests for the AnonymousTypedefProcessor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.processor = AnonymousTypedefProcessor()

    def test_extract_anonymous_structs_from_text(self):
        """Test the regex extraction of anonymous structures from text."""
        text = '''int(* complex_callback_t)(
            int param1,
            struct {
                int nested1;
                char* nested2;
                void(*nested_func)(int);
            }* param4
        )'''
        
        result = self.processor._extract_anonymous_structs_from_text(text)
        
        self.assertEqual(len(result), 1)
        struct_content, struct_type = result[0]
        self.assertEqual(struct_type, "struct")
        self.assertIn("nested1", struct_content)
        self.assertIn("nested2", struct_content)
        self.assertIn("nested_func", struct_content)

    def test_extract_multiple_anonymous_from_text(self):
        """Test extraction of multiple anonymous structures from text."""
        text = '''typedef struct {
            struct {
                int first_field;
            } first_struct;
            union {
                int union_field;
                float union_float;
            } first_union;
            struct {
                char second_field[32];
            } second_struct;
        } multi_anon;'''
        
        result = self.processor._extract_anonymous_structs_from_text(text)
        
        # Should find 2 structs and 1 union
        struct_count = sum(1 for _, t in result if t == "struct")
        union_count = sum(1 for _, t in result if t == "union")
        
        self.assertEqual(struct_count, 2)
        self.assertEqual(union_count, 1)

    def test_generate_anonymous_name(self):
        """Test the anonymous name generation."""
        name1 = self.processor._generate_anonymous_name("parent_struct", "struct", 1)
        name2 = self.processor._generate_anonymous_name("parent_union", "union", 2)
        
        self.assertEqual(name1, "parent_struct_anonymous_struct_1")
        self.assertEqual(name2, "parent_union_anonymous_union_2")

    def test_parse_struct_fields_simple(self):
        """Test parsing simple struct fields."""
        content = "int field1; char field2[32]; float field3;"
        
        fields = self.processor._parse_struct_fields(content)
        
        self.assertEqual(len(fields), 3)
        field_names = [f.name for f in fields]
        self.assertIn("field1", field_names)
        self.assertIn("field2", field_names) 
        self.assertIn("field3", field_names)

    def test_parse_struct_fields_function_pointer(self):
        """Test parsing struct fields with function pointers."""
        content = "int normal_field; void (*callback)(int); char* string_field;"
        
        fields = self.processor._parse_struct_fields(content)
        
        self.assertEqual(len(fields), 3)
        field_names = [f.name for f in fields]
        self.assertIn("normal_field", field_names)
        self.assertIn("callback", field_names)
        self.assertIn("string_field", field_names)

    def test_parse_struct_fields_multiple_declarations(self):
        """Test parsing struct fields with multiple declarations per line."""
        content = "int a, b, c; char x, y; float single;"
        
        fields = self.processor._parse_struct_fields(content)
        
        # Should handle comma-separated declarations
        field_names = [f.name for f in fields]
        self.assertIn("a", field_names)
        self.assertIn("b", field_names)
        self.assertIn("c", field_names)
        self.assertIn("x", field_names)
        self.assertIn("y", field_names)
        self.assertIn("single", field_names)

    def test_parse_struct_fields_mixed_declarations(self):
        """Test parsing mixed single and multiple field declarations."""
        content = "int solo; char *ptr1, *ptr2; unsigned long count1, count2, count3; float value;"
        
        fields = self.processor._parse_struct_fields(content)
        
        field_names = [f.name for f in fields]
        field_types = {f.name: f.type for f in fields}
        
        # Check all names are present
        self.assertIn("solo", field_names)
        self.assertIn("ptr1", field_names) 
        self.assertIn("ptr2", field_names)
        self.assertIn("count1", field_names)
        self.assertIn("count2", field_names)
        self.assertIn("count3", field_names)
        self.assertIn("value", field_names)
        
        # Check types are correctly assigned
        self.assertEqual(field_types["solo"], "int")
        self.assertEqual(field_types["ptr1"], "char *")
        self.assertEqual(field_types["ptr2"], "char *")
        self.assertEqual(field_types["count1"], "unsigned long")
        self.assertEqual(field_types["count2"], "unsigned long")
        self.assertEqual(field_types["count3"], "unsigned long")
        self.assertEqual(field_types["value"], "float")

    def test_parse_struct_fields_complex_comma_declarations(self):
        """Test parsing complex comma-separated declarations with arrays and pointers."""
        content = "struct point *p1, *p2; int arr1[10], arr2[20], simple; void *data1, *data2;"
        
        fields = self.processor._parse_struct_fields(content)
        
        field_names = [f.name for f in fields]
        field_types = {f.name: f.type for f in fields}
        
        # Check pointer fields
        self.assertIn("p1", field_names)
        self.assertIn("p2", field_names)
        self.assertEqual(field_types["p1"], "struct point *")
        self.assertEqual(field_types["p2"], "struct point *")
        
        # Check array fields  
        self.assertIn("arr1", field_names)
        self.assertIn("arr2", field_names)
        self.assertEqual(field_types["arr1"], "int[10]")
        self.assertEqual(field_types["arr2"], "int[20]")
        
        # Check simple field
        self.assertIn("simple", field_names)
        self.assertEqual(field_types["simple"], "int")
        
        # Check void pointers
        self.assertIn("data1", field_names)
        self.assertIn("data2", field_names)
        self.assertEqual(field_types["data1"], "void *")
        self.assertEqual(field_types["data2"], "void *")

    def test_replace_anonymous_struct_with_reference(self):
        """Test replacing anonymous struct definitions with references."""
        original_type = '''int(*callback)(
            struct {
                int config_id;
                char config_name[64];
            }* config
        )'''
        
        struct_content = "int config_id;\n                char config_name[64];"
        anon_name = "callback_anonymous_struct_1"
        struct_type = "struct"
        
        result = self.processor._replace_anonymous_struct_with_reference(
            original_type, struct_content, anon_name, struct_type
        )
        
        self.assertNotIn("struct {", result)
        self.assertIn(anon_name, result)

    def test_field_contains_anonymous_struct(self):
        """Test detection of anonymous structures in field definitions."""
        field_with_anon = Field(name="field1", type="struct { int x; } nested")
        field_without_anon = Field(name="field2", type="int normal_field")
        field_with_union = Field(name="field3", type="union { int x; float y; } data")
        
        self.assertTrue(self.processor._field_contains_anonymous_struct(field_with_anon))
        self.assertFalse(self.processor._field_contains_anonymous_struct(field_without_anon))
        self.assertTrue(self.processor._field_contains_anonymous_struct(field_with_union))

    def test_process_alias_for_anonymous_structs(self):
        """Test processing an alias for anonymous structures."""
        file_model = FileModel(file_path="test.h")
        
        # Create a function pointer alias with anonymous struct
        alias_data = Alias(
            name="test_callback_t",
            original_type='''void(*test_callback_t)(
                struct {
                    int event_id;
                    char event_name[32];
                }* event_info
            )'''
        )
        
        file_model.aliases["test_callback_t"] = alias_data
        
        # Process the alias
        self.processor._process_alias_for_anonymous_structs(
            file_model, "test_callback_t", alias_data
        )
        
        # Check that anonymous struct was extracted
        self.assertIn("test_callback_t_anonymous_struct_1", file_model.structs)
        self.assertIn("test_callback_t", file_model.anonymous_relationships)
        self.assertIn("test_callback_t_anonymous_struct_1", 
                     file_model.anonymous_relationships["test_callback_t"])

    def test_process_struct_for_anonymous_structs(self):
        """Test processing a struct for anonymous nested structures."""
        file_model = FileModel(file_path="test.h")
        
        # Create a struct with anonymous nested structures
        struct_data = Struct(
            name="parent_struct",
            fields=[
                Field(name="id", type="int"),
                Field(name="nested", type="struct { int x; int y; } nested_data"),
                Field(name="name", type="char[32]")
            ]
        )
        
        file_model.structs["parent_struct"] = struct_data
        
        # Process the struct
        self.processor._process_struct_for_anonymous_structs(
            file_model, "parent_struct", struct_data
        )
        
        # Check that anonymous struct was extracted with improved naming
        self.assertIn("parent_struct_nested_data", file_model.structs)
        self.assertIn("parent_struct", file_model.anonymous_relationships)

    def test_process_union_for_anonymous_structs(self):
        """Test processing a union for anonymous nested structures."""
        file_model = FileModel(file_path="test.h")
        
        # Create a union with anonymous nested structures
        union_data = Union(
            name="parent_union",
            fields=[
                Field(name="int_value", type="int"),
                Field(name="struct_value", type="struct { int x; int y; } struct_data"),
                Field(name="float_value", type="float")
            ]
        )
        
        file_model.unions["parent_union"] = union_data
        
        # Process the union
        self.processor._process_union_for_anonymous_structs(
            file_model, "parent_union", union_data
        )
        
        # Check that anonymous struct was extracted with improved naming
        self.assertIn("parent_union_struct_data", file_model.structs)
        self.assertIn("parent_union", file_model.anonymous_relationships)

    def test_process_file_model_comprehensive(self):
        """Test processing a complete file model with various anonymous structures."""
        file_model = FileModel(file_path="test.h")
        
        # Add alias with anonymous struct
        file_model.aliases["callback_t"] = Alias(
            name="callback_t",
            original_type="void(*callback_t)(struct { int id; }* param)"
        )
        
        # Add struct with anonymous union
        file_model.structs["main_struct"] = Struct(
            name="main_struct",
            fields=[
                Field(name="data", type="union { int i; float f; } data_union")
            ]
        )
        
        # Add union with anonymous struct
        file_model.unions["main_union"] = Union(
            name="main_union",
            fields=[
                Field(name="complex", type="struct { int x; int y; } point_data")
            ]
        )
        
        # Process the entire file model
        self.processor.process_file_model(file_model)
        
        # Verify all anonymous structures were extracted with improved naming
        expected_anon_structs = [
            "callback_t_anonymous_struct_1",  # Complex type, uses counter
            "main_union_point_data"           # Uses field name
        ]
        expected_anon_unions = [
            "main_struct_data_union"          # Uses field name
        ]
        
        for anon_struct in expected_anon_structs:
            self.assertIn(anon_struct, file_model.structs)
            
        for anon_union in expected_anon_unions:
            self.assertIn(anon_union, file_model.unions)
        
        # Verify relationships were tracked
        self.assertIn("callback_t", file_model.anonymous_relationships)
        self.assertIn("main_struct", file_model.anonymous_relationships)
        self.assertIn("main_union", file_model.anonymous_relationships)


if __name__ == "__main__":
    unittest.main()