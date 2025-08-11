#!/usr/bin/env python3
"""
Test CLI Features – Consolidated Entry
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
    
    def _prepare(self, test_id: str):
        test_data = self.data_loader.load_test_data(test_id)
        source_dir, config_path = self.data_loader.create_temp_files(test_data, test_id)
        test_folder = os.path.dirname(source_dir)
        test_dir = os.path.dirname(test_folder)
        config_filename = os.path.basename(config_path)
        output_dir = os.path.join(test_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        return test_data, source_dir, config_filename, test_folder, output_dir

    def _normalize_file_paths(self, assertions: dict, output_dir: str) -> dict:
        if not assertions:
            return {}
        import copy
        normalized = copy.deepcopy(assertions)
        files = normalized.get("files")
        if not files:
            return normalized
        def fix(p: str) -> str:
            if not isinstance(p, str):
                return p
            if p in ("./output", "./output/"):
                return output_dir
            if p.startswith("./output/"):
                return os.path.join(output_dir, p[len("./output/"):])
            return p
        for key in ("files_exist", "files_not_exist", "json_files_valid", "utf8_files"):
            if key in files:
                files[key] = [fix(p) for p in files[key]]
        if "output_dir_exists" in files:
            files["output_dir_exists"] = fix(files["output_dir_exists"]) or output_dir
        if "file_content" in files and isinstance(files["file_content"], dict):
            files["file_content"] = {fix(fp): v for fp, v in files["file_content"].items()}
        return normalized
    
    def test_parse_only_command(self):
        """Test parse-only command through the CLI interface"""
        test_id = "cli_feature_comprehensive_parse_only"
        test_data, source_dir, config_filename, test_folder, output_dir = self._prepare(test_id)
        
        # Execute c2puml parse-only command
        result = self.executor.run_parse_only(config_filename, test_folder)
        self.cli_validator.assert_cli_success(result)
        
        # Validate outputs
        model_file = self.output_validator.assert_model_file_exists(output_dir)
        puml_files = list(Path(output_dir).glob("*.puml"))
        self.assertEqual(len(puml_files), 0, "Parse-only should not generate PlantUML files")
        with open(model_file, 'r') as f:
            model_data = json.load(f)
        assertions = self._normalize_file_paths(test_data.get("assertions"), output_dir)
        self.validators_processor.process_assertions(assertions, model_data, {}, result, self)

    def test_transform_only_command(self):
        """Test transform-only command through the CLI interface"""
        test_id = "cli_feature_comprehensive_transform_only"
        test_data, source_dir, config_filename, test_folder, output_dir = self._prepare(test_id)
        
        # Seed model.json in output
        import shutil
        shutil.copy2(os.path.join(source_dir, "model.json"), os.path.join(output_dir, "model.json"))
        
        result = self.executor.run_transform_only(config_filename, test_folder)
        self.cli_validator.assert_cli_success(result)
        
        transformed_model_file = os.path.join(output_dir, "model_transformed.json")
        self.assertTrue(os.path.exists(transformed_model_file), "Transform step should generate model_transformed.json")
        puml_files = list(Path(output_dir).glob("*.puml"))
        self.assertEqual(len(puml_files), 0, "Transform-only should not generate PlantUML files")
        with open(transformed_model_file, 'r') as f:
            model_data = json.load(f)
        assertions = self._normalize_file_paths(test_data.get("assertions"), output_dir)
        self.validators_processor.process_assertions(assertions, model_data, {}, result, self)

    def test_generate_prefers_transformed_model(self):
        """Test generate command preferring transformed model through the CLI interface"""
        test_id = "cli_feature_comprehensive_generate_prefers_transformed"
        test_data, source_dir, config_filename, test_folder, output_dir = self._prepare(test_id)
        
        # Seed both models in output
        import shutil
        shutil.copy2(os.path.join(source_dir, "model.json"), os.path.join(output_dir, "model.json"))
        shutil.copy2(os.path.join(source_dir, "model_transformed.json"), os.path.join(output_dir, "model_transformed.json"))
        
        result = self.executor.run_generate_only(config_filename, test_folder)
        self.cli_validator.assert_cli_success(result)
        
        # Load PUML files
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files_dict[filename] = f.read()
        
        assertions = self._normalize_file_paths(test_data.get("assertions"), output_dir)
        self.validators_processor.process_assertions(assertions, {}, puml_files_dict, result, self)

    def test_generate_fallback_to_model(self):
        """Test generate command fallback to model.json through the CLI interface"""
        test_id = "cli_feature_comprehensive_generate_fallback"
        test_data, source_dir, config_filename, test_folder, output_dir = self._prepare(test_id)
        
        # Seed only model.json
        import shutil
        shutil.copy2(os.path.join(source_dir, "model.json"), os.path.join(output_dir, "model.json"))
        transformed_path = os.path.join(output_dir, "model_transformed.json")
        if os.path.exists(transformed_path):
            os.remove(transformed_path)
        
        result = self.executor.run_generate_only(config_filename, test_folder)
        self.cli_validator.assert_cli_success(result)
        
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        puml_files_dict = {}
        for puml_file_path in puml_files:
            filename = os.path.basename(puml_file_path)
            with open(puml_file_path, 'r') as f:
                puml_files_dict[filename] = f.read()
        
        assertions = self._normalize_file_paths(test_data.get("assertions"), output_dir)
        self.validators_processor.process_assertions(assertions, {}, puml_files_dict, result, self)

    def test_generate_command_isolation_error_handling(self):
        """Test generate command isolation error handling through the CLI interface"""
        test_id = "cli_feature_comprehensive_generate_isolation"
        test_data, source_dir, config_filename, test_folder, output_dir = self._prepare(test_id)
        
        # Execute c2puml generate-only command (should fail)
        result = self.executor.run_generate_only(config_filename, test_folder)
        self.assertEqual(result.exit_code, 1, "Generate command should fail when no model files exist")
        
        assertions = self._normalize_file_paths(test_data.get("assertions"), output_dir)
        self.validators_processor.process_assertions(assertions, {}, {}, result, self)

    def test_cli_modes_and_features_consolidated(self):
        result = self.run_test("cli_modes_comprehensive")
        self.validate_execution_success(result)
        # rely on YAML dir presence only


if __name__ == "__main__":
    unittest.main()