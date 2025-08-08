#!/usr/bin/env python3
"""
Test Generator New Formatting Through CLI Interface
"""
import os
import sys
import unittest
import json
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase

class TestGeneratorNewFormattingCLI(UnifiedTestCase):
    """Test the new PlantUML formatting rules through the CLI interface"""
    
    def test_enum_formatting_with_enumeration_stereotype(self):
        """Test that enum types use <<enumeration>> stereotype with #LightYellow"""
        test_data = self.data_loader.load_test_data("generator_new_formatting_cli_enum_stereotype")
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "generator_new_formatting_cli_enum_stereotype")
        temp_dir = os.path.dirname(source_dir)
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy model to expected output location for generate_only
        model_source = os.path.join(source_dir, "model.json")
        model_target = os.path.join(output_dir, "model.json")
        shutil.copy2(model_source, model_target)
        
        config_filename = os.path.basename(config_path)
        result = self.executor.run_generate_only(config_filename, temp_dir)
        self.cli_validator.assert_cli_success(result)
        
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files_dict[filename] = f.read()
        
        self.validators_processor.process_assertions(
            test_data["assertions"], {}, puml_files_dict, result, self
        )

    def test_struct_formatting_with_struct_stereotype(self):
        """Test that struct types use <<struct>> stereotype with + prefix for fields"""
        test_data = self.data_loader.load_test_data("generator_new_formatting_cli_struct_stereotype")
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "generator_new_formatting_cli_struct_stereotype")
        temp_dir = os.path.dirname(source_dir)
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy model to expected output location for generate_only
        model_source = os.path.join(source_dir, "model.json")
        model_target = os.path.join(output_dir, "model.json")
        shutil.copy2(model_source, model_target)
        
        config_filename = os.path.basename(config_path)
        result = self.executor.run_generate_only(config_filename, temp_dir)
        self.cli_validator.assert_cli_success(result)
        
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files_dict[filename] = f.read()
        
        self.validators_processor.process_assertions(
            test_data["assertions"], {}, puml_files_dict, result, self
        )

    def test_union_formatting_with_union_stereotype(self):
        """Test that union types use <<union>> stereotype with + prefix for fields"""
        test_data = self.data_loader.load_test_data("generator_new_formatting_cli_union_stereotype")
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "generator_new_formatting_cli_union_stereotype")
        temp_dir = os.path.dirname(source_dir)
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy model to expected output location for generate_only
        model_source = os.path.join(source_dir, "model.json")
        model_target = os.path.join(output_dir, "model.json")
        shutil.copy2(model_source, model_target)
        
        config_filename = os.path.basename(config_path)
        result = self.executor.run_generate_only(config_filename, temp_dir)
        self.cli_validator.assert_cli_success(result)
        
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files_dict[filename] = f.read()
        
        self.validators_processor.process_assertions(
            test_data["assertions"], {}, puml_files_dict, result, self
        )

    def test_alias_formatting_with_typedef_stereotype_and_alias_prefix(self):
        """Test that typedef aliases use <<typedef>> stereotype with ALIAS_ prefix"""
        test_data = self.data_loader.load_test_data("generator_new_formatting_cli_alias_stereotype")
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "generator_new_formatting_cli_alias_stereotype")
        temp_dir = os.path.dirname(source_dir)
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy model to expected output location for generate_only
        model_source = os.path.join(source_dir, "model.json")
        model_target = os.path.join(output_dir, "model.json")
        shutil.copy2(model_source, model_target)
        
        config_filename = os.path.basename(config_path)
        result = self.executor.run_generate_only(config_filename, temp_dir)
        self.cli_validator.assert_cli_success(result)
        
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files_dict[filename] = f.read()
        
        self.validators_processor.process_assertions(
            test_data["assertions"], {}, puml_files_dict, result, self
        )

    def test_function_pointer_formatting_with_function_pointer_stereotype(self):
        """Test that function pointer typedefs use <<function pointer>> stereotype"""
        test_data = self.data_loader.load_test_data("generator_new_formatting_cli_function_pointer")
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "generator_new_formatting_cli_function_pointer")
        temp_dir = os.path.dirname(source_dir)
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy model to expected output location for generate_only
        model_source = os.path.join(source_dir, "model.json")
        model_target = os.path.join(output_dir, "model.json")
        shutil.copy2(model_source, model_target)
        
        config_filename = os.path.basename(config_path)
        result = self.executor.run_generate_only(config_filename, temp_dir)
        self.cli_validator.assert_cli_success(result)
        
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files_dict[filename] = f.read()
        
        self.validators_processor.process_assertions(
            test_data["assertions"], {}, puml_files_dict, result, self
        )

    def test_complex_typedef_combination(self):
        """Test complex combination of struct, enum, union, and typedef in same file"""
        test_data = self.data_loader.load_test_data("generator_new_formatting_cli_complex_typedef")
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "generator_new_formatting_cli_complex_typedef")
        temp_dir = os.path.dirname(source_dir)
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy model to expected output location for generate_only
        model_source = os.path.join(source_dir, "model.json")
        model_target = os.path.join(output_dir, "model.json")
        shutil.copy2(model_source, model_target)
        
        config_filename = os.path.basename(config_path)
        result = self.executor.run_generate_only(config_filename, temp_dir)
        self.cli_validator.assert_cli_success(result)
        
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files_dict[filename] = f.read()
        
        self.validators_processor.process_assertions(
            test_data["assertions"], {}, puml_files_dict, result, self
        )

    def test_public_private_visibility_logic(self):
        """Test that globals and functions are marked as public if present in headers, private otherwise"""
        test_data = self.data_loader.load_test_data("generator_new_formatting_cli_visibility_logic")
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "generator_new_formatting_cli_visibility_logic")
        temp_dir = os.path.dirname(source_dir)
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy model to expected output location for generate_only
        model_source = os.path.join(source_dir, "model.json")
        model_target = os.path.join(output_dir, "model.json")
        shutil.copy2(model_source, model_target)
        
        config_filename = os.path.basename(config_path)
        result = self.executor.run_generate_only(config_filename, temp_dir)
        self.cli_validator.assert_cli_success(result)
        
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files_dict[filename] = f.read()
        
        self.validators_processor.process_assertions(
            test_data["assertions"], {}, puml_files_dict, result, self
        )

if __name__ == "__main__":
    unittest.main()