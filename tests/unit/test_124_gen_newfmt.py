#!/usr/bin/env python3
"""
Test Generator New Formatting – simplified using unified framework
"""
import os
import sys
import unittest
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase

class TestGeneratorNewFormattingCLI(UnifiedTestCase):
    """Test the PlantUML formatting rules using the unified simple pattern"""

    def test_generator_new_formatting_stereotypes_comprehensive(self):
        result = self.run_test("124_gen_newfmt")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_newfmt_complex_typedef(self):
        result = self.run_test("124_gen_newfmt_complex_typedef")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_newfmt_visibility_logic(self):
        result = self.run_test("124_gen_newfmt_visibility_logic")
        self.validate_execution_success(result)
        self.validate_test_output(result)

if __name__ == "__main__":
    unittest.main()