import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.parser import CParser
from src.c2puml.models import ProjectModel
import tempfile

class TestAnonymousStructureHandling:
    def test_anonymous_struct_in_typedef(self):
        """Test that anonymous structs within typedefs are correctly processed"""
        test_code = """
        typedef struct {
            int count;
            struct {
                int item_id;
                char item_name[32];
                union {
                    int int_data;
                    float float_data;
                    struct {
                        int x, y;
                    } point_data;
                } item_value;
            } items[10];
        } array_of_anon_structs_t;
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            parser = CParser()
            project_model = ProjectModel(project_name="test_project", source_folder=os.path.dirname(temp_file))
            file_model = parser.parse_file(temp_file, os.path.basename(temp_file))
            project_model.files[file_model.name] = file_model
            
            # Check that the main typedef is parsed
            assert "array_of_anon_structs_t" in file_model.structs, "Main typedef should be parsed"
            
            # Check that anonymous structures are created
            # The AnonymousTypedefProcessor should create separate entities for anonymous structs
            print(f"Anonymous relationships: {file_model.anonymous_relationships}")
            
            # Check that the main struct has anonymous relationships
            main_struct = file_model.structs["array_of_anon_structs_t"]
            assert hasattr(main_struct, 'anonymous_relationships'), "Main struct should have anonymous relationships"
            
            print("✅ Anonymous struct in typedef test passed")
            
        finally:
            os.unlink(temp_file)

    def test_nested_anonymous_structures(self):
        """Test that deeply nested anonymous structures are correctly processed"""
        test_code = """
        typedef struct {
            struct {
                struct {
                    int level3_field;
                } level3_struct;
            } level2_struct;
        } nested_anonymous_t;
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            parser = CParser()
            project_model = ProjectModel(project_name="test_project", source_folder=os.path.dirname(temp_file))
            file_model = parser.parse_file(temp_file, os.path.basename(temp_file))
            project_model.files[file_model.name] = file_model
            
            # Check that the main typedef is parsed
            assert "nested_anonymous_t" in file_model.structs, "Main typedef should be parsed"
            
            # Check that anonymous relationships are created
            print(f"Anonymous relationships: {file_model.anonymous_relationships}")
            
            print("✅ Nested anonymous structures test passed")
            
        finally:
            os.unlink(temp_file)

    def test_anonymous_union_handling(self):
        """Test that anonymous unions are correctly processed"""
        test_code = """
        typedef struct {
            int type_id;
            union {
                int int_value;
                float float_value;
                char string_value[64];
                struct {
                    int x, y, z;
                } point_value;
            } data_union;
            int checksum;
        } struct_with_union_t;
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            parser = CParser()
            project_model = ProjectModel(project_name="test_project", source_folder=os.path.dirname(temp_file))
            file_model = parser.parse_file(temp_file, os.path.basename(temp_file))
            project_model.files[file_model.name] = file_model
            
            # Check that the main typedef is parsed
            assert "struct_with_union_t" in file_model.structs, "Main typedef should be parsed"
            
            # Check that anonymous relationships are created
            print(f"Anonymous relationships: {file_model.anonymous_relationships}")
            
            print("✅ Anonymous union handling test passed")
            
        finally:
            os.unlink(temp_file)

    def test_multiple_anonymous_structures(self):
        """Test that multiple anonymous structures in the same typedef are handled"""
        test_code = """
        typedef struct {
            struct {
                int first_field;
            } first_anon;
            
            struct {
                int second_field;
            } second_anon;
            
            union {
                int union_field1;
            } first_union;
        } multiple_anonymous_t;
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            parser = CParser()
            project_model = ProjectModel(project_name="test_project", source_folder=os.path.dirname(temp_file))
            file_model = parser.parse_file(temp_file, os.path.basename(temp_file))
            project_model.files[file_model.name] = file_model
            
            # Check that the main typedef is parsed
            assert "multiple_anonymous_t" in file_model.structs, "Main typedef should be parsed"
            
            # Check that anonymous relationships are created
            print(f"Anonymous relationships: {file_model.anonymous_relationships}")
            
            print("✅ Multiple anonymous structures test passed")
            
        finally:
            os.unlink(temp_file)

    def test_anonymous_structure_field_parsing(self):
        """Test that anonymous structure fields are correctly parsed"""
        test_code = """
        typedef struct {
            int count;
            struct {
                int item_id;
                char item_name[32];
            } items[10];
        } simple_anonymous_t;
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            parser = CParser()
            project_model = ProjectModel(project_name="test_project", source_folder=os.path.dirname(temp_file))
            file_model = parser.parse_file(temp_file, os.path.basename(temp_file))
            project_model.files[file_model.name] = file_model
            
            # Check that the main typedef is parsed
            assert "simple_anonymous_t" in file_model.structs, "Main typedef should be parsed"
            
            # Check the field parsing
            main_struct = file_model.structs["simple_anonymous_t"]
            print(f"Main struct fields: {[(f.name, f.type) for f in main_struct.fields]}")
            
            # The field should be parsed as "struct { ... } items[10]"
            field_names = [f.name for f in main_struct.fields]
            assert "items" in field_names, "Anonymous struct field should be parsed"
            
            # Check if the field type contains the simplified format
            items_field = next(f for f in main_struct.fields if f.name == "items")
            print(f"Items field type: '{items_field.type}'")
            assert "struct { ... }" in items_field.type, "Field should have simplified struct type"
            
            print("✅ Anonymous structure field parsing test passed")
            
        finally:
            os.unlink(temp_file)

if __name__ == "__main__":
    test = TestAnonymousStructureHandling()
    try:
        test.test_anonymous_structure_field_parsing()
        print("✅ Anonymous structure field parsing test passed")
    except Exception as e:
        print(f"❌ Anonymous structure field parsing test failed: {e}")
        import traceback
        traceback.print_exc()