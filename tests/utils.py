"""
Shared test utilities for the C to PlantUML test suite.

This module provides common utilities, helpers, and patterns used across
multiple test modules to reduce code duplication and ensure consistency.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from unittest.mock import MagicMock, Mock

from c2puml.generator import Generator
from c2puml.models import Enum, FileModel, Function, ProjectModel, Struct
from c2puml.parser import Parser
from c2puml.transformer import Transformer


class ProjectBuilder:
    """Builder class for creating test project structures."""

    def __init__(self, base_dir: Union[str, Path]):
        self.base_dir = Path(base_dir)
        self.files = {}

    def add_c_file(
        self, filename: str, content: str, subdir: str = ""
    ) -> "TestProjectBuilder":
        """Add a C source file to the test project."""
        return self._add_file(filename, content, subdir, ".c")

    def add_h_file(
        self, filename: str, content: str, subdir: str = ""
    ) -> "TestProjectBuilder":
        """Add a C header file to the test project."""
        return self._add_file(filename, content, subdir, ".h")

    def add_config(
        self, config_data: Dict[str, Any], filename: str = "config.json"
    ) -> "TestProjectBuilder":
        """Add a configuration file to the test project."""
        config_content = json.dumps(config_data, indent=2)
        return self._add_file(filename, config_content)

    def _add_file(
        self, filename: str, content: str, subdir: str = "", extension: str = ""
    ) -> "TestProjectBuilder":
        """Internal method to add any file type."""
        if extension and not filename.endswith(extension):
            filename += extension

        if subdir:
            file_path = self.base_dir / subdir / filename
        else:
            file_path = self.base_dir / filename

        self.files[str(file_path)] = content
        return self

    def build(self) -> Path:
        """Create all files and return the project directory."""
        for file_path, content in self.files.items():
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        return self.base_dir


class MockObjectFactory:
    """Factory for creating mock objects for testing."""

    @staticmethod
    def create_file_model(
        filename: str = "test.c",
        includes: Optional[List[str]] = None,
        structs: Optional[List[Struct]] = None,
        functions: Optional[List[Function]] = None,
        enums: Optional[List[Enum]] = None,
    ) -> FileModel:
        """Create a mock FileModel for testing."""
        file_model = FileModel()
        file_model.filename = filename
        file_model.includes = includes or []
        file_model.structs = structs or []
        file_model.functions = functions or []
        file_model.enums = enums or []
        return file_model

    @staticmethod
    def create_project_model(
        project_name: str = "test_project", files: Optional[List[FileModel]] = None
    ) -> ProjectModel:
        """Create a mock ProjectModel for testing."""
        project_model = ProjectModel()
        project_model.project_name = project_name
        project_model.files = files or []
        return project_model

    @staticmethod
    def create_struct(
        name: str = "TestStruct", fields: Optional[List[str]] = None
    ) -> Struct:
        """Create a mock Struct for testing."""
        struct = Struct()
        struct.name = name
        struct.fields = fields or ["int field1", "char field2"]
        return struct


class AssertionHelpers:
    """Helper methods for common test assertions."""

    @staticmethod
    def assert_file_contains_includes(
        file_model: FileModel, expected_includes: List[str]
    ) -> None:
        """Assert that a file model contains all expected includes."""
        actual_includes = set(file_model.includes)
        expected_includes_set = set(expected_includes)

        missing = expected_includes_set - actual_includes
        if missing:
            raise AssertionError(f"Missing includes: {missing}")

        extra = actual_includes - expected_includes_set
        if extra:
            raise AssertionError(f"Unexpected includes: {extra}")

    @staticmethod
    def assert_struct_exists(file_model: FileModel, struct_name: str) -> Struct:
        """Assert that a struct exists in the file model and return it."""
        for struct in file_model.structs:
            if struct.name == struct_name:
                return struct

        available_structs = [s.name for s in file_model.structs]
        raise AssertionError(
            f"Struct '{struct_name}' not found. Available: {available_structs}"
        )

    @staticmethod
    def assert_function_exists(file_model: FileModel, function_name: str) -> Function:
        """Assert that a function exists in the file model and return it."""
        for function in file_model.functions:
            if function.name == function_name:
                return function

        available_functions = [f.name for f in file_model.functions]
        raise AssertionError(
            f"Function '{function_name}' not found. Available: {available_functions}"
        )


class TestDataProviders:
    """Providers for common test data patterns."""

    @staticmethod
    def get_sample_c_projects() -> Dict[str, Dict[str, str]]:
        """Get sample C projects for testing."""
        return {
            "simple_project": {
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
            },
            "complex_project": {
                "main.c": """
#include <stdio.h>
#include "math_utils.h"
#include "graphics.h"

int main() {
    Point origin = create_point(0, 0);
    Color red = {255, 0, 0};
    return 0;
}
""",
                "math_utils.h": """
#ifndef MATH_UTILS_H
#define MATH_UTILS_H

typedef struct {
    double x;
    double y;
} Point;

Point create_point(double x, double y);
double distance(Point a, Point b);

#endif
""",
                "math_utils.c": """
#include "math_utils.h"
#include <math.h>

Point create_point(double x, double y) {
    Point p = {x, y};
    return p;
}

double distance(Point a, Point b) {
    double dx = a.x - b.x;
    double dy = a.y - b.y;
    return sqrt(dx*dx + dy*dy);
}
""",
                "graphics.h": """
#ifndef GRAPHICS_H
#define GRAPHICS_H

#include "math_utils.h"

typedef struct {
    unsigned char r, g, b;
} Color;

typedef struct {
    Point position;
    Color color;
} Pixel;

#endif
""",
            },
        }

    @staticmethod
    def get_sample_configs() -> Dict[str, Dict[str, Any]]:
        """Get sample configuration data for testing."""
        return {
            "minimal": {
                "project_name": "test_project",
                "source_folders": ["."],
                "output_dir": "./output",
            },
            "standard": {
                "project_name": "standard_project",
                "source_folders": ["./src", "./include"],
                "output_dir": "./output",
                "recursive_search": True,
                "file_extensions": [".c", ".h"],
                "include_depth": 3,
            },
            "advanced": {
                "project_name": "advanced_project",
                "source_folders": ["./src", "./include", "./lib"],
                "output_dir": "./output",
                "recursive_search": True,
                "file_extensions": [".c", ".h", ".cpp", ".hpp"],
                "exclude_patterns": ["*test*", "*example*", "*_backup*"],
                "include_depth": 5,
                "generate_images": True,
                "filter_patterns": {
                    "include_only": ["*api*", "*core*"],
                    "exclude": ["*internal*", "*private*"],
                },
            },
        }


def create_temp_project(
    project_data: Dict[str, str], base_dir: Optional[str] = None
) -> Path:
    """Create a temporary project with the given file structure.

    Args:
        project_data: Dictionary mapping file paths to file contents
        base_dir: Optional base directory (creates temp dir if not provided)

    Returns:
        Path to the created project directory
    """
    if base_dir is None:
        base_dir = tempfile.mkdtemp()

    project_path = Path(base_dir)

    for file_path, content in project_data.items():
        full_path = project_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    return project_path


def run_full_pipeline(
    project_dir: Union[str, Path],
    config_data: Dict[str, Any],
    output_dir: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """Run the full C to PlantUML pipeline for testing.

    Args:
        project_dir: Path to the project to process
        config_data: Configuration for the pipeline
        output_dir: Optional output directory

    Returns:
        Dictionary containing the results of each pipeline stage
    """
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
