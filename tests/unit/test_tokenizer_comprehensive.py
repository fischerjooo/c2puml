#!/usr/bin/env python3
"""
Test Comprehensive Tokenizer Functionality (bundled scenarios)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestTokenizerComprehensive(UnifiedTestCase):
    def test_complex_parsing(self):
        result = self.run_test("tokenizer_comprehensive::complex_parsing")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_edge_cases(self):
        result = self.run_test("tokenizer_comprehensive::edge_cases")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_preprocessor(self):
        result = self.run_test("tokenizer_comprehensive::preprocessor")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()