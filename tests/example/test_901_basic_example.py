#!/usr/bin/env python3
"""
Example test using the unified framework and external example files
"""

import os
import sys
import json
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tests.framework import UnifiedTestCase  # noqa: E402


class TestBasicExample(UnifiedTestCase):
    """Validate example project end-to-end via CLI using YAML assertions"""

    def test_basic_example(self):
        """Run full pipeline on example project and validate outputs"""
        # Load assertions from YAML (assertions-only for example tests)
        test_data = self.data_loader.load_test_data("901_basic_example")

        # Determine workspace root (two levels up from this file)
        workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

        # Execute c2puml with project root as working directory
        result = self.executor.run_full_pipeline("tests/example/config.json", workspace_root)

        # Validate execution
        self.cli_validator.assert_cli_success(result)

        # Collect outputs from configured output directory
        output_dir = os.path.join(workspace_root, "artifacts", "output_example")
        model_file = self.output_validator.assert_model_file_exists(output_dir)

        # Load model
        with open(model_file, 'r') as f:
            model_data = json.load(f)

        # Load all PUML files into a dict {filename: content}
        puml_files = {}
        for entry in os.listdir(output_dir):
            if entry.endswith('.puml'):
                puml_path = os.path.join(output_dir, entry)
                with open(puml_path, 'r', encoding='utf-8') as pf:
                    puml_files[entry] = pf.read()

        # Process YAML assertions
        self.validators_processor.process_assertions(
            test_data["assertions"], model_data, puml_files, result, self
        )


if __name__ == "__main__":
    unittest.main()