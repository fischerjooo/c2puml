#!/usr/bin/env python3
"""
Comprehensive Integration Tests - Consolidated
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tests.framework import UnifiedTestCase


class TestComprehensiveIntegrationCLI(UnifiedTestCase):
    """Test comprehensive integration scenarios through the CLI interface"""

    def test_integration_relationships_and_formatting_comprehensive(self):
        """Run the relationships and formatting comprehensive scenario"""
        result = self.run_test("301_integration_rel_fmt")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_complete_system_integration(self):
        """Run the complete system integration scenario"""
        result = self.run_test("301_integration_complete")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
