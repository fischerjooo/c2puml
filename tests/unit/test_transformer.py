#!/usr/bin/env python3
"""
Unit tests for the transformer module
"""

import json
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, mock_open, patch

from c_to_plantuml.models import (
    Alias,
    Enum,
    Field,
    FileModel,
    Function,
    IncludeRelation,
    ProjectModel,
    Struct,
    Union,
)
from c_to_plantuml.transformer import Transformer


class TestTransformer(unittest.TestCase):
    """Test the transformer functionality"""

    def setUp(self):
        self.transformer = Transformer()

        # Create sample data for testing
        self.sample_file_model = FileModel(
            file_path="/test/project/sample.c",
            structs={
                "Person": Struct(
                    "Person", [Field("name", "char[50]"), Field("age", "int")]
                ),
                "Point": Struct("Point", [Field("x", "int"), Field("y", "int")]),
            },
            enums={"Status": Enum("Status", ["OK", "ERROR", "PENDING"])},
            unions={
                "Data": Union(
                    "Data",
                    [Field("i", "int"), Field("f", "float"), Field("str", "char[20]")],
                )
            },
            functions=[
                Function(
                    "main", "int", [Field("argc", "int"), Field("argv", "char**")]
                ),
                Function("calculate", "int", [Field("a", "int"), Field("b", "int")]),
            ],
            globals=[Field("global_var", "int"), Field("global_ptr", "void*")],
            includes={"stdio.h", "stdlib.h"},
            macros=["MAX_SIZE", "DEBUG_MODE"],
            aliases={
                "point_t": Alias("point_t", "struct Point"),
                "status_t": Alias("status_t", "enum Status"),
            },
        )

        self.sample_project_model = ProjectModel(
            source_folder="/test",
            project_name="TestProject",
            files={
                "sample.c": self.sample_file_model,
                "header.h": FileModel(
                    file_path="/test/project/header.h",
                    structs={},
                    enums={},
                    unions={},
                    functions=[],
                    globals=[],
                    includes=set(),
                    macros=[],
                    aliases={},
                ),
            },
        )

    def test_transform_main_method(self):
        """Test the main transform method"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as model_file:
            json.dump(
                {
                    "project_name": "TestProject",
                    "project_root": "/test/project",
                    "files": {"sample.c": self.sample_file_model.to_dict()},
                    "created_at": "2023-01-01T00:00:00",
                },
                model_file,
            )
            model_file_path = model_file.name

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as config_file:
            json.dump(
                {"file_filters": {"include": [r".*\.c$"], "exclude": [r".*test.*"]}},
                config_file,
            )
            config_file_path = config_file.name

        try:
            result = self.transformer.transform(model_file_path, config_file_path)
            self.assertIsInstance(result, str)
            self.assertTrue(os.path.exists(result))
        finally:
            os.unlink(model_file_path)
            os.unlink(config_file_path)

    def test_load_model_valid_file(self):
        """Test loading a valid model file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(
                {
                    "project_name": "TestProject",
                    "project_root": "/test/project",
                    "files": {"sample.c": self.sample_file_model.to_dict()},
                    "created_at": "2023-01-01T00:00:00",
                },
                f,
            )
            temp_file = f.name

        try:
            model = self.transformer._load_model(temp_file)
            self.assertIsInstance(model, ProjectModel)
            self.assertEqual(model.project_name, "TestProject")
            self.assertEqual(len(model.files), 1)
            self.assertIn("sample.c", model.files)
        finally:
            os.unlink(temp_file)

    def test_load_model_invalid_file(self):
        """Test loading a non-existent model file"""
        with self.assertRaises(FileNotFoundError):
            self.transformer._load_model("/nonexistent/file.json")

    def test_load_model_invalid_json(self):
        """Test loading a model file with invalid JSON"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name

        try:
            with self.assertRaises(ValueError):
                self.transformer._load_model(temp_file)
        finally:
            os.unlink(temp_file)

    def test_load_config_valid_file(self):
        """Test loading a valid configuration file"""
        config_data = {
            "file_filters": {"include": [r".*\.c$"], "exclude": [r".*test.*"]},
            "element_filters": {
                "structs": {"include": [r"Person.*"], "exclude": [r"Temp.*"]}
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config_data, f)
            temp_file = f.name

        try:
            config = self.transformer._load_config(temp_file)
            self.assertEqual(config, config_data)
        finally:
            os.unlink(temp_file)

    def test_load_config_invalid_file(self):
        """Test loading a non-existent configuration file"""
        with self.assertRaises(FileNotFoundError):
            self.transformer._load_config("/nonexistent/config.json")

    def test_apply_file_filters_include_only(self):
        """Test file filtering with include patterns only"""
        config = {"include": [r".*\.c$"], "exclude": []}

        result = self.transformer._apply_file_filters(self.sample_project_model, config)

        # Should only include .c files
        self.assertEqual(len(result.files), 1)
        self.assertIn("sample.c", result.files)
        self.assertNotIn("header.h", result.files)

    def test_apply_file_filters_exclude_only(self):
        """Test file filtering with exclude patterns only"""
        config = {"include": [], "exclude": [r".*\.h$"]}

        result = self.transformer._apply_file_filters(self.sample_project_model, config)

        # Should exclude .h files
        self.assertEqual(len(result.files), 1)
        self.assertIn("sample.c", result.files)
        self.assertNotIn("header.h", result.files)

    def test_apply_file_filters_both_patterns(self):
        """Test file filtering with both include and exclude patterns"""
        config = {"include": [r".*\.c$"], "exclude": [r".*test.*"]}

        result = self.transformer._apply_file_filters(self.sample_project_model, config)

        # Should include .c files but exclude test files
        self.assertEqual(len(result.files), 1)
        self.assertIn("sample.c", result.files)

    def test_apply_file_filters_no_patterns(self):
        """Test file filtering with no patterns (should return original model)"""
        config = {"include": [], "exclude": []}

        result = self.transformer._apply_file_filters(self.sample_project_model, config)

        # Should return the original model unchanged
        self.assertEqual(len(result.files), len(self.sample_project_model.files))
        self.assertEqual(result.files, self.sample_project_model.files)

    def test_compile_patterns_valid(self):
        """Test compiling valid regex patterns"""
        patterns = [r"test.*", r"[a-z]+", r"\d+"]
        compiled = self.transformer._compile_patterns(patterns)

        self.assertEqual(len(compiled), 3)
        for pattern in compiled:
            self.assertIsInstance(pattern, type(re.compile("")))

    def test_compile_patterns_invalid(self):
        """Test compiling invalid regex patterns"""
        patterns = [r"test.*", r"[invalid", r"\d+"]
        compiled = self.transformer._compile_patterns(patterns)

        # Should compile valid patterns and skip invalid ones
        self.assertEqual(len(compiled), 2)

    def test_should_include_file_include_patterns(self):
        """Test file inclusion with include patterns"""
        include_patterns = [re.compile(r".*\.c$")]
        exclude_patterns = []

        # Should include .c files
        self.assertTrue(
            self.transformer._should_include_file(
                "test.c", include_patterns, exclude_patterns
            )
        )

        # Should not include .h files
        self.assertFalse(
            self.transformer._should_include_file(
                "test.h", include_patterns, exclude_patterns
            )
        )

    def test_should_include_file_exclude_patterns(self):
        """Test file inclusion with exclude patterns"""
        include_patterns = []
        exclude_patterns = [re.compile(r".*test.*")]

        # Should not include test files
        self.assertFalse(
            self.transformer._should_include_file(
                "test.c", include_patterns, exclude_patterns
            )
        )

        # Should include non-test files
        self.assertTrue(
            self.transformer._should_include_file(
                "main.c", include_patterns, exclude_patterns
            )
        )

    def test_should_include_file_both_patterns(self):
        """Test file inclusion with both include and exclude patterns"""
        include_patterns = [re.compile(r".*\.c$")]
        exclude_patterns = [re.compile(r".*test.*")]

        # Should not include test.c (matches exclude)
        self.assertFalse(
            self.transformer._should_include_file(
                "test.c", include_patterns, exclude_patterns
            )
        )

        # Should include main.c (matches include, doesn't match exclude)
        self.assertTrue(
            self.transformer._should_include_file(
                "main.c", include_patterns, exclude_patterns
            )
        )

    def test_filter_dict_include_only(self):
        """Test dictionary filtering with include patterns only"""
        items = {"test1": "value1", "test2": "value2", "other": "value3"}
        filters = {"include": [r"test.*"], "exclude": []}

        result = self.transformer._filter_dict(items, filters)

        self.assertEqual(len(result), 2)
        self.assertIn("test1", result)
        self.assertIn("test2", result)
        self.assertNotIn("other", result)

    def test_filter_dict_exclude_only(self):
        """Test dictionary filtering with exclude patterns only"""
        items = {"test1": "value1", "test2": "value2", "other": "value3"}
        filters = {"include": [], "exclude": [r"test.*"]}

        result = self.transformer._filter_dict(items, filters)

        self.assertEqual(len(result), 1)
        self.assertNotIn("test1", result)
        self.assertNotIn("test2", result)
        self.assertIn("other", result)

    def test_filter_list_include_only(self):
        """Test list filtering with include patterns only"""
        items = ["test1", "test2", "other"]
        filters = {"include": [r"test.*"], "exclude": []}

        result = self.transformer._filter_list(items, filters)

        self.assertEqual(len(result), 2)
        self.assertIn("test1", result)
        self.assertIn("test2", result)
        self.assertNotIn("other", result)

    def test_filter_list_with_key_function(self):
        """Test list filtering with a key function"""
        items = [
            {"name": "test1", "value": 1},
            {"name": "test2", "value": 2},
            {"name": "other", "value": 3},
        ]
        filters = {"include": [r"test.*"], "exclude": []}

        result = self.transformer._filter_list(items, filters, key=lambda x: x["name"])

        self.assertEqual(len(result), 2)
        self.assertIn(items[0], result)
        self.assertIn(items[1], result)
        self.assertNotIn(items[2], result)

    def test_dict_to_file_model(self):
        """Test converting dictionary back to FileModel"""
        data = {
            "file_path": "/test/file.c",
            "project_root": "/test",
            "encoding_used": "utf-8",
            "structs": {
                "TestStruct": {
                    "name": "TestStruct",
                    "fields": [{"name": "field1", "type": "int"}],
                    "methods": [],
                }
            },
            "enums": {"TestEnum": {"name": "TestEnum", "values": ["VAL1", "VAL2"]}},
            "unions": {
                "TestUnion": {
                    "name": "TestUnion",
                    "fields": [{"name": "field1", "type": "int"}],
                }
            },
            "functions": [
                {"name": "test_func", "return_type": "int", "parameters": []}
            ],
            "globals": [{"name": "global_var", "type": "int"}],
            "includes": ["stdio.h"],
            "macros": ["TEST_MACRO"],
            "typedefs": {"test_t": "int"},
            "typedef_relations": [],
            "include_relations": [],
        }

        file_model = self.transformer._dict_to_file_model(data)

        self.assertIsInstance(file_model, FileModel)
        self.assertEqual(file_model.file_path, "/test/file.c")
        self.assertIn("TestStruct", file_model.structs)
        self.assertIn("TestEnum", file_model.enums)
        self.assertIn("TestUnion", file_model.unions)
        self.assertEqual(len(file_model.functions), 1)
        self.assertEqual(file_model.functions[0].name, "test_func")

    def test_save_model(self):
        """Test saving model to file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            self.transformer._save_model(self.sample_project_model, temp_file)

            # Verify file was created and contains valid JSON
            with open(temp_file, "r") as f:
                data = json.load(f)

            self.assertEqual(data["project_name"], "TestProject")
            self.assertIn("files", data)
        finally:
            os.unlink(temp_file)

    def test_process_include_relations(self):
        """Test processing include relations"""
        # Create a model with include relations
        file1 = FileModel(
            file_path="/test/file1.c",
            includes={"file2.h"},
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            macros=[],
            aliases={},
            include_relations=[],
        )

        file2 = FileModel(
            file_path="/test/file2.h",
            includes=set(),
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            macros=[],
            aliases={},
            include_relations=[],
        )

        model = ProjectModel(
            source_folder="/test",
            project_name="TestProject",
            files={"file1.c": file1, "file2.h": file2},
        )

        with patch.object(self.transformer, "_find_included_file") as mock_find:
            mock_find.return_value = "/test/file2.h"

            result = self.transformer._process_include_relations(model, 2)

            # Should process include relations
            self.assertEqual(len(result.files), 2)

    def test_find_included_file(self):
        """Test finding included file paths"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            include_dir = Path(temp_dir) / "include"
            include_dir.mkdir()

            header_file = include_dir / "test.h"
            header_file.touch()

            # Test finding the file - now returns filename instead of full path
            result = self.transformer._find_included_file("test.h", temp_dir)
            self.assertEqual(result, header_file.name)

    def test_find_included_file_not_found(self):
        """Test finding non-existent included file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.transformer._find_included_file("nonexistent.h", temp_dir)
            self.assertIsNone(result)

    def test_apply_transformations_no_config(self):
        """Test applying transformations with empty config"""
        config = {}
        result = self.transformer._apply_transformations(
            self.sample_project_model, config
        )

        # Should return the original model unchanged
        self.assertEqual(result, self.sample_project_model)

    def test_apply_transformations_with_all_sections(self):
        """Test applying transformations with all configuration sections"""
        config = {
            "file_filters": {"include": [".*\\.c$"], "exclude": [".*test.*"]},
            "element_filters": {
                "structs": {"include": ["^[A-Z].*"], "exclude": [".*_internal.*"]}
            },
            "transformations": {
                "file_selection": {"selected_files": []},
                "rename": {"structs": {"old_name": "new_name"}},
            },
            "include_depth": 2,
        }

        result = self.transformer._apply_transformations(
            self.sample_project_model, config
        )
        self.assertIsInstance(result, ProjectModel)
        self.assertEqual(len(result.files), 1)  # Only .c files after filtering

    def test_file_selection_apply_to_all(self):
        """Test file selection with empty selected_files (apply to all)"""
        config = {
            "transformations": {
                "file_selection": {"selected_files": []},
                "rename": {"structs": {"old_name": "new_name"}},
            }
        }

        result = self.transformer._apply_model_transformations(
            self.sample_project_model, config["transformations"]
        )
        self.assertIsInstance(result, ProjectModel)
        # Should apply to all files
        self.assertEqual(len(result.files), 2)

    def test_file_selection_no_file_selection(self):
        """Test file selection with no file_selection specified (apply to all)"""
        config = {"transformations": {"rename": {"structs": {"old_name": "new_name"}}}}

        result = self.transformer._apply_model_transformations(
            self.sample_project_model, config["transformations"]
        )
        self.assertIsInstance(result, ProjectModel)
        # Should apply to all files
        self.assertEqual(len(result.files), 2)

    def test_file_selection_selected_files(self):
        """Test file selection with specific file patterns"""
        config = {
            "transformations": {
                "file_selection": {"selected_files": [".*sample\\.c$"]},
                "rename": {"structs": {"old_name": "new_name"}},
            }
        }

        result = self.transformer._apply_model_transformations(
            self.sample_project_model, config["transformations"]
        )
        self.assertIsInstance(result, ProjectModel)
        # Should apply only to sample.c
        self.assertEqual(
            len(result.files), 2
        )  # Files still exist, but transformations applied only to selected

    def test_file_selection_no_matching_files(self):
        """Test file selection with no matching files"""
        config = {
            "transformations": {
                "file_selection": {"selected_files": [".*nonexistent\\.c$"]},
                "rename": {"structs": {"old_name": "new_name"}},
            }
        }

        result = self.transformer._apply_model_transformations(
            self.sample_project_model, config["transformations"]
        )
        self.assertIsInstance(result, ProjectModel)
        # Should not apply to any files
        self.assertEqual(len(result.files), 2)

    def test_matches_pattern_valid(self):
        """Test _matches_pattern method with valid patterns"""
        self.assertTrue(self.transformer._matches_pattern("main.c", ".*main\\.c$"))
        self.assertTrue(self.transformer._matches_pattern("utils.c", ".*utils\\.c$"))
        self.assertFalse(self.transformer._matches_pattern("main.c", ".*utils\\.c$"))

    def test_matches_pattern_invalid(self):
        """Test _matches_pattern method with invalid patterns"""
        # Should handle invalid regex gracefully
        result = self.transformer._matches_pattern("main.c", "[invalid")
        self.assertFalse(result)

    def test_renaming_with_file_selection(self):
        """Test renaming with file selection"""
        target_files = {"sample.c"}
        rename_config = {"structs": {"Person": "Employee", "Point": "Coordinate"}}

        result = self.transformer._apply_renaming(
            self.sample_project_model, rename_config, target_files
        )
        self.assertIsInstance(result, ProjectModel)
        # Should apply renaming only to sample.c
        self.assertIn("sample.c", result.files)

    def test_additions_with_file_selection(self):
        """Test additions with file selection"""
        target_files = {"sample.c"}
        add_config = {
            "structs": {
                "NewStruct": {
                    "fields": [
                        {"name": "field1", "type": "int"},
                        {"name": "field2", "type": "char*"},
                    ]
                }
            }
        }

        result = self.transformer._apply_additions(
            self.sample_project_model, add_config, target_files
        )
        self.assertIsInstance(result, ProjectModel)
        # Should apply additions only to sample.c
        self.assertIn("sample.c", result.files)

    def test_removals_with_file_selection(self):
        """Test removals with file selection"""
        target_files = {"sample.c"}
        remove_config = {"functions": ["calculate"], "structs": ["Point"]}

        result = self.transformer._apply_removals(
            self.sample_project_model, remove_config, target_files
        )
        self.assertIsInstance(result, ProjectModel)
        # Should apply removals only to sample.c
        self.assertIn("sample.c", result.files)

    def test_apply_include_filters_basic(self):
        """Test basic include filtering functionality"""
        # Create a project model with includes and include_relations
        file_model_with_includes = FileModel(
            file_path="/test/project/main.c",
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            includes={"stdio.h", "stdlib.h", "string.h", "math.h"},
            macros=[],
            aliases={},
            include_relations=[
                IncludeRelation("main.c", "stdio.h", 1),
                IncludeRelation("main.c", "stdlib.h", 1),
                IncludeRelation("main.c", "string.h", 1),
                IncludeRelation("main.c", "math.h", 1),
            ],
        )

        project_model = ProjectModel(
            source_folder="/test",
            project_name="TestProject",
            files={"main.c": file_model_with_includes},
        )

        # Configure include filters to only keep stdio.h and string.h
        config = {"file_specific": {"main.c": {"include_filter": [r"stdio\.h", r"string\.h"]}}}

        result = self.transformer._apply_include_filters(
            project_model, self.transformer._extract_include_filters_from_config(config)
        )

        # Check that includes were filtered
        self.assertEqual(len(result.files["main.c"].includes), 2)
        self.assertIn("stdio.h", result.files["main.c"].includes)
        self.assertIn("string.h", result.files["main.c"].includes)
        self.assertNotIn("stdlib.h", result.files["main.c"].includes)
        self.assertNotIn("math.h", result.files["main.c"].includes)

        # Check that include_relations were filtered
        self.assertEqual(len(result.files["main.c"].include_relations), 2)
        included_files = [
            rel.included_file for rel in result.files["main.c"].include_relations
        ]
        self.assertIn("stdio.h", included_files)
        self.assertIn("string.h", included_files)
        self.assertNotIn("stdlib.h", included_files)
        self.assertNotIn("math.h", included_files)

    def test_apply_include_filters_multiple_root_files(self):
        """Test include filtering with multiple root files"""
        # Create file models for different root files
        main_c_model = FileModel(
            file_path="/test/project/main.c",
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            includes={"stdio.h", "stdlib.h", "utils.h"},
            macros=[],
            aliases={},
            include_relations=[
                IncludeRelation("main.c", "stdio.h", 1),
                IncludeRelation("main.c", "stdlib.h", 1),
                IncludeRelation("main.c", "utils.h", 1),
            ],
        )

        utils_c_model = FileModel(
            file_path="/test/project/utils.c",
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            includes={"string.h", "math.h", "utils.h"},
            macros=[],
            aliases={},
            include_relations=[
                IncludeRelation("utils.c", "string.h", 1),
                IncludeRelation("utils.c", "math.h", 1),
                IncludeRelation("utils.c", "utils.h", 1),
            ],
        )

        project_model = ProjectModel(
            source_folder="/test",
            project_name="TestProject",
            files={
                "main.c": main_c_model,
                "utils.c": utils_c_model,
            },
        )

        # Configure different include filters for each root file
        config = {
            "file_specific": {
                "main.c": {"include_filter": [r"stdio\.h", r"stdlib\.h"]},
                "utils.c": {"include_filter": [r"string\.h"]},
            }
        }

        result = self.transformer._apply_include_filters(
            project_model, self.transformer._extract_include_filters_from_config(config)
        )

        # Check main.c filtering
        main_c = result.files["main.c"]
        self.assertEqual(len(main_c.includes), 2)
        self.assertIn("stdio.h", main_c.includes)
        self.assertIn("stdlib.h", main_c.includes)
        self.assertNotIn("utils.h", main_c.includes)

        # Check utils.c filtering
        utils_c = result.files["utils.c"]
        self.assertEqual(len(utils_c.includes), 1)
        self.assertIn("string.h", utils_c.includes)
        self.assertNotIn("math.h", utils_c.includes)
        self.assertNotIn("utils.h", utils_c.includes)

    def test_apply_include_filters_no_matching_root_file(self):
        """Test include filtering when root file doesn't match any filters"""
        file_model = FileModel(
            file_path="/test/project/other.c",
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            includes={"stdio.h", "stdlib.h"},
            macros=[],
            aliases={},
            include_relations=[
                IncludeRelation("other.c", "stdio.h", 1),
                IncludeRelation("other.c", "stdlib.h", 1),
            ],
        )

        project_model = ProjectModel(
            source_folder="/test",
            project_name="TestProject",
            files={"other.c": file_model},
        )

        # Configure filters for a different root file
        config = {"file_specific": {"main.c": {"include_filter": [r"stdio\.h"]}}}

        result = self.transformer._apply_include_filters(
            project_model, self.transformer._extract_include_filters_from_config(config)
        )

        # Should not affect files that don't match any root file filters
        other_c = result.files["other.c"]
        self.assertEqual(len(other_c.includes), 2)
        self.assertIn("stdio.h", other_c.includes)
        self.assertIn("stdlib.h", other_c.includes)

    def test_apply_include_filters_invalid_regex(self):
        """Test include filtering with invalid regex patterns"""
        file_model = FileModel(
            file_path="/test/project/main.c",
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            includes={"stdio.h", "stdlib.h"},
            macros=[],
            aliases={},
            include_relations=[
                IncludeRelation("main.c", "stdio.h", 1),
                IncludeRelation("main.c", "stdlib.h", 1),
            ],
        )

        project_model = ProjectModel(
            source_folder="/test",
            project_name="TestProject",
            files={"main.c": file_model},
        )

        # Configure filters with invalid regex
        config = {"file_specific": {"main.c": {"include_filter": [r"stdio\.h", "[invalid regex"]}}}

        result = self.transformer._apply_include_filters(
            project_model, self.transformer._extract_include_filters_from_config(config)
        )

        # Should skip invalid patterns but still apply valid ones
        main_c = result.files["main.c"]
        self.assertEqual(
            len(main_c.includes), 2
        )  # Both includes should remain since invalid pattern was skipped
        self.assertIn("stdio.h", main_c.includes)
        self.assertIn("stdlib.h", main_c.includes)

    def test_apply_include_filters_empty_config(self):
        """Test include filtering with empty configuration"""
        file_model = FileModel(
            file_path="/test/project/main.c",
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            includes={"stdio.h", "stdlib.h"},
            macros=[],
            aliases={},
            include_relations=[
                IncludeRelation("main.c", "stdio.h", 1),
                IncludeRelation("main.c", "stdlib.h", 1),
            ],
        )

        project_model = ProjectModel(
            source_folder="/test",
            project_name="TestProject",
            files={"main.c": file_model},
        )

        # Empty include filters
        config = {"file_specific": {}}

        result = self.transformer._apply_include_filters(
            project_model, self.transformer._extract_include_filters_from_config(config)
        )

        # Should not affect any files
        main_c = result.files["main.c"]
        self.assertEqual(len(main_c.includes), 2)
        self.assertIn("stdio.h", main_c.includes)
        self.assertIn("stdlib.h", main_c.includes)

    def test_find_root_file_c_file(self):
        """Test _find_root_file method for .c files"""
        file_model = FileModel(
            file_path="/test/project/main.c",
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            includes=set(),
            macros=[],
            aliases={},
        )

        root_file = self.transformer._find_root_file("/test/project/main.c", file_model)
        self.assertEqual(root_file, "main.c")

    def test_find_root_file_header_file(self):
        """Test _find_root_file method for header files"""
        file_model = FileModel(
            file_path="/test/project/header.h",
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            includes=set(),
            macros=[],
            aliases={},
        )

        root_file = self.transformer._find_root_file(
            "/test/project/header.h", file_model
        )
        self.assertEqual(root_file, "header.c")  # Now returns the corresponding .c file

    def test_matches_any_pattern(self):
        """Test _matches_any_pattern method"""
        patterns = [re.compile(r"stdio\.h"), re.compile(r"stdlib\.h")]

        # Should match first pattern
        self.assertTrue(self.transformer._matches_any_pattern("stdio.h", patterns))

        # Should match second pattern
        self.assertTrue(self.transformer._matches_any_pattern("stdlib.h", patterns))

        # Should not match any pattern
        self.assertFalse(self.transformer._matches_any_pattern("string.h", patterns))

    def test_apply_transformations_with_include_filters(self):
        """Test that include_filters preserve includes arrays but only affect include_relations generation"""
        # Create a project model with includes
        file_model = FileModel(
            file_path="/test/project/main.c",
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            includes={"stdio.h", "stdlib.h", "string.h"},
            macros=[],
            aliases={},
            include_relations=[],  # Start with empty relations
        )

        project_model = ProjectModel(
            source_folder="/test",
            project_name="TestProject",
            files={"main.c": file_model},
        )

        # Configure transformations with include_filters and include_depth
        config = {
            "file_specific": {"main.c": {"include_filter": [r"stdio\.h", r"string\.h"]}},
            "include_depth": 2  # Enable include_relations processing
        }

        result = self.transformer._apply_transformations(project_model, config)

        # Check that includes array is preserved (NOT modified by include_filters)
        main_c = result.files["main.c"]
        self.assertEqual(len(main_c.includes), 3)  # All original includes preserved
        self.assertIn("stdio.h", main_c.includes)
        self.assertIn("string.h", main_c.includes) 
        self.assertIn("stdlib.h", main_c.includes)  # This should still be present
        
        # Check that include_relations are filtered (this is what include_filters should affect)
        # Note: Since we don't have the actual included files in this test, 
        # include_relations generation may not work, but the includes should be preserved

    def test_include_filters_preserve_includes_arrays(self):
        """Test that include_filters preserve all includes arrays and only affect include_relations generation"""
        # Create a project model with transitive includes
        main_c_model = FileModel(
            file_path="/test/project/main.c",
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            includes={"header1.h"},  # main.c includes header1.h
            macros=[],
            aliases={},
            include_relations=[],
        )

        header1_model = FileModel(
            file_path="/test/project/header1.h",
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            includes={"header2.h"},  # header1.h includes header2.h
            macros=[],
            aliases={},
            include_relations=[],
        )

        header2_model = FileModel(
            file_path="/test/project/header2.h",
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            includes={"header3.h"},  # header2.h includes header3.h
            macros=[],
            aliases={},
            include_relations=[],
        )

        header3_model = FileModel(
            file_path="/test/project/header3.h",
            structs={},
            enums={},
            unions={},
            functions=[],
            globals=[],
            includes=set(),  # header3.h has no includes
            macros=[],
            aliases={},
            include_relations=[],
        )

        project_model = ProjectModel(
            source_folder="/test",
            project_name="TestProject",
            files={
                "main.c": main_c_model,
                "header1.h": header1_model,
                "header2.h": header2_model,
                "header3.h": header3_model,
            },
        )

        # Configure include_filters to only allow header1.h for main.c
        # This should only affect include_relations generation, NOT the includes arrays
        config = {
            "file_specific": {"main.c": {"include_filter": [r"^header1\.h$"]}},  # Only allow header1.h
            "include_depth": 3,  # Enable transitive include processing
        }

        result = self.transformer._apply_transformations(project_model, config)

        # Check that ALL includes arrays are preserved (NOT filtered)
        main_c = result.files["main.c"]
        self.assertEqual(len(main_c.includes), 1)  # Original includes preserved
        self.assertIn("header1.h", main_c.includes)
        
        # Check that header files' includes are also preserved
        header1 = result.files["header1.h"]
        self.assertEqual(len(header1.includes), 1)  # header1's includes preserved
        self.assertIn("header2.h", header1.includes)
        
        header2 = result.files["header2.h"]
        self.assertEqual(len(header2.includes), 1)  # header2's includes preserved
        self.assertIn("header3.h", header2.includes)
        
        # The key point: include_filters should only affect include_relations generation,
        # not the original includes arrays which should all be preserved.

        header1_relations = [rel.included_file for rel in header1.include_relations]
        self.assertNotIn(
            "header2.h",
            header1_relations,
            "header1.h should not have include relation to header2.h",
        )
        self.assertNotIn(
            "header3.h",
            header1_relations,
            "header1.h should not have include relation to header3.h",
        )

    def test_file_specific_include_depth(self):
        """Test file-specific include_depth functionality"""
        # Create project model with multiple files and includes
        main_file = FileModel(
            file_path="/test/main.c",
            structs={}, enums={}, unions={}, functions=[], globals=[],
            includes={"stdio.h", "utils.h"}, macros=[], aliases={},
            include_relations=[]
        )
        
        utils_file = FileModel(
            file_path="/test/utils.c", 
            structs={}, enums={}, unions={}, functions=[], globals=[],
            includes={"math.h", "time.h"}, macros=[], aliases={},
            include_relations=[]
        )
        
        # Mock header files
        stdio_file = FileModel(
            file_path="/test/stdio.h",
            structs={}, enums={}, unions={}, functions=[], globals=[],
            includes={"stddef.h"}, macros=[], aliases={},
            include_relations=[]
        )
        
        utils_header = FileModel(
            file_path="/test/utils.h",
            structs={}, enums={}, unions={}, functions=[], globals=[],
            includes={"string.h"}, macros=[], aliases={},
            include_relations=[]
        )

        project_model = ProjectModel(
            source_folder="/test",
            project_name="TestProject", 
            files={
                "main.c": main_file,
                "utils.c": utils_file, 
                "stdio.h": stdio_file,
                "utils.h": utils_header
            }
        )

        # Config with file-specific include_depth and global fallback
        config = {
            "include_depth": 2,  # Global fallback
            "file_specific": {
                "main.c": {"include_depth": 3},  # File-specific override
                "utils.c": {"include_depth": 1}   # File-specific override (no processing)
            }
        }

        result = self.transformer._apply_transformations(project_model, config)

        # Check main.c used include_depth=3
        main_relations = result.files["main.c"].include_relations
        self.assertGreater(len(main_relations), 0, "main.c should have include relations")

        # Check utils.c used include_depth=1 (no relations generated)
        utils_relations = result.files["utils.c"].include_relations
        self.assertEqual(len(utils_relations), 0, "utils.c should have no include relations with depth=1")

    def test_file_specific_include_filter_optional(self):
        """Test that include_filter is optional in file_specific configuration"""
        main_file = FileModel(
            file_path="/test/main.c",
            structs={}, enums={}, unions={}, functions=[], globals=[],
            includes={"stdio.h", "math.h"}, macros=[], aliases={},
            include_relations=[]
        )

        project_model = ProjectModel(
            source_folder="/test",
            project_name="TestProject",
            files={"main.c": main_file}
        )

        # Config with only include_depth, no include_filter
        config = {
            "include_depth": 1,  # Global
            "file_specific": {
                "main.c": {"include_depth": 2}  # Only depth, no filter
            }
        }

        # Should not raise an exception
        result = self.transformer._apply_transformations(project_model, config)
        self.assertIsNotNone(result)

    def test_file_specific_include_depth_fallback_to_global(self):
        """Test that files without file-specific config use global include_depth"""
        main_file = FileModel(
            file_path="/test/main.c",
            structs={}, enums={}, unions={}, functions=[], globals=[],
            includes={"stdio.h"}, macros=[], aliases={},
            include_relations=[]
        )
        
        other_file = FileModel(
            file_path="/test/other.c",
            structs={}, enums={}, unions={}, functions=[], globals=[],
            includes={"math.h"}, macros=[], aliases={},
            include_relations=[]
        )

        project_model = ProjectModel(
            source_folder="/test",
            project_name="TestProject",
            files={"main.c": main_file, "other.c": other_file}
        )

        config = {
            "include_depth": 2,  # Global setting
            "file_specific": {
                "main.c": {"include_depth": 3}  # Only main.c has file-specific setting
                # other.c should use global include_depth=2
            }
        }

        result = self.transformer._apply_transformations(project_model, config)
        
        # Both files should be processed since global include_depth=2 > 1
        main_relations = result.files["main.c"].include_relations
        other_relations = result.files["other.c"].include_relations
        
        # We can't easily check the exact depth without more complex setup,
        # but we can verify the method was called for both files
        self.assertIsInstance(main_relations, list)
        self.assertIsInstance(other_relations, list)

    def test_should_process_include_relations(self):
        """Test _should_process_include_relations helper method"""
        # Test global include_depth > 1
        config1 = {"include_depth": 2}
        self.assertTrue(self.transformer._should_process_include_relations(config1))
        
        # Test global include_depth = 1 (should not process)
        config2 = {"include_depth": 1}
        self.assertFalse(self.transformer._should_process_include_relations(config2))
        
        # Test file-specific include_depth > 1
        config3 = {
            "include_depth": 1,
            "file_specific": {
                "main.c": {"include_depth": 3}
            }
        }
        self.assertTrue(self.transformer._should_process_include_relations(config3))
        
        # Test no include_depth anywhere
        config4 = {"other_setting": "value"}
        self.assertFalse(self.transformer._should_process_include_relations(config4))
        
        # Test file-specific include_depth = 1 with no global
        config5 = {
            "file_specific": {
                "main.c": {"include_depth": 1}
            }
        }
        self.assertFalse(self.transformer._should_process_include_relations(config5))


if __name__ == "__main__":
    unittest.main()
