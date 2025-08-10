#!/usr/bin/env python3
"""
Test Generator New Formatting Through CLI Interface (bundled scenarios)
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase

class TestGeneratorNewFormattingCLI(UnifiedTestCase):
    def test_enum_formatting_with_enumeration_stereotype(self):
        r = self.run_test("generator_new_formatting_cli::enum_stereotype")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_struct_formatting_with_struct_stereotype(self):
        r = self.run_test("generator_new_formatting_cli::struct_stereotype")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_union_formatting_with_union_stereotype(self):
        r = self.run_test("generator_new_formatting_cli::union_stereotype")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_alias_formatting_with_typedef_stereotype_and_alias_prefix(self):
        r = self.run_test("generator_new_formatting_cli::alias_stereotype")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_function_pointer_formatting_with_function_pointer_stereotype(self):
        r = self.run_test("generator_new_formatting_cli::function_pointer")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_complex_typedef_combination(self):
        r = self.run_test("generator_new_formatting_cli::complex_typedef")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_public_private_visibility_logic(self):
        r = self.run_test("generator_new_formatting_cli::visibility_logic")
        self.validate_execution_success(r)
        self.validate_test_output(r)

if __name__ == "__main__":
    unittest.main()