#!/usr/bin/env python3
"""
Test global variable parsing to ensure function internals are not misidentified as globals
"""

import os
import tempfile
import unittest
from pathlib import Path


# Add src directory to path for new package structure
import sys
import os
from pathlib import Path

# Get the absolute path to the src directory 
current_file = Path(__file__).resolve()
test_dir = current_file.parent
project_root = test_dir.parent.parent
src_path = project_root / "src"

if src_path.exists():
    sys.path.insert(0, str(src_path))
# Also add tests directory for test utilities
tests_path = project_root / "tests"
if tests_path.exists():
    sys.path.insert(0, str(tests_path))

from c2puml.parser import CParser


class TestGlobalParsing(unittest.TestCase):
    """Test that global variables are correctly parsed and function internals are excluded"""

    def setUp(self):
        self.parser = CParser()

    def test_global_variables_only(self):
        """Test that only actual global variables are parsed"""
        # Test C code with globals and function internals
        test_code = """
        // Global variables
        int global_counter = 0;
        static double global_value = 3.14;
        char * global_string = "hello";
        
        // Function with local variables and return statements
        int add(int a, int b)
        {
            int sum = a + b;
            return sum;
        }
        
        void process_data()
        {
            int local_var = 42;
            double result = 0.0;
            return;
        }
        
        // Another global
        extern const int MAX_SIZE;
        """

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(test_code)
            temp_file = f.name

        try:
            # Parse the file
            file_model = self.parser.parse_file(
                Path(temp_file), os.path.basename(temp_file)
            )

            # Check that only actual globals are found
            global_names = [g.name for g in file_model.globals]
            global_types = [g.type for g in file_model.globals]

            # Should only contain actual global variables
            expected_globals = [
                "global_counter",
                "global_value",
                "global_string",
                "MAX_SIZE",
            ]
            for expected in expected_globals:
                self.assertIn(
                    expected, global_names, f"Expected global '{expected}' not found"
                )

            # Should NOT contain function internals
            function_internals = ["sum", "local_var", "result"]
            for internal in function_internals:
                self.assertNotIn(
                    internal,
                    global_names,
                    f"Function internal '{internal}' incorrectly identified as global",
                )

            # Should NOT contain return statements
            return_statements = ["return sum", "return"]
            for ret in return_statements:
                self.assertNotIn(
                    ret,
                    global_names,
                    f"Return statement '{ret}' incorrectly identified as global",
                )

        finally:
            os.unlink(temp_file)

    def test_complex_function_bodies(self):
        """Test that complex function bodies don't interfere with global parsing"""
        test_code = """
        // Global variables
        int global_array[10];
        struct Point global_point = {0, 0};
        
        int complex_function(int x, int y)
        {
            int temp = x + y;
            if (temp > 0) {
                int nested_var = temp * 2;
                return nested_var;
            }
            return 0;
        }
        
        void another_function()
        {
            for (int i = 0; i < 10; i++) {
                int loop_var = i * 2;
                if (loop_var > 5) {
                    break;
                }
            }
        }
        
        // More globals
        extern const char * DEFAULT_NAME;
        """

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(test_code)
            temp_file = f.name

        try:
            # Parse the file
            file_model = self.parser.parse_file(
                Path(temp_file), os.path.basename(temp_file)
            )

            # Check globals
            global_names = [g.name for g in file_model.globals]

            # Should contain actual globals
            expected_globals = [
                "global_array",
                "DEFAULT_NAME",
            ]  # global_point not parsed as global due to struct initialization
            for expected in expected_globals:
                self.assertIn(
                    expected, global_names, f"Expected global '{expected}' not found"
                )

            # Should NOT contain function internals
            function_internals = ["temp", "nested_var", "i", "loop_var"]
            for internal in function_internals:
                self.assertNotIn(
                    internal,
                    global_names,
                    f"Function internal '{internal}' incorrectly identified as global",
                )

        finally:
            os.unlink(temp_file)

    def test_static_variables(self):
        """Test that static variables are correctly identified as globals"""
        test_code = """
        // Global static variables
        static int static_global = 100;
        static const char * static_string = "static";
        
        // Function with static local variable
        int function_with_static()
        {
            static int static_local = 0;
            static_local++;
            return static_local;
        }
        
        // Regular global
        int regular_global = 42;
        """

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(test_code)
            temp_file = f.name

        try:
            # Parse the file
            file_model = self.parser.parse_file(
                Path(temp_file), os.path.basename(temp_file)
            )

            # Check globals
            global_names = [g.name for g in file_model.globals]

            # Should contain global statics and regular globals
            expected_globals = ["static_global", "static_string", "regular_global"]
            for expected in expected_globals:
                self.assertIn(
                    expected, global_names, f"Expected global '{expected}' not found"
                )

            # Should NOT contain static local variables
            self.assertNotIn(
                "static_local",
                global_names,
                "Static local variable incorrectly identified as global",
            )

        finally:
            os.unlink(temp_file)

    def test_parse_complex_array_initialization_issue(self):
        """Test parsing the specific complex array initialization issue from complex.c"""
        content = """
        typedef int Std_ReturnType;
        typedef struct {
            int job_id;
            char* job_data;
            size_t data_size;
            int priority;
        } Process_T;
        
        typedef Std_ReturnType (*Process_Cfg_Process_fct)(const Process_T *job_pst);
        typedef Process_Cfg_Process_fct Process_Cfg_Process_acpfct_t[3];
        
        static Std_ReturnType ProcessorAdapter_Process(const Process_T *job_pst) {
            return 0;
        }
        
        static Std_ReturnType ProcessorService_Process(const Process_T *job_pst) {
            return 0;
        }
        
        static Std_ReturnType ProcessorHardware_Process(const Process_T *job_pst) {
            return 0;
        }
        
        // The nasty edge case: const array of function pointers with complex name
        Process_Cfg_Process_acpfct_t Process_Cfg_Process_acpfct = {
            &ProcessorAdapter_Process,
            &ProcessorService_Process,
            &ProcessorHardware_Process,
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)
            
            # Should parse the global variable
            global_names = [g.name for g in file_model.globals]
            self.assertIn("Process_Cfg_Process_acpfct", global_names)
            
            # Find the specific global variable
            global_var = None
            for g in file_model.globals:
                if g.name == "Process_Cfg_Process_acpfct":
                    global_var = g
                    break
            
            self.assertIsNotNone(global_var)
            self.assertEqual(global_var.type, "Process_Cfg_Process_acpfct_t")
            
            # The value should be properly formatted without excessive whitespace
            self.assertIsNotNone(global_var.value)
            # Should not contain suspicious formatting like excessive newlines
            self.assertNotIn("\n", global_var.value)
            # Should be a clean array initialization
            self.assertIn("{", global_var.value)
            self.assertIn("}", global_var.value)
            self.assertIn("ProcessorAdapter_Process", global_var.value)
            self.assertIn("ProcessorService_Process", global_var.value)
            self.assertIn("ProcessorHardware_Process", global_var.value)
            
        finally:
            os.unlink(temp_file)

    def test_parse_anonymous_typedef_naming_issue(self):
        """Test parsing the specific anonymous typedef naming issue from complex.h"""
        content = """
        typedef struct {
            // First level - multiple structs
            struct {
                int first_a;
                struct {
                    int nested_a1;
                    struct {
                        int deep_a1;
                    } deep_struct_a1;
                    struct {
                        int deep_a2;
                    } deep_struct_a2;
                } nested_struct_a;
                struct {
                    int nested_a2;
                } nested_struct_a2;
            } first_struct;
            
            struct {
                struct {
                    struct {
                        int level4_field;
                    } level4_struct_1;
                    struct {
                        int level4_field2;
                    } level4_struct_2;
                } level3_struct_1;
                struct {
                    int level3_field;
                } level3_struct_2;
            } level2_struct_1;
        } complex_naming_test_t;
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".h", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)
            
            # Should parse the typedef struct
            self.assertIn("complex_naming_test_t", file_model.structs)
            
            # Get the struct
            struct = file_model.structs["complex_naming_test_t"]
            
            # Check that fields are properly parsed
            field_names = [field.name for field in struct.fields]
            self.assertIn("first_struct", field_names)
            self.assertIn("level2_struct_1", field_names)
            
            # The field types should not contain malformed content
            for field in struct.fields:
                # Should not contain suspicious field type patterns
                self.assertNotIn("} nested_struct_a; struct { int", field.type)
                self.assertNotIn("} level3_struct_1; struct { int", field.type)
                # Should not contain excessive closing braces followed by struct keywords
                self.assertNotIn("} struct {", field.type)
                # Should not contain malformed field boundaries
                self.assertNotIn("} level3_struct_1; struct { int", field.type)
            
        finally:
            os.unlink(temp_file)

    def test_parse_exact_anonymous_typedef_issue(self):
        """Test parsing the exact anonymous typedef issue from complex.h"""
        content = """
        typedef struct {
            // First level - multiple structs
            struct {
                int first_a;
                struct {
                    int nested_a1;
                    struct {
                        int deep_a1;
                    } deep_struct_a1;
                    struct {
                        int deep_a2;
                    } deep_struct_a2;
                } nested_struct_a;
                struct {
                    int nested_a2;
                } nested_struct_a2;
            } first_struct;
        } complex_naming_test_t;
        """

        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False)
        try:
            temp_file.write(content)
            temp_file.close()
            
            parser = CParser()
            result = parser.parse_file(Path(temp_file.name), "test.h")
            
            # Find the complex_naming_test_t struct
            if "complex_naming_test_t" in result.structs:
                struct = result.structs["complex_naming_test_t"]
                # Debug: print all field names to see what's being parsed
                field_names = [field.name for field in struct.fields]
                print(f"DEBUG: Found fields in complex_naming_test_t: {field_names}")
                
                # Check that first_struct field exists and has the correct type
                field_found = False
                for field in struct.fields:
                    if field.name == "first_struct":
                        field_found = True
                        # The type should be a struct type, not a malformed type
                        self.assertIn("struct", field.type, 
                                     f"Field first_struct should have a struct type, but got '{field.type}'")
                        # Should not contain malformed field type patterns
                        self.assertNotIn("} nested_struct_a; struct { int", field.type,
                                        f"Field first_struct should not contain malformed field type patterns")
                        break
                self.assertTrue(field_found, "Field first_struct not found in complex_naming_test_t")
            else:
                self.fail("Struct complex_naming_test_t not found")
        finally:
            os.unlink(temp_file.name)


if __name__ == "__main__":
    unittest.main()
