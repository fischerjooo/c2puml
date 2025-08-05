#!/usr/bin/env python3
"""
Test for field parsing issue with nested anonymous structures
"""

import unittest
from src.c2puml.core.parser_tokenizer import find_struct_fields, CTokenizer, TokenType


class TestFieldParsingIssue(unittest.TestCase):
    """Test for the specific field parsing issue with nested anonymous structures"""

    def setUp(self):
        self.tokenizer = CTokenizer()

    def test_nested_anonymous_struct_field_boundary_issue(self):
        """Test that field boundaries are correctly detected for nested anonymous structures"""
        
        # This is the problematic pattern from complex.h
        source_code = """
        typedef struct {
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
        } complex_naming_test_t;
        """
        
        tokens = self.tokenizer.tokenize(source_code)
        
        # Filter out whitespace and newline tokens for easier processing
        filtered_tokens = [t for t in tokens if t.type not in [TokenType.WHITESPACE, TokenType.NEWLINE]]
        
        # Find the typedef struct definition
        struct_start = None
        struct_end = None
        for i, token in enumerate(filtered_tokens):
            if (token.type == TokenType.TYPEDEF and 
                i + 1 < len(filtered_tokens) and 
                filtered_tokens[i + 1].type == TokenType.STRUCT and
                i + 2 < len(filtered_tokens) and
                filtered_tokens[i + 2].type == TokenType.LBRACE):
                struct_start = i + 1  # Start at the STRUCT token
                # Find the closing brace
                brace_count = 1
                for j in range(i + 3, len(filtered_tokens)):
                    if filtered_tokens[j].type == TokenType.LBRACE:
                        brace_count += 1
                    elif filtered_tokens[j].type == TokenType.RBRACE:
                        brace_count -= 1
                        if brace_count == 0:
                            struct_end = j
                            break
                break
        
        self.assertIsNotNone(struct_start, "Should find struct start")
        self.assertIsNotNone(struct_end, "Should find struct end")
        
        # Convert back to original token indices
        original_struct_start = None
        original_struct_end = None
        
        # Find the corresponding positions in the original token list
        filtered_index = 0
        for i, token in enumerate(tokens):
            if token.type not in [TokenType.WHITESPACE, TokenType.NEWLINE]:
                if filtered_index == struct_start:
                    original_struct_start = i
                if filtered_index == struct_end:
                    original_struct_end = i
                    break
                filtered_index += 1
        
        self.assertIsNotNone(original_struct_start, "Should find original struct start")
        self.assertIsNotNone(original_struct_end, "Should find original struct end")
        
        # Parse the fields
        fields = find_struct_fields(tokens, original_struct_start, original_struct_end)
        
        # Check that we have the expected fields
        field_names = [field[0] for field in fields]
        field_types = [field[1] for field in fields]
        
        # Should have two fields: nested_struct_a and nested_struct_a2
        self.assertIn("nested_struct_a", field_names, "Should find nested_struct_a field")
        self.assertIn("nested_struct_a2", field_names, "Should find nested_struct_a2 field")
        
        # Check that field types are not malformed
        for field_name, field_type in fields:
            # The field type should not contain malformed patterns
            self.assertNotIn("} nested_struct_a; struct { int", field_type, 
                           f"Field {field_name} should not have malformed type: {field_type}")
            self.assertNotIn("} level3_struct_1; struct { int", field_type,
                           f"Field {field_name} should not have malformed type: {field_type}")
            
            # Field types should be reasonable
            self.assertTrue(len(field_type.strip()) > 0, f"Field {field_name} should have non-empty type")
            self.assertNotIn(";", field_type, f"Field {field_name} type should not contain semicolon: {field_type}")

    def test_extreme_nesting_field_boundary_issue(self):
        """Test that field boundaries are correctly detected for extremely nested structures"""
        
        # This is the other problematic pattern from complex.h
        source_code = """
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
        
        tokens = self.tokenizer.tokenize(source_code)
        
        # Filter out whitespace and newline tokens for easier processing
        filtered_tokens = [t for t in tokens if t.type not in [TokenType.WHITESPACE, TokenType.NEWLINE]]
        
        # Find the typedef struct definition
        struct_start = None
        struct_end = None
        for i, token in enumerate(filtered_tokens):
            if (token.type == TokenType.TYPEDEF and 
                i + 1 < len(filtered_tokens) and 
                filtered_tokens[i + 1].type == TokenType.STRUCT and
                i + 2 < len(filtered_tokens) and
                filtered_tokens[i + 2].type == TokenType.LBRACE):
                struct_start = i + 1  # Start at the STRUCT token
                # Find the closing brace
                brace_count = 1
                for j in range(i + 3, len(filtered_tokens)):
                    if filtered_tokens[j].type == TokenType.LBRACE:
                        brace_count += 1
                    elif filtered_tokens[j].type == TokenType.RBRACE:
                        brace_count -= 1
                        if brace_count == 0:
                            struct_end = j
                            break
                break
        
        self.assertIsNotNone(struct_start, "Should find struct start")
        self.assertIsNotNone(struct_end, "Should find struct end")
        
        # Convert back to original token indices
        original_struct_start = None
        original_struct_end = None
        
        # Find the corresponding positions in the original token list
        filtered_index = 0
        for i, token in enumerate(tokens):
            if token.type not in [TokenType.WHITESPACE, TokenType.NEWLINE]:
                if filtered_index == struct_start:
                    original_struct_start = i
                if filtered_index == struct_end:
                    original_struct_end = i
                    break
                filtered_index += 1
        
        self.assertIsNotNone(original_struct_start, "Should find original struct start")
        self.assertIsNotNone(original_struct_end, "Should find original struct end")
        
        # Parse the fields
        fields = find_struct_fields(tokens, original_struct_start, original_struct_end)
        
        # Check that we have the expected fields
        field_names = [field[0] for field in fields]
        
        # Should have one field: level2_struct_1
        self.assertIn("level2_struct_1", field_names, "Should find level2_struct_1 field")
        
        # Check that field types are not malformed
        for field_name, field_type in fields:
            # The field type should not contain malformed patterns
            self.assertNotIn("} level3_struct_1; struct { int", field_type,
                           f"Field {field_name} should not have malformed type: {field_type}")
            
            # Field types should be reasonable
            self.assertTrue(len(field_type.strip()) > 0, f"Field {field_name} should have non-empty type")
            self.assertNotIn(";", field_type, f"Field {field_name} type should not contain semicolon: {field_type}")

    def test_field_boundary_detection_robustness(self):
        """Test that field boundary detection is robust for various nested patterns"""
        
        # Test with multiple consecutive anonymous structures
        source_code = """
        typedef struct {
            struct { int a; } struct_a;
            struct { int b; } struct_b;
            struct { int c; } struct_c;
        } test_struct_t;
        """
        
        tokens = self.tokenizer.tokenize(source_code)
        
        # Filter out whitespace and newline tokens for easier processing
        filtered_tokens = [t for t in tokens if t.type not in [TokenType.WHITESPACE, TokenType.NEWLINE]]
        
        # Find the typedef struct definition
        struct_start = None
        struct_end = None
        for i, token in enumerate(filtered_tokens):
            if (token.type == TokenType.TYPEDEF and 
                i + 1 < len(filtered_tokens) and 
                filtered_tokens[i + 1].type == TokenType.STRUCT and
                i + 2 < len(filtered_tokens) and
                filtered_tokens[i + 2].type == TokenType.LBRACE):
                struct_start = i + 1  # Start at the STRUCT token
                # Find the closing brace
                brace_count = 1
                for j in range(i + 3, len(filtered_tokens)):
                    if filtered_tokens[j].type == TokenType.LBRACE:
                        brace_count += 1
                    elif filtered_tokens[j].type == TokenType.RBRACE:
                        brace_count -= 1
                        if brace_count == 0:
                            struct_end = j
                            break
                break
        
        self.assertIsNotNone(struct_start, "Should find struct start")
        self.assertIsNotNone(struct_end, "Should find struct end")
        
        # Convert back to original token indices
        original_struct_start = None
        original_struct_end = None
        
        # Find the corresponding positions in the original token list
        filtered_index = 0
        for i, token in enumerate(tokens):
            if token.type not in [TokenType.WHITESPACE, TokenType.NEWLINE]:
                if filtered_index == struct_start:
                    original_struct_start = i
                if filtered_index == struct_end:
                    original_struct_end = i
                    break
                filtered_index += 1
        
        self.assertIsNotNone(original_struct_start, "Should find original struct start")
        self.assertIsNotNone(original_struct_end, "Should find original struct end")
        
        # Parse the fields
        fields = find_struct_fields(tokens, original_struct_start, original_struct_end)
        
        # Check that we have the expected fields
        field_names = [field[0] for field in fields]
        
        # Should have three fields
        self.assertIn("struct_a", field_names, "Should find struct_a field")
        self.assertIn("struct_b", field_names, "Should find struct_b field")
        self.assertIn("struct_c", field_names, "Should find struct_c field")
        
        # Check that field types are not malformed
        for field_name, field_type in fields:
            # Field types should be reasonable
            self.assertTrue(len(field_type.strip()) > 0, f"Field {field_name} should have non-empty type")
            self.assertNotIn(";", field_type, f"Field {field_name} type should not contain semicolon: {field_type}")
            
            # Should not have cross-contamination between fields
            if field_name == "struct_a":
                self.assertNotIn("struct_b", field_type, "struct_a should not contain struct_b in its type")
            elif field_name == "struct_b":
                self.assertNotIn("struct_a", field_type, "struct_b should not contain struct_a in its type")
                self.assertNotIn("struct_c", field_type, "struct_b should not contain struct_c in its type")


if __name__ == "__main__":
    unittest.main()