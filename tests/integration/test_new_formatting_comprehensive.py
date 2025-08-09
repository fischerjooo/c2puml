#!/usr/bin/env python3
"""
New Formatting Comprehensive Integration Tests - CLI-based

This test suite covers comprehensive new PlantUML formatting features using the CLI framework,
including enhanced stereotypes, visibility logic, and proper formatting across multiple files.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestNewFormattingComprehensiveCLI(UnifiedTestCase):
    """Comprehensive new formatting integration tests using CLI interface"""

    def test_complete_formatting_integration(self):
        """Test all new formatting rules working together in a realistic scenario"""
        result = self.run_test("complete_formatting_integration")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_mixed_project_comprehensive_formatting(self):
        """Test formatting in a project with multiple files and cross-references"""
        result = self.run_test("mixed_project_comprehensive_formatting")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()