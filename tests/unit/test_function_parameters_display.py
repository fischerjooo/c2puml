#!/usr/bin/env python3
"""
Test Function Parameters Display

This test verifies that the c2puml tool can display function parameters correctly in PlantUML and generate
the expected model and PlantUML output through the CLI interface.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestFunctionParametersDisplay(UnifiedTestCase):
    """Test function parameter display through the CLI interface"""
    
    def test_function_parameters_display(self):
        """Test function parameter display through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("function_parameters_display")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()