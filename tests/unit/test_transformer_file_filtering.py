#!/usr/bin/env python3
"""
Individual test file for test_transformer_file_filtering.yml
Auto-generated to maintain 1:1 pairing between .py and .yml files
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestTransformerFileFiltering(UnifiedTestCase):
    """Test class for test_transformer_file_filtering"""

    def test_transformer_file_filtering(self):
        """Run the test_transformer_file_filtering test through CLI interface."""
        result = self.run_test("test_transformer_file_filtering")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
