#!/usr/bin/env python3
"""
Test CLI Modes Comprehensive
"""

import os
import sys
import unittest
import json
from pathlib import Path
import copy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestCLIModesComprehensive(UnifiedTestCase):
    """Test CLI modes functionality through the CLI interface"""

    def test_cli_modes_and_features_comprehensive(self):
        result = self.run_test("cli_modes_comprehensive")
        # No model/puml validations needed; YAML asserts only dir presence
        self.validate_execution_success(result)
        self.validators_processor.process_assertions({"execution": {"should_succeed": True}}, {}, {}, result, self)

    def test_parse_mode_only_generates_model(self):
        """Test parse mode only generates model.json through the CLI interface"""
        # Load test data from YAML
        test_data = self.data_loader.load_test_data("cli_modes_comprehensive_parse_mode")
        
        # Create temporary files
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "cli_modes_comprehensive_parse_mode")
        
        # Calculate paths
        test_folder = os.path.dirname(source_dir)  # input/ folder
        test_dir = os.path.dirname(test_folder)    # test-###/ folder
        config_filename = os.path.basename(config_path)
        output_dir = os.path.join(test_dir, "output")
        
        # Execute c2puml parse-only command
        result = self.executor.run_parse_only(config_filename, test_folder)
        
        # Validate execution
        self.cli_validator.assert_cli_success(result)
        
        # Load output files
        model_file = self.output_validator.assert_model_file_exists(output_dir)
        
        # For parse-only, there should be no PlantUML files and no model_transformed.json
        puml_files = list(Path(output_dir).glob("*.puml"))
        self.assertEqual(len(puml_files), 0, "Parse-only should not generate PlantUML files")
        
        transformed_path = os.path.join(output_dir, "model_transformed.json")
        self.assertFalse(os.path.exists(transformed_path), "Parse-only should not generate model_transformed.json")
        
        # Load content for validation
        with open(model_file, 'r') as f:
            model_data = json.load(f)
        
        # Update file assertions to use absolute paths
        test_assertions = copy.deepcopy(test_data["assertions"])
        if "files" in test_assertions:
            if "output_dir_exists" in test_assertions["files"]:
                test_assertions["files"]["output_dir_exists"] = output_dir
            if "files_exist" in test_assertions["files"]:
                updated_files = []
                for file_path in test_assertions["files"]["files_exist"]:
                    if file_path.startswith("./output/"):
                        updated_files.append(os.path.join(output_dir, file_path[9:]))
                    else:
                        updated_files.append(file_path)
                test_assertions["files"]["files_exist"] = updated_files
            if "files_not_exist" in test_assertions["files"]:
                updated_files = []
                for file_path in test_assertions["files"]["files_not_exist"]:
                    if file_path.startswith("./output/"):
                        updated_files.append(os.path.join(output_dir, file_path[9:]))
                    else:
                        updated_files.append(file_path)
                test_assertions["files"]["files_not_exist"] = updated_files
            if "json_files_valid" in test_assertions["files"]:
                updated_json_files = []
                for json_file in test_assertions["files"]["json_files_valid"]:
                    if json_file.startswith("./output/"):
                        updated_json_files.append(os.path.join(output_dir, json_file[9:]))
                    else:
                        updated_json_files.append(json_file)
                test_assertions["files"]["json_files_valid"] = updated_json_files
        
        # Process assertions from YAML (no puml_files for parse-only)
        self.validators_processor.process_assertions(
            test_assertions, model_data, {}, result, self
        )

    def test_transform_mode_generates_transformed_model(self):
        """Test transform mode generates model_transformed.json through the CLI interface"""
        # Load test data from YAML
        test_data = self.data_loader.load_test_data("cli_modes_comprehensive_transform_mode")
        
        # Create temporary files
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "cli_modes_comprehensive_transform_mode")
        
        # Calculate paths
        test_folder = os.path.dirname(source_dir)
        test_dir = os.path.dirname(test_folder)
        config_filename = os.path.basename(config_path)
        output_dir = os.path.join(test_dir, "output")
        
        # For transform-only test, we need to copy model.json to output directory first
        os.makedirs(output_dir, exist_ok=True)
        import shutil
        shutil.copy2(os.path.join(source_dir, "model.json"), os.path.join(output_dir, "model.json"))
        
        # Execute c2puml transform-only command
        result = self.executor.run_transform_only(config_filename, test_folder)
        
        # Validate execution
        self.cli_validator.assert_cli_success(result)
        
        # Load output files
        transformed_model_file = os.path.join(output_dir, "model_transformed.json")
        self.assertTrue(os.path.exists(transformed_model_file), "Transform should generate model_transformed.json")
        
        # For transform-only, there should be no PlantUML files
        puml_files = list(Path(output_dir).glob("*.puml"))
        self.assertEqual(len(puml_files), 0, "Transform-only should not generate PlantUML files")
        
        # Load content for validation
        with open(transformed_model_file, 'r') as f:
            model_data = json.load(f)
        
        # Update file assertions to use absolute paths
        test_assertions = copy.deepcopy(test_data["assertions"])
        if "files" in test_assertions:
            if "output_dir_exists" in test_assertions["files"]:
                test_assertions["files"]["output_dir_exists"] = output_dir
            if "files_exist" in test_assertions["files"]:
                updated_files = []
                for file_path in test_assertions["files"]["files_exist"]:
                    if file_path.startswith("./output/"):
                        updated_files.append(os.path.join(output_dir, file_path[9:]))
                    else:
                        updated_files.append(file_path)
                test_assertions["files"]["files_exist"] = updated_files
            if "files_not_exist" in test_assertions["files"]:
                updated_files = []
                for file_path in test_assertions["files"]["files_not_exist"]:
                    if file_path.startswith("./output/"):
                        updated_files.append(os.path.join(output_dir, file_path[9:]))
                    else:
                        updated_files.append(file_path)
                test_assertions["files"]["files_not_exist"] = updated_files
            if "json_files_valid" in test_assertions["files"]:
                updated_json_files = []
                for json_file in test_assertions["files"]["json_files_valid"]:
                    if json_file.startswith("./output/"):
                        updated_json_files.append(os.path.join(output_dir, json_file[9:]))
                    else:
                        updated_json_files.append(json_file)
                test_assertions["files"]["json_files_valid"] = updated_json_files
        
        # Process assertions from YAML (no puml_files for transform-only)
        self.validators_processor.process_assertions(
            test_assertions, model_data, {}, result, self
        )

    def test_generate_mode_prefers_transformed_model(self):
        """Test generate mode prefers transformed model through the CLI interface"""
        # Load test data from YAML
        test_data = self.data_loader.load_test_data("cli_modes_comprehensive_generate_prefers_transformed")
        
        # Create temporary files
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "cli_modes_comprehensive_generate_prefers_transformed")
        
        # Calculate paths
        test_folder = os.path.dirname(source_dir)
        test_dir = os.path.dirname(test_folder)
        config_filename = os.path.basename(config_path)
        output_dir = os.path.join(test_dir, "output")
        
        # For generate test, we need to copy both model files to output directory first
        os.makedirs(output_dir, exist_ok=True)
        import shutil
        shutil.copy2(os.path.join(source_dir, "model.json"), os.path.join(output_dir, "model.json"))
        shutil.copy2(os.path.join(source_dir, "model_transformed.json"), os.path.join(output_dir, "model_transformed.json"))
        
        # Execute c2puml generate-only command
        result = self.executor.run_generate_only(config_filename, test_folder)
        
        # Validate execution
        self.cli_validator.assert_cli_success(result)
        
        # Load output files
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        self.assertGreaterEqual(len(puml_files), 1, "Generate should create PlantUML files")
        
        # Load all PlantUML files into a dictionary
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files_dict[filename] = f.read()
        
        # Update file assertions to use absolute paths
        test_assertions = copy.deepcopy(test_data["assertions"])
        if "files" in test_assertions:
            if "files_exist" in test_assertions["files"]:
                updated_files = []
                for file_path in test_assertions["files"]["files_exist"]:
                    if file_path.startswith("./output/"):
                        updated_files.append(os.path.join(output_dir, file_path[9:]))
                    else:
                        updated_files.append(file_path)
                test_assertions["files"]["files_exist"] = updated_files
        
        # Process assertions from YAML (no model validation for generate-only)
        self.validators_processor.process_assertions(
            test_assertions, {}, puml_files_dict, result, self
        )

    def test_generate_mode_fallback_to_model(self):
        """Test generate mode fallback to model.json through the CLI interface"""
        # Load test data from YAML
        test_data = self.data_loader.load_test_data("cli_modes_comprehensive_generate_fallback")
        
        # Create temporary files
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "cli_modes_comprehensive_generate_fallback")
        
        # Calculate paths
        test_folder = os.path.dirname(source_dir)
        test_dir = os.path.dirname(test_folder)
        config_filename = os.path.basename(config_path)
        output_dir = os.path.join(test_dir, "output")
        
        # For generate fallback test, we only copy model.json (not model_transformed.json)
        os.makedirs(output_dir, exist_ok=True)
        import shutil
        shutil.copy2(os.path.join(source_dir, "model.json"), os.path.join(output_dir, "model.json"))
        
        # Ensure model_transformed.json doesn't exist
        transformed_path = os.path.join(output_dir, "model_transformed.json")
        if os.path.exists(transformed_path):
            os.remove(transformed_path)
        
        # Execute c2puml generate-only command
        result = self.executor.run_generate_only(config_filename, test_folder)
        
        # Validate execution
        self.cli_validator.assert_cli_success(result)
        
        # Load output files
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        self.assertGreaterEqual(len(puml_files), 1, "Generate should create PlantUML files")
        
        # Load all PlantUML files into a dictionary
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files_dict[filename] = f.read()
        
        # Update file assertions to use absolute paths
        test_assertions = copy.deepcopy(test_data["assertions"])
        if "files" in test_assertions:
            if "files_exist" in test_assertions["files"]:
                updated_files = []
                for file_path in test_assertions["files"]["files_exist"]:
                    if file_path.startswith("./output/"):
                        updated_files.append(os.path.join(output_dir, file_path[9:]))
                    else:
                        updated_files.append(file_path)
                test_assertions["files"]["files_exist"] = updated_files
        
        # Process assertions from YAML (no model validation for generate-only)
        self.validators_processor.process_assertions(
            test_assertions, {}, puml_files_dict, result, self
        )

    def test_full_workflow_default_mode(self):
        """Test full workflow default mode through the CLI interface"""
        # Load test data from YAML
        test_data = self.data_loader.load_test_data("cli_modes_comprehensive_full_workflow")
        
        # Create temporary files
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "cli_modes_comprehensive_full_workflow")
        
        # Calculate paths
        test_folder = os.path.dirname(source_dir)
        test_dir = os.path.dirname(test_folder)
        config_filename = os.path.basename(config_path)
        output_dir = os.path.join(test_dir, "output")
        
        # Execute c2puml full pipeline (no command specified)
        result = self.executor.run_full_pipeline(config_filename, test_folder)
        
        # Validate execution
        self.cli_validator.assert_cli_success(result)
        
        # Load output files
        model_file = self.output_validator.assert_model_file_exists(output_dir)
        transformed_model_file = os.path.join(output_dir, "model_transformed.json")
        self.assertTrue(os.path.exists(transformed_model_file), "Full workflow should generate model_transformed.json")
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        self.assertGreaterEqual(len(puml_files), 1, "Full workflow should create PlantUML files")
        
        # Load content for validation
        with open(transformed_model_file, 'r') as f:
            model_data = json.load(f)
        
        # Load all PlantUML files into a dictionary
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files_dict[filename] = f.read()
        
        # Update file assertions to use absolute paths
        test_assertions = copy.deepcopy(test_data["assertions"])
        if "files" in test_assertions:
            if "output_dir_exists" in test_assertions["files"]:
                test_assertions["files"]["output_dir_exists"] = output_dir
            if "files_exist" in test_assertions["files"]:
                updated_files = []
                for file_path in test_assertions["files"]["files_exist"]:
                    if file_path.startswith("./output/"):
                        updated_files.append(os.path.join(output_dir, file_path[9:]))
                    else:
                        updated_files.append(file_path)
                test_assertions["files"]["files_exist"] = updated_files
            if "json_files_valid" in test_assertions["files"]:
                updated_json_files = []
                for json_file in test_assertions["files"]["json_files_valid"]:
                    if json_file.startswith("./output/"):
                        updated_json_files.append(os.path.join(output_dir, json_file[9:]))
                    else:
                        updated_json_files.append(json_file)
                test_assertions["files"]["json_files_valid"] = updated_json_files
        
        # Process assertions from YAML
        self.validators_processor.process_assertions(
            test_assertions, model_data, puml_files_dict, result, self
        )

    def test_generate_mode_isolation_error_handling(self):
        """Test generate mode isolation error handling through the CLI interface"""
        # Load test data from YAML
        test_data = self.data_loader.load_test_data("cli_modes_comprehensive_generate_isolation")
        
        # Create temporary files
        source_dir, config_path = self.data_loader.create_temp_files(test_data, "cli_modes_comprehensive_generate_isolation")
        
        # Calculate paths
        test_folder = os.path.dirname(source_dir)
        test_dir = os.path.dirname(test_folder)
        config_filename = os.path.basename(config_path)
        output_dir = os.path.join(test_dir, "output")
        
        # For error handling test, ensure no model files exist in output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Execute c2puml generate-only command (should fail)
        result = self.executor.run_generate_only(config_filename, test_folder)
        
        # Validate execution failure (expected exit code 1)
        self.assertEqual(result.exit_code, 1, "Generate command should fail when no model files exist")
        
        # Process assertions from YAML (no model or puml validation for error test)
        self.validators_processor.process_assertions(
            test_data["assertions"], {}, {}, result, self
        )


if __name__ == "__main__":
    unittest.main()