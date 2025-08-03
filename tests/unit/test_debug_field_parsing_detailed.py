import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.parser_tokenizer import CTokenizer, find_struct_fields, TokenType

def test_debug_nested_union_parsing():
    """Debug the nested union parsing step by step"""
    
    # Test code with nested union
    test_code = """
    typedef union {
        int primary_int;
        union {
            float nested_float;
            double nested_double;
        } nested_union;
    } test_union_t;
    """
    
    # Tokenize the code
    tokenizer = CTokenizer()
    tokens = tokenizer.tokenize(test_code)
    
    print("=== TOKENIZATION ===")
    for i, token in enumerate(tokens):
        print(f"{i:2d}: {token}")
    
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
    
    print(f"\n=== UNION BOUNDARIES ===")
    print(f"Union start: {union_start}, end: {union_end}")
    
    if union_start and union_end:
        # Extract the union content
        union_tokens = tokens[union_start:union_end+1]
        print(f"\n=== UNION TOKENS ===")
        for i, token in enumerate(union_tokens):
            print(f"{i:2d}: {token}")
        
        # Now let's manually step through the find_struct_fields logic
        print(f"\n=== MANUAL FIELD PARSING ===")
        
        pos = 1  # Skip opening brace
        closing_brace_pos = len(union_tokens) - 1  # Position of closing brace
        
        field_count = 0
        manual_fields = []
        while pos < closing_brace_pos and union_tokens[pos].type != TokenType.RBRACE:
            field_count += 1
            print(f"\n--- Field {field_count} ---")
            
            field_tokens = []
            # Collect tokens until we find the semicolon that ends this field
            brace_count = 0
            start_pos = pos
            while pos < closing_brace_pos:
                if union_tokens[pos].type == TokenType.LBRACE:
                    brace_count += 1
                elif union_tokens[pos].type == TokenType.RBRACE:
                    brace_count -= 1
                    if pos == closing_brace_pos:
                        break
                elif union_tokens[pos].type == TokenType.SEMICOLON and brace_count == 0:
                    break
                
                if union_tokens[pos].type not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
                    field_tokens.append(union_tokens[pos])
                pos += 1
            
            print(f"Field tokens: {[f'{t.type.name}:{t.value}' for t in field_tokens]}")
            
            # Parse field from collected tokens
            if len(field_tokens) >= 2:
                print(f"Field has {len(field_tokens)} tokens")
                
                # Check if this is a nested union field
                if (
                    len(field_tokens) >= 3
                    and field_tokens[0].type == TokenType.UNION
                    and field_tokens[1].type == TokenType.LBRACE
                ):
                    print("*** DETECTED NESTED UNION ***")
                    
                    # Find the field name after the closing brace
                    field_name = None
                    for i, token in enumerate(field_tokens):
                        if token.type == TokenType.RBRACE and i + 1 < len(field_tokens):
                            for j in range(i + 1, len(field_tokens)):
                                if field_tokens[j].type == TokenType.IDENTIFIER:
                                    field_name = field_tokens[j].value
                                    break
                            break
                    
                    print(f"Extracted field name: '{field_name}'")
                    
                    if field_name:
                        field_type = "union { ... }"
                        print(f"Would add field: ({field_name}, {field_type})")
                        manual_fields.append((field_name, field_type))
                    else:
                        print("ERROR: Could not extract field name!")
                else:
                    print("Not a nested union - processing as regular field")
                    # Regular field processing
                    field_name = field_tokens[-1].value
                    field_type = " ".join(t.value for t in field_tokens[:-1])
                    print(f"Regular field: ({field_name}, {field_type})")
                    manual_fields.append((field_name, field_type))
            
            if pos < closing_brace_pos:
                pos += 1  # Skip semicolon
        
        print(f"\n=== MANUAL PARSING RESULT ===")
        print(f"Manual fields: {manual_fields}")
        
        # Now test the actual find_struct_fields function
        print(f"\n=== ACTUAL find_struct_fields RESULT ===")
        actual_fields = find_struct_fields(tokens, union_start, union_end)
        print(f"Actual fields: {actual_fields}")
        
        # Compare results
        print(f"\n=== COMPARISON ===")
        print(f"Manual fields: {manual_fields}")
        print(f"Actual fields: {actual_fields}")
        print(f"Match: {manual_fields == actual_fields}")

if __name__ == "__main__":
    test_debug_nested_union_parsing()