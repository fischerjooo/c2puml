#!/usr/bin/env python3
"""
Transformer – Consolidated
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestTransformerComprehensive(UnifiedTestCase):
    def test_transformer_comprehensive(self):
        result = self.run_test("transformer_comprehensive")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()