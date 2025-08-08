#!/usr/bin/env python3
"""
Test Comprehensive Mixed Parsing

This test verifies that the c2puml tool can parse a complex C file with mixed
language features (structs, enums, unions, functions, typedefs, etc.) through the CLI interface.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestParserMixedComprehensive(UnifiedTestCase):
    """Test comprehensive mixed parsing through the CLI interface"""
    
    def test_parser_mixed_content(self):
        """Test parsing a file with mixed C language features through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("parser_mixed_comprehensive")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()