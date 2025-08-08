#!/usr/bin/env python3
"""
Validators for the unified testing framework

This module provides various validator classes for validating different
aspects of test outputs and CLI results.
"""

import os
import re
import json
from typing import Dict, List, Any, Optional
from .executor import CLIResult


class TestError(Exception):
    """Enhanced exception class for test framework errors with context"""
    def __init__(self, message: str, test_id: str = None, context: Dict = None):
        self.test_id = test_id
        self.context = context or {}
        super().__init__(f"Test '{test_id}' failed: {message}" if test_id else message)


class ModelValidator:
    """Validates c2puml generated model.json files and content"""
    
    def assert_model_structure_valid(self, model: dict) -> None:
        """Assert that model has valid structure"""
        required_keys = ["project_name", "files"]
        for key in required_keys:
            if key not in model:
                raise AssertionError(f"Model missing required key: {key}")
    
    def assert_model_schema_compliant(self, model: dict) -> None:
        """Assert that model complies with expected schema"""
        self.assert_model_structure_valid(model)
        
        # Validate files structure
        for filename, file_data in model.get("files", {}).items():
            if not isinstance(file_data, dict):
                raise AssertionError(f"File data for {filename} is not a dictionary")
            
            # Check for required file sections
            required_sections = ["functions", "structs", "enums", "aliases", "globals", "macros", "includes"]
            for section in required_sections:
                if section not in file_data:
                    raise AssertionError(f"File {filename} missing required section: {section}")
    
    def assert_model_project_name(self, model: dict, expected_name: str) -> None:
        """Assert that model has expected project name"""
        actual_name = model.get("project_name", "")
        if actual_name != expected_name:
            raise AssertionError(f"Expected project name '{expected_name}', got '{actual_name}'")
    
    def assert_model_file_count(self, model: dict, expected_count: int) -> None:
        """Assert that model has expected number of files"""
        actual_count = len(model.get("files", {}))
        if actual_count != expected_count:
            raise AssertionError(f"Expected {expected_count} files, got {actual_count}")
    
    def assert_model_files_parsed(self, model: dict, expected_files: List[str]) -> None:
        """Assert that specific files were parsed"""
        actual_files = list(model.get("files", {}).keys())
        for expected_file in expected_files:
            if expected_file not in actual_files:
                raise AssertionError(f"Expected file '{expected_file}' not found in parsed files")
    
    def assert_model_function_exists(self, model: dict, func_name: str) -> None:
        """Assert that a function exists in the model"""
        for file_data in model.get("files", {}).values():
            functions = file_data.get("functions", [])
            for func in functions:
                if func.get("name") == func_name:
                    return
        raise AssertionError(f"Function '{func_name}' not found in model")
    
    def assert_model_function_not_exists(self, model: dict, func_name: str) -> None:
        """Assert that a function does not exist in the model"""
        for file_data in model.get("files", {}).values():
            functions = file_data.get("functions", [])
            for func in functions:
                if func.get("name") == func_name:
                    raise AssertionError(f"Function '{func_name}' found in model but should not exist")
    
    def assert_model_struct_exists(self, model: dict, struct_name: str) -> None:
        """Assert that a struct exists in the model"""
        for file_data in model.get("files", {}).values():
            structs = file_data.get("structs", {})
            if struct_name in structs:
                return
        raise AssertionError(f"Struct '{struct_name}' not found in model")
    
    def assert_model_struct_not_exists(self, model: dict, struct_name: str) -> None:
        """Assert that a struct does not exist in the model"""
        for file_data in model.get("files", {}).values():
            structs = file_data.get("structs", {})
            if struct_name in structs:
                raise AssertionError(f"Struct '{struct_name}' found in model but should not exist")
    
    def assert_model_enum_exists(self, model: dict, enum_name: str) -> None:
        """Assert that an enum exists in the model"""
        for file_data in model.get("files", {}).values():
            enums = file_data.get("enums", {})
            if enum_name in enums:
                return
        raise AssertionError(f"Enum '{enum_name}' not found in model")
    
    def assert_model_enum_not_exists(self, model: dict, enum_name: str) -> None:
        """Assert that an enum does not exist in the model"""
        for file_data in model.get("files", {}).values():
            enums = file_data.get("enums", {})
            if enum_name in enums:
                raise AssertionError(f"Enum '{enum_name}' found in model but should not exist")
    
    def assert_model_typedef_exists(self, model: dict, typedef_name: str) -> None:
        """Assert that a typedef exists in the model"""
        for file_data in model.get("files", {}).values():
            typedefs = file_data.get("typedefs", {})
            if typedef_name in typedefs:
                return
        raise AssertionError(f"Typedef '{typedef_name}' not found in model")
    
    def assert_model_global_exists(self, model: dict, global_name: str) -> None:
        """Assert that a global variable exists in the model"""
        for file_data in model.get("files", {}).values():
            globals_list = file_data.get("globals", [])
            for global_var in globals_list:
                if global_var.get("name") == global_name:
                    return
        raise AssertionError(f"Global variable '{global_name}' not found in model")
    
    def assert_model_macro_exists(self, model: dict, macro_name: str) -> None:
        """Assert that a macro exists in the model"""
        for file_data in model.get("files", {}).values():
            macros = file_data.get("macros", [])
            for macro in macros:
                if macro_name in macro:  # Macros might be stored with full definition
                    return
        raise AssertionError(f"Macro '{macro_name}' not found in model")
    
    def assert_model_includes_exist(self, model: dict, expected_includes: List[str]) -> None:
        """Assert that specific includes exist in the model"""
        for file_data in model.get("files", {}).values():
            includes = file_data.get("includes", [])
            for expected_include in expected_includes:
                if expected_include not in includes:
                    raise AssertionError(f"Include '{expected_include}' not found in model")
            return
        raise AssertionError("No files found in model")
    
    def assert_model_include_exists(self, model: dict, include_name: str) -> None:
        """Assert that a specific include exists in the model"""
        self.assert_model_includes_exist(model, [include_name])
    
    def assert_model_struct_fields(self, model: dict, struct_name: str, expected_fields: List[str]) -> None:
        """Assert that a struct has specific fields"""
        for file_data in model.get("files", {}).values():
            structs = file_data.get("structs", {})
            if struct_name in structs:
                struct = structs[struct_name]
                fields = struct.get("fields", [])
                actual_field_names = [field.get("name") for field in fields]
                for expected_field in expected_fields:
                    if expected_field not in actual_field_names:
                        raise AssertionError(f"Field '{expected_field}' not found in struct '{struct_name}'")
                return
        raise AssertionError(f"Struct '{struct_name}' not found in model")
    
    def assert_model_enum_values(self, model: dict, enum_name: str, expected_values: List[str]) -> None:
        """Assert that an enum has specific values"""
        for file_data in model.get("files", {}).values():
            enums = file_data.get("enums", {})
            if enum_name in enums:
                enum = enums[enum_name]
                values = enum.get("values", [])
                actual_value_names = [value.get("name") for value in values]
                for expected_value in expected_values:
                    if expected_value not in actual_value_names:
                        raise AssertionError(f"Value '{expected_value}' not found in enum '{enum_name}'")
                return
        raise AssertionError(f"Enum '{enum_name}' not found in model")
    
    def assert_model_element_count(self, model: dict, element_type: str, expected_count: int) -> None:
        """Assert that a specific element type has expected count across all files"""
        total_count = 0
        for file_data in model.get("files", {}).values():
            if element_type == "functions":
                total_count += len(file_data.get("functions", []))
            elif element_type == "structs":
                total_count += len(file_data.get("structs", {}))
            elif element_type == "enums":
                total_count += len(file_data.get("enums", {}))
            elif element_type == "globals":
                total_count += len(file_data.get("globals", []))
            elif element_type == "includes":
                total_count += len(file_data.get("includes", []))
            elif element_type == "macros":
                total_count += len(file_data.get("macros", []))
            elif element_type == "unions":
                total_count += len(file_data.get("unions", {}))
            elif element_type == "aliases":
                total_count += len(file_data.get("aliases", {}))
        
        if total_count != expected_count:
            raise AssertionError(f"Expected {expected_count} {element_type}, got {total_count}")


