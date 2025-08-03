import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.parser_tokenizer import CTokenizer, TokenType

def test_debug_field_name_logic():
    """Debug the field name extraction logic for nested structures"""
    
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
    
    # Manually collect the field tokens for the nested union
    pos = 13  # Start after the first field
    field_tokens = []
    brace_count = 0
    while pos < union_end:
        if tokens[pos].type == TokenType.LBRACE:
            brace_count += 1
        elif tokens[pos].type == TokenType.RBRACE:
            brace_count -= 1
            # Only stop if we're at the main closing brace
            if pos == union_end:
                break
        elif tokens[pos].type == TokenType.SEMICOLON and brace_count == 0:
            # This is the semicolon that ends the field
            break
        
        if tokens[pos].type not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
            field_tokens.append(tokens[pos])
        pos += 1
    
    # For nested structures, continue collecting until we find the field name
    if (len(field_tokens) >= 3 and 
        field_tokens[0].type in [TokenType.STRUCT, TokenType.UNION] and 
        field_tokens[1].type == TokenType.LBRACE):
        temp_pos = pos
        while temp_pos < len(tokens):
            if tokens[temp_pos].type == TokenType.SEMICOLON:
                # Found the semicolon that ends the field
                break
            if tokens[temp_pos].type not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
                field_tokens.append(tokens[temp_pos])
            temp_pos += 1
    
    print(f"\nField tokens: {field_tokens}")
    print(f"Number of tokens: {len(field_tokens)}")
    
    # Debug the field name extraction logic
    print(f"\n=== DEBUGGING FIELD NAME EXTRACTION ===")
    
    # Find the LAST closing brace and then the field name
    field_name = None
    for i in range(len(field_tokens) - 1, -1, -1):
        print(f"Checking token {i}: {field_tokens[i]}")
        if field_tokens[i].type == TokenType.RBRACE and i + 1 < len(field_tokens):
            print(f"Found RBRACE at position {i}")
            # The field name should be the next identifier after the closing brace
            for j in range(i + 1, len(field_tokens)):
                print(f"  Checking for identifier at position {j}: {field_tokens[j]}")
                if field_tokens[j].type == TokenType.IDENTIFIER:
                    field_name = field_tokens[j].value
                    print(f"  Found field name: {field_name}")
                    break
            if field_name:
                break
    
    print(f"\nFinal field name: {field_name}")
    
    # Expected field name
    expected_field_name = "nested_union"
    print(f"Expected field name: {expected_field_name}")
    print(f"Match: {field_name == expected_field_name}")

if __name__ == "__main__":
    test_debug_field_name_logic()