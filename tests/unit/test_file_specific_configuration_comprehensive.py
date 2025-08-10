#!/usr/bin/env python3
"""
Comprehensive file-specific configuration tests using CLI interface (bundled scenarios).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestFileSpecificConfigurationComprehensive(UnifiedTestCase):
    def test_file_specific_include_filter(self):
        result = self.run_test("file_specific_configuration_comprehensive::filter")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_file_specific_include_depth(self):
        result = self.run_test("file_specific_configuration_comprehensive::depth")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_include_filter_patterns(self):
        result = self.run_test("file_specific_configuration_comprehensive::patterns")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_configuration_extraction(self):
        result = self.run_test("file_specific_configuration_comprehensive::extraction")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()