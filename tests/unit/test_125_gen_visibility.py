#!/usr/bin/env python3
"""
Test Generator Visibility Logic – simplified using unified framework
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tests.framework import UnifiedTestCase


class TestGeneratorVisibilityLogicCLI(UnifiedTestCase):
    """Test generator visibility logic using the unified simple pattern"""

    def test_generator_visibility_logic_comprehensive(self):
        """Test generator visibility logic through CLI interface"""
        result = self.run_test("125_gen_visibility")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
