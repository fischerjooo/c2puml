#!/usr/bin/env python3
"""
CLI-based comprehensive feature tests for include header processing functionality.

This file now runs only consolidated scenarios.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestIncludeProcessingConsolidated(UnifiedTestCase):
    def test_include_processing_consolidated(self):
        result = self.run_test("include_processing_comprehensive")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_include_processing_error_handling_consolidated(self):
        result = self.run_test("include_processing_error_handling_comprehensive")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()