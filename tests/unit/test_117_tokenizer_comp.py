#!/usr/bin/env python3
"""
Test Comprehensive Tokenizer Functionality

This test verifies that the c2puml tokenizer works correctly by testing complex
parsing scenarios through the CLI interface.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tests.framework import UnifiedTestCase


class TestTokenizerComprehensive(UnifiedTestCase):
    """Test comprehensive tokenizer functionality through the CLI interface"""

    def test_tokenizer_comprehensive(self):
        """Run the consolidated tokenizer scenario"""
        result = self.run_test("117_tokenizer_comp")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
