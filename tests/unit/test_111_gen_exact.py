#!/usr/bin/env python3
"""
Test Generator Exact Formatting – simplified using unified framework
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tests.framework import UnifiedTestCase


class TestGeneratorExactFormatCLI(UnifiedTestCase):
    """Test the exact PlantUML formatting using the unified simple pattern"""

    def test_exact_requested_format(self):
        """Test exact requested format through CLI interface"""
        result = self.run_test("111_gen_exact_requested")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_format_with_parameters(self):
        """Test exact format with parameters through CLI interface"""
        result = self.run_test("111_gen_exact_params")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
