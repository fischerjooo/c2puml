#!/usr/bin/env python3
"""
Test Typedef Extraction Comprehensive

This test verifies that the c2puml tool can correctly parse and extract various types
of typedef declarations from C source code through the CLI interface, replacing multiple
YAML scenarios with a single comprehensive one.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestTypedefExtractionComprehensive(UnifiedTestCase):
    """Test comprehensive typedef extraction through the CLI interface"""

    def test_typedef_extraction_comprehensive(self):
        """Run the consolidated typedef extraction scenario"""
        result = self.run_test("typedef_extraction_comprehensive")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()