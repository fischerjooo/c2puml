"""
Base class for feature tests

Provides common setup and teardown functionality for all feature tests.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path


class BaseFeatureTest(unittest.TestCase):
    """Base class for feature tests with common setup and teardown"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = []

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, filename: str, content: str) -> str:
        """Create a test file and return its path"""
        file_path = os.path.join(self.temp_dir, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.test_files.append(file_path)
        return file_path

    def write_json_config(self, config_file: str, config: dict) -> None:
        """Write JSON configuration to file"""
        import json

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
