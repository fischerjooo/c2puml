#!/usr/bin/env python3
"""
Test expectations for large codebase use case

This module defines the expected behavior and content for the large codebase
use case, including file structure, content validation, and output verification.
"""

from pathlib import Path
from typing import Dict, List
try:
    from tests.expectations.base_expectations import BaseExpectations
except ImportError:
    from .base_expectations import BaseExpectations
from c_to_plantuml.models import ProjectModel, FileModel


class LargeCodebaseExpectations(BaseExpectations):
    """Expectations for large codebase use case"""
    
    def __init__(self):
        super().__init__("use_case_large_codebase")
    
    def validate_project_structure(self, model: ProjectModel) -> None:
        """Validate the overall project structure"""
        # Verify project structure
        self.assertEqual(model.project_name, "input")  # Project name is derived from directory name
        self.assertGreaterEqual(len(model.files), 5)  # Should have at least 5 files
        
        # Check that all expected files are parsed
        file_paths = [f for f in model.files.keys()]
        self.assertIn("main.c", file_paths)
        self.assertIn("core.h", file_paths)
        self.assertIn("core.c", file_paths)
        self.assertIn("utils.h", file_paths)
        self.assertIn("utils.c", file_paths)
    
    def validate_file_content(self, model: ProjectModel) -> None:
        """Validate the content of individual files"""
        # Check main.c content
        main_c_model = model.files["main.c"]
        self.assertGreaterEqual(len(main_c_model.functions), 1)  # At least main function
        self.assertGreaterEqual(len(main_c_model.includes), 2)  # At least core.h and utils.h
        
        # Check core.h content
        core_h_model = model.files["core.h"]
        self.assertGreaterEqual(len(core_h_model.typedefs), 2)  # At least CoreObject and CoreStatus
        self.assertGreaterEqual(len(core_h_model.functions), 3)  # At least 3 functions (core_init, core_cleanup, core_create_object, core_destroy_object)
        
        # Check utils.h content
        utils_h_model = model.files["utils.h"]
        self.assertGreaterEqual(len(utils_h_model.typedefs), 3)  # At least Vector3D, Variant, UtilResult
        self.assertGreaterEqual(len(utils_h_model.functions), 6)  # At least 6 functions
    
    def validate_generated_output(self, output_dir: Path) -> None:
        """Validate the generated PlantUML output"""
        # Check that output was generated
        self.assertTrue(output_dir.exists())
        
        # Should generate multiple .puml files
        puml_files = list(output_dir.glob("*.puml"))
        self.assertGreaterEqual(len(puml_files), 3)  # At least 3 files (main.c, core.c, utils.c)
        
        # Check main.puml content
        main_puml = output_dir / "main.puml"
        if main_puml.exists():
            content = main_puml.read_text()
            self.assertIn("class \"main\"", content)
            self.assertIn("class \"core\"", content)
            self.assertIn("class \"utils\"", content)
    
    def get_expected_file_count(self) -> int:
        """Get the expected number of files in the project"""
        return 5
    
    def get_expected_output_files(self) -> List[str]:
        """Get the expected output file names"""
        return ["main.puml", "core.puml", "utils.puml"]
    
    def get_expected_structs(self) -> Dict[str, List[str]]:
        """Get expected structs for each file"""
        return {}
    
    def get_expected_enums(self) -> Dict[str, List[str]]:
        """Get expected enums for each file"""
        return {}
    
    def get_expected_functions(self) -> Dict[str, List[str]]:
        """Get expected functions for each file"""
        return {
            "main.c": ["main"],
            "core.h": ["core_init", "core_cleanup", "core_create_object", "core_destroy_object"],
            "utils.h": ["util_init", "util_cleanup", "util_create_vector", "util_destroy_vector", "util_create_variant", "util_destroy_variant"]
        }
    
    def get_expected_typedefs(self) -> Dict[str, List[str]]:
        """Get expected typedefs for each file"""
        return {
            "core.h": ["CoreObject", "CoreStatus"],
            "utils.h": ["Vector3D", "Variant", "UtilResult"]
        }
    
    def get_expected_macros(self) -> Dict[str, List[str]]:
        """Get expected macros for each file"""
        return {}
    
    def get_expected_includes(self) -> Dict[str, List[str]]:
        """Get expected includes for each file"""
        return {
            "main.c": ["core.h", "utils.h"]
        }
    
    def get_expected_globals(self) -> Dict[str, List[str]]:
        """Get expected global variables for each file"""
        return {}
    
    def get_expected_unions(self) -> Dict[str, List[str]]:
        """Get expected unions for each file"""
        return {}
    
    def get_expected_plantuml_content(self) -> List[str]:
        """Get expected content that should appear in PlantUML output"""
        return [
            "class \"main\"",
            "class \"core\"",
            "class \"utils\""
        ]
    
    def get_expected_plantuml_classes(self) -> List[str]:
        """Get expected class names that should appear in PlantUML output"""
        return ["main", "core", "utils"]
    
    def get_expected_plantuml_relationships(self) -> List[str]:
        """Get expected relationships that should appear in PlantUML output"""
        return []