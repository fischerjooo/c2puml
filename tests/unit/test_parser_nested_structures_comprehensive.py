#!/usr/bin/env python3
"""
Comprehensive parser nested structures – Repointed
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestParserNestedStructuresComprehensive(UnifiedTestCase):
    def test_struct_and_nested_ordering_comprehensive(self):
        result = self.run_test("struct_and_nested_ordering_comprehensive")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()