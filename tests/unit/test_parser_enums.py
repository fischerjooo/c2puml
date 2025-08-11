#!/usr/bin/env python3
"""
Test Parser Elements – Consolidated

This replaces separate enums/structs/globals/macros tests with a single scenario
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestParserElementsConsolidated(UnifiedTestCase):
    """Test consolidated parser elements through the CLI interface"""

    def test_parser_elements_comprehensive(self):
        result = self.run_test("parser_elements_comprehensive")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()