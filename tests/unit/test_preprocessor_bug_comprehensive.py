#!/usr/bin/env python3
"""
Test Preprocessor Bug Comprehensive
Comprehensive test for preprocessor bug fixes through CLI interface
This replaces the internal API test_preprocessor_bug.py with CLI-based testing
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestPreprocessorBugComprehensive(UnifiedTestCase):
    """Test comprehensive preprocessor bug handling through the CLI interface"""
    
    def test_preprocessor_bug_comprehensive(self):
        """Test comprehensive preprocessor bug scenarios through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("preprocessor_bug_comprehensive")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()