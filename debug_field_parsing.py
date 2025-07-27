#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'c_to_plantuml'))

from c_to_plantuml.parser_tokenizer import CTokenizer, TokenType, find_struct_fields

def debug_field_parsing():
    tokenizer = CTokenizer()
    
    # Test the exact declaration from complex.h
    content = '''
typedef struct {
    int count;
    math_operation_t operations[5];
    void (*callbacks[3])(int, char*);
} operation_set_t;
'''
    
    print("Tokenizing content:")
    print(content)
    
    tokens = tokenizer.tokenize(content)
    filtered_tokens = tokenizer.filter_tokens(tokens, exclude_types=[TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE])
    
    print("\nFiltered tokens:")
    for i, token in enumerate(filtered_tokens):
        print(f"{i:2d}: {token.type.name:15s} '{token.value}'")
    
    # Find struct boundaries
    struct_start = None
    struct_end = None
    for i, token in enumerate(filtered_tokens):
        if token.type == TokenType.STRUCT and token.value == "struct":
            struct_start = i
        elif token.type == TokenType.LBRACE and struct_start is not None:
            # Find matching closing brace
            brace_count = 1
            for j in range(i + 1, len(filtered_tokens)):
                if filtered_tokens[j].type == TokenType.LBRACE:
                    brace_count += 1
                elif filtered_tokens[j].type == TokenType.RBRACE:
                    brace_count -= 1
                    if brace_count == 0:
                        struct_end = j
                        break
            break
    
    print(f"\nStruct boundaries: {struct_start} to {struct_end}")
    
    if struct_start is not None and struct_end is not None:
        # Extract field tokens
        field_tokens = filtered_tokens[struct_start+2:struct_end]  # Skip struct and {
        print(f"\nField tokens ({len(field_tokens)} tokens):")
        for i, token in enumerate(field_tokens):
            print(f"{i:2d}: {token.type.name:15s} '{token.value}'")
        
        # Call the actual field parsing function
        fields = find_struct_fields(filtered_tokens, struct_start, struct_end)
        print(f"\nParsed fields:")
        for name, field_type in fields:
            print(f"  '{name}' : '{field_type}'")

if __name__ == "__main__":
    debug_field_parsing()