#!/usr/bin/env python3
"""
Test Generator Naming Conventions – simplified using unified framework
"""

import os
import sys
import unittest
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestGeneratorNamingComprehensive(UnifiedTestCase):
    """Test generator naming conventions using the unified simple pattern"""

    def test_generator_naming_conventions_comprehensive(self):
        result = self.run_test("123_gen_naming")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()