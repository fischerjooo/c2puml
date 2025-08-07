#!/usr/bin/env python3
"""
Test Comprehensive Generator Functionality

This test verifies that the c2puml PlantUML generator works correctly by testing
complex scenarios through the CLI interface that would fail if generation was broken.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestGeneratorComprehensive(UnifiedTestCase):
    """Test comprehensive generator functionality through the CLI interface"""
    
    def test_generator_basic_plantuml(self):
        """Test basic PlantUML generation with all major C constructs"""
        # Run the complete test using high-level methods
        result = self.run_test("generator_basic_plantuml")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)




if __name__ == "__main__":
    unittest.main()