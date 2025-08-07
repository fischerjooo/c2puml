#!/usr/bin/env python3
"""
Test Comprehensive Transformer Functionality

This test verifies that the c2puml tool can perform comprehensive transformations
including renaming, removal, filtering, and include processing through the CLI interface.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestTransformerComprehensive(UnifiedTestCase):
    """Test comprehensive transformer functionality through the CLI interface"""
    
    def test_transformer_comprehensive_operations(self):
        """Test comprehensive transformer operations including all major transformation types"""
        # Run the complete test using high-level methods
        result = self.run_test("transformer_comprehensive_operations")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_transformer_file_filtering(self):
        """Test transformer file filtering capabilities through CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("transformer_file_filtering")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_transformer_include_processing(self):
        """Test transformer include processing and depth control through CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("transformer_include_processing")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()