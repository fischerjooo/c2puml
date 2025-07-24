"""
pytest configuration and shared fixtures for the C to PlantUML test suite.

This module provides common test fixtures and configuration for consistent
testing across all test modules.
"""

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest


@pytest.fixture(scope="function")
def temp_dir():
    """Create a temporary directory that gets cleaned up after each test."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture(scope="function")
def test_project_dir(temp_dir):
    """Create a test project directory structure."""
    project_path = Path(temp_dir) / "test_project"
    project_path.mkdir(parents=True, exist_ok=True)
    return project_path


@pytest.fixture
def config_factory(temp_dir):
    """Factory for creating test configuration files."""
    def _create_config(config_data: Dict[str, Any], filename: str = "config.json") -> str:
        config_path = os.path.join(temp_dir, filename)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
        return config_path
    return _create_config


@pytest.fixture
def file_factory(temp_dir):
    """Factory for creating test files."""
    created_files = []
    
    def _create_file(filename: str, content: str, subdir: str = "") -> str:
        if subdir:
            file_dir = os.path.join(temp_dir, subdir)
            os.makedirs(file_dir, exist_ok=True)
            file_path = os.path.join(file_dir, filename)
        else:
            file_path = os.path.join(temp_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        created_files.append(file_path)
        return file_path
    
    yield _create_file
    # Cleanup is handled by temp_dir fixture


@pytest.fixture
def sample_c_code():
    """Provide sample C code for testing."""
    return {
        "simple_struct": """
typedef struct {
    int x;
    int y;
} Point;
""",
        "simple_function": """
int add(int a, int b) {
    return a + b;
}
""",
        "with_includes": """
#include <stdio.h>
#include "types.h"

typedef struct {
    int id;
    char name[256];
} Person;

int main() {
    return 0;
}
""",
        "header_file": """
#ifndef TYPES_H
#define TYPES_H

typedef unsigned char byte_t;
typedef unsigned short word_t;

typedef struct {
    byte_t r, g, b;
} Color;

#endif
"""
    }


@pytest.fixture
def sample_config():
    """Provide sample configuration data for testing."""
    return {
        "project_name": "test_project",
        "source_folders": ["."],
        "output_dir": "./output",
        "model_output_path": "model.json",
        "recursive_search": True,
        "file_extensions": [".c", ".h"],
        "exclude_patterns": ["*test*", "*example*"],
        "include_depth": 3
    }