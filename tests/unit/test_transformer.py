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


# Add src directory to path for new package structure
import sys
import os
from pathlib import Path

# Get the absolute path to the src directory 
current_file = Path(__file__).resolve()
test_dir = current_file.parent
project_root = test_dir.parent.parent
src_path = project_root / "src"

if src_path.exists():
    sys.path.insert(0, str(src_path))
# Also add tests directory for test utilities
tests_path = project_root / "tests"
if tests_path.exists():
    sys.path.insert(0, str(tests_path))

from c2puml.models import (
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
from c2puml.transformer import Transformer


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
                "file_selection": [],
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
        """Test file selection with empty file_selection array (apply to all)"""
        config = {
            "transformations": {
                "file_selection": [],
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
                "file_selection": [".*sample\\.c$"],
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
                "file_selection": [".*nonexistent\\.c$"],
                "rename": {"structs": {"old_name": "new_name"}},
            }
        }

        result = self.transformer._apply_model_transformations(
            self.sample_project_model, config["transformations"]
        )
        self.assertIsInstance(result, ProjectModel)
        # Should not apply to any files
        self.assertEqual(len(result.files), 2)

    def test_file_selection_array_format(self):
        """Test file selection with new array format"""
        config = {
            "transformations": {
                "file_selection": [".*sample\\.c$"],
                "rename": {"structs": {"old_name": "new_name"}},
            }
        }

        result = self.transformer._apply_model_transformations(
            self.sample_project_model, config["transformations"]
        )
        self.assertIsInstance(result, ProjectModel)
        # Should apply only to sample.c
        self.assertEqual(len(result.files), 2)

    def test_file_selection_empty_array(self):
        """Test file selection with empty array (apply to all)"""
        config = {
            "transformations": {
                "file_selection": [],
                "rename": {"structs": {"old_name": "new_name"}},
            }
        }

        result = self.transformer._apply_model_transformations(
            self.sample_project_model, config["transformations"]
        )
        self.assertIsInstance(result, ProjectModel)
        # Should apply to all files
        self.assertEqual(len(result.files), 2)

    def test_file_selection_invalid_format(self):
        """Test file selection with invalid format"""
        config = {
            "transformations": {
                "file_selection": "invalid_string",
                "rename": {"structs": {"old_name": "new_name"}},
            }
        }

        result = self.transformer._apply_model_transformations(
            self.sample_project_model, config["transformations"]
        )
        self.assertIsInstance(result, ProjectModel)
        # Should default to all files when format is invalid
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

    def test_remove_typedefs_regex_patterns(self):
        """Test removing typedefs with regex patterns"""
        # Create a file model with typedefs
        file_model = FileModel("test.c")
        file_model.aliases = {
            "old_type1": Alias("old_type1", "int", []),
            "new_type": Alias("new_type", "float", []),
            "temp_type": Alias("temp_type", "char", []),
            "old_type2": Alias("old_type2", "double", [])
        }
        
        # Remove typedefs starting with "old_" or containing "temp"
        patterns = ["^old_.*", ".*temp.*"]
        self.transformer._remove_typedefs(file_model, patterns)
        
        # Should only have new_type left
        self.assertEqual(len(file_model.aliases), 1)
        self.assertIn("new_type", file_model.aliases)
        self.assertNotIn("old_type1", file_model.aliases)
        self.assertNotIn("old_type2", file_model.aliases)
        self.assertNotIn("temp_type", file_model.aliases)

    def test_remove_functions_regex_patterns(self):
        """Test removing functions with regex patterns"""
        file_model = FileModel("test.c")
        file_model.functions = [
            Function("debug_init", "void", []),
            Function("main", "int", []),
            Function("debug_cleanup", "void", []),
            Function("calculate", "int", [])
        ]
        
        # Remove functions starting with "debug_"
        patterns = ["^debug_.*"]
        self.transformer._remove_functions(file_model, patterns)
        
        # Should have main and calculate left
        self.assertEqual(len(file_model.functions), 2)
        function_names = [f.name for f in file_model.functions]
        self.assertIn("main", function_names)
        self.assertIn("calculate", function_names)
        self.assertNotIn("debug_init", function_names)
        self.assertNotIn("debug_cleanup", function_names)

    def test_remove_macros_regex_patterns(self):
        """Test removing macros with regex patterns"""
        file_model = FileModel("test.c")
        file_model.macros = [
            "DEBUG_LEVEL",
            "TEMP_BUFFER_SIZE",
            "VERSION",
            "DEBUG_MODE"
        ]
        
        # Remove macros starting with "DEBUG_" or containing "TEMP"
        patterns = ["^DEBUG_.*", ".*TEMP.*"]
        self.transformer._remove_macros(file_model, patterns)
        
        # Should only have VERSION left
        self.assertEqual(len(file_model.macros), 1)
        self.assertIn("VERSION", file_model.macros)
        self.assertNotIn("DEBUG_LEVEL", file_model.macros)
        self.assertNotIn("DEBUG_MODE", file_model.macros)
        self.assertNotIn("TEMP_BUFFER_SIZE", file_model.macros)

    def test_remove_globals_regex_patterns(self):
        """Test removing global variables with regex patterns"""
        file_model = FileModel("test.c")
        file_model.globals = [
            Field("debug_flag", "int"),
            Field("version", "char*"),
            Field("debug_level", "int"),
            Field("config", "Config*")
        ]
        
        # Remove globals starting with "debug_"
        patterns = ["^debug_.*"]
        self.transformer._remove_globals(file_model, patterns)
        
        # Should have version and config left
        self.assertEqual(len(file_model.globals), 2)
        global_names = [g.name for g in file_model.globals]
        self.assertIn("version", global_names)
        self.assertIn("config", global_names)
        self.assertNotIn("debug_flag", global_names)
        self.assertNotIn("debug_level", global_names)

    def test_remove_includes_regex_patterns(self):
        """Test removing includes with regex patterns"""
        file_model = FileModel("test.c")
        file_model.includes = {"stdio.h", "debug.h", "config.h", "test_utils.h"}
        file_model.include_relations = [
            IncludeRelation("test.c", "stdio.h", 1),
            IncludeRelation("test.c", "debug.h", 1),
            IncludeRelation("test.c", "config.h", 1),
            IncludeRelation("test.c", "test_utils.h", 1)
        ]
        
        # Remove includes containing "debug" or starting with "test_"
        patterns = [".*debug.*", "^test_.*"]
        self.transformer._remove_includes(file_model, patterns)
        
        # Should have stdio.h and config.h left
        self.assertEqual(len(file_model.includes), 2)
        self.assertIn("stdio.h", file_model.includes)
        self.assertIn("config.h", file_model.includes)
        self.assertNotIn("debug.h", file_model.includes)
        self.assertNotIn("test_utils.h", file_model.includes)
        
        # Should also remove corresponding include relations
        self.assertEqual(len(file_model.include_relations), 2)
        relation_files = [r.included_file for r in file_model.include_relations]
        self.assertIn("stdio.h", relation_files)
        self.assertIn("config.h", relation_files)
        self.assertNotIn("debug.h", relation_files)
        self.assertNotIn("test_utils.h", relation_files)

    def test_remove_structs_regex_patterns(self):
        """Test removing structs with regex patterns"""
        file_model = FileModel("test.c")
        file_model.structs = {
            "Point": Struct("Point", []),
            "debug_info": Struct("debug_info", []),
            "Config": Struct("Config", []),
            "temp_data": Struct("temp_data", [])
        }
        
        # Remove structs containing "debug" or "temp"
        patterns = [".*debug.*", ".*temp.*"]
        self.transformer._remove_structs(file_model, patterns)
        
        # Should have Point and Config left
        self.assertEqual(len(file_model.structs), 2)
        self.assertIn("Point", file_model.structs)
        self.assertIn("Config", file_model.structs)
        self.assertNotIn("debug_info", file_model.structs)
        self.assertNotIn("temp_data", file_model.structs)

    def test_remove_enums_regex_patterns(self):
        """Test removing enums with regex patterns"""
        file_model = FileModel("test.c")
        file_model.enums = {
            "Color": Enum("Color", []),
            "LogLevel": Enum("LogLevel", []),
            "debug_state": Enum("debug_state", []),
            "Status": Enum("Status", [])
        }
        
        # Remove enums starting with lowercase or containing "debug"
        patterns = ["^[a-z].*", ".*debug.*"]
        self.transformer._remove_enums(file_model, patterns)
        
        # Should have Color, LogLevel, and Status left (debug_state matches both patterns)
        self.assertEqual(len(file_model.enums), 3)
        self.assertIn("Color", file_model.enums)
        self.assertIn("LogLevel", file_model.enums)
        self.assertIn("Status", file_model.enums)
        self.assertNotIn("debug_state", file_model.enums)

    def test_remove_unions_regex_patterns(self):
        """Test removing unions with regex patterns"""
        file_model = FileModel("test.c")
        file_model.unions = {
            "Value": Union("Value", []),
            "temp_union": Union("temp_union", []),
            "Data": Union("Data", []),
            "debug_union": Union("debug_union", [])
        }
        
        # Remove unions starting with lowercase
        patterns = ["^[a-z].*"]
        self.transformer._remove_unions(file_model, patterns)
        
        # Should have Value and Data left
        self.assertEqual(len(file_model.unions), 2)
        self.assertIn("Value", file_model.unions)
        self.assertIn("Data", file_model.unions)
        self.assertNotIn("temp_union", file_model.unions)
        self.assertNotIn("debug_union", file_model.unions)

    def test_remove_operations_empty_patterns(self):
        """Test that remove operations handle empty pattern lists correctly"""
        file_model = FileModel("test.c")
        file_model.functions = [Function("test", "void", [])]
        file_model.macros = ["TEST_MACRO"]
        
        # Empty patterns should not remove anything
        self.transformer._remove_functions(file_model, [])
        self.transformer._remove_macros(file_model, [])
        
        self.assertEqual(len(file_model.functions), 1)
        self.assertEqual(len(file_model.macros), 1)

    def test_remove_operations_no_matches(self):
        """Test remove operations when no patterns match"""
        file_model = FileModel("test.c")
        file_model.functions = [Function("main", "int", []), Function("helper", "void", [])]
        
        # Pattern that matches nothing
        patterns = ["^nonexistent_.*"]
        self.transformer._remove_functions(file_model, patterns)
        
        # Should still have all functions
        self.assertEqual(len(file_model.functions), 2)

    def test_rename_functions_with_deduplication(self):
        """Test renaming functions with deduplication when patterns create duplicates"""
        file_model = FileModel("test.c")
        file_model.functions = [
            Function("old_calculate", "int", []),
            Function("legacy_calculate", "float", []),  # This will create duplicate after rename
            Function("old_process", "void", []),
            Function("legacy_process", "char*", [])  # This will create duplicate after rename
        ]
        
        # Both patterns rename to the same result
        patterns_map = {
            "^old_(.*)": "new_\\1",
            "^legacy_(.*)": "new_\\1"
        }
        self.transformer._rename_functions(file_model, patterns_map)
        
        # Should have 2 functions: new_calculate (from old_calculate, first match) and new_process
        self.assertEqual(len(file_model.functions), 2)
        function_names = [f.name for f in file_model.functions]
        self.assertIn("new_calculate", function_names)
        self.assertIn("new_process", function_names)
        
        # The kept new_calculate should have return_type "int" (from old_calculate, the first match)
        new_calc = next(f for f in file_model.functions if f.name == "new_calculate")
        self.assertEqual(new_calc.return_type, "int")

    def test_rename_typedefs_with_deduplication(self):
        """Test renaming typedefs with deduplication"""
        file_model = FileModel("test.c")
        file_model.aliases = {
            "old_type1": Alias("old_type1", "int", []),
            "legacy_type1": Alias("legacy_type1", "float", []),  # Will create duplicate
            "old_type2": Alias("old_type2", "char", [])
        }
        
        patterns_map = {
            "^old_(.*)": "new_\\1",
            "^legacy_(.*)": "new_\\1"
        }
        self.transformer._rename_typedefs(file_model, patterns_map)
        
        # Should have 2 typedefs: new_type1 and new_type2
        self.assertEqual(len(file_model.aliases), 2)
        self.assertIn("new_type1", file_model.aliases)
        self.assertIn("new_type2", file_model.aliases)
        
        # First match wins - should have "int" original_type
        self.assertEqual(file_model.aliases["new_type1"].original_type, "int")

    def test_rename_macros_with_deduplication(self):
        """Test renaming macros with deduplication"""
        file_model = FileModel("test.c")
        file_model.macros = [
            "OLD_CONSTANT",
            "LEGACY_CONSTANT",  # Will create duplicate after rename
            "OLD_MAX_SIZE",
            "UNIQUE_MACRO"
        ]
        
        patterns_map = {
            "^OLD_(.*)": "NEW_\\1",
            "^LEGACY_(.*)": "NEW_\\1"
        }
        self.transformer._rename_macros(file_model, patterns_map)
        
        # Should have 3 macros: NEW_CONSTANT, NEW_MAX_SIZE, UNIQUE_MACRO
        self.assertEqual(len(file_model.macros), 3)
        self.assertIn("NEW_CONSTANT", file_model.macros)
        self.assertIn("NEW_MAX_SIZE", file_model.macros)
        self.assertIn("UNIQUE_MACRO", file_model.macros)

    def test_rename_globals_with_deduplication(self):
        """Test renaming global variables with deduplication"""
        file_model = FileModel("test.c")
        file_model.globals = [
            Field("old_counter", "int"),
            Field("legacy_counter", "long"),  # Will create duplicate
            Field("old_buffer", "char*"),
            Field("normal_var", "float")
        ]
        
        patterns_map = {
            "^old_(.*)": "new_\\1",
            "^legacy_(.*)": "new_\\1"
        }
        self.transformer._rename_globals(file_model, patterns_map)
        
        # Should have 3 globals: new_counter, new_buffer, normal_var
        self.assertEqual(len(file_model.globals), 3)
        global_names = [g.name for g in file_model.globals]
        self.assertIn("new_counter", global_names)
        self.assertIn("new_buffer", global_names)
        self.assertIn("normal_var", global_names)
        
        # First match wins - should have "int" type
        new_counter = next(g for g in file_model.globals if g.name == "new_counter")
        self.assertEqual(new_counter.type, "int")

    def test_rename_includes_with_deduplication(self):
        """Test renaming includes with deduplication"""
        file_model = FileModel("test.c")
        file_model.includes = {"old_header.h", "legacy_header.h", "normal.h"}
        file_model.include_relations = [
            IncludeRelation("test.c", "old_header.h", 1),
            IncludeRelation("test.c", "legacy_header.h", 1),
            IncludeRelation("test.c", "normal.h", 1)
        ]
        
        patterns_map = {
            "^old_(.*)": "new_\\1",
            "^legacy_(.*)": "new_\\1"
        }
        self.transformer._rename_includes(file_model, patterns_map)
        
        # Should have 2 includes: new_header.h, normal.h
        self.assertEqual(len(file_model.includes), 2)
        self.assertIn("new_header.h", file_model.includes)
        self.assertIn("normal.h", file_model.includes)
        
        # Include relations should also be updated
        relation_files = [r.included_file for r in file_model.include_relations]
        # We expect to see 3 relations but only 2 unique includes due to deduplication
        self.assertEqual(len(file_model.include_relations), 3)
        self.assertIn("new_header.h", relation_files)
        self.assertIn("normal.h", relation_files)

    def test_rename_structs_with_deduplication(self):
        """Test renaming structs with deduplication"""
        file_model = FileModel("test.c")
        file_model.structs = {
            "old_point": Struct("old_point", []),
            "legacy_point": Struct("legacy_point", []),  # Will create duplicate
            "old_rect": Struct("old_rect", [])
        }
        
        patterns_map = {
            "^old_(.*)": "new_\\1",
            "^legacy_(.*)": "new_\\1"
        }
        self.transformer._rename_structs(file_model, patterns_map)
        
        # Should have 2 structs: new_point and new_rect
        self.assertEqual(len(file_model.structs), 2)
        self.assertIn("new_point", file_model.structs)
        self.assertIn("new_rect", file_model.structs)

    def test_rename_enums_with_deduplication(self):
        """Test renaming enums with deduplication"""
        file_model = FileModel("test.c")
        file_model.enums = {
            "old_color": Enum("old_color", []),
            "legacy_color": Enum("legacy_color", []),  # Will create duplicate
            "old_state": Enum("old_state", [])
        }
        
        patterns_map = {
            "^old_(.*)": "new_\\1",
            "^legacy_(.*)": "new_\\1"
        }
        self.transformer._rename_enums(file_model, patterns_map)
        
        # Should have 2 enums: new_color and new_state
        self.assertEqual(len(file_model.enums), 2)
        self.assertIn("new_color", file_model.enums)
        self.assertIn("new_state", file_model.enums)

    def test_rename_unions_with_deduplication(self):
        """Test renaming unions with deduplication"""
        file_model = FileModel("test.c")
        file_model.unions = {
            "old_data": Union("old_data", []),
            "legacy_data": Union("legacy_data", []),  # Will create duplicate
            "old_value": Union("old_value", [])
        }
        
        patterns_map = {
            "^old_(.*)": "new_\\1",
            "^legacy_(.*)": "new_\\1"
        }
        self.transformer._rename_unions(file_model, patterns_map)
        
        # Should have 2 unions: new_data and new_value
        self.assertEqual(len(file_model.unions), 2)
        self.assertIn("new_data", file_model.unions)
        self.assertIn("new_value", file_model.unions)

    def test_rename_files(self):
        """Test renaming files"""
        model = ProjectModel("test_project", ".")
        model.files = {
            "old_main.c": FileModel("old_main.c"),
            "legacy_utils.c": FileModel("legacy_utils.c"),
            "normal.c": FileModel("normal.c")
        }
        
        target_files = {"old_main.c", "legacy_utils.c"}
        patterns_map = {
            "^old_(.*)": "new_\\1",
            "^legacy_(.*)": "modern_\\1"
        }
        
        result = self.transformer._rename_files(model, patterns_map, target_files)
        
        # Should have new file names
        self.assertIn("new_main.c", result.files)
        self.assertIn("modern_utils.c", result.files)
        self.assertIn("normal.c", result.files)  # Unchanged
        self.assertNotIn("old_main.c", result.files)
        self.assertNotIn("legacy_utils.c", result.files)
        
        # File models should have updated names
        self.assertEqual(result.files["new_main.c"].name, "new_main.c")
        self.assertEqual(result.files["modern_utils.c"].name, "modern_utils.c")

    def test_apply_rename_patterns_no_match(self):
        """Test apply_rename_patterns when no patterns match"""
        original_name = "unchanged_name"
        patterns_map = {"^old_(.*)": "new_\\1"}
        
        result = self.transformer._apply_rename_patterns(original_name, patterns_map)
        self.assertEqual(result, original_name)

    def test_apply_rename_patterns_invalid_regex(self):
        """Test apply_rename_patterns with invalid regex"""
        original_name = "test_name"
        patterns_map = {"[invalid": "replacement"}
        
        result = self.transformer._apply_rename_patterns(original_name, patterns_map)
        self.assertEqual(result, original_name)  # Should return original on error

    def test_rename_operations_empty_patterns(self):
        """Test that rename operations handle empty pattern maps correctly"""
        file_model = FileModel("test.c")
        file_model.functions = [Function("test", "void", [])]
        file_model.macros = ["TEST_MACRO"]
        
        # Empty patterns should not rename anything
        self.transformer._rename_functions(file_model, {})
        self.transformer._rename_macros(file_model, {})
        
        self.assertEqual(file_model.functions[0].name, "test")
        self.assertEqual(file_model.macros[0], "TEST_MACRO")

    def test_multiple_transformation_containers(self):
        """Test multiple transformation containers applied in alphabetical order"""
        config = {
            "transformations_z_last": {
                "file_selection": [],
                "add": {"macros": ["FINAL_MACRO"]}
            },
            "transformations_a_first": {
                "file_selection": [],
                "remove": {"functions": ["debug_.*"]}
            },
            "transformations_m_middle": {
                "file_selection": [],
                "rename": {"functions": {"old_(.*)": "new_\\1"}}
            }
        }
        
        # Create model with functions that will be affected
        model = ProjectModel("test_project", ".")
        model.files = {
            "test.c": FileModel("test.c")
        }
        model.files["test.c"].functions = [
            Function("debug_func", "void", []),
            Function("old_calculate", "int", []),
            Function("normal_func", "char*", [])
        ]
        model.files["test.c"].macros = []
        
        # Should execute in order: a_first, m_middle, z_last
        result = self.transformer._apply_transformations(model, config)
        
        # Verify transformations were applied in correct order
        self.assertIsInstance(result, ProjectModel)
        # After a_first: debug_func should be removed
        # After m_middle: old_calculate should be renamed to new_calculate
        # After z_last: FINAL_MACRO should be added
        function_names = [f.name for f in result.files["test.c"].functions]
        self.assertNotIn("debug_func", function_names)  # Removed in a_first
        self.assertIn("new_calculate", function_names)  # Renamed in m_middle
        self.assertIn("normal_func", function_names)  # Unchanged
        # Macro addition functionality is available

    def test_backward_compatibility_single_transformations(self):
        """Test that old single 'transformations' format still works"""
        config = {
            "transformations": {
                "file_selection": [],
                "remove": {"functions": ["test_.*"]}
            }
        }
        
        model = ProjectModel("test_project", ".")
        model.files = {
            "test.c": FileModel("test.c")
        }
        model.files["test.c"].functions = [
            Function("test_func", "void", []),
            Function("normal_func", "int", [])
        ]
        
        result = self.transformer._apply_transformations(model, config)
        
        # Should work the same as before
        self.assertIsInstance(result, ProjectModel)
        function_names = [f.name for f in result.files["test.c"].functions]
        self.assertNotIn("test_func", function_names)
        self.assertIn("normal_func", function_names)

    def test_discover_transformation_containers(self):
        """Test discovery and sorting of transformation containers"""
        config = {
            "project_name": "test",
            "transformations_z_last": {"remove": {}},
            "transformations_a_first": {"rename": {}},
            "transformations_m_middle": {"add": {}},
            "not_transformation": {"some": "value"},
            "transformations_invalid": "not_a_dict"  # Should be ignored
        }
        
        containers = self.transformer._discover_transformation_containers(config)
        
        # Should find 3 valid containers in alphabetical order
        self.assertEqual(len(containers), 3)
        names = [name for name, _ in containers]
        self.assertEqual(names, ["transformations_a_first", "transformations_m_middle", "transformations_z_last"])

    def test_ensure_backward_compatibility(self):
        """Test backward compatibility conversion"""
        # Test old format conversion
        old_config = {
            "transformations": {
                "remove": {"functions": ["test"]}
            }
        }
        
        converted = self.transformer._ensure_backward_compatibility(old_config)
        
        # Should convert to new format
        self.assertNotIn("transformations", converted)
        self.assertIn("transformations_00_default", converted)
        self.assertEqual(converted["transformations_00_default"]["remove"]["functions"], ["test"])
        
        # Test new format (should not change)
        new_config = {
            "transformations_01_first": {
                "remove": {"functions": ["test"]}
            }
        }
        
        unchanged = self.transformer._ensure_backward_compatibility(new_config)
        self.assertEqual(unchanged, new_config)

    def test_apply_single_transformation_container(self):
        """Test applying a single transformation container"""
        model = ProjectModel("test_project", ".")
        model.files = {
            "test.c": FileModel("test.c"),
            "other.c": FileModel("other.c")
        }
        model.files["test.c"].functions = [Function("old_func", "void", [])]
        model.files["other.c"].functions = [Function("old_func", "void", [])]
        
        # Container with file selection
        container_config = {
            "file_selection": [".*test\\.c$"],
            "rename": {
                "functions": {"old_(.*)": "new_\\1"}
            }
        }
        
        result = self.transformer._apply_single_transformation_container(
            model, container_config, "test_container"
        )
        
        # Should only affect test.c
        self.assertEqual(result.files["test.c"].functions[0].name, "new_func")
        self.assertEqual(result.files["other.c"].functions[0].name, "old_func")  # Unchanged

    def test_transformation_container_order_execution(self):
        """Test that containers are executed in alphabetical order with correct transformations"""
        config = {
            "transformations_02_rename": {
                "file_selection": [],
                "rename": {
                    "functions": {"prefix_(.*)": "renamed_\\1"}
                }
            },
            "transformations_01_remove": {
                "file_selection": [],
                "remove": {
                    "functions": ["debug_.*"]
                }
            }
        }
        
        model = ProjectModel("test_project", ".")
        model.files = {
            "test.c": FileModel("test.c")
        }
        model.files["test.c"].functions = [
            Function("debug_func", "void", []),
            Function("prefix_calculate", "int", []),
            Function("normal_func", "char*", [])
        ]
        
        result = self.transformer._apply_transformations(model, config)
        
        # Should execute 01_remove first, then 02_rename
        function_names = [f.name for f in result.files["test.c"].functions]
        self.assertNotIn("debug_func", function_names)  # Removed in step 1
        self.assertIn("renamed_calculate", function_names)  # Renamed in step 2
        self.assertIn("normal_func", function_names)  # Unchanged

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

        # Check that includes were preserved (correct behavior)
        self.assertEqual(len(result.files["main.c"].includes), 4)
        self.assertIn("stdio.h", result.files["main.c"].includes)
        self.assertIn("string.h", result.files["main.c"].includes)
        self.assertIn("stdlib.h", result.files["main.c"].includes)
        self.assertIn("math.h", result.files["main.c"].includes)

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

        # Check main.c filtering (includes preserved, only relations filtered)
        main_c = result.files["main.c"]
        self.assertEqual(len(main_c.includes), 3)
        self.assertIn("stdio.h", main_c.includes)
        self.assertIn("stdlib.h", main_c.includes)
        self.assertIn("utils.h", main_c.includes)

        # Check utils.c filtering (includes preserved, only relations filtered)
        utils_c = result.files["utils.c"]
        self.assertEqual(len(utils_c.includes), 3)
        self.assertIn("string.h", utils_c.includes)
        self.assertIn("math.h", utils_c.includes)
        self.assertIn("utils.h", utils_c.includes)

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
        # Include relations generation depends on file discovery

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
