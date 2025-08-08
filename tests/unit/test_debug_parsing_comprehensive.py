#!/usr/bin/env python3
"""
Comprehensive test for debugging parsing functionality through CLI interface
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestDebugParsingComprehensive(UnifiedTestCase):
    """Test debugging parsing functionality through CLI interface"""
    
    def test_complex_union_parsing(self):
        """Test parsing complex union with nested structures through CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("debug_complex_union_parsing")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_nested_struct_parsing(self):
        """Test parsing nested struct definitions through CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("debug_nested_struct_parsing")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_anonymous_structure_parsing(self):
        """Test parsing anonymous structures in typedefs through CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("debug_anonymous_structure_parsing")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()