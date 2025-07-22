#!/usr/bin/env python3

from c_to_plantuml.parser import CParser
from c_to_plantuml.parser_tokenizer import CTokenizer, StructureFinder
from pathlib import Path

# Create test file with the same content as the failing test
content = """
typedef struct point_tag {
    int x;
    int y;
} point_t;
"""

with open('test_field_count.c', 'w') as f:
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

# Parse the file
parser = CParser()
file_model = parser.parse_file(Path('test_field_count.c'), 'test_field_count.c', '.')

print("\n=== Parser Results ===")
print("Structs:", list(file_model.structs.keys()))
if 'point_t' in file_model.structs:
    point_struct = file_model.structs['point_t']
    print(f"point_t fields count: {len(point_struct.fields)}")
    print("point_t fields:")
    for i, field in enumerate(point_struct.fields):
        print(f"  {i}: {field.name} ({field.type})")
else:
    print("point_t not found in structs")

print("Typedefs:", file_model.typedefs)

# Clean up
Path('test_field_count.c').unlink()