#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from c2puml.core.parser_tokenizer import CTokenizer, TokenType

def test_global_variable_parsing():
    # Test the specific case that's failing
    test_code = """
    math_operation_t global_math_ops[10];
    """
    
    tokenizer = CTokenizer()
    tokens = tokenizer.tokenize(test_code)
    
    print("All tokens:")
    for i, token in enumerate(tokens):
        print(f"  {i}: {token}")
    
    # Find the global variable declaration
    collected_tokens = []
    for token in tokens:
        if token.type not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
            collected_tokens.append(token)
    
    print(f"\nCollected tokens: {collected_tokens}")
    
    # Check if this is an array declaration
    bracket_idx = None
    for j in range(len(collected_tokens) - 1, -1, -1):
        if collected_tokens[j].type == TokenType.RBRACKET:
            bracket_idx = j
            break
    
    print(f"Bracket index: {bracket_idx}")
    
    if bracket_idx is not None:
        # Array declaration: find the identifier before the opening bracket
        for j in range(bracket_idx - 1, -1, -1):
            if collected_tokens[j].type == TokenType.LBRACKET:
                print(f"Opening bracket at position {j}")
                # Found opening bracket, look for identifier before it
                for k in range(j - 1, -1, -1):
                    if collected_tokens[k].type == TokenType.IDENTIFIER:
                        var_name = collected_tokens[k].value
                        type_tokens = collected_tokens[:k]
                        print(f"Variable name: {var_name}")
                        print(f"Type tokens: {type_tokens}")
                        
                        # Format array type properly
                        formatted_type = []
                        for idx, token in enumerate(type_tokens):
                            if idx > 0:
                                formatted_type.append(" " + token.value)
                            else:
                                formatted_type.append(token.value)
                        
                        # Add array brackets without spaces
                        array_size = collected_tokens[j + 1].value if j + 1 < bracket_idx else ""
                        var_type = "".join(formatted_type) + "[" + array_size + "]"
                        print(f"Formatted type: {var_type}")
                        break
                break

if __name__ == "__main__":
    test_global_variable_parsing()