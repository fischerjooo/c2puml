#!/usr/bin/env python3
"""
Test Comprehensive Model Verifier

This test verifies that the model verifier works correctly through the CLI interface
by testing both valid models (that should pass) and invalid models (that should show warnings).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestVerifierComprehensive(UnifiedTestCase):
    """Test comprehensive model verifier functionality through the CLI interface"""
    
    def test_verifier_valid_model(self):
        """Test that valid models pass verification without warnings"""
        # Run the complete test using high-level methods
        result = self.run_test("verifier_valid_model")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()