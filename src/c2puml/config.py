#!/usr/bin/env python3
"""
Configuration management for C to PlantUML converter
"""

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from .models import FileModel


@dataclass
class Config:
    """Configuration class for C to PlantUML converter"""

    # Configuration settings
    project_name: str = "Unknown_Project"
    source_folders: List[str] = field(default_factory=list)
    output_dir: str = "./output"
    model_output_path: str = "model.json"
    recursive_search: bool = True
    include_depth: int = 1
    include_filter_local_only: bool = False
    always_show_includes: bool = False
    convert_empty_class_to_artifact: bool = False

    # Generator formatting options
    max_function_signature_chars: int = 0  # 0 or less means unlimited (no truncation)
    hide_macro_values: bool = False  # Hide macro values in generated PlantUML diagrams

    # Filters
    file_filters: Dict[str, List[str]] = field(default_factory=dict)
    file_specific: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Transformations
    transformations: Dict[str, Any] = field(default_factory=dict)

    # Compiled patterns for performance
    file_include_patterns: List[re.Pattern] = field(default_factory=list)
    file_exclude_patterns: List[re.Pattern] = field(default_factory=list)

    def __init__(self, *args, **kwargs):
        """Initialize configuration with keyword arguments or a single dict"""
        # Initialize logger
        self.logger = logging.getLogger(__name__)

        # Initialize with default values first
        object.__init__(self)

        # Ensure all dataclass fields are initialized with defaults
        if not hasattr(self, "project_name"):
            self.project_name = "Unknown_Project"
        if not hasattr(self, "source_folders"):
            self.source_folders = []
        if not hasattr(self, "output_dir"):
            self.output_dir = "./output"
        if not hasattr(self, "model_output_path"):
            self.model_output_path = "model.json"
        if not hasattr(self, "recursive_search"):
            self.recursive_search = True
        if not hasattr(self, "include_depth"):
            self.include_depth = 1
        if not hasattr(self, "include_filter_local_only"):
            self.include_filter_local_only = False
        if not hasattr(self, "always_show_includes"):
            self.always_show_includes = False
        if not hasattr(self, "convert_empty_class_to_artifact"):
            self.convert_empty_class_to_artifact = False
        if not hasattr(self, "max_function_signature_chars"):
            self.max_function_signature_chars = 0
        if not hasattr(self, "hide_macro_values"):
            self.hide_macro_values = False
        if not hasattr(self, "file_filters"):
            self.file_filters = {}
        if not hasattr(self, "file_specific"):
            self.file_specific = {}
        if not hasattr(self, "transformations"):
            self.transformations = {}
        if not hasattr(self, "file_include_patterns"):
            self.file_include_patterns = []
        if not hasattr(self, "file_exclude_patterns"):
            self.file_exclude_patterns = []
        if not hasattr(self, "element_include_patterns"):
            self.element_include_patterns = {}
        if not hasattr(self, "element_exclude_patterns"):
            self.element_exclude_patterns = {}

        if len(args) == 1 and isinstance(args[0], dict):
            # Handle case where a single dict is passed as positional argument
            data = args[0]
            # Set attributes manually
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        elif len(kwargs) == 1 and isinstance(next(iter(kwargs.values())), dict):
            # Handle case where a single dict is passed as keyword argument
            data = next(iter(kwargs.values()))
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        else:
            # Handle normal keyword arguments
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)

        # Compile patterns after initialization
        self._compile_patterns()

    def __post_init__(self):
        """Compile regex patterns after initialization"""
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for filtering"""
        # Compile file filter patterns with error handling
        self.file_include_patterns = []
        for pattern in self.file_filters.get("include", []):
            try:
                self.file_include_patterns.append(re.compile(pattern))
            except re.error as e:
                self.logger.warning("Invalid include pattern '%s': %s", pattern, e)
                # Skip invalid patterns

        self.file_exclude_patterns = []
        for pattern in self.file_filters.get("exclude", []):
            try:
                self.file_exclude_patterns.append(re.compile(pattern))
            except re.error as e:
                self.logger.warning("Invalid exclude pattern '%s': %s", pattern, e)
                # Skip invalid patterns



    @classmethod
    def load(cls, config_file: str) -> "Config":
        """Load configuration from JSON file"""
        if not Path(config_file).exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle backward compatibility: project_roots -> source_folders
            if "project_roots" in data and "source_folders" not in data:
                data["source_folders"] = data.pop("project_roots")

            # Enhanced validation for source_folders
            if "source_folders" not in data:
                raise ValueError("Configuration must contain 'source_folders' field")

            if not isinstance(data["source_folders"], list):
                raise ValueError(f"'source_folders' must be a list, got: {type(data['source_folders'])}")

            if not data["source_folders"]:
                raise ValueError("'source_folders' list cannot be empty")

            # Validate each source folder
            for i, folder in enumerate(data["source_folders"]):
                if not isinstance(folder, str):
                    raise ValueError(f"Source folder at index {i} must be a string, got: {type(folder)}")
                if not folder.strip():
                    raise ValueError(f"Source folder at index {i} cannot be empty or whitespace: {repr(folder)}")

            return cls(**data)

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file {config_file}: {e}")
        except Exception as e:
            raise ValueError(
                f"Failed to load configuration from {config_file}: {e}"
            ) from e

    def save(self, config_file: str) -> None:
        """Save configuration to JSON file"""
        data = {
            "project_name": self.project_name,
            "source_folders": self.source_folders,
            "output_dir": self.output_dir,
            "model_output_path": self.model_output_path,
            "recursive_search": self.recursive_search,
            "include_depth": self.include_depth,
            "include_filter_local_only": self.include_filter_local_only,
            "always_show_includes": self.always_show_includes,
            "convert_empty_class_to_artifact": self.convert_empty_class_to_artifact,
            "max_function_signature_chars": self.max_function_signature_chars,
            "hide_macro_values": self.hide_macro_values,
            "file_filters": self.file_filters,
            "file_specific": self.file_specific,
            "transformations": self.transformations,
        }

        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ValueError(
                f"Failed to save configuration to {config_file}: {e}"
            ) from e

    def has_filters(self) -> bool:
        """Check if configuration has any filters defined"""
        # Check if any file has include_filter defined in file_specific
        has_include_filters = any(
            file_config.get("include_filter") 
            for file_config in self.file_specific.values()
        )
        return bool(self.file_filters or has_include_filters)

    def _should_include_file(self, file_path: str) -> bool:
        """Check if a file should be included based on filters"""
        # Check exclude patterns first
        for pattern in self.file_exclude_patterns:
            if pattern.search(file_path):
                return False

        # If no include patterns, include all files (after exclusions)
        if not self.file_include_patterns:
            return True

        # Check include patterns - file must match at least one
        for pattern in self.file_include_patterns:
            if pattern.search(file_path):
                return True

        return False





    def __eq__(self, other: Any) -> bool:
        """Check if two configurations are equal"""
        if not isinstance(other, Config):
            return False

        return (
            self.project_name == other.project_name
            and self.source_folders == other.source_folders
            and self.output_dir == other.output_dir
            and self.model_output_path == other.model_output_path
            and self.recursive_search == other.recursive_search
            and self.include_depth == other.include_depth
            and self.include_filter_local_only == other.include_filter_local_only
            and self.always_show_includes == other.always_show_includes
            and self.convert_empty_class_to_artifact == other.convert_empty_class_to_artifact
            and self.hide_macro_values == other.hide_macro_values
            and self.file_filters == other.file_filters
            and self.file_specific == other.file_specific
            and self.transformations == other.transformations
        )

    def __repr__(self) -> str:
        """String representation of the configuration"""
        return (
            f"Config(project_name='{self.project_name}', "
            f"source_folders={self.source_folders})"
        )
