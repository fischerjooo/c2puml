#!/usr/bin/env python3
"""
Test Simple Struct Parsing

This test verifies that the c2puml tool can parse a simple struct definition
and generate the expected model and PlantUML output through the CLI interface.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestParserSimpleStruct(UnifiedTestCase):
    """Test parsing a simple struct definition through the CLI interface"""
    
    def test_parser_simple_struct(self):
        """Test parsing a simple struct definition through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("parser_simple_struct")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()