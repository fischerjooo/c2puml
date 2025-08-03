import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.parser_tokenizer import CTokenizer, find_struct_fields, TokenType

def test_debug_step_by_step():
    """Debug the find_struct_fields function step by step"""
    
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
    
    # Manually trace the find_struct_fields logic
    print(f"\n=== MANUAL TRACE ===")
    
    fields = []
    pos = union_start
    while pos <= union_end and tokens[pos].type != TokenType.LBRACE:
        pos += 1
    if pos > union_end:
        print("No opening brace found")
        return
    pos += 1  # Skip opening brace
    print(f"After skipping opening brace: pos={pos}")

    # Find the closing brace position of the main struct body
    closing_brace_pos = pos
    brace_count = 1  # Start at 1 because we're already past the opening brace
    while closing_brace_pos <= union_end:
        if tokens[closing_brace_pos].type == TokenType.LBRACE:
            brace_count += 1
        elif tokens[closing_brace_pos].type == TokenType.RBRACE:
            brace_count -= 1
            if brace_count == 0:
                # This is the closing brace of the main struct body
                break
        closing_brace_pos += 1
    
    print(f"Main closing brace position: {closing_brace_pos}")
    print(f"Main closing brace token: {tokens[closing_brace_pos] if closing_brace_pos <= union_end else 'NOT FOUND'}")

    # Only parse fields up to the closing brace
    while pos < closing_brace_pos and tokens[pos].type != TokenType.RBRACE:
        print(f"\n--- Processing field at pos={pos} ---")
        print(f"Current token: {tokens[pos]}")
        
        field_tokens = []
        # Collect tokens until we find the semicolon that ends this field
        # For nested structures, we need to handle braces properly
        brace_count = 0
        start_pos = pos
        while pos < closing_brace_pos:
            if tokens[pos].type == TokenType.LBRACE:
                brace_count += 1
            elif tokens[pos].type == TokenType.RBRACE:
                brace_count -= 1
                # Only stop if we're at the main closing brace
                if pos == closing_brace_pos:
                    break
            elif tokens[pos].type == TokenType.SEMICOLON and brace_count == 0:
                # This is the semicolon that ends the field
                break
            
            if tokens[pos].type not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
                field_tokens.append(tokens[pos])
            pos += 1
        
        print(f"Collected field_tokens: {field_tokens}")
        print(f"Position after collection: {pos}")
        
        # For nested structures, we need to continue collecting tokens until we find the field name
        # and the semicolon that ends the entire field
        if (len(field_tokens) >= 3 and 
            field_tokens[0].type in [TokenType.STRUCT, TokenType.UNION] and 
            field_tokens[1].type == TokenType.LBRACE):
            print(f"Detected nested structure: {field_tokens[0].value}")
            # This might be a nested structure, continue collecting until we find the field name
            temp_pos = pos
            additional_tokens = []
            while temp_pos < len(tokens):
                if tokens[temp_pos].type == TokenType.SEMICOLON:
                    # Found the semicolon that ends the field
                    break
                if tokens[temp_pos].type not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
                    additional_tokens.append(tokens[temp_pos])
                temp_pos += 1
            print(f"Additional tokens collected: {additional_tokens}")
            print(f"Temp position after additional collection: {temp_pos}")
            field_tokens.extend(additional_tokens)
            pos = temp_pos
            print(f"Final field_tokens: {field_tokens}")
            print(f"Final position: {pos}")

        # Parse field from collected tokens
        if len(field_tokens) >= 2:
            print(f"Parsing field with {len(field_tokens)} tokens")
            
            # Check if this is a nested struct field
            if (
                len(field_tokens) >= 3
                and field_tokens[0].type == TokenType.STRUCT
                and field_tokens[1].type == TokenType.LBRACE
            ):
                print("Detected nested struct")
                # This is a nested struct - find the field name after the closing brace
                # Look for the pattern: struct { ... } field_name;
                field_name = None
                # Find the closing brace and then the field name
                for i, token in enumerate(field_tokens):
                    if token.type == TokenType.RBRACE and i + 1 < len(field_tokens):
                        # The field name should be the next identifier after the closing brace
                        for j in range(i + 1, len(field_tokens)):
                            if field_tokens[j].type == TokenType.IDENTIFIER:
                                field_name = field_tokens[j].value
                                break
                        break
                
                print(f"Found nested struct field name: {field_name}")
                if field_name:
                    field_type = "struct { ... }"
                    if field_name not in ["[", "]", ";", "}"]:
                        fields.append((field_name, field_type))
                        print(f"Added nested struct field: {field_name}")
            # Check if this is a nested union field
            elif (
                len(field_tokens) >= 3
                and field_tokens[0].type == TokenType.UNION
                and field_tokens[1].type == TokenType.LBRACE
            ):
                print("Detected nested union")
                # This is a nested union - find the field name after the closing brace
                # Look for the pattern: union { ... } field_name;
                field_name = None
                # Find the closing brace and then the field name
                for i, token in enumerate(field_tokens):
                    if token.type == TokenType.RBRACE and i + 1 < len(field_tokens):
                        # The field name should be the next identifier after the closing brace
                        for j in range(i + 1, len(field_tokens)):
                            if field_tokens[j].type == TokenType.IDENTIFIER:
                                field_name = field_tokens[j].value
                                break
                        break
                
                print(f"Found nested union field name: {field_name}")
                if field_name:
                    field_type = "union { ... }"
                    if field_name not in ["[", "]", ";", "}"]:
                        fields.append((field_name, field_type))
                        print(f"Added nested union field: {field_name}")
            else:
                # Regular field processing
                print("Processing as regular field")
                field_name = field_tokens[-1].value
                field_type = " ".join(t.value for t in field_tokens[:-1])
                print(f"Regular field: {field_name} = {field_type}")
                if (
                    field_name not in ["[", "]", ";", "}"]
                    and field_name
                    and field_name.strip()
                    and field_type.strip()
                ):
                    # Additional validation to ensure we don't have empty strings
                    stripped_name = field_name.strip()
                    stripped_type = field_type.strip()
                    if stripped_name and stripped_type:
                        fields.append((stripped_name, stripped_type))
                        print(f"Added regular field: {stripped_name}")
        
        if pos < closing_brace_pos:
            pos += 1  # Skip semicolon
            print(f"Advanced past semicolon to pos={pos}")
    
    print(f"\n=== FINAL RESULT ===")
    print(f"Fields found: {fields}")
    
    # Expected result
    expected_fields = [('primary_int', 'int'), ('nested_union', 'union { ... }'), ('primary_bytes', 'char[32]')]
    print(f"Expected fields: {expected_fields}")
    print(f"Match: {fields == expected_fields}")

if __name__ == "__main__":
    test_debug_step_by_step()