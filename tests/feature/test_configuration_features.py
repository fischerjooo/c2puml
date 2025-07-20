"""
Feature tests for configuration functionality

Tests the ability to load and validate configuration files.
"""

import json
import os

from .base import BaseFeatureTest


class TestConfigurationFeatures(BaseFeatureTest):
    """Test configuration loading and validation"""

    def test_feature_configuration_loading(self):
        """Test configuration loading and validation"""
        from c_to_plantuml.config import Config

        config_data = {
            "project_name": "test_project",
            "source_folders": [self.temp_dir],  # Use actual existing directory
            "output_dir": "./output",
            "model_output_path": "model.json",
            "recursive": True,
            "file_filters": {},
            "element_filters": {},
        }

        config_path = os.path.join(self.temp_dir, "test_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)

        config = Config.load(config_path)

        # Verify configuration loading
        self.assertEqual(config.project_name, "test_project")
        self.assertEqual(config.source_folders, [self.temp_dir])
        self.assertEqual(config.output_dir, "./output")
        self.assertEqual(config.model_output_path, "model.json")
        self.assertTrue(config.recursive)