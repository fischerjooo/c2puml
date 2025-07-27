#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'c_to_plantuml'))

from c_to_plantuml.parser_tokenizer import CTokenizer, TokenType

def debug_tokenization():
    tokenizer = CTokenizer()
    
    # Test the problematic declaration
    content = '''
typedef struct {
    void (*callbacks[3])(int, char*);
} operation_set_t;
'''
    
    print("Tokenizing content:")
    print(content)
    print("\nTokens:")
    
    tokens = tokenizer.tokenize(content)
    for i, token in enumerate(tokens):
        print(f"{i:2d}: {token.type.name:15s} '{token.value}'")
    
    print("\nFiltered tokens (excluding whitespace and comments):")
    filtered_tokens = tokenizer.filter_tokens(tokens, exclude_types=[TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE])
    for i, token in enumerate(filtered_tokens):
        print(f"{i:2d}: {token.type.name:15s} '{token.value}'")

if __name__ == "__main__":
    debug_tokenization()