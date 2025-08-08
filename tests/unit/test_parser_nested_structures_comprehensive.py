#!/usr/bin/env python3
"""
Comprehensive parser nested structures tests using CLI interface.
Replaces test_parser_nested_structures.py

Addresses Issue 1.2 from TODO.md:
"Struct Field Order and Structure Issues - Nested Union/Struct Flattening"
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestParserNestedStructuresComprehensive(UnifiedTestCase):
    """Comprehensive CLI-based parser nested structures tests."""

    def test_nested_union_preservation(self):
        """Test that nested unions maintain their structure through CLI interface."""
        result = self.run_test("parser_nested_structures_comprehensive_union")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_nested_struct_preservation(self):
        """Test that nested structs maintain their structure through CLI interface."""
        result = self.run_test("parser_nested_structures_comprehensive_struct")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_nested_structures_in_generated_puml(self):
        """Test that nested structures appear correctly in generated PlantUML through CLI interface."""
        result = self.run_test("parser_nested_structures_comprehensive_puml")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()