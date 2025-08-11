#!/usr/bin/env python3
"""
Test Global Parsing – Repointed to consolidated elements
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestGlobalParsingComprehensive(UnifiedTestCase):
    def test_global_parsing_comprehensive(self):
        result = self.run_test("parser_elements_comprehensive")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()