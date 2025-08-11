#!/usr/bin/env python3
"""
Comprehensive absolute path bug detection tests using CLI interface.
Replaces test_absolute_path_bug_detection.py

Tests for absolute path bug detection in include tree building.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestAbsolutePathBugComprehensive(UnifiedTestCase):
    """Comprehensive CLI-based absolute path bug detection tests."""

    def test_relative_path_handling_in_include_tree(self):
        """Test that relative paths are handled correctly in include tree building through CLI interface."""
        result = self.run_test("103_abs_path_relative")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_subdirectory_includes_path_resolution(self):
        """Test subdirectory includes path resolution through CLI interface."""
        result = self.run_test("103_abs_path_subdir")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_mixed_path_styles_handling(self):
        """Test mixed path styles handling through CLI interface."""
        result = self.run_test("103_abs_path_mixed")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_absolute_vs_relative_path_consistency(self):
        """Test absolute vs relative path consistency through CLI interface."""
        result = self.run_test("103_abs_path_consistency")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_path_resolution_and_include_tree_comprehensive(self):
        result = self.run_test("103_abs_path_include_tree")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()