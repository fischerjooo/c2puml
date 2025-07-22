#!/usr/bin/env python3

from c_to_plantuml.parser import CParser
from c_to_plantuml.parser_tokenizer import CTokenizer, StructureFinder
from pathlib import Path
from c_to_plantuml.parser_tokenizer import TokenType

# Create test file with the same content as the failing test
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

with open('test_complex_typedef.c', 'w') as f:
    f.write(content)

# Test tokenization and structure finding
tokenizer = CTokenizer()
tokens = tokenizer.tokenize(content)
filtered_tokens = tokenizer.filter_tokens(tokens)

print("=== Token Analysis ===")
print("All filtered tokens:")
for i, token in enumerate(filtered_tokens):
    print(f"  {i}: {token}")

# Find struct tokens
struct_tokens = [i for i, t in enumerate(filtered_tokens) if t.type == TokenType.STRUCT]
print(f"\nStruct tokens at positions: {struct_tokens}")

finder = StructureFinder(filtered_tokens)

print("=== StructureFinder Results ===")
print("Structs found:", finder.find_structs())
print("Enums found:", finder.find_enums())
print("Unions found:", finder.find_unions())

# Parse the file
parser = CParser()
file_model = parser.parse_file(Path('test_complex_typedef.c'), 'test_complex_typedef.c', '.')

print("\n=== Parser Results ===")
print("Structs:", list(file_model.structs.keys()))
print("Typedefs:", file_model.typedefs)
print("Functions:", [f.name for f in file_model.functions])

# Clean up
Path('test_complex_typedef.c').unlink()