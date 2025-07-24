#!/usr/bin/env python3
"""
Transformer module for C to PlantUML converter - Step 2: Transform model based on configuration
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .models import (
    FileModel,
    ProjectModel,
    IncludeRelation,
    Alias,
    Enum,
    EnumValue,
    Field,
    Function,
    Struct,
    Union,
)


class Transformer:
    """Main transformer class for Step 2: Transform model based on configuration"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def transform(
        self, model_file: str, config_file: str, output_file: str = None
    ) -> str:
        """
        Step 2: Transform model based on configuration

        Args:
            model_file: Input JSON model file path
            config_file: Configuration file path
            output_file: Output transformed model file path (optional, defaults to model_file)

        Returns:
            Path to the transformed model file
        """
        self.logger.info("Step 2: Transforming model: %s", model_file)

        # Load the model
        model = self._load_model(model_file)

        # Load configuration
        config = self._load_config(config_file)

        # Apply transformations
        transformed_model = self._apply_transformations(model, config)

        # Save transformed model
        output_path = output_file or model_file
        self._save_model(transformed_model, output_path)

        self.logger.info("Step 2 complete! Transformed model saved to: %s", output_path)

        return output_path

    def _load_model(self, model_file: str) -> ProjectModel:
        """Load model from JSON file"""
        if not Path(model_file).exists():
            raise FileNotFoundError(f"Model file not found: {model_file}")

        try:
            with open(model_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Convert back to ProjectModel
            model = ProjectModel(
                project_name=data["project_name"],
                project_root=data["project_root"],
                files={},
            )

            # Convert file data back to FileModel objects
            for file_path, file_data in data["files"].items():
                model.files[file_path] = self._dict_to_file_model(file_data)

            self.logger.debug("Loaded model with %d files", len(model.files))
            return model

        except Exception as e:
            raise ValueError(f"Failed to load model from {model_file}: {e}") from e

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        if not Path(config_file).exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            self.logger.debug("Loaded configuration from: %s", config_file)
            return config

        except Exception as e:
            raise ValueError(
                f"Failed to load configuration from {config_file}: {e}"
            ) from e

    def _apply_transformations(
        self, model: ProjectModel, config: Dict[str, Any]
    ) -> ProjectModel:
        """Apply all configured transformations to the model"""
        self.logger.info("Applying transformations to model")

        # Apply comprehensive file filtering (moved from parser)
        if "file_filters" in config:
            model = self._apply_file_filters(model, config["file_filters"])

        # Apply element filters
        if "element_filters" in config:
            model = self._apply_element_filters(model, config["element_filters"])

        # Apply transformations with file selection support
        if "transformations" in config:
            model = self._apply_model_transformations(model, config["transformations"])

        # Apply include depth processing
        if "include_depth" in config and config["include_depth"] > 1:
            model = self._process_include_relations(model, config["include_depth"])

        self.logger.info(
            "Transformations complete. Model now has %d files", len(model.files)
        )
        return model

    def _apply_file_filters(
        self, model: ProjectModel, filters: Dict[str, Any]
    ) -> ProjectModel:
        """Apply user-configured file-level filters (important filtering already done in parser)"""
        include_patterns = self._compile_patterns(filters.get("include", []))
        exclude_patterns = self._compile_patterns(filters.get("exclude", []))

        if not include_patterns and not exclude_patterns:
            return model

        filtered_files = {}
        for file_path, file_model in model.files.items():
            if self._should_include_file(file_path, include_patterns, exclude_patterns):
                filtered_files[file_path] = file_model

        model.files = filtered_files
        self.logger.debug(
            "User file filtering: %d files after filtering", len(model.files)
        )
        return model

    def _apply_element_filters(
        self, model: ProjectModel, filters: Dict[str, Any]
    ) -> ProjectModel:
        """Apply element-level filters"""
        for file_path, file_model in model.files.items():
            model.files[file_path] = self._filter_file_elements(file_model, filters)

        return model

    def _filter_file_elements(
        self, file_model: FileModel, filters: Dict[str, Any]
    ) -> FileModel:
        """Filter elements within a file"""
        # Filter structs
        if "structs" in filters:
            file_model.structs = self._filter_dict(
                file_model.structs, filters["structs"]
            )

        # Filter enums
        if "enums" in filters:
            file_model.enums = self._filter_dict(file_model.enums, filters["enums"])

        # Filter unions
        if "unions" in filters:
            file_model.unions = self._filter_dict(file_model.unions, filters["unions"])

        # Filter functions
        if "functions" in filters:
            file_model.functions = self._filter_list(
                file_model.functions, filters["functions"], key=lambda f: f.name
            )

        # Filter globals
        if "globals" in filters:
            file_model.globals = self._filter_list(
                file_model.globals, filters["globals"], key=lambda g: g.name
            )

        # Filter macros
        if "macros" in filters:
            file_model.macros = self._filter_list(file_model.macros, filters["macros"])

        # Filter aliases (replaces typedefs)
        if "aliases" in filters:
            file_model.aliases = self._filter_dict(
                file_model.aliases, filters["aliases"]
            )

        return file_model

    def _apply_model_transformations(
        self, model: ProjectModel, transformations: Dict[str, Any]
    ) -> ProjectModel:
        """Apply model-level transformations with file selection support"""
        # Get file selection configuration
        file_selection = transformations.get("file_selection", {})
        selected_files = file_selection.get("selected_files", [])

        # Determine which files to apply transformations to
        # If selected_files is empty or not specified, apply to all files
        if not selected_files:
            target_files = set(model.files.keys())
        else:
            # Apply only to selected files
            target_files = set()
            for pattern in selected_files:
                for file_path in model.files.keys():
                    if self._matches_pattern(file_path, pattern):
                        target_files.add(file_path)

        self.logger.debug(
            "Applying transformations to %d files: %s",
            len(target_files),
            list(target_files),
        )

        # Rename elements
        if "rename" in transformations:
            model = self._apply_renaming(model, transformations["rename"], target_files)

        # Add elements
        if "add" in transformations:
            model = self._apply_additions(model, transformations["add"], target_files)

        # Remove elements
        if "remove" in transformations:
            model = self._apply_removals(model, transformations["remove"], target_files)

        return model

    def _apply_renaming(
        self, model: ProjectModel, rename_config: Dict[str, Any], target_files: Set[str]
    ) -> ProjectModel:
        """Apply renaming transformations to selected files"""
        self.logger.debug(
            "Applying renaming transformations to %d files", len(target_files)
        )

        # Apply renaming only to target files
        for file_path in target_files:
            if file_path in model.files:
                # Apply renaming logic here
                # This would handle renaming structs, enums, functions, etc.
                self.logger.debug("Applying renaming to file: %s", file_path)

        return model

    def _apply_additions(
        self, model: ProjectModel, add_config: Dict[str, Any], target_files: Set[str]
    ) -> ProjectModel:
        """Apply addition transformations to selected files"""
        self.logger.debug(
            "Applying addition transformations to %d files", len(target_files)
        )

        # Apply additions only to target files
        for file_path in target_files:
            if file_path in model.files:
                # Apply addition logic here
                # This would handle adding new elements like structs, enums, functions, etc.
                self.logger.debug("Applying additions to file: %s", file_path)

        return model

    def _apply_removals(
        self, model: ProjectModel, remove_config: Dict[str, Any], target_files: Set[str]
    ) -> ProjectModel:
        """Apply removal transformations to selected files"""
        self.logger.debug(
            "Applying removal transformations to %d files", len(target_files)
        )

        # Apply removals only to target files
        for file_path in target_files:
            if file_path in model.files:
                # Apply removal logic here
                # This would handle removing elements like structs, enums, functions, etc.
                self.logger.debug("Applying removals to file: %s", file_path)

        return model

    def _process_include_relations(
        self, model: ProjectModel, max_depth: int
    ) -> ProjectModel:
        """Process include relationships up to specified depth"""
        self.logger.info("Processing include relations with max depth: %d", max_depth)

        # Create a mapping of filenames to their models for quick lookup
        file_map = {
            file_model.relative_path: file_model for file_model in model.files.values()
        }

        # Process each file's includes
        for file_path, file_model in model.files.items():
            self._process_file_includes(file_model, file_map, max_depth, 1, set())

        return model

    def _process_file_includes(
        self,
        file_model: FileModel,
        file_map: Dict[str, FileModel],
        max_depth: int,
        current_depth: int,
        visited: Set[str],
    ) -> None:
        """Recursively process includes for a file using filename-based matching"""
        if current_depth > max_depth or file_model.relative_path in visited:
            return

        visited.add(file_model.relative_path)

        # Process each include
        for include_name in file_model.includes:
            # Try to find the included file
            included_filename = self._find_included_file(
                include_name, file_model.project_root
            )

            if included_filename and included_filename in file_map:
                # Prevent self-referencing include relations
                if file_model.relative_path == included_filename:
                    self.logger.debug(
                        "Skipping self-include relation for %s", file_model.relative_path
                    )
                    continue

                # Check if this include relation already exists to prevent cycles
                relation_exists = any(
                    rel.source_file == file_model.relative_path
                    and rel.included_file == included_filename
                    for rel in file_model.include_relations
                )

                if relation_exists:
                    self.logger.debug(
                        "Cyclic include detected and skipped: %s -> %s",
                        file_model.relative_path,
                        included_filename,
                    )
                    continue

                # Create include relation using filenames
                include_relation = IncludeRelation(
                    source_file=file_model.relative_path,
                    included_file=included_filename,
                    depth=current_depth,
                )
                file_model.include_relations.append(include_relation)

                # Recursively process the included file
                included_file_model = file_map[included_filename]
                self._process_file_includes(
                    included_file_model,
                    file_map,
                    max_depth,
                    current_depth + 1,
                    visited.copy(),
                )

    def _find_included_file(
        self, include_name: str, project_root: str
    ) -> Optional[str]:
        """Find the actual file path for an include using simplified filename matching"""
        # Since we now use filenames as keys, we can simplify this significantly
        # Just return the filename if it exists in the project files
        
        # Common include paths to search
        search_paths = [
            Path(project_root),
            Path(project_root) / "include",
            Path(project_root) / "src",
            Path(project_root) / "lib",
            Path(project_root) / "headers",
        ]

        # Try different extensions
        extensions = [".h", ".hpp", ".hxx", ""]

        for search_path in search_paths:
            if not search_path.exists():
                continue

            for ext in extensions:
                file_path = search_path / f"{include_name}{ext}"
                if file_path.exists():
                    # Return filename instead of full path for simplified tracking
                    return file_path.name

        return None

    def _matches_pattern(self, file_path: str, pattern: str) -> bool:
        """Check if a file path matches a pattern"""
        try:
            return bool(re.search(pattern, file_path))
        except re.error:
            self.logger.warning("Invalid pattern '%s' for file matching", pattern)
            return False

    def _compile_patterns(self, patterns: List[str]) -> List[re.Pattern]:
        """Compile regex patterns with error handling"""
        compiled_patterns = []

        for pattern in patterns:
            try:
                compiled_patterns.append(re.compile(pattern))
            except re.error as e:
                self.logger.warning("Invalid regex pattern '%s': %s", pattern, e)

        return compiled_patterns

    def _should_include_file(
        self,
        file_path: str,
        include_patterns: List[re.Pattern],
        exclude_patterns: List[re.Pattern],
    ) -> bool:
        """Check if a file should be included based on filters"""
        # Check include patterns
        if include_patterns:
            if not any(pattern.search(file_path) for pattern in include_patterns):
                return False

        # Check exclude patterns
        if exclude_patterns:
            if any(pattern.search(file_path) for pattern in exclude_patterns):
                return False

        return True

    def _filter_dict(self, items: Dict, filters: Dict) -> Dict:
        """Filter a dictionary based on include/exclude patterns"""
        include_patterns = self._compile_patterns(filters.get("include", []))
        exclude_patterns = self._compile_patterns(filters.get("exclude", []))

        filtered = {}
        for name, item in items.items():
            # Check include patterns
            if include_patterns:
                if not any(pattern.search(name) for pattern in include_patterns):
                    continue

            # Check exclude patterns
            if exclude_patterns:
                if any(pattern.search(name) for pattern in exclude_patterns):
                    continue

            filtered[name] = item

        return filtered

    def _filter_list(self, items: List, filters: Dict, key=None) -> List:
        """Filter a list based on include/exclude patterns"""
        include_patterns = self._compile_patterns(filters.get("include", []))
        exclude_patterns = self._compile_patterns(filters.get("exclude", []))

        filtered = []
        for item in items:
            item_name = key(item) if key else str(item)

            # Check include patterns
            if include_patterns:
                if not any(pattern.search(item_name) for pattern in include_patterns):
                    continue

            # Check exclude patterns
            if exclude_patterns:
                if any(pattern.search(item_name) for pattern in exclude_patterns):
                    continue

            filtered.append(item)

        return filtered

    def _dict_to_file_model(self, data: Dict) -> FileModel:
        """Convert dictionary back to FileModel"""

        # Convert structs
        structs = {}
        for name, struct_data in data.get("structs", {}).items():
            fields = [
                Field(f["name"], f["type"]) for f in struct_data.get("fields", [])
            ]
            structs[name] = Struct(
                name,
                fields,
                struct_data.get("methods", []),
                struct_data.get("tag_name", ""),
                struct_data.get("uses", []),
            )

        # Convert enums
        enums = {}
        for name, enum_data in data.get("enums", {}).items():
            values = []
            for value_data in enum_data.get("values", []):
                if isinstance(value_data, dict):
                    values.append(
                        EnumValue(value_data["name"], value_data.get("value"))
                    )
                else:
                    values.append(EnumValue(value_data))
            enums[name] = Enum(name, values)

        # Convert unions
        unions = {}
        for name, union_data in data.get("unions", {}).items():
            fields = [Field(f["name"], f["type"]) for f in union_data.get("fields", [])]
            unions[name] = Union(
                name, fields, union_data.get("tag_name", ""), union_data.get("uses", [])
            )

        # Convert aliases
        aliases = {}
        for name, alias_data in data.get("aliases", {}).items():
            if isinstance(alias_data, dict):
                aliases[name] = Alias(
                    alias_data.get("name", name),
                    alias_data.get("original_type", ""),
                    alias_data.get("uses", []),
                )
            else:
                # Handle legacy format where aliases was Dict[str, str]
                aliases[name] = Alias(name, alias_data, [])

        # Convert functions
        functions = []
        for func_data in data.get("functions", []):
            parameters = [
                Field(p["name"], p["type"]) for p in func_data.get("parameters", [])
            ]
            functions.append(
                Function(
                    func_data["name"],
                    func_data["return_type"],
                    parameters,
                    is_static=func_data.get("is_static", False),
                    is_declaration=func_data.get("is_declaration", False),
                )
            )

        # Convert globals
        globals_list = []
        for global_data in data.get("globals", []):
            globals_list.append(Field(global_data["name"], global_data["type"]))

        return FileModel(
            file_path=data["file_path"],
            relative_path=data["relative_path"],
            project_root=data["project_root"],
            encoding_used=data["encoding_used"],
            structs=structs,
            enums=enums,
            unions=unions,
            functions=functions,
            globals=globals_list,
            includes=data.get("includes", []),
            macros=data.get("macros", []),
            aliases=aliases,
        )

    def _save_model(self, model: ProjectModel, output_file: str) -> None:
        """Save model to JSON file"""
        try:
            model.save(output_file)
            self.logger.debug("Model saved to: %s", output_file)
        except Exception as e:
            raise ValueError(f"Failed to save model to {output_file}: {e}") from e
