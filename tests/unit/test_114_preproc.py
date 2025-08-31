#!/usr/bin/env python3
"""
Test Preprocessor Handling Comprehensive
Consolidated test for preprocessor handling and macros through CLI interface
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tests.framework import UnifiedTestCase


class TestPreprocessorHandlingComprehensive(UnifiedTestCase):
    """Test comprehensive preprocessor handling functionality through the CLI interface"""

    def test_preprocessor_and_macros_comprehensive(self):
        """Run the consolidated preprocessor and macros scenario"""
        result = self.run_test("114_preproc")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
