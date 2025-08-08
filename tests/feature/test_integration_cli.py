#!/usr/bin/env python3
"""
Integration Feature Tests via CLI
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestIntegrationCLI(UnifiedTestCase):
    """Integration tests using the CLI interface"""

    def test_complete_workflow(self):
        """End-to-end parse → transform → generate workflow"""
        result = self.run_test("integration_cli_complete_workflow")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()