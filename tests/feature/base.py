"""
Base class for feature tests

Provides common setup and teardown functionality for all feature tests.
This base class now inherits from the shared test utilities for consistency.
"""

import os
import shutil
import tempfile
import unittest
from pathlib import Path

# Import shared utilities for consistency
try:
    from tests.utils import ProjectBuilder, TestDataProviders, create_temp_project
except ImportError:
    # Fallback if utils not available
    ProjectBuilder = None
    TestDataProviders = None
    create_temp_project = None


class BaseFeatureTest(unittest.TestCase):
    """Base class for feature tests with common setup and teardown"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_files = []

        # Initialize project builder if available
        if ProjectBuilder:
            self.project_builder = ProjectBuilder(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def create_test_file(self, filename: str, content: str) -> str:
        """Create a test file and return its path"""
        file_path = os.path.join(self.temp_dir, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        self.test_files.append(file_path)
        return file_path

    def write_json_config(self, config_file: str, config: dict) -> None:
        """Write JSON configuration to file"""
        import json

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    def get_sample_project(self, project_name: str = "simple_project") -> dict:
        """Get a sample project for testing (uses shared data providers if available)"""
        if TestDataProviders:
            projects = TestDataProviders.get_sample_c_projects()
            return projects.get(project_name, projects["simple_project"])
        else:
            # Fallback minimal project
            return {
                "main.c": """
#include "types.h"

int main() {
    Point p = {0, 0};
    return 0;
}
""",
                "types.h": """
#ifndef TYPES_H
#define TYPES_H

typedef struct {
    int x;
    int y;
} Point;

#endif
""",
            }

    def get_sample_config(self, config_name: str = "standard") -> dict:
        """Get a sample configuration for testing (uses shared data providers if available)"""
        if TestDataProviders:
            configs = TestDataProviders.get_sample_configs()
            return configs.get(config_name, configs["standard"])
        else:
            # Fallback minimal config
            return {
                "project_name": "test_project",
                "source_folders": ["."],
                "output_dir": "./output",
                "recursive_search": True,
            }

    def create_temp_project(self, project_data: dict, base_dir: str = None) -> Path:
        """Create a temporary project with the given file structure."""
        if create_temp_project:
            return create_temp_project(project_data, base_dir or self.temp_dir)
        else:
            # Fallback implementation
            if base_dir is None:
                base_dir = self.temp_dir

            project_path = Path(base_dir)

            for file_path, content in project_data.items():
                full_path = project_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(content)

            return project_path

    def run_full_pipeline(
        self, project_dir: Path, config_data: dict, output_dir: Path = None
    ) -> dict:
        """Run the full C to PlantUML pipeline for testing."""
        try:
            from tests.utils import run_full_pipeline

            return run_full_pipeline(project_dir, config_data, output_dir)
        except ImportError:
            # Fallback implementation
            import json

            from c_to_plantuml.generator import Generator
            from c_to_plantuml.parser import Parser
            from c_to_plantuml.transformer import Transformer

            project_dir = Path(project_dir)

            if output_dir is None:
                output_dir = project_dir / "output"
            else:
                output_dir = Path(output_dir)

            output_dir.mkdir(parents=True, exist_ok=True)

            # Create temporary files for pipeline
            model_file = output_dir / "model.json"
            config_file = output_dir / "config.json"
            transformed_model_file = output_dir / "transformed_model.json"

            # Write config
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)

            # Run pipeline
            parser = Parser()
            transformer = Transformer()
            generator = Generator()

            # Parse
            parser.parse(source_folders=[str(project_dir)], output_file=str(model_file))

            # Transform
            transformer.transform(
                str(model_file), str(config_file), str(transformed_model_file)
            )

            # Generate
            generator.generate(str(transformed_model_file), str(output_dir))

            # Return results
            results = {
                "project_dir": project_dir,
                "output_dir": output_dir,
                "model_file": model_file,
                "config_file": config_file,
                "transformed_model_file": transformed_model_file,
            }

            # Load generated models if they exist
            if model_file.exists():
                with open(model_file, "r", encoding="utf-8") as f:
                    results["parsed_model"] = json.load(f)

            if transformed_model_file.exists():
                with open(transformed_model_file, "r", encoding="utf-8") as f:
                    results["transformed_model"] = json.load(f)

            return results
