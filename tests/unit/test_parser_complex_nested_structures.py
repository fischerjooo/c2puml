#!/usr/bin/env python3
"""
Test cases for complex nested anonymous structure field parsing issues
"""

import unittest
import tempfile
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.c2puml.core.parser import CParser
from src.c2puml.core.parser_tokenizer import find_struct_fields, CTokenizer, TokenType


class TestComplexNestedStructureFieldParsing(unittest.TestCase):
    """Test field parsing for complex nested anonymous structures"""

    def test_nested_a2_field_parsing_issue(self):
        """Test the specific nested_a2 field parsing issue"""
        # This reproduces the exact structure from complex.h that causes the issue
        test_code = """
typedef struct {
    struct {
        int first_a;
        struct {
            int nested_a1;
            struct {
                int deep_a1;
            } deep_struct_a1;
            struct {
                int deep_a2;
            } deep_struct_a2;
        } nested_struct_a;
        struct {
            int nested_a2;
        } nested_struct_a2;
    } first_struct;
} complex_naming_test_t;
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Parse the file
            parser = CParser()
            model = parser.parse_project(os.path.dirname(temp_file))
            
            # Find the struct in the model
            file_model = list(model.files.values())[0]
            struct = file_model.structs.get('complex_naming_test_t')
            
            self.assertIsNotNone(struct, "Struct should be found")
            
            # Debug: Print all fields
            print(f"All fields in complex_naming_test_t: {[(f.name, f.type) for f in struct.fields]}")
            
            # The nested_a2 field should be in the extracted anonymous structure
            extracted_struct = file_model.structs.get('complex_naming_test_t_first_struct')
            self.assertIsNotNone(extracted_struct, "Extracted anonymous structure should be found")
            
            print(f"All fields in complex_naming_test_t_first_struct: {[(f.name, f.type) for f in extracted_struct.fields]}")
            
            # Check that nested_a2 field has correct type in the extracted structure
            nested_a2_field = None
            for field in extracted_struct.fields:
                if field.name == 'nested_a2':
                    nested_a2_field = field
                    break
            
            self.assertIsNotNone(nested_a2_field, "nested_a2 field should be found in extracted structure")
            self.assertNotIn("} nested_struct_a; struct { int", nested_a2_field.type, 
                           f"Field type should not contain malformed content: {nested_a2_field.type}")
            
        finally:
            os.unlink(temp_file)

    def test_level3_field_parsing_issue(self):
        """Test the specific level3_field parsing issue"""
        # This reproduces the exact structure from complex.h that causes the issue
        test_code = """
