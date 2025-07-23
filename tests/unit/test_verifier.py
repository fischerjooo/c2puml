#!/usr/bin/env python3
"""
Unit tests for the ModelVerifier class
"""

import unittest
import tempfile
import os
from pathlib import Path

from c_to_plantuml.verifier import ModelVerifier
from c_to_plantuml.models import (
    ProjectModel, FileModel, Field, Struct, Enum, Union, 
    Function, Alias, EnumValue
)


class TestModelVerifier(unittest.TestCase):
    """Test cases for ModelVerifier"""

    def setUp(self):
        """Set up test fixtures"""
        self.verifier = ModelVerifier()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_valid_model_passes_verification(self):
        """Test that a valid model passes verification"""
        # Create a valid model
        valid_field = Field(name="valid_field", type="int", value="42")
        valid_struct = Struct(name="valid_struct", fields=[valid_field])
        
        file_model = FileModel(
            file_path="/test/file.c",
            relative_path="file.c",
            project_root="/test",
            encoding_used="utf-8",
            structs={"valid_struct": valid_struct}
        )
        
        model = ProjectModel(
            project_name="TestProject",
            project_root="/test",
            files={"file.c": file_model}
        )
        
        is_valid, issues = self.verifier.verify_model(model)
        
        self.assertTrue(is_valid)
        self.assertEqual(len(issues), 0)

    def test_invalid_global_name_detected(self):
        """Test that invalid global variable names are detected"""
        # Create a global with invalid name (just a bracket)
        invalid_global = Field(name="]", type="int", value="42")
        
        file_model = FileModel(
            file_path="/test/file.c",
            relative_path="file.c",
            project_root="/test",
            encoding_used="utf-8",
            globals=[invalid_global]
        )
        
        model = ProjectModel(
            project_name="TestProject",
            project_root="/test",
            files={"file.c": file_model}
        )
        
        is_valid, issues = self.verifier.verify_model(model)
        
        self.assertFalse(is_valid)
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("Invalid field name ']'" in issue for issue in issues))

    def test_suspicious_type_detected(self):
        """Test that suspicious types are detected"""
        # Create a global with suspicious type (mostly brackets and whitespace)
        suspicious_global = Field(
            name="test_var", 
            type="{ \\ \n ( ptr_pau8 ) [ 3 U", 
            value="( uint8 ) ( value_u32 )"
        )
        
        file_model = FileModel(
            file_path="/test/file.c",
            relative_path="file.c",
            project_root="/test",
            encoding_used="utf-8",
            globals=[suspicious_global]
        )
        
        model = ProjectModel(
            project_name="TestProject",
            project_root="/test",
            files={"file.c": file_model}
        )
        
        is_valid, issues = self.verifier.verify_model(model)
        
        self.assertFalse(is_valid)
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("Suspicious field type" in issue for issue in issues))

    def test_suspicious_value_detected(self):
        """Test that suspicious values are detected"""
        # Create a global with suspicious value
        suspicious_global = Field(
            name="test_var", 
            type="int", 
            value="\\ \n } \n \n \n \n \n \n \n \n \n #define CRYPTO_PRV_UTILS_U16_TO_U8ARR_BIG_ENDIAN(value_u16, ptr_pau8) \\ \n { \\ \n ( ptr_pau8 ) [ 1 U"
        )
        
        file_model = FileModel(
            file_path="/test/file.c",
            relative_path="file.c",
            project_root="/test",
            encoding_used="utf-8",
            globals=[suspicious_global]
        )
        
        model = ProjectModel(
            project_name="TestProject",
            project_root="/test",
            files={"file.c": file_model}
        )
        
        is_valid, issues = self.verifier.verify_model(model)
        
        self.assertFalse(is_valid)
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("Suspicious field value" in issue for issue in issues))

    def test_empty_names_detected(self):
        """Test that empty names are detected"""
        # Create a struct with empty name by directly setting the attribute
        empty_struct = Struct(name="dummy", fields=[])
        empty_struct.name = ""  # Override the validation
        
        file_model = FileModel(
            file_path="/test/file.c",
            relative_path="file.c",
            project_root="/test",
            encoding_used="utf-8",
            structs={"": empty_struct}
        )
        
        model = ProjectModel(
            project_name="TestProject",
            project_root="/test",
            files={"file.c": file_model}
        )
        
        is_valid, issues = self.verifier.verify_model(model)
        
        self.assertFalse(is_valid)
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("Struct name is empty" in issue for issue in issues))

    def test_invalid_identifier_detected(self):
        """Test that invalid identifiers are detected"""
        # Create a struct with invalid name (starts with number)
        invalid_struct = Struct(name="123invalid", fields=[])
        
        file_model = FileModel(
            file_path="/test/file.c",
            relative_path="file.c",
            project_root="/test",
            encoding_used="utf-8",
            structs={"123invalid": invalid_struct}
        )
        
        model = ProjectModel(
            project_name="TestProject",
            project_root="/test",
            files={"file.c": file_model}
        )
        
        is_valid, issues = self.verifier.verify_model(model)
        
        self.assertFalse(is_valid)
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("Invalid struct name '123invalid'" in issue for issue in issues))

    def test_unbalanced_brackets_detected(self):
        """Test that unbalanced brackets are detected"""
        # Create a field with unbalanced brackets
        unbalanced_field = Field(name="test", type="int[10", value="42")
        
        file_model = FileModel(
            file_path="/test/file.c",
            relative_path="file.c",
            project_root="/test",
            encoding_used="utf-8",
            globals=[unbalanced_field]
        )
        
        model = ProjectModel(
            project_name="TestProject",
            project_root="/test",
            files={"file.c": file_model}
        )
        
        is_valid, issues = self.verifier.verify_model(model)
        
        self.assertFalse(is_valid)
        self.assertGreater(len(issues), 0)
        self.assertTrue(any("Suspicious field type" in issue for issue in issues))

    def test_valid_identifiers_pass(self):
        """Test that valid identifiers pass verification"""
        valid_identifiers = [
            "valid_name",
            "ValidName",
            "_valid_name",
            "valid123",
            "VALID_NAME",
            "validName"
        ]
        
        for identifier in valid_identifiers:
            with self.subTest(identifier=identifier):
                valid_field = Field(name=identifier, type="int")
                file_model = FileModel(
                    file_path="/test/file.c",
                    relative_path="file.c",
                    project_root="/test",
                    encoding_used="utf-8",
                    globals=[valid_field]
                )
                
                model = ProjectModel(
                    project_name="TestProject",
                    project_root="/test",
                    files={"file.c": file_model}
                )
                
                is_valid, issues = self.verifier.verify_model(model)
                self.assertTrue(is_valid, f"Valid identifier '{identifier}' failed verification")

    def test_invalid_identifiers_fail(self):
        """Test that invalid identifiers fail verification"""
        invalid_identifiers = [
            "123invalid",
            "invalid-name",
            "invalid.name",
            "invalid name",
            "]",
            "[",
            "{",
            "}",
            "(",
            ")"
        ]
        
        for identifier in invalid_identifiers:
            with self.subTest(identifier=identifier):
                # Create field with valid name first, then override
                invalid_field = Field(name="dummy", type="int")
                invalid_field.name = identifier  # Override the validation
                
                file_model = FileModel(
                    file_path="/test/file.c",
                    relative_path="file.c",
                    project_root="/test",
                    encoding_used="utf-8",
                    globals=[invalid_field]
                )
                
                model = ProjectModel(
                    project_name="TestProject",
                    project_root="/test",
                    files={"file.c": file_model}
                )
                
                is_valid, issues = self.verifier.verify_model(model)
                self.assertFalse(is_valid, f"Invalid identifier '{identifier}' passed verification")
                self.assertTrue(any("Invalid field name" in issue for issue in issues))

    def test_project_level_validation(self):
        """Test project-level validation"""
        # Test empty project name
        file_model = FileModel(
            file_path="/test/file.c",
            relative_path="file.c",
            project_root="/test",
            encoding_used="utf-8"
        )
        
        model = ProjectModel(
            project_name="TestProject",
            project_root="/test",
            files={"file.c": file_model}
        )
        model.project_name = ""  # Override the validation
        
        is_valid, issues = self.verifier.verify_model(model)
        self.assertFalse(is_valid)
        self.assertTrue(any("Project name is empty" in issue for issue in issues))

        # Test empty project root
        model = ProjectModel(
            project_name="TestProject",
            project_root="/test",
            files={"file.c": file_model}
        )
        model.project_root = ""  # Override the validation
        
        is_valid, issues = self.verifier.verify_model(model)
        self.assertFalse(is_valid)
        self.assertTrue(any("Project root is empty" in issue for issue in issues))

        # Test no files
        model = ProjectModel(
            project_name="TestProject",
            project_root="/test",
            files={}
        )
        
        is_valid, issues = self.verifier.verify_model(model)
        self.assertFalse(is_valid)
        self.assertTrue(any("No files found" in issue for issue in issues))


if __name__ == "__main__":
    unittest.main()