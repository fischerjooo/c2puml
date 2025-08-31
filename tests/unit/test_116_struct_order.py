#!/usr/bin/env python3
"""
Test Struct and Nested Ordering – Comprehensive

Consolidated struct order and PUML field order validation through CLI interface
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tests.framework import UnifiedTestCase


class TestStructOrderPuml(UnifiedTestCase):
    """Test struct and nested ordering comprehensive through the CLI interface"""

    def test_struct_and_nested_ordering_comprehensive(self):
        """Run the consolidated struct order and PUML field order validation scenario"""
        result = self.run_test("116_struct_order")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
