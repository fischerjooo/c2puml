#!/usr/bin/env python3
"""
Test Nested Struct Preservation

This test verifies that the c2puml tool can preserve nested struct structures correctly and generate
the expected model and PlantUML output through the CLI interface.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestNestedStructPreservation(UnifiedTestCase):
    """Test nested struct preservation through the CLI interface"""
    
    def test_nested_struct_preservation(self):
        """Test nested struct preservation through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("nested_struct_preservation")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()