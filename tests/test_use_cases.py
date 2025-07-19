#!/usr/bin/env python3
"""
Use case focused unit tests for the C to PlantUML converter

These tests cover specific use cases and behavioral scenarios
described in the specification. They now use the examples from
the examples folder and expectations classes for validation.
"""

import unittest
from pathlib import Path
from tests.test_helper import UseCaseTestHelper
from tests.expectations import (
    BasicProjectExpectations,
    ComplexTypedefExpectations,
    ConfigurationExpectations,
    LargeCodebaseExpectations,
    ErrorHandlingExpectations
)


class TestBasicProjectUseCase(unittest.TestCase):
    """Test the basic project analysis use case"""
    
    def setUp(self):
        self.helper = UseCaseTestHelper(BasicProjectExpectations)
        self.project_dir = Path(__file__).parent.parent / "examples" / "use_case_basic_project" / "input"
        self.config_file = Path(__file__).parent.parent / "examples" / "use_case_basic_project" / "config.json"
    
    def test_basic_project_analysis(self):
        """Test basic project analysis use case"""
        self.helper.run_basic_analysis_test(self.project_dir, self)
    
    def test_basic_project_generation(self):
        """Test PlantUML generation for basic project"""
        self.helper.run_generation_test(self.project_dir, self)


class TestComplexTypedefUseCase(unittest.TestCase):
    """Test the complex typedef analysis use case"""
    
    def setUp(self):
        self.helper = UseCaseTestHelper(ComplexTypedefExpectations)
        self.project_dir = Path(__file__).parent.parent / "examples" / "use_case_typedef_complex" / "input"
        self.config_file = Path(__file__).parent.parent / "examples" / "use_case_typedef_complex" / "config.json"
    
    def test_complex_typedef_analysis(self):
        """Test complex typedef analysis use case"""
        self.helper.run_basic_analysis_test(self.project_dir, self)
    
    def test_typedef_relationship_visualization(self):
        """Test typedef relationship visualization in PlantUML"""
        self.helper.run_generation_test(self.project_dir, self)


class TestLargeCodebaseUseCase(unittest.TestCase):
    """Test the large codebase analysis use case"""
    
    def setUp(self):
        self.helper = UseCaseTestHelper(LargeCodebaseExpectations)
        self.project_dir = Path(__file__).parent.parent / "examples" / "use_case_large_codebase" / "input"
        self.config_file = Path(__file__).parent.parent / "examples" / "use_case_large_codebase" / "config.json"
    
    def test_large_codebase_analysis(self):
        """Test large codebase analysis use case"""
        self.helper.run_basic_analysis_test(self.project_dir, self)
    
    def test_large_codebase_generation(self):
        """Test PlantUML generation for large codebase"""
        self.helper.run_generation_test(self.project_dir, self)


class TestErrorHandlingUseCase(unittest.TestCase):
    """Test error handling use cases"""
    
    def setUp(self):
        self.helper = UseCaseTestHelper(ErrorHandlingExpectations)
        self.project_dir = Path(__file__).parent.parent / "examples" / "use_case_error_handling" / "input"
        self.config_file = Path(__file__).parent.parent / "examples" / "use_case_error_handling" / "config.json"
    
    def test_encoding_detection_and_recovery(self):
        """Test encoding detection and recovery"""
        self.helper.run_encoding_test(self)
    
    def test_partial_parsing_on_errors(self):
        """Test partial parsing when encountering errors"""
        self.helper.run_error_handling_test(self.project_dir, self)
    
    def test_missing_file_handling(self):
        """Test handling of missing files"""
        self.helper.run_error_handling_test(self.project_dir, self)


class TestConfigurationUseCase(unittest.TestCase):
    """Test configuration-driven use cases"""
    
    def setUp(self):
        self.helper = UseCaseTestHelper(ConfigurationExpectations)
        self.project_dir = Path(__file__).parent.parent / "examples" / "use_case_configuration" / "input"
        self.config_file = Path(__file__).parent.parent / "examples" / "use_case_configuration" / "config.json"
        
        # Verify that the files exist
        if not self.config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")
        if not self.project_dir.exists():
            raise FileNotFoundError(f"Project directory not found: {self.project_dir}")
    
    def test_configuration_filtering(self):
        """Test configuration-based filtering"""
        self.helper.run_configuration_test(self.project_dir, self.config_file, self)


if __name__ == '__main__':
    unittest.main()