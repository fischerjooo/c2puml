#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'c_to_plantuml'))

from c_to_plantuml.parser import CParser
from c_to_plantuml.parser_tokenizer import CTokenizer, TokenType, StructureFinder

def debug_full_parsing():
    parser = CParser()
    tokenizer = CTokenizer()
    
    # Test the exact declaration from complex.h
    content = '''
typedef struct {
    int count;
    math_operation_t operations[5];
    void (*callbacks[3])(int, char*);
} operation_set_t;
'''
    
    print("Testing full parsing pipeline:")
    print(content)
    
    # Step 1: Tokenize
    tokens = tokenizer.tokenize(content)
    filtered_tokens = tokenizer.filter_tokens(tokens, exclude_types=[TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE])
    
    print(f"\nStep 1: Tokenization complete. {len(tokens)} total tokens, {len(filtered_tokens)} filtered tokens")
    
    # Step 2: Find structures
    structure_finder = StructureFinder(filtered_tokens)
    struct_infos = structure_finder.find_structs()
    
    print(f"\nStep 2: Structure finding complete. Found {len(struct_infos)} structs")
    for i, (start_pos, end_pos, struct_name) in enumerate(struct_infos):
        print(f"  Struct {i}: '{struct_name}' at positions {start_pos}-{end_pos}")
    
    # Step 3: Parse structs
    structs = parser._parse_structs_with_tokenizer(tokens, structure_finder)
    
    print(f"\nStep 3: Struct parsing complete. Parsed {len(structs)} structs")
    for struct_name, struct in structs.items():
        print(f"  Struct '{struct_name}' with {len(struct.fields)} fields:")
        for field in struct.fields:
            print(f"    '{field.name}' : '{field.type}'")

if __name__ == "__main__":
    debug_full_parsing()