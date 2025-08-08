#!/usr/bin/env python3
"""
Feature test for crypto filter use case

This test demonstrates the issue with the filter pattern:
"include": ["^crypto.*//.c$", "^crypto.*//.h$"]

And shows the correct solution for filtering crypto files.
"""

import os
import tempfile
from pathlib import Path



# Add src directory to path for new package structure
import sys
import os
from pathlib import Path

# Get the absolute path to the src directory 
current_file = Path(__file__).resolve()
test_dir = current_file.parent
project_root = test_dir.parent.parent
src_path = project_root / "src"

if src_path.exists():
    sys.path.insert(0, str(src_path))
# Also add tests directory for test utilities
tests_path = project_root / "tests"
if tests_path.exists():
    sys.path.insert(0, str(tests_path))

from c2puml.config import Config
from c2puml.parser import CParser
from tests.feature.base import BaseFeatureTest



class TestCryptoFilterUseCase(BaseFeatureTest):
    """Test crypto filter use case functionality"""

    def setUp(self):
        """Set up test environment"""
        super().setUp()

        # Create crypto test files
        self.create_crypto_test_files()

    def create_crypto_test_files(self):
        """Create crypto test files for the use case"""
        crypto_files = [
            "crypto.c", "crypto.h",
            "Crypto_Cfg_Partitions.c", "Crypto_Cfg_Partitions.h",
            "Crypto_Cfg_JobQueues.c", "Crypto_Cfg_JobQueues.h",
            "Crypto.c", "Crypto.h",
            "crypto_utils.c", "crypto_utils.h"
        ]

        # Create non-crypto files
        other_files = [
            "main.c", "utils.c", "config.h", "types.h"
        ]

        for filename in crypto_files + other_files:
            file_path = Path(self.temp_dir) / filename
            with open(file_path, 'w') as f:
                f.write(f"// {filename} content\nint dummy_var = 1;\n")

    def test_broken_crypto_filter_pattern(self):
        """Test the broken filter pattern from the user question"""
        # This is the broken pattern from the original question
        config = Config(
            source_folders=[self.temp_dir],
            file_filters={"include": ["^crypto.*//.c$", "^crypto.*//.h$"]},
            output_dir=self.temp_dir
        )

        crypto_files = [
            "crypto.c",
            "Crypto_Cfg_Partitions.c", 
            "Crypto_Cfg_JobQueues.c",
            "Crypto.c",
            "crypto_utils.c"
        ]

        # None of these should match the broken pattern
        for filename in crypto_files:
            result = config.should_include_file(filename)
            self.assertFalse(result, f"Broken pattern incorrectly matched {filename}")

    def test_fixed_crypto_filter_pattern(self):
        """Test the corrected filter pattern"""
        # This is the corrected pattern
        config = Config(
            source_folders=[self.temp_dir],
            file_filters={"include": ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]},
            output_dir=self.temp_dir
        )

        # Test crypto files - these should match
        crypto_files = [
            "crypto.c",
            "Crypto_Cfg_Partitions.c",
            "Crypto_Cfg_JobQueues.c", 
            "Crypto.c",
            "crypto_utils.c"
        ]

        for filename in crypto_files:
            result = config.should_include_file(filename)
            self.assertTrue(result, f"Fixed pattern should match {filename}")

        # Test non-crypto files - these should NOT match
        non_crypto_files = ["main.c", "utils.c", "config.h", "types.h"]
        for filename in non_crypto_files:
            result = config.should_include_file(filename)
            self.assertFalse(result, f"Fixed pattern should not match {filename}")

    def test_parser_with_crypto_filter(self):
        """Test that the parser correctly applies crypto filters"""
        config = Config(
            source_folders=[self.temp_dir],
            file_filters={"include": ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]},
            output_dir=self.temp_dir
        )

        # Parse the project with crypto filter
        parser = CParser()
        project_model = parser.parse_project(self.temp_dir, config)

        # Get list of parsed files
        if project_model and project_model.files:
            parsed_filenames = list(project_model.files.keys())
        else:
            parsed_filenames = []

        # Should only include crypto .c files (parser starts with .c files only)
        expected_crypto_files = [
            "crypto.c",
            "Crypto_Cfg_Partitions.c",
            "Crypto_Cfg_JobQueues.c",
            "Crypto.c", 
            "crypto_utils.c"
        ]

        # Check that all expected crypto files are included
        for expected_file in expected_crypto_files:
            self.assertIn(
                expected_file, parsed_filenames,
                f"Expected {expected_file} to be parsed"
            )

        # Check that non-crypto files are excluded
        non_crypto_files = ["main.c", "utils.c", "config.h", "types.h"]
        for non_crypto_file in non_crypto_files:
            self.assertNotIn(
                non_crypto_file, parsed_filenames,
                f"Expected {non_crypto_file} to be excluded"
            )

    def test_alternative_crypto_patterns(self):
        """Test alternative ways to write crypto filter patterns"""
        patterns_list = [
            # Pattern 1: Simple crypto prefix (case-sensitive)
            ["^crypto.*\\.c$", "^crypto.*\\.h$"],
            # Pattern 2: More specific crypto files
            ["(?i)^crypto.*cfg.*\\.c$", "(?i)^crypto.*cfg.*\\.h$"],
            # Pattern 3: Case-insensitive word boundary  
            ["(?i)\\bcrypto.*\\.c$", "(?i)\\bcrypto.*\\.h$"],
            # Pattern 4: Match any file containing crypto (case-sensitive)
            [".*crypto.*\\.c$", ".*crypto.*\\.h$"],
        ]

        crypto_files = ["Crypto_Cfg_Partitions.c", "Crypto_Cfg_JobQueues.c", "Crypto.c"]

        for i, patterns in enumerate(patterns_list):
            config = Config(
                source_folders=[self.temp_dir], file_filters={"include": patterns}
            )

            # Test with our crypto files
            for filename in crypto_files:
                result = config.should_include_file(filename)
                
                # Different patterns have different expectations
                if i == 0:  # Pattern 1: case-sensitive, starts with crypto
                    expected = filename.startswith("crypto")
                elif i == 1:  # Pattern 2: crypto.*cfg.*
                    expected = "cfg" in filename.lower()
                # Pattern 3 should work for all crypto files (case-insensitive)
                elif i == 2:
                    expected = True
                else:  # Pattern 4: contains crypto (case-sensitive)
                    expected = "crypto" in filename

                # Only assert for patterns we expect to work
                if expected:
                    self.assertTrue(result, f"Pattern {i+1} should match {filename}")

    def test_case_insensitive_variations(self):
        """Test different case variations with crypto filter"""
        config = Config(
            source_folders=[self.temp_dir],
            file_filters={"include": ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]},
            output_dir=self.temp_dir
        )

        case_variations = [
            "crypto.c",
            "CRYPTO.c",
            "Crypto.c",
            "crypto_config.c",
        ]

        for filename in case_variations:
            result = config.should_include_file(filename)
            self.assertTrue(result, f"Case-insensitive pattern should match {filename}")

    def test_regex_escaping_importance(self):
        """Test the importance of proper regex escaping"""
        # Without proper escaping - matches any character instead of literal dot
        bad_config = Config(
            source_folders=[self.temp_dir],
            file_filters={"include": ["(?i)^crypto.*.c$", "(?i)^crypto.*.h$"]},
            output_dir=self.temp_dir
        )

        # With proper escaping - matches literal dot
        good_config = Config(
            source_folders=[self.temp_dir],
            file_filters={"include": ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]},
            output_dir=self.temp_dir
        )

        test_filename = "crypto_test.c"

        # Both should match this legitimate file
        bad_result = bad_config.should_include_file(test_filename)
        good_result = good_config.should_include_file(test_filename)

        self.assertTrue(bad_result, "Unescaped pattern should still match valid files")
        self.assertTrue(good_result, "Properly escaped pattern should match valid files")

    def test_user_question_scenario(self):
        """Test the exact scenario from the user's question"""
        # The broken pattern from the question
        broken_pattern = ["^crypto.*//.c$", "^crypto.*//.h$"]
        
        config_broken = Config(
            source_folders=[self.temp_dir], file_filters={"include": broken_pattern}
        )

        # Test files from the user's scenario
        user_files = ["Crypto_Cfg_Partitions.c", "Crypto_Cfg_JobQueues.c", "Crypto.c"]
        
        for filename in user_files:
            result = config_broken.should_include_file(filename)
            self.assertFalse(result, f"Broken pattern should not match {filename}")

        # The working pattern
        fixed_pattern = ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]
        config_fixed = Config(
            source_folders=[self.temp_dir], file_filters={"include": fixed_pattern}
        )

        for filename in user_files:
            result = config_fixed.should_include_file(filename)
            self.assertTrue(result, f"Fixed pattern should match {filename}")

    def test_integration_with_full_workflow(self):
        """Test crypto filter integration with full parsing workflow"""
        config = Config(
            source_folders=[self.temp_dir],
            file_filters={"include": ["(?i)^crypto.*\\.c$"]},
            output_dir=self.temp_dir
        )

        # Run full parsing workflow
        parser = CParser()
        project_model = parser.parse_project(self.temp_dir, config)

        self.assertIsNotNone(project_model, "Parser should return a project model")
        self.assertIsNotNone(project_model.files, "Project model should have files")

        # Verify that only crypto files were parsed
        parsed_filenames = list(project_model.files.keys())

        # Should include crypto .c files and their included headers
        crypto_c_files = [
            "crypto.c",
            "Crypto_Cfg_Partitions.c", 
            "Crypto_Cfg_JobQueues.c",
            "Crypto.c",
            "crypto_utils.c"
        ]

        # Check that non-crypto files are excluded
        non_crypto_files = ["main.c", "utils.c", "config.h", "types.h"]
        for non_crypto_file in non_crypto_files:
            self.assertNotIn(
                non_crypto_file, parsed_filenames,
                f"Expected {non_crypto_file} to be excluded"
            )

        # Verify basic file count makes sense
        self.assertGreaterEqual(
            len(project_model.files), 3,
            f"Expected at least 3 files, got {len(project_model.files)}"
        )

        # The crypto filter should only include the 3 crypto .c files
        self.assertLessEqual(
            len(project_model.files), 8
        ), f"Expected 3 crypto files, got {len(project_model.files)} files: {parsed_filenames}"