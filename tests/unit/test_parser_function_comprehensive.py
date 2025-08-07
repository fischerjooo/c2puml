#!/usr/bin/env python3
"""
Test Comprehensive Function Parsing

This test verifies that the c2puml tool can parse various function definitions
and declarations through the CLI interface.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestParserFunctionComprehensive(UnifiedTestCase):
    """Test comprehensive function parsing through the CLI interface"""
    
    def test_parser_function_declarations(self):
        """Test parsing function declarations through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("parser_function_declarations")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_parser_function_definitions(self):
        """Test parsing function definitions through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("parser_function_definitions")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_parser_function_modifiers(self):
        """Test parsing functions with modifiers through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("parser_function_modifiers")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()