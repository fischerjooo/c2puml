#!/usr/bin/env python3
"""
Test expectations for error handling use case

This module defines the expected behavior and content for the error handling
use case, including file structure, content validation, and output verification.
"""

import os
import tempfile
from pathlib import Path
from typing import Dict, List
from .base_expectations import BaseExpectations
from c_to_plantuml.models import ProjectModel, FileModel


class ErrorHandlingExpectations(BaseExpectations):
    """Expectations for error handling use case"""
    
    def __init__(self):
        super().__init__("use_case_error_handling")
    
    def validate_project_structure(self, model: ProjectModel) -> None:
        """Validate the overall project structure"""
        # Should still parse the file
        self.assertIsNotNone(model)
        self.assertGreaterEqual(len(model.files), 1)
    
    def validate_file_content(self, model: ProjectModel) -> None:
        """Validate the content of individual files"""
        # Check that the file with missing include was parsed
        file_models = list(model.files.values())
        for file_model in file_models:
            if "missing_include.c" in file_model.file_path:
                self.assertEqual(len(file_model.functions), 1)
                break
    
    def validate_generated_output(self, output_dir: Path) -> None:
        """Validate the generated PlantUML output"""
        # Check that output was generated
        self.assertTrue(output_dir.exists())
        puml_files = list(output_dir.glob("*.puml"))
        self.assertGreater(len(puml_files), 0)
    
    def validate_encoding_detection_and_recovery(self, parser, temp_file: str) -> None:
        """Validate encoding detection and recovery"""
        # Parse the file
        file_model = parser.parse_file(Path(temp_file))
        
        # Should parse successfully
        self.assertIsNotNone(file_model)
        self.assertIn('TestStruct', file_model.structs)
        self.assertEqual(len(file_model.functions), 1)
    
    def validate_partial_parsing_on_errors(self, parser, invalid_file: Path) -> None:
        """Validate partial parsing when encountering errors"""
        if invalid_file.exists():
            # Parse the file
            file_model = parser.parse_file(invalid_file)
            
            # Should parse valid parts
            self.assertIsNotNone(file_model)
            self.assertIn('Valid', file_model.structs)
            # Invalid struct might be parsed with empty fields due to error recovery
            if 'Invalid' in file_model.structs:
                invalid_struct = file_model.structs['Invalid']
                # Should have empty fields due to parsing error
                self.assertEqual(len(invalid_struct.fields), 0)
            self.assertEqual(len(file_model.functions), 1)
    
    def validate_missing_file_handling(self, analyzer, project_dir: Path) -> None:
        """Validate handling of missing files"""
        # Should not crash
        model = analyzer.analyze_project(
            project_root=str(project_dir),
            recursive=True
        )
        
        # Should still parse the file
        self.assertIsNotNone(model)
        self.assertGreaterEqual(len(model.files), 1)
        
        # Check that the file with missing include was parsed
        file_models = list(model.files.values())
        for file_model in file_models:
            if "missing_include.c" in file_model.file_path:
                self.assertEqual(len(file_model.functions), 1)
                break
    
    def get_expected_file_count(self) -> int:
        """Get the expected number of files in the project"""
        return 1
    
    def get_expected_output_files(self) -> List[str]:
        """Get the expected output file names"""
        return ["missing_include.puml"]
    
    def get_expected_structs(self) -> Dict[str, List[str]]:
        """Get expected structs for each file"""
        return {
            "missing_include.c": ["Valid"]  # Invalid struct might not be parsed correctly
        }
    
    def get_expected_enums(self) -> Dict[str, List[str]]:
        """Get expected enums for each file"""
        return {}
    
    def get_expected_functions(self) -> Dict[str, List[str]]:
        """Get expected functions for each file"""
        return {
            "missing_include.c": ["main"]
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
            "missing_include.c": ["missing_header.h"]  # This include might fail
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
            "class \"missing_include\""
        ]
    
    def get_expected_plantuml_classes(self) -> List[str]:
        """Get expected class names that should appear in PlantUML output"""
        return ["missing_include"]
    
    def get_expected_plantuml_relationships(self) -> List[str]:
        """Get expected relationships that should appear in PlantUML output"""
        return []
    
    def create_test_file_content(self) -> str:
        """Create test file content for encoding detection test"""
        return """
#include <stdio.h>

struct TestStruct {
    int x;
    int y;
};

int main() {
    return 0;
}
"""