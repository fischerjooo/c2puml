"""
Feature tests for error handling functionality

Tests the ability to handle various error scenarios gracefully.
"""

import os

from .base import BaseFeatureTest


class TestErrorHandlingFeatures(BaseFeatureTest):
    """Test error handling in various scenarios"""

    def test_feature_error_handling(self):
        """Test error handling in various scenarios"""
        from c_to_plantuml.parser import Parser

        # Test with non-existent directory
        parser = Parser()
        with self.assertRaises(Exception):
            parser.c_parser.parse_project("/non/existent/path", recursive=True)

        # Test with empty directory
        empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(empty_dir, exist_ok=True)
        model = parser.c_parser.parse_project(empty_dir, recursive=True)
        self.assertEqual(len(model.files), 0)