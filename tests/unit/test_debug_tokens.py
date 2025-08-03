"""
Debug test to understand token generation for nested structures.
"""

import unittest
from pathlib import Path
import tempfile
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.parser_tokenizer import CTokenizer, TokenType


class TestDebugTokens(unittest.TestCase):
    """Debug test to understand token generation."""

    def setUp(self):
        self.tokenizer = CTokenizer()

    def test_nested_union_tokens(self):
        """Debug: See what tokens are generated for nested unions."""
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
        
        # Print all tokens
        print("All tokens:")
        for i, token in enumerate(tokens):
            print(f"{i:3d}: {token.type.name:15s} '{token.value}'")
        
        # Find the union field tokens
        print("\nLooking for nested union field...")
        for i, token in enumerate(tokens):
            if token.type == TokenType.UNION and i + 1 < len(tokens):
                print(f"Found UNION at position {i}: '{token.value}'")
                # Look at next few tokens
                for j in range(i, min(i + 10, len(tokens))):
                    print(f"  {j}: {tokens[j].type.name:15s} '{tokens[j].value}'")


if __name__ == '__main__':
    unittest.main()