#!/usr/bin/env python3
"""
Unit tests for the transformer module
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import re

from c_to_plantuml.models import (
    Enum, Field, FileModel, Function, IncludeRelation, 
    ProjectModel, Struct, TypedefRelation, Union
)
from c_to_plantuml.transformer import Transformer


class TestTransformer(unittest.TestCase):
    """Test the transformer functionality"""

    def setUp(self):
        self.transformer = Transformer()
        
        # Create sample data for testing
        self.sample_file_model = FileModel(
            file_path="/test/project/sample.c",
            relative_path="sample.c",
            project_root="/test/project",
            encoding_used="utf-8",
            structs={
                "Person": Struct("Person", [
                    Field("name", "char[50]"),
                    Field("age", "int")
                ]),
                "Point": Struct("Point", [
                    Field("x", "int"),
                    Field("y", "int")
                ])
            },
            enums={
                "Status": Enum("Status", ["OK", "ERROR", "PENDING"])
            },
            unions={
                "Data": Union("Data", [
                    Field("i", "int"),
                    Field("f", "float"),
                    Field("str", "char[20]")
                ])
            },
            functions=[
                Function("main", "int", [Field("argc", "int"), Field("argv", "char**")]),
                Function("calculate", "int", [Field("a", "int"), Field("b", "int")])
            ],
            globals=[
                Field("global_var", "int"),
                Field("global_ptr", "void*")
            ],
            includes={"stdio.h", "stdlib.h"},
            macros=["MAX_SIZE", "DEBUG_MODE"],
            typedefs={"point_t": "struct Point", "status_t": "enum Status"}
        )
        
        self.sample_project_model = ProjectModel(
            project_name="TestProject",
            project_root="/test/project",
            files={
                "sample.c": self.sample_file_model,
                "header.h": FileModel(
                    file_path="/test/project/header.h",
                    relative_path="header.h",
                    project_root="/test/project",
                    encoding_used="utf-8",
                    structs={},
                    enums={},
                    unions={},
                    functions=[],
                    globals=[],
                    includes=set(),
                    macros=[],
                    typedefs={}
                )
            }
        )

    def test_transform_main_method(self):
        """Test the main transform method"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as model_file:
            json.dump({
                "project_name": "TestProject",
                "project_root": "/test/project",
                "files": {
                    "sample.c": self.sample_file_model.to_dict()
                },
                "created_at": "2023-01-01T00:00:00"
            }, model_file)
            model_file_path = model_file.name
            
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as config_file:
            json.dump({
                "file_filters": {
                    "include": [r".*\.c$"],
                    "exclude": [r".*test.*"]
                }
            }, config_file)
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
            json.dump({
                "project_name": "TestProject",
                "project_root": "/test/project",
                "files": {
                    "sample.c": self.sample_file_model.to_dict()
                },
                "created_at": "2023-01-01T00:00:00"
            }, f)
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
            "file_filters": {
                "include": [r".*\.c$"],
                "exclude": [r".*test.*"]
            },
            "element_filters": {
                "structs": {
                    "include": [r"Person.*"],
                    "exclude": [r"Temp.*"]
                }
            }
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
        config = {
            "include": [r".*\.c$"],
            "exclude": []
        }
        
        result = self.transformer._apply_file_filters(self.sample_project_model, config)
        
        # Should only include .c files
        self.assertEqual(len(result.files), 1)
        self.assertIn("sample.c", result.files)
        self.assertNotIn("header.h", result.files)

    def test_apply_file_filters_exclude_only(self):
        """Test file filtering with exclude patterns only"""
        config = {
            "include": [],
            "exclude": [r".*\.h$"]
        }
        
        result = self.transformer._apply_file_filters(self.sample_project_model, config)
        
        # Should exclude .h files
        self.assertEqual(len(result.files), 1)
        self.assertIn("sample.c", result.files)
        self.assertNotIn("header.h", result.files)

    def test_apply_file_filters_both_patterns(self):
        """Test file filtering with both include and exclude patterns"""
        config = {
            "include": [r".*\.c$"],
            "exclude": [r".*test.*"]
        }
        
        result = self.transformer._apply_file_filters(self.sample_project_model, config)
        
        # Should include .c files but exclude test files
        self.assertEqual(len(result.files), 1)
        self.assertIn("sample.c", result.files)

    def test_apply_file_filters_no_patterns(self):
        """Test file filtering with no patterns (should return original model)"""
        config = {
            "include": [],
            "exclude": []
        }
        
        result = self.transformer._apply_file_filters(self.sample_project_model, config)
        
        # Should return the original model unchanged
        self.assertEqual(len(result.files), len(self.sample_project_model.files))
        self.assertEqual(result.files, self.sample_project_model.files)

    def test_apply_element_filters_structs(self):
        """Test element filtering for structs"""
        config = {
            "structs": {
                "include": [r"Person.*"],
                "exclude": [r"Temp.*"]
            }
        }
        
        result = self.transformer._apply_element_filters(self.sample_project_model, config)
        
        # Should only include Person struct
        file_model = result.files["sample.c"]
        self.assertIn("Person", file_model.structs)
        self.assertNotIn("Point", file_model.structs)

    def test_apply_element_filters_functions(self):
        """Test element filtering for functions"""
        config = {
            "functions": {
                "include": [r"main.*"],
                "exclude": [r"temp.*"]
            }
        }
        
        result = self.transformer._apply_element_filters(self.sample_project_model, config)
        
        # Should only include main function
        file_model = result.files["sample.c"]
        function_names = [f.name for f in file_model.functions]
        self.assertIn("main", function_names)
        self.assertNotIn("calculate", function_names)

    def test_apply_element_filters_enums(self):
        """Test element filtering for enums"""
        config = {
            "enums": {
                "include": [r"Status.*"],
                "exclude": [r"Temp.*"]
            }
        }
        
        result = self.transformer._apply_element_filters(self.sample_project_model, config)
        
        # Should only include Status enum
        file_model = result.files["sample.c"]
        self.assertIn("Status", file_model.enums)

    def test_apply_element_filters_unions(self):
        """Test element filtering for unions"""
        config = {
            "unions": {
                "include": [r"Data.*"],
                "exclude": [r"Temp.*"]
            }
        }
        
        result = self.transformer._apply_element_filters(self.sample_project_model, config)
        
        # Should only include Data union
        file_model = result.files["sample.c"]
        self.assertIn("Data", file_model.unions)

    def test_apply_element_filters_globals(self):
        """Test element filtering for globals"""
        config = {
            "globals": {
                "include": [r"global_var.*"],
                "exclude": [r"temp.*"]
            }
        }
        
        result = self.transformer._apply_element_filters(self.sample_project_model, config)
        
        # Should only include global_var
        file_model = result.files["sample.c"]
        global_names = [g.name for g in file_model.globals]
        self.assertIn("global_var", global_names)
        self.assertNotIn("global_ptr", global_names)

    def test_apply_element_filters_macros(self):
        """Test element filtering for macros"""
        config = {
            "macros": {
                "include": [r"MAX.*"],
                "exclude": [r"TEMP.*"]
            }
        }
        
        result = self.transformer._apply_element_filters(self.sample_project_model, config)
        
        # Should only include MAX_SIZE macro
        file_model = result.files["sample.c"]
        self.assertIn("MAX_SIZE", file_model.macros)
        self.assertNotIn("DEBUG_MODE", file_model.macros)

    def test_apply_element_filters_typedefs(self):
        """Test element filtering for typedefs"""
        config = {
            "typedefs": {
                "include": [r"point_t.*"],
                "exclude": [r"temp.*"]
            }
        }
        
        result = self.transformer._apply_element_filters(self.sample_project_model, config)
        
        # Should only include point_t typedef
        file_model = result.files["sample.c"]
        self.assertIn("point_t", file_model.typedefs)
        self.assertNotIn("status_t", file_model.typedefs)

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
        self.assertTrue(self.transformer._should_include_file(
            "test.c", include_patterns, exclude_patterns
        ))
        
        # Should not include .h files
        self.assertFalse(self.transformer._should_include_file(
            "test.h", include_patterns, exclude_patterns
        ))

    def test_should_include_file_exclude_patterns(self):
        """Test file inclusion with exclude patterns"""
        include_patterns = []
        exclude_patterns = [re.compile(r".*test.*")]
        
        # Should not include test files
        self.assertFalse(self.transformer._should_include_file(
            "test.c", include_patterns, exclude_patterns
        ))
        
        # Should include non-test files
        self.assertTrue(self.transformer._should_include_file(
            "main.c", include_patterns, exclude_patterns
        ))

    def test_should_include_file_both_patterns(self):
        """Test file inclusion with both include and exclude patterns"""
        include_patterns = [re.compile(r".*\.c$")]
        exclude_patterns = [re.compile(r".*test.*")]
        
        # Should not include test.c (matches exclude)
        self.assertFalse(self.transformer._should_include_file(
            "test.c", include_patterns, exclude_patterns
        ))
        
        # Should include main.c (matches include, doesn't match exclude)
        self.assertTrue(self.transformer._should_include_file(
            "main.c", include_patterns, exclude_patterns
        ))

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
            {"name": "other", "value": 3}
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
            "relative_path": "file.c",
            "project_root": "/test",
            "encoding_used": "utf-8",
            "structs": {
                "TestStruct": {
                    "name": "TestStruct",
                    "fields": [{"name": "field1", "type": "int"}],
                    "methods": []
                }
            },
            "enums": {
                "TestEnum": {
                    "name": "TestEnum",
                    "values": ["VAL1", "VAL2"]
                }
            },
            "unions": {
                "TestUnion": {
                    "name": "TestUnion",
                    "fields": [{"name": "field1", "type": "int"}]
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
            "include_relations": []
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
            relative_path="file1.c",
            project_root="/test",
            encoding_used="utf-8",
            includes={"file2.h"},
            structs={}, enums={}, unions={}, functions=[], globals=[],
            macros=[], typedefs={}, typedef_relations=[], include_relations=[]
        )
        
        file2 = FileModel(
            file_path="/test/file2.h",
            relative_path="file2.h",
            project_root="/test",
            encoding_used="utf-8",
            includes=set(),
            structs={}, enums={}, unions={}, functions=[], globals=[],
            macros=[], typedefs={}, typedef_relations=[], include_relations=[]
        )
        
        model = ProjectModel(
            project_name="TestProject",
            project_root="/test",
            files={"file1.c": file1, "file2.h": file2}
        )
        
        with patch.object(self.transformer, '_find_included_file') as mock_find:
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
            
            # Test finding the file
            result = self.transformer._find_included_file("test.h", temp_dir)
            self.assertEqual(result, str(header_file.resolve()))

    def test_find_included_file_not_found(self):
        """Test finding non-existent included file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = self.transformer._find_included_file("nonexistent.h", temp_dir)
            self.assertIsNone(result)

    def test_apply_transformations_no_config(self):
        """Test applying transformations with empty config"""
        config = {}
        result = self.transformer._apply_transformations(self.sample_project_model, config)
        
        # Should return the original model unchanged
        self.assertEqual(result, self.sample_project_model)

    def test_apply_transformations_with_all_sections(self):
        """Test applying transformations with all configuration sections"""
        config = {
            "file_filters": {
                "include": [".*\\.c$"],
                "exclude": [".*test.*"]
            },
            "element_filters": {
                "structs": {
                    "include": ["^[A-Z].*"],
                    "exclude": [".*_internal.*"]
                }
            },
            "transformations": {
                "file_selection": {
                    "selected_files": []
                },
                "rename": {
                    "structs": {
                        "old_name": "new_name"
                    }
                }
            },
            "include_depth": 2
        }
        
        result = self.transformer._apply_transformations(self.sample_project_model, config)
        self.assertIsInstance(result, ProjectModel)
        self.assertEqual(len(result.files), 1)  # Only .c files after filtering

    def test_file_selection_apply_to_all(self):
        """Test file selection with empty selected_files (apply to all)"""
        config = {
            "transformations": {
                "file_selection": {
                    "selected_files": []
                },
                "rename": {
                    "structs": {
                        "old_name": "new_name"
                    }
                }
            }
        }
        
        result = self.transformer._apply_model_transformations(self.sample_project_model, config["transformations"])
        self.assertIsInstance(result, ProjectModel)
        # Should apply to all files
        self.assertEqual(len(result.files), 2)

    def test_file_selection_no_file_selection(self):
        """Test file selection with no file_selection specified (apply to all)"""
        config = {
            "transformations": {
                "rename": {
                    "structs": {
                        "old_name": "new_name"
                    }
                }
            }
        }
        
        result = self.transformer._apply_model_transformations(self.sample_project_model, config["transformations"])
        self.assertIsInstance(result, ProjectModel)
        # Should apply to all files
        self.assertEqual(len(result.files), 2)

    def test_file_selection_selected_files(self):
        """Test file selection with specific file patterns"""
        config = {
            "transformations": {
                "file_selection": {
                    "selected_files": [".*sample\\.c$"]
                },
                "rename": {
                    "structs": {
                        "old_name": "new_name"
                    }
                }
            }
        }
        
        result = self.transformer._apply_model_transformations(self.sample_project_model, config["transformations"])
        self.assertIsInstance(result, ProjectModel)
        # Should apply only to sample.c
        self.assertEqual(len(result.files), 2)  # Files still exist, but transformations applied only to selected

    def test_file_selection_no_matching_files(self):
        """Test file selection with no matching files"""
        config = {
            "transformations": {
                "file_selection": {
                    "selected_files": [".*nonexistent\\.c$"]
                },
                "rename": {
                    "structs": {
                        "old_name": "new_name"
                    }
                }
            }
        }
        
        result = self.transformer._apply_model_transformations(self.sample_project_model, config["transformations"])
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
        rename_config = {
            "structs": {
                "Person": "Employee",
                "Point": "Coordinate"
            }
        }
        
        result = self.transformer._apply_renaming(self.sample_project_model, rename_config, target_files)
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
                        {"name": "field2", "type": "char*"}
                    ]
                }
            }
        }
        
        result = self.transformer._apply_additions(self.sample_project_model, add_config, target_files)
        self.assertIsInstance(result, ProjectModel)
        # Should apply additions only to sample.c
        self.assertIn("sample.c", result.files)

    def test_removals_with_file_selection(self):
        """Test removals with file selection"""
        target_files = {"sample.c"}
        remove_config = {
            "functions": ["calculate"],
            "structs": ["Point"]
        }
        
        result = self.transformer._apply_removals(self.sample_project_model, remove_config, target_files)
        self.assertIsInstance(result, ProjectModel)
        # Should apply removals only to sample.c
        self.assertIn("sample.c", result.files)


if __name__ == "__main__":
    unittest.main()