class PlantUMLValidator:
    """Validates generated PlantUML files and diagram content"""
    
    def assert_puml_file_exists(self, output_dir: str, filename: str) -> None:
        """Assert that a PlantUML file exists"""
        file_path = os.path.join(output_dir, filename)
        if not os.path.exists(file_path):
            raise AssertionError(f"PlantUML file not found: {file_path}")
    
    def assert_puml_file_count(self, output_dir: str, expected_count: int) -> None:
        """Assert that expected number of PlantUML files exist"""
        puml_files = glob.glob(os.path.join(output_dir, "*.puml"))
        actual_count = len(puml_files)
        if actual_count != expected_count:
            raise AssertionError(f"Expected {expected_count} PlantUML files, got {actual_count}")
    
    def assert_puml_start_end_tags(self, puml_content: str) -> None:
        """Assert that PlantUML content has proper start/end tags"""
        if "@startuml" not in puml_content:
            raise AssertionError("PlantUML content missing @startuml tag")
        if "@enduml" not in puml_content:
            raise AssertionError("PlantUML content missing @enduml tag")
    
    def assert_puml_start_end_tags_multi(self, puml_files: Dict[str, str]) -> None:
        """Assert that all PlantUML files have proper start/end tags"""
        for filename, content in puml_files.items():
            try:
                self.assert_puml_start_end_tags(content)
            except AssertionError as e:
                raise AssertionError(f"File {filename}: {str(e)}")
    
    def assert_puml_contains(self, puml_content: str, expected_text: str) -> None:
        """Assert that PlantUML content contains specific text"""
        if expected_text not in puml_content:
            raise AssertionError(f"PlantUML content missing expected text: '{expected_text}'")
    
    def assert_puml_contains_multi(self, puml_files: Dict[str, str], expected_text: str) -> None:
        """Assert that at least one PlantUML file contains specific text"""
        for filename, content in puml_files.items():
            if expected_text in content:
                return  # Found in at least one file
        raise AssertionError(f"Expected text '{expected_text}' not found in any PlantUML file")
    
    def assert_puml_not_contains(self, puml_content: str, forbidden_text: str) -> None:
        """Assert that PlantUML content does not contain specific text"""
        if forbidden_text in puml_content:
            raise AssertionError(f"PlantUML content contains forbidden text: '{forbidden_text}'")
    
    def assert_puml_not_contains_multi(self, puml_files: Dict[str, str], forbidden_text: str) -> None:
        """Assert that no PlantUML file contains specific text"""
        for filename, content in puml_files.items():
            if forbidden_text in content:
                raise AssertionError(f"File {filename} contains forbidden text: '{forbidden_text}'")
    
    def assert_puml_contains_lines(self, puml_content: str, expected_lines: List[str]) -> None:
        """Assert that PlantUML content contains specific lines"""
        for expected_line in expected_lines:
            if expected_line not in puml_content:
                raise AssertionError(f"PlantUML content missing expected line: '{expected_line}'")
    
    def assert_puml_contains_lines_multi(self, puml_files: Dict[str, str], expected_lines: List[str]) -> None:
        """Assert that at least one PlantUML file contains all specific lines"""
        for filename, content in puml_files.items():
            try:
                self.assert_puml_contains_lines(content, expected_lines)
                return  # Found in this file
            except AssertionError:
                continue  # Try next file
        raise AssertionError(f"Expected lines not found in any PlantUML file: {expected_lines}")
    
    def assert_puml_line_count(self, puml_content: str, expected_count: int) -> None:
        """Assert that PlantUML content has expected number of lines"""
        actual_count = len(puml_content.splitlines())
        if actual_count != expected_count:
            raise AssertionError(f"Expected {expected_count} lines, got {actual_count}")
    
    def assert_puml_line_count_multi(self, puml_files: Dict[str, str], expected_count: int) -> None:
        """Assert that total lines across all PlantUML files equals expected count"""
        total_lines = sum(len(content.splitlines()) for content in puml_files.values())
        if total_lines != expected_count:
            raise AssertionError(f"Expected {expected_count} total lines across all files, got {total_lines}")
    
    def assert_puml_class_exists(self, puml_content: str, class_name: str, stereotype: str = None) -> None:
        """Assert that a class exists in PlantUML content"""
        class_pattern = rf'class\s+"[^"]*"\s+as\s+{re.escape(class_name)}'
        if not re.search(class_pattern, puml_content, re.IGNORECASE):
            raise AssertionError(f"Class '{class_name}' not found in PlantUML content")
        
        if stereotype:
            stereotype_pattern = rf'class\s+"[^"]*"\s+as\s+{re.escape(class_name)}[^<]*<<{re.escape(stereotype)}>>'
            if not re.search(stereotype_pattern, puml_content, re.IGNORECASE):
                raise AssertionError(f"Class '{class_name}' missing stereotype '{stereotype}'")
    
    def assert_puml_class_exists_multi(self, puml_files: Dict[str, str], class_name: str, stereotype: str = None) -> None:
        """Assert that a class exists in at least one PlantUML file"""
        for filename, content in puml_files.items():
            try:
                self.assert_puml_class_exists(content, class_name, stereotype)
                return  # Found in this file
            except AssertionError:
                continue  # Try next file
        raise AssertionError(f"Class '{class_name}' not found in any PlantUML file")
    
    def assert_puml_class_count(self, puml_content: str, expected_count: int) -> None:
        """Assert that PlantUML content has expected number of classes"""
        class_matches = re.findall(r'class\s+"[^"]*"\s+as\s+\w+', puml_content, re.IGNORECASE)
        actual_count = len(class_matches)
        if actual_count != expected_count:
            raise AssertionError(f"Expected {expected_count} classes, got {actual_count}")
    
    def assert_puml_class_count_multi(self, puml_files: Dict[str, str], expected_count: int) -> None:
        """Assert that total classes across all PlantUML files equals expected count"""
        total_classes = 0
        for content in puml_files.values():
            class_matches = re.findall(r'class\s+"[^"]*"\s+as\s+\w+', content, re.IGNORECASE)
            total_classes += len(class_matches)
        
        if total_classes != expected_count:
            raise AssertionError(f"Expected {expected_count} total classes across all files, got {total_classes}")
    
    def assert_puml_relationship(self, puml_content: str, source: str, target: str, rel_type: str) -> None:
        """Assert that a relationship exists in PlantUML content"""
        rel_pattern = rf'{re.escape(source)}\s+{re.escape(rel_type)}\s+{re.escape(target)}'
        if not re.search(rel_pattern, puml_content, re.IGNORECASE):
            raise AssertionError(f"Relationship '{source} {rel_type} {target}' not found in PlantUML content")
    
    def assert_puml_relationship_multi(self, puml_files: Dict[str, str], source: str, target: str, rel_type: str) -> None:
        """Assert that a relationship exists in at least one PlantUML file"""
        for filename, content in puml_files.items():
            try:
                self.assert_puml_relationship(content, source, target, rel_type)
                return  # Found in this file
            except AssertionError:
                continue  # Try next file
        raise AssertionError(f"Relationship '{source} {rel_type} {target}' not found in any PlantUML file")
    
    def assert_puml_relationship_count(self, puml_content: str, expected_count: int) -> None:
        """Assert that PlantUML content has expected number of relationships"""
        # Count various relationship types
        rel_patterns = [
            r'\w+\s+-->\s+\w+',  # arrows
            r'\w+\s+\.\.>\s+\w+',  # dotted arrows
            r'\w+\s+\*--\s+\w+',  # composition
            r'\w+\s+o--\s+\w+',   # aggregation
        ]
        
        total_relationships = 0
        for pattern in rel_patterns:
            matches = re.findall(pattern, puml_content, re.IGNORECASE)
            total_relationships += len(matches)
        
        if total_relationships != expected_count:
            raise AssertionError(f"Expected {expected_count} relationships, got {total_relationships}")
    
    def assert_puml_relationship_count_multi(self, puml_files: Dict[str, str], expected_count: int) -> None:
        """Assert that total relationships across all PlantUML files equals expected count"""
        total_relationships = 0
        rel_patterns = [
            r'\w+\s+-->\s+\w+',  # arrows
            r'\w+\s+\.\.>\s+\w+',  # dotted arrows
            r'\w+\s+\*--\s+\w+',  # composition
            r'\w+\s+o--\s+\w+',   # aggregation
        ]
        
        for content in puml_files.values():
            for pattern in rel_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                total_relationships += len(matches)
        
        if total_relationships != expected_count:
            raise AssertionError(f"Expected {expected_count} total relationships across all files, got {total_relationships}")


