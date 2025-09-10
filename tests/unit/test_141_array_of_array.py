#!/usr/bin/env python3
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tests.framework import UnifiedTestCase


class TestArrayOfArrayFormatting(UnifiedTestCase):
    def test_array_of_array_typedef_struct_field(self):
        result = self.run_test("141_array_of_array")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()

