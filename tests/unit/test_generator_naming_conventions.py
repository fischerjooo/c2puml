import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.generator import Generator
from src.c2puml.models import ProjectModel, FileModel, Struct, Enum, Union, Alias
import tempfile

class TestGeneratorNamingConventions:
    def test_typedef_naming_conventions(self):
        """Test that typedef UML IDs follow the correct naming conventions"""
        # Create a test project model
        project_model = ProjectModel(project_name="test_project", source_folder="/tmp")
        
        # Create a test file model
        file_model = FileModel(name="test.c", file_path="/tmp/test.c")
        
        # Add various typedefs
        file_model.structs["MyBuffer"] = Struct(name="MyBuffer", fields=[])
        file_model.enums["Color"] = Enum(name="Color", values=[])
        file_model.unions["Value"] = Union(name="Value", fields=[])
        file_model.aliases["Integer"] = Alias(name="Integer", original_type="int")
        
        project_model.files["test.c"] = file_model
        
        # Create generator and generate UML IDs
        generator = Generator()
        uml_ids = generator._generate_uml_ids({"test.c": file_model}, project_model)
        
        # Test typedef naming conventions
        assert uml_ids["typedef_MyBuffer"] == "TYPEDEF_MYBUFFER", f"Expected TYPEDEF_MYBUFFER, got {uml_ids['typedef_MyBuffer']}"
        assert uml_ids["typedef_Color"] == "TYPEDEF_COLOR", f"Expected TYPEDEF_COLOR, got {uml_ids['typedef_Color']}"
        assert uml_ids["typedef_Value"] == "TYPEDEF_VALUE", f"Expected TYPEDEF_VALUE, got {uml_ids['typedef_Value']}"
        assert uml_ids["typedef_Integer"] == "TYPEDEF_INTEGER", f"Expected TYPEDEF_INTEGER, got {uml_ids['typedef_Integer']}"
        
        print("✅ Typedef naming conventions test passed")

    def test_file_naming_conventions(self):
        """Test that file UML IDs follow the correct naming conventions"""
        # Create a test project model
        project_model = ProjectModel(project_name="test_project", source_folder="/tmp")
        
        # Create test file models
        c_file_model = FileModel(name="main.c", file_path="/tmp/main.c")
        h_file_model = FileModel(name="utils.h", file_path="/tmp/utils.h")
        
        project_model.files["main.c"] = c_file_model
        project_model.files["utils.h"] = h_file_model
        
        # Create generator and generate UML IDs
        generator = Generator()
        uml_ids = generator._generate_uml_ids({"main.c": c_file_model, "utils.h": h_file_model}, project_model)
        
        # Test file naming conventions
        assert uml_ids["main.c"] == "MAIN", f"Expected MAIN, got {uml_ids['main.c']}"
        assert uml_ids["utils.h"] == "HEADER_UTILS", f"Expected HEADER_UTILS, got {uml_ids['utils.h']}"
        
        print("✅ File naming conventions test passed")

    def test_complex_typedef_names(self):
        """Test that complex typedef names are handled correctly"""
        # Create a test project model
        project_model = ProjectModel(project_name="test_project", source_folder="/tmp")
        
        # Create a test file model
        file_model = FileModel(name="test.c", file_path="/tmp/test.c")
        
        # Add typedefs with various naming patterns
        file_model.structs["complex_naming_test_t"] = Struct(name="complex_naming_test_t", fields=[])
        file_model.enums["LOG_LEVEL_T"] = Enum(name="LOG_LEVEL_T", values=[])
        file_model.unions["callback_function_t"] = Union(name="callback_function_t", fields=[])
        file_model.aliases["pointer_to_int"] = Alias(name="pointer_to_int", original_type="int*")
        
        project_model.files["test.c"] = file_model
        
        # Create generator and generate UML IDs
        generator = Generator()
        uml_ids = generator._generate_uml_ids({"test.c": file_model}, project_model)
        
        # Test complex typedef naming
        assert uml_ids["typedef_complex_naming_test_t"] == "TYPEDEF_COMPLEX_NAMING_TEST_T"
        assert uml_ids["typedef_LOG_LEVEL_T"] == "TYPEDEF_LOG_LEVEL_T"
        assert uml_ids["typedef_callback_function_t"] == "TYPEDEF_CALLBACK_FUNCTION_T"
        assert uml_ids["typedef_pointer_to_int"] == "TYPEDEF_POINTER_TO_INT"
        
        print("✅ Complex typedef naming test passed")

    def test_edge_case_names(self):
        """Test edge cases in naming conventions"""
        # Create a test project model
        project_model = ProjectModel(project_name="test_project", source_folder="/tmp")
        
        # Create a test file model
        file_model = FileModel(name="test.c", file_path="/tmp/test.c")
        
        # Add typedefs with edge case names
        file_model.structs["a"] = Struct(name="a", fields=[])
        file_model.enums["_private"] = Enum(name="_private", values=[])
        file_model.unions["123invalid"] = Union(name="123invalid", fields=[])
        file_model.aliases["UPPERCASE"] = Alias(name="UPPERCASE", original_type="int")
        
        project_model.files["test.c"] = file_model
        
        # Create generator and generate UML IDs
        generator = Generator()
        uml_ids = generator._generate_uml_ids({"test.c": file_model}, project_model)
        
        # Test edge case naming
        assert uml_ids["typedef_a"] == "TYPEDEF_A"
        assert uml_ids["typedef__private"] == "TYPEDEF__PRIVATE"
        assert uml_ids["typedef_123invalid"] == "TYPEDEF_123INVALID"
        assert uml_ids["typedef_UPPERCASE"] == "TYPEDEF_UPPERCASE"
        
        print("✅ Edge case naming test passed")

if __name__ == "__main__":
    test = TestGeneratorNamingConventions()
    test.test_typedef_naming_conventions()
    test.test_file_naming_conventions()
    test.test_complex_typedef_names()
    test.test_edge_case_names()
    print("🎉 All naming convention tests passed!")