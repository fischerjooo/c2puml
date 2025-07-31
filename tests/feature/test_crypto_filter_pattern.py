#!/usr/bin/env python3
"""
Crypto Filter Pattern tests.

Comprehensive test suite for verifying the functionality of
crypto filter pattern components.

This test demonstrates the problem with the filter pattern:
"include": ["^crypto.*//.c$", "^crypto.*//.h$"]

The issue is that // is being interpreted as literal forward slashes,
not as a path separator. This test shows the problem and validates the fix.
"""

import os
import tempfile
import unittest
from pathlib import Path

from c2puml.config import Config
from c2puml.parser import CParser
from tests.feature.base import BaseFeatureTest


class TestCryptoFilterPattern(BaseFeatureTest):
    """Test crypto filter pattern functionality"""

    def setUp(self):
        """Set up test environment"""
        super().setUp()
        self.source_folder = Path(self.temp_dir)

        # Create test files
        self.create_test_files()

    def tearDown(self):
        """Clean up test environment"""
        super().tearDown()

    def create_test_files(self):
        """Create test files for the crypto filter test"""
        # Create crypto files
        crypto_files = [
            "Crypto_Cfg_Partitions.c",
            "Crypto_Cfg_JobQueues.c",
            "Crypto.c",
            "Crypto.h",
            "Crypto_Cfg_Partitions.h",
            "Crypto_Cfg_JobQueues.h",
        ]

        # Create non-crypto files
        other_files = ["main.c", "utils.c", "config.h", "types.h"]

        # Create all files
        for filename in crypto_files + other_files:
            file_path = self.source_folder / filename
            with open(file_path, "w") as f:
                f.write(f"// Test file: {filename}\n")
                f.write("#include <stdio.h>\n")
                f.write("// End of file\n")

    def test_broken_crypto_filter_pattern(self):
        """Test the broken filter pattern that doesn't work"""
        # This is the problematic pattern from the user's question
        config = Config(
            source_folders=[str(self.source_folder)],
            file_filters={"include": ["^crypto.*//.c$", "^crypto.*//.h$"]},
        )

        # Test individual files
        crypto_c_files = [
            "Crypto_Cfg_Partitions.c",
            "Crypto_Cfg_JobQueues.c",
            "Crypto.c",
        ]

        crypto_h_files = [
            "Crypto.h",
            "Crypto_Cfg_Partitions.h",
            "Crypto_Cfg_JobQueues.h",
        ]

        # These should NOT match with the broken pattern
        for filename in crypto_c_files + crypto_h_files:
            should_include = config._should_include_file(filename)
            print(f"Broken pattern - {filename}: {should_include}")
            # The broken pattern should NOT match these files
            assert not should_include, f"Broken pattern incorrectly matched {filename}"

    def test_fixed_crypto_filter_pattern(self):
        """Test the corrected filter pattern that should work"""
        # This is the corrected pattern using proper regex
        config = Config(
            source_folders=[str(self.source_folder)],
            file_filters={"include": ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]},
        )

        # Test individual files
        crypto_c_files = [
            "Crypto_Cfg_Partitions.c",
            "Crypto_Cfg_JobQueues.c",
            "Crypto.c",
        ]

        crypto_h_files = [
            "Crypto.h",
            "Crypto_Cfg_Partitions.h",
            "Crypto_Cfg_JobQueues.h",
        ]

        other_files = ["main.c", "utils.c", "config.h", "types.h"]

        # Crypto files should match
        for filename in crypto_c_files + crypto_h_files:
            should_include = config._should_include_file(filename)
            print(f"Fixed pattern - {filename}: {should_include}")
            assert should_include, f"Fixed pattern should match {filename}"

        # Other files should NOT match
        for filename in other_files:
            should_include = config._should_include_file(filename)
            print(f"Fixed pattern - {filename}: {should_include}")
            assert not should_include, f"Fixed pattern should not match {filename}"

    def test_case_insensitive_crypto_filter_pattern(self):
        """Test case-insensitive crypto filter pattern"""
        config = Config(
            source_folders=[str(self.source_folder)],
            file_filters={"include": ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]},
        )

        # Test with different case variations
        test_files = [
            "crypto.c",
            "CRYPTO.c",
            "Crypto.c",
            "crypto_config.c",
            "CRYPTO_CONFIG.c",
            "Crypto_Cfg_Partitions.c",
        ]

        for filename in test_files:
            should_include = config._should_include_file(filename)
            print(f"Case-insensitive pattern - {filename}: {should_include}")
            # All should match with case-insensitive pattern
            assert should_include, f"Case-insensitive pattern should match {filename}"

    def test_alternative_crypto_filter_patterns(self):
        """Test alternative ways to write crypto filter patterns"""
        patterns_to_test = [
            # Pattern 1: Simple crypto prefix
            ["^crypto.*\\.c$", "^crypto.*\\.h$"],
            # Pattern 2: More specific crypto files
            ["^crypto.*cfg.*\\.c$", "^crypto.*cfg.*\\.h$"],
            # Pattern 3: Case-insensitive with word boundaries
            ["(?i)\\bcrypto.*\\.c$", "(?i)\\bcrypto.*\\.h$"],
            # Pattern 4: Match any file containing crypto
            [".*crypto.*\\.c$", ".*crypto.*\\.h$"],
        ]

        for i, patterns in enumerate(patterns_to_test):
            print(f"\nTesting pattern set {i+1}: {patterns}")
            config = Config(
                source_folders=[str(self.source_folder)],
                file_filters={"include": patterns},
            )

            # Test with our crypto files
            crypto_files = [
                "Crypto_Cfg_Partitions.c",
                "Crypto_Cfg_JobQueues.c",
                "Crypto.c",
            ]

            for filename in crypto_files:
                should_include = config._should_include_file(filename)
                print(f"  {filename}: {should_include}")

    def test_parser_integration_with_crypto_filter(self):
        """Test that the parser correctly applies crypto filters"""
        config = Config(
            source_folders=[str(self.source_folder)],
            file_filters={"include": ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]},
        )

        parser = CParser()

        # Parse the project with crypto filter
        project_model = parser.parse_project(
            str(self.source_folder), recursive_search=True, config=config
        )

        # Get the file paths that were actually parsed
        parsed_files = list(project_model.files.keys())
        parsed_filenames = [Path(fp).name for fp in parsed_files]

        print(f"Parsed files: {parsed_filenames}")

        # Should only include crypto .c files (parser starts with .c files only)
        expected_crypto_files = [
            "Crypto_Cfg_Partitions.c",
            "Crypto_Cfg_JobQueues.c",
            "Crypto.c",
        ]

        # Check that all expected crypto files are included
        for expected_file in expected_crypto_files:
            assert (
                expected_file in parsed_filenames
            ), f"Expected {expected_file} to be parsed"

        # Check that non-crypto files are excluded
        non_crypto_files = ["main.c", "utils.c", "config.h", "types.h"]
        for non_crypto_file in non_crypto_files:
            assert (
                non_crypto_file not in parsed_filenames
            ), f"Expected {non_crypto_file} to be excluded"


if __name__ == "__main__":
    # Run the test
    test = TestCryptoFilterPattern()
    test.setup_method()

    print("Testing broken crypto filter pattern:")
    test.test_broken_crypto_filter_pattern()

    print("\nTesting fixed crypto filter pattern:")
    test.test_fixed_crypto_filter_pattern()

    print("\nTesting case-insensitive crypto filter pattern:")
    test.test_case_insensitive_crypto_filter_pattern()

    print("\nTesting alternative crypto filter patterns:")
    test.test_alternative_crypto_filter_patterns()

    print("\nTesting parser integration with crypto filter:")
    test.test_parser_integration_with_crypto_filter()

    test.teardown_method()
    print("\n✅ All tests passed!")
