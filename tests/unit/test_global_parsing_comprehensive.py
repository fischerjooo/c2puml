#!/usr/bin/env python3
"""
Test Global Parsing Comprehensive
Comprehensive test for global variable parsing through CLI interface
This replaces the internal API test_global_parsing.py with CLI-based testing
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestGlobalParsingComprehensive(UnifiedTestCase):
    """Test comprehensive global variable parsing through the CLI interface"""
    
    def test_global_parsing_comprehensive(self):
        """Test comprehensive global parsing scenarios through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("global_parsing_comprehensive")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()