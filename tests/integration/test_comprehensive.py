#!/usr/bin/env python3
"""
Comprehensive Integration Tests - CLI-based

This test suite covers comprehensive integration scenarios using the CLI framework,
including complex file relationships, multi-level includes, and end-to-end workflows.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestComprehensiveIntegrationCLI(UnifiedTestCase):
    """Comprehensive integration tests using CLI interface"""

    def test_comprehensive_c_to_h_relationships(self):
        """Test comprehensive C to H file relationships with full integration"""
        result = self.run_test("comprehensive_c_to_h_relationships")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_comprehensive_header_to_header_relationships(self):
        """Test comprehensive header-to-header relationships integration"""
        result = self.run_test("comprehensive_header_to_header_relationships")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_comprehensive_typedef_relationships(self):
        """Test comprehensive typedef relationships integration"""
        result = self.run_test("comprehensive_typedef_relationships")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_parser_tokenizer_integration(self):
        """Test parser-tokenizer integration with complex structures"""
        result = self.run_test("parser_tokenizer_integration")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)

    def test_complete_system_integration(self):
        """Test complete system integration with real-world project structure"""
        result = self.run_test("complete_system_integration")
        
        self.validate_execution_success(result)
        self.validate_test_output(result)


if __name__ == "__main__":
    unittest.main()