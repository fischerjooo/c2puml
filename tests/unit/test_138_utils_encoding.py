#!/usr/bin/env python3
import io
import os
import tempfile
import unittest
from pathlib import Path

from src.c2puml.utils import (
    detect_file_encoding,
    get_acceptable_encodings,
    is_acceptable_encoding,
    normalize_encoding,
    get_platform_default_encoding,
)


class TestUtilsEncoding(unittest.TestCase):
    def test_acceptables_and_normalization(self):
        encs = get_acceptable_encodings()
        self.assertIn("utf-8", [e.lower() for e in encs])
        self.assertTrue(is_acceptable_encoding("UTF-8"))
        self.assertEqual(normalize_encoding("cp1252"), "windows-1252")
        self.assertEqual(normalize_encoding("latin-1"), "iso-8859-1")

    def test_platform_default(self):
        default = get_platform_default_encoding()
        self.assertIsInstance(default, str)
        self.assertGreater(len(default), 0)

    def test_detect_file_encoding_prefers_utf8(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "sample.txt"
            data = "hello utf-8 äöü".encode("utf-8")
            with open(p, "wb") as f:
                f.write(data)
            detected = detect_file_encoding(p)
            # Should be one of acceptable encodings and comparable after normalization
            self.assertTrue(is_acceptable_encoding(detected))
            self.assertEqual(normalize_encoding(detected), "utf-8")


if __name__ == "__main__":
    unittest.main()

