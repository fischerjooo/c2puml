#!/usr/bin/env python3
"""
Comprehensive absolute path bug detection tests using CLI interface (bundled scenarios).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestAbsolutePathBugComprehensive(UnifiedTestCase):
    def test_relative_path_handling_in_include_tree(self):
        r = self.run_test("absolute_path_bug_comprehensive::relative_path")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_subdirectory_includes_path_resolution(self):
        r = self.run_test("absolute_path_bug_comprehensive::subdirectory")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_mixed_path_styles_handling(self):
        r = self.run_test("absolute_path_bug_comprehensive::mixed_paths")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_absolute_vs_relative_path_consistency(self):
        r = self.run_test("absolute_path_bug_comprehensive::consistency")
        self.validate_execution_success(r)
        self.validate_test_output(r)


if __name__ == "__main__":
    unittest.main()