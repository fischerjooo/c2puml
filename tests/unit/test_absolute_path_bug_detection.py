#!/usr/bin/env python3
"""
Comprehensive tests to detect bugs related to absolute paths and missing source files
in generated diagrams.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from c_to_plantuml.generator import PlantUMLGenerator
from c_to_plantuml.models import (
    FileModel,
    ProjectModel,
    Field,
    Struct,
    Enum,
    Function,
)
from c_to_plantuml.parser import CParser


class TestAbsolutePathBugDetection(unittest.TestCase):
    """Comprehensive tests to detect absolute path related bugs"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = PlantUMLGenerator()
        self.parser = CParser()
        self.temp_dir = tempfile.mkdtemp()
        self.test_dir = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_absolute_path_file_keys_in_project_model(self):
        """Test that files with absolute path keys are properly handled"""
        # Create test files
        main_c_path = self.test_dir / "main.c"
        utils_h_path = self.test_dir / "utils.h"
        
        with open(main_c_path, "w") as f:
            f.write('#include "utils.h"\nint main() { return 0; }\n')
        
        with open(utils_h_path, "w") as f:
            f.write('// utils.h content\n#define UTILS_H\n')

        # Create FileModel instances with absolute paths as keys
        main_file_model = FileModel(
            file_path=str(main_c_path),
            relative_path="main.c",
            project_root=str(self.test_dir),
            encoding_used="utf-8",
            includes={"utils.h"},
            structs={},
            enums={},
            unions={},
            functions=[Function("main", "int", [], False, False)],
            globals=[],
            macros=[],
            aliases={}
        )

        utils_file_model = FileModel(
            file_path=str(utils_h_path),
            relative_path="utils.h",
            project_root=str(self.test_dir),
            encoding_used="utf-8",
            includes=set(),
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            macros=["#define UTILS_H"],
            aliases={}
        )

        # Create ProjectModel with absolute paths as keys
        project_model = ProjectModel(
            project_name="test_project",
            project_root=str(self.test_dir),
            files={
                str(main_c_path): main_file_model,
                str(utils_h_path): utils_file_model
            }
        )

        # Test the _build_include_tree method
        include_tree = self.generator._build_include_tree(
            main_file_model, project_model, include_depth=1
        )

        # Verify that both files are found
        expected_files = {str(main_c_path), str(utils_h_path)}
        actual_files = set(include_tree.keys())
        
        self.assertEqual(actual_files, expected_files, 
                        f"Expected to find {expected_files}, but found {actual_files}")

    def test_mixed_absolute_and_relative_paths(self):
        """Test handling of mixed absolute and relative paths in project model"""
        # Create test files
        main_c_path = self.test_dir / "main.c"
        utils_h_path = self.test_dir / "utils.h"
        
        with open(main_c_path, "w") as f:
            f.write('#include "utils.h"\nint main() { return 0; }\n')
        
        with open(utils_h_path, "w") as f:
            f.write('// utils.h content\n#define UTILS_H\n')

        # Create FileModel instances - one with absolute path, one with relative
        main_file_model = FileModel(
            file_path=str(main_c_path),
            relative_path="main.c",
            project_root=str(self.test_dir),
            encoding_used="utf-8",
            includes={"utils.h"},
            structs={},
            enums={},
            unions={},
            functions=[Function("main", "int", [], False, False)],
            globals=[],
            macros=[],
            aliases={}
        )

        utils_file_model = FileModel(
            file_path="utils.h",
            relative_path="utils.h",
            project_root=str(self.test_dir),
            encoding_used="utf-8",
            includes=set(),
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            macros=["#define UTILS_H"],
            aliases={}
        )

        # Create ProjectModel with mixed path keys
        project_model = ProjectModel(
            project_name="test_project",
            project_root=str(self.test_dir),
            files={
                str(main_c_path): main_file_model,  # Absolute path
                "utils.h": utils_file_model         # Relative path
            }
        )

        # Test the _build_include_tree method
        include_tree = self.generator._build_include_tree(
            main_file_model, project_model, include_depth=1
        )

        # Verify that both files are found
        expected_files = {str(main_c_path), "utils.h"}
        actual_files = set(include_tree.keys())
        
        self.assertEqual(actual_files, expected_files, 
                        f"Expected to find {expected_files}, but found {actual_files}")

    def test_missing_source_files_in_generated_diagram(self):
        """Test that source files are not missing from generated diagrams"""
        # Create test files
        main_c_path = self.test_dir / "main.c"
        utils_h_path = self.test_dir / "utils.h"
        
        with open(main_c_path, "w") as f:
            f.write('#include "utils.h"\nint main() { return 0; }\n')
        
        with open(utils_h_path, "w") as f:
            f.write('// utils.h content\n#define UTILS_H\n')

        # Create FileModel instances
        main_file_model = FileModel(
            file_path=str(main_c_path),
            relative_path="main.c",
            project_root=str(self.test_dir),
            encoding_used="utf-8",
            includes={"utils.h"},
            structs={},
            enums={},
            unions={},
            functions=[Function("main", "int", [], False, False)],
            globals=[],
            macros=[],
            aliases={}
        )

        utils_file_model = FileModel(
            file_path=str(utils_h_path),
            relative_path="utils.h",
            project_root=str(self.test_dir),
            encoding_used="utf-8",
            includes=set(),
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            macros=["#define UTILS_H"],
            aliases={}
        )

        # Create ProjectModel
        project_model = ProjectModel(
            project_name="test_project",
            project_root=str(self.test_dir),
            files={
                str(main_c_path): main_file_model,
                str(utils_h_path): utils_file_model
            }
        )

        # Generate PlantUML diagram
        diagram = self.generator.generate_diagram(
            main_file_model, project_model, include_depth=1
        )

        # Verify that both source and header files are present in the diagram
        self.assertIn("class \"main\" as MAIN", diagram, "Main source file missing from diagram")
        self.assertIn("class \"utils\" as HEADER_UTILS", diagram, "Header file missing from diagram")

    def test_missing_header_classes_in_generated_diagram(self):
        """Test that header file classes are not missing from generated diagrams"""
        # Create test files with structs and enums
        main_c_path = self.test_dir / "main.c"
        utils_h_path = self.test_dir / "utils.h"
        
        with open(main_c_path, "w") as f:
            f.write('#include "utils.h"\nint main() { return 0; }\n')
        
        with open(utils_h_path, "w") as f:
            f.write('''// utils.h content
#define UTILS_H
typedef struct point_tag {
    int x;
    int y;
} point_t;

typedef enum color_tag {
    RED,
    GREEN,
    BLUE
} color_t;
''')

        # Create FileModel instances with structs and enums
        main_file_model = FileModel(
            file_path=str(main_c_path),
            relative_path="main.c",
            project_root=str(self.test_dir),
            encoding_used="utf-8",
            includes={"utils.h"},
            structs={},
            enums={},
            unions={},
            functions=[Function("main", "int", [], False, False)],
            globals=[],
            macros=[],
            aliases={}
        )

        utils_file_model = FileModel(
            file_path=str(utils_h_path),
            relative_path="utils.h",
            project_root=str(self.test_dir),
            encoding_used="utf-8",
            includes=set(),
            structs={"point_t": Struct("point_t", [], tag_name="point_tag")},
            enums={"color_t": Enum("color_t", [], tag_name="color_tag")},
            unions={},
            functions=[],
            globals=[],
            macros=["#define UTILS_H"],
            aliases={}
        )

        # Create ProjectModel
        project_model = ProjectModel(
            project_name="test_project",
            project_root=str(self.test_dir),
            files={
                str(main_c_path): main_file_model,
                str(utils_h_path): utils_file_model
            }
        )

        # Generate PlantUML diagram
        diagram = self.generator.generate_diagram(
            main_file_model, project_model, include_depth=1
        )

        # Verify that typedef classes are present in the diagram
        self.assertIn("class \"point_t\" as TYPEDEF_POINT_T", diagram, "Struct typedef missing from diagram")
        self.assertIn("class \"color_t\" as TYPEDEF_COLOR_T", diagram, "Enum typedef missing from diagram")

    def test_include_relationships_preserved_with_absolute_paths(self):
        """Test that include relationships are preserved when using absolute paths"""
        # Create test files
        main_c_path = self.test_dir / "main.c"
        utils_h_path = self.test_dir / "utils.h"
        
        with open(main_c_path, "w") as f:
            f.write('#include "utils.h"\nint main() { return 0; }\n')
        
        with open(utils_h_path, "w") as f:
            f.write('// utils.h content\n#define UTILS_H\n')

        # Create FileModel instances
        main_file_model = FileModel(
            file_path=str(main_c_path),
            relative_path="main.c",
            project_root=str(self.test_dir),
            encoding_used="utf-8",
            includes={"utils.h"},
            structs={},
            enums={},
            unions={},
            functions=[Function("main", "int", [], False, False)],
            globals=[],
            macros=[],
            aliases={}
        )

        utils_file_model = FileModel(
            file_path=str(utils_h_path),
            relative_path="utils.h",
            project_root=str(self.test_dir),
            encoding_used="utf-8",
            includes=set(),
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            macros=["#define UTILS_H"],
            aliases={}
        )

        # Create ProjectModel with absolute paths
        project_model = ProjectModel(
            project_name="test_project",
            project_root=str(self.test_dir),
            files={
                str(main_c_path): main_file_model,
                str(utils_h_path): utils_file_model
            }
        )

        # Generate PlantUML diagram
        diagram = self.generator.generate_diagram(
            main_file_model, project_model, include_depth=1
        )

        # Verify that include relationships are present
        self.assertIn("MAIN --> HEADER_UTILS : <<include>>", diagram, "Include relationship missing from diagram")

    def test_deep_include_dependencies_with_absolute_paths(self):
        """Test deep include dependencies work correctly with absolute paths"""
        # Create test files with nested includes
        main_c_path = self.test_dir / "main.c"
        utils_h_path = self.test_dir / "utils.h"
        config_h_path = self.test_dir / "config.h"
        
        with open(main_c_path, "w") as f:
            f.write('#include "utils.h"\nint main() { return 0; }\n')
        
        with open(utils_h_path, "w") as f:
            f.write('#include "config.h"\n#define UTILS_H\n')
        
        with open(config_h_path, "w") as f:
            f.write('#define CONFIG_H\n')

        # Create FileModel instances
        main_file_model = FileModel(
            file_path=str(main_c_path),
            relative_path="main.c",
            project_root=str(self.test_dir),
            encoding_used="utf-8",
            includes={"utils.h"},
            structs={},
            enums={},
            unions={},
            functions=[Function("main", "int", [], False, False)],
            globals=[],
            macros=[],
            aliases={}
        )

        utils_file_model = FileModel(
            file_path=str(utils_h_path),
            relative_path="utils.h",
            project_root=str(self.test_dir),
            encoding_used="utf-8",
            includes={"config.h"},
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            macros=["#define UTILS_H"],
            aliases={}
        )

        config_file_model = FileModel(
            file_path=str(config_h_path),
            relative_path="config.h",
            project_root=str(self.test_dir),
            encoding_used="utf-8",
            includes=set(),
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            macros=["#define CONFIG_H"],
            aliases={}
        )

        # Create ProjectModel with absolute paths
        project_model = ProjectModel(
            project_name="test_project",
            project_root=str(self.test_dir),
            files={
                str(main_c_path): main_file_model,
                str(utils_h_path): utils_file_model,
                str(config_h_path): config_file_model
            }
        )

        # Test with include_depth=2 to include config.h
        include_tree = self.generator._build_include_tree(
            main_file_model, project_model, include_depth=2
        )

        # Verify that all three files are found
        expected_files = {str(main_c_path), str(utils_h_path), str(config_h_path)}
        actual_files = set(include_tree.keys())
        
        self.assertEqual(actual_files, expected_files, 
                        f"Expected to find {expected_files}, but found {actual_files}")

    def test_file_key_matching_robustness(self):
        """Test that file key matching is robust with various path formats"""
        # Create test files
        main_c_path = self.test_dir / "main.c"
        utils_h_path = self.test_dir / "utils.h"
        
        with open(main_c_path, "w") as f:
            f.write('#include "utils.h"\nint main() { return 0; }\n')
        
        with open(utils_h_path, "w") as f:
            f.write('// utils.h content\n#define UTILS_H\n')

        # Create FileModel instances
        main_file_model = FileModel(
            file_path=str(main_c_path),
            relative_path="main.c",
            project_root=str(self.test_dir),
            encoding_used="utf-8",
            includes={"utils.h"},
            structs={},
            enums={},
            unions={},
            functions=[Function("main", "int", [], False, False)],
            globals=[],
            macros=[],
            aliases={}
        )

        utils_file_model = FileModel(
            file_path=str(utils_h_path),
            relative_path="utils.h",
            project_root=str(self.test_dir),
            encoding_used="utf-8",
            includes=set(),
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            macros=["#define UTILS_H"],
            aliases={}
        )

        # Test various key formats in project model
        test_cases = [
            # Absolute paths
            {str(main_c_path): main_file_model, str(utils_h_path): utils_file_model},
            # Relative paths
            {"main.c": main_file_model, "utils.h": utils_file_model},
            # Mixed paths
            {str(main_c_path): main_file_model, "utils.h": utils_file_model},
            # Filenames only
            {"main.c": main_file_model, "utils.h": utils_file_model},
        ]

        for i, files_dict in enumerate(test_cases):
            with self.subTest(test_case=i):
                project_model = ProjectModel(
                    project_name="test_project",
                    project_root=str(self.test_dir),
                    files=files_dict
                )

                # Test the _build_include_tree method
                include_tree = self.generator._build_include_tree(
                    main_file_model, project_model, include_depth=1
                )

                # Verify that both files are found regardless of key format
                expected_keys = set(files_dict.keys())
                actual_keys = set(include_tree.keys())
                
                self.assertEqual(actual_keys, expected_keys, 
                                f"Test case {i}: Expected {expected_keys}, but found {actual_keys}")

    def test_error_handling_for_missing_files(self):
        """Test that missing files are handled gracefully"""
        # Create test files
        main_c_path = self.test_dir / "main.c"
        
        with open(main_c_path, "w") as f:
            f.write('#include "missing.h"\nint main() { return 0; }\n')

        # Create FileModel instance that includes a missing file
        main_file_model = FileModel(
            file_path=str(main_c_path),
            relative_path="main.c",
            project_root=str(self.test_dir),
            encoding_used="utf-8",
            includes={"missing.h"},
            structs={},
            enums={},
            unions={},
            functions=[Function("main", "int", [], False, False)],
            globals=[],
            macros=[],
            aliases={}
        )

        # Create ProjectModel with only the main file
        project_model = ProjectModel(
            project_name="test_project",
            project_root=str(self.test_dir),
            files={
                str(main_c_path): main_file_model
            }
        )

        # Test that the method doesn't crash and handles missing files gracefully
        include_tree = self.generator._build_include_tree(
            main_file_model, project_model, include_depth=1
        )

        # Should only find the main file, not crash
        expected_files = {str(main_c_path)}
        actual_files = set(include_tree.keys())
        
        self.assertEqual(actual_files, expected_files, 
                        f"Expected to find {expected_files}, but found {actual_files}")


if __name__ == "__main__":
    unittest.main()