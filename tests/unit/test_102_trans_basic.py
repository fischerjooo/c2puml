#!/usr/bin/env python3
"""
Test Basic Transformer Functionality

This test verifies that the c2puml tool can perform basic transformation operations
and generate the expected transformed model through the CLI interface.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tests.framework import UnifiedTestCase


class TestTransformerBasic(UnifiedTestCase):
    """Test basic transformer functionality through the CLI interface"""

    def test_transformer_basic(self):
        """Test basic transformer functionality through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("102_trans_basic")

        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
