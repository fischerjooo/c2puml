#!/usr/bin/env python3
"""
Test Generator Include Tree – simplified using unified framework
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tests.framework import UnifiedTestCase


class TestGeneratorIncludeTreeCLI(UnifiedTestCase):
    """Test include tree generation using the unified simple pattern"""

    def test_include_tree_with_absolute_paths(self):
        """Test include tree generation with absolute paths through CLI interface."""
        result = self.run_test("113_gen_inctree_abs")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_include_tree_comprehensive(self):
        """Test include tree generation comprehensively through CLI interface."""
        result = self.run_test("113_gen_inctree")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
