#!/usr/bin/env python3
"""
Component Features – Types and Relationships (Consolidated Runner)
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestComponentFeaturesTypesAndRelationshipsConsolidated(UnifiedTestCase):
    def test_component_features_types_and_relationships_comprehensive(self):
        result = self.run_test("203_comp_features")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()