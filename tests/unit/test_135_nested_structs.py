#!/usr/bin/env python3
"""
Test Nested Structures PUML

This test verifies that the c2puml tool can preserve nested structure hierarchy
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tests.framework import UnifiedTestCase


class TestNestedStructuresPuml(UnifiedTestCase):
    """Test nested structures puml through the CLI interface"""

    def test_nested_structures_puml(self):
        """Test nested structures puml through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("135_nested_structs")

        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
