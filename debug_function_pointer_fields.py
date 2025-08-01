#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from c2puml.core.parser_tokenizer import CTokenizer, TokenType

def test_function_pointer_field_parsing():
    # Test the specific case that's failing
    test_code = """
typedef struct {
    int count;
    math_operation_t operations[5];
    void (*callbacks[3])(int, char*);
} operation_set_t;
"""
    
    tokenizer = CTokenizer()
    tokens = tokenizer.tokenize(test_code)
    
    print("All tokens:")
    for i, token in enumerate(tokens):
        print(f"  {i}: {token}")
    
    # Find struct tokens
    for i, token in enumerate(tokens):
        if token.type == TokenType.STRUCT:
            print(f"\nFound struct at position {i}")
            
            # Find the opening brace
            brace_start = None
            for j in range(i + 1, len(tokens)):
                if tokens[j].type == TokenType.LBRACE:
                    brace_start = j
                    break
                elif tokens[j].type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                    break
            
            if brace_start is not None:
                print(f"Opening brace at position {brace_start}")
                
                # Find the closing brace
                brace_depth = 1
                brace_end = None
                for j in range(brace_start + 1, len(tokens)):
                    if tokens[j].type == TokenType.LBRACE:
                        brace_depth += 1
                    elif tokens[j].type == TokenType.RBRACE:
                        brace_depth -= 1
                        if brace_depth == 0:
                            brace_end = j
                            break
                
                if brace_end is not None:
                    print(f"Closing brace at position {brace_end}")
                    
                    # Extract field tokens
                    field_tokens = []
                    current_field = []
                    for j in range(brace_start + 1, brace_end):
                        if tokens[j].type == TokenType.SEMICOLON:
                            if current_field:
                                field_tokens.append(current_field)
                                current_field = []
                        else:
                            current_field.append(tokens[j])
                    
                    if current_field:
                        field_tokens.append(current_field)
                    
                    print(f"\nField tokens:")
                    for i, field in enumerate(field_tokens):
                        print(f"  Field {i}: {field}")
                        
                        # Check if this is a function pointer field
                        if len(field) >= 5:
                            # Look for pattern: type ( * name ) ( params )
                            for j in range(len(field) - 4):
                                if (
                                    field[j].type == TokenType.LPAREN
                                    and field[j + 1].type == TokenType.ASTERISK
                                    and field[j + 2].type == TokenType.IDENTIFIER
                                    and field[j + 3].type == TokenType.RPAREN
                                    and field[j + 4].type == TokenType.LPAREN
                                ):
                                    print(f"    Found function pointer pattern at position {j}")
                                    print(f"    Function name: {field[j + 2].value}")

if __name__ == "__main__":
    test_function_pointer_field_parsing()