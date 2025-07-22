#!/usr/bin/env python3

import re

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

# Test the function
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

typedefs = extract_typedefs(test_content)
print('Extracted typedefs:')
for i, typedef in enumerate(typedefs, 1):
    print(f'{i}. {typedef}')

# Check expected patterns
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