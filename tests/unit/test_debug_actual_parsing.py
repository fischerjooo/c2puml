"""
Debug test to see what's happening in the actual parsing process.
"""

import unittest
from pathlib import Path
import tempfile
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.parser import CParser
from src.c2puml.core.parser_tokenizer import CTokenizer, find_struct_fields


class TestDebugActualParsing(unittest.TestCase):
    """Debug test to see what's happening in the actual parsing process."""

    def setUp(self):
        self.parser = CParser()
        self.tokenizer = CTokenizer()

    def test_actual_union_parsing(self):
        """Debug: See what happens in the actual parsing process."""
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
        
        # Create a temporary file with the test code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(source_code)
            temp_file = f.name
        
        try:
            # Parse the file
            file_model = self.parser.parse_file(Path(temp_file), "test.c")
            
            # Check what was parsed
            print(f"Available unions: {list(file_model.unions.keys())}")
            
            if "test_union_t" in file_model.unions:
                union = file_model.unions["test_union_t"]
                print(f"Union fields: {[(f.name, f.type) for f in union.fields]}")
                
                # Check if there are any anonymous relationships
                print(f"Anonymous relationships: {file_model.anonymous_relationships}")
            else:
                print("test_union_t not found in unions")
            
            # Debug: Check the tokenization and field parsing directly
            print("\nDebugging tokenization and field parsing:")
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
                # Parse fields directly
                fields = find_struct_fields(tokens, union_start, union_end)
                print(f"Direct field parsing result: {fields}")
                
        finally:
            # Clean up
            Path(temp_file).unlink()


if __name__ == '__main__':
    unittest.main()