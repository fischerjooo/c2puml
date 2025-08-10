#!/usr/bin/env python3
"""
Generator New Formatting CLI (single-scenario files)
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase

class TestGeneratorNewFormattingCLI(UnifiedTestCase):
    def test_enum_formatting_with_enumeration_stereotype(self):
        r = self.run_test("generator_new_formatting_cli_enum_stereotype")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_struct_formatting_with_struct_stereotype(self):
        r = self.run_test("generator_new_formatting_cli_struct_stereotype")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_union_formatting_with_union_stereotype(self):
        r = self.run_test("generator_new_formatting_cli_union_stereotype")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_alias_formatting_with_typedef_stereotype_and_alias_prefix(self):
        r = self.run_test("generator_new_formatting_cli_alias_stereotype")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_function_pointer_formatting_with_function_pointer_stereotype(self):
        r = self.run_test("generator_new_formatting_cli_function_pointer")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_complex_typedef_combination(self):
        r = self.run_test("generator_new_formatting_cli_complex_typedef")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_public_private_visibility_logic(self):
        r = self.run_test("generator_new_formatting_cli_visibility_logic")
        self.validate_execution_success(r)
        self.validate_test_output(r)

if __name__ == "__main__":
    unittest.main()