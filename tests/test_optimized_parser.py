#!/usr/bin/env python3
"""
Unit tests for the optimized C parser
"""

import unittest
import os
import sys
import tempfile
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from c_to_plantuml.parsers.optimized_c_parser import OptimizedCParser
from c_to_plantuml.models.c_structures import Field, Function, Struct, Enum

class TestOptimizedCParser(unittest.TestCase):
    """Test cases for the OptimizedCParser"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = OptimizedCParser()
        self.test_files_dir = Path(__file__).parent / "test_files"
        
    def test_file_caching(self):
        """Test file content caching functionality"""
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as tf:
            tf.write("int test = 42;")
            temp_path = tf.name
        
        try:
            # First read should cache the file
            content1, encoding1 = self.parser.read_file_with_encoding_detection(temp_path)
            self.assertEqual(content1, "int test = 42;")
            self.assertIn(temp_path, self.parser.file_cache)
            
            # Second read should use cache
            content2, encoding2 = self.parser.read_file_with_encoding_detection(temp_path)
            self.assertEqual(content1, content2)
            self.assertEqual(encoding1, encoding2)
            
        finally:
            os.unlink(temp_path)
    
    def test_regex_compilation(self):
        """Test that regex patterns are pre-compiled"""
        # Check that patterns are compiled regex objects
        self.assertTrue(hasattr(self.parser.COMMENT_BLOCK_PATTERN, 'pattern'))
        self.assertTrue(hasattr(self.parser.STRUCT_PATTERN, 'pattern'))
        self.assertTrue(hasattr(self.parser.FUNCTION_PATTERN, 'pattern'))
    
    def test_comment_removal(self):
        """Test comment removal using compiled patterns"""
        test_content = """
        /* This is a block comment */
        int main() {
            // This is a line comment
            return 0;
        }
        """
        
        # Remove comments
        content = self.parser.COMMENT_BLOCK_PATTERN.sub('', test_content)
        content = self.parser.COMMENT_LINE_PATTERN.sub('', content)
        
        # Check that comments are removed
        self.assertNotIn("block comment", content)
        self.assertNotIn("line comment", content)
        self.assertIn("int main()", content)
    
    def test_struct_parsing(self):
        """Test struct parsing functionality"""
        test_content = """
        typedef struct point {
            int x;
            int y;
            char label[32];
        } point_t;
        
        struct simple_struct {
            float value;
            int *pointer;
        };
        """
        
        self.parser._parse_content(test_content)
        
        # Check that structs are parsed
        self.assertIn("point", self.parser.structs)
        self.assertIn("simple_struct", self.parser.structs)
        
        # Check point struct details
        point_struct = self.parser.structs["point"]
        self.assertEqual(len(point_struct.fields), 3)
        self.assertEqual(point_struct.typedef_name, "point_t")
        
        # Check field types
        field_names = [f.name for f in point_struct.fields]
        self.assertIn("x", field_names)
        self.assertIn("y", field_names)
        self.assertIn("label", field_names)
    
    def test_function_parsing(self):
        """Test function parsing functionality"""
        test_content = """
        static void helper_function(void);
        int calculate(int a, int b) {
            return a + b;
        }
        static void helper_function(void) {
            printf("Helper\\n");
        }
        """
        
        self.parser._parse_content(test_content)
        
        # Check that functions are parsed
        function_names = [f.name for f in self.parser.functions]
        self.assertIn("calculate", function_names)
        self.assertIn("helper_function", function_names)
        
        # Check function details
        calc_func = next(f for f in self.parser.functions if f.name == "calculate")
        self.assertEqual(calc_func.return_type, "int")
        self.assertEqual(len(calc_func.parameters), 2)
        self.assertFalse(calc_func.is_static)
        
        helper_func = next(f for f in self.parser.functions if f.name == "helper_function")
        self.assertTrue(helper_func.is_static)
    
    def test_macro_parsing(self):
        """Test macro parsing functionality"""
        test_content = """
        #define MAX_SIZE 100
        #define DEBUG_MODE 1
        #define CALC(x, y) ((x) + (y))
        """
        
        self.parser._parse_content(test_content)
        
        # Check that macros are parsed
        macro_names = [m.split()[2] for m in self.parser.macros]  # Extract macro names
        self.assertIn("MAX_SIZE", macro_names)
        self.assertIn("DEBUG_MODE", macro_names)
        self.assertIn("CALC", macro_names)
    
    def test_global_variable_parsing(self):
        """Test global variable parsing"""
        test_content = """
        int global_var = 42;
        static char buffer[256];
        double *pointer_var;
        """
        
        self.parser._parse_content(test_content)
        
        # Check that globals are parsed
        global_names = [g.name for g in self.parser.globals]
        self.assertIn("global_var", global_names)
        self.assertIn("buffer", global_names)
        self.assertIn("pointer_var", global_names)
        
        # Check static flag
        buffer_var = next(g for g in self.parser.globals if g.name == "buffer")
        self.assertTrue(getattr(buffer_var, 'is_static', False))
        
        global_var = next(g for g in self.parser.globals if g.name == "global_var")
        self.assertFalse(getattr(global_var, 'is_static', False))
    
    def test_enum_parsing(self):
        """Test enum parsing functionality"""
        test_content = """
        typedef enum {
            STATE_IDLE,
            STATE_RUNNING,
            STATE_ERROR = 99
        } state_t;
        """
        
        self.parser._parse_content(test_content)
        
        # Check that enum is parsed
        self.assertIn("anonymous", self.parser.enums)
        enum_obj = self.parser.enums["anonymous"]
        self.assertEqual(len(enum_obj.values), 3)
        self.assertIn("STATE_IDLE", enum_obj.values)
        self.assertIn("STATE_RUNNING", enum_obj.values)
        self.assertIn("STATE_ERROR", enum_obj.values)
    
    def test_sample_file_parsing(self):
        """Test parsing of the sample.c test file"""
        sample_file = self.test_files_dir / "sample.c"
        if not sample_file.exists():
            self.skipTest("sample.c test file not found")
        
        content, encoding = self.parser.parse_file(str(sample_file))
        
        # Check that content was read
        self.assertIsInstance(content, str)
        self.assertIn("utf-8", encoding.lower())
        
        # Check parsing results
        self.assertGreater(len(self.parser.functions), 0)
        self.assertGreater(len(self.parser.macros), 0)
        self.assertGreater(len(self.parser.includes), 0)
        
        # Check for specific elements
        function_names = [f.name for f in self.parser.functions]
        self.assertIn("calculate_sum", function_names)
        self.assertIn("create_point", function_names)
    
    def test_complex_file_parsing(self):
        """Test parsing of the complex_example.c test file"""
        complex_file = self.test_files_dir / "complex_example.c"
        if not complex_file.exists():
            self.skipTest("complex_example.c test file not found")
        
        content, encoding = self.parser.parse_file(str(complex_file))
        
        # Check parsing results
        self.assertGreater(len(self.parser.functions), 0)
        self.assertGreater(len(self.parser.macros), 0)
        
        # Check for complex structures
        function_names = [f.name for f in self.parser.functions]
        self.assertIn("create_entity", function_names)
        self.assertIn("register_event_handler", function_names)
    
    def test_header_file_parsing(self):
        """Test optimized header file parsing"""
        sample_header = self.test_files_dir / "sample.h"
        if not sample_header.exists():
            self.skipTest("sample.h test file not found")
        
        prototypes, macros = OptimizedCParser.parse_header_file_optimized(str(sample_header))
        
        # Check that prototypes and macros are found
        self.assertGreater(len(prototypes), 0)
        self.assertGreater(len(macros), 0)
        
        # Check for specific elements
        proto_text = ' '.join(prototypes)
        self.assertIn("calculate_sum", proto_text)
        
        macro_text = ' '.join(macros)
        self.assertIn("PI", macro_text)
    
    def test_cache_management(self):
        """Test cache clearing functionality"""
        # Add some entries to cache
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as tf:
            tf.write("int test = 42;")
            temp_path = tf.name
        
        try:
            self.parser.read_file_with_encoding_detection(temp_path)
            self.assertGreater(len(self.parser.file_cache), 0)
            
            # Clear cache
            self.parser.clear_cache()
            self.assertEqual(len(self.parser.file_cache), 0)
            self.assertEqual(len(self.parser.encoding_cache), 0)
            
        finally:
            os.unlink(temp_path)
    
    def test_parser_state_reset(self):
        """Test parser state reset functionality"""
        # Parse some content
        test_content = "int test() { return 42; }"
        self.parser._parse_content(test_content)
        
        # Check that state has data
        self.assertGreater(len(self.parser.functions), 0)
        
        # Reset state
        self.parser.reset_parser_state()
        
        # Check that state is cleared
        self.assertEqual(len(self.parser.functions), 0)
        self.assertEqual(len(self.parser.structs), 0)
        self.assertEqual(len(self.parser.macros), 0)

class TestPerformanceImprovements(unittest.TestCase):
    """Test cases for performance improvements"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = OptimizedCParser()
    
    def test_regex_compilation_performance(self):
        """Test that compiled regex patterns perform better"""
        import time
        
        test_content = """
        /* Comment 1 */ int func1() { return 1; }
        /* Comment 2 */ int func2() { return 2; }
        /* Comment 3 */ int func3() { return 3; }
        """ * 100  # Repeat to make performance difference noticeable
        
        # Time with compiled patterns
        start_time = time.perf_counter()
        content = self.parser.COMMENT_BLOCK_PATTERN.sub('', test_content)
        compiled_time = time.perf_counter() - start_time
        
        # Time with non-compiled patterns (for comparison)
        import re
        start_time = time.perf_counter()
        content = re.sub(r'/\*.*?\*/', '', test_content, flags=re.DOTALL)
        non_compiled_time = time.perf_counter() - start_time
        
        # Compiled should be faster or at least not significantly slower
        # (Small test content might not show significant difference)
        self.assertLessEqual(compiled_time, non_compiled_time * 1.1)

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)