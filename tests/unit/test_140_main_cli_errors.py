#!/usr/bin/env python3
"""
Unit tests for main CLI error paths: missing config, invalid JSON, missing model on generate
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

from tests.framework.executor import TestExecutor
from tests.framework.validators import CLIValidator


class TestMainCliErrors(unittest.TestCase):
    def setUp(self):
        self.exec = TestExecutor()
        self.cli = CLIValidator()

    def test_missing_config_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = os.path.join(tmp, "nope.json")
            result = self.exec.run_full_pipeline(missing, working_dir=tmp)
            # Should fail and mention configuration load error
            self.cli.assert_cli_failure(result)

    def test_invalid_json_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = os.path.join(tmp, "config.json")
            with open(cfg, "w", encoding="utf-8") as f:
                f.write("{ invalid json ")
            result = self.exec.run_full_pipeline(cfg, working_dir=tmp)
            self.cli.assert_cli_failure(result)

    def test_generate_without_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Valid minimal config
            cfg = os.path.join(tmp, "config.json")
            with open(cfg, "w", encoding="utf-8") as f:
                json.dump({"project_name": "x", "source_folders": ["."], "output_dir": os.path.join(tmp, "output")}, f)
            # Call generate directly - no model files exist
            result = self.exec.run_generate_only(cfg, working_dir=tmp)
            self.cli.assert_cli_failure(result)


if __name__ == "__main__":
    unittest.main()

