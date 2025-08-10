#!/usr/bin/env python3
"""
Test Typedef Extraction Comprehensive (bundled scenarios)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestTypedefExtractionComprehensive(UnifiedTestCase):
    def test_simple(self):
        r = self.run_test("typedef_extraction_comprehensive::simple")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_function_pointers(self):
        r = self.run_test("typedef_extraction_comprehensive::function_pointers")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_structs(self):
        r = self.run_test("typedef_extraction_comprehensive::structs")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_enums(self):
        r = self.run_test("typedef_extraction_comprehensive::enums")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_unions(self):
        r = self.run_test("typedef_extraction_comprehensive::unions")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_mixed(self):
        r = self.run_test("typedef_extraction_comprehensive::mixed")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_edge_cases(self):
        r = self.run_test("typedef_extraction_comprehensive::edge_cases")
        self.validate_execution_success(r)
        self.validate_test_output(r)


if __name__ == "__main__":
    unittest.main()