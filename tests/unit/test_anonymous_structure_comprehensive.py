#!/usr/bin/env python3
"""
Anonymous Structure Comprehensive (single-scenario files)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestAnonymousStructureComprehensive(UnifiedTestCase):
    def test_anonymous_struct_in_typedef(self):
        r = self.run_test("anonymous_structures_and_debug_anonymous_struct")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_nested_anonymous_structures(self):
        r = self.run_test("anonymous_structures_and_debug_nested_anonymous")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_anonymous_unions_in_structs(self):
        r = self.run_test("anonymous_structures_and_debug_anonymous_union")
        self.validate_execution_success(r)
        self.validate_test_output(r)


if __name__ == "__main__":
    unittest.main()