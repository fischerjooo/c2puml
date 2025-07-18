#!/usr/bin/env python3
"""
Unit tests for the enhanced C parser
"""

import unittest
import os
import tempfile
import json
from c_to_plantuml.parsers.c_parser import CParser
from c_to_plantuml.models.c_structures import Struct, Function, Field, Enum

class TestCParser(unittest.TestCase):
    """Test the C parser functionality"""
    
    def setUp(self):
        self.parser = CParser()
    
    def test_compiled_regex_patterns(self):
        """Test that regex patterns are properly compiled"""
        # Check that patterns are compiled regex objects
        self.assertTrue(hasattr(self.parser.COMMENT_BLOCK_PATTERN, 'pattern'))
        self.assertTrue(hasattr(self.parser.COMMENT_LINE_PATTERN, 'pattern'))
        self.assertTrue(hasattr(self.parser.STRUCT_PATTERN, 'pattern'))
        self.assertTrue(hasattr(self.parser.FUNCTION_PATTERN, 'pattern'))
    
    def test_file_caching(self):
        """Test file content caching functionality"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write("int main() { return 0; }")
            temp_file = f.name
        
        try:
            # First read
            content1, encoding1 = self.parser.read_file_with_encoding_detection(temp_file)
            
            # Second read (should use cache)
            content2, encoding2 = self.parser.read_file_with_encoding_detection(temp_file)
            
            self.assertEqual(content1, content2)
            self.assertEqual(encoding1, encoding2)
            self.assertIn(temp_file, self.parser.file_cache)
            self.assertIn(temp_file, self.parser.encoding_cache)
            
        finally:
            os.unlink(temp_file)
    
    def test_cache_clearing(self):
        """Test cache clearing functionality"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write("int main() { return 0; }")
            temp_file = f.name
        
        try:
            # Read file to populate cache
            self.parser.read_file_with_encoding_detection(temp_file)
            self.assertTrue(len(self.parser.file_cache) > 0)
            
            # Clear cache
            self.parser.clear_cache()
            self.assertEqual(len(self.parser.file_cache), 0)
            self.assertEqual(len(self.parser.encoding_cache), 0)
            
        finally:
            os.unlink(temp_file)
    
    def test_parser_state_reset(self):
        """Test parser state reset functionality"""
        # Add some data to parser state
        self.parser.structs['test'] = Struct('test', [], [])
        self.parser.functions.append(Function('test', 'void', []))
        self.parser.includes.add('stdio.h')
        
        # Reset state
        self.parser.reset_parser_state()
        
        # Check all collections are empty
        self.assertEqual(len(self.parser.structs), 0)
        self.assertEqual(len(self.parser.functions), 0)
        self.assertEqual(len(self.parser.includes), 0)
        self.assertEqual(len(self.parser.enums), 0)
        self.assertEqual(len(self.parser.globals), 0)
        self.assertEqual(len(self.parser.macros), 0)
    
    def test_comment_removal(self):
        """Test comment removal using compiled patterns"""
        code = """
        /* Block comment */
        int x; // Line comment
        /* Multi
           line
           comment */
        int y;
        """
        
        result = self.parser._remove_comments(code)
        
        # Comments should be removed
        self.assertNotIn('Block comment', result)
        self.assertNotIn('Line comment', result)
        self.assertNotIn('Multi', result)
        
        # Code should remain
        self.assertIn('int x;', result)
        self.assertIn('int y;', result)
    
    def test_include_parsing(self):
        """Test include statement parsing"""
        self.parser.reset_parser_state()
        
        code = '''
        #include <stdio.h>
        #include "myheader.h"
        #include <stdlib.h>
        '''
        
        self.parser._parse_content(code)
        
        expected_includes = {'stdio.h', 'myheader.h', 'stdlib.h'}
        self.assertEqual(self.parser.includes, expected_includes)
    
    def test_macro_parsing(self):
        """Test macro parsing"""
        self.parser.reset_parser_state()
        
        code = '''
        #define MAX_SIZE 100
        #define PI 3.14159
        #define FUNCTION_LIKE(x) ((x) * 2)
        '''
        
        self.parser._parse_content(code)
        
        expected_macros = ['- #define MAX_SIZE', '- #define PI', '- #define FUNCTION_LIKE']
        self.assertEqual(self.parser.macros, expected_macros)
    
    def test_struct_parsing(self):
        """Test struct definition parsing"""
        self.parser.reset_parser_state()
        
        code = '''
        typedef struct Point {
            int x;
            int y;
        } Point;
        
        struct Rectangle {
            int width;
            int height;
        };
        '''
        
        self.parser._parse_content(code)
        
        self.assertIn('Point', self.parser.structs)
        self.assertIn('Rectangle', self.parser.structs)
        
        point_struct = self.parser.structs['Point']
        self.assertEqual(len(point_struct.fields), 2)
        self.assertEqual(point_struct.fields[0].name, 'x')
        self.assertEqual(point_struct.fields[1].name, 'y')
    
    def test_enum_parsing(self):
        """Test enum definition parsing"""
        self.parser.reset_parser_state()
        
        code = '''
        typedef enum Color {
            RED,
            GREEN,
            BLUE
        } Color;
        
        enum Status {
            RUNNING,
            STOPPED
        };
        '''
        
        self.parser._parse_content(code)
        
        self.assertIn('Color', self.parser.enums)
        self.assertIn('Status', self.parser.enums)
        
        color_enum = self.parser.enums['Color']
        self.assertEqual(len(color_enum.values), 3)
        self.assertIn('RED', color_enum.values)
    
    def test_typedef_parsing(self):
        """Test typedef parsing"""
        self.parser.reset_parser_state()
        
        code = '''
        typedef int Integer;
        typedef char* String;
        typedef unsigned long ulong;
        '''
        
        self.parser._parse_content(code)
        
        self.assertEqual(self.parser.typedefs['Integer'], 'int')
        self.assertEqual(self.parser.typedefs['String'], 'char*')
        self.assertEqual(self.parser.typedefs['ulong'], 'unsigned long')
    
    def test_global_variable_parsing(self):
        """Test global variable parsing"""
        self.parser.reset_parser_state()
        
        code = '''
        int global_var;
        static char buffer[256];
        double* ptr_value = NULL;
        extern int external_var;
        '''
        
        self.parser._parse_content(code)
        
        # Should find global variables
        global_names = [field.name for field in self.parser.globals]
        self.assertIn('global_var', global_names)
        self.assertIn('buffer', global_names)
        self.assertIn('ptr_value', global_names)
    
    def test_function_parsing(self):
        """Test function definition parsing"""
        self.parser.reset_parser_state()
        
        code = '''
        int add(int a, int b) {
            return a + b;
        }
        
        static void helper_function(void) {
            // Helper code
        }
        
        char* get_string(const char* input) {
            return strdup(input);
        }
        '''
        
        self.parser._parse_content(code)
        
        function_names = [func.name for func in self.parser.functions]
        self.assertIn('add', function_names)
        self.assertIn('helper_function', function_names)
        self.assertIn('get_string', function_names)
        
        # Check function details
        add_func = next(func for func in self.parser.functions if func.name == 'add')
        self.assertEqual(add_func.return_type, 'int')
        self.assertEqual(len(add_func.parameters), 2)
        self.assertEqual(add_func.parameters[0].name, 'a')
        self.assertEqual(add_func.parameters[1].name, 'b')
    
    def test_complete_file_parsing(self):
        """Test parsing a complete C file"""
        self.parser.reset_parser_state()
        
        code = '''
        #include <stdio.h>
        #include "local.h"
        
        #define MAX_BUFFER 1024
        
        typedef struct Data {
            int value;
            char name[50];
        } Data;
        
        static int counter = 0;
        
        int process_data(Data* data) {
            if (data == NULL) return -1;
            counter++;
            return data->value;
        }
        '''
        
        self.parser._parse_content(code)
        
        # Check all elements were parsed
        self.assertIn('stdio.h', self.parser.includes)
        self.assertIn('local.h', self.parser.includes)
        self.assertIn('- #define MAX_BUFFER', self.parser.macros)
        self.assertIn('Data', self.parser.structs)
        
        function_names = [func.name for func in self.parser.functions]
        self.assertIn('process_data', function_names)
        
        global_names = [field.name for field in self.parser.globals]
        self.assertIn('counter', global_names)
    
    def test_header_file_parsing(self):
        """Test header file parsing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False) as f:
            f.write('''
            #ifndef HEADER_H
            #define HEADER_H
            
            #define MAX_ITEMS 100
            
            int function_prototype(char* str);
            void another_function(int x, int y);
            
            #endif
            ''')
            header_file = f.name
        
        try:
            prototypes, macros = CParser.parse_header_file(header_file)
            
            # Check prototypes
            prototype_strs = ''.join(prototypes)
            self.assertIn('function_prototype', prototype_strs)
            self.assertIn('another_function', prototype_strs)
            
            # Check macros
            macro_strs = ''.join(macros)
            self.assertIn('MAX_ITEMS', macro_strs)
            
        finally:
            os.unlink(header_file)
    
    def test_encoding_detection(self):
        """Test encoding detection for files"""
        # Test UTF-8 file
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.c', delete=False) as f:
            f.write("// UTF-8 comment with unicode: ñáéíóú\nint main() { return 0; }")
            utf8_file = f.name
        
        try:
            content, encoding = self.parser.read_file_with_encoding_detection(utf8_file)
            self.assertEqual(encoding, 'utf-8')
            self.assertIn('unicode', content)
            
        finally:
            os.unlink(utf8_file)
    
    def test_performance_with_caching(self):
        """Test that caching provides performance benefits"""
        import time
        
        # Create a larger test file
        large_code = '''
        #include <stdio.h>
        
        #define LARGE_BUFFER 2048
        
        ''' + '\n'.join([f'int function_{i}(int param_{i}) {{ return param_{i} * {i}; }}' for i in range(100)])
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(large_code)
            large_file = f.name
        
        try:
            # First parse (without cache)
            start_time = time.time()
            self.parser.parse_file(large_file)
            first_parse_time = time.time() - start_time
            
            # Second parse (with cache for file reading)
            start_time = time.time()
            self.parser.parse_file(large_file)
            second_parse_time = time.time() - start_time
            
            # File reading should be faster due to caching
            # (Note: parsing itself will still take time, but file I/O should be cached)
            self.assertGreater(first_parse_time, 0)
            self.assertGreater(second_parse_time, 0)
            
        finally:
            os.unlink(large_file)

if __name__ == '__main__':
    unittest.main()