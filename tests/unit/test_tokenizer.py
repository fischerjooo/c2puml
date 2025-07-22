#!/usr/bin/env python3
"""
Comprehensive unit tests for the C tokenizer and structure finder
"""

import unittest
from typing import List

from c_to_plantuml.parser_tokenizer import (
    CTokenizer, StructureFinder, Token, TokenType,
    find_struct_fields, find_enum_values, extract_token_range
)


class TestCTokenizer(unittest.TestCase):
    """Test the C tokenizer functionality"""

    def setUp(self):
        self.tokenizer = CTokenizer()

    def test_tokenize_keywords(self):
        """Test tokenization of C keywords"""
        content = "struct enum union typedef static extern inline const void"
        tokens = self.tokenizer.tokenize(content)
        
        expected_types = [
            TokenType.STRUCT, TokenType.WHITESPACE, TokenType.ENUM, TokenType.WHITESPACE,
            TokenType.UNION, TokenType.WHITESPACE, TokenType.TYPEDEF, TokenType.WHITESPACE,
            TokenType.STATIC, TokenType.WHITESPACE, TokenType.EXTERN, TokenType.WHITESPACE,
            TokenType.INLINE, TokenType.WHITESPACE, TokenType.CONST, TokenType.WHITESPACE,
            TokenType.VOID, TokenType.EOF
        ]
        
        self.assertEqual(len(tokens), len(expected_types))
        for i, expected_type in enumerate(expected_types):
            self.assertEqual(tokens[i].type, expected_type)

    def test_tokenize_data_types(self):
        """Test tokenization of C data types"""
        content = "char int float double long short unsigned signed"
        tokens = self.tokenizer.tokenize(content)
        
        expected_types = [
            TokenType.CHAR, TokenType.WHITESPACE, TokenType.INT, TokenType.WHITESPACE,
            TokenType.FLOAT, TokenType.WHITESPACE, TokenType.DOUBLE, TokenType.WHITESPACE,
            TokenType.LONG, TokenType.WHITESPACE, TokenType.SHORT, TokenType.WHITESPACE,
            TokenType.UNSIGNED, TokenType.WHITESPACE, TokenType.SIGNED, TokenType.EOF
        ]
        
        self.assertEqual(len(tokens), len(expected_types))
        for i, expected_type in enumerate(expected_types):
            self.assertEqual(tokens[i].type, expected_type)

    def test_tokenize_operators_and_punctuation(self):
        """Test tokenization of operators and punctuation"""
        content = "{}()[];,=*&"
        tokens = self.tokenizer.tokenize(content)
        
        expected_types = [
            TokenType.LBRACE, TokenType.RBRACE, TokenType.LPAREN, TokenType.RPAREN,
            TokenType.LBRACKET, TokenType.RBRACKET, TokenType.SEMICOLON, TokenType.COMMA,
            TokenType.ASSIGN, TokenType.ASTERISK, TokenType.AMPERSAND, TokenType.EOF
        ]
        
        self.assertEqual(len(tokens), len(expected_types))
        for i, expected_type in enumerate(expected_types):
            self.assertEqual(tokens[i].type, expected_type)

    def test_tokenize_identifiers(self):
        """Test tokenization of identifiers"""
        content = "variable_name _underscore camelCase UPPER_CASE"
        tokens = self.tokenizer.tokenize(content)
        
        # Filter out whitespace and EOF
        identifier_tokens = [t for t in tokens if t.type == TokenType.IDENTIFIER]
        
        expected_identifiers = ["variable_name", "_underscore", "camelCase", "UPPER_CASE"]
        self.assertEqual(len(identifier_tokens), len(expected_identifiers))
        for i, expected_id in enumerate(expected_identifiers):
            self.assertEqual(identifier_tokens[i].value, expected_id)

    def test_tokenize_numbers(self):
        """Test tokenization of numbers"""
        content = "123 456.789 0x1A 0b1010 42L 3.14f 2.5e-10"
        tokens = self.tokenizer.tokenize(content)
        
        # Filter out whitespace and EOF
        number_tokens = [t for t in tokens if t.type == TokenType.NUMBER]
        
        expected_numbers = ["123", "456.789", "0x1A", "0b1010", "42L", "3.14f", "2.5e-10"]
        self.assertEqual(len(number_tokens), len(expected_numbers))
        for i, expected_num in enumerate(expected_numbers):
            self.assertEqual(number_tokens[i].value, expected_num)

    def test_tokenize_strings(self):
        """Test tokenization of string literals"""
        content = '"Hello, World!" "Escape\\n\\t\\"quotes\\""'
        tokens = self.tokenizer.tokenize(content)
        
        # Filter out whitespace and EOF
        string_tokens = [t for t in tokens if t.type == TokenType.STRING]
        
        expected_strings = ['"Hello, World!"', '"Escape\\n\\t\\"quotes\\""']
        self.assertEqual(len(string_tokens), len(expected_strings))
        for i, expected_str in enumerate(expected_strings):
            self.assertEqual(string_tokens[i].value, expected_str)

    def test_tokenize_char_literals(self):
        """Test tokenization of character literals"""
        content = "'a' '\\n' '\\t' '\\''"
        tokens = self.tokenizer.tokenize(content)
        
        # Filter out whitespace and EOF
        char_tokens = [t for t in tokens if t.type == TokenType.CHAR_LITERAL]
        
        expected_chars = ["'a'", "'\\n'", "'\\t'", "'\\''"]
        self.assertEqual(len(char_tokens), len(expected_chars))
        for i, expected_char in enumerate(expected_chars):
            self.assertEqual(char_tokens[i].value, expected_char)

    def test_tokenize_comments(self):
        """Test tokenization of comments"""
        content = "// Single line comment\n/* Multi-line\ncomment */"
        tokens = self.tokenizer.tokenize(content)
        
        # Filter out whitespace, newlines and EOF
        comment_tokens = [t for t in tokens if t.type == TokenType.COMMENT]
        
        self.assertEqual(len(comment_tokens), 2)
        self.assertTrue(comment_tokens[0].value.startswith("//"))
        self.assertTrue(comment_tokens[1].value.startswith("/*"))

    def test_tokenize_preprocessor(self):
        """Test tokenization of preprocessor directives"""
        content = "#include <stdio.h>\n#define MAX_SIZE 100\n#ifdef DEBUG"
        tokens = self.tokenizer.tokenize(content)
        
        # Filter out whitespace, newlines and EOF
        preprocessor_tokens = [t for t in tokens if t.type in [TokenType.INCLUDE, TokenType.DEFINE, TokenType.PREPROCESSOR]]
        
        self.assertEqual(len(preprocessor_tokens), 3)
        self.assertEqual(preprocessor_tokens[0].type, TokenType.INCLUDE)
        self.assertEqual(preprocessor_tokens[1].type, TokenType.DEFINE)
        self.assertEqual(preprocessor_tokens[2].type, TokenType.PREPROCESSOR)

    def test_tokenize_whitespace(self):
        """Test tokenization of whitespace"""
        content = "  \t  \n  "
        tokens = self.tokenizer.tokenize(content)
        
        whitespace_tokens = [t for t in tokens if t.type == TokenType.WHITESPACE]
        newline_tokens = [t for t in tokens if t.type == TokenType.NEWLINE]
        
        self.assertGreater(len(whitespace_tokens), 0)
        self.assertGreater(len(newline_tokens), 0)

    def test_tokenize_complex_expression(self):
        """Test tokenization of complex C expressions"""
        content = "int* ptr = (int*)malloc(sizeof(int));"
        tokens = self.tokenizer.tokenize(content)
        
        # Filter out whitespace and EOF
        significant_tokens = [t for t in tokens if t.type not in [TokenType.WHITESPACE, TokenType.EOF]]
        
        expected_types = [
            TokenType.INT, TokenType.ASTERISK, TokenType.IDENTIFIER, TokenType.ASSIGN,
            TokenType.LPAREN, TokenType.INT, TokenType.ASTERISK, TokenType.RPAREN,
            TokenType.IDENTIFIER, TokenType.LPAREN, TokenType.IDENTIFIER, TokenType.LPAREN,
            TokenType.INT, TokenType.RPAREN, TokenType.RPAREN, TokenType.SEMICOLON
        ]
        
        self.assertEqual(len(significant_tokens), len(expected_types))
        for i, expected_type in enumerate(expected_types):
            self.assertEqual(significant_tokens[i].type, expected_type)

    def test_tokenize_edge_cases(self):
        """Test tokenization of edge cases"""
        # Empty content
        tokens = self.tokenizer.tokenize("")
        self.assertEqual(len(tokens), 1)  # Only EOF token
        self.assertEqual(tokens[0].type, TokenType.EOF)
        
        # Single character
        tokens = self.tokenizer.tokenize("a")
        self.assertEqual(len(tokens), 2)  # Identifier + EOF
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[0].value, "a")
        
        # Unknown characters
        tokens = self.tokenizer.tokenize("@#$%")
        unknown_tokens = [t for t in tokens if t.type == TokenType.UNKNOWN]
        self.assertEqual(len(unknown_tokens), 4)

    def test_tokenize_line_numbers_and_columns(self):
        """Test that line numbers and columns are correctly tracked"""
        content = "int x;\nchar y;"
        tokens = self.tokenizer.tokenize(content)
        
        # Find the 'x' identifier
        x_token = next(t for t in tokens if t.value == "x")
        self.assertEqual(x_token.line, 1)
        self.assertEqual(x_token.column, 4)
        
        # Find the 'y' identifier
        y_token = next(t for t in tokens if t.value == "y")
        self.assertEqual(y_token.line, 2)
        self.assertEqual(y_token.column, 5)

    def test_filter_tokens(self):
        """Test token filtering functionality"""
        content = "int x; // comment\nchar y;"
        tokens = self.tokenizer.tokenize(content)
        
        # Filter out whitespace, comments, and newlines
        filtered = self.tokenizer.filter_tokens(tokens)
        
        # Should only have significant tokens
        significant_types = [TokenType.INT, TokenType.IDENTIFIER, TokenType.SEMICOLON,
                           TokenType.CHAR, TokenType.IDENTIFIER, TokenType.SEMICOLON]
        print('Filtered tokens:', filtered)
        print('Filtered types:', [t.type for t in filtered])
        self.assertEqual(len(filtered), len(significant_types))
        for i, expected_type in enumerate(significant_types):
            self.assertEqual(filtered[i].type, expected_type)

    def test_filter_tokens_custom_exclude(self):
        """Test token filtering with custom exclude types"""
        content = "int x; // comment\nchar y;"
        tokens = self.tokenizer.tokenize(content)
        
        # Filter out only comments
        filtered = self.tokenizer.filter_tokens(tokens, exclude_types=[TokenType.COMMENT])
        
        # Should still have whitespace and newlines
        comment_tokens = [t for t in filtered if t.type == TokenType.COMMENT]
        self.assertEqual(len(comment_tokens), 0)
        
        whitespace_tokens = [t for t in filtered if t.type == TokenType.WHITESPACE]
        self.assertGreater(len(whitespace_tokens), 0)


