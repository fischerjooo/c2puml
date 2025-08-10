#!/usr/bin/env python3
"""
Comprehensive debug field parsing tests using CLI interface (bundled scenarios).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestDebugFieldParsingComprehensive(UnifiedTestCase):
    def test_nested_union_field_parsing(self):
        r = self.run_test("anonymous_structures_and_debug::debug_field_parsing_union")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_complex_struct_field_processing(self):
        r = self.run_test("anonymous_structures_and_debug::debug_field_parsing_struct")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_nested_anonymous_structure_fields(self):
        r = self.run_test("anonymous_structures_and_debug::debug_field_parsing_anonymous")
        self.validate_execution_success(r)
        self.validate_test_output(r)


if __name__ == "__main__":
    import unittest
    unittest.main()