#!/usr/bin/env python3
"""
New Formatting Comprehensive Integration Tests - CLI-based (bundled scenarios)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestNewFormattingComprehensiveCLI(UnifiedTestCase):
    def test_complete_formatting_integration(self):
        r = self.run_test("comprehensive::new_formatting_complete")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_mixed_project_comprehensive_formatting(self):
        r = self.run_test("comprehensive::new_formatting_mixed_project")
        self.validate_execution_success(r)
        self.validate_test_output(r)


if __name__ == "__main__":
    unittest.main()