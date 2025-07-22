#!/usr/bin/env python3
"""
Debug script to test function parsing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'c_to_plantuml'))

from c_to_plantuml.parser_tokenizer import CTokenizer, StructureFinder, TokenType

def test_function_parsing():
    # Test with the actual function declaration
    test_code = """
    extern point_t * create_point(int x, int y, const char * label);
    """
    
    print("Testing function parsing with:")
    print(test_code)
    print("-" * 50)
    
    # Tokenize
    tokenizer = CTokenizer()
    tokens = tokenizer.tokenize(test_code)
    
    print("All tokens:")
    for i, token in enumerate(tokens):
        print(f"  {i}: {token.type.name} = '{token.value}'")
    
    print("\nFiltered tokens:")
    filtered_tokens = tokenizer.filter_tokens(tokens)
    for i, token in enumerate(filtered_tokens):
        print(f"  {i}: {token.type.name} = '{token.value}'")
    
    print("\nFunction parsing:")
    structure_finder = StructureFinder(filtered_tokens)
    functions = structure_finder.find_functions()
    for start_pos, end_pos, func_name, return_type, is_declaration in functions:
        print(f"  Function: {func_name}")
        print(f"  Return type: '{return_type}'")
        print(f"  Is declaration: {is_declaration}")
        print(f"  Range: {start_pos} to {end_pos}")
        
        # Manual extraction for comparison
        if func_name == "create_point":
            func_name_pos = None
            for i, token in enumerate(filtered_tokens):
                if token.value == func_name:
                    func_name_pos = i
                    break
            
            if func_name_pos is not None:
                # Look backwards from function name to find return type
                return_type_end = func_name_pos - 1
                return_type_start = return_type_end
                
                print(f"  Initial return_type_end: {return_type_end}")
                print(f"  Initial return_type_start: {return_type_start}")
                
                # Skip backwards over whitespace
                while return_type_start >= 0:
                    token_type = filtered_tokens[return_type_start].type
                    if token_type in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
                        return_type_start -= 1
                    else:
                        break
                
                print(f"  After skipping whitespace: {return_type_start}")
                
                # Skip backwards over modifiers
                modifiers = {TokenType.STATIC, TokenType.EXTERN, TokenType.INLINE}
                while return_type_start >= 0:
                    if filtered_tokens[return_type_start].type in modifiers:
                        return_type_start -= 1
                    else:
                        break
                
                print(f"  After skipping modifiers: {return_type_start}")
                
                # Now look backwards to find the complete return type
                final_return_start = return_type_start
                while final_return_start >= 0:
                    if filtered_tokens[final_return_start].type in modifiers:
                        final_return_start += 1  # Don't include the modifier
                        break
                    final_return_start -= 1
                
                if final_return_start < 0:
                    final_return_start = 0
                
                print(f"  Final return type range: {final_return_start} to {return_type_end}")
                
                # Extract return type tokens
                if final_return_start >= 0 and final_return_start <= return_type_end:
                    actual_return_tokens = filtered_tokens[final_return_start:return_type_end + 1]
                    actual_return_type = ' '.join(t.value for t in actual_return_tokens)
                    print(f"  Actual return type tokens: {[t.value for t in actual_return_tokens]}")
                    print(f"  Actual return type: '{actual_return_type}'")
                else:
                    print(f"  Invalid return type range!")
        
        print()

if __name__ == "__main__":
    test_function_parsing()