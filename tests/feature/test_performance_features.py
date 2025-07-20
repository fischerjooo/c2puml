"""
Feature tests for performance functionality

Tests the performance characteristics of the tool with reasonable limits.
"""

import time

from .base import BaseFeatureTest


class TestPerformanceFeatures(BaseFeatureTest):
    """Test performance with reasonable limits"""

    def test_feature_performance(self):
        """Test performance with reasonable limits"""
        from c_to_plantuml.parser import Parser

        # Create a moderately complex test project
        for i in range(5):
            content = f"""
#include <stdio.h>

struct Data{i} {{
    int value{i};
    char name{i}[50];
}};

int process{i}(int input) {{
    return input * {i};
}}
            """
            self.create_test_file(f"file{i}.c", content)

        # Measure analysis time
        parser = Parser()
        start_time = time.perf_counter()
        model = parser.c_parser.parse_project(self.temp_dir, recursive=True)
        end_time = time.perf_counter()

        duration = end_time - start_time

        # Verify performance (should complete within 10 seconds for test files)
        self.assertLess(
            duration,
            10.0,
            f"Analysis took {duration:.2f} seconds, expected < 10 seconds",
        )
        self.assertEqual(len(model.files), 5)
