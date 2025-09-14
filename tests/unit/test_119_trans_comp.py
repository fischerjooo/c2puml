#!/usr/bin/env python3
"""
Transformer – Consolidated
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tests.framework import UnifiedTestCase


class TestTransformerComprehensive(UnifiedTestCase):
    """Test comprehensive transformer functionality through the CLI interface"""

    def test_transformer_comprehensive(self):
        """Run the consolidated transformer scenario"""
        result = self.run_test("119_trans_comp")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
