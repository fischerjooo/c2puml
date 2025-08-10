#!/usr/bin/env python3
"""
Include Processing Comprehensive (single-scenario files)
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestIncludeProcessing(UnifiedTestCase):
    def test_basic_workflow(self):
        r = self.run_test("include_processing_basic_workflow")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_c_to_h_relationships(self):
        r = self.run_test("include_processing_c_to_h_relationships")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_header_to_header_relationships(self):
        r = self.run_test("include_processing_header_to_header_relationships")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_complex_project_structure(self):
        r = self.run_test("include_processing_complex_project_structure")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_nested_directory_structure(self):
        r = self.run_test("include_processing_nested_directory_structure")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_circular_include_detection(self):
        r = self.run_test("include_processing_circular_include_detection")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_full_pipeline_integration(self):
        r = self.run_test("include_processing_full_pipeline_integration")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_include_depth_control(self):
        r = self.run_test("include_processing_include_depth_control")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_include_filtering(self):
        r = self.run_test("include_processing_include_filtering")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_transitive_dependencies(self):
        r = self.run_test("include_processing_transitive_dependencies")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_dependency_ordering(self):
        r = self.run_test("include_processing_dependency_ordering")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_missing_dependency_handling(self):
        r = self.run_test("include_processing_missing_dependency_handling")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_comprehensive_scenario(self):
        r = self.run_test("include_processing_comprehensive_scenario")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_typedef_relationships(self):
        r = self.run_test("include_processing_typedef_relationships")
        self.validate_execution_success(r)
        self.validate_test_output(r)

    def test_macro_propagation(self):
        r = self.run_test("include_processing_macro_propagation")
        self.validate_execution_success(r)
        self.validate_test_output(r)


if __name__ == "__main__":
    unittest.main()