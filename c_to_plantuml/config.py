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

    # Basic configuration
    project_name: str = "Unknown_Project"
    source_folders: List[str] = field(default_factory=list)
    output_dir: str = "./output"
    model_output_path: str = "model.json"
    recursive_search: bool = True
    include_depth: int = 1

    # Filters
    file_filters: Dict[str, List[str]] = field(default_factory=dict)
    element_filters: Dict[str, Dict[str, List[str]]] = field(default_factory=dict)
    include_filters: Dict[str, List[str]] = field(default_factory=dict)

    # Transformations
    transformations: Dict[str, Any] = field(default_factory=dict)

    # Compiled patterns for performance
    file_include_patterns: List[re.Pattern] = field(default_factory=list)
    file_exclude_patterns: List[re.Pattern] = field(default_factory=list)
    element_include_patterns: Dict[str, Dict[str, List[re.Pattern]]] = field(
        default_factory=dict
    )
    element_exclude_patterns: Dict[str, Dict[str, List[re.Pattern]]] = field(
        default_factory=dict
    )

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
        if not hasattr(self, "file_filters"):
            self.file_filters = {}
        if not hasattr(self, "element_filters"):
            self.element_filters = {}
        if not hasattr(self, "include_filters"):
            self.include_filters = {}
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

        # Compile element filter patterns with error handling
        self.element_include_patterns = {}
        self.element_exclude_patterns = {}

        for element_type, filters in self.element_filters.items():
            self.element_include_patterns[element_type] = []
            for pattern in filters.get("include", []):
                try:
                    self.element_include_patterns[element_type].append(
                        re.compile(pattern)
                    )
                except re.error as e:
                    self.logger.warning(
                        "Invalid %s include pattern '%s': %s", element_type, pattern, e
                    )
                    # Skip invalid patterns

            self.element_exclude_patterns[element_type] = []
            for pattern in filters.get("exclude", []):
                try:
                    self.element_exclude_patterns[element_type].append(
                        re.compile(pattern)
                    )
                except re.error as e:
                    self.logger.warning(
                        "Invalid %s exclude pattern '%s': %s", element_type, pattern, e
                    )
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

            # Validate required fields
            if "source_folders" not in data:
                raise ValueError("Configuration must contain 'source_folders' field")

            if not isinstance(data["source_folders"], list):
                raise ValueError("'source_folders' must be a list")

            return cls(**data)

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
            "file_filters": self.file_filters,
            "element_filters": self.element_filters,
            "include_filters": self.include_filters,
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
        return bool(self.file_filters or self.element_filters or self.include_filters)

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

    def _apply_element_filters(self, file_model) -> Any:
        """Apply element filters to a file model"""

        # Create a copy of the file model to avoid modifying the original
        filtered_model = FileModel(
            file_path=file_model.file_path,
            structs=file_model.structs.copy(),
            enums=file_model.enums.copy(),
            unions=file_model.unions.copy(),
            functions=file_model.functions.copy(),
            globals=file_model.globals.copy(),
            includes=file_model.includes.copy(),
            macros=file_model.macros.copy(),
            aliases=file_model.aliases.copy(),
            # typedef_relations removed - tag names are now in struct/enum/union
        )

        # Filter structs
        if "structs" in self.element_filters:
            filtered_model.structs = self._filter_dict(
                filtered_model.structs, self.element_filters["structs"]
            )

        # Filter enums
        if "enums" in self.element_filters:
            filtered_model.enums = self._filter_dict(
                filtered_model.enums, self.element_filters["enums"]
            )

        # Filter unions
        if "unions" in self.element_filters:
            filtered_model.unions = self._filter_dict(
                filtered_model.unions, self.element_filters["unions"]
            )

        # Filter functions
        if "functions" in self.element_filters:
            filtered_model.functions = self._filter_list(
                filtered_model.functions,
                self.element_filters["functions"],
                key=lambda f: f.name,
            )

        # Filter globals
        if "globals" in self.element_filters:
            filtered_model.globals = self._filter_list(
                filtered_model.globals,
                self.element_filters["globals"],
                key=lambda g: g.name,
            )

        # Filter macros
        if "macros" in self.element_filters:
            filtered_model.macros = self._filter_list(
                filtered_model.macros, self.element_filters["macros"]
            )

        # Filter aliases
        if "aliases" in self.element_filters:
            filtered_model.aliases = self._filter_dict(
                filtered_model.aliases, self.element_filters["aliases"]
            )

        return filtered_model

    def _filter_dict(self, items: dict, filters: dict) -> dict:
        """Filter dictionary items based on include/exclude patterns"""
        include_patterns = [
            re.compile(pattern) for pattern in filters.get("include", [])
        ]
        exclude_patterns = [
            re.compile(pattern) for pattern in filters.get("exclude", [])
        ]

        filtered_items = {}

        for name, item in items.items():
            # Check include patterns
            if include_patterns:
                should_include = False
                for pattern in include_patterns:
                    if pattern.search(name):
                        should_include = True
                        break
                if not should_include:
                    continue

            # Check exclude patterns
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern.search(name):
                    should_exclude = True
                    break
            if should_exclude:
                continue

            filtered_items[name] = item

        return filtered_items

    def _filter_list(self, items: list, filters: dict, key=None) -> list:
        """Filter list items based on include/exclude patterns"""
        include_patterns = [
            re.compile(pattern) for pattern in filters.get("include", [])
        ]
        exclude_patterns = [
            re.compile(pattern) for pattern in filters.get("exclude", [])
        ]

        filtered_items = []

        for item in items:
            # Get the name to check against patterns
            if key:
                name = key(item)
            else:
                name = str(item)

            # Check include patterns
            if include_patterns:
                should_include = False
                for pattern in include_patterns:
                    if pattern.search(name):
                        should_include = True
                        break
                if not should_include:
                    continue

            # Check exclude patterns
            should_exclude = False
            for pattern in exclude_patterns:
                if pattern.search(name):
                    should_exclude = True
                    break
            if should_exclude:
                continue

            filtered_items.append(item)

        return filtered_items

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the configuration"""
        return {
            "project_name": self.project_name,
            "source_folders": self.source_folders,
            "output_dir": self.output_dir,
            "recursive_search": self.recursive_search,
            "include_depth": self.include_depth,
            "has_file_filters": bool(self.file_filters),
            "has_element_filters": bool(self.element_filters),
            "has_include_filters": bool(self.include_filters),
            "has_transformations": bool(self.transformations),
        }

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
            and self.file_filters == other.file_filters
            and self.element_filters == other.element_filters
            and self.include_filters == other.include_filters
            and self.transformations == other.transformations
        )

    def __repr__(self) -> str:
        """String representation of the configuration"""
        return (
            f"Config(project_name='{self.project_name}', "
            f"source_folders={self.source_folders})"
        )
