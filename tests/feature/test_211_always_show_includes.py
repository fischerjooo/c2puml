"""Feature test for always showing includes in the output diagrams."""

import unittest
from tests.framework import UnifiedTestCase


class TestAlwaysShowIncludesFeature(UnifiedTestCase):
    """Feature test for always showing includes in the output diagrams."""

    def test_always_show_includes(self):
        """Run the always show includes scenario"""
        result = self.run_test("211_always_show_includes")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
