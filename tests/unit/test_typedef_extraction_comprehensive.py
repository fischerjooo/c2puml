#!/usr/bin/env python3
"""
Test Typedef Extraction Comprehensive

This test verifies that the c2puml tool can correctly parse and extract various types
of typedef declarations from C source code through the CLI interface, replacing the
old internal API test with comprehensive CLI-based testing.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestTypedefExtractionComprehensive(UnifiedTestCase):
    """Test comprehensive typedef extraction through the CLI interface"""
    
    def test_simple_typedefs_extraction(self):
        """Test extraction of simple typedefs (basic type aliases)"""
        # Run the complete test using high-level methods
        result = self.run_test("typedef_extraction_comprehensive_simple")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_function_pointer_typedefs_extraction(self):
        """Test extraction of function pointer typedefs"""
        # Run the complete test using high-level methods
        result = self.run_test("typedef_extraction_comprehensive_function_pointers")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_struct_typedefs_extraction(self):
        """Test extraction of struct typedefs"""
        # Run the complete test using high-level methods
        result = self.run_test("typedef_extraction_comprehensive_structs")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_enum_typedefs_extraction(self):
        """Test extraction of enum typedefs"""
        # Run the complete test using high-level methods
        result = self.run_test("typedef_extraction_comprehensive_enums")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_union_typedefs_extraction(self):
        """Test extraction of union typedefs"""
        # Run the complete test using high-level methods
        result = self.run_test("typedef_extraction_comprehensive_unions")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_comprehensive_mixed_typedefs_extraction(self):
        """Test extraction of all typedef types in a comprehensive scenario"""
        # Run the complete test using high-level methods
        result = self.run_test("typedef_extraction_comprehensive_mixed")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_edge_cases_typedefs_extraction(self):
        """Test typedef extraction with edge cases (comments, whitespace, etc.)"""
        # Run the complete test using high-level methods
        result = self.run_test("typedef_extraction_comprehensive_edge_cases")
        
        # Validate results
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()