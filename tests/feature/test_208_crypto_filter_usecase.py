#!/usr/bin/env python3
"""
Test Crypto Filter Usecase Comprehensive
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestCryptoFilterUsecaseComprehensive(UnifiedTestCase):
    """Test crypto filter usecase functionality through the CLI interface"""
    
    def test_crypto_filter_usecase_functionality(self):
        """Test crypto filter usecase functionality through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("208_crypto_filter_usecase")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()