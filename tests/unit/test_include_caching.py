#!/usr/bin/env python3
"""
Unit tests for include caching feature in C to PlantUML parser.
"""

import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from c_to_plantuml.parser import CParser


class TestIncludeCaching(unittest.TestCase):
    """Test cases for include caching functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = CParser()
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        
        # Create test files
        self.c_file = self.project_root / "test.c"
        self.c_file.write_text("""
#include "existing_header.h"
#include "missing_header1.h"
#include "missing_header2.h"
#include "missing_header1.h"  // Duplicate include
#include "missing_header2.h"  // Duplicate include
""")
        
        # Create an existing header
        self.existing_header = self.project_root / "existing_header.h"
        self.existing_header.write_text("// Existing header content")

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initial_cache_state(self):
        """Test that cache is initially empty."""
        stats = self.parser.get_failed_includes_cache_stats()
        self.assertEqual(stats["cache_size"], 0)
        self.assertEqual(stats["cached_includes"], [])

    def test_cache_failed_include_search(self):
        """Test that failed include searches are cached."""
        # First search for missing header
        result = self.parser._find_included_file("missing_header.h", self.c_file, self.project_root)
        self.assertIsNone(result)
        
        # Check that it was cached
        stats = self.parser.get_failed_includes_cache_stats()
        self.assertEqual(stats["cache_size"], 1)
        self.assertIn("missing_header.h:", stats["cached_includes"][0])

    def test_cache_hit_for_duplicate_search(self):
        """Test that cached searches return immediately."""
        # First search (should cache the failure)
        result1 = self.parser._find_included_file("missing_header.h", self.c_file, self.project_root)
        self.assertIsNone(result1)
        
        # Get initial cache size
        initial_cache_size = self.parser.get_failed_includes_cache_stats()["cache_size"]
        
        # Second search (should use cache)
        result2 = self.parser._find_included_file("missing_header.h", self.c_file, self.project_root)
        self.assertIsNone(result2)
        
        # Check cache size hasn't increased
        final_cache_size = self.parser.get_failed_includes_cache_stats()["cache_size"]
        self.assertEqual(final_cache_size, initial_cache_size)

    def test_existing_headers_not_cached(self):
        """Test that existing headers are not cached."""
        # Search for existing header
        result = self.parser._find_included_file("existing_header.h", self.c_file, self.project_root)
        self.assertIsNotNone(result)
        self.assertEqual(result, self.existing_header)
        
        # Check that it wasn't cached
        stats = self.parser.get_failed_includes_cache_stats()
        self.assertEqual(stats["cache_size"], 0)

    def test_multiple_missing_headers_cached(self):
        """Test that multiple different missing headers are cached separately."""
        # Search for first missing header
        result1 = self.parser._find_included_file("missing_header1.h", self.c_file, self.project_root)
        self.assertIsNone(result1)
        
        # Search for second missing header
        result2 = self.parser._find_included_file("missing_header2.h", self.c_file, self.project_root)
        self.assertIsNone(result2)
        
        # Check that both are cached
        stats = self.parser.get_failed_includes_cache_stats()
        self.assertEqual(stats["cache_size"], 2)
        
        cached_includes = stats["cached_includes"]
        self.assertTrue(any("missing_header1.h:" in include for include in cached_includes))
        self.assertTrue(any("missing_header2.h:" in include for include in cached_includes))

    def test_cache_key_uniqueness(self):
        """Test that cache keys are unique per project root."""
        # Create a second project root
        temp_dir2 = tempfile.mkdtemp()
        project_root2 = Path(temp_dir2)
        
        try:
            # Search in first project
            result1 = self.parser._find_included_file("missing_header.h", self.c_file, self.project_root)
            self.assertIsNone(result1)
            
            # Search in second project (should not use cache from first project)
            result2 = self.parser._find_included_file("missing_header.h", self.c_file, project_root2)
            self.assertIsNone(result2)
            
            # Check that both are cached separately
            stats = self.parser.get_failed_includes_cache_stats()
            self.assertEqual(stats["cache_size"], 2)
            
        finally:
            import shutil
            shutil.rmtree(temp_dir2, ignore_errors=True)

    def test_cache_cleared_on_new_project(self):
        """Test that cache is cleared when starting a new project."""
        # Add some failed searches to cache
        self.parser._find_included_file("missing_header1.h", self.c_file, self.project_root)
        self.parser._find_included_file("missing_header2.h", self.c_file, self.project_root)
        
        # Verify cache has entries
        stats = self.parser.get_failed_includes_cache_stats()
        self.assertEqual(stats["cache_size"], 2)
        
        # Start a new project (this should clear the cache)
        with patch.object(self.parser, '_find_c_files') as mock_find_files, \
             patch.object(self.parser, '_find_files_with_include_dependencies') as mock_find_with_deps:
            
            mock_find_files.return_value = []
            mock_find_with_deps.return_value = []
            
            # This should clear the cache
            self.parser.parse_project(str(self.project_root))
            
            # Verify cache is cleared
            stats = self.parser.get_failed_includes_cache_stats()
            self.assertEqual(stats["cache_size"], 0)

    def test_cache_with_different_include_formats(self):
        """Test that cache works with different include formats."""
        # Test with quotes
        result1 = self.parser._find_included_file('"missing_header.h"', self.c_file, self.project_root)
        self.assertIsNone(result1)
        
        # Test with angle brackets
        result2 = self.parser._find_included_file('<missing_header.h>', self.c_file, self.project_root)
        self.assertIsNone(result2)
        
        # Test without quotes
        result3 = self.parser._find_included_file('missing_header.h', self.c_file, self.project_root)
        self.assertIsNone(result3)
        
        # All should be cached as the same key since quotes/angle brackets are stripped
        stats = self.parser.get_failed_includes_cache_stats()
        self.assertEqual(stats["cache_size"], 1)  # All three become the same key after stripping

    def test_cache_with_file_extensions(self):
        """Test that cache works with different file extensions."""
        # Test with .h extension
        result1 = self.parser._find_included_file("missing_header.h", self.c_file, self.project_root)
        self.assertIsNone(result1)
        
        # Test with .hpp extension
        result2 = self.parser._find_included_file("missing_header.hpp", self.c_file, self.project_root)
        self.assertIsNone(result2)
        
        # Test without extension
        result3 = self.parser._find_included_file("missing_header", self.c_file, self.project_root)
        self.assertIsNone(result3)
        
        # All should be cached separately
        stats = self.parser.get_failed_includes_cache_stats()
        self.assertEqual(stats["cache_size"], 3)

    def test_cache_performance_improvement(self):
        """Test that caching provides performance improvement."""
        import time
        
        # First search (should be slow)
        start_time = time.time()
        result1 = self.parser._find_included_file("missing_header.h", self.c_file, self.project_root)
        first_search_time = time.time() - start_time
        self.assertIsNone(result1)
        
        # Second search (should be fast due to cache)
        start_time = time.time()
        result2 = self.parser._find_included_file("missing_header.h", self.c_file, self.project_root)
        second_search_time = time.time() - start_time
        self.assertIsNone(result2)
        
        # Second search should be significantly faster
        self.assertLess(second_search_time, first_search_time * 0.1)  # At least 10x faster

    def test_cache_with_nested_directories(self):
        """Test that cache works with nested directory structures."""
        # Create nested directory structure
        nested_dir = self.project_root / "include" / "nested"
        nested_dir.mkdir(parents=True, exist_ok=True)
        
        nested_file = nested_dir / "nested_file.c"
        nested_file.write_text("// Nested file")
        
        # Search for missing header from nested location
        result = self.parser._find_included_file("missing_header.h", nested_file, self.project_root)
        self.assertIsNone(result)
        
        # Check that it was cached
        stats = self.parser.get_failed_includes_cache_stats()
        self.assertEqual(stats["cache_size"], 1)

    def test_cache_with_special_characters(self):
        """Test that cache works with special characters in include names."""
        # Test with underscore
        result1 = self.parser._find_included_file("missing_header_file.h", self.c_file, self.project_root)
        self.assertIsNone(result1)
        
        # Test with dash
        result2 = self.parser._find_included_file("missing-header-file.h", self.c_file, self.project_root)
        self.assertIsNone(result2)
        
        # Test with numbers
        result3 = self.parser._find_included_file("missing_header_123.h", self.c_file, self.project_root)
        self.assertIsNone(result3)
        
        # All should be cached
        stats = self.parser.get_failed_includes_cache_stats()
        self.assertEqual(stats["cache_size"], 3)

    def test_cache_clear_method(self):
        """Test that cache can be manually cleared."""
        # Add some failed searches
        self.parser._find_included_file("missing_header1.h", self.c_file, self.project_root)
        self.parser._find_included_file("missing_header2.h", self.c_file, self.project_root)
        
        # Verify cache has entries
        stats = self.parser.get_failed_includes_cache_stats()
        self.assertEqual(stats["cache_size"], 2)
        
        # Clear cache manually
        self.parser._failed_includes_cache.clear()
        
        # Verify cache is empty
        stats = self.parser.get_failed_includes_cache_stats()
        self.assertEqual(stats["cache_size"], 0)

    def test_cache_with_empty_include_name(self):
        """Test that cache handles empty include names gracefully."""
        # Test with empty string
        result1 = self.parser._find_included_file("", self.c_file, self.project_root)
        self.assertIsNone(result1)
        
        # Test with whitespace only
        result2 = self.parser._find_included_file("   ", self.c_file, self.project_root)
        self.assertIsNone(result2)
        
        # Both should be cached
        stats = self.parser.get_failed_includes_cache_stats()
        self.assertEqual(stats["cache_size"], 2)

    def test_cache_with_none_project_root(self):
        """Test that cache works when project_root is None."""
        # Search with None project root
        result = self.parser._find_included_file("missing_header.h", self.c_file, None)
        self.assertIsNone(result)
        
        # Check that it was cached
        stats = self.parser.get_failed_includes_cache_stats()
        self.assertEqual(stats["cache_size"], 1)
        self.assertIn("missing_header.h:None", stats["cached_includes"][0])


if __name__ == '__main__':
    unittest.main()