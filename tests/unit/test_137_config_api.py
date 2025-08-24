#!/usr/bin/env python3
"""
Unit tests for Config API: load, save, has_filters, include-file filtering, equality
"""

import json
import os
import tempfile
import unittest

from src.c2puml.config import Config


class TestConfigAPI(unittest.TestCase):
    def test_load_save_and_equality(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = os.path.join(tmp, "config.json")
            data = {
                "project_name": "TestProject",
                "source_folders": ["."],
                "output_dir": "./output",
                "include_depth": 2,
                "file_filters": {"include": [".*\\.(c|h)$"], "exclude": [".*_test\\.c$"]},
                "file_specific": {"main.c": {"include_filter": ["^main\\.h$"]}},
            }
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump(data, f)

            # Load via Config.load
            cfg = Config.load(cfg_path)
            self.assertEqual(cfg.project_name, "TestProject")
            self.assertEqual(cfg.source_folders, ["."])
            self.assertEqual(cfg.output_dir, "./output")
            self.assertEqual(cfg.include_depth, 2)

            # Save and re-read JSON bytes to ensure all keys are written
            out_path = os.path.join(tmp, "saved.json")
            cfg.save(out_path)
            with open(out_path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            # Spot-check a few critical keys
            self.assertEqual(saved["project_name"], "TestProject")
            self.assertIn("source_folders", saved)
            self.assertIn("file_filters", saved)
            self.assertIn("file_specific", saved)

            # Equality
            cfg2 = Config(**saved)
            self.assertTrue(cfg == cfg2)
            cfg2.project_name = "Other"
            self.assertFalse(cfg == cfg2)

    def test_has_filters_and_should_include_file(self):
        # include '*.c' and exclude '*_gen.c'
        cfg = Config(
            project_name="X",
            source_folders=["."],
            file_filters={"include": [".*\\.c$"], "exclude": [".*_gen\\.c$"]},
            file_specific={"main.c": {"include_filter": ["^main\\.h$"]}},
        )
        # Compiles patterns in __init__/__post_init__
        self.assertTrue(cfg.has_filters())

        # Included: foo.c matches include and not excluded
        self.assertTrue(cfg._should_include_file("src/foo.c"))
        # Excluded: foo_gen.c matches exclude
        self.assertFalse(cfg._should_include_file("src/foo_gen.c"))
        # Not included: header.h does not match include
        self.assertFalse(cfg._should_include_file("include/header.h"))


if __name__ == "__main__":
    unittest.main()

