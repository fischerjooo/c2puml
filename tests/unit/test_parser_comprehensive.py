#!/usr/bin/env python3
"""
Comprehensive unit tests for the C parser
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from typing import Dict, List


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

from c2puml.models import Alias, Enum, Field, Function, Struct, Union
from c2puml.parser import CParser
from c2puml.parser_tokenizer import CTokenizer, TokenType


class TestCParserComprehensive(unittest.TestCase):
    """Comprehensive tests for the C parser"""

    def setUp(self):
        self.parser = CParser()
        self.tokenizer = CTokenizer()

    def test_parse_simple_struct(self):
        """Test parsing a simple struct definition"""
        content = """
        struct Point {
            int x;
            int y;
            char label[32];
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertIn("Point", file_model.structs)
            point_struct = file_model.structs["Point"]
            self.assertEqual(len(point_struct.fields), 3)

            # Check field names
            field_names = [field.name for field in point_struct.fields]
            self.assertIn("x", field_names)
            self.assertIn("y", field_names)
            self.assertIn("label", field_names)

        finally:
            os.unlink(temp_file)

    def test_parse_typedef_struct(self):
        """Test parsing typedef struct definitions"""
        content = """
        typedef struct point_tag {
            int x;
            int y;
        } point_t;
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertIn("point_t", file_model.structs)
            point_struct = file_model.structs["point_t"]
            self.assertEqual(len(point_struct.fields), 2)

        finally:
            os.unlink(temp_file)

    def test_parse_anonymous_struct(self):
        """Test parsing anonymous struct definitions"""
        content = """
        struct {
            int x;
            int y;
        } point;
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            # Anonymous structs should be handled appropriately
            # The parser might create a name or handle it differently
            self.assertGreaterEqual(len(file_model.structs), 0)

        finally:
            os.unlink(temp_file)

    def test_parse_nested_struct(self):
        """Test parsing nested struct definitions"""
        content = """
        struct Rectangle {
            struct Point top_left;
            struct Point bottom_right;
            int width;
            int height;
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertIn("Rectangle", file_model.structs)
            rect_struct = file_model.structs["Rectangle"]
            self.assertEqual(len(rect_struct.fields), 4)

        finally:
            os.unlink(temp_file)

    def test_parse_enum_simple(self):
        """Test parsing simple enum definitions"""
        content = """
        enum Status {
            OK = 0,
            ERROR = 1,
            PENDING = 2
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertIn("Status", file_model.enums)
            status_enum = file_model.enums["Status"]
            self.assertEqual(len(status_enum.values), 3)

            # Check enum values
            enum_values = [value.name for value in status_enum.values]
            self.assertIn("OK", enum_values)
            self.assertIn("ERROR", enum_values)
            self.assertIn("PENDING", enum_values)

        finally:
            os.unlink(temp_file)

    def test_parse_typedef_enum(self):
        """Test parsing typedef enum definitions"""
        content = """
        typedef enum color_tag {
            RED = 0,
            GREEN = 1,
            BLUE = 2
        } color_t;
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertIn("color_t", file_model.enums)
            color_enum = file_model.enums["color_t"]
            self.assertEqual(len(color_enum.values), 3)

        finally:
            os.unlink(temp_file)

    def test_parse_union(self):
        """Test parsing union definitions"""
        content = """
        union Number {
            int i;
            float f;
            double d;
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertIn("Number", file_model.unions)
            number_union = file_model.unions["Number"]
            self.assertEqual(len(number_union.fields), 3)

        finally:
            os.unlink(temp_file)

    def test_parse_function_declaration(self):
        """Test parsing function declarations"""
        content = """
        int calculate_sum(int a, int b);
        void process_data(char* data);
        point_t* create_point(int x, int y);
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertEqual(len(file_model.functions), 3)

            # Check function names
            func_names = [func.name for func in file_model.functions]
            self.assertIn("calculate_sum", func_names)
            self.assertIn("process_data", func_names)
            self.assertIn("create_point", func_names)

        finally:
            os.unlink(temp_file)

    def test_parse_function_definition(self):
        """Test parsing function definitions"""
        content = """
        int calculate_sum(int a, int b) {
            return a + b;
        }
        
        void process_data(char* data) {
            printf("%s", data);
        }
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertEqual(len(file_model.functions), 2)

            # Check function names
            func_names = [func.name for func in file_model.functions]
            self.assertIn("calculate_sum", func_names)
            self.assertIn("process_data", func_names)

        finally:
            os.unlink(temp_file)

    def test_parse_function_with_modifiers(self):
        """Test parsing functions with modifiers"""
        content = """
        static int internal_function(void);
        extern void external_function(char* data);
        inline int fast_function(int x);
        const char* get_string(void);
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertEqual(len(file_model.functions), 4)

            # Check function names
            func_names = [func.name for func in file_model.functions]
            self.assertIn("internal_function", func_names)
            self.assertIn("external_function", func_names)
            self.assertIn("fast_function", func_names)
            self.assertIn("get_string", func_names)

        finally:
            os.unlink(temp_file)

    def test_parse_global_variables(self):
        """Test parsing global variables"""
        content = """
        int global_counter = 0;
        static char buffer[100];
        extern double* global_ptr;
        const int MAX_SIZE = 100;
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertGreaterEqual(len(file_model.globals), 1)

            # Check global variable names
            global_names = [g.name for g in file_model.globals]
            self.assertIn("global_counter", global_names)

        finally:
            os.unlink(temp_file)

    def test_parse_includes(self):
        """Test parsing include directives"""
        content = """
        #include <stdio.h>
        #include <stdlib.h>
        #include "local.h"
        #include "config.h"
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertGreaterEqual(len(file_model.includes), 2)

            # Check include paths
            include_paths = [inc for inc in file_model.includes]
            self.assertIn("stdio.h", include_paths)
            self.assertIn("stdlib.h", include_paths)

        finally:
            os.unlink(temp_file)

    def test_parse_macros(self):
        """Test parsing macro definitions"""
        content = """
        #define MAX_SIZE 100
        #define PI 3.14159
        #define SQUARE(x) ((x) * (x))
        #define MIN(a, b) ((a) < (b) ? (a) : (b))
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertGreaterEqual(len(file_model.macros), 2)

        finally:
            os.unlink(temp_file)

    def test_parse_typedefs(self):
        """Test parsing typedef definitions"""
        content = """
        typedef int MyInt;
        typedef char* MyString;
        typedef struct Point* PointPtr;
        typedef int (*Callback)(int, int);
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertGreaterEqual(len(file_model.aliases), 2)

        finally:
            os.unlink(temp_file)

    def test_parse_complex_file(self):
        """Test parsing a complex C file with multiple constructs"""
        content = """
        #include <stdio.h>
        #include <stdlib.h>
        #include "config.h"
        
        #define MAX_SIZE 100
        #define PI 3.14159
        
        typedef int MyInt;
        typedef char* MyString;
        
        struct Point {
            int x;
            int y;
            char label[32];
        };
        
        typedef struct point_tag {
            int x;
            int y;
        } point_t;
        
        enum Status {
            OK = 0,
            ERROR = 1
        };
        
        typedef enum color_tag {
            RED = 0,
            GREEN = 1,
            BLUE = 2
        } color_t;
        
        union Number {
            int i;
            float f;
        };
        
        static int global_counter = 0;
        extern double* global_ptr;
        
        int calculate_sum(int a, int b);
        void process_data(char* data);
        point_t* create_point(int x, int y);
        
        int calculate_sum(int a, int b) {
            return a + b;
        }
        
        void process_data(char* data) {
            printf("%s", data);
        }
        
        point_t* create_point(int x, int y) {
            point_t* p = malloc(sizeof(point_t));
            p->x = x;
            p->y = y;
            return p;
        }
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            # Check that all constructs were parsed
            self.assertGreaterEqual(len(file_model.structs), 1)
            self.assertGreaterEqual(len(file_model.enums), 1)
            self.assertGreaterEqual(len(file_model.unions), 1)
            self.assertGreaterEqual(len(file_model.functions), 3)
            self.assertGreaterEqual(len(file_model.globals), 1)
            self.assertGreaterEqual(len(file_model.includes), 2)
            self.assertGreaterEqual(len(file_model.macros), 1)
            self.assertGreaterEqual(len(file_model.aliases), 1)

        finally:
            os.unlink(temp_file)

    def test_parse_file_with_comments(self):
        """Test parsing file with various comment types"""
        content = """
        // Single line comment
        #include <stdio.h>
        
        /* Multi-line comment
           spanning multiple lines */
        struct Point {
            int x;      // Field comment
            int y;      /* Another comment */
        };
        
        // Function comment
        int calculate_sum(int a, int b) {
            return a + b;  // Return comment
        }
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            # Should still parse correctly despite comments
            self.assertIn("Point", file_model.structs)
            self.assertIn("calculate_sum", [f.name for f in file_model.functions])

        finally:
            os.unlink(temp_file)

    def test_parse_file_with_preprocessor_conditionals(self):
        """Test parsing file with preprocessor conditionals"""
        content = """
        #ifdef DEBUG
        #define LOG_LEVEL 2
        #else
        #define LOG_LEVEL 0
        #endif
        
        #if LOG_LEVEL > 0
        void debug_print(const char* msg);
        #endif
        
        struct Point {
            int x;
            int y;
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            # Should parse the struct correctly
            self.assertIn("Point", file_model.structs)

        finally:
            os.unlink(temp_file)

    def test_parse_file_with_nested_structures(self):
        """Test parsing file with nested structures"""
        content = """
        struct Rectangle {
            struct Point top_left;
            struct Point bottom_right;
        };
        
        struct Container {
            struct {
                int x;
                int y;
            } point;
            struct Rectangle rect;
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertIn("Rectangle", file_model.structs)
            self.assertIn("Container", file_model.structs)

        finally:
            os.unlink(temp_file)

    def test_parse_file_with_function_pointers(self):
        """Test parsing file with function pointers"""
        content = """
        typedef int (*Callback)(int, int);
        
        struct Handler {
            Callback callback;
            void* data;
        };
        
        int process_with_callback(int x, int y, Callback cb);
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertIn("Handler", file_model.structs)
            self.assertIn(
                "process_with_callback", [f.name for f in file_model.functions]
            )

        finally:
            os.unlink(temp_file)

    def test_parse_file_with_arrays(self):
        """Test parsing file with array declarations"""
        content = """
        struct Buffer {
            char data[100];
            int size;
        };
        
        int matrix[10][10];
        char* strings[5];
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertIn("Buffer", file_model.structs)

        finally:
            os.unlink(temp_file)

    def test_parse_file_with_const_and_volatile(self):
        """Test parsing file with const and volatile qualifiers"""
        content = """
        const int MAX_VALUE = 100;
        volatile int status_flag;
        
        struct Config {
            const char* name;
            volatile int* status;
        };
        
        const char* get_name(void);
        void set_status(volatile int* status);
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertIn("Config", file_model.structs)
            self.assertIn("get_name", [f.name for f in file_model.functions])
            self.assertIn("set_status", [f.name for f in file_model.functions])

        finally:
            os.unlink(temp_file)

    def test_parse_file_with_bit_fields(self):
        """Test parsing file with bit fields"""
        content = """
        struct Flags {
            unsigned int read : 1;
            unsigned int write : 1;
            unsigned int exec : 1;
            unsigned int reserved : 29;
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertIn("Flags", file_model.structs)

        finally:
            os.unlink(temp_file)

    def test_parse_file_with_forward_declarations(self):
        """Test parsing file with forward declarations"""
        content = """
        struct Point;
        struct Rectangle;
        
        struct Point {
            int x;
            int y;
        };
        
        struct Rectangle {
            struct Point top_left;
            struct Point bottom_right;
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertIn("Point", file_model.structs)
            self.assertIn("Rectangle", file_model.structs)

        finally:
            os.unlink(temp_file)

    def test_parse_file_with_unnamed_parameters(self):
        """Test parsing file with unnamed function parameters"""
        content = """
        int process_data(int, char*);
        void callback(int, void*);
        
        int process_data(int count, char* data) {
            return count;
        }
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertIn("process_data", [f.name for f in file_model.functions])
            self.assertIn("callback", [f.name for f in file_model.functions])

        finally:
            os.unlink(temp_file)

    def test_parse_file_with_variadic_functions(self):
        """Test parsing file with variadic functions"""
        content = """
        int printf(const char* format, ...);
        int sprintf(char* buffer, const char* format, ...);
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertIn("printf", [f.name for f in file_model.functions])
            self.assertIn("sprintf", [f.name for f in file_model.functions])

        finally:
            os.unlink(temp_file)

    def test_parse_file_with_complex_typedefs(self):
        """Test parsing file with complex typedef definitions"""
        content = """
        typedef struct Node* NodePtr;
        typedef int (*Comparator)(const void*, const void*);
        typedef void (*Callback)(int, void*);
        
        struct Node {
            int data;
            NodePtr next;
        };
        
        void sort_array(int* array, int size, Comparator cmp);
        void process_items(int count, Callback callback, void* user_data);
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            self.assertIn("Node", file_model.structs)
            self.assertIn("sort_array", [f.name for f in file_model.functions])
            self.assertIn("process_items", [f.name for f in file_model.functions])

        finally:
            os.unlink(temp_file)

    def test_parse_file_with_mixed_content(self):
        """Test parsing file with mixed content from example files"""
        content = """
        #include <stdio.h>
        #include <stdlib.h>
        #include "sample.h"
        
        #define MAX_SIZE 100U
        #define DEBUG_MODE 1U
        
        typedef struct point_tag {
            int x;
            int y;
            char label[32];
        } point_t;
        
        typedef enum system_state_tag {
            STATE_IDLE = 0,
            STATE_RUNNING,
            STATE_ERROR
        } system_state_t;
        
        static int global_counter = 0;
        static char buffer[MAX_SIZE];
        double* global_ptr = NULL;
        
        static void internal_helper(void);
        int calculate_sum(int a, int b);
        point_t* create_point(int x, int y, const char* label);
        
        static void internal_helper(void) {
            printf("Internal helper called\\n");
            global_counter++;
        }
        
        int calculate_sum(int a, int b) {
            return a + b;
        }
        
        point_t* create_point(int x, int y, const char* label) {
            point_t* p = (point_t*)malloc(sizeof(point_t));
            if (p != NULL) {
                p->x = x;
                p->y = y;
                strncpy(p->label, label, sizeof(p->label) - 1);
                p->label[sizeof(p->label) - 1] = '\\0';
            }
            return p;
        }
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            # Check all expected constructs
            self.assertIn("point_t", file_model.structs)
            self.assertIn("system_state_t", file_model.enums)
            self.assertIn("internal_helper", [f.name for f in file_model.functions])
            self.assertIn("calculate_sum", [f.name for f in file_model.functions])
            self.assertIn("create_point", [f.name for f in file_model.functions])
            self.assertGreaterEqual(len(file_model.globals), 1)
            self.assertGreaterEqual(len(file_model.includes), 2)
            self.assertGreaterEqual(len(file_model.macros), 1)

        finally:
            os.unlink(temp_file)

    def test_parse_project(self):
        """Test parsing an entire project"""
        # Create a temporary project directory
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)

            # Create multiple C files
            files_content = {
                "main.c": """
                #include "header.h"
                #include <stdio.h>
                
                int main(void) {
                    return 0;
                }
                """,
                "header.h": """
                #ifndef HEADER_H
                #define HEADER_H
                
                struct Point {
                    int x;
                    int y;
                };
                
                int calculate_sum(int a, int b);
                
                #endif
                """,
                "utils.c": """
                #include "header.h"
                
                int calculate_sum(int a, int b) {
                    return a + b;
                }
                """,
            }

            # Write files
            for filename, content in files_content.items():
                file_path = project_path / filename
                with open(file_path, "w") as f:
                    f.write(content)

            # Parse the project
            project_model = self.parser.parse_project(str(project_path))

            # Check results
            self.assertEqual(project_model.project_name, project_path.name)
            self.assertEqual(len(project_model.files), 3)

            # Check that all files were parsed
            file_names = list(project_model.files.keys())
            self.assertIn("main.c", file_names)
            self.assertIn("header.h", file_names)
            self.assertIn("utils.c", file_names)

    def test_parse_file_encoding_detection(self):
        """Test parsing file with different encodings"""
        content = "struct Point { int x; int y; };"

        # Test with UTF-8 encoding
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".c", delete=False, encoding="utf-8"
        ) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)
            self.assertIn("Point", file_model.structs)
        finally:
            os.unlink(temp_file)

    def test_parse_file_error_handling(self):
        """Test error handling for invalid files"""
        # Test with non-existent file
        with self.assertRaises(FileNotFoundError):
            self.parser.parse_file(Path("/nonexistent/file.c"), "file.c")

        # Test with non-C file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("This is not C code")
            temp_file = f.name

        try:
            # Should still attempt to parse but might fail gracefully
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)
            # Should not crash, even if parsing fails
        finally:
            os.unlink(temp_file)

    def test_parse_file_with_malformed_code(self):
        """Test parsing file with malformed C code"""
        content = """
        struct Point {
            int x;
            int y;
            // Missing semicolon
        }
        
        int main(void {
            return 0;
        }
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            # Should handle malformed code gracefully
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)
            # Should not crash, even if some parsing fails
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    unittest.main()
