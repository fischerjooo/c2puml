#!/usr/bin/env python3
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tests.framework import UnifiedTestCase


class TestUtilsEncodingCli(UnifiedTestCase):
    """Test utils encoding through the CLI interface"""

    def test_utils_encoding_cli(self):
        """Run the utils encoding CLI scenario"""
        result = self.run_test("138_utils_encoding_cli")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
