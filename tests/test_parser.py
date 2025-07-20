#!/usr/bin/env python3
"""
Unit tests for the C parser
"""

import unittest
import os
import tempfile
import json
from pathlib import Path
from c_to_plantuml.parser import CParser
from c_to_plantuml.models import Struct, Function, Field, Enum


class TestCParser(unittest.TestCase):
    """Test the C parser functionality"""
    
    def setUp(self):
        self.parser = CParser()
    
    def test_parse_simple_c_file(self):
        """Test parsing a simple C file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write("""
#include <stdio.h>

struct Person {
    char name[50];
    int age;
};

enum Status {
    OK,
    ERROR
};

int main() {
    return 0;
}

int global_var;
            """)
            temp_file = f.name
        
        try:
            # Parse the file
            file_model = self.parser.parse_file(Path(temp_file))
            
            # Check results
            self.assertIn('Person', file_model.structs)
            self.assertIn('Status', file_model.enums)
            self.assertEqual(len(file_model.functions), 1)
            self.assertEqual(file_model.functions[0].name, 'main')
            self.assertGreaterEqual(len(file_model.globals), 1)
            global_names = [g.name for g in file_model.globals]
            self.assertIn('global_var', global_names)
            
        finally:
            os.unlink(temp_file)
    
    def test_parse_structs(self):
        """Test parsing struct definitions"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write("""
struct Point {
    int x;
    int y;
};

struct Rectangle {
    int width;
    int height;
};
            """)
            temp_file = f.name
        
        try:
            file_model = self.parser.parse_file(Path(temp_file))
            
            self.assertIn('Point', file_model.structs)
            self.assertIn('Rectangle', file_model.structs)
            
            point_struct = file_model.structs['Point']
            self.assertEqual(len(point_struct.fields), 2)
            self.assertEqual(point_struct.fields[0].name, 'x')
            self.assertEqual(point_struct.fields[1].name, 'y')
            
        finally:
            os.unlink(temp_file)
    
    def test_parse_enums(self):
        """Test parsing enum definitions"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write("""
enum Color {
    RED,
    GREEN,
    BLUE
};

enum Status {
    RUNNING,
    STOPPED
};
            """)
            temp_file = f.name
        
        try:
            file_model = self.parser.parse_file(Path(temp_file))
            
            self.assertIn('Color', file_model.enums)
            self.assertIn('Status', file_model.enums)
            
            color_enum = file_model.enums['Color']
            self.assertEqual(len(color_enum.values), 3)
            self.assertIn('RED', color_enum.values)
            self.assertIn('GREEN', color_enum.values)
            self.assertIn('BLUE', color_enum.values)
            
        finally:
            os.unlink(temp_file)
    
    def test_parse_functions(self):
        """Test parsing function declarations"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write("""
int calculate(int a, int b) {
    return a + b;
}

void print_message(char* message) {
    printf("%s\\n", message);
}

float get_average(float* values, int count) {
    return 0.0f;
}
            """)
            temp_file = f.name
        
        try:
            file_model = self.parser.parse_file(Path(temp_file))
            
            self.assertEqual(len(file_model.functions), 3)
            function_names = [f.name for f in file_model.functions]
            self.assertIn('calculate', function_names)
            self.assertIn('print_message', function_names)
            self.assertIn('get_average', function_names)
            
        finally:
            os.unlink(temp_file)
    
    def test_parse_macros(self):
        """Test parsing macro definitions"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write("""
#define MAX_SIZE 100
#define PI 3.14159
#define VERSION "1.0.0"
#define MIN(a, b) ((a) < (b) ? (a) : (b))
            """)
            temp_file = f.name
        
        try:
            file_model = self.parser.parse_file(Path(temp_file))
            
            self.assertEqual(len(file_model.macros), 4)
            self.assertIn('MAX_SIZE', file_model.macros)
            self.assertIn('PI', file_model.macros)
            self.assertIn('VERSION', file_model.macros)
            self.assertIn('MIN', file_model.macros)
            
        finally:
            os.unlink(temp_file)
    
    def test_parse_includes(self):
        """Test parsing include statements"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write("""
#include <stdio.h>
#include <stdlib.h>
#include "myheader.h"
#include "config.h"
            """)
            temp_file = f.name
        
        try:
            file_model = self.parser.parse_file(Path(temp_file))
            
            self.assertEqual(len(file_model.includes), 4)
            self.assertIn('stdio.h', file_model.includes)
            self.assertIn('stdlib.h', file_model.includes)
            self.assertIn('myheader.h', file_model.includes)
            self.assertIn('config.h', file_model.includes)
            
        finally:
            os.unlink(temp_file)
    
    def test_parse_globals(self):
        """Test parsing global variables"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write("""
int global_int = 42;
float global_float = 3.14f;
char* global_string = "hello";
static int static_var = 10;
            """)
            temp_file = f.name
        
        try:
            file_model = self.parser.parse_file(Path(temp_file))
            
            self.assertGreaterEqual(len(file_model.globals), 3)
            global_names = [g.name for g in file_model.globals]
            self.assertIn('global_int', global_names)
            self.assertIn('global_float', global_names)
            self.assertIn('global_string', global_names)
            
        finally:
            os.unlink(temp_file)
    
    def test_parse_typedefs(self):
        """Test parsing typedef declarations"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write("""
typedef int Integer;
typedef char* String;
typedef void (*Callback)(int);
typedef struct {
    int x;
    int y;
} Point;
            """)
            temp_file = f.name
        
        try:
            file_model = self.parser.parse_file(Path(temp_file))
            
            self.assertGreaterEqual(len(file_model.typedefs), 3)
            self.assertIn('Integer', file_model.typedefs)
            self.assertIn('String', file_model.typedefs)
            self.assertIn('Callback', file_model.typedefs)
            
        finally:
            os.unlink(temp_file)
    
    def test_encoding_detection(self):
        """Test encoding detection and handling"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False, encoding='utf-8') as f:
            f.write("// UTF-8 comment with émojis 🚀\nint main() { return 0; }")
            temp_file = f.name
        
        try:
            file_model = self.parser.parse_file(Path(temp_file))
            self.assertEqual(file_model.encoding_used, "utf-8")
            self.assertEqual(len(file_model.functions), 1)
            
        finally:
            os.unlink(temp_file)
    
    def test_complete_file_parsing(self):
        """Test parsing a complete C file with all elements"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write("""
#include <stdio.h>
#include <stdlib.h>
#include "config.h"

#define MAX_SIZE 100
#define DEBUG_MODE 1

typedef int Integer;
typedef char* String;

struct Person {
    char name[50];
    int age;
    float height;
};

struct Config {
    int max_users;
    int timeout;
    String server_name;
};

enum Status {
    OK,
    ERROR,
    PENDING
};

int global_var = 42;
String global_string = "test";

int main() {
    printf("Hello, World!\\n");
    return 0;
}

void process_data(void* data) {
    // Process data
}

float calculate(float a, float b) {
    return a + b;
}
            """)
            temp_file = f.name
        
        try:
            file_model = self.parser.parse_file(Path(temp_file))
            
            # Verify all elements are parsed
            self.assertEqual(len(file_model.includes), 3)
            self.assertEqual(len(file_model.macros), 2)
            self.assertEqual(len(file_model.typedefs), 2)
            self.assertEqual(len(file_model.structs), 2)
            self.assertEqual(len(file_model.enums), 1)
            self.assertEqual(len(file_model.functions), 3)
            self.assertGreaterEqual(len(file_model.globals), 2)
            
        finally:
            os.unlink(temp_file)