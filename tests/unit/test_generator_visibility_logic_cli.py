#!/usr/bin/env python3
"""
Test Generator Visibility Logic Through CLI Interface
"""
import os
import sys
import unittest
import json
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase

class TestGeneratorVisibilityLogicCLI(UnifiedTestCase):
    """Test generator visibility logic through the CLI interface"""
    
    def test_function_visibility_public_when_in_header(self):
        """Test that functions present in headers are marked as + (public)"""
        test_data = self.data_loader.load_test_data("generator_visibility_logic_public_functions")
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "generator_visibility_logic_public_functions")
        temp_dir = os.path.dirname(source_dir)
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy model to expected output location
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
    
    def test_function_visibility_private_when_not_in_header(self):
        """Test that functions not present in headers are marked as - (private)"""
        test_data = self.data_loader.load_test_data("generator_visibility_logic_private_functions")
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "generator_visibility_logic_private_functions")
        temp_dir = os.path.dirname(source_dir)
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy model to expected output location
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
    
    def test_global_visibility_public_when_in_header(self):
        """Test that globals present in headers are marked as + (public)"""
        test_data = self.data_loader.load_test_data("generator_visibility_logic_public_globals")
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "generator_visibility_logic_public_globals")
        temp_dir = os.path.dirname(source_dir)
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy model to expected output location
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
    
    def test_global_visibility_private_when_not_in_header(self):
        """Test that globals not present in headers are marked as - (private)"""
        test_data = self.data_loader.load_test_data("generator_visibility_logic_private_globals")
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "generator_visibility_logic_private_globals")
        temp_dir = os.path.dirname(source_dir)
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy model to expected output location
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
    
    def test_mixed_visibility_comprehensive(self):
        """Test mixed visibility scenarios with both public and private elements"""
        test_data = self.data_loader.load_test_data("generator_visibility_logic_mixed_visibility")
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "generator_visibility_logic_mixed_visibility")
        temp_dir = os.path.dirname(source_dir)
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy model to expected output location
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
    
    def test_no_headers_all_private(self):
        """Test that without headers, all elements are marked as - (private)"""
        test_data = self.data_loader.load_test_data("generator_visibility_logic_no_headers")
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "generator_visibility_logic_no_headers")
        temp_dir = os.path.dirname(source_dir)
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy model to expected output location
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

if __name__ == '__main__':
    unittest.main()