"""
Feature tests for project analysis functionality

Tests project-wide analysis and discovery features.
"""

import os

from tests.feature.base import BaseFeatureTest


class TestProjectAnalysisFeatures(BaseFeatureTest):
    """Test project analysis features"""

    def test_recursive_project_analysis(self):
        """Test recursive project analysis with multiple directories"""
        from c_to_plantuml.parser import Parser

        # Create nested directory structure
        subdir = os.path.join(self.temp_dir, "subdir")
        os.makedirs(subdir, exist_ok=True)

        main_content = """
#include <stdio.h>
#include "subdir/header.h"

int main() {
    return 0;
}
        """

        header_content = """
#ifndef HEADER_H
#define HEADER_H

struct Data {
    int value;
};

#endif
        """

        self.create_test_file("main.c", main_content)
        self.create_test_file("subdir/header.h", header_content)

        # Test recursive analysis
        parser = Parser()
        model = parser.c_parser.parse_project(self.temp_dir, recursive_search=True)

        # Verify both files were found
        self.assertIn("main.c", model.files)
        # Use os.path.join to handle cross-platform path separators
        expected_header_path = os.path.join("subdir", "header.h")
        self.assertIn(expected_header_path, model.files)

    def test_file_filtering(self):
        """Test file filtering during project analysis"""
        from c_to_plantuml.parser import Parser

        # Create various file types
        self.create_test_file("main.c", "int main() { return 0; }")
        self.create_test_file("test.c", "void test() {}")
        self.create_test_file("ignore.txt", "ignore this file")
        self.create_test_file("backup.c~", "backup file")

        # Test analysis with default filtering
        parser = Parser()
        model = parser.c_parser.parse_project(self.temp_dir, recursive_search=True)

        # Should only include .c and .h files
        self.assertIn("main.c", model.files)
        self.assertIn("test.c", model.files)
        # Should not include non-C files
        self.assertNotIn("ignore.txt", model.files)
        self.assertNotIn("backup.c~", model.files)
