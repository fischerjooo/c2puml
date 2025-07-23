#!/usr/bin/env python3
"""
Integration tests for parser and tokenizer using real example files
"""

import os
import unittest
from pathlib import Path

from c_to_plantuml.parser import CParser
from c_to_plantuml.parser_tokenizer import CTokenizer, StructureFinder, TokenType


class TestParserTokenizerIntegration(unittest.TestCase):
    """Integration tests for parser and tokenizer"""

    def setUp(self):
        self.parser = CParser()
        self.tokenizer = CTokenizer()
        
        # Get the example source directory
        self.example_dir = Path(__file__).parent.parent.parent / "example" / "source"
        self.assertTrue(self.example_dir.exists(), f"Example directory not found: {self.example_dir}")

    def test_tokenize_sample_c_file(self):
        """Test tokenizing the sample.c file"""
        sample_c_path = self.example_dir / "sample.c"
        self.assertTrue(sample_c_path.exists(), f"sample.c not found: {sample_c_path}")
        
        with open(sample_c_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        tokens = self.tokenizer.tokenize(content)
        
        # Check that we have tokens
        self.assertGreater(len(tokens), 0)
        
        # Check for specific token types we expect in sample.c
        token_types = set(t.type for t in tokens)
        expected_types = {
            TokenType.INCLUDE, TokenType.DEFINE, TokenType.COMMENT,
            TokenType.IDENTIFIER,
            TokenType.NUMBER, TokenType.LBRACE, TokenType.RBRACE,
            TokenType.LPAREN, TokenType.RPAREN, TokenType.SEMICOLON,
            TokenType.INT, TokenType.CHAR, TokenType.ASTERISK, TokenType.VOID,
            TokenType.STATIC, TokenType.CONST,
            TokenType.WHITESPACE, TokenType.NEWLINE, TokenType.EOF
        }
        
        for expected_type in expected_types:
            self.assertIn(expected_type, token_types, f"Missing token type: {expected_type}")

    def test_tokenize_sample_h_file(self):
        """Test tokenizing the sample.h file"""
        sample_h_path = self.example_dir / "sample.h"
        self.assertTrue(sample_h_path.exists(), f"sample.h not found: {sample_h_path}")
        
        with open(sample_h_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        tokens = self.tokenizer.tokenize(content)
        
        # Check that we have tokens
        self.assertGreater(len(tokens), 0)
        
        # Check for specific token types we expect in sample.h
        token_types = set(t.type for t in tokens)
        expected_types = {
            TokenType.INCLUDE, TokenType.DEFINE, TokenType.COMMENT,
            TokenType.TYPEDEF, TokenType.STRUCT,
            TokenType.IDENTIFIER, TokenType.NUMBER,
            TokenType.LBRACE, TokenType.RBRACE, TokenType.SEMICOLON,
            TokenType.INT, TokenType.CHAR, TokenType.EXTERN, TokenType.CONST,
            TokenType.WHITESPACE, TokenType.NEWLINE, TokenType.EOF
        }
        
        for expected_type in expected_types:
            self.assertIn(expected_type, token_types, f"Missing token type: {expected_type}")

    def test_find_structures_in_sample_files(self):
        """Test finding structures in sample files"""
        sample_files = ["sample.c", "sample.h", "typedef_test.c", "typedef_test.h"]
        
        for filename in sample_files:
            file_path = self.example_dir / filename
            if not file_path.exists():
                continue
                
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            tokens = self.tokenizer.tokenize(content)
            finder = StructureFinder(tokens)
            
            # Find structs
            structs = finder.find_structs()
            self.assertIsInstance(structs, list)
            
            # Find enums
            enums = finder.find_enums()
            self.assertIsInstance(enums, list)
            
            # Find functions
            functions = finder.find_functions()
            self.assertIsInstance(functions, list)

    def test_parse_sample_c_file(self):
        """Test parsing the sample.c file"""
        sample_c_path = self.example_dir / "sample.c"
        self.assertTrue(sample_c_path.exists(), f"sample.c not found: {sample_c_path}")
        
        file_model = self.parser.parse_file(
            sample_c_path, sample_c_path.name, str(sample_c_path.parent)
        )
        
        # Check that we parsed something
        self.assertIsNotNone(file_model)
        
        # Check for expected functions from sample.c
        func_names = [f.name for f in file_model.functions]
        expected_functions = ["internal_helper", "calculate_sum", "create_point", "process_point", "demo_triangle_usage", "main"]
        
        for expected_func in expected_functions:
            self.assertIn(expected_func, func_names, f"Missing function: {expected_func}")
        
        # Check for globals
        global_names = [g.name for g in file_model.globals]
        expected_globals = ["global_counter", "buffer", "global_ptr"]
        
        for expected_global in expected_globals:
            self.assertIn(expected_global, global_names, f"Missing global: {expected_global}")
        
        # Check for includes
        self.assertGreaterEqual(len(file_model.includes), 3)

    def test_parse_sample_h_file(self):
        """Test parsing the sample.h file"""
        sample_h_path = self.example_dir / "sample.h"
        self.assertTrue(sample_h_path.exists(), f"sample.h not found: {sample_h_path}")
        
        file_model = self.parser.parse_file(
            sample_h_path, sample_h_path.name, str(sample_h_path.parent)
        )
        
        # Check that we parsed something
        self.assertIsNotNone(file_model)
        
        # Check for expected structs from sample.h
        self.assertIn("point_t", file_model.structs)
        point_struct = file_model.structs["point_t"]
        self.assertEqual(len(point_struct.fields), 3)
        
        # Check field names
        field_names = [field.name for field in point_struct.fields]
        self.assertIn("x", field_names)
        self.assertIn("y", field_names)
        self.assertIn("label", field_names)
        
        # Check for expected enums
        self.assertIn("system_state_t", file_model.enums)
        system_state_enum = file_model.enums["system_state_t"]
        self.assertEqual(len(system_state_enum.values), 3)
        
        # Check enum values
        enum_value_names = [value.name for value in system_state_enum.values]
        self.assertIn("STATE_IDLE", enum_value_names)
        self.assertIn("STATE_RUNNING", enum_value_names)
        self.assertIn("STATE_ERROR", enum_value_names)
        
        # Check for function declarations
        func_names = [f.name for f in file_model.functions]
        expected_functions = ["calculate_sum", "create_point", "process_point"]
        
        for expected_func in expected_functions:
            self.assertIn(expected_func, func_names, f"Missing function: {expected_func}")

    def test_parse_typedef_test_files(self):
        """Test parsing typedef test files"""
        typedef_test_c_path = self.example_dir / "typedef_test.c"
        typedef_test_h_path = self.example_dir / "typedef_test.h"
        
        if typedef_test_c_path.exists():
            file_model = self.parser.parse_file(
                typedef_test_c_path, typedef_test_c_path.name, str(typedef_test_c_path.parent)
            )
            
            # Check for expected functions
            func_names = [f.name for f in file_model.functions]
            expected_functions = ["log_buffer", "process_buffer", "my_callback", "create_complex", "main"]
            
            for expected_func in expected_functions:
                self.assertIn(expected_func, func_names, f"Missing function: {expected_func}")
        
        if typedef_test_h_path.exists():
            file_model = self.parser.parse_file(
                typedef_test_h_path, typedef_test_h_path.name, str(typedef_test_h_path.parent)
            )
            
            # Check for expected typedefs
            self.assertGreaterEqual(len(file_model.aliases), 5)
            
            # Check for expected structs
            self.assertIn("MyBuffer", file_model.structs)
            self.assertIn("MyComplex", file_model.structs)
            self.assertIn("Point_t", file_model.structs)
            self.assertIn("NamedStruct_t", file_model.structs)
            
            # Check for expected enums
            self.assertIn("Color_t", file_model.enums)
            self.assertIn("Status_t", file_model.enums)
            
            # Check for expected unions
            self.assertIn("Number_t", file_model.unions)
            self.assertIn("NamedUnion_t", file_model.unions)

    def test_parse_all_example_files(self):
        """Test parsing all example files"""
        c_files = list(self.example_dir.glob("*.c"))
        h_files = list(self.example_dir.glob("*.h"))
        
        all_files = c_files + h_files
        self.assertGreater(len(all_files), 0, "No example files found")
        
        for file_path in all_files:
            try:
                file_model = self.parser.parse_file(
                    file_path, file_path.name, str(file_path.parent)
                )
                
                # Basic validation that parsing didn't crash
                self.assertIsNotNone(file_model)
                self.assertIsInstance(file_model.structs, dict)
                self.assertIsInstance(file_model.enums, dict)
                self.assertIsInstance(file_model.unions, dict)
                self.assertIsInstance(file_model.functions, list)
                self.assertIsInstance(file_model.globals, list)
                self.assertIsInstance(file_model.includes, list)
                self.assertIsInstance(file_model.macros, list)
                self.assertIsInstance(file_model.aliases, dict)
                
            except Exception as e:
                self.fail(f"Failed to parse {file_path}: {e}")

    def test_tokenizer_parser_consistency(self):
        """Test that tokenizer and parser produce consistent results"""
        sample_c_path = self.example_dir / "sample.c"
        if not sample_c_path.exists():
            self.skipTest("sample.c not found")
        
        with open(sample_c_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Tokenize the content
        tokens = self.tokenizer.tokenize(content)
        filtered_tokens = self.tokenizer.filter_tokens(tokens)
        
        # Use StructureFinder to find structures
        finder = StructureFinder(filtered_tokens)
        tokenizer_structs = finder.find_structs()
        tokenizer_enums = finder.find_enums()
        tokenizer_functions = finder.find_functions()
        
        # Parse the same file with the parser
        file_model = self.parser.parse_file(
            sample_c_path, sample_c_path.name, str(sample_c_path.parent)
        )
        
        # Compare results - they should be consistent
        # Note: The parser might find more structures due to more sophisticated parsing
        self.assertGreaterEqual(len(file_model.structs), len(tokenizer_structs))
        self.assertGreaterEqual(len(file_model.enums), len(tokenizer_enums))
        self.assertGreaterEqual(len(file_model.functions), len(tokenizer_functions))

    def test_parse_complex_example_file(self):
        """Test parsing the complex_example.h file"""
        complex_example_path = self.example_dir / "complex_example.h"
        if not complex_example_path.exists():
            self.skipTest("complex_example.h not found")
        
        file_model = self.parser.parse_file(
            complex_example_path, complex_example_path.name, str(complex_example_path.parent)
        )
        
        # Basic validation
        self.assertIsNotNone(file_model)
        self.assertIsInstance(file_model.structs, dict)
        self.assertIsInstance(file_model.enums, dict)
        self.assertIsInstance(file_model.functions, list)

    def test_parse_geometry_files(self):
        """Test parsing geometry files"""
        geometry_c_path = self.example_dir / "geometry.c"
        geometry_h_path = self.example_dir / "geometry.h"
        
        if geometry_c_path.exists():
            file_model = self.parser.parse_file(
                geometry_c_path, geometry_c_path.name, str(geometry_c_path.parent)
            )
            
            # Check for expected functions
            func_names = [f.name for f in file_model.functions]
            expected_functions = ["create_triangle", "triangle_area"]
            
            for expected_func in expected_functions:
                self.assertIn(expected_func, func_names, f"Missing function: {expected_func}")
        
        if geometry_h_path.exists():
            file_model = self.parser.parse_file(
                geometry_h_path, geometry_h_path.name, str(geometry_h_path.parent)
            )
            
            # Check for expected structs
            self.assertIn("triangle_t", file_model.structs)
            triangle_struct = file_model.structs["triangle_t"]
            self.assertGreaterEqual(len(triangle_struct.fields), 2)  # At least 2 fields

    def test_parse_logger_files(self):
        """Test parsing logger files"""
        logger_c_path = self.example_dir / "logger.c"
        logger_h_path = self.example_dir / "logger.h"
        
        if logger_c_path.exists():
            file_model = self.parser.parse_file(
                logger_c_path, logger_c_path.name, str(logger_c_path.parent)
            )
            
            # Check for expected functions
            func_names = [f.name for f in file_model.functions]
            expected_functions = ["log_message"]
            
            for expected_func in expected_functions:
                self.assertIn(expected_func, func_names, f"Missing function: {expected_func}")
        
        if logger_h_path.exists():
            file_model = self.parser.parse_file(
                logger_h_path, logger_h_path.name, str(logger_h_path.parent)
            )
            
            # Check for expected enums
            self.assertIn("log_level_t", file_model.enums)
            log_level_enum = file_model.enums["log_level_t"]
            self.assertGreaterEqual(len(log_level_enum.values), 3)

    def test_parse_math_utils_files(self):
        """Test parsing math_utils files"""
        math_utils_c_path = self.example_dir / "math_utils.c"
        math_utils_h_path = self.example_dir / "math_utils.h"
        
        if math_utils_c_path.exists():
            file_model = self.parser.parse_file(
                math_utils_c_path, math_utils_c_path.name, str(math_utils_c_path.parent)
            )
            
            # Check for expected functions
            func_names = [f.name for f in file_model.functions]
            expected_functions = ["add", "subtract", "average"]  # Updated based on actual content
            
            for expected_func in expected_functions:
                self.assertIn(expected_func, func_names, f"Missing function: {expected_func}")
        
        if math_utils_h_path.exists():
            file_model = self.parser.parse_file(
                math_utils_h_path, math_utils_h_path.name, str(math_utils_h_path.parent)
            )
            
            # Check for function declarations
            func_names = [f.name for f in file_model.functions]
            expected_functions = ["add", "subtract", "average"]  # Updated based on actual content
            
            for expected_func in expected_functions:
                self.assertIn(expected_func, func_names, f"Missing function: {expected_func}")

    def test_parse_config_file(self):
        """Test parsing config.h file"""
        config_path = self.example_dir / "config.h"
        if not config_path.exists():
            self.skipTest("config.h not found")
        
        file_model = self.parser.parse_file(
            config_path, config_path.name, str(config_path.parent)
        )
        
        # Check for macros
        self.assertGreaterEqual(len(file_model.macros), 1)
        
        # Check for includes
        self.assertGreaterEqual(len(file_model.includes), 1)

    def test_end_to_end_parsing_workflow(self):
        """Test the complete parsing workflow from tokenization to model generation"""
        sample_c_path = self.example_dir / "sample.c"
        if not sample_c_path.exists():
            self.skipTest("sample.c not found")
        
        with open(sample_c_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Step 1: Tokenize
        tokens = self.tokenizer.tokenize(content)
        self.assertGreater(len(tokens), 0)
        
        # Step 2: Filter tokens
        filtered_tokens = self.tokenizer.filter_tokens(tokens)
        self.assertGreater(len(filtered_tokens), 0)
        
        # Step 3: Find structures
        finder = StructureFinder(filtered_tokens)
        structs = finder.find_structs()
        enums = finder.find_enums()
        functions = finder.find_functions()
        
        # Step 4: Parse with parser
        file_model = self.parser.parse_file(
            sample_c_path, sample_c_path.name, str(sample_c_path.parent)
        )
        
        # Step 5: Validate results
        self.assertIsNotNone(file_model)
        self.assertIsInstance(file_model.structs, dict)
        self.assertIsInstance(file_model.enums, dict)
        self.assertIsInstance(file_model.functions, list)
        self.assertIsInstance(file_model.globals, list)
        
        # Step 6: Check that we found the expected content
        self.assertGreaterEqual(len(file_model.functions), 6)  # sample.c has 6 functions
        self.assertGreaterEqual(len(file_model.globals), 3)    # sample.c has 3 globals


if __name__ == '__main__':
    unittest.main()