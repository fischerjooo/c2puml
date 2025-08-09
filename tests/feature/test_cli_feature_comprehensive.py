#!/usr/bin/env python3
"""
Test CLI Feature Comprehensive
"""

import os
import sys
import unittest
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestCLIFeatureComprehensive(UnifiedTestCase):
    """Test CLI feature functionality through the CLI interface"""
    
    def test_parse_only_command(self):
        """Test parse-only command through the CLI interface"""
        # Prepare environment
        test_id = "cli_feature_comprehensive_parse_only"
        test_data, source_dir, config_filename, test_folder, test_dir, output_dir = self.prepare_test_environment(test_id)
        
        # Execute c2puml parse-only command
        result = self.executor.run_parse_only(config_filename, test_folder)
        
        # Validate execution
        self.cli_validator.assert_cli_success(result)
        
        # Load output files
        model_file = self.output_validator.assert_model_file_exists(output_dir)
        
        # For parse-only, there should be no PlantUML files
        puml_files = list(Path(output_dir).glob("*.puml"))
        self.assertEqual(len(puml_files), 0, "Parse-only should not generate PlantUML files")
        
        # Load content for validation
        with open(model_file, 'r') as f:
            model_data = json.load(f)
        
        # Normalize file assertion paths and validate
        assertions = self.normalize_file_assertions_paths(test_data.get("assertions"), output_dir)
        self.validators_processor.process_assertions(assertions, model_data, {}, result, self)

    def test_transform_only_command(self):
        """Test transform-only command through the CLI interface"""
        # Prepare environment
        test_id = "cli_feature_comprehensive_transform_only"
        test_data, source_dir, config_filename, test_folder, test_dir, output_dir = self.prepare_test_environment(test_id)
        
        # For transform-only test, copy model.json to output directory first
        import shutil
        shutil.copy2(os.path.join(source_dir, "model.json"), os.path.join(output_dir, "model.json"))
        
        # Execute c2puml transform-only command
        result = self.executor.run_transform_only(config_filename, test_folder)
        
        # Validate execution
        self.cli_validator.assert_cli_success(result)
        
        # Load output files
        transformed_model_file = os.path.join(output_dir, "model_transformed.json")
        self.assertTrue(os.path.exists(transformed_model_file), "Transform step should generate model_transformed.json")
        
        # For transform-only, there should be no PlantUML files
        puml_files = list(Path(output_dir).glob("*.puml"))
        self.assertEqual(len(puml_files), 0, "Transform-only should not generate PlantUML files")
        
        # Load content for validation
        with open(transformed_model_file, 'r') as f:
            model_data = json.load(f)
        
        # Normalize file assertion paths and validate
        assertions = self.normalize_file_assertions_paths(test_data.get("assertions"), output_dir)
        self.validators_processor.process_assertions(assertions, model_data, {}, result, self)

    def test_generate_prefers_transformed_model(self):
        """Test generate command preferring transformed model through the CLI interface"""
        # Prepare environment
        test_id = "cli_feature_comprehensive_generate_prefers_transformed"
        test_data, source_dir, config_filename, test_folder, test_dir, output_dir = self.prepare_test_environment(test_id)
        
        # For generate test, copy both model files to output directory first
        import shutil
        shutil.copy2(os.path.join(source_dir, "model.json"), os.path.join(output_dir, "model.json"))
        shutil.copy2(os.path.join(source_dir, "model_transformed.json"), os.path.join(output_dir, "model_transformed.json"))
        
        # Execute c2puml generate-only command
        result = self.executor.run_generate_only(config_filename, test_folder)
        
        # Validate execution
        self.cli_validator.assert_cli_success(result)
        
        # Load output files
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        self.assertGreaterEqual(len(puml_files), 1, "Generate step should create PlantUML files")
        
        # Load all PlantUML files into a dictionary
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files_dict[filename] = f.read()
        
        # Normalize file assertion paths and validate (no model validation for generate-only)
        assertions = self.normalize_file_assertions_paths(test_data.get("assertions"), output_dir)
        self.validators_processor.process_assertions(assertions, {}, puml_files_dict, result, self)

    def test_generate_fallback_to_model(self):
        """Test generate command fallback to model.json through the CLI interface"""
        # Prepare environment
        test_id = "cli_feature_comprehensive_generate_fallback"
        test_data, source_dir, config_filename, test_folder, test_dir, output_dir = self.prepare_test_environment(test_id)
        
        # Only copy model.json (not model_transformed.json)
        import shutil
        shutil.copy2(os.path.join(source_dir, "model.json"), os.path.join(output_dir, "model.json"))
        transformed_path = os.path.join(output_dir, "model_transformed.json")
        if os.path.exists(transformed_path):
            os.remove(transformed_path)
        
        # Execute c2puml generate-only command
        result = self.executor.run_generate_only(config_filename, test_folder)
        
        # Validate execution
        self.cli_validator.assert_cli_success(result)
        
        # Load output files
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        self.assertGreaterEqual(len(puml_files), 1, "Generate step should create PlantUML files")
        
        # Load all PlantUML files into a dictionary
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files_dict[filename] = f.read()
        
        # Normalize file assertion paths and validate (no model validation for generate-only)
        assertions = self.normalize_file_assertions_paths(test_data.get("assertions"), output_dir)
        self.validators_processor.process_assertions(assertions, {}, puml_files_dict, result, self)

    def test_generate_command_isolation_error_handling(self):
        """Test generate command isolation error handling through the CLI interface"""
        # Prepare environment
        test_id = "cli_feature_comprehensive_generate_isolation"
        test_data, source_dir, config_filename, test_folder, test_dir, output_dir = self.prepare_test_environment(test_id)
        
        # Ensure no model files exist in output directory
        # (output_dir is created by prepare_test_environment)
        
        # Execute c2puml generate-only command (should fail)
        result = self.executor.run_generate_only(config_filename, test_folder)
        
        # Validate execution failure (expected exit code asserted by YAML too)
        self.assertEqual(result.exit_code, 1, "Generate command should fail when no model files exist")
        
        # Directly process assertions from YAML (no model or puml validation for error test)
        assertions = self.normalize_file_assertions_paths(test_data.get("assertions"), output_dir)
        self.validators_processor.process_assertions(assertions, {}, {}, result, self)


if __name__ == "__main__":
    unittest.main()