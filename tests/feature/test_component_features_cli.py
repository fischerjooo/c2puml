#!/usr/bin/env python3
"""
CLI-based Component Features tests.

Comprehensive test suite for verifying component-level functionality through CLI interface.
Tests advanced parser, generator, and project analysis features.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestParserComponentFeaturesCli(UnifiedTestCase):
    """Test advanced parser component features through CLI interface"""

    def test_parse_complex_typedefs_cli(self):
        """Test parsing complex typedef relationships through CLI"""
        result = self.run_test("component_features_complex_typedefs")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_parse_unions_cli(self):
        """Test parsing union structures through CLI"""
        result = self.run_test("component_features_unions")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_parse_function_pointers_cli(self):
        """Test parsing function pointers through CLI"""
        result = self.run_test("component_features_function_pointers")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)


class TestGeneratorComponentFeaturesCli(UnifiedTestCase):
    """Test advanced generator component features through CLI interface"""

    def test_generate_with_typedefs_cli(self):
        """Test PlantUML generation with complex typedefs through CLI"""
        result = self.run_test("component_features_generator_typedefs")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_generate_with_unions_cli(self):
        """Test PlantUML generation with unions through CLI"""
        result = self.run_test("component_features_generator_unions")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_generate_with_complex_relationships_cli(self):
        """Test PlantUML generation with complex relationships through CLI"""
        result = self.run_test("component_features_generator_complex")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)


class TestProjectAnalysisComponentFeaturesCli(UnifiedTestCase):
    """Test advanced project analysis features through CLI interface"""

    def test_project_structure_analysis_cli(self):
        """Test comprehensive project structure analysis through CLI"""
        result = self.run_test("component_features_project_analysis")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_cross_file_dependencies_cli(self):
        """Test cross-file type dependencies analysis through CLI"""
        result = self.run_test("component_features_cross_file_deps")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_recursive_include_handling_cli(self):
        """Test recursive include handling through CLI"""
        result = self.run_test("component_features_recursive_includes")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()