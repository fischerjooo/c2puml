#!/usr/bin/env python3
"""
Test Component Features – Consolidated
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tests.framework import UnifiedTestCase


class TestComponentFeaturesConsolidated(UnifiedTestCase):
    """Test component features types and relationships through the CLI interface"""

    def test_component_features_types_and_relationships_comprehensive(self):
        """Run the component features types and relationships comprehensive scenario"""
        result = self.run_test("203_comp_features")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
