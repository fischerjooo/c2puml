#!/usr/bin/env python3
"""
Transformer module for C to PlantUML converter - Step 2: Transform model based on
configuration
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
            output_file: Output transformed model file path (optional, defaults to
                model_file)

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
                source_folder=data.get("source_folder", data.get("project_root", "")),
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

        # Apply include filters for each root file
        include_filters = config.get("include_filters", {})
        if include_filters:
            model = self._apply_include_filters(model, include_filters)

        # Apply transformations with file selection support
        if "transformations" in config:
            model = self._apply_model_transformations(model, config["transformations"])

        # Apply include depth processing with include_filters support
        if "include_depth" in config and config["include_depth"] > 1:
            model = self._process_include_relations(
                model, config["include_depth"], include_filters
            )

        self.logger.info(
            "Transformations complete. Model now has %d files", len(model.files)
        )
        return model

    def _apply_file_filters(
        self, model: ProjectModel, filters: Dict[str, Any]
    ) -> ProjectModel:
        """Apply user-configured file-level filters (important filtering already
        done in parser)"""
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

    def _apply_include_filters(
        self, model: ProjectModel, include_filters: Dict[str, List[str]]
    ) -> ProjectModel:
        """Apply include filters for each root file based on regex patterns"""
        self.logger.info(
            "Applying include filters for %d root files", len(include_filters)
        )

        # Compile regex patterns for each root file
        compiled_filters = {}
        for root_file, patterns in include_filters.items():
            try:
                compiled_filters[root_file] = [
                    re.compile(pattern) for pattern in patterns
                ]
                self.logger.debug(
                    "Compiled %d patterns for root file: %s", len(patterns), root_file
                )
            except re.error as e:
                self.logger.warning(
                    "Invalid regex pattern for root file %s: %s", root_file, e
                )
                # Skip invalid patterns for this root file
                continue

        if not compiled_filters:
            self.logger.warning(
                "No valid include filters found, skipping include filtering"
            )
            return model

        # Create a mapping from header files to their root C files
        header_to_root = self._create_header_to_root_mapping(model)

        # Apply filters to each file in the model
        for file_path, file_model in model.files.items():
            # Find the root file for this file
            root_file = self._find_root_file_with_mapping(
                file_path, file_model, header_to_root
            )

            if root_file in compiled_filters:
                # Apply the filters for this root file
                self._filter_file_includes(
                    file_model, compiled_filters[root_file], root_file
                )

        return model

    def _create_header_to_root_mapping(self, model: ProjectModel) -> Dict[str, str]:
        """Create a mapping from header files to their root C files"""
        header_to_root = {}

        # For now, use a simple approach: all header files are associated with the first C file
        # This is a limitation of the current implementation
        c_files = [f for f in model.files.keys() if f.endswith(".c")]
        if c_files:
            root_c_file = c_files[0]  # Use the first C file as root
            for file_path, file_model in model.files.items():
                if file_model.name.endswith(".c"):
                    header_to_root[file_model.name] = file_model.name
                else:
                    # Associate all header files with the root C file
                    header_to_root[file_model.name] = root_c_file

        return header_to_root

    def _find_root_file_with_mapping(
        self, file_path: str, file_model: FileModel, header_to_root: Dict[str, str]
    ) -> str:
        """Find the root C file for a given file using the header mapping"""
        if file_model.name.endswith(".c"):
            return file_model.name

        # For header files, use the mapping
        return header_to_root.get(file_model.name, file_model.name)

    def _find_root_file(self, file_path: str, file_model: FileModel) -> str:
        """Find the root C file for a given file"""
        filename = Path(file_path).name

        # If it's a .c file, it's its own root
        if filename.endswith(".c"):
            return filename

        # For header files, we need to find the corresponding .c file
        # This is a simplified approach - in a real scenario, we might need
        # more sophisticated logic to determine which .c file includes this header
        # For now, we'll look for a .c file with the same base name
        base_name = Path(file_path).stem

        # Check if there's a corresponding .c file in the same directory
        # This is a heuristic and might need to be enhanced
        if base_name and not filename.startswith("."):
            # For header files, we'll use the first .c file we find as the root
            # This is a limitation of the current approach
            return base_name + ".c"

        # Fallback: use the filename as root (original behavior)
        return filename

    def _filter_file_includes(
        self, file_model: FileModel, patterns: List[re.Pattern], root_file: str
    ) -> None:
        """Filter includes and include_relations for a file based on regex
        patterns"""
        self.logger.debug(
            "Filtering includes for file %s (root: %s)", file_model.name, root_file
        )

        # Filter includes
        original_includes_count = len(file_model.includes)
        filtered_includes = set()

        for include_name in file_model.includes:
            if self._matches_any_pattern(include_name, patterns):
                filtered_includes.add(include_name)
            else:
                self.logger.debug(
                    "Filtered out include: %s (root: %s)", include_name, root_file
                )

        file_model.includes = filtered_includes

        # Filter include_relations
        original_relations_count = len(file_model.include_relations)
        filtered_relations = []

        for relation in file_model.include_relations:
            # Check if the included file matches any pattern
            if self._matches_any_pattern(relation.included_file, patterns):
                filtered_relations.append(relation)
            else:
                self.logger.debug(
                    "Filtered out include relation: %s -> %s (root: %s)",
                    relation.source_file,
                    relation.included_file,
                    root_file,
                )

        file_model.include_relations = filtered_relations

        self.logger.debug(
            "Include filtering for %s: includes %d->%d, relations %d->%d",
            file_model.name,
            original_includes_count,
            len(file_model.includes),
            original_relations_count,
            len(file_model.include_relations),
        )

    def _matches_any_pattern(self, text: str, patterns: List[re.Pattern]) -> bool:
        """Check if text matches any of the given regex patterns"""
        return any(pattern.search(text) for pattern in patterns)

    def _should_process_include(
        self,
        file_model: FileModel,
        include_name: str,
        compiled_filters: Dict[str, List[re.Pattern]],
    ) -> bool:
        """Check if an include should be processed based on include_filters"""
        # Find the root file for this file
        root_file = self._find_root_file(file_model.name, file_model)

        # If no filters for this root file, allow all includes
        if root_file not in compiled_filters:
            return True

        # Check if the include name matches any pattern for this root file
        patterns = compiled_filters[root_file]
        return self._matches_any_pattern(include_name, patterns)

    def _should_process_include_with_root(
        self,
        include_name: str,
        compiled_filters: Dict[str, List[re.Pattern]],
        root_file: str,
    ) -> bool:
        """Check if an include should be processed based on include_filters with explicit root file"""
        # If no filters for this root file, allow all includes
        if root_file not in compiled_filters:
            return True

        # Check if the include name matches any pattern for this root file
        patterns = compiled_filters[root_file]
        return self._matches_any_pattern(include_name, patterns)

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
                # This would handle adding new elements like structs, enums,
                # functions, etc.
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
                # This would handle removing elements like structs, enums,
                # functions, etc.
                self.logger.debug("Applying removals to file: %s", file_path)

        return model

    def _process_include_relations(
        self,
        model: ProjectModel,
        max_depth: int,
        include_filters: Dict[str, List[str]] = None,
    ) -> ProjectModel:
        """Process include relationships up to specified depth with include_filters support"""
        self.logger.info("Processing include relations with max depth: %d", max_depth)

        # Compile include_filters patterns if provided
        compiled_filters = {}
        if include_filters:
            for root_file, patterns in include_filters.items():
                try:
                    compiled_filters[root_file] = [
                        re.compile(pattern) for pattern in patterns
                    ]
                    self.logger.debug(
                        "Compiled %d patterns for root file: %s",
                        len(patterns),
                        root_file,
                    )
                except re.error as e:
                    self.logger.warning(
                        "Invalid regex pattern for root file %s: %s", root_file, e
                    )
                    continue

        # Create a mapping of filenames to their models for quick lookup
        # Since we now use relative paths as keys, we need to map by filename
        # for include processing
        file_map = {}
        for file_model in model.files.values():
            filename = Path(file_model.name).name
            file_map[filename] = file_model

        # Clear all include_relations first
        for file_model in model.files.values():
            file_model.include_relations = []

        # Only process .c files as root files for include_relations
        # This ensures include_relations are only populated for .c files
        for file_path, file_model in model.files.items():
            if file_model.name.endswith(".c"):
                root_file = Path(file_model.name).name

                # Get compiled filters for this specific .c file
                root_filters = (
                    compiled_filters.get(root_file, []) if compiled_filters else []
                )

                # Process includes and collect all relations for this .c file
                self._collect_include_relations_for_c_file(
                    file_model,
                    file_map,
                    max_depth,
                    1,
                    set(),
                    root_filters,
                    model.source_folder,
                )

        return model

    def _collect_include_relations_for_c_file(
        self,
        file_model: FileModel,
        file_map: Dict[str, FileModel],
        max_depth: int,
        current_depth: int,
        visited: Set[str],
        compiled_filters: List[re.Pattern],
        source_folder: str,
        root_c_file: FileModel = None,
    ) -> None:
        """Recursively process includes for a .c file and collect all include_relations"""
        if current_depth > max_depth or file_model.name in visited:
            return

        visited.add(file_model.name)

        # If this is the first call, set the root .c file
        if root_c_file is None:
            root_c_file = file_model

        # Process each include
        for include_name in file_model.includes:
            # Directly check if the included file exists in our file_map
            # This is more reliable than file path resolution since we already
            # have all project files mapped by filename
            if include_name in file_map:
                # Prevent self-referencing include relations
                if file_model.name == include_name:
                    self.logger.debug(
                        "Skipping self-include relation for %s", file_model.name
                    )
                    continue

                # Check if this include relation already exists in the root .c file to prevent cycles
                relation_exists = any(
                    rel.source_file == file_model.name
                    and rel.included_file == include_name
                    for rel in root_c_file.include_relations
                )

                if relation_exists:
                    self.logger.debug(
                        "Cyclic include detected and skipped: %s -> %s",
                        file_model.name,
                        include_name,
                    )
                    continue

                # Check include_filters before processing this include
                if compiled_filters and not self._matches_any_pattern(
                    include_name, compiled_filters
                ):
                    self.logger.debug(
                        "Skipping filtered include: %s -> %s",
                        file_model.name,
                        include_name,
                    )
                    continue

                # Create include relation using FileModel names for consistency
                # Always add to the root .c file, regardless of which file we're currently processing
                source_file = file_model.name
                included_file = file_map[include_name].name

                include_relation = IncludeRelation(
                    source_file=source_file,
                    included_file=included_file,
                    depth=current_depth,
                )
                root_c_file.include_relations.append(include_relation)

                # Recursively process the included file
                included_file_model = file_map[include_name]
                self._collect_include_relations_for_c_file(
                    included_file_model,
                    file_map,
                    max_depth,
                    current_depth + 1,
                    visited,
                    compiled_filters,
                    source_folder,
                    root_c_file,  # Pass the root .c file to maintain context
                )

    def _find_included_file(
        self, include_name: str, source_folder: str
    ) -> Optional[str]:
        """Find the actual file path for an include using simplified filename
        matching"""
        # Since we now use filenames as keys, we can simplify this significantly
        # Just return the filename if it exists in the project files

        # Common include paths to search
        search_paths = [
            Path(source_folder),
            Path(source_folder) / "include",
            Path(source_folder) / "src",
            Path(source_folder) / "lib",
            Path(source_folder) / "headers",
        ]

        # Try different extensions
        extensions = [".h", ".hpp", ".hxx", ""]

        for search_path in search_paths:
            if not search_path.exists():
                continue

            for ext in extensions:
                file_path = search_path / f"{include_name}{ext}"
                if file_path.exists():
                    # Always return filename for simplified tracking using FileModel.name
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
