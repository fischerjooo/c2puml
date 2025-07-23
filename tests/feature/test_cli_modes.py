import os
import subprocess
import sys
from pathlib import Path
from tests.feature.base import BaseFeatureTest


class TestCLIModes(BaseFeatureTest):
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
        # Minimal config.json
        self.config_path = os.path.join(self.temp_dir, "config.json")
        self.write_json_config(
            self.config_path,
            {
                "project_name": "cli_modes_test",
                "source_folders": [self.temp_dir],
                "recursive_search": True,
            },
        )
        self.cli = [
            sys.executable,
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../main.py")),
        ]
        self.env = os.environ.copy()
        self.env["PYTHONPATH"] = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../")
        )
        self.output_dir = os.path.join(self.temp_dir, "output")

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

    def test_parse_mode(self):
        result = self.run_cli(["--config", self.config_path, "parse"])
        self.assertEqual(result.returncode, 0)
        model_path = os.path.join(self.output_dir, "model.json")
        self.assertTrue(os.path.exists(model_path))
        # Only model.json should exist, not model_transformed.json or .puml
        self.assertFalse(
            os.path.exists(os.path.join(self.output_dir, "model_transformed.json"))
        )
        puml_files = list(Path(self.output_dir).glob("*.puml"))
        self.assertEqual(len(puml_files), 0)

    def test_transform_mode(self):
        # First, run parse
        self.run_cli(["--config", self.config_path, "parse"])
        # Then, run transform
        result = self.run_cli(["--config", self.config_path, "transform"])
        self.assertEqual(result.returncode, 0)
        transformed_path = os.path.join(self.output_dir, "model_transformed.json")
        self.assertTrue(os.path.exists(transformed_path))
        # .puml files should not exist
        puml_files = list(Path(self.output_dir).glob("*.puml"))
        self.assertEqual(len(puml_files), 0)

    def test_generate_mode_prefers_transformed(self):
        # First, run parse and transform
        self.run_cli(["--config", self.config_path, "parse"])
        self.run_cli(["--config", self.config_path, "transform"])
        # Then, run generate
        result = self.run_cli(["--config", self.config_path, "generate"])
        self.assertEqual(result.returncode, 0)
        puml_files = list(Path(self.output_dir).glob("*.puml"))
        self.assertGreaterEqual(len(puml_files), 1)

    def test_generate_mode_fallback_to_model(self):
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

    def test_full_workflow_default(self):
        # Run with no command (should run full workflow)
        result = self.run_cli(["--config", self.config_path])
        self.assertEqual(result.returncode, 0)
        model_path = os.path.join(self.output_dir, "model.json")
        transformed_path = os.path.join(self.output_dir, "model_transformed.json")
        self.assertTrue(os.path.exists(model_path))
        self.assertTrue(os.path.exists(transformed_path))
        puml_files = list(Path(self.output_dir).glob("*.puml"))
        self.assertGreaterEqual(len(puml_files), 1)
