#!/usr/bin/env python3
"""
CLI-based comprehensive feature tests for include header processing functionality using bundled scenarios.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestIncludeProcessingBundledCLI(UnifiedTestCase):
    def test_basic_workflow(self):
        r = self.run_test("include_processing::basic_workflow")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_c_to_h(self):
        r = self.run_test("include_processing::c_to_h_relationships")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_header_to_header(self):
        r = self.run_test("include_processing::header_to_header_relationships")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_complex_project(self):
        r = self.run_test("include_processing::complex_project_structure")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_nested(self):
        r = self.run_test("include_processing::nested_directory_structure")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_circular(self):
        r = self.run_test("include_processing::circular_include_detection")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_full_pipeline(self):
        r = self.run_test("include_processing::full_pipeline_integration")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_depth(self):
        r = self.run_test("include_processing::include_depth_control")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_filtering(self):
        r = self.run_test("include_processing::include_filtering")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_transitive(self):
        r = self.run_test("include_processing::transitive_dependencies")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_ordering(self):
        r = self.run_test("include_processing::dependency_ordering")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_missing_dependency(self):
        r = self.run_test("include_processing::missing_dependency_handling")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_comprehensive(self):
        r = self.run_test("include_processing::comprehensive_scenario")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_typedef_relationships(self):
        r = self.run_test("include_processing::typedef_relationships")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_macro_propagation(self):
        r = self.run_test("include_processing::macro_propagation")
        self.validate_execution_success(r)
        self.validate_test_output(r)


if __name__ == "__main__":
    unittest.main()