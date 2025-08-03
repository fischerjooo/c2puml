"""
Debug test to see what's happening in the field processing logic for nested unions.
"""

import unittest
from pathlib import Path
import tempfile
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.parser_tokenizer import CTokenizer, TokenType


class TestDebugFieldProcessing(unittest.TestCase):
    """Debug test to see what's happening in the field processing logic."""

    def setUp(self):
        self.tokenizer = CTokenizer()

    def test_nested_union_field_processing(self):
        """Debug: See what's happening in the field processing logic for nested unions."""
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
            if token.type.name == "UNION":
                # Find the opening brace
                for j in range(i, len(tokens)):
                    if tokens[j].type.name == "LBRACE":
                        union_start = j
                        break
                # Find the closing brace
                if union_start:
                    brace_count = 0
                    for j in range(union_start, len(tokens)):
                        if tokens[j].type.name == "LBRACE":
                            brace_count += 1
                        elif tokens[j].type.name == "RBRACE":
                            brace_count -= 1
                            if brace_count == 0:
                                union_end = j
                                break
                break
        
        print(f"Union definition: start={union_start}, end={union_end}")
        
        if union_start is not None and union_end is not None:
            # Debug the field parsing step by step
            pos = union_start + 1  # Skip opening brace
            closing_brace_pos = union_end
            
            while pos < closing_brace_pos:
                print(f"\nStarting field at position {pos}: '{tokens[pos].value}'")
                field_tokens = []
                brace_count = 0
                
                while pos < closing_brace_pos:
                    if tokens[pos].type.name == "LBRACE":
                        brace_count += 1
                    elif tokens[pos].type.name == "RBRACE":
                        brace_count -= 1
                        if pos == closing_brace_pos:
                            break
                    elif tokens[pos].type.name == "SEMICOLON" and brace_count == 0:
                        break
                    
                    if tokens[pos].type.name not in ["WHITESPACE", "COMMENT", "NEWLINE"]:
                        field_tokens.append(tokens[pos])
                    pos += 1
                
                print(f"  Field tokens: {[t.value for t in field_tokens]}")
                
                # Debug the field processing logic
                if len(field_tokens) >= 2:
                    # Check if this is a nested union field
                    if (
                        len(field_tokens) >= 3
                        and field_tokens[0].type.name == "UNION"
                        and field_tokens[1].type.name == "LBRACE"
                    ):
                        print("  Detected as nested union field")
                        # Find the field name after the closing brace
                        field_name = None
                        for i, token in enumerate(field_tokens):
                            if token.type.name == "RBRACE" and i + 1 < len(field_tokens):
                                print(f"    Found closing brace at position {i}")
                                # The field name should be the next identifier after the closing brace
                                for j in range(i + 1, len(field_tokens)):
                                    if field_tokens[j].type.name == "IDENTIFIER":
                                        field_name = field_tokens[j].value
                                        print(f"    Found field name: {field_name}")
                                        break
                                break
                        
                        if field_name:
                            field_type = "union { ... }"
                            if field_name not in ["[", "]", ";", "}"]:
                                print(f"    Would create field: ({field_name}, {field_type})")
                            else:
                                print(f"    Field name '{field_name}' is invalid")
                        else:
                            print("    No field name found")
                    else:
                        print("  Not detected as nested union field")
                
                # Move past the semicolon
                if pos < closing_brace_pos and tokens[pos].type.name == "SEMICOLON":
                    pos += 1


if __name__ == '__main__':
    unittest.main()