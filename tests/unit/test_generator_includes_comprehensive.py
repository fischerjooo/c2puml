#!/usr/bin/env python3
"""
Comprehensive test for generator include handling functionality through CLI interface
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestGeneratorIncludesComprehensive(UnifiedTestCase):
    """Test generator include handling functionality through CLI interface"""
    
    def test_duplicate_include_handling(self):
        """Test handling of duplicate include relationships through CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("generator_includes_comprehensive")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)




if __name__ == "__main__":
    unittest.main()