#!/usr/bin/env python3

from c_to_plantuml.parser import CParser
from c_to_plantuml.parser_tokenizer import CTokenizer, StructureFinder
from pathlib import Path

# Create test file
content = '''typedef struct {
    int x;
    int y;
} point_t;

typedef enum {
    RED,
    GREEN,
    BLUE
} color_t;

union Number {
    int i;
    float f;
    char c;
};
'''

with open('test_typedef.c', 'w') as f:
    f.write(content)

# Test tokenization and structure finding
tokenizer = CTokenizer()
tokens = tokenizer.tokenize(content)
filtered_tokens = tokenizer.filter_tokens(tokens)
finder = StructureFinder(filtered_tokens)

print("=== StructureFinder Results ===")
print("Structs found:", finder.find_structs())
print("Enums found:", finder.find_enums())
print("Unions found:", finder.find_unions())
print("Functions found:", finder.find_functions())

# Parse the file
parser = CParser()
file_model = parser.parse_file(Path('test_typedef.c'), 'test_typedef.c', '.')

print("\n=== Parser Results ===")
print("Structs:", list(file_model.structs.keys()))
print("Enums:", list(file_model.enums.keys()))
print("Typedefs:", file_model.typedefs)
print("Unions:", list(file_model.unions.keys()))

# Clean up
Path('test_typedef.c').unlink()