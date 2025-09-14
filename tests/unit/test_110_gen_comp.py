#!/usr/bin/env python3
"""
Test Generator Comprehensive
Comprehensive test for PlantUML generator functionality through CLI interface
This replaces the internal API test_generator.py with CLI-based testing
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tests.framework import UnifiedTestCase


class TestGeneratorComprehensive(UnifiedTestCase):
    """Test comprehensive generator functionality through the CLI interface"""

    def test_generator_comprehensive(self):
        """Test comprehensive generator scenarios through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("110_gen_comp")

        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
