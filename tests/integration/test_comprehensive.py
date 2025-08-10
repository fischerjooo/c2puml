#!/usr/bin/env python3
"""
Comprehensive Integration Tests - single-scenario files
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestComprehensiveIntegrationCLI(UnifiedTestCase):
    def test_comprehensive_c_to_h_relationships(self):
        r = self.run_test("comprehensive_c_to_h_relationships")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_comprehensive_header_to_header_relationships(self):
        r = self.run_test("comprehensive_header_to_header_relationships")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_comprehensive_typedef_relationships(self):
        r = self.run_test("comprehensive_typedef_relationships")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_parser_tokenizer_integration(self):
        r = self.run_test("comprehensive_parser_tokenizer_integration")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_complete_system_integration(self):
        r = self.run_test("comprehensive_complete_system_integration")
        self.validate_execution_success(r)
        self.validate_test_output(r)


if __name__ == "__main__":
    unittest.main()