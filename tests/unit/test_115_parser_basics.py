#!/usr/bin/env python3
"""
Test Parser Comprehensive Basics

Consolidated basic parsing via CLI
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestParserComprehensiveBasics(UnifiedTestCase):
    """Test basic/mixed parsing through the CLI interface"""

    def test_parser_comprehensive_basics(self):
        result = self.run_test("115_parser_basics")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()