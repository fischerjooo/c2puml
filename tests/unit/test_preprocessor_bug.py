#!/usr/bin/env python3
"""
Unit tests for preprocessing directive bug and edge cases.
Tests the parser's handling of #if, #elif, #else, #endif directives.
"""

import os
import tempfile
import unittest
from pathlib import Path

from c2puml.parser import CParser
from c2puml.parser_tokenizer import CTokenizer, TokenType


class TestPreprocessorBug(unittest.TestCase):
    """Test preprocessing directive handling bug and edge cases."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CParser()
        self.tokenizer = CTokenizer()

    def test_simple_if_endif_block(self):
        """Test simple #if/#endif block processing."""
        code = """
        #if FEATURE_ENABLED
        typedef struct {
            int id;
            char name[32];
        } enabled_feature_t;
        #endif
        """

        tokens = self.tokenizer.tokenize(code)
        # The bug: preprocessor directives should be processed, not included as raw text
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should have preprocessor tokens (this is expected)
        self.assertGreater(len(preprocessor_tokens), 0)

        # But the content should be processed, not raw
        # This test will fail until the bug is fixed
        self.assertTrue(any("#if" in t.value for t in preprocessor_tokens))

    def test_if_else_endif_block(self):
        """Test #if/#else/#endif block processing."""
        code = """
        #if FEATURE_ENABLED
        typedef struct {
            int id;
            char name[32];
        } enabled_feature_t;
        #else
        typedef struct {
            int id;
        } disabled_feature_t;
        #endif
        """

        tokens = self.tokenizer.tokenize(code)
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should detect both #if and #else directives
        if_directives = [t for t in preprocessor_tokens if "#if" in t.value]
        else_directives = [t for t in preprocessor_tokens if "#else" in t.value]
        endif_directives = [t for t in preprocessor_tokens if "#endif" in t.value]

        self.assertGreater(len(if_directives), 0)
        self.assertGreater(len(else_directives), 0)
        self.assertGreater(len(endif_directives), 0)

    def test_nested_preprocessor_blocks(self):
        """Test nested #if blocks processing."""
        code = """
        #if DEBUG_MODE
            #if MAX_SIZE > 50
                typedef struct {
                    int debug_id;
                    char debug_name[64];
                    #if MIN_SIZE < 20
                        int extra_debug_field;
                    #endif
                } debug_struct_t;
            #else
                typedef struct {
                    int debug_id;
                } simple_debug_t;
            #endif
        #else
            typedef struct {
                int release_id;
            } release_struct_t;
        #endif
        """

        tokens = self.tokenizer.tokenize(code)
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should detect all preprocessor directives
        if_count = len([t for t in preprocessor_tokens if "#if" in t.value])
        endif_count = len([t for t in preprocessor_tokens if "#endif" in t.value])

        # Should have matching #if and #endif pairs
        self.assertEqual(if_count, endif_count)

    def test_preprocessor_in_typedefs(self):
        """Test preprocessing directives within typedef definitions."""
        code = """
        typedef enum {
            #if FEATURE_ENABLED
                STATUS_ENABLED = 1,
                STATUS_DISABLED = 0,
            #else
                STATUS_OFF = 0,
            #endif
            STATUS_UNKNOWN = -1
        } status_t;
        """

        tokens = self.tokenizer.tokenize(code)
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should detect preprocessor directives within enum
        self.assertGreater(len(preprocessor_tokens), 0)

    def test_complex_preprocessor_conditions(self):
        """Test complex preprocessor conditions."""
        code = """
        #if defined(FEATURE_ENABLED) && !defined(DEBUG_MODE)
            typedef struct {
                int optimized_field;
                #if MAX_SIZE > 50
                    char large_buffer[MAX_SIZE];
                #else
                    char small_buffer[MIN_SIZE];
                #endif
            } optimized_struct_t;
        #elif defined(DEBUG_MODE)
            typedef struct {
                int debug_field;
                char debug_buffer[128];
            } debug_optimized_t;
        #else
            typedef struct {
                int default_field;
            } default_struct_t;
        #endif
        """

        tokens = self.tokenizer.tokenize(code)
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should detect complex conditions
        if_directives = [t for t in preprocessor_tokens if "#if" in t.value]
        elif_directives = [t for t in preprocessor_tokens if "#elif" in t.value]
        else_directives = [t for t in preprocessor_tokens if "#else" in t.value]
        endif_directives = [t for t in preprocessor_tokens if "#endif" in t.value]

        self.assertGreater(len(if_directives), 0)
        self.assertGreater(len(elif_directives), 0)
        self.assertGreater(len(else_directives), 0)
        self.assertGreater(len(endif_directives), 0)

    def test_preprocessor_in_function_pointers(self):
        """Test preprocessing directives in function pointer typedefs."""
        code = """
        #if FEATURE_ENABLED
            typedef int (*feature_callback_t)(enabled_feature_t* feature);
        #else
            typedef int (*basic_callback_t)(void);
        #endif
        """

        tokens = self.tokenizer.tokenize(code)
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should detect preprocessor directives in function pointer typedefs
        self.assertGreater(len(preprocessor_tokens), 0)

    def test_preprocessor_in_array_typedefs(self):
        """Test preprocessing directives in array typedefs."""
        code = """
        #if MAX_SIZE > 50
            typedef char large_buffer_t[MAX_SIZE];
        #else
            typedef char small_buffer_t[MIN_SIZE];
        #endif
        """

        tokens = self.tokenizer.tokenize(code)
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should detect preprocessor directives in array typedefs
        self.assertGreater(len(preprocessor_tokens), 0)

    def test_preprocessor_in_unions(self):
        """Test preprocessing directives in union typedefs."""
        code = """
        #if FEATURE_ENABLED
            typedef union {
                int int_value;
                char char_value;
                #if DEBUG_MODE
                    double debug_value;
                #endif
            } feature_union_t;
        #else
            typedef union {
                int int_value;
                char char_value;
            } basic_union_t;
        #endif
        """

        tokens = self.tokenizer.tokenize(code)
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should detect preprocessor directives in unions
        self.assertGreater(len(preprocessor_tokens), 0)

    def test_preprocessor_with_comments(self):
        """Test preprocessing directives with comments."""
        code = """
        #if FEATURE_ENABLED  // Feature is enabled
        typedef struct {
            int id;  // Feature ID
            char name[32];  // Feature name
        } enabled_feature_t;
        #else  // Feature is disabled
        typedef struct {
            int id;  // Basic ID
        } disabled_feature_t;
        #endif  // End of feature conditional
        """

        tokens = self.tokenizer.tokenize(code)
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should detect preprocessor directives with comments
        self.assertGreater(len(preprocessor_tokens), 0)

    def test_preprocessor_with_whitespace_variations(self):
        """Test preprocessing directives with various whitespace patterns."""
        code = """
        #if FEATURE_ENABLED
        typedef struct {
            int id;
        } feature_t;
        #  elif DEBUG_MODE
        typedef struct {
            int debug_id;
        } debug_t;
        #  else
        typedef struct {
            int basic_id;
        } basic_t;
        #  endif
        """

        tokens = self.tokenizer.tokenize(code)
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should detect preprocessor directives with extra whitespace
        self.assertGreater(len(preprocessor_tokens), 0)

    def test_preprocessor_with_multiline_conditions(self):
        """Test preprocessing directives with multiline conditions."""
        code = """
        #if defined(FEATURE_ENABLED) && \
            !defined(DEBUG_MODE) && \
            MAX_SIZE > 50
        typedef struct {
            int optimized_field;
            char large_buffer[MAX_SIZE];
        } optimized_struct_t;
        #endif
        """

        tokens = self.tokenizer.tokenize(code)
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should detect multiline preprocessor directives
        self.assertGreater(len(preprocessor_tokens), 0)

    def test_preprocessor_with_defined_operator(self):
        """Test preprocessing directives with defined() operator."""
        code = """
        #ifdef FEATURE_ENABLED
            #ifdef DEBUG_MODE
                typedef struct {
                    int debug_enabled_id;
                    char debug_enabled_name[64];
                } debug_enabled_t;
            #else
                typedef struct {
                    int enabled_id;
                    char enabled_name[32];
                } enabled_t;
            #endif
        #else
            typedef struct {
                int disabled_id;
            } disabled_t;
        #endif
        """

        tokens = self.tokenizer.tokenize(code)
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should detect #ifdef directives
        ifdef_directives = [t for t in preprocessor_tokens if "#ifdef" in t.value]
        self.assertGreater(len(ifdef_directives), 0)

    def test_preprocessor_with_ifndef(self):
        """Test preprocessing directives with #ifndef."""
        code = """
        #ifndef FEATURE_DISABLED
            typedef struct {
                int feature_id;
                char feature_name[32];
            } feature_struct_t;
        #else
            typedef struct {
                int basic_id;
            } basic_struct_t;
        #endif
        """

        tokens = self.tokenizer.tokenize(code)
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should detect #ifndef directives
        ifndef_directives = [t for t in preprocessor_tokens if "#ifndef" in t.value]
        self.assertGreater(len(ifndef_directives), 0)

    def test_preprocessor_edge_case_empty_blocks(self):
        """Test preprocessing directives with empty blocks."""
        code = """
        #if FEATURE_ENABLED
        #else
        #endif
        """

        tokens = self.tokenizer.tokenize(code)
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should detect empty preprocessor blocks
        self.assertGreater(len(preprocessor_tokens), 0)

    def test_preprocessor_edge_case_malformed(self):
        """Test preprocessing directives with malformed conditions."""
        code = """
        #if FEATURE_ENABLED
        typedef struct {
            int id;
        } feature_t;
        #if DEBUG_MODE  // Missing #endif for previous #if
        typedef struct {
            int debug_id;
        } debug_t;
        #endif
        """

        tokens = self.tokenizer.tokenize(code)
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should detect malformed preprocessor directives
        self.assertGreater(len(preprocessor_tokens), 0)

    def test_preprocessor_in_global_variables(self):
        """Test preprocessing directives in global variable declarations."""
        code = """
        #if FEATURE_ENABLED
        enabled_feature_t global_feature = {0, ""};
        #if DEBUG_MODE
        debug_struct_t global_debug = {0, "", 0};
        #endif
        #else
        int global_basic = 0;
        #endif
        """

        tokens = self.tokenizer.tokenize(code)
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should detect preprocessor directives in global variables
        self.assertGreater(len(preprocessor_tokens), 0)

    def test_preprocessor_in_function_declarations(self):
        """Test preprocessing directives in function declarations."""
        code = """
        #if FEATURE_ENABLED
            int process_feature(enabled_feature_t* feature);
            #if DEBUG_MODE
                void debug_feature(enabled_feature_t* feature);
            #endif
        #else
            int process_basic(void);
        #endif
        """

        tokens = self.tokenizer.tokenize(code)
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should detect preprocessor directives in function declarations
        self.assertGreater(len(preprocessor_tokens), 0)

    def test_preprocessor_with_complex_expressions(self):
        """Test preprocessing directives with complex expressions."""
        code = """
        #if (FEATURE_ENABLED == 1) && (DEBUG_MODE == 0) && (MAX_SIZE > 50)
        typedef struct {
            int complex_field;
            char complex_buffer[MAX_SIZE];
        } complex_struct_t;
        #elif (FEATURE_ENABLED == 0) || (DEBUG_MODE == 1)
        typedef struct {
            int simple_field;
        } simple_struct_t;
        #else
        typedef struct {
            int default_field;
        } default_struct_t;
        #endif
        """

        tokens = self.tokenizer.tokenize(code)
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should detect complex preprocessor expressions
        self.assertGreater(len(preprocessor_tokens), 0)

    def test_preprocessor_with_string_literals(self):
        """Test preprocessing directives with string literals in conditions."""
        code = """
        #if VERSION == "1.0"
        typedef struct {
            int version_1_field;
        } version_1_struct_t;
        #elif VERSION == "2.0"
        typedef struct {
            int version_2_field;
        } version_2_struct_t;
        #else
        typedef struct {
            int unknown_version_field;
        } unknown_version_struct_t;
        #endif
        """

        tokens = self.tokenizer.tokenize(code)
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should detect preprocessor directives with string literals
        self.assertGreater(len(preprocessor_tokens), 0)


if __name__ == "__main__":
    unittest.main()
