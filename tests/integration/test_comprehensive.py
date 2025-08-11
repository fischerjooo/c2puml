#!/usr/bin/env python3
"""
Comprehensive Integration Tests - Consolidated
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestComprehensiveIntegrationCLI(UnifiedTestCase):
    def test_integration_relationships_and_formatting_comprehensive(self):
        result = self.run_test("integration_relationships_and_formatting_comprehensive")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_complete_system_integration(self):
        result = self.run_test("comprehensive_complete_system_integration")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()