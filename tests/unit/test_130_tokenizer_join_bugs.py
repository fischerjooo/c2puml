#!/usr/bin/env python3
"""
Test for tokenizer join bugs that cause field name corruption
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestTokenizerJoinBugs(UnifiedTestCase):
    """Test that tokenizer correctly handles field parsing without corrupting names"""

    def test_tokenizer_join_bugs_detection(self):
        """Test that tokenizer correctly parses field names without corruption"""
        # Run the test using high-level methods
        result = self.run_test("130_tokenizer_join_bugs")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()