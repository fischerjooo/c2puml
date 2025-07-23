#!/usr/bin/env python3
"""
Unit tests for user-configurable filtering features via config.json
"""

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from c_to_plantuml.config import Config
from c_to_plantuml.models import (
    Alias, Enum, Field, FileModel, Function, ProjectModel, Struct, Union
)
from c_to_plantuml.transformer import Transformer


class TestUserConfigurableFiltering(unittest.TestCase):
    """Test cases for user-configurable filtering features via config.json"""

    def setUp(self):
        """Set up test fixtures"""
        self.transformer = Transformer()
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = []

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

    def create_test_model(self) -> ProjectModel:
        """Create a test project model with various elements"""
        # Create a file model with different types of elements
        file_model = FileModel(
            file_path="/test/project/main.c",
            relative_path="main.c",
            project_root="/test/project",
            encoding_used="utf-8",
            structs={
                "PublicStruct": Struct("PublicStruct", [Field("id", "int")]),
                "InternalStruct": Struct("InternalStruct", [Field("data", "char*")]),
                "UserData": Struct("UserData", [Field("name", "char*"), Field("age", "int")]),
                "temp_data": Struct("temp_data", [Field("buffer", "void*")])
            },
            enums={
                "Status": Enum("Status", ["OK", "ERROR", "PENDING"]),
                "internal_state": Enum("internal_state", ["IDLE", "BUSY"]),
                "UserType": Enum("UserType", ["ADMIN", "USER", "GUEST"])
            },
            functions=[
                Function("public_function", "int", [Field("param", "int")]),
                Function("private_function", "void", [Field("data", "char*")]),
                Function("main", "int", []),
                Function("internal_helper", "void", [])
            ],
            globals=[
                Field("global_var", "int"),
                Field("internal_var", "char*"),
                Field("public_constant", "const int")
            ],
            macros=["MAX_SIZE", "internal_macro", "PUBLIC_DEFINE"],
            aliases={
                "UserPtr": Alias("UserPtr", "UserData*"),
                "internal_type": Alias("internal_type", "void*"),
                "PublicType": Alias("PublicType", "int")
            },
            includes={"stdio.h", "stdlib.h", "internal.h"},
            unions={}
        )

        # Create project model
        model = ProjectModel(
            project_name="TestProject",
            project_root="/test/project",
            files={"main.c": file_model},
        )

        return model

    def test_file_filters_include_patterns(self):
        """Test file filtering with include patterns"""
        config = Config()
        config.file_filters = {
            "include": [r".*\.c$", r".*\.h$"],
            "exclude": []
        }
        config._compile_patterns()

        # Test files that should be included
        self.assertTrue(config._should_include_file("main.c"))
        self.assertTrue(config._should_include_file("header.h"))
        self.assertTrue(config._should_include_file("src/file.c"))
        self.assertTrue(config._should_include_file("include/config.h"))

        # Test files that should be excluded
        self.assertFalse(config._should_include_file("readme.txt"))
        self.assertFalse(config._should_include_file("script.py"))
        self.assertFalse(config._should_include_file("Makefile"))

    def test_file_filters_exclude_patterns(self):
        """Test file filtering with exclude patterns"""
        config = Config()
        config.file_filters = {
            "include": [],
            "exclude": [r".*test.*", r".*temp.*", r".*\.bak$"]
        }
        config._compile_patterns()

        # Test files that should be excluded
        self.assertFalse(config._should_include_file("test.c"))
        self.assertFalse(config._should_include_file("temp.h"))
        self.assertFalse(config._should_include_file("file.bak"))
        self.assertFalse(config._should_include_file("unittest.c"))
        self.assertFalse(config._should_include_file("temporary.h"))

        # Test files that should be included
        self.assertTrue(config._should_include_file("main.c"))
        self.assertTrue(config._should_include_file("header.h"))
        self.assertTrue(config._should_include_file("production.c"))

    def test_file_filters_include_and_exclude(self):
        """Test file filtering with both include and exclude patterns"""
        config = Config()
        config.file_filters = {
            "include": [r".*\.c$", r".*\.h$"],
            "exclude": [r".*test.*", r".*temp.*"]
        }
        config._compile_patterns()

        # Test files that should be included (match include, don't match exclude)
        self.assertTrue(config._should_include_file("main.c"))
        self.assertTrue(config._should_include_file("header.h"))
        self.assertTrue(config._should_include_file("production.c"))

        # Test files that should be excluded (match exclude patterns)
        self.assertFalse(config._should_include_file("test.c"))
        self.assertFalse(config._should_include_file("temp.h"))
        self.assertFalse(config._should_include_file("unittest.c"))

        # Test files that should be excluded (don't match include patterns)
        self.assertFalse(config._should_include_file("readme.txt"))
        self.assertFalse(config._should_include_file("script.py"))

    def test_element_filters_structs(self):
        """Test element filtering for structs"""
        config = Config()
        config.element_filters = {
            "structs": {
                "include": [r"^[A-Z].*"],
                "exclude": [r".*[Ii]nternal.*", r".*temp.*"]
            }
        }
        config._compile_patterns()

        model = self.create_test_model()
        file_model = list(model.files.values())[0]

        # Apply filters
        filtered_model = config._apply_element_filters(file_model)

        # Check that only public structs are included
        self.assertIn("PublicStruct", filtered_model.structs)
        self.assertIn("UserData", filtered_model.structs)
        self.assertNotIn("InternalStruct", filtered_model.structs)
        self.assertNotIn("temp_data", filtered_model.structs)

    def test_element_filters_functions(self):
        """Test element filtering for functions"""
        config = Config()
        config.element_filters = {
            "functions": {
                "include": [r"^public_.*", r"^main$"],
                "exclude": [r".*private.*", r".*internal.*"]
            }
        }
        config._compile_patterns()

        model = self.create_test_model()
        file_model = list(model.files.values())[0]

        # Apply filters
        filtered_model = config._apply_element_filters(file_model)

        # Check that only public functions and main are included
        function_names = [f.name for f in filtered_model.functions]
        self.assertIn("public_function", function_names)
        self.assertIn("main", function_names)
        self.assertNotIn("private_function", function_names)
        self.assertNotIn("internal_helper", function_names)

    def test_element_filters_enums(self):
        """Test element filtering for enums"""
        config = Config()
        config.element_filters = {
            "enums": {
                "include": [r"^[A-Z].*"],
                "exclude": [r".*[Ii]nternal.*"]
            }
        }
        config._compile_patterns()

        model = self.create_test_model()
        file_model = list(model.files.values())[0]

        # Apply filters
        filtered_model = config._apply_element_filters(file_model)

        # Check that only public enums are included
        self.assertIn("Status", filtered_model.enums)
        self.assertIn("UserType", filtered_model.enums)
        self.assertNotIn("internal_state", filtered_model.enums)

    def test_element_filters_globals(self):
        """Test element filtering for global variables"""
        config = Config()
        config.element_filters = {
            "globals": {
                "include": [r"^public_.*"],
                "exclude": [r".*[Ii]nternal.*"]
            }
        }
        config._compile_patterns()

        model = self.create_test_model()
        file_model = list(model.files.values())[0]

        # Apply filters
        filtered_model = config._apply_element_filters(file_model)

        # Check that only public globals are included
        global_names = [g.name for g in filtered_model.globals]
        self.assertIn("public_constant", global_names)
        self.assertNotIn("global_var", global_names)
        self.assertNotIn("internal_var", global_names)

    def test_element_filters_macros(self):
        """Test element filtering for macros"""
        config = Config()
        config.element_filters = {
            "macros": {
                "include": [r"^[A-Z].*"],
                "exclude": [r".*[Ii]nternal.*"]
            }
        }
        config._compile_patterns()

        model = self.create_test_model()
        file_model = list(model.files.values())[0]

        # Apply filters
        filtered_model = config._apply_element_filters(file_model)

        # Check that only public macros are included
        self.assertIn("MAX_SIZE", filtered_model.macros)
        self.assertIn("PUBLIC_DEFINE", filtered_model.macros)
        self.assertNotIn("internal_macro", filtered_model.macros)

    def test_element_filters_typedefs(self):
        """Test element filtering for typedefs"""
        config = Config()
        config.element_filters = {
            "aliases": {
                "include": [r"^[A-Z].*"],
                "exclude": [r".*[Ii]nternal.*"]
            }
        }
        config._compile_patterns()

        model = self.create_test_model()
        file_model = list(model.files.values())[0]

        # Apply filters
        filtered_model = config._apply_element_filters(file_model)

        # Check that only public typedefs are included
        self.assertIn("UserPtr", filtered_model.aliases)
        self.assertIn("PublicType", filtered_model.aliases)
        self.assertNotIn("internal_type", filtered_model.aliases)

    def test_multiple_element_filters(self):
        """Test applying multiple element filters simultaneously"""
        config = Config()
        config.element_filters = {
            "structs": {
                "include": [r"^[A-Z].*"],
                "exclude": [r".*[Ii]nternal.*"]
            },
            "functions": {
                "include": [r"^public_.*"],
                "exclude": [r".*private.*"]
            },
            "enums": {
                "include": [r"^[A-Z].*"],
                "exclude": [r".*[Ii]nternal.*"]
            }
        }
        config._compile_patterns()

        model = self.create_test_model()
        file_model = list(model.files.values())[0]

        # Apply filters
        filtered_model = config._apply_element_filters(file_model)

        # Check structs
        self.assertIn("PublicStruct", filtered_model.structs)
        self.assertIn("UserData", filtered_model.structs)
        self.assertNotIn("InternalStruct", filtered_model.structs)
        self.assertNotIn("temp_data", filtered_model.structs)

        # Check functions
        function_names = [f.name for f in filtered_model.functions]
        self.assertIn("public_function", function_names)
        self.assertNotIn("private_function", function_names)
        self.assertNotIn("internal_helper", function_names)

        # Check enums
        self.assertIn("Status", filtered_model.enums)
        self.assertIn("UserType", filtered_model.enums)
        self.assertNotIn("internal_state", filtered_model.enums)

    def test_config_loading_with_filters(self):
        """Test loading configuration with filters from JSON"""
        config_data = {
            "project_name": "TestProject",
            "source_folders": ["./src"],
            "file_filters": {
                "include": [r".*\.c$", r".*\.h$"],
                "exclude": [r".*test.*"]
            },
            "element_filters": {
                "structs": {
                    "include": [r"^[A-Z].*"],
                    "exclude": [r".*[Ii]nternal.*"]
                }
            }
        }

        config = Config()
        for key, value in config_data.items():
            setattr(config, key, value)
        config._compile_patterns()

        # Verify configuration was loaded correctly
        self.assertEqual(config.project_name, "TestProject")
        self.assertEqual(config.source_folders, ["./src"])
        self.assertEqual(config.file_filters["include"], [r".*\.c$", r".*\.h$"])
        self.assertEqual(config.file_filters["exclude"], [r".*test.*"])
        self.assertIn("structs", config.element_filters)

    def test_invalid_regex_patterns(self):
        """Test handling of invalid regex patterns in filters"""
        config = Config()
        config.file_filters = {
            "include": [r"valid_pattern", r"[invalid_regex"],
            "exclude": [r"another_valid", r"[invalid_exclude"]
        }
        config.element_filters = {
            "structs": {
                "include": [r"^[A-Z].*", r"[invalid_struct"],
                "exclude": [r".*[Ii]nternal.*"]
            }
        }
        config._compile_patterns()

        # Configuration should still be created, but invalid patterns should be skipped
        self.assertIsInstance(config, Config)
        self.assertEqual(len(config.file_include_patterns), 1)  # Only valid pattern
        self.assertEqual(len(config.file_exclude_patterns), 1)  # Only valid pattern

    def test_empty_filters(self):
        """Test behavior with empty filter configurations"""
        config = Config()
        config.file_filters = {}
        config.element_filters = {}
        config._compile_patterns()

        # Should include all files when no file filters are specified
        self.assertTrue(config._should_include_file("any_file.c"))
        self.assertTrue(config._should_include_file("test.h"))

        # Should not have any compiled patterns
        self.assertEqual(len(config.file_include_patterns), 0)
        self.assertEqual(len(config.file_exclude_patterns), 0)

    def test_filter_performance(self):
        """Test that filtering doesn't significantly impact performance"""
        import time

        # Create a large model
        model = self.create_test_model()
        file_model = list(model.files.values())[0]

        # Create configuration with multiple filters
        config = Config()
        config.file_filters = {
            "include": [r".*\.c$"],
            "exclude": [r".*test.*"]
        }
        config.element_filters = {
            "structs": {
                "include": [r"^[A-Z].*"],
                "exclude": [r".*internal.*"]
            },
            "functions": {
                "include": [r"^public_.*"],
                "exclude": [r".*private.*"]
            },
            "enums": {
                "include": [r"^[A-Z].*"],
                "exclude": [r".*internal.*"]
            }
        }
        config._compile_patterns()

        # Measure filtering time
        start_time = time.time()
        for _ in range(100):  # Apply filters multiple times
            filtered_model = config._apply_element_filters(file_model)
        end_time = time.time()

        # Verify performance is reasonable (should complete quickly)
        self.assertLess(end_time - start_time, 1.0)

    def test_config_equality(self):
        """Test configuration equality comparison"""
        config1 = Config()
        config1.project_name = "Test"
        config1.file_filters = {"include": [r".*\.c$"]}
        config1.element_filters = {"structs": {"include": [r"^[A-Z].*"]}}

        config2 = Config()
        config2.project_name = "Test"
        config2.file_filters = {"include": [r".*\.c$"]}
        config2.element_filters = {"structs": {"include": [r"^[A-Z].*"]}}

        config3 = Config()
        config3.project_name = "Different"
        config3.file_filters = {"include": [r".*\.c$"]}
        config3.element_filters = {"structs": {"include": [r"^[A-Z].*"]}}

        self.assertEqual(config1, config2)
        self.assertNotEqual(config1, config3)

    def test_config_has_filters(self):
        """Test the has_filters method"""
        # Config with no filters
        config1 = Config()
        self.assertFalse(config1.has_filters())

        # Config with file filters only
        config2 = Config()
        config2.file_filters = {"include": [r".*\.c$"]}
        self.assertTrue(config2.has_filters())

        # Config with element filters only
        config3 = Config()
        config3.element_filters = {"structs": {"include": [r"^[A-Z].*"]}}
        self.assertTrue(config3.has_filters())

        # Config with both filters
        config4 = Config()
        config4.file_filters = {"include": [r".*\.c$"]}
        config4.element_filters = {"structs": {"include": [r"^[A-Z].*"]}}
        self.assertTrue(config4.has_filters())

        # Config with empty filter dictionaries
        config5 = Config()
        config5.file_filters = {}
        config5.element_filters = {}
        self.assertFalse(config5.has_filters())


if __name__ == "__main__":
    unittest.main()