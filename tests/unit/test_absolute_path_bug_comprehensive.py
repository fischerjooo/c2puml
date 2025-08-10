#!/usr/bin/env python3
"""
Absolute Path Bug Comprehensive (single-scenario files)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestAbsolutePathBugComprehensive(UnifiedTestCase):
    def test_relative_path_handling_in_include_tree(self):
        r = self.run_test("absolute_path_bug_comprehensive_relative_path")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_subdirectory_includes_path_resolution(self):
        r = self.run_test("absolute_path_bug_comprehensive_subdirectory")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_mixed_path_styles_handling(self):
        r = self.run_test("absolute_path_bug_comprehensive_mixed_paths")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_absolute_vs_relative_path_consistency(self):
        r = self.run_test("absolute_path_bug_comprehensive_consistency")
        self.validate_execution_success(r)
        self.validate_test_output(r)


if __name__ == "__main__":
    unittest.main()