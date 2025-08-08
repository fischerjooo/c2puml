#!/usr/bin/env python3
"""
Comprehensive test for include processing functionality through CLI interface
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestIncludeProcessingComprehensive(UnifiedTestCase):
    """Test include processing functionality through CLI interface"""
    
    def test_basic_include_processing(self):
        """Test basic include file processing through CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("include_processing_comprehensive")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)




if __name__ == "__main__":
    unittest.main()