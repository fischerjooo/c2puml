import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.parser import CParser
from src.c2puml.models import ProjectModel
import tempfile

class TestMacroDuplicateParsing:
    """Test macro duplicate parsing issues"""
    
    def test_no_duplicate_macro_definitions(self):
        """Test that same macro name doesn't appear twice"""
        
        # Test code with conditional macro definition
        test_code = """
        #if 1
            #define DEPRECATED __attribute__((deprecated))
        #else
            #define DEPRECATED
        #endif
        
        #define MAX_SIZE 100
        #define MIN_SIZE 10
        """
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Parse the file
            parser = CParser()
            project_model = ProjectModel(project_name="test_project", source_folder=os.path.dirname(temp_file))
            file_model = parser.parse_file(temp_file, os.path.basename(temp_file))
            
            # Add to project model
            project_model.files[file_model.name] = file_model
            
            # Check that we have macros
            assert len(file_model.macros) > 0, "No macros found"
            
            # Check for duplicate macro names
            macro_names = [macro for macro in file_model.macros]
            unique_macro_names = list(set(macro_names))
            
            print(f"All macro names: {macro_names}")
            print(f"Unique macro names: {unique_macro_names}")
            
            # Assert no duplicates
            assert len(macro_names) == len(unique_macro_names), f"Duplicate macros found: {macro_names}"
            
            # Check that DEPRECATED appears only once
            deprecated_count = macro_names.count("DEPRECATED")
            assert deprecated_count == 1, f"DEPRECATED macro appears {deprecated_count} times, expected 1"
            
            # Check that all expected macros are present
            expected_macros = ["DEPRECATED", "MAX_SIZE", "MIN_SIZE"]
            for expected_macro in expected_macros:
                assert expected_macro in macro_names, f"Expected macro '{expected_macro}' not found"
            
            print(f"Macro parsing successful: {len(macro_names)} unique macros found")
            
        finally:
            # Clean up
            os.unlink(temp_file)
    
    def test_complex_macro_definitions(self):
        """Test complex macro definitions with multiple conditions"""
        
        test_code = """
        #if 1
            #define LOG_LEVEL 3
            #define DEBUG_PRINT(x) printf("DEBUG: %s\\n", x)
        #else
            #define LOG_LEVEL 1
            #define DEBUG_PRINT(x) ((void)0)
        #endif
        
        #if 1
            #define PLATFORM "Windows"
        #elif 0
            #define PLATFORM "Linux"
        #else
            #define PLATFORM "Unknown"
        #endif
        
        #define VERSION "1.0.0"
        """
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Parse the file
            parser = CParser()
            project_model = ProjectModel(project_name="test_project", source_folder=os.path.dirname(temp_file))
            file_model = parser.parse_file(temp_file, os.path.basename(temp_file))
            
            # Add to project model
            project_model.files[file_model.name] = file_model
            
            # Check for duplicates
            macro_names = [macro for macro in file_model.macros]
            unique_macro_names = list(set(macro_names))
            
            print(f"Complex macros: {macro_names}")
            print(f"Unique complex macros: {unique_macro_names}")
            
            # Assert no duplicates
            assert len(macro_names) == len(unique_macro_names), f"Duplicate macros found: {macro_names}"
            
            # Check that LOG_LEVEL appears only once
            log_level_count = macro_names.count("LOG_LEVEL")
            assert log_level_count == 1, f"LOG_LEVEL macro appears {log_level_count} times, expected 1"
            
            # Check that VERSION appears only once
            version_count = macro_names.count("VERSION")
            assert version_count == 1, f"VERSION macro appears {version_count} times, expected 1"
            
            print(f"Complex macro parsing successful: {len(macro_names)} unique macros found")
            
        finally:
            # Clean up
            os.unlink(temp_file)

if __name__ == "__main__":
    test = TestMacroDuplicateParsing()
    test.test_no_duplicate_macro_definitions()
    test.test_complex_macro_definitions()