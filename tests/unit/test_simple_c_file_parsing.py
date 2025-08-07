#!/usr/bin/env python3
"""
Test Simple C File Parsing

This test verifies that the c2puml tool can parse a simple C file and generate
the expected model and PlantUML output through the CLI interface.
"""

import os
import sys
import unittest
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestSimpleCFileParsing(UnifiedTestCase):
    """Test parsing a simple C file through the CLI interface"""
    
    def test_simple_c_file_parsing(self):
        """Test parsing a simple C file through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("simple_c_file_parsing")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()