#!/usr/bin/env python3
"""
Transformer Comprehensive (single-scenario files)
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestTransformerComprehensive(UnifiedTestCase):
    def test_operations(self):
        result = self.run_test("transformer_comprehensive_operations")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_filtering(self):
        result = self.run_test("transformer_comprehensive_filtering")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_includes(self):
        result = self.run_test("transformer_comprehensive_includes")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()