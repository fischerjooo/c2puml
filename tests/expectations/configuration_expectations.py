#!/usr/bin/env python3
"""
Test expectations for configuration use case

This module defines the expected behavior and content for the configuration
use case, including file structure, content validation, and output verification.
"""

from pathlib import Path
from typing import Dict, List
from .base_expectations import BaseExpectations
from c_to_plantuml.models import ProjectModel, FileModel


class ConfigurationExpectations(BaseExpectations):
    """Expectations for configuration use case"""
    
    def __init__(self):
        super().__init__("use_case_configuration")
    
    def validate_project_structure(self, model: ProjectModel) -> None:
        """Validate the overall project structure"""
        # Check that the model was created successfully
        self.assertIsNotNone(model)
        self.assertGreater(len(model.files), 0)
        
        # Check that main.c was parsed
        self.assertIn("main.c", model.files)
        main_c_model = model.files["main.c"]
        
        # Should include public elements
        self.assertIn('PublicStruct', main_c_model.structs)
        self.assertIn('public_function', [f.name for f in main_c_model.functions])
        self.assertIn('global_public_var', [g.name for g in main_c_model.globals])
    
    def validate_file_content(self, model: ProjectModel) -> None:
        """Validate the content of individual files"""
        # This is handled in validate_project_structure for this use case
        pass
    
    def validate_generated_output(self, output_dir: Path) -> None:
        """Validate the generated PlantUML output"""
        # Check that output was generated
        self.assertTrue(output_dir.exists())
        puml_files = list(output_dir.glob("*.puml"))
        self.assertGreater(len(puml_files), 0)
    
    def get_expected_file_count(self) -> int:
        """Get the expected number of files in the project"""
        return 3
    
    def get_expected_output_files(self) -> List[str]:
        """Get the expected output file names"""
        return ["main.puml"]
    
    def get_expected_structs(self) -> Dict[str, List[str]]:
        """Get expected structs for each file"""
        return {
            "main.c": ["PublicStruct"]  # InternalStruct should be filtered out
        }
    
    def get_expected_enums(self) -> Dict[str, List[str]]:
        """Get expected enums for each file"""
        return {}
    
    def get_expected_functions(self) -> Dict[str, List[str]]:
        """Get expected functions for each file"""
        return {
            "main.c": ["public_function"]  # internal_function should be filtered out
        }
    
    def get_expected_typedefs(self) -> Dict[str, List[str]]:
        """Get expected typedefs for each file"""
        return {}
    
    def get_expected_macros(self) -> Dict[str, List[str]]:
        """Get expected macros for each file"""
        return {}
    
    def get_expected_includes(self) -> Dict[str, List[str]]:
        """Get expected includes for each file"""
        return {
            "main.c": ["public.h", "internal.h"]
        }
    
    def get_expected_globals(self) -> Dict[str, List[str]]:
        """Get expected global variables for each file"""
        return {
            "main.c": ["global_public_var"]  # global_internal_var should be filtered out
        }
    
    def get_expected_unions(self) -> Dict[str, List[str]]:
        """Get expected unions for each file"""
        return {}
    
    def get_expected_plantuml_content(self) -> List[str]:
        """Get expected content that should appear in PlantUML output"""
        return [
            "class \"main\"",
            "struct PublicStruct",
            "public_function"
        ]
    
    def get_expected_plantuml_classes(self) -> List[str]:
        """Get expected class names that should appear in PlantUML output"""
        return ["main", "public", "internal"]
    
    def get_expected_plantuml_relationships(self) -> List[str]:
        """Get expected relationships that should appear in PlantUML output"""
        return []
    
    def get_filtered_out_elements(self) -> Dict[str, List[str]]:
        """Get elements that should be filtered out by configuration"""
        return {
            "structs": ["InternalStruct"],
            "functions": ["internal_function"],
            "globals": ["global_internal_var"]
        }