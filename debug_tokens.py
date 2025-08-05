#!/usr/bin/env python3
"""
Debug script to see what tokens are generated for typedef struct
"""

from src.c2puml.core.parser_tokenizer import CTokenizer, TokenType

def debug_tokens():
    source_code = """
    typedef struct {
        struct {
            int nested_a1;
            struct {
                int deep_a1;
            } deep_struct_a1;
            struct {
                int deep_a2;
            } deep_struct_a2;
        } nested_struct_a;
        struct {
            int nested_a2;
        } nested_struct_a2;
    } complex_naming_test_t;
    """
    
    tokenizer = CTokenizer()
    tokens = tokenizer.tokenize(source_code)
    
    print("All tokens:")
    for i, token in enumerate(tokens):
        print(f"{i:3d}: {token}")
    
    print("\nLooking for typedef struct pattern:")
    for i, token in enumerate(tokens):
        if (token.type == TokenType.TYPEDEF and 
            i + 1 < len(tokens) and 
            tokens[i + 1].type == TokenType.STRUCT and
            i + 2 < len(tokens) and
            tokens[i + 2].type == TokenType.LBRACE):
            print(f"Found typedef struct at position {i}")
            print(f"  typedef: {tokens[i]}")
            print(f"  struct: {tokens[i + 1]}")
            print(f"  {{: {tokens[i + 2]}")
            break
    else:
        print("No typedef struct found!")
        
        # Let's look for any TYPEDEF or STRUCT tokens
        typedef_positions = [i for i, t in enumerate(tokens) if t.type == TokenType.TYPEDEF]
        struct_positions = [i for i, t in enumerate(tokens) if t.type == TokenType.STRUCT]
        lbrace_positions = [i for i, t in enumerate(tokens) if t.type == TokenType.LBRACE]
        
        print(f"TYPEDEF tokens at positions: {typedef_positions}")
        print(f"STRUCT tokens at positions: {struct_positions}")
        print(f"LBRACE tokens at positions: {lbrace_positions}")

if __name__ == "__main__":
    debug_tokens()