class OutputValidator:
    """Validates general output files, directories, and content"""
    
    def assert_output_dir_exists(self, output_path: str) -> None:
        """Assert that output directory exists"""
        if not os.path.exists(output_path):
            raise AssertionError(f"Output directory does not exist: {output_path}")
        if not os.path.isdir(output_path):
            raise AssertionError(f"Output path is not a directory: {output_path}")
    
    def assert_file_exists(self, file_path: str) -> None:
        """Assert that a file exists"""
        if not os.path.exists(file_path):
            raise AssertionError(f"File does not exist: {file_path}")
    
    def assert_file_not_exists(self, file_path: str) -> None:
        """Assert that a file does not exist"""
        if os.path.exists(file_path):
            raise AssertionError(f"File exists but should not: {file_path}")
    
    def assert_directory_empty(self, dir_path: str) -> None:
        """Assert that a directory is empty"""
        if not os.path.exists(dir_path):
            raise AssertionError(f"Directory does not exist: {dir_path}")
        
        files = os.listdir(dir_path)
        if files:
            raise AssertionError(f"Directory is not empty: {dir_path} contains {files}")
    
    def assert_directory_not_empty(self, dir_path: str) -> None:
        """Assert that a directory is not empty"""
        if not os.path.exists(dir_path):
            raise AssertionError(f"Directory does not exist: {dir_path}")
        
        files = os.listdir(dir_path)
        if not files:
            raise AssertionError(f"Directory is empty: {dir_path}")
    
    def assert_file_contains(self, file_path: str, expected_text: str) -> None:
        """Assert that a file contains specific text"""
        if not os.path.exists(file_path):
            raise AssertionError(f"File does not exist: {file_path}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        if expected_text not in content:
            raise AssertionError(f"File '{file_path}' missing expected text: '{expected_text}'")
    
    def assert_file_not_contains(self, file_path: str, forbidden_text: str) -> None:
        """Assert that a file does not contain specific text"""
        if not os.path.exists(file_path):
            raise AssertionError(f"File does not exist: {file_path}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        if forbidden_text in content:
            raise AssertionError(f"File '{file_path}' contains forbidden text: '{forbidden_text}'")
    
    def assert_file_contains_lines(self, file_path: str, expected_lines: List[str]) -> None:
        """Assert that a file contains specific lines"""
        if not os.path.exists(file_path):
            raise AssertionError(f"File does not exist: {file_path}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        for expected_line in expected_lines:
            if expected_line not in content:
                raise AssertionError(f"File '{file_path}' missing expected line: '{expected_line}'")
    
    def assert_file_line_count(self, file_path: str, expected_count: int) -> None:
        """Assert that a file has expected number of lines"""
        if not os.path.exists(file_path):
            raise AssertionError(f"File does not exist: {file_path}")
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        actual_count = len(lines)
        if actual_count != expected_count:
            raise AssertionError(f"File '{file_path}' expected {expected_count} lines, got {actual_count}")
    
    def assert_file_empty(self, file_path: str) -> None:
        """Assert that a file is empty"""
        if not os.path.exists(file_path):
            raise AssertionError(f"File does not exist: {file_path}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        if content.strip():
            raise AssertionError(f"File '{file_path}' is not empty")
    
    def assert_file_not_empty(self, file_path: str) -> None:
        """Assert that a file is not empty"""
        if not os.path.exists(file_path):
            raise AssertionError(f"File does not exist: {file_path}")
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        if not content.strip():
            raise AssertionError(f"File '{file_path}' is empty")
    
    def assert_log_contains(self, log_content: str, expected_message: str) -> None:
        """Assert that log content contains specific message"""
        if expected_message not in log_content:
            raise AssertionError(f"Log missing expected message: '{expected_message}'")
    
    def assert_log_no_errors(self, log_content: str) -> None:
        """Assert that log content contains no error messages"""
        error_patterns = ["ERROR", "FATAL", "Exception", "Traceback"]
        for pattern in error_patterns:
            if pattern in log_content:
                raise AssertionError(f"Log contains error pattern: '{pattern}'")
    
    def assert_log_no_warnings(self, log_content: str) -> None:
        """Assert that log content contains no warnings"""
        warning_patterns = [r'WARNING', r'Warning', r'warning']
        for pattern in warning_patterns:
            if re.search(pattern, log_content):
                raise AssertionError(f"Log contains warnings: {log_content}")
    
    # === C2PUML Output Specific Assertions ===
    
    def assert_model_file_exists(self, output_dir: str) -> str:
        """
        Assert that model.json file exists and return its path.
        Prefers model_transformed.json if it exists, otherwise uses model.json
        
        Args:
            output_dir: Output directory to check
            
        Returns:
            Path to the model.json or model_transformed.json file
        """
        # Check for transformed model first (for tests that use transformations)
        transformed_model_file = os.path.join(output_dir, "model_transformed.json")
        if os.path.exists(transformed_model_file):
            model_file = transformed_model_file
        else:
            model_file = os.path.join(output_dir, "model.json")
        
        self.assert_file_exists(model_file)
        return model_file
    
    def assert_transformed_model_file_exists(self, output_dir: str) -> str:
        """
        Assert that model_transformed.json file exists and return its path
        
        Args:
            output_dir: Output directory to check
            
        Returns:
            Path to the model_transformed.json file
        """
        transformed_model_file = os.path.join(output_dir, "model_transformed.json")
        self.assert_file_exists(transformed_model_file)
        return transformed_model_file
    
    def assert_puml_files_exist(self, output_dir: str, min_count: int = 1) -> list:
        """
        Assert that PlantUML files exist and return their paths
        
        Args:
            output_dir: Output directory to check
            min_count: Minimum number of .puml files expected
            
        Returns:
            List of paths to .puml files
        """
        if not os.path.exists(output_dir):
            raise AssertionError(f"Output directory does not exist: {output_dir}")
        
        puml_files = [f for f in os.listdir(output_dir) if f.endswith('.puml')]
        if len(puml_files) < min_count:
            raise AssertionError(f"Expected at least {min_count} .puml files, found {len(puml_files)}")
        
        return [os.path.join(output_dir, f) for f in puml_files]


class FileValidator:
    """Advanced file validation and manipulation utilities"""
    
    def assert_files_equal(self, file1_path: str, file2_path: str) -> None:
        """Assert that two files have identical content"""
        if not os.path.exists(file1_path):
            raise AssertionError(f"File 1 does not exist: {file1_path}")
        if not os.path.exists(file2_path):
            raise AssertionError(f"File 2 does not exist: {file2_path}")
        
        with open(file1_path, 'r') as f1, open(file2_path, 'r') as f2:
            content1 = f1.read()
            content2 = f2.read()
        
        if content1 != content2:
            raise AssertionError(f"Files '{file1_path}' and '{file2_path}' have different content")
    
    def assert_json_valid(self, json_file_path: str) -> None:
        """Assert that a file contains valid JSON"""
        if not os.path.exists(json_file_path):
            raise AssertionError(f"JSON file does not exist: {json_file_path}")
        
        try:
            with open(json_file_path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            raise AssertionError(f"Invalid JSON in file '{json_file_path}': {e}")
    
    def assert_file_valid_utf8(self, file_path: str) -> None:
        """Assert that a file is valid UTF-8"""
        if not os.path.exists(file_path):
            raise AssertionError(f"File does not exist: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read()
        except UnicodeDecodeError as e:
            raise AssertionError(f"File '{file_path}' is not valid UTF-8: {e}")
    
    def assert_file_no_trailing_whitespace(self, file_path: str) -> None:
        """Assert that a file has no trailing whitespace"""
        if not os.path.exists(file_path):
            raise AssertionError(f"File does not exist: {file_path}")
        
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line:
                raise AssertionError(f"File '{file_path}' line {i} has trailing whitespace")
    
    def assert_execution_time_under(self, actual_time: float, max_time: float) -> None:
        """Assert that execution time is under the specified maximum"""
        if actual_time > max_time:
            raise AssertionError(f"Execution time {actual_time:.2f}s exceeds maximum {max_time:.2f}s")


class CLIValidator:
    """Validates CLI execution results and behavior"""
    
    def assert_cli_success(self, result: CLIResult, message: str = None) -> None:
        """
        Assert that CLI execution was successful
        
        Args:
            result: CLIResult from CLI execution
            message: Optional custom error message
        """
        if result.exit_code != 0:
            error_msg = message or f"CLI execution failed with exit code {result.exit_code}"
            if result.stderr:
                error_msg += f"\nStderr: {result.stderr}"
            raise TestError(error_msg, context={"exit_code": result.exit_code, "stderr": result.stderr})
    
    def assert_cli_failure(self, result: CLIResult, expected_error: str = None, message: str = None) -> None:
        """
        Assert that CLI execution failed
        
        Args:
            result: CLIResult from CLI execution
            expected_error: Optional expected error message to check for
            message: Optional custom error message
        """
        if result.exit_code == 0:
            error_msg = message or "CLI execution succeeded when failure was expected"
            raise TestError(error_msg, context={"exit_code": result.exit_code, "stdout": result.stdout})
        
        if expected_error and expected_error not in result.stderr:
            error_msg = f"Expected error '{expected_error}' not found in stderr: {result.stderr}"
            raise TestError(error_msg, context={"exit_code": result.exit_code, "stderr": result.stderr})
    
    def assert_cli_exit_code(self, result: CLIResult, expected_exit_code: int) -> None:
        """Assert that CLI execution returned expected exit code"""
        if result.exit_code != expected_exit_code:
            raise TestError(f"Expected exit code {expected_exit_code}, got {result.exit_code}", 
                          context={"exit_code": result.exit_code, "expected_exit_code": expected_exit_code})
    
    def assert_cli_stdout_contains(self, result: CLIResult, expected_text: str) -> None:
        """Assert that CLI stdout contains expected text"""
        if expected_text not in result.stdout:
            raise TestError(f"Expected text '{expected_text}' not found in stdout: {result.stdout}",
                          context={"stdout": result.stdout, "expected_text": expected_text})
    
    def assert_cli_stderr_contains(self, result: CLIResult, expected_text: str) -> None:
        """Assert that CLI stderr contains expected text"""
        if expected_text not in result.stderr:
            raise TestError(f"Expected text '{expected_text}' not found in stderr: {result.stderr}",
                          context={"stderr": result.stderr, "expected_text": expected_text})
    
    def assert_cli_execution_time_under(self, result: CLIResult, max_time: float) -> None:
        """Assert that CLI execution time is under the specified maximum"""
        if result.execution_time > max_time:
            raise TestError(f"Execution time {result.execution_time:.2f}s exceeds maximum {max_time:.2f}s",
                          context={"execution_time": result.execution_time, "max_time": max_time})