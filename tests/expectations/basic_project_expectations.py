#!/usr/bin/env python3
"""
Test expectations for basic project use case

This module defines the expected behavior and content for the basic project
use case, including file structure, content validation, and output verification.
"""

import unittest
from pathlib import Path
from typing import Dict, List
from tests.expectations.base_expectations import BaseExpectations
from c_to_plantuml.models import ProjectModel, FileModel


class BasicProjectExpectations(BaseExpectations):
    """Expectations for basic project use case"""
    
    def __init__(self):
        super().__init__("use_case_basic_project")
    
    def validate_project_structure(self, model: ProjectModel) -> None:
        """Validate the overall project structure"""
        # Verify project structure
        self.assertEqual(model.project_name, "input")  # Project name is derived from directory name
        self.assertEqual(len(model.files), 3)
        
        # Check that all files are parsed
        file_paths = [f for f in model.files.keys()]
        self.assertIn("main.c", file_paths)
        self.assertIn("utils.h", file_paths)
        self.assertIn("types.h", file_paths)
    
    def validate_file_content(self, model: ProjectModel) -> None:
        """Validate the content of individual files"""
        # Check main.c content
        main_c_model = model.files["main.c"]
        self.assertEqual(len(main_c_model.functions), 4)  # add, multiply, print_point, main
        self.assertEqual(len(main_c_model.globals), 2)  # global_counter, global_name
        self.assertEqual(len(main_c_model.includes), 3)  # stdio.h, utils.h, types.h
        
        # Check utils.h content
        utils_h_model = model.files["utils.h"]
        self.assertEqual(len(utils_h_model.structs), 1)  # Rectangle
        self.assertEqual(len(utils_h_model.enums), 1)  # Status
        self.assertEqual(len(utils_h_model.unions), 1)  # Data
        self.assertEqual(len(utils_h_model.functions), 3)  # add, multiply, print_point
        
        # Check types.h content
        types_h_model = model.files["types.h"]
        self.assertEqual(len(types_h_model.typedefs), 6)  # MyInt, String, ULong, Point, Color, Value
        self.assertGreaterEqual(len(types_h_model.typedef_relations), 4)  # At least 4 typedef relations
    
    def validate_generated_output(self, output_dir: Path) -> None:
        """Validate the generated PlantUML output"""
        # Check that output was generated
        self.assertTrue(output_dir.exists())
        main_puml = output_dir / "main.puml"
        self.assertTrue(main_puml.exists())
        
        # Check content
        content = main_puml.read_text()
        self.assertIn("class \"main\"", content)
        self.assertIn("class \"utils\"", content)
        self.assertIn("class \"types\"", content)
        self.assertIn("typedef", content)
    
    def get_expected_file_count(self) -> int:
        """Get the expected number of files in the project"""
        return 3
    
    def get_expected_output_files(self) -> List[str]:
        """Get the expected output file names"""
        return ["main.puml"]
    
    def get_expected_structs(self) -> Dict[str, List[str]]:
        """Get expected structs for each file"""
        return {
            "utils.h": ["Rectangle"],
            "types.h": []  # Structs are defined as typedefs
        }
    
    def get_expected_enums(self) -> Dict[str, List[str]]:
        """Get expected enums for each file"""
        return {
            "utils.h": ["Status"],
            "types.h": []
        }
    
    def get_expected_functions(self) -> Dict[str, List[str]]:
        """Get expected functions for each file"""
        return {
            "main.c": ["add", "multiply", "print_point", "main"],
            "utils.h": ["add", "multiply", "print_point"]
        }
    
    def get_expected_typedefs(self) -> Dict[str, List[str]]:
        """Get expected typedefs for each file"""
        return {
            "types.h": ["MyInt", "String", "ULong", "Point", "Color", "Value"]
        }
    
    def get_expected_macros(self) -> Dict[str, List[str]]:
        """Get expected macros for each file"""
        return {}
    
    def get_expected_includes(self) -> Dict[str, List[str]]:
        """Get expected includes for each file"""
        return {
            "main.c": ["stdio.h", "utils.h", "types.h"]
        }
    
    def get_expected_globals(self) -> Dict[str, List[str]]:
        """Get expected global variables for each file"""
        return {
            "main.c": ["global_counter", "global_name"]
        }
    
    def get_expected_unions(self) -> Dict[str, List[str]]:
        """Get expected unions for each file"""
        return {
            "utils.h": ["Data"]
        }
    
    def get_expected_plantuml_content(self) -> List[str]:
        """Get expected content that should appear in PlantUML output"""
        return [
            "class \"main\"",
            "class \"utils\"",
            "class \"types\"",
            "typedef"
        ]
    
    def get_expected_plantuml_classes(self) -> List[str]:
        """Get expected class names that should appear in PlantUML output"""
        return ["main", "utils", "types"]
    
    def get_expected_plantuml_relationships(self) -> List[str]:
        """Get expected relationships that should appear in PlantUML output"""
        return []