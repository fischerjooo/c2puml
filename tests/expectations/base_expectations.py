#!/usr/bin/env python3
"""
Base class for test expectations

This module provides a base class that defines the interface for all
example test expectations. Each example should have its own expectations
file that inherits from this base class.
"""

import unittest
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from pathlib import Path
from c_to_plantuml.models import ProjectModel, FileModel


class BaseExpectations(unittest.TestCase, ABC):
    """Base class for test expectations"""
    
    def __init__(self, example_name: str):
        self.example_name = example_name
        super().__init__()
    
    @abstractmethod
    def validate_project_structure(self, model: ProjectModel) -> None:
        """Validate the overall project structure"""
        pass
    
    @abstractmethod
    def validate_file_content(self, model: ProjectModel) -> None:
        """Validate the content of individual files"""
        pass
    
    @abstractmethod
    def validate_generated_output(self, output_dir: Path) -> None:
        """Validate the generated PlantUML output"""
        pass
    
    def get_expected_file_count(self) -> int:
        """Get the expected number of files in the project"""
        return 0
    
    def get_expected_output_files(self) -> List[str]:
        """Get the expected output file names"""
        return []
    
    def get_expected_structs(self) -> Dict[str, List[str]]:
        """Get expected structs for each file"""
        return {}
    
    def get_expected_enums(self) -> Dict[str, List[str]]:
        """Get expected enums for each file"""
        return {}
    
    def get_expected_functions(self) -> Dict[str, List[str]]:
        """Get expected functions for each file"""
        return {}
    
    def get_expected_typedefs(self) -> Dict[str, List[str]]:
        """Get expected typedefs for each file"""
        return {}
    
    def get_expected_macros(self) -> Dict[str, List[str]]:
        """Get expected macros for each file"""
        return {}
    
    def get_expected_includes(self) -> Dict[str, List[str]]:
        """Get expected includes for each file"""
        return {}
    
    def get_expected_globals(self) -> Dict[str, List[str]]:
        """Get expected global variables for each file"""
        return {}
    
    def get_expected_unions(self) -> Dict[str, List[str]]:
        """Get expected unions for each file"""
        return {}
    
    def get_expected_plantuml_content(self) -> List[str]:
        """Get expected content that should appear in PlantUML output"""
        return []
    
    def get_expected_plantuml_classes(self) -> List[str]:
        """Get expected class names that should appear in PlantUML output"""
        return []
    
    def get_expected_plantuml_relationships(self) -> List[str]:
        """Get expected relationships that should appear in PlantUML output"""
        return []