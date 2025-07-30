#!/usr/bin/env python3
"""
Unit tests for preprocessor directive handling in C to PlantUML converter

Tests various preprocessor directive scenarios and edge cases to ensure
they are properly ignored while their content is parsed correctly.
"""

import os
import tempfile
import unittest
from pathlib import Path

from c_to_plantuml.parser import CParser
from c_to_plantuml.parser_tokenizer import CTokenizer, TokenType


class TestPreprocessorHandling(unittest.TestCase):
    """Test preprocessor directive handling and edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.parser = CParser()
        self.tokenizer = CTokenizer()

    def test_simple_preprocessor_conditional(self):
        """Test simple #if/#endif block"""
        content = """
        #if (STD_ON == CRYPTO_CFG_BULK_JOB_PROCESSING_ENABLED)
        uint32_t bulk_job_processing_enabled;
        #endif
        
        struct TestStruct {
            int x;
            int y;
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            # Should parse the struct correctly
            self.assertIn("TestStruct", file_model.structs)

            # Should parse the variable from preprocessor block
            global_names = [g.name for g in file_model.globals]
            self.assertIn("bulk_job_processing_enabled", global_names)

            # Check the type
            for global_var in file_model.globals:
                if global_var.name == "bulk_job_processing_enabled":
                    self.assertEqual(global_var.type, "uint32_t")

        finally:
            os.unlink(temp_file)

    def test_preprocessor_with_else_branch(self):
        """Test #if/#else/#endif block"""
        content = """
        #if (STD_ON == CRYPTO_CFG_BULK_JOB_PROCESSING_ENABLED)
        uint32_t bulk_job_processing_enabled;
        #else
        int bulk_job_processing_enabled;
        #endif
        
        struct TestStruct {
            int x;
            int y;
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            # Should parse the struct correctly
            self.assertIn("TestStruct", file_model.structs)

            # Should parse both variables from preprocessor blocks
            global_names = [g.name for g in file_model.globals]
            self.assertEqual(global_names.count("bulk_job_processing_enabled"), 2)

            # Check both types are present
            types = [
                g.type
                for g in file_model.globals
                if g.name == "bulk_job_processing_enabled"
            ]
            self.assertIn("uint32_t", types)
            self.assertIn("int", types)

        finally:
            os.unlink(temp_file)

    def test_multiline_preprocessor_directive(self):
        """Test multiline preprocessor directive"""
        content = """
        #if (STD_ON == CRYPTO_CFG_BULK_JOB_PROCESSING_ENABLED && \\
             CRYPTO_CFG_FEATURE_ENABLED == 1)
        uint32_t bulk_job_processing_enabled;
        #endif
        
        struct TestStruct {
            int x;
            int y;
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            # Should parse the struct correctly
            self.assertIn("TestStruct", file_model.structs)

            # Should parse the variable from preprocessor block
            global_names = [g.name for g in file_model.globals]
            self.assertIn("bulk_job_processing_enabled", global_names)

        finally:
            os.unlink(temp_file)

    def test_nested_preprocessor_blocks(self):
        """Test nested #if blocks"""
        content = """
        #if (STD_ON == CRYPTO_CFG_BULK_JOB_PROCESSING_ENABLED)
            #if (CRYPTO_CFG_FEATURE_ENABLED == 1)
            uint32_t bulk_job_processing_enabled;
            #endif
        #endif
        
        struct TestStruct {
            int x;
            int y;
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            # Should parse the struct correctly
            self.assertIn("TestStruct", file_model.structs)

            # Should parse the variable from nested preprocessor blocks
            global_names = [g.name for g in file_model.globals]
            self.assertIn("bulk_job_processing_enabled", global_names)

        finally:
            os.unlink(temp_file)

    def test_preprocessor_with_elif(self):
        """Test #if/#elif/#else/#endif block"""
        content = """
        #if (STD_ON == CRYPTO_CFG_BULK_JOB_PROCESSING_ENABLED)
        uint32_t bulk_job_processing_enabled;
        #elif (STD_ON == CRYPTO_CFG_FEATURE_ENABLED)
        int bulk_job_processing_enabled;
        #else
        char bulk_job_processing_enabled;
        #endif
        
        struct TestStruct {
            int x;
            int y;
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            # Should parse the struct correctly
            self.assertIn("TestStruct", file_model.structs)

            # Should parse all three variables from preprocessor blocks
            global_names = [g.name for g in file_model.globals]
            self.assertEqual(global_names.count("bulk_job_processing_enabled"), 3)

            # Check all types are present
            types = [
                g.type
                for g in file_model.globals
                if g.name == "bulk_job_processing_enabled"
            ]
            self.assertIn("uint32_t", types)
            self.assertIn("int", types)
            self.assertIn("char", types)

        finally:
            os.unlink(temp_file)

    def test_preprocessor_with_comments(self):
        """Test preprocessor directives with comments"""
        content = """
        #if (STD_ON == CRYPTO_CFG_BULK_JOB_PROCESSING_ENABLED)  // Feature enabled
        uint32_t bulk_job_processing_enabled;  // Bulk processing variable
        #else  // Feature disabled
        int bulk_job_processing_enabled;  // Fallback variable
        #endif  // End of conditional
        
        struct TestStruct {
            int x;
            int y;
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            # Should parse the struct correctly
            self.assertIn("TestStruct", file_model.structs)

            # Should parse both variables from preprocessor blocks
            global_names = [g.name for g in file_model.globals]
            self.assertEqual(global_names.count("bulk_job_processing_enabled"), 2)

        finally:
            os.unlink(temp_file)

    def test_preprocessor_with_structs(self):
        """Test preprocessor directives containing struct definitions"""
        content = """
        #if (STD_ON == CRYPTO_CFG_BULK_JOB_PROCESSING_ENABLED)
        struct BulkJobConfig {
            uint32_t max_jobs;
            uint32_t timeout;
        };
        #else
        struct SimpleJobConfig {
            int max_jobs;
            int timeout;
        };
        #endif
        
        struct TestStruct {
            int x;
            int y;
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            # Should parse all structs
            struct_names = list(file_model.structs.keys())
            self.assertIn("TestStruct", struct_names)
            self.assertIn("BulkJobConfig", struct_names)
            self.assertIn("SimpleJobConfig", struct_names)

        finally:
            os.unlink(temp_file)

    def test_preprocessor_with_functions(self):
        """Test preprocessor directives containing function declarations"""
        content = """
        #if (STD_ON == CRYPTO_CFG_BULK_JOB_PROCESSING_ENABLED)
        uint32_t process_bulk_jobs(uint32_t job_count);
        #else
        int process_simple_jobs(int job_count);
        #endif
        
        struct TestStruct {
            int x;
            int y;
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            # Should parse the struct correctly
            self.assertIn("TestStruct", file_model.structs)

            # Should parse both functions from preprocessor blocks
            function_names = [f.name for f in file_model.functions]
            self.assertIn("process_bulk_jobs", function_names)
            self.assertIn("process_simple_jobs", function_names)

        finally:
            os.unlink(temp_file)

    def test_preprocessor_with_typedefs(self):
        """Test preprocessor directives containing typedef definitions"""
        content = """
        #if (STD_ON == CRYPTO_CFG_BULK_JOB_PROCESSING_ENABLED)
        typedef uint32_t job_id_t;
        typedef struct {
            uint32_t id;
            uint32_t data;
        } bulk_job_t;
        #else
        typedef int job_id_t;
        typedef struct {
            int id;
            int data;
        } simple_job_t;
        #endif
        
        struct TestStruct {
            int x;
            int y;
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            # Should parse the struct correctly
            self.assertIn("TestStruct", file_model.structs)

            # Should parse typedefs from preprocessor blocks
            alias_names = list(file_model.aliases.keys())
            self.assertIn("job_id_t", alias_names)
            # Note: typedef struct might be parsed as struct + typedef separately
            # Check if either the typedef or the struct is found
            struct_names = list(file_model.structs.keys())
            self.assertTrue(
                "bulk_job_t" in alias_names or "bulk_job_t" in struct_names,
                f"bulk_job_t not found in aliases {alias_names} or structs {struct_names}",
            )
            self.assertTrue(
                "simple_job_t" in alias_names or "simple_job_t" in struct_names,
                f"simple_job_t not found in aliases {alias_names} or structs {struct_names}",
            )

        finally:
            os.unlink(temp_file)

    def test_preprocessor_with_enums(self):
        """Test preprocessor directives containing enum definitions"""
        content = """
        #if (STD_ON == CRYPTO_CFG_BULK_JOB_PROCESSING_ENABLED)
        enum BulkJobStatus {
            BULK_JOB_IDLE = 0,
            BULK_JOB_RUNNING = 1,
            BULK_JOB_COMPLETED = 2
        };
        #else
        enum SimpleJobStatus {
            SIMPLE_JOB_IDLE = 0,
            SIMPLE_JOB_RUNNING = 1,
            SIMPLE_JOB_COMPLETED = 2
        };
        #endif
        
        struct TestStruct {
            int x;
            int y;
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            # Should parse the struct correctly
            self.assertIn("TestStruct", file_model.structs)

            # Should parse enums from preprocessor blocks
            enum_names = list(file_model.enums.keys())
            self.assertIn("BulkJobStatus", enum_names)
            self.assertIn("SimpleJobStatus", enum_names)

        finally:
            os.unlink(temp_file)

    def test_preprocessor_with_mixed_content(self):
        """Test preprocessor directives with mixed content types"""
        content = """
        #if (STD_ON == CRYPTO_CFG_BULK_JOB_PROCESSING_ENABLED)
        // Bulk processing configuration
        typedef uint32_t bulk_job_id_t;
        struct BulkJobConfig {
            bulk_job_id_t id;
            uint32_t timeout;
        };
        uint32_t bulk_job_count = 0;
        uint32_t process_bulk_jobs(bulk_job_id_t job_id);
        enum BulkJobState {
            BULK_JOB_READY,
            BULK_JOB_PROCESSING,
            BULK_JOB_DONE
        };
        #else
        // Simple processing configuration
        typedef int simple_job_id_t;
        struct SimpleJobConfig {
            simple_job_id_t id;
            int timeout;
        };
        int simple_job_count = 0;
        int process_simple_jobs(simple_job_id_t job_id);
        enum SimpleJobState {
            SIMPLE_JOB_READY,
            SIMPLE_JOB_PROCESSING,
            SIMPLE_JOB_DONE
        };
        #endif
        
        struct TestStruct {
            int x;
            int y;
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            # Should parse the struct correctly
            self.assertIn("TestStruct", file_model.structs)

            # Should parse all content from both preprocessor branches
            # Check typedefs
            alias_names = list(file_model.aliases.keys())
            self.assertIn("bulk_job_id_t", alias_names)
            self.assertIn("simple_job_id_t", alias_names)

            # Check structs
            struct_names = list(file_model.structs.keys())
            self.assertIn("BulkJobConfig", struct_names)
            self.assertIn("SimpleJobConfig", struct_names)

            # Check globals
            global_names = [g.name for g in file_model.globals]
            self.assertIn("bulk_job_count", global_names)
            self.assertIn("simple_job_count", global_names)

            # Check functions
            function_names = [f.name for f in file_model.functions]
            self.assertIn("process_bulk_jobs", function_names)
            self.assertIn("process_simple_jobs", function_names)

            # Check enums
            enum_names = list(file_model.enums.keys())
            self.assertIn("BulkJobState", enum_names)
            self.assertIn("SimpleJobState", enum_names)

        finally:
            os.unlink(temp_file)

    def test_preprocessor_directive_tokenization(self):
        """Test that preprocessor directives are properly tokenized"""
        content = """
        #if (STD_ON == CRYPTO_CFG_BULK_JOB_PROCESSING_ENABLED)
        uint32_t bulk_job_processing_enabled;
        #else
        int bulk_job_processing_enabled;
        #endif
        """

        tokens = self.tokenizer.tokenize(content)

        # Check that preprocessor directives are tokenized correctly
        preprocessor_tokens = [t for t in tokens if t.type == TokenType.PREPROCESSOR]

        # Should have 3 preprocessor tokens: #if, #else, #endif
        self.assertEqual(len(preprocessor_tokens), 3)

        # Check the values
        directive_values = [t.value.strip() for t in preprocessor_tokens]
        self.assertIn(
            "#if (STD_ON == CRYPTO_CFG_BULK_JOB_PROCESSING_ENABLED)", directive_values
        )
        self.assertIn("#else", directive_values)
        self.assertIn("#endif", directive_values)

    def test_preprocessor_with_whitespace_variations(self):
        """Test preprocessor directives with various whitespace patterns"""
        content = """
        #if(STD_ON==CRYPTO_CFG_BULK_JOB_PROCESSING_ENABLED)
        uint32_t bulk_job_processing_enabled;
        #elif ( STD_ON == CRYPTO_CFG_FEATURE_ENABLED )
        int bulk_job_processing_enabled;
        #else
        char bulk_job_processing_enabled;
        #endif
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            # Should parse all three variables from preprocessor blocks
            global_names = [g.name for g in file_model.globals]
            self.assertEqual(global_names.count("bulk_job_processing_enabled"), 3)

        finally:
            os.unlink(temp_file)

    def test_preprocessor_with_empty_blocks(self):
        """Test preprocessor directives with empty blocks"""
        content = """
        #if (STD_ON == CRYPTO_CFG_BULK_JOB_PROCESSING_ENABLED)
        #else
        int bulk_job_processing_enabled;
        #endif
        
        struct TestStruct {
            int x;
            int y;
        };
        """

        with tempfile.NamedTemporaryFile(mode="w", suffix=".c", delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            file_model = self.parser.parse_file(Path(temp_file), Path(temp_file).name)

            # Should parse the struct correctly
            self.assertIn("TestStruct", file_model.structs)

            # Should parse only the variable from the else block
            global_names = [g.name for g in file_model.globals]
            self.assertEqual(global_names.count("bulk_job_processing_enabled"), 1)

        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    unittest.main()
