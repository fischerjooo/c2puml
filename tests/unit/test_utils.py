#!/usr/bin/env python3
"""
Unit tests for utility functions
"""

import tempfile
import unittest
from pathlib import Path

from c_to_plantuml.utils import (
    detect_file_encoding,
    get_acceptable_encodings,
    get_platform_default_encoding,
    is_acceptable_encoding,
    normalize_encoding,
)


class TestUtils(unittest.TestCase):
    """Test utility functions"""

    def test_get_acceptable_encodings(self):
        """Test getting acceptable encodings"""
        encodings = get_acceptable_encodings()
        
        # Should include common encodings
        self.assertIn("utf-8", encodings)
        self.assertIn("utf-8-sig", encodings)
        self.assertIn("windows-1252", encodings)
        self.assertIn("windows-1254", encodings)
        
        # Should be a list
        self.assertIsInstance(encodings, list)
        self.assertGreater(len(encodings), 0)

    def test_is_acceptable_encoding(self):
        """Test encoding acceptability check"""
        # Should accept UTF-8
        self.assertTrue(is_acceptable_encoding("utf-8"))
        self.assertTrue(is_acceptable_encoding("UTF-8"))
        
        # Should accept Windows encodings
        self.assertTrue(is_acceptable_encoding("windows-1252"))
        self.assertTrue(is_acceptable_encoding("windows-1254"))
        
        # Should reject unknown encodings
        self.assertFalse(is_acceptable_encoding("unknown-encoding"))
        self.assertFalse(is_acceptable_encoding(""))

    def test_normalize_encoding(self):
        """Test encoding normalization"""
        # Should normalize Windows encodings
        self.assertEqual(normalize_encoding("cp1252"), "windows-1252")
        self.assertEqual(normalize_encoding("cp1254"), "windows-1254")
        self.assertEqual(normalize_encoding("latin-1"), "iso-8859-1")
        
        # Should preserve other encodings
        self.assertEqual(normalize_encoding("utf-8"), "utf-8")
        self.assertEqual(normalize_encoding("utf-16"), "utf-16")
        
        # Should handle case
        self.assertEqual(normalize_encoding("UTF-8"), "utf-8")
        self.assertEqual(normalize_encoding("CP1252"), "windows-1252")

    def test_get_platform_default_encoding(self):
        """Test platform default encoding detection"""
        encoding = get_platform_default_encoding()
        
        # Should return a valid encoding
        self.assertIsInstance(encoding, str)
        self.assertGreater(len(encoding), 0)
        
        # Should be acceptable
        self.assertTrue(is_acceptable_encoding(encoding))

    def test_detect_file_encoding_utf8(self):
        """Test encoding detection for UTF-8 files"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("Hello, World! 🌍")
            temp_file = f.name

        try:
            encoding = detect_file_encoding(Path(temp_file))
            self.assertIn(encoding.lower(), ["utf-8", "utf-8-sig"])
        finally:
            Path(temp_file).unlink()

    def test_detect_file_encoding_with_bom(self):
        """Test encoding detection for files with BOM"""
        # Create a file with UTF-8 BOM
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False) as f:
            f.write(b'\xef\xbb\xbfHello, World!')
            temp_file = f.name

        try:
            encoding = detect_file_encoding(Path(temp_file))
            # Should detect UTF-8 with BOM, but some systems might normalize it
            self.assertIn(encoding.lower(), ["utf-8-sig", "utf-8"])
        finally:
            Path(temp_file).unlink()

    def test_detect_file_encoding_ascii(self):
        """Test encoding detection for ASCII files"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="ascii") as f:
            f.write("Hello, World!")
            temp_file = f.name

        try:
            encoding = detect_file_encoding(Path(temp_file))
            # ASCII should be detected as UTF-8 or similar
            self.assertTrue(is_acceptable_encoding(encoding))
        finally:
            Path(temp_file).unlink()


if __name__ == "__main__":
    unittest.main()