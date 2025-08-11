#!/usr/bin/env python3
"""
Comprehensive test for generator include handling and filtering through CLI interface – Consolidated
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestGeneratorIncludesComprehensive(UnifiedTestCase):
    def test_generator_includes_and_filtering_comprehensive(self):
        result = self.run_test("122_gen_includes")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()