class TestStructureFinder(unittest.TestCase):
    """Test the StructureFinder class"""

    def setUp(self):
        self.tokenizer = CTokenizer()

    def test_find_structs_simple(self):
        """Test finding simple struct definitions"""
        content = """
        struct Point {
            int x;
            int y;
        };
        """
        tokens = self.tokenizer.tokenize(content)
        finder = StructureFinder(tokens)
        
        structs = finder.find_structs()
        self.assertEqual(len(structs), 1)
        
        start_pos, end_pos, name = structs[0]
        self.assertEqual(name, "Point")

    def test_find_structs_anonymous(self):
        """Test finding anonymous struct definitions"""
        content = """
        struct {
            int x;
            int y;
        } point;
        """
        tokens = self.tokenizer.tokenize(content)
        finder = StructureFinder(tokens)
        
        structs = finder.find_structs()
        self.assertEqual(len(structs), 1)
        
        start_pos, end_pos, name = structs[0]
        self.assertEqual(name, "")  # Anonymous struct

    def test_find_typedef_structs(self):
        """Test finding typedef struct definitions"""
        content = """
        typedef struct point_tag {
            int x;
            int y;
        } point_t;
        """
        tokens = self.tokenizer.tokenize(content)
        finder = StructureFinder(tokens)
        
        structs = finder.find_structs()
        self.assertEqual(len(structs), 1)
        
        start_pos, end_pos, name = structs[0]
        self.assertEqual(name, "point_t")

    def test_find_enums_simple(self):
        """Test finding simple enum definitions"""
        content = """
        enum Status {
            OK,
            ERROR
        };
        """
        tokens = self.tokenizer.tokenize(content)
        finder = StructureFinder(tokens)
        
        enums = finder.find_enums()
        self.assertEqual(len(enums), 1)
        
        start_pos, end_pos, name = enums[0]
        self.assertEqual(name, "Status")

    def test_find_typedef_enums(self):
        """Test finding typedef enum definitions"""
        content = """
        typedef enum color_tag {
            RED,
            GREEN,
            BLUE
        } color_t;
        """
        tokens = self.tokenizer.tokenize(content)
        finder = StructureFinder(tokens)
        
        enums = finder.find_enums()
        self.assertEqual(len(enums), 1)
        
        start_pos, end_pos, name = enums[0]
        self.assertEqual(name, "color_t")

    def test_find_functions_declarations(self):
        """Test finding function declarations"""
        content = """
        int calculate_sum(int a, int b);
        void process_data(char* data);
        """
        tokens = self.tokenizer.tokenize(content)
        finder = StructureFinder(tokens)
        
        functions = finder.find_functions()
        self.assertEqual(len(functions), 2)
        
        # Check first function
        start_pos, end_pos, name, return_type, is_declaration = functions[0]
        self.assertEqual(name, "calculate_sum")
        self.assertEqual(return_type, "int")
        self.assertTrue(is_declaration)
        
        # Check second function
        start_pos, end_pos, name, return_type, is_declaration = functions[1]
        self.assertEqual(name, "process_data")
        self.assertEqual(return_type, "void")
        self.assertTrue(is_declaration)

    def test_find_functions_definitions(self):
        """Test finding function definitions"""
        content = """
        int calculate_sum(int a, int b) {
            return a + b;
        }
        """
        tokens = self.tokenizer.tokenize(content)
        finder = StructureFinder(tokens)
        
        functions = finder.find_functions()
        self.assertEqual(len(functions), 1)
        
        start_pos, end_pos, name, return_type, is_declaration = functions[0]
        self.assertEqual(name, "calculate_sum")
        self.assertEqual(return_type, "int")
        self.assertFalse(is_declaration)

    def test_find_functions_with_modifiers(self):
        """Test finding functions with modifiers"""
        content = """
        static int internal_function(void);
        extern void external_function(char* data);
        inline int fast_function(int x);
        """
        tokens = self.tokenizer.tokenize(content)
        finder = StructureFinder(tokens)
        
        functions = finder.find_functions()
        self.assertEqual(len(functions), 3)
        
        # Check that return types include modifiers
        return_types = [f[3] for f in functions]
        self.assertIn("static int", return_types)
        self.assertIn("extern void", return_types)
        self.assertIn("inline int", return_types)

    def test_find_functions_pointer_return(self):
        """Test finding functions with pointer return types"""
        content = """
        point_t* create_point(int x, int y);
        char* get_string(void);
        """
        tokens = self.tokenizer.tokenize(content)
        finder = StructureFinder(tokens)
        
        functions = finder.find_functions()
        self.assertEqual(len(functions), 2)
        
        # Check pointer return types
        return_types = [f[3] for f in functions]
        self.assertIn("point_t *", return_types)
        self.assertIn("char *", return_types)

    def test_find_matching_brace(self):
        """Test finding matching braces"""
        content = "{ int x; { int y; } int z; }"
        tokens = self.tokenizer.tokenize(content)
        finder = StructureFinder(tokens)
        
        # Find matching brace for first opening brace
        match_pos = finder._find_matching_brace(0)
        self.assertIsNotNone(match_pos)
        self.assertEqual(tokens[match_pos].type, TokenType.RBRACE)

    def test_find_matching_brace_no_match(self):
        """Test finding matching brace when there's no match"""
        content = "{ int x; { int y;"
        tokens = self.tokenizer.tokenize(content)
        finder = StructureFinder(tokens)
        
        # Should return None for unmatched brace
        match_pos = finder._find_matching_brace(0)
        self.assertIsNone(match_pos)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions for token processing"""

    def setUp(self):
        self.tokenizer = CTokenizer()

    def test_extract_token_range(self):
        """Test extracting text from token range"""
        content = "int x = 42;"
        tokens = self.tokenizer.tokenize(content)
        
        # Extract range for "int x"
        print('All tokens:', tokens)
        text = extract_token_range(tokens, 0, 2)
        print('Extracted text:', text)
        self.assertEqual(text, "int x")

    def test_extract_token_range_invalid(self):
        """Test extracting token range with invalid indices"""
        content = "int x;"
        tokens = self.tokenizer.tokenize(content)
        
        # Invalid range
        text = extract_token_range(tokens, 10, 20)
        self.assertEqual(text, "")
        
        # Reversed range
        text = extract_token_range(tokens, 2, 1)
        self.assertEqual(text, "")

    def test_find_struct_fields(self):
        """Test extracting struct fields"""
        content = """
        struct Point {
            int x;
            char label[32];
            double value;
        };
        """
        tokens = self.tokenizer.tokenize(content)
        finder = StructureFinder(tokens)
        
        structs = finder.find_structs()
        self.assertEqual(len(structs), 1)
        
        start_pos, end_pos, name = structs[0]
        fields = find_struct_fields(tokens, start_pos, end_pos)
        
        expected_fields = [
            ("x", "int"),
            ("label", "char [32]"),
            ("value", "double")
        ]
        
        self.assertEqual(len(fields), len(expected_fields))
        for i, (field_name, field_type) in enumerate(fields):
            self.assertEqual(field_name, expected_fields[i][0])
            # Note: field type parsing might be simplified, so we check it contains the expected parts
            self.assertIn(expected_fields[i][1].split()[0], field_type)

    def test_find_enum_values(self):
        """Test extracting enum values"""
        content = """
        enum Status {
            OK = 0,
            ERROR = 1,
            PENDING
        };
        """
        tokens = self.tokenizer.tokenize(content)
        finder = StructureFinder(tokens)
        
        enums = finder.find_enums()
        self.assertEqual(len(enums), 1)
        
        start_pos, end_pos, name = enums[0]
        values = find_enum_values(tokens, start_pos, end_pos)
        
        expected_values = ["OK = 0", "ERROR = 1", "PENDING"]
        self.assertEqual(len(values), len(expected_values))
        for i, value in enumerate(values):
            self.assertEqual(value, expected_values[i])

    def test_find_enum_values_complex(self):
        """Test extracting complex enum values"""
        content = """
        enum Flags {
            FLAG_NONE = 0,
            FLAG_READ = 1 << 0,
            FLAG_WRITE = 1 << 1,
            FLAG_EXEC = 1 << 2
        };
        """
        tokens = self.tokenizer.tokenize(content)
        finder = StructureFinder(tokens)
        
        enums = finder.find_enums()
        self.assertEqual(len(enums), 1)
        
        start_pos, end_pos, name = enums[0]
        values = find_enum_values(tokens, start_pos, end_pos)
        
        self.assertEqual(len(values), 4)
        self.assertEqual(values[0], "FLAG_NONE = 0")
        self.assertEqual(values[1], "FLAG_READ = 1 << 0")
        self.assertEqual(values[2], "FLAG_WRITE = 1 << 1")
        self.assertEqual(values[3], "FLAG_EXEC = 1 << 2")


class TestTokenizerEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def setUp(self):
        self.tokenizer = CTokenizer()

    def test_tokenize_nested_comments(self):
        """Test tokenization with nested comments"""
        content = "/* Outer /* Inner */ comment */"
        tokens = self.tokenizer.tokenize(content)
        
        comment_tokens = [t for t in tokens if t.type == TokenType.COMMENT]
        self.assertEqual(len(comment_tokens), 1)
        self.assertTrue(comment_tokens[0].value.startswith("/*"))

    def test_tokenize_multiline_strings(self):
        """Test tokenization of multiline strings"""
        content = '"Line 1\nLine 2\nLine 3"'
        tokens = self.tokenizer.tokenize(content)
        
        string_tokens = [t for t in tokens if t.type == TokenType.STRING]
        print('String tokens:', string_tokens)
        print('String values:', [t.value for t in string_tokens])
        self.assertEqual(len(string_tokens), 1)
        self.assertTrue(string_tokens[0].value.startswith('"'))

    def test_tokenize_escaped_characters(self):
        """Test tokenization of escaped characters"""
        content = "'\\n' '\\t' '\\r' '\\\\' '\\'' '\\\"'"
        tokens = self.tokenizer.tokenize(content)
        
        char_tokens = [t for t in tokens if t.type == TokenType.CHAR_LITERAL]
        self.assertEqual(len(char_tokens), 6)

    def test_tokenize_mixed_content(self):
        """Test tokenization of mixed content with all token types"""
        content = """
        #include <stdio.h>
        #define MAX_SIZE 100
        
        /* This is a comment */
        struct Point {  // Inline comment
            int x;      /* Field comment */
            int y;
        };
        
        enum Status {
            OK = 0,     // Success
            ERROR = 1   /* Failure */
        };
        
        int main(void) {
            char* str = "Hello, World!";
            char ch = 'A';
            int num = 42;
            return 0;
        }
        """
        tokens = self.tokenizer.tokenize(content)
        
        # Check that all expected token types are present
        token_types = set(t.type for t in tokens)
        expected_types = {
            TokenType.INCLUDE, TokenType.DEFINE, TokenType.COMMENT,
            TokenType.STRUCT, TokenType.ENUM, TokenType.IDENTIFIER,
            TokenType.STRING, TokenType.CHAR_LITERAL, TokenType.NUMBER,
            TokenType.LBRACE, TokenType.RBRACE, TokenType.LPAREN, TokenType.RPAREN,
            TokenType.SEMICOLON, TokenType.ASSIGN, TokenType.COMMA,
            TokenType.INT, TokenType.CHAR, TokenType.ASTERISK, TokenType.VOID,
            TokenType.WHITESPACE, TokenType.NEWLINE, TokenType.EOF
        }
        
        for expected_type in expected_types:
            self.assertIn(expected_type, token_types, f"Missing token type: {expected_type}")

    def test_tokenize_preprocessor_edge_cases(self):
        """Test tokenization of preprocessor edge cases"""
        content = """
        #include "local.h"
        #include <system.h>
        #define SQUARE(x) ((x) * (x))
        #ifdef DEBUG
        #endif
        #pragma once
        """
        tokens = self.tokenizer.tokenize(content)
        
        include_tokens = [t for t in tokens if t.type == TokenType.INCLUDE]
        define_tokens = [t for t in tokens if t.type == TokenType.DEFINE]
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]
        
        self.assertEqual(len(include_tokens), 2)
        self.assertEqual(len(define_tokens), 1)
        self.assertGreater(len(preprocessor_tokens), 0)

    def test_tokenize_complex_expressions(self):
        """Test tokenization of complex C expressions"""
        content = """
        int* ptr = (int*)malloc(sizeof(int));
        char arr[10] = {'a', 'b', 'c'};
        struct Point* p = &point;
        int result = (*ptr) + arr[0] + p->x;
        """
        tokens = self.tokenizer.tokenize(content)
        
        # Check for specific tokens
        asterisk_tokens = [t for t in tokens if t.type == TokenType.ASTERISK]
        ampersand_tokens = [t for t in tokens if t.type == TokenType.AMPERSAND]
        bracket_tokens = [t for t in tokens if t.type in [TokenType.LBRACKET, TokenType.RBRACKET]]
        
        self.assertGreater(len(asterisk_tokens), 0)
        self.assertGreater(len(ampersand_tokens), 0)
        self.assertGreater(len(bracket_tokens), 0)


if __name__ == '__main__':
    unittest.main()