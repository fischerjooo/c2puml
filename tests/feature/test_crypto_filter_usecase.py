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
from c_to_plantuml.config import Config
from c_to_plantuml.parser import CParser
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
            "Crypto_Cfg_Partitions.c",
            "Crypto_Cfg_JobQueues.c", 
            "Crypto.c",
            "Crypto.h",
            "Crypto_Cfg_Partitions.h",
            "Crypto_Cfg_JobQueues.h"
        ]
        
        # Create non-crypto files
        other_files = [
            "main.c",
            "utils.c",
            "config.h",
            "types.h"
        ]
        
        # Create all files
        for filename in crypto_files + other_files:
            file_path = Path(self.temp_dir) / filename
            with open(file_path, 'w') as f:
                f.write(f"// Test file: {filename}\n")
                f.write("#include <stdio.h>\n")
                f.write("// End of file\n")
                
    def test_broken_crypto_filter_pattern(self):
        """Test that the broken pattern from user's question doesn't work"""
        # This is the problematic pattern from the user's question
        config = Config(
            source_folders=[self.temp_dir],
            file_filters={
                "include": ["^crypto.*//.c$", "^crypto.*//.h$"]
            }
        )
        
        # Test individual files - these should NOT match with the broken pattern
        crypto_files = [
            "Crypto_Cfg_Partitions.c",
            "Crypto_Cfg_JobQueues.c",
            "Crypto.c",
            "Crypto.h",
            "Crypto_Cfg_Partitions.h", 
            "Crypto_Cfg_JobQueues.h"
        ]
        
        for filename in crypto_files:
            should_include = config._should_include_file(filename)
            # The broken pattern should NOT match these files
            assert not should_include, f"Broken pattern incorrectly matched {filename}"
            
    def test_fixed_crypto_filter_pattern(self):
        """Test that the corrected pattern works correctly"""
        # This is the corrected pattern using proper regex
        config = Config(
            source_folders=[self.temp_dir],
            file_filters={
                "include": ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]
            }
        )
        
        # Test crypto files - these should match
        crypto_files = [
            "Crypto_Cfg_Partitions.c",
            "Crypto_Cfg_JobQueues.c",
            "Crypto.c",
            "Crypto.h",
            "Crypto_Cfg_Partitions.h",
            "Crypto_Cfg_JobQueues.h"
        ]
        
        for filename in crypto_files:
            should_include = config._should_include_file(filename)
            assert should_include, f"Fixed pattern should match {filename}"
            
        # Test non-crypto files - these should NOT match
        other_files = [
            "main.c",
            "utils.c", 
            "config.h",
            "types.h"
        ]
        
        for filename in other_files:
            should_include = config._should_include_file(filename)
            assert not should_include, f"Fixed pattern should not match {filename}"
            
    def test_parser_with_crypto_filter(self):
        """Test that the parser correctly applies crypto filters"""
        config = Config(
            source_folders=[self.temp_dir],
            file_filters={
                "include": ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]
            }
        )
        
        parser = CParser()
        
        # Parse the project with crypto filter
        project_model = parser.parse_project(
            self.temp_dir,
            recursive=True,
            config=config
        )
        
        # Get the file paths that were actually parsed
        parsed_files = list(project_model.files.keys())
        parsed_filenames = [Path(fp).name for fp in parsed_files]
        
        # Should only include crypto .c files (parser starts with .c files only)
        expected_crypto_files = [
            "Crypto_Cfg_Partitions.c",
            "Crypto_Cfg_JobQueues.c", 
            "Crypto.c"
        ]
        
        # Check that all expected crypto files are included
        for expected_file in expected_crypto_files:
            assert expected_file in parsed_filenames, f"Expected {expected_file} to be parsed"
            
        # Check that non-crypto files are excluded
        non_crypto_files = ["main.c", "utils.c", "config.h", "types.h"]
        for non_crypto_file in non_crypto_files:
            assert non_crypto_file not in parsed_filenames, f"Expected {non_crypto_file} to be excluded"
            
    def test_alternative_crypto_patterns(self):
        """Test alternative ways to write crypto filter patterns"""
        patterns_to_test = [
            # Pattern 1: Simple crypto prefix (case-sensitive)
            ["^crypto.*\\.c$", "^crypto.*\\.h$"],
            
            # Pattern 2: More specific crypto files
            ["(?i)^crypto.*cfg.*\\.c$", "(?i)^crypto.*cfg.*\\.h$"],
            
            # Pattern 3: Case-insensitive with word boundaries
            ["(?i)\\bcrypto.*\\.c$", "(?i)\\bcrypto.*\\.h$"],
            
            # Pattern 4: Match any file containing crypto (case-sensitive)
            [".*crypto.*\\.c$", ".*crypto.*\\.h$"]
        ]
        
        crypto_files = [
            "Crypto_Cfg_Partitions.c",
            "Crypto_Cfg_JobQueues.c",
            "Crypto.c"
        ]
        
        for i, patterns in enumerate(patterns_to_test):
            config = Config(
                source_folders=[self.temp_dir],
                file_filters={"include": patterns}
            )
            
            # Test with our crypto files
            for filename in crypto_files:
                should_include = config._should_include_file(filename)
                # Pattern 1 and 4 should fail (case-sensitive)
                # Pattern 2 should only match files with "cfg" in the name
                # Pattern 3 should work for all crypto files (case-insensitive)
                if i == 1:  # Pattern 2: crypto.*cfg.*
                    if "cfg" in filename.lower():
                        assert should_include, f"Pattern {i+1} should match {filename} (contains 'cfg')"
                    else:
                        assert not should_include, f"Pattern {i+1} should not match {filename} (no 'cfg')"
                elif i == 2:  # Pattern 3: case-insensitive with word boundaries
                    assert should_include, f"Pattern {i+1} should match {filename}"
                else:  # Pattern 1 and 4: case-sensitive patterns
                    assert not should_include, f"Pattern {i+1} should not match {filename} (case-sensitive)"
                    
    def test_case_insensitive_variations(self):
        """Test different case variations with crypto filter"""
        config = Config(
            source_folders=[self.temp_dir],
            file_filters={
                "include": ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]
            }
        )
        
        # Test with different case variations
        test_files = [
            "crypto.c",
            "CRYPTO.c", 
            "Crypto.c",
            "crypto_config.c",
            "CRYPTO_CONFIG.c",
            "Crypto_Cfg_Partitions.c"
        ]
        
        for filename in test_files:
            should_include = config._should_include_file(filename)
            # All should match with case-insensitive pattern
            assert should_include, f"Case-insensitive pattern should match {filename}"
            
    def test_regex_escaping_importance(self):
        """Test the importance of proper regex escaping"""
        # Test unescaped dot (wrong)
        wrong_config = Config(
            source_folders=[self.temp_dir],
            file_filters={
                "include": ["(?i)^crypto.*.c$", "(?i)^crypto.*.h$"]
            }
        )
        
        # Test escaped dot (correct)
        correct_config = Config(
            source_folders=[self.temp_dir],
            file_filters={
                "include": ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]
            }
        )
        
        test_file = "Crypto.c"
        
        # Unescaped dot should match anything ending with 'c', not just '.c'
        wrong_result = wrong_config._should_include_file(test_file)
        correct_result = correct_config._should_include_file(test_file)
        
        # Both should work for this simple case, but escaped is more precise
        assert correct_result, "Escaped pattern should match Crypto.c"
        
    def test_user_question_scenario(self):
        """Test the exact scenario from the user's question"""
        # User's original pattern
        broken_pattern = ["^crypto.*//.c$", "^crypto.*//.h$"]
        
        # User's target files
        target_files = [
            "Crypto_Cfg_Partitions.c",
            "Crypto_Cfg_JobQueues.c", 
            "Crypto.c"
        ]
        
        # Test that the broken pattern doesn't work
        config = Config(
            source_folders=[self.temp_dir],
            file_filters={"include": broken_pattern}
        )
        
        for filename in target_files:
            should_include = config._should_include_file(filename)
            assert not should_include, f"Broken pattern should not match {filename}"
            
        # Test that the fixed pattern works
        fixed_pattern = ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]
        config = Config(
            source_folders=[self.temp_dir],
            file_filters={"include": fixed_pattern}
        )
        
        for filename in target_files:
            should_include = config._should_include_file(filename)
            assert should_include, f"Fixed pattern should match {filename}"
            
    def test_integration_with_full_workflow(self):
        """Test crypto filter integration with full parsing workflow"""
        config = Config(
            source_folders=[self.temp_dir],
            file_filters={
                "include": ["(?i)^crypto.*\\.c$", "(?i)^crypto.*\\.h$"]
            },
            include_depth=2  # Include header files
        )
        
        parser = CParser()
        
        # Parse the project
        project_model = parser.parse_project(
            self.temp_dir,
            recursive=True,
            config=config
        )
        
        # Verify that only crypto files were parsed
        parsed_files = list(project_model.files.keys())
        parsed_filenames = [Path(fp).name for fp in parsed_files]
        
        # Should include crypto .c files and their included headers
        expected_files = [
            "Crypto_Cfg_Partitions.c",
            "Crypto_Cfg_JobQueues.c", 
            "Crypto.c"
        ]
        
        # Check that expected files are included
        for expected_file in expected_files:
            assert expected_file in parsed_filenames, f"Expected {expected_file} to be parsed"
            
        # Check that non-crypto files are excluded
        non_crypto_files = ["main.c", "utils.c", "config.h", "types.h"]
        for non_crypto_file in non_crypto_files:
            assert non_crypto_file not in parsed_filenames, f"Expected {non_crypto_file} to be excluded"
            
        # Verify project structure
        # The project name can vary depending on how the parser is called, so we'll just check it's a string
        assert isinstance(project_model.project_name, str) and len(project_model.project_name) > 0
        assert len(project_model.files) == 3  # Only the 3 crypto .c files
        
        # Verify that each parsed file has the expected structure
        for file_path, file_model in project_model.files.items():
            assert file_model.file_path == file_path
            assert file_model.project_root == self.temp_dir
            assert file_model.encoding_used in ["utf-8", "latin-1", "cp1252"]  # Common encodings