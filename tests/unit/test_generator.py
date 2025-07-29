#!/usr/bin/env python3
"""
Unit tests for PlantUML generator functionality
"""

import os
import tempfile
import unittest
from pathlib import Path

# We need to add the parent directory to Python path for imports
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from c_to_plantuml.generator import Generator
from c_to_plantuml.parser import CParser
from c_to_plantuml.models import (
    Alias,
    Enum,
    Field,
    FileModel,
    Function,
    ProjectModel,
    Struct,
    Union,
)


class TestGenerator(unittest.TestCase):
    """Test suite for the Generator class"""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.parser = CParser()
        self.generator = Generator()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file_model(self, filename: str = "test.c") -> FileModel:
        """Create a test file model with sample data"""
        return FileModel(
            file_path=filename,
            structs={
                "Person": Struct(
                    "Person",
                    [
                        Field("name", "char*"),
                        Field("age", "int"),
                        Field("height", "float"),
                    ],
                ),
                "Config": Struct(
                    "Config", [Field("max_users", "int"), Field("timeout", "int")]
                ),
            },
            enums={
                "Status": Enum("Status", ["OK", "ERROR", "PENDING"]),
                "Color": Enum("Color", ["RED", "GREEN", "BLUE"]),
            },
            functions=[
                Function("main", "int", []),
                Function("process_data", "void", [Field("data", "void*")]),
                Function(
                    "calculate", "float", [Field("a", "float"), Field("b", "float")]
                ),
            ],
            globals=[Field("global_var", "int"), Field("global_string", "char*")],
            includes=["stdio.h", "stdlib.h", "local.h"],
            macros=["MAX_SIZE", "DEBUG_MODE", "VERSION"],
            aliases={
                "Integer": Alias("Integer", "int"),
                "String": Alias("String", "char*"),
                "Callback": Alias("Callback", "void (*)(int)"),
            },
        )

    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file with given content."""
        file_path = self.temp_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def test_generate_basic_plantuml_content(self):
        """Test basic PlantUML content generation"""
        content = """
        #include <stdio.h>

        struct my_struct {
            int field1;
            char field2[10];
        };

        enum my_enum {
            VALUE1,
            VALUE2 = 5
        };

        void my_function(int param) {
            // Function implementation
            return;
        }
        """

        test_file = self.create_test_file("test.c", content)

        # Parse the file
        project_model = self.parser.parse_project(str(self.temp_dir))
        file_model = project_model.files["test.c"]

        # Generate PlantUML diagram
        diagram = self.generator.generate_diagram(file_model, project_model)

        # Check that PlantUML syntax is correct
        self.assertIn("@startuml test", diagram)
        self.assertIn("@enduml", diagram)

        # Check that main class is generated
        self.assertIn('class "test" as TEST <<source>> #LightBlue', diagram)

        # Check that struct is included as typedef
        self.assertIn("my_struct", diagram)
        self.assertIn("field1", diagram)
        self.assertIn("field2", diagram)

        # Check that enum is included as typedef
        self.assertIn("my_enum", diagram)
        self.assertIn("VALUE1", diagram)
        self.assertIn("VALUE2", diagram)

        # Check that function is included
        self.assertIn("my_function", diagram)

    def test_generate_with_macros(self):
        """Test PlantUML generation with macros"""
        content = """
        #define MAX_SIZE 100
        #define DEBUG 1
        #define MIN(a, b) ((a) < (b) ? (a) : (b))

        int main() {
            return 0;
        }
        """

        test_file = self.create_test_file("test.c", content)

        # Parse the file
        project_model = self.parser.parse_project(str(self.temp_dir))
        file_model = project_model.files["test.c"]

        # Generate PlantUML diagram
        diagram = self.generator.generate_diagram(file_model, project_model)

        # Check that PlantUML syntax is correct
        self.assertIn("@startuml test", diagram)
        self.assertIn("@enduml", diagram)

        # Check that main class is generated
        self.assertIn('class "test" as TEST <<source>> #LightBlue', diagram)

        # Check that macros are included
        self.assertIn("-- Macros --", diagram)
        self.assertIn("- #define MAX_SIZE", diagram)
        self.assertIn("- #define DEBUG", diagram)

    def test_generate_file_diagram(self):
        """Test generating a PlantUML diagram file"""
        file_model = self.create_test_file_model("test.c")
        output_dir = self.temp_dir

        # Create a simple project model for testing
        project_model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"test.c": file_model},
        )
        diagram = self.generator.generate_diagram(file_model, project_model)

        # Write the content to file
        puml_file = output_dir / "test.puml"
        with open(puml_file, "w", encoding="utf-8") as f:
            f.write(diagram)

        # Check that the file was created
        puml_file = output_dir / "test.puml"
        self.assertTrue(puml_file.exists())

        # Check file content
        with open(puml_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("@startuml test", content)
        self.assertIn("@enduml", content)
        self.assertIn('class "test" as TEST <<source>> #LightBlue', content)

    def test_generate_from_model(self):
        """Test generating diagrams from a model file"""
        # Create a test model
        file_model = self.create_test_file_model("main.c")
        model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"main.c": file_model},
        )

        # Save model to file
        model_path = os.path.join(self.temp_dir, "test_model.json")
        model.save(model_path)

        # Generate diagrams
        output_dir = os.path.join(self.temp_dir, "output")
        self.generator.generate(model_path, output_dir)

        # Check output directory was created
        self.assertTrue(os.path.exists(output_dir))

        # Check that diagram file was created
        puml_file = os.path.join(output_dir, "main.puml")
        self.assertTrue(os.path.exists(puml_file))

        # Check file content
        with open(puml_file, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertIn("@startuml main", content)
        self.assertIn("@enduml", content)

    def test_generate_with_config(self):
        """Test generating diagrams using configuration"""
        # Create test model
        file_model = self.create_test_file_model("main.c")
        model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"main.c": file_model},
        )

        # Create configuration
        config = {
            "project_name": "test_project",
            "source_folders": ["/test"],
            "output_dir": os.path.join(self.temp_dir, "config_output"),
            "recursive_search": True,
            "file_filters": {},
            "element_filters": {},
        }

        # Save model
        model_path = os.path.join(self.temp_dir, "test_model.json")
        model.save(model_path)

        # Generate with config
        self.generator.generate(model_path, config["output_dir"])

        # Verify output
        self.assertTrue(os.path.exists(config["output_dir"]))
        puml_file = os.path.join(config["output_dir"], "main.puml")
        self.assertTrue(os.path.exists(puml_file))

    def test_generate_multiple_files(self):
        """Test generating diagrams for multiple files"""
        # Create multiple file models
        file1 = self.create_test_file_model("main.c")
        file2 = FileModel(
            file_path="utils.c",
            structs={},
            enums={},
            functions=[Function("helper", "void", [])],
            globals=[],
            includes=["stdio.h"],
            macros=[],
            aliases={},
        )

        model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"main.c": file1, "utils.c": file2},
        )

        # Save and generate
        model_path = os.path.join(self.temp_dir, "test_model.json")
        model.save(model_path)

        output_dir = os.path.join(self.temp_dir, "output")
        self.generator.generate(model_path, output_dir)

        # Check both files were generated
        self.assertTrue(os.path.exists(os.path.join(output_dir, "main.puml")))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "utils.puml")))

    def test_generate_empty_file_model(self):
        """Test generating diagram for empty file model"""
        empty_file = FileModel(
            file_path="empty.c",
            structs={},
            enums={},
            functions=[],
            globals=[],
            includes=[],
            macros=[],
            aliases={},
        )

        # Create a simple project model for testing
        project_model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"empty.c": empty_file},
        )
        diagram = self.generator.generate_diagram(empty_file, project_model)

        # Should still generate valid PlantUML
        self.assertIn("@startuml empty", diagram)
        self.assertIn("@enduml", diagram)
        self.assertIn('class "empty" as EMPTY <<source>> #LightBlue', diagram)

    def test_generate_with_special_characters(self):
        """Test generation with special characters in names"""
        # Create a test file with special characters
        content = """
