#!/usr/bin/env python3
"""
Unit test for LOCAL_INLINE function detection
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tests.framework import UnifiedTestCase


class TestLocalInlineFunctions(UnifiedTestCase):
    def test_local_inline_functions_detection(self):
        """Test that LOCAL_INLINE functions are correctly parsed and detected as inline"""
        result = self.run_test("140_local_inline_funcs")
        self.validate_execution_success(result)
        self.validate_test_output(result)