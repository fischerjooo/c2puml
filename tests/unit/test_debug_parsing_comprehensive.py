#!/usr/bin/env python3
"""
Comprehensive test for debugging parsing functionality through CLI interface (bundled scenarios)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestDebugParsingComprehensive(UnifiedTestCase):
    def test_complex_union_parsing(self):
        r = self.run_test("anonymous_structures_and_debug::debug_parsing_union")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_nested_struct_parsing(self):
        r = self.run_test("anonymous_structures_and_debug::debug_parsing_struct")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_anonymous_structure_parsing(self):
        r = self.run_test("anonymous_structures_and_debug::debug_parsing_anonymous")
        self.validate_execution_success(r)
        self.validate_test_output(r)


if __name__ == "__main__":
    unittest.main()