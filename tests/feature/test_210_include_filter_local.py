"""Test include filter with local only option through the CLI interface"""

import unittest
from tests.framework import UnifiedTestCase


class TestIncludeFilterLocalOnlyFeature(UnifiedTestCase):
    """Test include filter with local only option through the CLI interface"""

    def test_include_filter_local_only(self):
        """Run the include filter local only scenario"""
        result = self.run_test("210_include_filter_local")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
