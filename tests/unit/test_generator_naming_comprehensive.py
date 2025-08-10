#!/usr/bin/env python3
"""
Test Generator Naming Conventions Through CLI Interface (bundled scenarios)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestGeneratorNamingComprehensive(UnifiedTestCase):
    def test_typedef_conventions(self):
        r = self.run_test("generator_naming_comprehensive::typedef_conventions")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_file_conventions(self):
        r = self.run_test("generator_naming_comprehensive::file_conventions")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_complex_names(self):
        r = self.run_test("generator_naming_comprehensive::complex_names")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_edge_cases(self):
        r = self.run_test("generator_naming_comprehensive::edge_cases")
        self.validate_execution_success(r)
        self.validate_test_output(r)


if __name__ == "__main__":
    unittest.main()