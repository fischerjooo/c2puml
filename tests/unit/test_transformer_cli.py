#!/usr/bin/env python3
"""
CLI-based comprehensive transformer tests.
Tests transformer functionality through CLI interface covering major use cases.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestTransformerCli(UnifiedTestCase):
    """CLI-based comprehensive transformer tests"""

    def test_transformer_file_filtering_comprehensive(self):
        """Test comprehensive file filtering capabilities through CLI"""
        result = self.run_test("transformer_cli_file_filtering")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_transformer_remove_operations_comprehensive(self):
        """Test comprehensive remove operations through CLI"""
        result = self.run_test("transformer_cli_remove_operations")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_transformer_rename_operations_comprehensive(self):
        """Test comprehensive rename operations through CLI"""
        result = self.run_test("transformer_cli_rename_operations")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_transformer_include_processing_comprehensive(self):
        """Test comprehensive include processing through CLI"""
        result = self.run_test("transformer_cli_include_processing")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_transformer_transformation_containers(self):
        """Test transformation containers functionality through CLI"""
        result = self.run_test("transformer_cli_transformation_containers")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_transformer_error_handling(self):
        """Test transformer error handling scenarios through CLI"""
        result = self.run_test("transformer_cli_error_handling")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()