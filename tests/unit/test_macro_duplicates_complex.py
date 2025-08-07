#!/usr/bin/env python3
"""
Test Macro Duplicates Complex

This test verifies that the c2puml tool can handle complex macro definitions with multiple conditions correctly and generate
the expected model and PlantUML output through the CLI interface.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestMacroDuplicatesComplex(UnifiedTestCase):
    """Test macro duplicates complex through the CLI interface"""
    
    def test_macro_duplicates_complex(self):
        """Test macro duplicates complex through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("macro_duplicates_complex")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()