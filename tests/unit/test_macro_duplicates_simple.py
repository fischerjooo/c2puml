#!/usr/bin/env python3
"""
Test Macro Duplicates Simple

This test verifies that the c2puml tool can handle macro definitions without duplicates correctly and generate
the expected model and PlantUML output through the CLI interface.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestMacroDuplicatesSimple(UnifiedTestCase):
    """Test macro duplicates simple through the CLI interface"""
    
    def test_macro_duplicates_simple(self):
        """Test macro duplicates simple through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("macro_duplicates_simple")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()