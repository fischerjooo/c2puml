#!/usr/bin/env python3
"""
Test Anonymous Processing Comprehensive (bundled scenarios)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestAnonymousProcessingComprehensive(UnifiedTestCase):
    def test_anonymous_processing_comprehensive(self):
        r = self.run_test("anonymous_structures_and_debug::debug_parsing_anonymous")
        self.validate_execution_success(r)
        self.validate_test_output(r)


if __name__ == "__main__":
    unittest.main()