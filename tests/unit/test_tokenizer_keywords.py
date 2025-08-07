#!/usr/bin/env python3
"""
Test Tokenizer Keywords

This test verifies that the c2puml tool can correctly tokenize C keywords
and generate the expected model through the CLI interface.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestTokenizerKeywords(UnifiedTestCase):
    """Test tokenizer keyword recognition through the CLI interface"""
    
    def test_tokenizer_keywords(self):
        """Test tokenizer keyword recognition through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("tokenizer_keywords")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()