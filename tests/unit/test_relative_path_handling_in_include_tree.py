#!/usr/bin/env python3
"""
Individual test file for test_relative_path_handling_in_include_tree.yml
Auto-generated to maintain 1:1 pairing between .py and .yml files
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestRelativePathHandlingInIncludeTree(UnifiedTestCase):
    """Test class for test_relative_path_handling_in_include_tree"""

    def test_relative_path_handling_in_include_tree(self):
        """Run the test_relative_path_handling_in_include_tree test through CLI interface."""
        result = self.run_test("test_relative_path_handling_in_include_tree")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
