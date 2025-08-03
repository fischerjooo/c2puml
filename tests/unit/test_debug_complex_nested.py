import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.parser_tokenizer import CTokenizer, find_struct_fields, TokenType

def test_debug_complex_nested():
    """Debug the complex nested union structure"""
    
    # Test code with complex nested union
    test_code = """
    typedef union {
        int primary_int;
        union {
            float nested_float;
            double nested_double;
            union {
                char deep_char;
                short deep_short;
            } deep_union;
        } nested_union;
        char primary_bytes[32];
    } union_with_union_t;
    """
    
    # Tokenize the code
    tokenizer = CTokenizer()
    tokens = tokenizer.tokenize(test_code)
    
    # Find the union definition
    union_start = None
    union_end = None
    for i, token in enumerate(tokens):
        if token.type == TokenType.UNION and i + 1 < len(tokens):
            # Find the opening brace
            for j in range(i + 1, len(tokens)):
                if tokens[j].type == TokenType.LBRACE:
                    union_start = j
                    break
            if union_start:
                break
    
    if union_start:
        # Find the closing brace
        brace_count = 1
        for i in range(union_start + 1, len(tokens)):
            if tokens[i].type == TokenType.LBRACE:
                brace_count += 1
            elif tokens[i].type == TokenType.RBRACE:
                brace_count -= 1
                if brace_count == 0:
                    union_end = i
                    break
    
    print(f"Union boundaries: start={union_start}, end={union_end}")
    
    # Show tokens around the union
    print(f"\n=== TOKENS AROUND UNION ===")
    for i in range(max(0, union_start-2), min(len(tokens), union_end+3)):
        print(f"{i:2d}: {tokens[i]}")
    
    if union_start and union_end:
        # Test the actual find_struct_fields function
        print(f"\n=== TESTING ACTUAL find_struct_fields ===")
        actual_fields = find_struct_fields(tokens, union_start, union_end)
        print(f"Actual fields: {actual_fields}")
        
        # Expected result
        expected_fields = [('primary_int', 'int'), ('nested_union', 'union { ... }'), ('primary_bytes', 'char[32]')]
        print(f"Expected fields: {expected_fields}")
        print(f"Match: {actual_fields == expected_fields}")
        
        # Check field names
        actual_field_names = [field[0] for field in actual_fields]
        expected_field_names = [field[0] for field in expected_fields]
        print(f"Actual field names: {actual_field_names}")
        print(f"Expected field names: {expected_field_names}")
        print(f"Field names match: {actual_field_names == expected_field_names}")

if __name__ == "__main__":
    test_debug_complex_nested()