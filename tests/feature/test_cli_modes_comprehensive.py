#!/usr/bin/env python3
"""
Test CLI Modes Comprehensive (Consolidated)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestCLIModesComprehensive(UnifiedTestCase):
    """Test CLI modes functionality through the CLI interface (single scenario)"""

    def test_cli_modes_and_features_comprehensive(self):
        result = self.run_test("cli_modes_comprehensive")
        self.validate_execution_success(result)
        # Assertions are handled in YAML; only success required here


if __name__ == "__main__":
    unittest.main()