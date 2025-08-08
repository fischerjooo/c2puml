#!/usr/bin/env python3
"""
CLI-based transformer features tests.

Tests advanced transformer features and integration scenarios through CLI interface.
Covers the same functionality as test_transformer_features.py but using CLI.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestTransformerFeaturesCli(UnifiedTestCase):
    """CLI-based tests for advanced transformer features"""

    def test_transform_complex_project_with_filters_cli(self):
        """Test transforming a complex project with various filters through CLI"""
        result = self.run_test("transformer_features_complex_project_filters")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_transform_with_include_relations_cli(self):
        """Test transformer with include relationship processing through CLI"""
        result = self.run_test("transformer_features_include_relations")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_transform_with_renaming_cli(self):
        """Test comprehensive renaming transformations through CLI"""
        result = self.run_test("transformer_features_renaming")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_transform_with_additions_cli(self):
        """Test adding new elements via transformations through CLI"""
        result = self.run_test("transformer_features_additions")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_transform_with_removals_cli(self):
        """Test removing elements via transformations through CLI"""
        result = self.run_test("transformer_features_removals")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_transform_complex_regex_patterns_cli(self):
        """Test complex regex pattern matching in transformations through CLI"""
        result = self.run_test("transformer_features_complex_regex")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_transform_error_handling_cli(self):
        """Test transformer error handling scenarios through CLI"""
        result = self.run_test("transformer_features_error_handling")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_transform_integration_with_parser_and_generator_cli(self):
        """Test transformer integration with full pipeline through CLI"""
        result = self.run_test("transformer_features_integration")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_include_filters_with_filtered_header_cli(self):
        """Test include filters with filtered header files through CLI"""
        result = self.run_test("transformer_features_include_filters")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()