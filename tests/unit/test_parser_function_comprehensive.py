#!/usr/bin/env python3
"""
Test Comprehensive Function Parsing (bundled scenarios)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestParserFunctionComprehensive(UnifiedTestCase):
    def test_parser_function_declarations(self):
        r = self.run_test("parser_functions_comprehensive::declarations")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_parser_function_definitions(self):
        r = self.run_test("parser_functions_comprehensive::definitions")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_parser_function_modifiers(self):
        r = self.run_test("parser_functions_comprehensive::modifiers")
        self.validate_execution_success(r)
        self.validate_test_output(r)


if __name__ == "__main__":
    unittest.main()