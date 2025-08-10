#!/usr/bin/env python3
"""
Generator Visibility Logic (single-scenario files)
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestGeneratorVisibilityLogic(UnifiedTestCase):
    def test_public_functions(self):
        r = self.run_test("generator_visibility_logic_public_functions")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_private_functions(self):
        r = self.run_test("generator_visibility_logic_private_functions")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_public_globals(self):
        r = self.run_test("generator_visibility_logic_public_globals")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_private_globals(self):
        r = self.run_test("generator_visibility_logic_private_globals")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_mixed_visibility(self):
        r = self.run_test("generator_visibility_logic_mixed_visibility")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_no_headers(self):
        r = self.run_test("generator_visibility_logic_no_headers")
        self.validate_execution_success(r)
        self.validate_test_output(r)


if __name__ == "__main__":
    unittest.main()