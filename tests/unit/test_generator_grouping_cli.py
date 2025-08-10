#!/usr/bin/env python3
"""
Test Generator Grouping Through CLI Interface (bundled scenarios)
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase

class TestGeneratorGroupingCLI(UnifiedTestCase):
    def test_function_grouping_with_empty_line_separation(self):
        r = self.run_test("generator_grouping_cli::function_separation")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_global_grouping_with_empty_line_separation(self):
        r = self.run_test("generator_grouping_cli::global_separation")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_mixed_grouping_comprehensive(self):
        r = self.run_test("generator_grouping_cli::mixed_comprehensive")
        self.validate_execution_success(r)
        self.validate_test_output(r)

if __name__ == "__main__":
    unittest.main()