typedef struct {
    struct {
        struct {
            struct {
                int level4_field;
            } level4_struct_1;
            struct {
                int level4_field2;
            } level4_struct_2;
        } level3_struct_1;
        struct {
            int level3_field;
        } level3_struct_2;
    } level2_struct_1;
} extreme_nesting_test_t;
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Parse the file
            parser = CParser()
            model = parser.parse_project(os.path.dirname(temp_file))
            
            # Find the struct in the model
            file_model = list(model.files.values())[0]
            struct = file_model.structs.get('extreme_nesting_test_t')
            
            self.assertIsNotNone(struct, "Struct should be found")
            
            # Check that level3_field field has correct type
            level3_field = None
            for field in struct.fields:
                if field.name == 'level3_field':
                    level3_field = field
                    break
            
            self.assertIsNotNone(level3_field, "level3_field should be found")
            self.assertNotIn("} level3_struct_1; struct { int", level3_field.type, 
                           f"Field type should not contain malformed content: {level3_field.type}")
            
        finally:
            os.unlink(temp_file)

    def test_tokenizer_field_parsing_directly(self):
        """Test the tokenizer field parsing directly to isolate the issue"""
        test_code = """
typedef struct {
    struct {
        int first_a;
        struct {
            int nested_a1;
        } nested_struct_a;
        struct {
            int nested_a2;
        } nested_struct_a2;
    } first_struct;
} test_struct_t;
"""
        
        # Tokenize the code
        tokenizer = CTokenizer()
        tokens = tokenizer.tokenize(test_code)
        
        # Find the struct definition - look for typedef struct pattern
        struct_start = None
        struct_end = None
        
        # Find typedef struct
        for i in range(len(tokens) - 2):
            if (tokens[i].type == TokenType.TYPEDEF and 
                tokens[i + 1].type == TokenType.STRUCT and
                tokens[i + 2].type == TokenType.LBRACE):
                struct_start = i + 2  # Start at the opening brace
                break
        
        if struct_start:
            # Find the closing brace
            brace_count = 1
            for j in range(struct_start + 1, len(tokens)):
                if tokens[j].type == TokenType.LBRACE:
                    brace_count += 1
                elif tokens[j].type == TokenType.RBRACE:
                    brace_count -= 1
                    if brace_count == 0:
                        struct_end = j
                        break
        
        self.assertIsNotNone(struct_start, "Struct start should be found")
        self.assertIsNotNone(struct_end, "Struct end should be found")
        
        # Parse fields
        fields = find_struct_fields(tokens, struct_start, struct_end)
        
        # Check that nested_a2 field is parsed correctly
        nested_a2_found = False
        for field_name, field_type in fields:
            if field_name == 'nested_a2':
                nested_a2_found = True
                self.assertNotIn("} nested_struct_a; struct { int", field_type,
                               f"Field type should not contain malformed content: {field_type}")
                break
        
        self.assertTrue(nested_a2_found, "nested_a2 field should be found")

    def test_debug_token_sequence(self):
        """Debug the exact token sequence for the problematic structure"""
        test_code = """
typedef struct {
    struct {
        int nested_a1;
    } nested_struct_a;
    struct {
        int nested_a2;
    } nested_struct_a2;
} test_struct_t;
"""
        
        # Tokenize the code
        tokenizer = CTokenizer()
        tokens = tokenizer.tokenize(test_code)
        
        # Print all tokens for debugging
        print("All tokens:")
        for i, token in enumerate(tokens):
            print(f"{i:3d}: {token}")
        
        # Find the struct definition
        struct_start = None
        struct_end = None
        
        # Find typedef struct (skip whitespace)
        for i in range(len(tokens) - 2):
            if tokens[i].type == TokenType.TYPEDEF:
                # Find the next STRUCT token
                j = i + 1
                while j < len(tokens) and tokens[j].type in [TokenType.WHITESPACE, TokenType.NEWLINE]:
                    j += 1
                if j < len(tokens) and tokens[j].type == TokenType.STRUCT:
                    # Find the next LBRACE token
                    k = j + 1
                    while k < len(tokens) and tokens[k].type in [TokenType.WHITESPACE, TokenType.NEWLINE]:
                        k += 1
                    if k < len(tokens) and tokens[k].type == TokenType.LBRACE:
                        struct_start = k  # Start at the opening brace
                        break
        
        # If not found, look for just struct
        if struct_start is None:
            for i in range(len(tokens) - 1):
                if tokens[i].type == TokenType.STRUCT:
                    # Find the next LBRACE token
                    j = i + 1
                    while j < len(tokens) and tokens[j].type in [TokenType.WHITESPACE, TokenType.NEWLINE]:
                        j += 1
                    if j < len(tokens) and tokens[j].type == TokenType.LBRACE:
                        struct_start = j  # Start at the opening brace
                        break
        
        if struct_start:
            # Find the closing brace
            brace_count = 1
            for j in range(struct_start + 1, len(tokens)):
                if tokens[j].type == TokenType.LBRACE:
                    brace_count += 1
                elif tokens[j].type == TokenType.RBRACE:
                    brace_count -= 1
                    if brace_count == 0:
                        struct_end = j
                        break
        
        self.assertIsNotNone(struct_start, "Struct start should be found")
        self.assertIsNotNone(struct_end, "Struct end should be found")
        
        print(f"\nStruct range: {struct_start} to {struct_end}")
        print("Struct tokens:")
        for i in range(struct_start, struct_end + 1):
            print(f"{i:3d}: {tokens[i]}")
        
        # Parse fields
        fields = find_struct_fields(tokens, struct_start, struct_end)
        
        print(f"\nParsed fields: {fields}")
        
        # Check that nested_a2 field is parsed correctly
        nested_a2_found = False
        for field_name, field_type in fields:
            if field_name == 'nested_a2':
                nested_a2_found = True
                print(f"Found nested_a2 with type: {field_type}")
                self.assertNotIn("} nested_struct_a; struct { int", field_type,
                               f"Field type should not contain malformed content: {field_type}")
                break
        
        self.assertTrue(nested_a2_found, "nested_a2 field should be found")

    def test_debug_find_struct_fields_complex(self):
        """Debug test to understand why find_struct_fields fails on complex nested structures"""
        # This is the problematic structure from complex.h
        source_code = """
typedef struct {
    struct {
        struct {
            int level3_field;
        } level2_field;
    } level1_field;
} complex_naming_test_t;
"""
        
        tokenizer = CTokenizer()
        tokens = tokenizer.tokenize(source_code)
        
        # Find the struct start and end
        struct_start = None
        struct_end = None
        
        for i, token in enumerate(tokens):
            if token.type == TokenType.TYPEDEF:
                # Find the next STRUCT token (skip whitespace)
                j = i + 1
                while j < len(tokens) and tokens[j].type in [TokenType.WHITESPACE, TokenType.NEWLINE]:
                    j += 1
                if j < len(tokens) and tokens[j].type == TokenType.STRUCT:
                    # Find the next LBRACE token
                    k = j + 1
                    while k < len(tokens) and tokens[k].type in [TokenType.WHITESPACE, TokenType.NEWLINE]:
                        k += 1
                    if k < len(tokens) and tokens[k].type == TokenType.LBRACE:
                        struct_start = k  # Start at the opening brace
                        break
        
        if struct_start is None:
            self.fail("Could not find TYPEDEF STRUCT")
        
        # Find the closing brace of the main struct
        brace_count = 0
        for i in range(struct_start, len(tokens)):
            if tokens[i].type == TokenType.LBRACE:
                brace_count += 1
            elif tokens[i].type == TokenType.RBRACE:
                brace_count -= 1
                if brace_count == 0:
                    struct_end = i
                    break
        
        if struct_end is None:
            self.fail("Could not find struct end")
        
        print(f"\n=== DEBUG: Token sequence for complex nested structure ===")
        print(f"Struct start: {struct_start}, Struct end: {struct_end}")
        print(f"Tokens from {struct_start} to {struct_end}:")
        for i in range(struct_start, min(struct_end + 10, len(tokens))):
            print(f"  {i}: {tokens[i]}")
        
        # Call find_struct_fields with detailed debugging
        print(f"\n=== DEBUG: Calling find_struct_fields ===")
        fields = find_struct_fields(tokens, struct_start, struct_end)
        
        print(f"\n=== DEBUG: Parsed fields ===")
        for i, (name, field_type) in enumerate(fields):
            print(f"  Field {i}: name='{name}', type='{field_type}'")
        
        # The expected result should be:
        # - level1_field with type containing the nested structure
        assert len(fields) > 0, "Should find at least one field"
        
        # Check if we found the expected field
        field_names = [name for name, _ in fields]
        print(f"Found field names: {field_names}")
        
        # The main issue is that we should find 'level1_field' as a field
        assert 'level1_field' in field_names, f"Expected to find 'level1_field', found: {field_names}"

    def test_complex_nested_structure_exact_reproduction(self):
        """Test the exact complex structure from complex.h that causes the issue"""
        test_code = """
typedef struct {
    struct {
        int first_a;
        struct {
            int nested_a1;
            struct {
                int deep_a1;
            } deep_struct_a1;
            struct {
                int deep_a2;
            } deep_struct_a2;
        } nested_struct_a;
        struct {
            int nested_a2;
        } nested_struct_a2;
    } first_struct;
} complex_naming_test_t;
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Parse the file
            parser = CParser()
            model = parser.parse_project(os.path.dirname(temp_file))
            
            # Find the struct in the model
            file_model = list(model.files.values())[0]
            struct = file_model.structs.get('complex_naming_test_t')
            
            self.assertIsNotNone(struct, "Struct should be found")
            
            # Debug: Print all fields
            print(f"All fields in complex_naming_test_t: {[(f.name, f.type) for f in struct.fields]}")
            
            # The nested_a2 field should be in the extracted anonymous structure
            extracted_struct = file_model.structs.get('complex_naming_test_t_first_struct')
            self.assertIsNotNone(extracted_struct, "Extracted anonymous structure should be found")
            
            print(f"All fields in complex_naming_test_t_first_struct: {[(f.name, f.type) for f in extracted_struct.fields]}")
            
            # Check that nested_a2 field has correct type in the extracted structure
            nested_a2_field = None
            for field in extracted_struct.fields:
                if field.name == 'nested_a2':
                    nested_a2_field = field
                    break
            
            self.assertIsNotNone(nested_a2_field, "nested_a2 field should be found in extracted structure")
            print(f"nested_a2 field type: {nested_a2_field.type}")
            self.assertNotIn("} nested_struct_a; struct { int", nested_a2_field.type, 
                           f"Field type should not contain malformed content: {nested_a2_field.type}")
            
        finally:
            os.unlink(temp_file)

    def test_complex_naming_test_t_debug(self):
        """Debug the exact complex_naming_test_t structure that causes the issue"""
        test_code = """
