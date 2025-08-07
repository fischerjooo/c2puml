#!/usr/bin/env python3
"""
Test Struct Order Preservation

This test verifies that the c2puml tool can preserve struct field order correctly and generate
the expected model and PlantUML output through the CLI interface.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestStructOrderPreservation(UnifiedTestCase):
    """Test struct order preservation through the CLI interface"""
    
    def test_struct_order_preservation(self):
        """Test struct order preservation through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("struct_order_preservation")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()