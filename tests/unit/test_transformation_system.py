import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.transformer import Transformer
from src.c2puml.models import ProjectModel, FileModel, Alias, Function, Field
import tempfile
import json

class TestTransformationSystem:
    def test_typedef_renaming(self):
        """Test that typedef renaming works correctly"""
        # Create a test project model
        project_model = ProjectModel(project_name="test_project", source_folder="/tmp")
        
        # Create a test file model with typedefs
        file_model = FileModel(name="transformed.c", file_path="/tmp/transformed.c")
        file_model.aliases["old_config_t"] = Alias(name="old_config_t", original_type="void*")
        file_model.aliases["legacy_int_t"] = Alias(name="legacy_int_t", original_type="int")
        
        project_model.files["transformed.c"] = file_model
        
        # Create configuration with rename transformations
        config = {
            "transformations_01_rename": {
                "file_selection": [".*transformed\\.(c|h)$"],
                "rename": {
                    "typedef": {"^old_config_t$": "config_t"},
                    "functions": {"^deprecated_(.*)": "legacy_\\1"}
                }
            }
        }
        
        # Create transformer and apply transformations
        transformer = Transformer()
        transformed_model = transformer._apply_transformations(project_model, config)
        
        # Check that typedef was renamed
        transformed_file = transformed_model.files["transformed.c"]
        
        # The old typedef should be gone
        assert "old_config_t" not in transformed_file.aliases, "old_config_t should be renamed"
        
        # The new typedef should exist
        assert "config_t" in transformed_file.aliases, "config_t should exist after renaming"
        assert transformed_file.aliases["config_t"].original_type == "void*", "config_t should have the same type as old_config_t"
        
        print("✅ Typedef renaming test passed")

    def test_function_renaming(self):
        """Test that function renaming works correctly"""
        # Create a test project model
        project_model = ProjectModel(project_name="test_project", source_folder="/tmp")
        
        # Create a test file model with functions
        file_model = FileModel(name="transformed.c", file_path="/tmp/transformed.c")
        file_model.functions = [
            Function(name="deprecated_print_info", return_type="void", parameters=[]),
            Function(name="deprecated_cleanup", return_type="void", parameters=[]),
            Function(name="keep_this_function", return_type="void", parameters=[])
        ]
        
        project_model.files["transformed.c"] = file_model
        
        # Create configuration with function rename transformations
        config = {
            "transformations_01_rename": {
                "file_selection": [".*transformed\\.(c|h)$"],
                "rename": {
                    "functions": {"^deprecated_(.*)": "legacy_\\1"}
                }
            }
        }
        
        # Create transformer and apply transformations
        transformer = Transformer()
        transformed_model = transformer._apply_transformations(project_model, config)
        
        # Check that functions were renamed
        transformed_file = transformed_model.files["transformed.c"]
        
        # Get function names
        function_names = [func.name for func in transformed_file.functions]
        
        # The old function names should be gone
        assert "deprecated_print_info" not in function_names, "deprecated_print_info should be renamed"
        assert "deprecated_cleanup" not in function_names, "deprecated_cleanup should be renamed"
        
        # The new function names should exist
        assert "legacy_print_info" in function_names, "legacy_print_info should exist after renaming"
        assert "legacy_cleanup" in function_names, "legacy_cleanup should exist after renaming"
        
        # Functions that don't match the pattern should remain unchanged
        assert "keep_this_function" in function_names, "keep_this_function should remain unchanged"
        
        print("✅ Function renaming test passed")

    def test_macro_renaming(self):
        """Test that macro renaming works correctly"""
        # Create a test project model
        project_model = ProjectModel(project_name="test_project", source_folder="/tmp")
        
        # Create a test file model with macros
        file_model = FileModel(name="transformed.c", file_path="/tmp/transformed.c")
        file_model.macros = [
            "#define OLD_VERSION \"1.0\"",
            "#define OLD_API_VERSION 100",
            "#define NEW_CONSTANT 42"
        ]
        
        project_model.files["transformed.c"] = file_model
        
        # Create configuration with macro rename transformations
        config = {
            "transformations_01_rename": {
                "file_selection": [".*transformed\\.(c|h)$"],
                "rename": {
                    "macros": {"^OLD_(.*)": "LEGACY_\\1"}
                }
            }
        }
        
        # Create transformer and apply transformations
        transformer = Transformer()
        transformed_model = transformer._apply_transformations(project_model, config)
        
        # Check that macros were renamed
        transformed_file = transformed_model.files["transformed.c"]
        
        # Get macro names
        macro_names = [macro.replace("#define ", "").split(" ")[0] for macro in transformed_file.macros]
        print(f"Original macros: {file_model.macros}")
        print(f"Transformed macros: {transformed_file.macros}")
        print(f"Macro names: {macro_names}")
        
        # The old macro names should be gone
        assert "OLD_VERSION" not in macro_names, "OLD_VERSION should be renamed"
        assert "OLD_API_VERSION" not in macro_names, "OLD_API_VERSION should be renamed"
        
        # The new macro names should exist
        assert "LEGACY_VERSION" in macro_names, "LEGACY_VERSION should exist after renaming"
        assert "LEGACY_API_VERSION" in macro_names, "LEGACY_API_VERSION should exist after renaming"
        
        # Macros that don't match the pattern should remain unchanged
        assert "NEW_CONSTANT" in macro_names, "NEW_CONSTANT should remain unchanged"
        
        print("✅ Macro renaming test passed")

    def test_global_variable_renaming(self):
        """Test that global variable renaming works correctly"""
        # Create a test project model
        project_model = ProjectModel(project_name="test_project", source_folder="/tmp")
        
        # Create a test file model with global variables
        file_model = FileModel(name="transformed.c", file_path="/tmp/transformed.c")
        file_model.globals = [
            Field(name="legacy_path", type="char*"),
            Field(name="old_global_counter", type="int"),
            Field(name="new_variable", type="int")
        ]
        
        project_model.files["transformed.c"] = file_model
        
        # Create configuration with global variable rename transformations
        config = {
            "transformations_01_rename": {
                "file_selection": [".*transformed\\.(c|h)$"],
                "rename": {
                    "globals": {"^legacy_path$": "system_path"}
                }
            }
        }
        
        # Create transformer and apply transformations
        transformer = Transformer()
        transformed_model = transformer._apply_transformations(project_model, config)
        
        # Check that global variables were renamed
        transformed_file = transformed_model.files["transformed.c"]
        
        # Get global variable names
        global_names = [global_var.name for global_var in transformed_file.globals]
        
        # The old global variable name should be gone
        assert "legacy_path" not in global_names, "legacy_path should be renamed"
        
        # The new global variable name should exist
        assert "system_path" in global_names, "system_path should exist after renaming"
        
        # Global variables that don't match the pattern should remain unchanged
        assert "old_global_counter" in global_names, "old_global_counter should remain unchanged"
        assert "new_variable" in global_names, "new_variable should remain unchanged"
        
        print("✅ Global variable renaming test passed")

    def test_removal_operations(self):
        """Test that removal operations work correctly"""
        # Create a test project model
        project_model = ProjectModel(project_name="test_project", source_folder="/tmp")
        
        # Create a test file model with various elements
        file_model = FileModel(name="transformed.c", file_path="/tmp/transformed.c")
        file_model.aliases["legacy_int_t"] = Alias(name="legacy_int_t", original_type="int")
        file_model.functions = [
            Function(name="test_function_one", return_type="void", parameters=[]),
            Function(name="debug_log", return_type="void", parameters=[]),
            Function(name="keep_this_function", return_type="void", parameters=[])
        ]
        file_model.macros = [
            "#define DEPRECATED_MAX_SIZE 1024",
            "#define LEGACY_DEBUG 1",
            "#define NEW_CONSTANT 42"
        ]
        
        project_model.files["transformed.c"] = file_model
        
        # Create configuration with removal transformations
        config = {
            "transformations_02_cleanup": {
                "file_selection": [".*transformed\\.(c|h)$"],
                "remove": {
                    "typedef": ["^legacy_.*"],
                    "functions": ["^test_.*", "^debug_.*"],
                    "macros": ["^DEPRECATED_.*", "^LEGACY_(?!API_VERSION$).*"]
                }
            }
        }
        
        # Create transformer and apply transformations
        transformer = Transformer()
        transformed_model = transformer._apply_transformations(project_model, config)
        
        # Check that elements were removed
        transformed_file = transformed_model.files["transformed.c"]
        
        # The removed typedef should be gone
        assert "legacy_int_t" not in transformed_file.aliases, "legacy_int_t should be removed"
        
        # The removed functions should be gone
        function_names = [func.name for func in transformed_file.functions]
        assert "test_function_one" not in function_names, "test_function_one should be removed"
        assert "debug_log" not in function_names, "debug_log should be removed"
        
        # The removed macros should be gone
        macro_names = [macro.replace("#define ", "").split(" ")[0] for macro in transformed_file.macros]
        assert "DEPRECATED_MAX_SIZE" not in macro_names, "DEPRECATED_MAX_SIZE should be removed"
        assert "LEGACY_DEBUG" not in macro_names, "LEGACY_DEBUG should be removed"
        
        # Elements that don't match the patterns should remain
        assert "keep_this_function" in function_names, "keep_this_function should remain"
        assert "NEW_CONSTANT" in macro_names, "NEW_CONSTANT should remain"
        
        print("✅ Removal operations test passed")

if __name__ == "__main__":
    test = TestTransformationSystem()
    test.test_typedef_renaming()
    test.test_function_renaming()
    test.test_macro_renaming()
    test.test_global_variable_renaming()
    test.test_removal_operations()
    print("🎉 All transformation system tests passed!")