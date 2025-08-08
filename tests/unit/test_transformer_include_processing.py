#!/usr/bin/env python3
"""
Individual test file for test_transformer_include_processing.yml
Auto-generated to maintain 1:1 pairing between .py and .yml files
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestTransformerIncludeProcessing(UnifiedTestCase):
    """Test class for test_transformer_include_processing"""

    def test_transformer_include_processing(self):
        """Run the test_transformer_include_processing test through CLI interface."""
        result = self.run_test("test_transformer_include_processing")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
