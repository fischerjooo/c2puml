#!/usr/bin/env python3
"""
Test Parser Typedefs – Consolidated

This replaces separate typedef and typedef-struct and enum typedef/simple enum tests with a single scenario
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestParserTypedefsConsolidated(UnifiedTestCase):
    """Test consolidated parser typedefs through the CLI interface"""

    def test_parser_typedefs_comprehensive(self):
        result = self.run_test("parser_typedefs_comprehensive")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()