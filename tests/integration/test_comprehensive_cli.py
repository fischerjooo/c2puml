#!/usr/bin/env python3
"""
CLI-based comprehensive integration tests for the C to PlantUML converter.
Tests complete end-to-end workflows through CLI interface.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestIntegrationCli(UnifiedTestCase):
    """CLI-based integration tests"""

    def test_simple_integration(self):
        """Test basic integration functionality through CLI"""
        result = self.run_test("comprehensive_cli_simple")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()