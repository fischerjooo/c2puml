"""
Debug test to understand field parsing for nested structures.
"""

import unittest
from pathlib import Path
import tempfile
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.parser_tokenizer import CTokenizer, TokenType, find_struct_fields


class TestDebugFieldParsing(unittest.TestCase):
    """Debug test to understand field parsing."""

    def setUp(self):
        self.tokenizer = CTokenizer()

    def test_nested_union_field_parsing(self):
        """Debug: See how field parsing works for nested unions."""
        source_code = """
        typedef union {
            int primary_int;
            union {
                float nested_float;
                double nested_double;
            } nested_union;
            char primary_bytes[32];
        } test_union_t;
        """
        
        # Tokenize the code
        tokens = self.tokenizer.tokenize(source_code)
        
        # Find the union definition
        union_start = None
        union_end = None
        for i, token in enumerate(tokens):
            if token.type == TokenType.UNION:
                # Find the opening brace
                for j in range(i, len(tokens)):
                    if tokens[j].type == TokenType.LBRACE:
                        union_start = j
                        break
                # Find the closing brace
                if union_start:
                    brace_count = 0
                    for j in range(union_start, len(tokens)):
                        if tokens[j].type == TokenType.LBRACE:
                            brace_count += 1
                        elif tokens[j].type == TokenType.RBRACE:
                            brace_count -= 1
                            if brace_count == 0:
                                union_end = j
                                break
                break
        
        print(f"Union definition: start={union_start}, end={union_end}")
        
        if union_start is not None and union_end is not None:
            # Parse fields
            fields = find_struct_fields(tokens, union_start, union_end)
            print(f"Parsed fields: {fields}")
            
            # Debug: Show the tokens in the union body
            print("\nTokens in union body:")
            for i in range(union_start, union_end + 1):
                print(f"{i:3d}: {tokens[i].type.name:15s} '{tokens[i].value}'")
            
            # Debug: Show what happens during field parsing
            print("\nDebugging field parsing:")
            pos = union_start + 1  # Skip opening brace
            closing_brace_pos = union_end
            
            while pos < closing_brace_pos and tokens[pos].type != TokenType.RBRACE:
                print(f"\nStarting field at position {pos}: '{tokens[pos].value}'")
                field_tokens = []
                brace_count = 0
                start_pos = pos
                
                while pos < closing_brace_pos:
                    if tokens[pos].type == TokenType.LBRACE:
                        brace_count += 1
                        print(f"  Opening brace at {pos}, brace_count = {brace_count}")
                    elif tokens[pos].type == TokenType.RBRACE:
                        brace_count -= 1
                        print(f"  Closing brace at {pos}, brace_count = {brace_count}")
                        if pos == closing_brace_pos:
                            print(f"  Reached main closing brace at {pos}")
                            break
                    elif tokens[pos].type == TokenType.SEMICOLON and brace_count == 0:
                        print(f"  Found field-ending semicolon at {pos}, brace_count = {brace_count}")
                        break
                    
                    if tokens[pos].type not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
                        field_tokens.append(tokens[pos])
                    pos += 1
                
                print(f"  Field tokens: {[t.value for t in field_tokens]}")
                print(f"  Ended at position {pos}")
                
                # Move past the semicolon
                if pos < closing_brace_pos and tokens[pos].type == TokenType.SEMICOLON:
                    pos += 1


if __name__ == '__main__':
    unittest.main()