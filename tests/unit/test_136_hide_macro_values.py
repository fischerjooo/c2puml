#!/usr/bin/env python3
"""
Individual test file for hide_macro_values functionality
Tests the hide_macro_values configuration flag
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestHideMacroValues(UnifiedTestCase):
    """Test class for hide_macro_values configuration"""

    def test_hide_macro_values_false(self):
        """Test that macro values are shown when hide_macro_values=false (default)."""
        result = self.run_test("136_hide_macro_values_false")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_hide_macro_values_true(self):
        """Test that macro values are hidden when hide_macro_values=true."""
        result = self.run_test("136_hide_macro_values_true")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()