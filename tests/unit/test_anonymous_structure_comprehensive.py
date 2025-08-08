#!/usr/bin/env python3
"""
Comprehensive anonymous structure handling tests using CLI interface.
Replaces test_anonymous_structure_handling.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestAnonymousStructureComprehensive(UnifiedTestCase):
    """Comprehensive CLI-based anonymous structure handling tests."""

    def test_anonymous_struct_in_typedef(self):
        """Test that anonymous structs within typedefs are correctly processed through CLI interface."""
        result = self.run_test("anonymous_structure_comprehensive_typedef")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_nested_anonymous_structures(self):
        """Test that deeply nested anonymous structures are correctly processed through CLI interface."""
        result = self.run_test("anonymous_structure_comprehensive_nested")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_anonymous_unions_in_structs(self):
        """Test anonymous unions within structs through CLI interface."""
        result = self.run_test("anonymous_structure_comprehensive_unions")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()