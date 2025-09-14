#!/usr/bin/env python3
"""
Test Parser Includes – Comprehensive

Consolidated basic includes and include filtering/depth validation
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tests.framework import UnifiedTestCase


class TestParserIncludes(UnifiedTestCase):
    """Test parsing include statements through the CLI interface"""

    def test_parser_includes_comprehensive(self):
        """Run the comprehensive parser includes scenario"""
        result = self.run_test("132_parser_includes")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
