#!/usr/bin/env python3
"""
Test Comprehensive Enum Parsing

This test verifies that the c2puml tool can parse various enum definitions
and generate the expected model and PlantUML output through the CLI interface.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestParserEnumComprehensive(UnifiedTestCase):
    """Test comprehensive enum parsing through the CLI interface"""
    
    def test_parser_enum_simple(self):
        """Test parsing simple enum definitions through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("parser_enum_comprehensive_simple")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_parser_enum_typedef(self):
        """Test parsing typedef enum definitions through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("parser_enum_comprehensive_typedef")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()