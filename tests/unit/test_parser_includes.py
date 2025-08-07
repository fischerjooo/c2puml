#!/usr/bin/env python3
"""
Test Parser Includes

This test verifies that the c2puml tool can parse include statements and generate
the expected model and PlantUML output through the CLI interface.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestParserIncludes(UnifiedTestCase):
    """Test parsing include statements through the CLI interface"""
    
    def test_parser_includes(self):
        """Test parsing include statements through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("parser_includes")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()