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
        result = self.run_test("202_include_proc")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_include_processing_error_handling_consolidated(self):
        result = self.run_test("202_include_proc_error")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_include_processing_basic_consolidated(self):
        result = self.run_test("202_include_proc_basic")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()