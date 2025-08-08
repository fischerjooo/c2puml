#!/usr/bin/env python3
"""
Comprehensive test for validating tokenization through CLI interface
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestTokenizerValidationComprehensive(UnifiedTestCase):
    """Test tokenization validation through CLI parsing of complex structures"""
    
    def test_complex_nested_union_tokenization(self):
        """Test tokenization of complex nested unions through CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("tokenizer_complex_nested_union")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)




if __name__ == "__main__":
    unittest.main()