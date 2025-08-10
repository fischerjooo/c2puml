#!/usr/bin/env python3
"""
Test CLI Modes Comprehensive (single-scenario files)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestCLIModesComprehensive(UnifiedTestCase):
    def test_parse_only(self):
        result = self.run_test("cli_modes_comprehensive_parse_only")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_transform_only(self):
        result = self.run_test("cli_modes_comprehensive_transform_only")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_generate_prefers_transformed(self):
        result = self.run_test("cli_modes_comprehensive_generate_prefers_transformed")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_generate_fallback(self):
        result = self.run_test("cli_modes_comprehensive_generate_fallback")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_full_workflow(self):
        result = self.run_test("cli_modes_comprehensive_full_workflow")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()