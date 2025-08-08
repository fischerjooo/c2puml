#!/usr/bin/env python3
"""
Transformer Feature Tests via CLI (transform-only)
"""

import os
import sys
import unittest
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase


class TestTransformerFeaturesCLI(UnifiedTestCase):
    """Transformer feature tests using the CLI transform-only step"""

    def test_transform_renaming(self):
        """Validate renaming transformations using transform-only"""
        # Load test data from YAML
        test_id = "transformer_features_cli_renaming"
        test_data = self.data_loader.load_test_data(test_id)

        # Create temporary files
        source_dir, config_path = self.data_loader.create_temp_files(test_data, test_id)

        # Compute paths
        test_folder = os.path.dirname(source_dir)
        test_dir = os.path.dirname(test_folder)
        config_filename = os.path.basename(config_path)
        output_dir = os.path.join(test_dir, "output")

        # For transform-only, copy model.json into output directory
        os.makedirs(output_dir, exist_ok=True)
        import shutil
        shutil.copy2(os.path.join(source_dir, "model.json"), os.path.join(output_dir, "model.json"))

        # Execute transform-only
        result = self.executor.run_transform_only(config_filename, test_folder)
        self.cli_validator.assert_cli_success(result)

        # Load transformed model
        transformed_model_file = os.path.join(output_dir, "model_transformed.json")
        self.output_validator.assert_file_exists(transformed_model_file)
        with open(transformed_model_file, 'r') as f:
            model_data = json.load(f)

        # Process assertions from YAML
        self.validators_processor.process_assertions(
            test_data["assertions"], model_data, {}, result, self
        )


if __name__ == "__main__":
    unittest.main()