typedef struct {
    // First level - multiple structs
    struct {
        int first_a;
        struct {
            int nested_a1;
            struct {
                int deep_a1;
            } deep_struct_a1;
            struct {
                int deep_a2;
            } deep_struct_a2;
        } nested_struct_a;
        struct {
            int nested_a2;
        } nested_struct_a2;
    } first_struct;
} complex_naming_test_t;
"""
        
        # Tokenize the code
        tokenizer = CTokenizer()
        tokens = tokenizer.tokenize(test_code)
        
        # Find the typedef struct
        struct_start = None
        struct_end = None
        
        # Find typedef struct (skip whitespace)
        for i in range(len(tokens) - 2):
            if tokens[i].type == TokenType.TYPEDEF:
                # Find the next STRUCT token
                j = i + 1
                while j < len(tokens) and tokens[j].type in [TokenType.WHITESPACE, TokenType.NEWLINE]:
                    j += 1
                if j < len(tokens) and tokens[j].type == TokenType.STRUCT:
                    # Find the next LBRACE token
                    k = j + 1
                    while k < len(tokens) and tokens[k].type in [TokenType.WHITESPACE, TokenType.NEWLINE]:
                        k += 1
                    if k < len(tokens) and tokens[k].type == TokenType.LBRACE:
                        struct_start = k  # Start at the opening brace
                        break
        
        if struct_start:
            # Find the closing brace
            brace_count = 1
            for j in range(struct_start + 1, len(tokens)):
                if tokens[j].type == TokenType.LBRACE:
                    brace_count += 1
                elif tokens[j].type == TokenType.RBRACE:
                    brace_count -= 1
                    if brace_count == 0:
                        struct_end = j
                        break
        
        self.assertIsNotNone(struct_start, "Struct start should be found")
        self.assertIsNotNone(struct_end, "Struct end should be found")
        
        print(f"\nStruct range: {struct_start} to {struct_end}")
        print("Struct tokens:")
        for i in range(struct_start, struct_end + 1):
            print(f"{i:3d}: {tokens[i]}")
        
        # Parse fields
        fields = find_struct_fields(tokens, struct_start, struct_end)
        
        print(f"\nParsed fields: {fields}")
        
        # Check for the problematic field
        nested_a2_found = False
        for field_name, field_type in fields:
            print(f"Field: '{field_name}' -> '{field_type}'")
            if field_name == 'nested_a2':
                nested_a2_found = True
                self.assertNotIn("} nested_struct_a; struct { int", field_type,
                               f"Field type should not contain malformed content: {field_type}")
                break
        
        # The field should be named 'first_struct', not 'nested_a2'
        first_struct_found = False
        for field_name, field_type in fields:
            if field_name == 'first_struct':
                first_struct_found = True
                break
        
        self.assertTrue(first_struct_found, "first_struct field should be found")
        self.assertFalse(nested_a2_found, "nested_a2 should not be a top-level field")

    def test_inner_structure_parsing_issue(self):
        """Test the specific inner structure parsing that's causing the issue"""
        test_code = """
struct {
    int first_a;
    struct {
        int nested_a1;
        struct {
            int deep_a1;
        } deep_struct_a1;
        struct {
            int deep_a2;
        } deep_struct_a2;
    } nested_struct_a;
    struct {
        int nested_a2;
    } nested_struct_a2;
} first_struct;
"""
        
        # Tokenize the code
        tokenizer = CTokenizer()
        tokens = tokenizer.tokenize(test_code)
        
        # Find the struct definition (this is the inner structure)
        struct_start = None
        struct_end = None
        
        # Find struct (skip whitespace)
        for i in range(len(tokens) - 1):
            if tokens[i].type == TokenType.STRUCT:
                # Find the next LBRACE token
                j = i + 1
                while j < len(tokens) and tokens[j].type in [TokenType.WHITESPACE, TokenType.NEWLINE]:
                    j += 1
                if j < len(tokens) and tokens[j].type == TokenType.LBRACE:
                    struct_start = j  # Start at the opening brace
                    break
        
        if struct_start:
            # Find the closing brace
            brace_count = 1
            for j in range(struct_start + 1, len(tokens)):
                if tokens[j].type == TokenType.LBRACE:
                    brace_count += 1
                elif tokens[j].type == TokenType.RBRACE:
                    brace_count -= 1
                    if brace_count == 0:
                        struct_end = j
                        break
        
        self.assertIsNotNone(struct_start, "Struct start should be found")
        self.assertIsNotNone(struct_end, "Struct end should be found")
        
        print(f"\nInner struct range: {struct_start} to {struct_end}")
        print("Inner struct tokens:")
        for i in range(struct_start, struct_end + 1):
            print(f"{i:3d}: {tokens[i]}")
        
        # Parse fields
        fields = find_struct_fields(tokens, struct_start, struct_end)
        
        print(f"\nParsed inner fields: {fields}")
        
        # Check for the problematic field
        nested_a2_found = False
        for field_name, field_type in fields:
            print(f"Inner field: '{field_name}' -> '{field_type}'")
            if field_name == 'nested_a2':
                nested_a2_found = True
                self.assertNotIn("} nested_struct_a; struct { int", field_type,
                               f"Field type should not contain malformed content: {field_type}")
                break
        
        # The field should be named 'nested_struct_a2', not 'nested_a2'
        nested_struct_a2_found = False
        for field_name, field_type in fields:
            if field_name == 'nested_struct_a2':
                nested_struct_a2_found = True
                break
        
        self.assertTrue(nested_struct_a2_found, "nested_struct_a2 field should be found")
        self.assertFalse(nested_a2_found, "nested_a2 should not be a field name")


if __name__ == '__main__':
    unittest.main()