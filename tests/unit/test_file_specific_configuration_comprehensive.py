#!/usr/bin/env python3
"""
Comprehensive file-specific configuration tests using CLI interface.
Replaces test_file_specific_configuration.py

Tests for file-specific configuration features like include filtering and depth settings.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestFileSpecificConfigurationComprehensive(UnifiedTestCase):
    """Comprehensive CLI-based file-specific configuration tests."""

    def test_file_specific_include_filter(self):
        """Test that file-specific include filters preserve includes arrays correctly through CLI interface."""
        result = self.run_test("file_specific_include_filter")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_file_specific_include_depth(self):
        """Test file-specific include depth configuration through CLI interface."""
        result = self.run_test("file_specific_include_depth")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_include_filter_patterns(self):
        """Test include filter patterns validation through CLI interface."""
        result = self.run_test("include_filter_patterns")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_configuration_extraction(self):
        """Test configuration extraction functionality through CLI interface."""
        result = self.run_test("configuration_extraction")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()