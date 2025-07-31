import json
import os
import subprocess
import sys
from pathlib import Path

from tests.feature.base import BaseFeatureTest


class TestCLIFeature(BaseFeatureTest):
    def setUp(self):
        super().setUp()
        # Minimal C file
        self.c_file = self.create_test_file(
            "test.c",
            """
        typedef struct { int x; } Point;
        int main() { return 0; }
        """,
        )
        # Minimal config.json with explicit output_dir
        self.output_dir = os.path.join(self.temp_dir, "output")
        self.config_path = os.path.join(self.temp_dir, "config.json")
        self.write_json_config(
            self.config_path,
            {
                "project_name": "cli_test",
                "source_folders": [self.temp_dir],
                "recursive_search": True,
                "output_dir": self.output_dir,
            },
        )
        self.cli = [
            sys.executable,
            "-m", "c2puml.main"
        ]
        self.env = os.environ.copy()
        self.env["PYTHONPATH"] = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../src")
        )

    def run_cli(self, args, cwd=None):
        result = subprocess.run(
            self.cli + args,
            cwd=cwd or self.temp_dir,
            env=self.env,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        print(result.stderr)
        return result

    def test_parse_only(self):
        # Run parse only
        result = self.run_cli(["--config", self.config_path, "parse"])
        self.assertEqual(result.returncode, 0)
        model_path = os.path.join(self.output_dir, "model.json")
        self.assertTrue(os.path.exists(model_path))

    def test_transform_only(self):
        # First, run parse
        self.run_cli(["--config", self.config_path, "parse"])
        # Then, run transform
        result = self.run_cli(["--config", self.config_path, "transform"])
        self.assertEqual(result.returncode, 0)
        transformed_path = os.path.join(self.output_dir, "model_transformed.json")
        self.assertTrue(os.path.exists(transformed_path))

    def test_generate_prefers_transformed(self):
        # First, run parse and transform
        self.run_cli(["--config", self.config_path, "parse"])
        self.run_cli(["--config", self.config_path, "transform"])
        # Then, run generate
        result = self.run_cli(["--config", self.config_path, "generate"])
        self.assertEqual(result.returncode, 0)
        puml_files = list(Path(self.output_dir).glob("*.puml"))
        self.assertGreaterEqual(len(puml_files), 1)

    def test_generate_fallback_to_model(self):
        # Only run parse
        self.run_cli(["--config", self.config_path, "parse"])
        # Remove model_transformed.json if exists
        transformed_path = os.path.join(self.output_dir, "model_transformed.json")
        if os.path.exists(transformed_path):
            os.remove(transformed_path)
        # Run generate
        result = self.run_cli(["--config", self.config_path, "generate"])
        self.assertEqual(result.returncode, 0)
        puml_files = list(Path(self.output_dir).glob("*.puml"))
        self.assertGreaterEqual(len(puml_files), 1)

    def test_generate_command_isolation(self):
        """Test that generate command works when called independently without model files"""
        # This test would have caught the CLI indentation bug
        # It tests the generate command in isolation without any pre-existing model files
        result = self.run_cli(["--config", self.config_path, "generate"])
        # Should fail gracefully with proper error message when no model files exist
        self.assertEqual(result.returncode, 1)
        self.assertIn("No model file found for generation", result.stdout)
