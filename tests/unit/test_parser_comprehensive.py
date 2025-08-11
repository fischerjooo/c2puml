#!/usr/bin/env python3
"""
Parser Comprehensive Scenarios – Unit Tests

Covers:
- parser_function_comprehensive_declarations
- parser_function_comprehensive_definitions
- parser_function_comprehensive_modifiers
- parser_mixed_comprehensive
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestParserComprehensive(UnifiedTestCase):
    def test_function_declarations(self):
        result = self.run_test("parser_function_comprehensive_declarations")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_function_definitions(self):
        result = self.run_test("parser_function_comprehensive_definitions")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_function_modifiers(self):
        result = self.run_test("parser_function_comprehensive_modifiers")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_mixed_comprehensive(self):
        result = self.run_test("parser_mixed_comprehensive")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()