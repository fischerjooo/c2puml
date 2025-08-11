#!/usr/bin/env python3
"""
Comprehensive debug field parsing tests using CLI interface.
Replaces test_debug_field_parsing.py, test_debug_field_processing.py, and test_debug_field_parsing_detailed.py
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestDebugFieldParsingComprehensive(UnifiedTestCase):
    """Comprehensive CLI-based debug field parsing tests."""

    def test_nested_union_field_parsing(self):
        """Test nested union field parsing through CLI interface."""
        result = self.run_test("107_debug_fields_union")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_complex_struct_field_processing(self):
        """Test complex struct field processing through CLI interface."""
        result = self.run_test("107_debug_fields_struct") 
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_nested_anonymous_structure_fields(self):
        """Test nested anonymous structure field parsing through CLI interface."""
        result = self.run_test("107_debug_fields_anonymous")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    import unittest
    unittest.main()