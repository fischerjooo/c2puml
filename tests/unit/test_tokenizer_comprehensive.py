#!/usr/bin/env python3
"""
Test Comprehensive Tokenizer Functionality

This test verifies that the c2puml tokenizer works correctly by testing complex
parsing scenarios through the CLI interface that would fail if tokenization was broken.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestTokenizerComprehensive(UnifiedTestCase):
    """Test comprehensive tokenizer functionality through the CLI interface"""
    
    def test_tokenizer_complex_parsing(self):
        """Test tokenizer with complex C constructs that stress tokenization"""
        # Run the complete test using high-level methods
        result = self.run_test("tokenizer_complex_parsing")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_tokenizer_edge_cases(self):
        """Test tokenizer with edge cases like comments, strings, complex expressions"""
        # Run the complete test using high-level methods
        result = self.run_test("tokenizer_edge_cases")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_tokenizer_preprocessor_handling(self):
        """Test tokenizer with complex preprocessor constructs"""
        # Run the complete test using high-level methods
        result = self.run_test("tokenizer_preprocessor_handling")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()