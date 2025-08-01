#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from c2puml.core.parser_tokenizer import CTokenizer, TokenType

def test_function_parameter_parsing():
    # Test the specific case that's failing
    test_code = """
    int main(int argc, char* argv[]) {
        return 0;
    }
    """
    
    tokenizer = CTokenizer()
    tokens = tokenizer.tokenize(test_code)
    
    print("All tokens:")
    for i, token in enumerate(tokens):
        print(f"  {i}: {token}")
    
    # Find function tokens
    for i, token in enumerate(tokens):
        if token.type == TokenType.IDENTIFIER and token.value == "main":
            print(f"\nFound function 'main' at position {i}")
            
            # Find the opening parenthesis
            paren_start = None
            for j in range(i + 1, len(tokens)):
                if tokens[j].type == TokenType.LPAREN:
                    paren_start = j
                    break
                elif tokens[j].type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                    break
            
            if paren_start is not None:
                print(f"Opening parenthesis at position {paren_start}")
                
                # Find the closing parenthesis
                paren_depth = 1
                paren_end = None
                for j in range(paren_start + 1, len(tokens)):
                    if tokens[j].type == TokenType.LPAREN:
                        paren_depth += 1
                    elif tokens[j].type == TokenType.RPAREN:
                        paren_depth -= 1
                        if paren_depth == 0:
                            paren_end = j
                            break
                
                if paren_end is not None:
                    print(f"Closing parenthesis at position {paren_end}")
                    
                    # Extract parameter tokens
                    param_tokens = []
                    for j in range(paren_start + 1, paren_end):
                        if tokens[j].type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                            param_tokens.append(tokens[j])
                    
                    print(f"\nParameter tokens: {param_tokens}")
                    
                    # Split by commas
                    current_param = []
                    all_params = []
                    for token in param_tokens:
                        if token.type == TokenType.COMMA:
                            if current_param:
                                all_params.append(current_param)
                                current_param = []
                        else:
                            current_param.append(token)
                    
                    if current_param:
                        all_params.append(current_param)
                    
                    print(f"\nSplit parameters:")
                    for i, param in enumerate(all_params):
                        print(f"  Param {i}: {param}")

if __name__ == "__main__":
    test_function_parameter_parsing()