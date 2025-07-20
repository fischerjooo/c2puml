"""
Feature tests for project analysis functionality

Tests the ability to analyze entire C/C++ projects with multiple files.
"""

import os

from .base import BaseFeatureTest


class TestProjectAnalysisFeatures(BaseFeatureTest):
    """Test project analysis functionality"""

    def test_feature_project_analysis(self):
        """Test project analysis functionality"""
        from c_to_plantuml.parser import Parser

        # Create test project
        file1_content = """
#include <stdio.h>

typedef struct User {
    int id;
    char name[50];
} User;

void print_user(User* user) {
    printf("User: %s\\n", user->name);
}
        """

        file2_content = """
#include <stdlib.h>

typedef struct Config {
    int max_users;
    int timeout;
} Config;

Config* create_config(int max_users) {
    return malloc(sizeof(Config));
}
        """

        self.create_test_file("user.c", file1_content)
        self.create_test_file("config.c", file2_content)

        parser = Parser()
        model = parser.c_parser.parse_project(self.temp_dir, recursive=True)

        # Verify analysis results
        self.assertEqual(len(model.files), 2)
        file_names = [os.path.basename(fp) for fp in model.files.keys()]
        self.assertIn("user.c", file_names)
        self.assertIn("config.c", file_names)
