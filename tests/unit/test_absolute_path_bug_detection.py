#!/usr/bin/env python3
"""
Test for absolute path bug detection in include tree building.
"""

import os

# We need to add the parent directory to Python path for imports
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from c2puml.generator import Generator
from c2puml.parser import CParser


class TestAbsolutePathBugDetection(unittest.TestCase):
    """Test cases for absolute path bug detection and resolution."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.parser = CParser()
        self.generator = Generator()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, filename: str, content: str) -> Path:
        """Create a test file with given content."""
        file_path = self.temp_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def test_relative_path_handling_in_include_tree(self):
        """Test that relative paths are handled correctly in include tree building."""

        # Create a header file
        self.create_test_file(
            "utils.h",
            """
            #ifndef UTILS_H
            #define UTILS_H
            
            typedef struct {
                int id;
                char name[32];
            } util_data_t;
            
            void init_utils(void);
            
            #endif
            """,
        )

        # Create a source file that includes the header
        self.create_test_file(
            "main.c",
            """
            #include "utils.h"
            
            int main() {
                util_data_t data;
                init_utils();
                return 0;
            }
            """,
        )

        # Parse the project
        project_model = self.parser.parse_project(str(self.temp_dir))

        # Get the main.c file model
        main_file = project_model.files["main.c"]

        # Generate the PlantUML diagram - this should not crash due to absolute path issues
        diagram = self.generator.generate_diagram(
            main_file, project_model, include_depth=2
        )

        # Verify basic structure
        self.assertIn("@startuml main", diagram)
        self.assertIn("@enduml", diagram)

        # Check that files are correctly included
        self.assertIn('class "main"', diagram)
        self.assertIn('class "utils"', diagram)

        # Check that typedefs from included files are processed
        self.assertIn("util_data_t", diagram)

    def test_subdirectory_includes_path_resolution(self):
        """Test path resolution for includes in subdirectories."""

        # Create subdirectory structure
        subdir = self.temp_dir / "include"
        subdir.mkdir(parents=True, exist_ok=True)

        # Create header in subdirectory
        header_path = subdir / "types.h"
        with open(header_path, "w", encoding="utf-8") as f:
            f.write(
                """
            #ifndef TYPES_H
            #define TYPES_H
            
            typedef struct {
                float x, y, z;
            } vector3_t;
            
            #endif
            """
            )

        # Create source file that includes header from subdirectory
        self.create_test_file(
            "geometry.c",
            """
            #include "include/types.h"
            
            vector3_t normalize(vector3_t v) {
                // Implementation here
                return v;
            }
            """,
        )

        # Parse the project
        project_model = self.parser.parse_project(str(self.temp_dir))

        # Get the geometry.c file model
        geometry_file = project_model.files["geometry.c"]

        # Generate the PlantUML diagram
        diagram = self.generator.generate_diagram(
            geometry_file, project_model, include_depth=2
        )

        # Verify basic structure - should not crash with path resolution issues
        self.assertIn("@startuml geometry", diagram)
        self.assertIn("@enduml", diagram)

        # Check that the source file is included
        self.assertIn('class "geometry"', diagram)

    def test_mixed_path_styles_handling(self):
        """Test handling of mixed path styles (forward/backward slashes)."""

        # Create header file
        self.create_test_file(
            "config.h",
            """
            #ifndef CONFIG_H
            #define CONFIG_H
            
            #define MAX_CONNECTIONS 100
            #define DEFAULT_PORT 8080
            
            typedef enum {
                CONFIG_OK,
                CONFIG_ERROR
            } config_result_t;
            
            #endif
            """,
        )

        # Create source file with different include styles
        self.create_test_file(
            "server.c",
            """
            #include "config.h"
            
            static config_result_t current_status = CONFIG_OK;
            
            int start_server() {
                return 0;
            }
            """,
        )

        # Parse the project
        project_model = self.parser.parse_project(str(self.temp_dir))

        # Get the server.c file model
        server_file = project_model.files["server.c"]

        # Generate the PlantUML diagram - should handle path styles gracefully
        diagram = self.generator.generate_diagram(
            server_file, project_model, include_depth=2
        )

        # Verify structure
        self.assertIn("@startuml server", diagram)
        self.assertIn("@enduml", diagram)

        # Check that files are properly processed
        self.assertIn('class "server"', diagram)
        self.assertIn('class "config"', diagram)

    def test_absolute_vs_relative_path_consistency(self):
        """Test that absolute and relative paths are handled consistently."""

        # Create test files
        self.create_test_file(
            "common.h",
            """
            #ifndef COMMON_H
            #define COMMON_H
            
            typedef struct {
                int id;
                char buffer[256];
            } common_data_t;
            
            #endif
            """,
        )

        self.create_test_file(
            "processor.c",
            """
            #include "common.h"
            
            void process_data(common_data_t* data) {
                // Process data
            }
            """,
        )

        # Parse the project using absolute path
        project_model_abs = self.parser.parse_project(str(self.temp_dir.resolve()))

        # Parse the project using relative path (if different from absolute)
        rel_path = os.path.relpath(str(self.temp_dir))
        if rel_path != str(self.temp_dir.resolve()):
            project_model_rel = self.parser.parse_project(rel_path)
        else:
            project_model_rel = project_model_abs

        # Generate diagrams with both models
        processor_file_abs = project_model_abs.files["processor.c"]
        diagram_abs = self.generator.generate_diagram(
            processor_file_abs, project_model_abs, include_depth=2
        )

        processor_file_rel = project_model_rel.files["processor.c"]
        diagram_rel = self.generator.generate_diagram(
            processor_file_rel, project_model_rel, include_depth=2
        )

        # Both diagrams should have similar structure
        self.assertIn("@startuml processor", diagram_abs)
        self.assertIn("@startuml processor", diagram_rel)

        self.assertIn("@enduml", diagram_abs)
        self.assertIn("@enduml", diagram_rel)

        # Both should include the main files
        self.assertIn('class "processor"', diagram_abs)
        self.assertIn('class "processor"', diagram_rel)


if __name__ == "__main__":
    unittest.main()
