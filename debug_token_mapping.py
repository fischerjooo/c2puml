#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'c_to_plantuml'))

from c_to_plantuml.parser import CParser
from c_to_plantuml.parser_tokenizer import CTokenizer, TokenType, StructureFinder

def debug_token_mapping():
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
    
    print("Testing token position mapping:")
    print(content)
    
    # Step 1: Tokenize
    tokens = tokenizer.tokenize(content)
    filtered_tokens = tokenizer.filter_tokens(tokens, exclude_types=[TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE])
    
    print(f"\nAll tokens ({len(tokens)}):")
    for i, token in enumerate(tokens):
        print(f"{i:2d}: {token.type.name:15s} '{token.value}' (line {token.line}, col {token.column})")
    
    print(f"\nFiltered tokens ({len(filtered_tokens)}):")
    for i, token in enumerate(filtered_tokens):
        print(f"{i:2d}: {token.type.name:15s} '{token.value}' (line {token.line}, col {token.column})")
    
    # Step 2: Find structures
    structure_finder = StructureFinder(filtered_tokens)
    struct_infos = structure_finder.find_structs()
    
    print(f"\nStruct boundaries:")
    for i, (start_pos, end_pos, struct_name) in enumerate(struct_infos):
        print(f"  Struct {i}: '{struct_name}' at filtered positions {start_pos}-{end_pos}")
        
        # Test token position mapping
        original_start = parser._find_original_token_pos(tokens, filtered_tokens, start_pos)
        original_end = parser._find_original_token_pos(tokens, filtered_tokens, end_pos)
        
        print(f"    Mapped to original positions: {original_start}-{original_end}")
        
        if original_start is not None and original_end is not None:
            print(f"    Original token range:")
            for j in range(original_start, min(original_end + 1, len(tokens))):
                print(f"      {j:2d}: {tokens[j].type.name:15s} '{tokens[j].value}'")

if __name__ == "__main__":
    debug_token_mapping()