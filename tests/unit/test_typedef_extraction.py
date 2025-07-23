#!/usr/bin/env python3
"""
Unit tests for typedef extraction functionality
"""

import re
import unittest


def extract_typedefs(content: str):
    """Extract all typedef statements from source file content."""
    typedefs = []
    
    # Pattern for simple typedefs: typedef type name;
    simple_pattern = r'typedef\s+[a-zA-Z_][a-zA-Z0-9_]*\s+\*?\s*[a-zA-Z_][a-zA-Z0-9_]*\s*(?:\[[^\]]*\])?\s*;'
    simple_matches = re.findall(simple_pattern, content)
    for match in simple_matches:
        typedefs.append(match.strip())
    
    # Pattern for function pointer typedefs
    func_ptr_pattern = r'typedef\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\(\s*\*\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\)\s*\([^)]*\)\s*;'
    func_matches = re.findall(func_ptr_pattern, content)
    for match in func_matches:
        typedefs.append(match.strip())
    
    # For complex typedefs (struct/enum/union), look for the pattern:
    # typedef struct/enum/union tag { ... } name;
    # We'll use a simpler approach that looks for the key parts
    
    # Look for typedef followed by struct/enum/union
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('typedef') and any(keyword in line for keyword in ['struct', 'enum', 'union']):
            # This is a complex typedef, extract the basic pattern
            # Look for: typedef struct/enum/union tag
            match = re.search(r'typedef\s+(struct|enum|union)\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
            if match:
                typedef_type = match.group(1)
                typedef_tag = match.group(2)
                typedefs.append(f"typedef {typedef_type} {typedef_tag}")
    
    return typedefs


class TestTypedefExtraction(unittest.TestCase):
    """Test typedef extraction functionality"""

    def test_simple_typedefs(self):
        """Test extraction of simple typedefs"""
        test_content = '''
        typedef uint32_t MyLen;
        typedef int32_t MyInt;
        typedef char * MyString;
        typedef MyComplex * MyComplexPtr;
        typedef MyComplexPtr MyComplexArray[10];
        '''
        
        typedefs = extract_typedefs(test_content)
        
        expected_patterns = [
            'typedef uint32_t MyLen',
            'typedef int32_t MyInt', 
            'typedef char * MyString',
            'typedef MyComplex * MyComplexPtr',
            'typedef MyComplexPtr MyComplexArray'
        ]
        
        for pattern in expected_patterns:
            found = any(pattern in typedef for typedef in typedefs)
            self.assertTrue(found, f"Expected pattern '{pattern}' not found in extracted typedefs")

    def test_function_pointer_typedefs(self):
        """Test extraction of function pointer typedefs"""
        test_content = '''
        typedef int (*MyCallback)(MyBuffer * buffer);
        typedef void (*log_callback_t)(log_level_t level, const char * message);
        typedef int (*complex_callback)(int a, int b, char * str);
        '''
        
        typedefs = extract_typedefs(test_content)
        
        expected_patterns = [
            'typedef int (*MyCallback)',
            'typedef void (*log_callback_t)',
            'typedef int (*complex_callback)'
        ]
        
        for pattern in expected_patterns:
            found = any(pattern in typedef for typedef in typedefs)
            self.assertTrue(found, f"Expected pattern '{pattern}' not found in extracted typedefs")

    def test_struct_typedefs(self):
        """Test extraction of struct typedefs"""
        test_content = '''
        typedef struct MyBuffer_tag {
            MyLen length;
            MyString data;
        } MyBuffer;
        
        typedef struct MyComplexStruct_tag {
            MyLen id;
            MyString name;
            MyCallback callback;
            log_level_t log_level;
        } MyComplex;
        
        typedef struct point_tag {
            int x;
            int y;
        } point_t;
        '''
        
        typedefs = extract_typedefs(test_content)
        
        expected_patterns = [
            'typedef struct MyBuffer_tag',
            'typedef struct MyComplexStruct_tag',
            'typedef struct point_tag'
        ]
        
        for pattern in expected_patterns:
            found = any(pattern in typedef for typedef in typedefs)
            self.assertTrue(found, f"Expected pattern '{pattern}' not found in extracted typedefs")

    def test_enum_typedefs(self):
        """Test extraction of enum typedefs"""
        test_content = '''
        typedef enum Color_tag {
            COLOR_RED,
            COLOR_GREEN,
            COLOR_BLUE
        } Color_t;
        
        typedef enum log_level_tag {
            LOG_DEBUG,
            LOG_INFO,
            LOG_WARN,
            LOG_ERROR
        } log_level_t;
        
        typedef enum GlobalStatus GlobalStatus_t;
        '''
        
        typedefs = extract_typedefs(test_content)
        
        expected_patterns = [
            'typedef enum Color_tag',
            'typedef enum log_level_tag',
            'typedef enum GlobalStatus'
        ]
        
        for pattern in expected_patterns:
            found = any(pattern in typedef for typedef in typedefs)
            self.assertTrue(found, f"Expected pattern '{pattern}' not found in extracted typedefs")

    def test_union_typedefs(self):
        """Test extraction of union typedefs"""
        test_content = '''
        typedef union Number_tag {
            int i;
            float f;
        } Number_t;
        
        typedef union NamedUnion_tag {
            char c;
            int i;
        } NamedUnion_t;
        '''
        
        typedefs = extract_typedefs(test_content)
        
        expected_patterns = [
            'typedef union Number_tag',
            'typedef union NamedUnion_tag'
        ]
        
        for pattern in expected_patterns:
            found = any(pattern in typedef for typedef in typedefs)
            self.assertTrue(found, f"Expected pattern '{pattern}' not found in extracted typedefs")

    def test_comprehensive_typedef_extraction(self):
        """Test comprehensive typedef extraction with all types"""
        test_content = '''
        // Simple typedefs
        typedef uint32_t MyLen;
        typedef int32_t MyInt;
        typedef char * MyString;
        
        // Struct typedefs
        typedef struct MyBuffer_tag {
            MyLen length;
            MyString data;
        } MyBuffer;
        
        typedef struct MyComplexStruct_tag {
            MyLen id;
            MyString name;
            MyCallback callback;
            log_level_t log_level;
        } MyComplex;
        
        // Function pointer typedefs
        typedef int (*MyCallback)(MyBuffer * buffer);
        
        // Pointer typedefs
        typedef MyComplex * MyComplexPtr;
        typedef MyComplexPtr MyComplexArray[10];
        
        // Enum typedefs
        typedef enum Color_tag {
            COLOR_RED,
            COLOR_GREEN,
            COLOR_BLUE
        } Color_t;
        
        // Union typedefs
        typedef union Number_tag {
            int i;
            float f;
        } Number_t;
        '''
        
        typedefs = extract_typedefs(test_content)
        
        expected_patterns = [
            'typedef uint32_t MyLen',
            'typedef int32_t MyInt', 
            'typedef char * MyString',
            'typedef struct MyBuffer_tag',
            'typedef int (*MyCallback)',
            'typedef struct MyComplexStruct_tag',
            'typedef MyComplex * MyComplexPtr',
            'typedef MyComplexPtr MyComplexArray',
            'typedef enum Color_tag',
            'typedef union Number_tag'
        ]
        
        print(f"\nExtracted {len(typedefs)} typedefs:")
        for i, typedef in enumerate(typedefs, 1):
            print(f'{i}. {typedef}')
        
        print('\nChecking expected patterns:')
        for pattern in expected_patterns:
            found = any(pattern in typedef for typedef in typedefs)
            status = "✅" if found else "❌"
            print(f'{status} {pattern}')
            self.assertTrue(found, f"Expected pattern '{pattern}' not found in extracted typedefs")

    def test_empty_content(self):
        """Test extraction with empty content"""
        typedefs = extract_typedefs("")
        self.assertEqual(typedefs, [])

    def test_no_typedefs_content(self):
        """Test extraction with content that has no typedefs"""
        test_content = '''
        int main() {
            return 0;
        }
        
        struct Point {
            int x;
            int y;
        };
        '''
        
        typedefs = extract_typedefs(test_content)
        self.assertEqual(typedefs, [])

    def test_comments_and_whitespace(self):
        """Test extraction with comments and whitespace"""
        test_content = '''
        // This is a comment
        typedef uint32_t MyLen;  // Another comment
        
        /* Multi-line comment
           about typedefs */
        typedef int32_t MyInt;
        
        typedef char * MyString; /* Inline comment */
        '''
        
        typedefs = extract_typedefs(test_content)
        
        expected_patterns = [
            'typedef uint32_t MyLen',
            'typedef int32_t MyInt', 
            'typedef char * MyString'
        ]
        
        for pattern in expected_patterns:
            found = any(pattern in typedef for typedef in typedefs)
            self.assertTrue(found, f"Expected pattern '{pattern}' not found in extracted typedefs")


if __name__ == '__main__':
    unittest.main()