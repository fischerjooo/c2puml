#!/usr/bin/env python3
"""
CLI-based comprehensive integration tests for the new PlantUML formatting rules.
Tests the complete PlantUML generation workflow with all new formatting features through CLI interface.
"""

import os
import sys
import unittest
import json
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestNewFormattingIntegrationCli(UnifiedTestCase):
    """CLI-based integration tests for all new formatting rules working together"""

    def test_complete_formatting_integration(self):
        """Test all new formatting rules working together in a realistic scenario"""
        test_data = self.data_loader.load_test_data("new_formatting_comprehensive_complete")
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "new_formatting_comprehensive_complete")
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

    def test_mixed_project_comprehensive_formatting(self):
        """Test formatting in a project with multiple files and cross-references"""
        test_data = self.data_loader.load_test_data("new_formatting_comprehensive_mixed_project")
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "new_formatting_comprehensive_mixed_project")
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