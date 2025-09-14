#!/usr/bin/env python3
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from c2puml.config import Config


class TestConfigEdges(unittest.TestCase):
    def test_compile_patterns_invalid_and_valid(self):
        cfg = Config(file_filters={"include": ["(", "^main\\.c$"]})
        # Invalid pattern is skipped; only valid compiled
        self.assertEqual(len(cfg.file_include_patterns), 1)
        self.assertTrue(cfg.file_include_patterns[0].search("main.c"))

    def test_has_filters_variants(self):
        cfg1 = Config()
        self.assertFalse(cfg1.has_filters())
        cfg2 = Config(file_specific={"main.c": {"include_filter": ["^keep\\.h$"]}})
        self.assertTrue(cfg2.has_filters())
        cfg3 = Config(file_filters={"include": [".*\\.c$"]})
        self.assertTrue(cfg3.has_filters())

    def test_should_include_file_precedence(self):
        cfg = Config(file_filters={
            "include": ["^main\\.c$"],
            "exclude": [".*\\.c$"]
        })
        cfg._compile_patterns()
        # Exclude patterns are checked first; exclusion wins
        self.assertFalse(cfg._should_include_file("main.c"))
        # A header should also be excluded by pattern
        self.assertFalse(cfg._should_include_file("util.c"))

    def test_load_with_backward_compat_and_errors(self):
        with tempfile.TemporaryDirectory() as td:
            # Backward compatibility: project_roots -> source_folders
            p1 = os.path.join(td, "config1.json")
            with open(p1, "w", encoding="utf-8") as f:
                json.dump({"project_roots": ["."], "output_dir": "out"}, f)
            cfg1 = Config.load(p1)
            self.assertEqual(cfg1.source_folders, ["."])

            # Invalid JSON
            p2 = os.path.join(td, "config2.json")
            with open(p2, "w", encoding="utf-8") as f:
                f.write("{ invalid json }")
            with self.assertRaises(ValueError):
                Config.load(p2)

            # Missing source_folders
            p3 = os.path.join(td, "config3.json")
            with open(p3, "w", encoding="utf-8") as f:
                json.dump({"project_name": "x"}, f)
            with self.assertRaises(ValueError):
                Config.load(p3)

            # Wrong type for source_folders
            p4 = os.path.join(td, "config4.json")
            with open(p4, "w", encoding="utf-8") as f:
                json.dump({"source_folders": "not-a-list"}, f)
            with self.assertRaises(ValueError):
                Config.load(p4)

    def test_save_roundtrip(self):
        cfg = Config(project_name="P", source_folders=["."], output_dir="out")
        with tempfile.TemporaryDirectory() as td:
            fp = os.path.join(td, "saved.json")
            cfg.save(fp)
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data["project_name"], "P")
            self.assertEqual(data["source_folders"], ["."])
            self.assertEqual(data["output_dir"], "out")


if __name__ == "__main__":
    unittest.main()

