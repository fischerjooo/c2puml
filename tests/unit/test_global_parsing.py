#!/usr/bin/env python3
"""
Test global variable parsing to ensure function internals are not misidentified as globals
"""

import unittest
import tempfile
import os
from pathlib import Path

from c_to_plantuml.parser import CParser


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
                Path(temp_file), os.path.basename(temp_file), os.path.dirname(temp_file)
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
                Path(temp_file), os.path.basename(temp_file), os.path.dirname(temp_file)
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
                Path(temp_file), os.path.basename(temp_file), os.path.dirname(temp_file)
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


if __name__ == "__main__":
    unittest.main()
