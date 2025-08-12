#!/usr/bin/env python3
"""
Individual test file for test_generator_basic_plantuml.yml
Auto-generated to maintain 1:1 pairing between .py and .yml files
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestGeneratorBasicPlantuml(UnifiedTestCase):
    """Test class for test_generator_basic_plantuml"""

    def test_generator_basic_plantuml(self):
        """Run the test_generator_basic_plantuml test through CLI interface."""
        result = self.run_test("101_gen_basic")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_generator_basic_plantuml_truncation(self):
        result = self.run_test("101_gen_basic_trunc")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()
