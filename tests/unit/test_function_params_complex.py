#!/usr/bin/env python3
"""
Test Function Params Complex

This test verifies that the c2puml tool can handle complex function parameters correctly and generate
the expected model and PlantUML output through the CLI interface.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestFunctionParamsComplex(UnifiedTestCase):
    """Test function params complex through the CLI interface"""
    
    def test_function_params_complex(self):
        """Test function params complex through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("function_params_complex")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()