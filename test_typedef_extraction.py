#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'example'))

from assertions import PUMLValidator

def test_typedef_extraction():
    validator = PUMLValidator()
    
    # Test content with various typedef patterns
    test_content = '''
typedef uint32_t MyLen;
typedef int32_t MyInt;
typedef char * MyString;

typedef struct MyBuffer_tag {
    MyLen length;
    MyString data;
} MyBuffer;

typedef int (*MyCallback)(MyBuffer * buffer);

typedef struct MyComplexStruct_tag {
    MyLen id;
    MyString name;
    MyCallback callback;
    log_level_t log_level;
} MyComplex;

typedef MyComplex * MyComplexPtr;
typedef MyComplexPtr MyComplexArray[10];
'''
    
    typedefs = validator.extract_typedefs(test_content)
    print('Extracted typedefs:')
    for i, typedef in enumerate(typedefs, 1):
        print(f'{i}. {typedef}')
    
    # Check if expected typedefs are found
    expected_patterns = [
        'typedef uint32_t MyLen',
        'typedef int32_t MyInt', 
        'typedef char * MyString',
        'typedef struct MyBuffer_tag',
        'typedef int (*MyCallback)',
        'typedef struct MyComplexStruct_tag',
        'typedef MyComplex * MyComplexPtr',
        'typedef MyComplexPtr MyComplexArray'
    ]
    
    print('\nChecking expected patterns:')
    for pattern in expected_patterns:
        found = any(pattern in typedef for typedef in typedefs)
        status = "✅" if found else "❌"
        print(f'{status} {pattern}')

if __name__ == '__main__':
    test_typedef_extraction()