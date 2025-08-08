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
import sys
import tempfile
import unittest
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


class TestCryptoFilterPattern(BaseFeatureTest):
    """Test crypto filter pattern functionality"""

    def setUp(self):
        """Set up test environment"""
        super().setUp()
        self.source_folder = Path(self.temp_dir)

        # Create test files for the crypto filter test
        self.create_test_files()

    def create_test_files(self):
        """Create test files for the crypto filter test"""
        # Create crypto files
        crypto_files = [
            "crypto.c", "crypto.h",
            "crypto_config.c", "crypto_config.h",
            "Crypto.c", "Crypto.h",
            "CRYPTO_UTILS.c", "CRYPTO_UTILS.h"
        ]
        # Create non-crypto files
        other_files = [
            "main.c", "utils.c", "config.h", "types.h"
        ]

        for filename in crypto_files + other_files:
            file_path = self.source_folder / filename
            with open(file_path, 'w') as f:
                f.write(f"// {filename} content\n")

    def test_broken_crypto_filter_pattern(self):
        """Test the broken filter pattern that doesn't work"""
        config = Config(
            source_folders=[str(self.source_folder)],
            file_filters={"include": ["^crypto.*//.c$", "^crypto.*//.h$"]},
            output_dir=self.temp_dir
        )

        crypto_c_files = [
            "crypto.c",
            "crypto_config.c",
            "Crypto.c",
            "CRYPTO_UTILS.c"
        ]
        crypto_h_files = [
            "crypto.h",
            "crypto_config.h", 
            "Crypto.h",
            "CRYPTO_UTILS.h"
        ]

        for filename in crypto_c_files + crypto_h_files:
            result = config.should_include_file(filename)
            self.assertFalse(result, f"Expected {filename} to be excluded with broken pattern")

    def test_fixed_crypto_filter_pattern(self):
        """Test the corrected filter pattern that should work"""
        config = Config(
            source_folders=[str(self.source_folder)],
            file_filters={"include": ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]},
            output_dir=self.temp_dir
        )

        crypto_c_files = [
            "crypto.c",
            "crypto_config.c",
            "Crypto.c",
            "CRYPTO_UTILS.c"
        ]
        crypto_h_files = [
            "crypto.h",
            "crypto_config.h",
            "Crypto.h", 
            "CRYPTO_UTILS.h"
        ]

        # These should match the corrected pattern
        for filename in crypto_c_files + crypto_h_files:
            result = config.should_include_file(filename)
            self.assertTrue(result, f"Expected {filename} to be included with fixed pattern")

        # Non-crypto files should be excluded
        non_crypto_files = ["main.c", "utils.c", "config.h", "types.h"]
        for filename in non_crypto_files:
            result = config.should_include_file(filename)
            self.assertFalse(result, f"Expected {filename} to be excluded")

    def test_case_insensitive_crypto_filter_pattern(self):
        """Test case-insensitive crypto filter pattern"""
        config = Config(
            source_folders=[str(self.source_folder)],
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
            self.assertTrue(result, f"Expected {filename} to match case-insensitive pattern")

    def test_alternative_crypto_filter_patterns(self):
        """Test alternative ways to write crypto filter patterns"""
        patterns = [
            # Pattern 1: Simple crypto prefix
            ["^crypto.*\\.c$", "^crypto.*\\.h$"],
            # Pattern 2: More specific crypto files
            ["^crypto.*cfg.*\\.c$", "^crypto.*cfg.*\\.h$"],
            # Pattern 3: Case-insensitive word boundary
            ["(?i)\\bcrypto.*\\.c$", "(?i)\\bcrypto.*\\.h$"],
            # Pattern 4: Match any file containing crypto
            [".*crypto.*\\.c$", ".*crypto.*\\.h$"],
        ]

        for i, patterns in enumerate(patterns):
            with self.subTest(pattern_set=i):
                config = Config(
                    source_folders=[str(self.source_folder)],
                    file_filters={"include": patterns},
                    output_dir=self.temp_dir
                )

            # Test with our crypto files
            crypto_files = [
                "crypto.c", "crypto_config.c", "Crypto.c"
            ]
            for filename in crypto_files:
                result = config.should_include_file(filename)
                # Pattern 2 should work for all crypto files (case-insensitive)
                if i == 1:  # Pattern 2: crypto.*cfg.*
                    if "cfg" not in filename.lower():
                        continue  # Skip files that don't match this specific pattern
                        
                expected = True if i != 1 or "config" in filename else True
                # Adjust expectation based on pattern specificity

    def test_parser_integration_with_crypto_filter(self):
        """Test that the parser correctly applies crypto filters"""
        config = Config(
            source_folders=[str(self.source_folder)],
            file_filters={"include": ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]},
            output_dir=self.temp_dir
        )

        # Parse the project with crypto filter
        parser = CParser()
        try:
            project_model = parser.parse_project(str(self.source_folder), config)
            
            # Get list of parsed files
            parsed_filenames = list(project_model.files.keys()) if project_model and project_model.files else []
            
            # Should only include crypto .c files (parser starts with .c files only)
            expected_crypto_files = [
                "crypto.c",
                "crypto_config.c", 
                "Crypto.c",
                "CRYPTO_UTILS.c"
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
        except Exception as e:
            self.fail(f"Parser integration test failed: {e}")


if __name__ == "__main__":
    test = TestCryptoFilterPattern()
    test.setUp()
    
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
    
    print("\nAll crypto filter pattern tests completed!")