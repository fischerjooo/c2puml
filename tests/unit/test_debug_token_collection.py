import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.parser_tokenizer import CTokenizer, TokenType

def test_debug_token_collection():
    """Debug the token collection logic step by step"""
    
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
        # Let's manually step through the token collection
        print(f"\n=== MANUAL TOKEN COLLECTION DEBUG ===")
        
        pos = union_start
        while pos <= union_end and tokens[pos].type != TokenType.LBRACE:
            pos += 1
        if pos > union_end:
            print("No opening brace found!")
            return
        
        pos += 1  # Skip opening brace
        print(f"After skipping opening brace: pos={pos}")
        
        # Find the closing brace position
        closing_brace_pos = pos
        while (
            closing_brace_pos <= union_end
            and tokens[closing_brace_pos].type != TokenType.RBRACE
        ):
            closing_brace_pos += 1
        
        print(f"Closing brace position: {closing_brace_pos}")
        
        # Main loop - let's trace the second iteration (nested union)
        iteration = 0
        while pos < closing_brace_pos and tokens[pos].type != TokenType.RBRACE:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")
            print(f"Current pos: {pos}, token: {tokens[pos]}")
            
            field_tokens = []
            # Collect tokens until we find the semicolon that ends this field
            brace_count = 0
            start_pos = pos
            while pos < closing_brace_pos:
                if tokens[pos].type == TokenType.LBRACE:
                    brace_count += 1
                elif tokens[pos].type == TokenType.RBRACE:
                    brace_count -= 1
                    if pos == closing_brace_pos:
                        break
                elif tokens[pos].type == TokenType.SEMICOLON and brace_count == 0:
                    break
                
                if tokens[pos].type not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
                    field_tokens.append(tokens[pos])
                pos += 1
            
            print(f"Field tokens after first collection: {[f'{t.type.name}:{t.value}' for t in field_tokens]}")
            print(f"Position after first collection: {pos}")
            
            # Check if this might be a nested structure
            if (len(field_tokens) >= 3 and 
                field_tokens[0].type in [TokenType.STRUCT, TokenType.UNION] and 
                field_tokens[1].type == TokenType.LBRACE):
                print("*** DETECTED POTENTIAL NESTED STRUCTURE ***")
                
                # Continue collecting tokens until we find the field name
                temp_pos = pos
                print(f"Starting additional collection from pos: {temp_pos}")
                print(f"Tokens around temp_pos:")
                for i in range(max(0, temp_pos-2), min(len(tokens), temp_pos+5)):
                    print(f"  {i:2d}: {tokens[i]}")
                
                while temp_pos <= closing_brace_pos:
                    print(f"  temp_pos: {temp_pos}, token: {tokens[temp_pos]}")
                    if tokens[temp_pos].type == TokenType.SEMICOLON:
                        print(f"  Found semicolon at {temp_pos}")
                        break
                    if tokens[temp_pos].type not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
                        field_tokens.append(tokens[temp_pos])
                        print(f"  Added token: {tokens[temp_pos]}")
                    temp_pos += 1
                pos = temp_pos
                print(f"Final position after additional collection: {pos}")
            
            print(f"Final field tokens: {[f'{t.type.name}:{t.value}' for t in field_tokens]}")
            
            # Skip to next iteration
            if pos < closing_brace_pos:
                pos += 1  # Skip semicolon
                print(f"Position after skipping semicolon: {pos}")

if __name__ == "__main__":
    test_debug_token_collection()