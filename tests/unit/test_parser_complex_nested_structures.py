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
        # Create the complex structure that's failing
        complex_code = """
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
        
        # Tokenize the code
        tokenizer = CTokenizer()
        tokens = tokenizer.tokenize(complex_code)
        
        # Find the struct start and end
        struct_start = None
        struct_end = None
        
        # Look for TYPEDEF STRUCT pattern
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
        
        print("=== DEBUG: Token sequence for complex nested structure ===")
        print(f"Struct start: {struct_start}, Struct end: {struct_end}")
        print("Tokens from {} to {}:".format(struct_start, struct_end))
        for i in range(struct_start, min(struct_end + 1, len(tokens))):
            print(f"  {i}: {tokens[i]}")
        
        # Call find_struct_fields directly
        fields = find_struct_fields(tokens, struct_start, struct_end)
        
        print("=== DEBUG: Parsed fields ===")
        for field_name, field_type in fields:
            print(f"Field: '{field_name}' -> '{field_type}'")
        
        # Check if we found the expected fields
        field_names = [field[0] for field in fields]
        print(f"Field names found: {field_names}")
        
        # The complex structure should have at least one field
        self.assertGreater(len(fields), 0, "Should find at least one field")
        
        # Check for specific fields that should be found
        self.assertIn("first_struct", field_names, "first_struct field should be found")

    def test_anonymous_structure_deduplication(self):
        """Test that anonymous structures with identical content are deduplicated correctly"""
        # This test verifies that the same anonymous union content is not duplicated
        test_code = """
typedef struct {
    int level1_id;
    struct {
        int level2_id;
        union {
            int level3_int;
            float level3_float;
        } level3_union;
    } level2_struct;
} moderately_nested_t;

typedef struct {
    int other_id;
    struct {
        int other_level2_id;
        union {
            int level3_int;
            float level3_float;
        } level3_union;
    } other_level2_struct;
} other_nested_t;
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.h', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        try:
            # Parse the file
            parser = CParser()
            model = parser.parse_project(os.path.dirname(temp_file))
            
            # Find the structs in the model
            file_model = list(model.files.values())[0]
            
            # Check that both structs exist
            self.assertIn('moderately_nested_t', file_model.structs)
            self.assertIn('other_nested_t', file_model.structs)
            
            # Get the extracted anonymous structures
            moderately_nested = file_model.structs['moderately_nested_t']
            other_nested = file_model.structs['other_nested_t']
            
            # Debug: Print all struct names to see what was extracted
            print(f"All struct names: {list(file_model.structs.keys())}")
            
            # Debug: Print all fields in moderately_nested_t
            print(f"moderately_nested_t fields: {[(f.name, f.type) for f in moderately_nested.fields]}")
            print(f"other_nested_t fields: {[(f.name, f.type) for f in other_nested.fields]}")
            
            # Debug: Check the extracted level2_struct
            if 'moderately_nested_t_level2_struct' in file_model.structs:
                level2_struct = file_model.structs['moderately_nested_t_level2_struct']
                print(f"moderately_nested_t_level2_struct fields: {[(f.name, f.type) for f in level2_struct.fields]}")
            
            if 'other_nested_t_other_level2_struct' in file_model.structs:
                other_level2_struct = file_model.structs['other_nested_t_other_level2_struct']
                print(f"other_nested_t_other_level2_struct fields: {[(f.name, f.type) for f in other_level2_struct.fields]}")
            
            # Check that the level3_union field in both structs references the same extracted structure
            moderately_level3_field = None
            other_level3_field = None
            
            # Look in the extracted level2_struct
            if 'moderately_nested_t_level2_struct' in file_model.structs:
                level2_struct = file_model.structs['moderately_nested_t_level2_struct']
                for field in level2_struct.fields:
                    if field.name == 'level3_union':
                        moderately_level3_field = field
                        break
            
            if 'other_nested_t_other_level2_struct' in file_model.structs:
                other_level2_struct = file_model.structs['other_nested_t_other_level2_struct']
                for field in other_level2_struct.fields:
                    if field.name == 'level3_union':
                        other_level3_field = field
                        break
            
            self.assertIsNotNone(moderately_level3_field, "level3_union field should be found in moderately_nested_t_level2_struct")
            self.assertIsNotNone(other_level3_field, "level3_union field should be found in other_nested_t_other_level2_struct")
            
            print(f"moderately_nested_t_level2_struct.level3_union type: {moderately_level3_field.type}")
            print(f"other_nested_t_other_level2_struct.level3_union type: {other_level3_field.type}")
            
            # The types should be the same (referencing the same extracted structure)
            self.assertEqual(moderately_level3_field.type, other_level3_field.type, 
                           "Both structs should reference the same extracted anonymous union")
            
            # Verify that the referenced structure exists and has the correct content
            referenced_struct_name = moderately_level3_field.type
            self.assertIn(referenced_struct_name, file_model.unions, 
                         f"Referenced union {referenced_struct_name} should exist")
            
            referenced_union = file_model.unions[referenced_struct_name]
            print(f"Referenced union fields: {[(f.name, f.type) for f in referenced_union.fields]}")
            
            # Check that the union has the expected fields
            field_names = [f.name for f in referenced_union.fields]
            self.assertIn('level3_int', field_names, "Union should contain level3_int field")
            self.assertIn('level3_float', field_names, "Union should contain level3_float field")
            
        finally:
            os.unlink(temp_file)

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