#!/usr/bin/env python3
"""
Individual test file for test_tokenizer_complex_nested_union.yml
Auto-generated to maintain 1:1 pairing between .py and .yml files
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestTokenizerComplexNestedUnion(UnifiedTestCase):
    """Test class for test_tokenizer_complex_nested_union"""

    def test_tokenizer_complex_nested_union(self):
        """Run the test_tokenizer_complex_nested_union test through CLI interface."""
        result = self.run_test("test_tokenizer_complex_nested_union")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