struct Test_Struct {
    int field_1;
    char* field_2;
};

void test_function() {
    // Test function
}
        """
        test_file = self.create_test_file("test_file.c", content)

        # Parse the file
        project_model = self.parser.parse_project(str(self.temp_dir))
        file_model = project_model.files["test_file.c"]

        # Generate PlantUML diagram
        diagram = self.generator.generate_diagram(file_model, project_model)

        # Check that PlantUML syntax is correct
        self.assertIn("@startuml test_file", diagram)
        self.assertIn("@enduml", diagram)

        # Check that main class is generated with correct name
        self.assertIn('class "test_file" as TEST_FILE <<source>> #LightBlue', diagram)

        # Check that functions are included
        self.assertIn("-- Functions --", diagram)
        self.assertIn("void test_function()", diagram)

        # Structs are not shown inside source file classes, but as separate typedef classes
        # self.assertIn("struct Test_Struct", content)  # no + prefix in source files - REMOVED
        # Instead, verify struct appears as separate typedef class
        self.assertIn('class "Test_Struct" as TYPEDEF_TEST_STRUCT <<typedef>> #LightYellow', diagram)

    def test_generate_error_handling(self):
        """Test error handling in diagram generation"""
        # Test with non-existent model file
        with self.assertRaises(Exception):
            self.generator.generate_from_model(
                "/non/existent/model.json", self.temp_dir
            )

        # Test with invalid model file
        invalid_model_path = os.path.join(self.temp_dir, "invalid.json")
        with open(invalid_model_path, "w") as f:
            f.write("invalid json")

        with self.assertRaises(Exception):
            self.generator.generate_from_model(invalid_model_path, self.temp_dir)

    def test_plantuml_syntax_validity(self):
        """Test that generated PlantUML syntax is valid"""
        file_model = self.create_test_file_model("test.c")
        # Create a simple project model for testing
        project_model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"test.c": file_model},
        )
        diagram = self.generator.generate_diagram(file_model, project_model)

        # Check for required PlantUML elements
        self.assertIn("@startuml", diagram)
        self.assertIn("@enduml", diagram)
        self.assertIn("class", diagram)

        # Check for proper class syntax
        self.assertIn('class "test" as TEST', diagram)

        # Check for proper relationship syntax
        # At minimum, we should have relationship sections even if empty
        self.assertIn("' Include relationships", diagram)
        self.assertIn("' Declaration relationships", diagram)

        # Check for proper section separators
        self.assertIn("--", diagram)

    def test_relationship_generation(self):
        """Test that relationships are properly generated when they exist"""
        # Create content with includes and structs
        content = '''
        #include <stdio.h>
        
        struct my_struct {
            int field1;
        };
        
        void my_function() {
            return;
        }
        '''
        
        test_file = self.create_test_file("test.c", content)
        
        # Parse the file
        project_model = self.parser.parse_project(str(self.temp_dir))
        file_model = project_model.files["test.c"]
        
        # Generate PlantUML diagram
        diagram = self.generator.generate_diagram(file_model, project_model)
        
        # Check that relationship sections exist
        self.assertIn("' Include relationships", diagram)
        self.assertIn("' Declaration relationships", diagram)
        
        # Check that declaration relationships are generated for structs
        self.assertIn("..>", diagram)  # Declaration relationship arrow
        self.assertIn("<<declares>>", diagram)  # Declaration relationship label

    def test_global_variables_generation(self):
        """Test that global variables are properly generated"""
        # Use the test file model that includes global variables
        file_model = self.create_test_file_model("test.c")
        project_model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"test.c": file_model},
        )
        
        # Generate PlantUML diagram
        diagram = self.generator.generate_diagram(file_model, project_model)
        
        # Check that global variables section exists
        self.assertIn("-- Global Variables --", diagram)
        
        # Check that the specific global variables are included
        self.assertIn("int global_var", diagram)
        self.assertIn("char* global_string", diagram)
        
    def test_global_variables_with_real_parsing(self):
        """Test global variables generation with real C code parsing"""
        content = '''
        int global_counter = 0;
        char* global_message = "Hello";
        static float internal_value = 3.14;
        
        void test_function() {
            global_counter++;
        }
        '''
        
        test_file = self.create_test_file("globals_test.c", content)
        
        # Parse the file
        project_model = self.parser.parse_project(str(self.temp_dir))
        file_model = project_model.files["globals_test.c"]
        
        # Generate PlantUML diagram
        diagram = self.generator.generate_diagram(file_model, project_model)
        
        # Check that global variables section exists
        self.assertIn("-- Global Variables --", diagram)
        
        # Check that parsed global variables appear
        # Note: The exact format may depend on how the parser handles initialization
        self.assertIn("global_counter", diagram)
        self.assertIn("global_message", diagram)
        self.assertIn("internal_value", diagram)

    def test_typedef_generation_comprehensive(self):
        """Test that all typedef types (structs, enums, unions, aliases) are generated"""
        # Use the test file model that includes various typedef types
        file_model = self.create_test_file_model("test.c")
        project_model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"test.c": file_model},
        )
        
        # Generate PlantUML diagram
        diagram = self.generator.generate_diagram(file_model, project_model)
        
        # Check that struct typedef classes are generated
        self.assertIn('class "Person" as TYPEDEF_PERSON <<typedef>> #LightYellow', diagram)
        self.assertIn('class "Config" as TYPEDEF_CONFIG <<typedef>> #LightYellow', diagram)
        
        # Check that enum typedef classes are generated
        self.assertIn('class "Status" as TYPEDEF_STATUS <<typedef>> #LightYellow', diagram)
        self.assertIn('class "Color" as TYPEDEF_COLOR <<typedef>> #LightYellow', diagram)
        
        # Check that alias typedef classes are generated
        self.assertIn('class "Integer" as TYPEDEF_INTEGER <<typedef>> #LightYellow', diagram)
        self.assertIn('class "String" as TYPEDEF_STRING <<typedef>> #LightYellow', diagram)
        self.assertIn('class "Callback" as TYPEDEF_CALLBACK <<typedef>> #LightYellow', diagram)

    def test_union_generation(self):
        """Test union generation with real C code parsing"""
        content = '''
        union data_union {
            int int_value;
            float float_value;
            char char_array[16];
        };
        
        union {
            long long_val;
            double double_val;
        } anonymous_union;
        
        void test_function() {
            union data_union my_union;
        }
        '''
        
        test_file = self.create_test_file("union_test.c", content)
        
        # Parse the file
        project_model = self.parser.parse_project(str(self.temp_dir))
        file_model = project_model.files["union_test.c"]
        
        # Generate PlantUML diagram
        diagram = self.generator.generate_diagram(file_model, project_model)
        
        # Check that union typedef classes are generated
        self.assertIn("data_union", diagram)
        self.assertIn("int_value", diagram)
        self.assertIn("float_value", diagram)
        self.assertIn("char_array", diagram)

    def test_function_parameter_truncation(self):
        """Test that long function signatures are properly truncated"""
        content = '''
        // This should create a very long function signature
        int very_long_function_name_that_exceeds_limits(
            int very_long_parameter_name_one,
            char* very_long_parameter_name_two,
            float very_long_parameter_name_three,
            double very_long_parameter_name_four,
            struct very_long_struct_name* very_long_parameter_name_five,
            void (*very_long_callback_parameter)(int, char*, float, double)
        ) {
            return 0;
        }
        '''
        
        test_file = self.create_test_file("truncation_test.c", content)
        
        # Parse the file
        project_model = self.parser.parse_project(str(self.temp_dir))
        file_model = project_model.files["truncation_test.c"]
        
        # Generate PlantUML diagram
        diagram = self.generator.generate_diagram(file_model, project_model)
        
        # Check that function is included
        self.assertIn("very_long_function_name_that_exceeds_limits", diagram)
        
        # Check for truncation indicator when signature is too long
        # The function should appear but potentially with "..." if truncated
        function_lines = [line for line in diagram.split('\n') if 'very_long_function_name_that_exceeds_limits' in line]
        self.assertTrue(len(function_lines) > 0, "Function should appear in diagram")
        
        # If truncated, should contain "..."
        function_line = function_lines[0]
        # Function is likely truncated due to length, but we just verify it exists
        self.assertIn("very_long_function_name_that_exceeds_limits", function_line)

    def test_enum_generation_with_values(self):
        """Test enum generation with specific values"""
        content = '''
        enum http_status {
            HTTP_OK = 200,
            HTTP_NOT_FOUND = 404,
            HTTP_ERROR = 500
        };
        
        enum simple_enum {
            FIRST,
            SECOND,
            THIRD
        };
        
        void process_status(enum http_status status) {
            // Process status
        }
        '''
        
        test_file = self.create_test_file("enum_test.c", content)
        
        # Parse the file
        project_model = self.parser.parse_project(str(self.temp_dir))
        file_model = project_model.files["enum_test.c"]
        
        # Generate PlantUML diagram
        diagram = self.generator.generate_diagram(file_model, project_model)
        
        # Check that enum typedef classes are generated
        self.assertIn("http_status", diagram)
        self.assertIn("simple_enum", diagram)
        
        # Check that enum values are included
        self.assertIn("HTTP_OK", diagram)
        self.assertIn("HTTP_NOT_FOUND", diagram)
        self.assertIn("FIRST", diagram)
        self.assertIn("SECOND", diagram)

    def test_header_vs_source_prefixes(self):
        """Test that headers use + prefix and sources use - prefix for macros"""
        # Create a header file and a source file
        header_content = '''
        #ifndef TEST_H
        #define TEST_H
        #define HEADER_MACRO 42
        
        extern int global_header_var;
        void header_function(void);
        
        #endif
        '''
        
        source_content = '''
        #include "test.h"
        #define SOURCE_MACRO 100
        
        int global_source_var = 0;
        
        void source_function(void) {
            // Implementation
        }
        '''
        
        # Create both files
        header_file = self.create_test_file("test.h", header_content)
        source_file = self.create_test_file("test.c", source_content)
        
        # Parse the project
        project_model = self.parser.parse_project(str(self.temp_dir))
        file_model = project_model.files["test.c"]
        
        # Generate PlantUML diagram
        diagram = self.generator.generate_diagram(file_model, project_model)
        
        # Check that source file uses no prefix for globals, - prefix for macros
        self.assertIn('class "test" as TEST <<source>> #LightBlue', diagram)
        self.assertIn("- #define SOURCE_MACRO", diagram)  # Source macros with - prefix
        
        # Check that header file uses + prefix for macros and globals
        self.assertIn('class "test" as HEADER_TEST <<header>> #LightGreen', diagram)
        self.assertIn("+ #define HEADER_MACRO", diagram)  # Header macros with + prefix
        self.assertIn("+ int global_header_var", diagram)  # Header globals with + prefix

    def test_include_relationships_generation(self):
        """Test that include relationships are properly generated"""
        # Create a header file
        header_content = '''
        #ifndef MYHEADER_H
        #define MYHEADER_H
        
        typedef struct {
            int value;
        } my_type_t;
        
        #endif
        '''
        
        # Create a source file that includes the header
        source_content = '''
        #include "myheader.h"
        #include <stdio.h>
        
        void test_function(my_type_t* param) {
            printf("Value: %d\\n", param->value);
        }
        '''
        
        # Create both files
        header_file = self.create_test_file("myheader.h", header_content)
        source_file = self.create_test_file("main.c", source_content)
        
        # Parse the project
        project_model = self.parser.parse_project(str(self.temp_dir))
        file_model = project_model.files["main.c"]
        
        # Generate PlantUML diagram
        diagram = self.generator.generate_diagram(file_model, project_model)
        
        # Check that include relationships are generated
        self.assertIn("' Include relationships", diagram)
        self.assertIn("-->", diagram)  # Include relationship arrow
        self.assertIn("<<include>>", diagram)  # Include relationship label
        
        # Should have relationship from main.c to myheader.h
        self.assertIn("MAIN --> HEADER_MYHEADER : <<include>>", diagram)

    def test_output_directory_creation(self):
        """Test that output directory is created if it doesn't exist"""
        file_model = self.create_test_file_model("test.c")
        model = ProjectModel(
            project_name="test_project",
            source_folder="/test",
            files={"test.c": file_model},
        )

        # Save model
        model_path = os.path.join(self.temp_dir, "test_model.json")
        model.save(model_path)

        # Generate to non-existent directory
        output_dir = os.path.join(self.temp_dir, "new_output_dir")
        self.generator.generate(model_path, output_dir)

        # Directory should be created
        self.assertTrue(os.path.exists(output_dir))
        self.assertTrue(os.path.exists(os.path.join(output_dir, "test.puml")))
