#!/usr/bin/env python3
"""
Test Generator New Formatting Through CLI Interface – Consolidated
"""
import os
import sys
import unittest
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase

class TestGeneratorNewFormattingCLI(UnifiedTestCase):
    """Test the new PlantUML formatting rules through the CLI interface (consolidated)"""

    def test_generator_new_formatting_stereotypes_comprehensive(self):
        test_id = "124_gen_newfmt"
        test_data = self.data_loader.load_test_data(test_id)
        source_dir, config_path = self.data_loader.create_temp_files(test_data, test_id)
        temp_dir = os.path.dirname(source_dir)
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)

        # Copy model to expected output location for generate_only
        shutil.copy2(os.path.join(source_dir, "model.json"), os.path.join(output_dir, "model.json"))

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

    def test_newfmt_complex_typedef(self):
        test_id = "124_gen_newfmt_complex_typedef"
        test_data = self.data_loader.load_test_data(test_id)
        source_dir, config_path = self.data_loader.create_temp_files(test_data, test_id)
        temp_dir = os.path.dirname(source_dir)
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)
        shutil.copy2(os.path.join(source_dir, "model.json"), os.path.join(output_dir, "model.json"))
        result = self.executor.run_generate_only(os.path.basename(config_path), temp_dir)
        self.cli_validator.assert_cli_success(result)
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        puml_files_dict = {os.path.basename(p): open(p, 'r').read() for p in puml_files}
        self.validators_processor.process_assertions(test_data["assertions"], {}, puml_files_dict, result, self)

    def test_newfmt_visibility_logic(self):
        test_id = "124_gen_newfmt_visibility_logic"
        test_data = self.data_loader.load_test_data(test_id)
        source_dir, config_path = self.data_loader.create_temp_files(test_data, test_id)
        temp_dir = os.path.dirname(source_dir)
        output_dir = os.path.join(os.path.dirname(temp_dir), "output")
        os.makedirs(output_dir, exist_ok=True)
        shutil.copy2(os.path.join(source_dir, "model.json"), os.path.join(output_dir, "model.json"))
        result = self.executor.run_generate_only(os.path.basename(config_path), temp_dir)
        self.cli_validator.assert_cli_success(result)
        puml_files = self.output_validator.assert_puml_files_exist(output_dir)
        puml_files_dict = {os.path.basename(p): open(p, 'r').read() for p in puml_files}
        self.validators_processor.process_assertions(test_data["assertions"], {}, puml_files_dict, result, self)

if __name__ == "__main__":
    unittest.main()