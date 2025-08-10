#!/usr/bin/env python3
"""
File-specific configuration (single-scenario files)
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestFileSpecificConfigurationComprehensive(UnifiedTestCase):
    def test_filter(self):
        result = self.run_test("file_specific_configuration_comprehensive_filter")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_depth(self):
        result = self.run_test("file_specific_configuration_comprehensive_depth")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_patterns(self):
        result = self.run_test("file_specific_configuration_comprehensive_patterns")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_extraction(self):
        result = self.run_test("file_specific_configuration_comprehensive_extraction")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()