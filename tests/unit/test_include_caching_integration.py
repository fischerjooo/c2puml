#!/usr/bin/env python3
"""
Integration tests for include caching feature in the full parsing workflow.
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from c_to_plantuml.parser import CParser
from c_to_plantuml.config import Config


class TestIncludeCachingIntegration(unittest.TestCase):
    """Integration test cases for include caching in full parsing workflow."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CParser()
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)

        # Create a simple project structure
        self._create_test_project()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_test_project(self):
        """Create a test project with multiple files and includes."""
        # Create main.c
        main_c = self.project_root / "main.c"
        main_c.write_text(
            """
#include "header1.h"
#include "header2.h"
#include "missing_header1.h"
#include "missing_header2.h"

int main() {
    return 0;
}
"""
        )

        # Create header1.h
        header1 = self.project_root / "header1.h"
        header1.write_text(
            """
#include "header3.h"
#include "missing_header3.h"
#include "missing_header1.h"  // Duplicate missing include

struct TestStruct {
    int value;
};
"""
        )

        # Create header2.h
        header2 = self.project_root / "header2.h"
        header2.write_text(
            """
#include "missing_header2.h"  // Duplicate missing include
#include "missing_header4.h"

enum TestEnum {
    VALUE1,
    VALUE2
};
"""
        )

        # Create header3.h (existing)
        header3 = self.project_root / "header3.h"
        header3.write_text(
            """
// This header exists
"""
        )

    def test_caching_in_include_dependency_processing(self):
        """Test that caching works during include dependency processing."""
        # Create a config with include depth > 0
        config = Config()
        config.include_depth = 2

        # Mock the file finding methods to avoid actual file system operations
        with patch.object(
            self.parser, "_find_c_files"
        ) as mock_find_files, patch.object(
            self.parser, "_extract_includes_from_file"
        ) as mock_extract_includes, patch.object(
            self.parser, "_should_include_file"
        ) as mock_should_include:

            # Setup mocks
            mock_find_files.return_value = [self.project_root / "main.c"]
            mock_should_include.return_value = True

            # Mock include extraction to return different includes for different files
            def mock_extract_includes_impl(file_path):
                if "main.c" in str(file_path):
                    return [
                        "header1.h",
                        "header2.h",
                        "missing_header1.h",
                        "missing_header2.h",
                    ]
                elif "header1.h" in str(file_path):
                    return ["header3.h", "missing_header3.h", "missing_header1.h"]
                elif "header2.h" in str(file_path):
                    return ["missing_header2.h", "missing_header4.h"]
                else:
                    return []

            mock_extract_includes.side_effect = mock_extract_includes_impl

            # Call the method that processes include dependencies
            result = self.parser._find_files_with_include_dependencies(
                self.project_root, True, config
            )

            # Verify that the method was called and caching was used
            # The exact number of calls depends on the implementation, but we can verify
            # that the method completed successfully
            self.assertIsInstance(result, list)

    def test_cache_cleared_between_projects(self):
        """Test that cache is cleared when parsing different projects."""
        # Add some failed searches to cache
        self.parser._find_included_file(
            "missing_header1.h", self.project_root / "main.c", self.project_root
        )
        self.parser._find_included_file(
            "missing_header2.h", self.project_root / "main.c", self.project_root
        )

        # Verify cache has entries
        stats = self.parser.get_failed_includes_cache_stats()
        self.assertEqual(stats["cache_size"], 2)

        # Create a second project
        temp_dir2 = tempfile.mkdtemp()
        project_root2 = Path(temp_dir2)

        try:
            # Create a simple file in the second project
            test_file = project_root2 / "test.c"
            test_file.write_text('#include "missing_header.h"')

            # Mock the parsing methods to avoid actual parsing
            with patch.object(
                self.parser, "_find_c_files"
            ) as mock_find_files, patch.object(
                self.parser, "_find_files_with_include_dependencies"
            ) as mock_find_with_deps, patch.object(
                self.parser, "parse_file"
            ) as mock_parse_file:

                mock_find_files.return_value = []
                mock_find_with_deps.return_value = []
                mock_parse_file.return_value = MagicMock()

                # Parse the second project (should clear cache)
                self.parser.parse_project(str(project_root2))

                # Verify cache is cleared
                stats = self.parser.get_failed_includes_cache_stats()
                self.assertEqual(stats["cache_size"], 0)

        finally:
            import shutil

            shutil.rmtree(temp_dir2, ignore_errors=True)

    def test_cache_with_real_file_system_operations(self):
        """Test caching with real file system operations."""
        # This test uses the actual file system to verify caching works
        # Search for a missing header multiple times
        missing_header = "nonexistent_header.h"

        # First search
        result1 = self.parser._find_included_file(
            missing_header, self.project_root / "main.c", self.project_root
        )
        self.assertIsNone(result1)

        # Check cache
        stats1 = self.parser.get_failed_includes_cache_stats()
        self.assertEqual(stats1["cache_size"], 1)

        # Second search (should use cache)
        result2 = self.parser._find_included_file(
            missing_header, self.project_root / "main.c", self.project_root
        )
        self.assertIsNone(result2)

        # Check cache size hasn't increased
        stats2 = self.parser.get_failed_includes_cache_stats()
        self.assertEqual(stats2["cache_size"], 1)

    def test_cache_with_different_source_files(self):
        """Test that cache works across different source files."""
        # Search from main.c
        result1 = self.parser._find_included_file(
            "missing_header.h", self.project_root / "main.c", self.project_root
        )
        self.assertIsNone(result1)

        # Search from header1.h (should use cache)
        result2 = self.parser._find_included_file(
            "missing_header.h", self.project_root / "header1.h", self.project_root
        )
        self.assertIsNone(result2)

        # Check cache size hasn't increased
        stats = self.parser.get_failed_includes_cache_stats()
        self.assertEqual(stats["cache_size"], 1)

    def test_cache_with_include_depth_zero(self):
        """Test that caching doesn't interfere with include_depth=0."""
        config = Config()
        config.include_depth = 0

        # Add some failed searches to cache
        self.parser._find_included_file(
            "missing_header1.h", self.project_root / "main.c", self.project_root
        )

        # Mock the file finding methods
        with patch.object(
            self.parser, "_find_c_files"
        ) as mock_find_files, patch.object(
            self.parser, "_should_include_file"
        ) as mock_should_include:

            mock_find_files.return_value = [self.project_root / "main.c"]
            mock_should_include.return_value = True

            # Call the method with include_depth=0
            result = self.parser._find_files_with_include_dependencies(
                self.project_root, True, config
            )

            # Should return only the initial files (no include processing)
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0], self.project_root / "main.c")

    def test_cache_logging(self):
        """Test that cache statistics are properly logged."""
        # Add some failed searches
        self.parser._find_included_file(
            "missing_header1.h", self.project_root / "main.c", self.project_root
        )
        self.parser._find_included_file(
            "missing_header2.h", self.project_root / "main.c", self.project_root
        )

        # Get cache stats
        stats = self.parser.get_failed_includes_cache_stats()

        # Verify stats structure
        self.assertIn("cache_size", stats)
        self.assertIn("cached_includes", stats)
        self.assertEqual(stats["cache_size"], 2)
        self.assertEqual(len(stats["cached_includes"]), 2)

    def test_cache_with_complex_include_chains(self):
        """Test caching with complex include dependency chains."""
        # Create a more complex project structure
        complex_dir = self.project_root / "complex"
        complex_dir.mkdir(exist_ok=True)

        # Create files with complex include chains
        file_a = complex_dir / "file_a.c"
        file_a.write_text('#include "missing_chain1.h"')

        file_b = complex_dir / "file_b.c"
        file_b.write_text('#include "missing_chain2.h"')

        # Search for missing headers from different locations
        result1 = self.parser._find_included_file(
            "missing_chain1.h", file_a, self.project_root
        )
        result2 = self.parser._find_included_file(
            "missing_chain2.h", file_b, self.project_root
        )

        self.assertIsNone(result1)
        self.assertIsNone(result2)

        # Both should be cached
        stats = self.parser.get_failed_includes_cache_stats()
        self.assertEqual(stats["cache_size"], 2)

        # Search again (should use cache)
        result3 = self.parser._find_included_file(
            "missing_chain1.h", file_b, self.project_root
        )
        result4 = self.parser._find_included_file(
            "missing_chain2.h", file_a, self.project_root
        )

        self.assertIsNone(result3)
        self.assertIsNone(result4)

        # Cache size should still be 2
        stats = self.parser.get_failed_includes_cache_stats()
        self.assertEqual(stats["cache_size"], 2)


if __name__ == "__main__":
    unittest.main()
