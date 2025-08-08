#!/usr/bin/env python3
"""
Test Component Features Comprehensive
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestComponentFeaturesComprehensive(UnifiedTestCase):
    """Test component features functionality through the CLI interface"""
    
    def test_parser_complex_typedefs_parsing(self):
        """Test parsing complex typedef relationships through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("component_features_comprehensive_complex_typedefs")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_parser_unions_parsing(self):
        """Test parsing union definitions through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("component_features_comprehensive_unions")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_parser_function_pointers_parsing(self):
        """Test parsing function pointer definitions through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("component_features_comprehensive_function_pointers")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_generator_typedef_relationships(self):
        """Test PlantUML generation with typedef relationships through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("component_features_comprehensive_generator_typedefs")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_generator_union_support(self):
        """Test PlantUML generation with union definitions through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("component_features_comprehensive_generator_unions")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_generator_complex_relationships(self):
        """Test PlantUML generation with complex relationships through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("component_features_comprehensive_complex_relationships")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_project_structure_analysis(self):
        """Test project structure analysis through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("component_features_comprehensive_project_structure")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_cross_file_type_dependencies(self):
        """Test cross-file type dependencies through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("component_features_comprehensive_cross_file_dependencies")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_recursive_include_handling(self):
        """Test recursive include handling through the CLI interface"""
        # Run the complete test using high-level methods
        result = self.run_test("component_features_comprehensive_recursive_includes")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()