#!/usr/bin/env python3
"""
Test Parser Functions – Consolidated (replaces parser_functions)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestParserFunctions(UnifiedTestCase):
    def test_parser_functions_and_parameters_comprehensive(self):
        result = self.run_test("131_parser_funcs")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()