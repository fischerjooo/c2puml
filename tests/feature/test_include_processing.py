#!/usr/bin/env python3
"""
CLI-based comprehensive feature tests for include header processing functionality.

This file contains feature tests refactored to use the unified CLI testing framework,
organized into logical test groups focusing on:
1. Basic workflow features
2. Complex project structures  
3. Integration scenarios
4. Dependency processing
5. Comprehensive end-to-end testing

All tests use the CLI interface through the unified testing framework.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestIncludeProcessingBasicFeaturesCLI(UnifiedTestCase):
    """Basic feature tests for include header processing workflow through CLI."""

    def test_basic_include_processing_workflow(self):
        """Test basic include processing workflow from parsing to generation through CLI."""
        result = self.run_test("include_processing_basic_workflow")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_c_to_h_relationships(self):
        """Test feature-level C to H file relationships through CLI."""
        result = self.run_test("include_processing_c_to_h_relationships")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_header_to_header_relationships(self):
        """Test feature-level header to header relationships through CLI."""
        result = self.run_test("include_processing_header_to_header_relationships")
        self.validate_execution_success(result)
        self.validate_test_output(result)


class TestIncludeProcessingComplexFeaturesCLI(UnifiedTestCase):
    """Complex feature tests for advanced include processing scenarios through CLI."""

    def test_complex_project_structure(self):
        """Test complex project structure with multiple layers of includes through CLI."""
        result = self.run_test("include_processing_complex_project_structure")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_nested_directory_structure(self):
        """Test nested directory structure with relative includes through CLI."""
        result = self.run_test("include_processing_nested_directory_structure")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_circular_include_detection(self):
        """Test circular include detection and handling through CLI."""
        result = self.run_test("include_processing_circular_include_detection")
        self.validate_execution_success(result)
        self.validate_test_output(result)


class TestIncludeProcessingIntegrationCLI(UnifiedTestCase):
    """Integration tests for include processing with full pipeline through CLI."""

    def test_full_pipeline_with_includes(self):
        """Test full pipeline with complex include relationships through CLI."""
        result = self.run_test("include_processing_full_pipeline_integration")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_include_depth_control(self):
        """Test include depth control functionality through CLI."""
        result = self.run_test("include_processing_include_depth_control")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_include_filtering(self):
        """Test include filtering functionality through CLI."""
        result = self.run_test("include_processing_include_filtering")
        self.validate_execution_success(result)
        self.validate_test_output(result)


class TestIncludeProcessingDependenciesCLI(UnifiedTestCase):
    """Dependency processing tests for include relationships through CLI."""

    def test_transitive_dependencies(self):
        """Test transitive dependency resolution through CLI."""
        result = self.run_test("include_processing_transitive_dependencies")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_dependency_ordering(self):
        """Test that dependency ordering is preserved through CLI."""
        result = self.run_test("include_processing_dependency_ordering")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_missing_dependency_handling(self):
        """Test handling of missing dependencies through CLI."""
        result = self.run_test("include_processing_missing_dependency_handling")
        self.validate_execution_success(result)
        self.validate_test_output(result)


class TestIncludeProcessingComprehensiveCLI(UnifiedTestCase):
    """Comprehensive end-to-end tests for include processing through CLI."""

    def test_comprehensive_include_scenario(self):
        """Test comprehensive include processing scenario through CLI."""
        result = self.run_test("include_processing_comprehensive_scenario")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_typedef_relationships_across_files(self):
        """Test typedef relationships across multiple files through CLI."""
        result = self.run_test("include_processing_typedef_relationships")
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_macro_propagation_through_includes(self):
        """Test macro propagation through include relationships through CLI."""
        result = self.run_test("include_processing_macro_propagation")
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()