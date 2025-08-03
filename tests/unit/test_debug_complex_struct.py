import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.parser_tokenizer import CTokenizer, find_struct_fields, TokenType

def test_debug_complex_struct():
    """Debug the complex struct parsing"""
    
    # Test code with complex struct
    test_code = """
    typedef struct complex_struct {
        int id;
        char name[32];
        float value;
        struct {
            int x;
            int y;
        } position;
        union {
            int int_data;
            float float_data;
        } data;
    } complex_struct_t;
    """
    
    # Tokenize the code
    tokenizer = CTokenizer()
    tokens = tokenizer.tokenize(test_code)
    
    # Find the struct definition
    struct_start = None
    struct_end = None
    for i, token in enumerate(tokens):
        if token.type == TokenType.STRUCT and i + 1 < len(tokens):
            # Find the opening brace
            for j in range(i + 1, len(tokens)):
                if tokens[j].type == TokenType.LBRACE:
                    struct_start = j
                    break
            if struct_start:
                break
    
    if struct_start:
        # Find the closing brace
        brace_count = 1
        for i in range(struct_start + 1, len(tokens)):
            if tokens[i].type == TokenType.LBRACE:
                brace_count += 1
            elif tokens[i].type == TokenType.RBRACE:
                brace_count -= 1
                if brace_count == 0:
                    struct_end = i
                    break
    
    print(f"Struct boundaries: start={struct_start}, end={struct_end}")
    
    # Show tokens around the struct
    print(f"\n=== TOKENS AROUND STRUCT ===")
    for i in range(max(0, struct_start-2), min(len(tokens), struct_end+3)):
        print(f"{i:2d}: {tokens[i]}")
    
    if struct_start and struct_end:
        # Let's manually check what the closing brace position should be
        print(f"\n=== MANUAL CLOSING BRACE CHECK ===")
        pos = struct_start
        while pos <= struct_end and tokens[pos].type != TokenType.LBRACE:
            pos += 1
        if pos > struct_end:
            print("No opening brace found!")
            return
        
        pos += 1  # Skip opening brace
        print(f"After skipping opening brace: pos={pos}")
        
        # Find the closing brace position of the main struct body
        closing_brace_pos = pos
        brace_count = 1  # Start at 1 because we're already past the opening brace
        while closing_brace_pos <= struct_end:
            if tokens[closing_brace_pos].type == TokenType.LBRACE:
                brace_count += 1
            elif tokens[closing_brace_pos].type == TokenType.RBRACE:
                brace_count -= 1
                if brace_count == 0:
                    # This is the closing brace of the main struct body
                    break
            closing_brace_pos += 1
        
        print(f"Closing brace position: {closing_brace_pos}")
        print(f"Token at closing brace position: {tokens[closing_brace_pos] if closing_brace_pos < len(tokens) else 'OUT_OF_BOUNDS'}")
        
        # Test the actual find_struct_fields function
        print(f"\n=== TESTING ACTUAL find_struct_fields ===")
        actual_fields = find_struct_fields(tokens, struct_start, struct_end)
        print(f"Actual fields: {actual_fields}")
        
        # Expected result
        expected_fields = [('id', 'int'), ('name', 'char[32]'), ('value', 'float'), ('position', 'struct { ... }'), ('data', 'union { ... }')]
        print(f"Expected fields: {expected_fields}")
        print(f"Match: {actual_fields == expected_fields}")
        
        # Check field names
        actual_field_names = [field[0] for field in actual_fields]
        expected_field_names = [field[0] for field in expected_fields]
        print(f"Actual field names: {actual_field_names}")
        print(f"Expected field names: {expected_field_names}")
        print(f"Field names match: {actual_field_names == expected_field_names}")

if __name__ == "__main__":
    test_debug_complex_struct()