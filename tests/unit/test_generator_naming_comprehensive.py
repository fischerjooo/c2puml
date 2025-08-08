#!/usr/bin/env python3
"""
Test Generator Naming Conventions Through CLI Interface
"""

import os
import sys
import unittest
import json
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestGeneratorNamingComprehensive(UnifiedTestCase):
    """Test generator naming conventions through the CLI interface"""
    
    def test_generator_typedef_naming_conventions(self):
        """Test that typedef UML IDs follow the correct naming conventions"""
        # Load test data from YAML
        test_data = self.data_loader.load_test_data("generator_naming_comprehensive_typedef_conventions")
        
        # Create temporary files
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "generator_naming_comprehensive_typedef_conventions")
        
        # Get the temp directory (parent of source_dir)
        temp_dir = os.path.dirname(source_dir)
        
        # The TestDataLoader automatically sets config output_dir to "../output" which means
        # output will be at the same level as the input directory (where temp_dir is)
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy model.json from source to output directory (where CLI expects it)
        model_source = os.path.join(source_dir, "model.json")
        model_target = os.path.join(output_dir, "model.json")
        shutil.copy2(model_source, model_target)
        
        # Make config path relative to working directory (which will be temp_dir)
        config_filename = os.path.basename(config_path)
        
        # Execute c2puml with temp directory as working directory - generate only since we provide model.json
        result = self.executor.run_generate_only(config_filename, temp_dir)
        
        # Validate execution
        self.cli_validator.assert_cli_success(result)
        
        # Load output files
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        
        # Load all PlantUML files into a dictionary
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files_dict[filename] = f.read()
        
        # Process assertions from YAML
        self.validators_processor.process_assertions(
            test_data["assertions"], {}, puml_files_dict, result, self
        )

    def test_generator_file_naming_conventions(self):
        """Test that file UML IDs follow the correct naming conventions"""
        # Load test data from YAML
        test_data = self.data_loader.load_test_data("generator_naming_comprehensive_file_conventions")
        
        # Create temporary files
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "generator_naming_comprehensive_file_conventions")
        
        # Get the temp directory (parent of source_dir)
        temp_dir = os.path.dirname(source_dir)
        
        # The TestDataLoader automatically sets config output_dir to "../output"
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy model.json from source to output directory (where CLI expects it)
        model_source = os.path.join(source_dir, "model.json")
        model_target = os.path.join(output_dir, "model.json")
        shutil.copy2(model_source, model_target)
        
        # Make config path relative to working directory
        config_filename = os.path.basename(config_path)
        
        # Execute c2puml with temp directory as working directory - generate only since we provide model.json
        result = self.executor.run_generate_only(config_filename, temp_dir)
        
        # Validate execution
        self.cli_validator.assert_cli_success(result)
        
        # Load output files
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        
        # Load all PlantUML files into a dictionary
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files_dict[filename] = f.read()
        
        # Process assertions from YAML
        self.validators_processor.process_assertions(
            test_data["assertions"], {}, puml_files_dict, result, self
        )

    def test_generator_complex_typedef_names(self):
        """Test that complex typedef names are handled correctly"""
        # Load test data from YAML
        test_data = self.data_loader.load_test_data("generator_naming_comprehensive_complex_names")
        
        # Create temporary files
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "generator_naming_comprehensive_complex_names")
        
        # Get the temp directory (parent of source_dir)
        temp_dir = os.path.dirname(source_dir)
        
        # The TestDataLoader automatically sets config output_dir to "../output"
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy model.json from source to output directory (where CLI expects it)
        model_source = os.path.join(source_dir, "model.json")
        model_target = os.path.join(output_dir, "model.json")
        shutil.copy2(model_source, model_target)
        
        # Make config path relative to working directory
        config_filename = os.path.basename(config_path)
        
        # Execute c2puml with temp directory as working directory - generate only since we provide model.json
        result = self.executor.run_generate_only(config_filename, temp_dir)
        
        # Validate execution
        self.cli_validator.assert_cli_success(result)
        
        # Load output files
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        
        # Load all PlantUML files into a dictionary
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files_dict[filename] = f.read()
        
        # Process assertions from YAML
        self.validators_processor.process_assertions(
            test_data["assertions"], {}, puml_files_dict, result, self
        )

    def test_generator_edge_case_names(self):
        """Test edge cases in naming conventions"""
        # Load test data from YAML
        test_data = self.data_loader.load_test_data("generator_naming_comprehensive_edge_cases")
        
        # Create temporary files
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "generator_naming_comprehensive_edge_cases")
        
        # Get the temp directory (parent of source_dir)
        temp_dir = os.path.dirname(source_dir)
        
        # The TestDataLoader automatically sets config output_dir to "../output"
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy model.json from source to output directory (where CLI expects it)
        model_source = os.path.join(source_dir, "model.json")
        model_target = os.path.join(output_dir, "model.json")
        shutil.copy2(model_source, model_target)
        
        # Make config path relative to working directory
        config_filename = os.path.basename(config_path)
        
        # Execute c2puml with temp directory as working directory - generate only since we provide model.json
        result = self.executor.run_generate_only(config_filename, temp_dir)
        
        # Validate execution
        self.cli_validator.assert_cli_success(result)
        
        # Load output files
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        
        # Load all PlantUML files into a dictionary
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files_dict[filename] = f.read()
        
        # Process assertions from YAML
        self.validators_processor.process_assertions(
            test_data["assertions"], {}, puml_files_dict, result, self
        )


if __name__ == "__main__":
    unittest.main()