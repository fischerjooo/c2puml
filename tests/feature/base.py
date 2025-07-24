"""
Base class for feature tests

Provides common setup and teardown functionality for all feature tests.
This base class now inherits from the shared test utilities for consistency.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

# Import shared utilities for consistency
try:
    from tests.utils import TestProjectBuilder, TestDataProviders, create_temp_project
except ImportError:
    # Fallback if utils not available
    TestProjectBuilder = None
    TestDataProviders = None
    create_temp_project = None


class BaseFeatureTest(unittest.TestCase):
    """Base class for feature tests with common setup and teardown"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = []
        
        # Initialize project builder if available
        if TestProjectBuilder:
            self.project_builder = TestProjectBuilder(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, filename: str, content: str) -> str:
        """Create a test file and return its path"""
        file_path = os.path.join(self.temp_dir, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.test_files.append(file_path)
        return file_path

    def write_json_config(self, config_file: str, config: dict) -> None:
        """Write JSON configuration to file"""
        import json

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    
    def get_sample_project(self, project_name: str = "simple_project") -> dict:
        """Get a sample project for testing (uses shared data providers if available)"""
        if TestDataProviders:
            projects = TestDataProviders.get_sample_c_projects()
            return projects.get(project_name, projects["simple_project"])
        else:
            # Fallback minimal project
            return {
                "main.c": """
#include "types.h"

int main() {
    Point p = {0, 0};
    return 0;
}
""",
                "types.h": """
#ifndef TYPES_H
#define TYPES_H

typedef struct {
    int x;
    int y;
} Point;

#endif
"""
            }
    
    def get_sample_config(self, config_name: str = "standard") -> dict:
        """Get a sample configuration for testing (uses shared data providers if available)"""
        if TestDataProviders:
            configs = TestDataProviders.get_sample_configs()
            return configs.get(config_name, configs["standard"])
        else:
            # Fallback minimal config
            return {
                "project_name": "test_project",
                "source_folders": ["."],
                "output_dir": "./output",
                "recursive_search": True
            }
