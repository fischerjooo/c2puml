#!/usr/bin/env python3
"""
Test Parser Typedefs Consolidated
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tests.framework import UnifiedTestCase


class TestParserTypedefsConsolidated(UnifiedTestCase):
    """Test consolidated parser typedefs through the CLI interface"""

    def test_parser_typedefs_comprehensive(self):
        """Run the consolidated parser typedefs scenario"""
        result = self.run_test("126_parser_typedefs")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
