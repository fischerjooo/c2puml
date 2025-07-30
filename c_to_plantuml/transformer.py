#!/usr/bin/env python3
"""
Transformer module for C to PlantUML converter - Step 2: Transform model based on
configuration
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .models import (
    Alias,
    Enum,
    EnumValue,
    Field,
    FileModel,
    Function,
    IncludeRelation,
    ProjectModel,
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

        # Support backward compatibility - convert single 'transformations' to container format
        config = self._ensure_backward_compatibility(config)

        # Discover and apply transformation containers in alphabetical order
        transformation_containers = self._discover_transformation_containers(config)
        
        if transformation_containers:
            for container_name, transformation_config in transformation_containers:
                self.logger.info("Applying transformation container: %s", container_name)
                model = self._apply_single_transformation_container(model, transformation_config, container_name)
                
                # Log model state after each container
                total_elements = sum(
                    len(file_model.structs) + len(file_model.enums) + len(file_model.unions) +
                    len(file_model.functions) + len(file_model.globals) + len(file_model.macros) +
                    len(file_model.aliases)
                    for file_model in model.files.values()
                )
                self.logger.info(
                    "After %s: model contains %d files with %d total elements",
                    container_name, len(model.files), total_elements
                )

        # Apply include depth processing with file-specific support
        # NOTE: include_filters are used ONLY for generating include_relations, 
        # not for modifying the original includes arrays
        if self._should_process_include_relations(config):
            model = self._process_include_relations_with_file_specific_settings(model, config)

        self.logger.info(
            "Transformations complete. Model now has %d files", len(model.files)
        )
        return model

    def _extract_include_filters_from_config(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract include_filters from file_specific configuration structure"""
        if "file_specific" not in config:
            return {}
        
        include_filters = {}
        for file_name, file_config in config["file_specific"].items():
            if "include_filter" in file_config:
                include_filters[file_name] = file_config["include_filter"]
        return include_filters

    def _should_process_include_relations(self, config: Dict[str, Any]) -> bool:
        """Check if include relations should be processed based on global or file-specific settings"""
        # Check global include_depth
        if "include_depth" in config and config["include_depth"] > 1:
            return True
        
        # Check file-specific include_depth settings
        if "file_specific" in config:
            for file_config in config["file_specific"].values():
                if "include_depth" in file_config and file_config["include_depth"] > 1:
                    return True
        
        return False

    def _discover_transformation_containers(self, config: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Discover all transformation containers and sort them alphabetically
        
        Returns:
            List of (container_name, transformation_config) tuples sorted by name
        """
        transformation_containers = []
        
        for key, value in config.items():
            if key.startswith("transformations") and isinstance(value, dict):
                transformation_containers.append((key, value))
        
        # Sort alphabetically by container name
        transformation_containers.sort(key=lambda x: x[0])
        
        self.logger.info(
            "Discovered %d transformation containers: %s",
            len(transformation_containers),
            [name for name, _ in transformation_containers]
        )
        
        return transformation_containers

    def _ensure_backward_compatibility(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure backward compatibility by converting old single 'transformations' 
        to new container format
        
        Args:
            config: Original configuration
            
        Returns:
            Updated configuration with container format
        """
        # Make a copy to avoid modifying the original
        config = config.copy()
        
        # Check if old format is used (single 'transformations' key)
        if "transformations" in config and not any(
            key.startswith("transformations_") for key in config.keys()
        ):
            self.logger.info("Converting legacy 'transformations' format to container format")
            
            # Move old transformations to a default container
            old_transformations = config.pop("transformations")
            config["transformations_00_default"] = old_transformations
            
            self.logger.debug("Converted to container: transformations_00_default")
        
        return config

    def _apply_single_transformation_container(
        self, 
        model: ProjectModel, 
        transformation_config: Dict[str, Any], 
        container_name: str
    ) -> ProjectModel:
        """
        Apply a single transformation container
        
        Args:
            model: Project model to transform
            transformation_config: Single transformation container configuration
            container_name: Name of the container for logging
            
        Returns:
            Transformed project model
        """
        self.logger.debug("Processing transformation container: %s", container_name)
        
        # Get file selection configuration for this container
        selected_files = transformation_config.get("file_selection", [])
        
        # Validate that file_selection is a list
        if not isinstance(selected_files, list):
            selected_files = []
            self.logger.warning("Invalid file_selection format, must be a list, defaulting to empty list")
        
        # Determine which files to apply transformations to
        if not selected_files:
            target_files = set(model.files.keys())
            self.logger.debug("No file selection specified, applying to all %d files", len(target_files))
        else:
            target_files = set()
            for pattern in selected_files:
                for file_path in model.files.keys():
                    if self._matches_pattern(file_path, pattern):
                        target_files.add(file_path)
            
            self.logger.debug(
                "File selection patterns %s matched %d files: %s",
                selected_files, len(target_files), list(target_files)
            )
        
        # Apply transformations in specific order: remove -> rename -> add
        # This order ensures that removals happen first, then renaming with deduplication,
        # then additions to the cleaned model
        
        if "remove" in transformation_config:
            self.logger.debug("Applying remove operations for container: %s", container_name)
            model = self._apply_removals(model, transformation_config["remove"], target_files)
        
        if "rename" in transformation_config:
            self.logger.debug("Applying rename operations for container: %s", container_name)
            model = self._apply_renaming(model, transformation_config["rename"], target_files)
        
        if "add" in transformation_config:
            self.logger.debug("Applying add operations for container: %s", container_name)
            model = self._apply_additions(model, transformation_config["add"], target_files)
        
        return model

    def _process_include_relations_with_file_specific_settings(
        self, model: ProjectModel, config: Dict[str, Any]
    ) -> ProjectModel:
        """Process include relations with support for file-specific include_depth and include_filter"""
        global_include_depth = config.get("include_depth", 1)
        file_specific_config = config.get("file_specific", {})
        
        # Clear all include_relations first
        for file_model in model.files.values():
            file_model.include_relations = []

        # Process each .c file individually with its specific settings
        for file_path, file_model in model.files.items():
            if file_model.name.endswith(".c"):
                root_filename = Path(file_model.name).name
                
                # Get file-specific settings or fall back to global
                if root_filename in file_specific_config:
                    file_config = file_specific_config[root_filename]
                    include_depth = file_config.get("include_depth", global_include_depth)
                    include_filter_patterns = file_config.get("include_filter", [])
                else:
                    include_depth = global_include_depth
                    include_filter_patterns = []
                
                # Only process if include_depth > 1
                if include_depth > 1:
                    # Compile include filter patterns
                    compiled_filters = []
                    if include_filter_patterns:
                        try:
                            compiled_filters = [re.compile(pattern) for pattern in include_filter_patterns]
                            self.logger.debug(
                                "Using %d include filter patterns for %s with depth %d", 
                                len(compiled_filters), root_filename, include_depth
                            )
                        except re.error as e:
                            self.logger.warning(
                                "Invalid regex pattern for file %s: %s", root_filename, e
                            )
                            compiled_filters = []
                    
                    # Process this specific file's include relations
                    self._process_single_file_include_relations(
                        model, file_model, include_depth, compiled_filters
                    )

        return model

    def _process_single_file_include_relations(
        self, 
        model: ProjectModel, 
        root_file_model: "FileModel",
        max_depth: int,
        compiled_filters: List[Any]
    ) -> None:
        """Process include relations for a single root file with specific depth and filters"""
        from collections import deque
        
        # Create a mapping of filenames to their models for quick lookup
        file_map = {}
        for file_model in model.files.values():
            filename = Path(file_model.name).name
            file_map[filename] = file_model

        # BFS to process includes up to max_depth
        queue = deque([(root_file_model, 0)])  # (file_model, current_depth)
        processed = set()
        
        while queue:
            current_file, depth = queue.popleft()
            
            if depth >= max_depth:
                continue
                
            current_filename = Path(current_file.name).name
            if current_filename in processed:
                continue
            processed.add(current_filename)
            
            # Process includes for this file
            for include_name in current_file.includes:
                # Apply include filters if they exist
                if compiled_filters:
                    if not any(pattern.search(include_name) for pattern in compiled_filters):
                        continue
                
                # Create include relation
                relation = IncludeRelation(
                    source_file=current_filename,
                    included_file=include_name,
                    depth=depth + 1
                )
                
                # Add to the root file's include_relations
                root_file_model.include_relations.append(relation)
                
                # Continue processing if we haven't reached max depth and the included file exists
                if depth + 1 < max_depth and include_name in file_map:
                    queue.append((file_map[include_name], depth + 1))

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





    def _apply_model_transformations(
        self, model: ProjectModel, transformations: Dict[str, Any]
    ) -> ProjectModel:
        """Apply model-level transformations with file selection support"""
        # Get file selection configuration
        selected_files = transformations.get("file_selection", [])
        
        # Validate that file_selection is a list
        if not isinstance(selected_files, list):
            selected_files = []
            self.logger.warning("Invalid file_selection format, must be a list, defaulting to empty list")

        # Determine which files to apply transformations to
        # If selected_files is empty or not specified, apply to all files
        if not selected_files:
            target_files = set(model.files.keys())
            self.logger.debug("No file selection specified, applying to all %d files", len(target_files))
        else:
            # Apply only to selected files
            target_files = set()
            for pattern in selected_files:
                for file_path in model.files.keys():
                    if self._matches_pattern(file_path, pattern):
                        target_files.add(file_path)
            
            self.logger.debug(
                "File selection patterns %s matched %d files: %s",
                selected_files, len(target_files), list(target_files)
            )

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
                file_model = model.files[file_path]
                self.logger.debug("Applying renaming to file: %s", file_path)
                
                # Apply each type of renaming
                if "typedef" in rename_config:
                    self._rename_typedefs(file_model, rename_config["typedef"])
                
                if "functions" in rename_config:
                    self._rename_functions(file_model, rename_config["functions"])
                
                if "macros" in rename_config:
                    self._rename_macros(file_model, rename_config["macros"])
                
                if "globals" in rename_config:
                    self._rename_globals(file_model, rename_config["globals"])
                
                if "includes" in rename_config:
                    self._rename_includes(file_model, rename_config["includes"])
                
                if "structs" in rename_config:
                    self._rename_structs(file_model, rename_config["structs"])
                
                if "enums" in rename_config:
                    self._rename_enums(file_model, rename_config["enums"])
                
                if "unions" in rename_config:
                    self._rename_unions(file_model, rename_config["unions"])
        
        # Apply file renaming (affects model.files keys)
        if "files" in rename_config:
            model = self._rename_files(model, rename_config["files"], target_files)

        return model

    def _apply_rename_patterns(self, original_name: str, patterns_map: Dict[str, str]) -> str:
        """
        Apply rename patterns to an element name
        
        Args:
            original_name: Original element name
            patterns_map: Dict mapping regex patterns to replacement strings
            
        Returns:
            Renamed element name (or original if no patterns match)
        """
        for pattern, replacement in patterns_map.items():
            try:
                # Apply regex substitution
                new_name = re.sub(pattern, replacement, original_name)
                if new_name != original_name:
                    self.logger.debug(
                        "Renamed '%s' to '%s' using pattern '%s'", 
                        original_name, new_name, pattern
                    )
                    return new_name
            except re.error as e:
                self.logger.warning(
                    "Invalid regex pattern '%s': %s", pattern, e
                )
                continue
        
        return original_name

    def _rename_typedefs(self, file_model: FileModel, patterns_map: Dict[str, str]) -> None:
        """Rename typedefs with deduplication"""
        if not patterns_map:
            return
        
        original_count = len(file_model.aliases)
        seen_names = set()
        deduplicated_aliases = {}
        
        for name, alias in file_model.aliases.items():
            # Apply rename patterns
            new_name = self._apply_rename_patterns(name, patterns_map)
            
            # Check for duplicates
            if new_name in seen_names:
                self.logger.debug(
                    "Deduplicating typedef: removing duplicate '%s' (renamed from '%s')", 
                    new_name, name
                )
                continue
                
            seen_names.add(new_name)
            
            # Update alias with new name
            updated_alias = Alias(new_name, alias.original_type, alias.uses)
            deduplicated_aliases[new_name] = updated_alias
        
        file_model.aliases = deduplicated_aliases
        removed_count = original_count - len(file_model.aliases)
        
        if removed_count > 0:
            self.logger.info(
                "Renamed typedefs in %s, removed %d duplicates", file_model.name, removed_count
            )

    def _rename_functions(self, file_model: FileModel, patterns_map: Dict[str, str]) -> None:
        """Rename functions with deduplication"""
        if not patterns_map:
            return
        
        original_count = len(file_model.functions)
        seen_names = set()
        deduplicated_functions = []
        
        for function in file_model.functions:
            # Apply rename patterns
            new_name = self._apply_rename_patterns(function.name, patterns_map)
            
            # Check for duplicates
            if new_name in seen_names:
                self.logger.debug(
                    "Deduplicating function: removing duplicate '%s' (renamed from '%s')", 
                    new_name, function.name
                )
                continue
                
            seen_names.add(new_name)
            
            # Update function with new name
            updated_function = Function(
                new_name,
                function.return_type,
                function.parameters,
                function.is_static,
                function.is_declaration
            )
            deduplicated_functions.append(updated_function)
        
        file_model.functions = deduplicated_functions
        removed_count = original_count - len(file_model.functions)
        
        if removed_count > 0:
            self.logger.info(
                "Renamed functions in %s, removed %d duplicates", file_model.name, removed_count
            )

    def _rename_macros(self, file_model: FileModel, patterns_map: Dict[str, str]) -> None:
        """Rename macros with deduplication"""
        if not patterns_map:
            return
        
        original_count = len(file_model.macros)
        seen_names = set()
        deduplicated_macros = []
        
        for macro in file_model.macros:
            # Apply rename patterns
            new_name = self._apply_rename_patterns(macro, patterns_map)
            
            # Check for duplicates
            if new_name in seen_names:
                self.logger.debug(
                    "Deduplicating macro: removing duplicate '%s' (renamed from '%s')", 
                    new_name, macro
                )
                continue
                
            seen_names.add(new_name)
            deduplicated_macros.append(new_name)
        
        file_model.macros = deduplicated_macros
        removed_count = original_count - len(file_model.macros)
        
        if removed_count > 0:
            self.logger.info(
                "Renamed macros in %s, removed %d duplicates", file_model.name, removed_count
            )

    def _rename_globals(self, file_model: FileModel, patterns_map: Dict[str, str]) -> None:
        """Rename global variables with deduplication"""
        if not patterns_map:
            return
        
        original_count = len(file_model.globals)
        seen_names = set()
        deduplicated_globals = []
        
        for global_var in file_model.globals:
            # Apply rename patterns
            new_name = self._apply_rename_patterns(global_var.name, patterns_map)
            
            # Check for duplicates
            if new_name in seen_names:
                self.logger.debug(
                    "Deduplicating global: removing duplicate '%s' (renamed from '%s')", 
                    new_name, global_var.name
                )
                continue
                
            seen_names.add(new_name)
            
            # Update global with new name
            updated_global = Field(new_name, global_var.type)
            deduplicated_globals.append(updated_global)
        
        file_model.globals = deduplicated_globals
        removed_count = original_count - len(file_model.globals)
        
        if removed_count > 0:
            self.logger.info(
                "Renamed globals in %s, removed %d duplicates", file_model.name, removed_count
            )

    def _rename_includes(self, file_model: FileModel, patterns_map: Dict[str, str]) -> None:
        """Rename includes with deduplication"""
        if not patterns_map:
            return
        
        original_count = len(file_model.includes)
        seen_names = set()
        deduplicated_includes = set()
        
        for include in file_model.includes:
            # Apply rename patterns
            new_name = self._apply_rename_patterns(include, patterns_map)
            
            # Check for duplicates
            if new_name in seen_names:
                self.logger.debug(
                    "Deduplicating include: removing duplicate '%s' (renamed from '%s')", 
                    new_name, include
                )
                continue
                
            seen_names.add(new_name)
            deduplicated_includes.add(new_name)
        
        file_model.includes = deduplicated_includes
        removed_count = original_count - len(file_model.includes)
        
        # Also update include_relations with new names
        updated_relations = []
        for relation in file_model.include_relations:
            new_included_file = self._apply_rename_patterns(relation.included_file, patterns_map)
            updated_relation = IncludeRelation(
                relation.source_file,
                new_included_file,
                relation.depth
            )
            updated_relations.append(updated_relation)
        
        file_model.include_relations = updated_relations
        
        if removed_count > 0:
            self.logger.info(
                "Renamed includes in %s, removed %d duplicates", file_model.name, removed_count
            )

    def _rename_structs(self, file_model: FileModel, patterns_map: Dict[str, str]) -> None:
        """Rename structs with deduplication"""
        if not patterns_map:
            return
        
        original_count = len(file_model.structs)
        seen_names = set()
        deduplicated_structs = {}
        
        for name, struct in file_model.structs.items():
            # Apply rename patterns
            new_name = self._apply_rename_patterns(name, patterns_map)
            
            # Check for duplicates
            if new_name in seen_names:
                self.logger.debug(
                    "Deduplicating struct: removing duplicate '%s' (renamed from '%s')", 
                    new_name, name
                )
                continue
                
            seen_names.add(new_name)
            
            # Update struct with new name
            updated_struct = Struct(new_name, struct.fields)
            deduplicated_structs[new_name] = updated_struct
        
        file_model.structs = deduplicated_structs
        removed_count = original_count - len(file_model.structs)
        
        if removed_count > 0:
            self.logger.info(
                "Renamed structs in %s, removed %d duplicates", file_model.name, removed_count
            )

    def _rename_enums(self, file_model: FileModel, patterns_map: Dict[str, str]) -> None:
        """Rename enums with deduplication"""
        if not patterns_map:
            return
        
        original_count = len(file_model.enums)
        seen_names = set()
        deduplicated_enums = {}
        
        for name, enum in file_model.enums.items():
            # Apply rename patterns
            new_name = self._apply_rename_patterns(name, patterns_map)
            
            # Check for duplicates
            if new_name in seen_names:
                self.logger.debug(
                    "Deduplicating enum: removing duplicate '%s' (renamed from '%s')", 
                    new_name, name
                )
                continue
                
            seen_names.add(new_name)
            
            # Update enum with new name
            updated_enum = Enum(new_name, enum.values)
            deduplicated_enums[new_name] = updated_enum
        
        file_model.enums = deduplicated_enums
        removed_count = original_count - len(file_model.enums)
        
        if removed_count > 0:
            self.logger.info(
                "Renamed enums in %s, removed %d duplicates", file_model.name, removed_count
            )

    def _rename_unions(self, file_model: FileModel, patterns_map: Dict[str, str]) -> None:
        """Rename unions with deduplication"""
        if not patterns_map:
            return
        
        original_count = len(file_model.unions)
        seen_names = set()
        deduplicated_unions = {}
        
        for name, union in file_model.unions.items():
            # Apply rename patterns
            new_name = self._apply_rename_patterns(name, patterns_map)
            
            # Check for duplicates
            if new_name in seen_names:
                self.logger.debug(
                    "Deduplicating union: removing duplicate '%s' (renamed from '%s')", 
                    new_name, name
                )
                continue
                
            seen_names.add(new_name)
            
            # Update union with new name
            updated_union = Union(new_name, union.fields)
            deduplicated_unions[new_name] = updated_union
        
        file_model.unions = deduplicated_unions
        removed_count = original_count - len(file_model.unions)
        
        if removed_count > 0:
            self.logger.info(
                "Renamed unions in %s, removed %d duplicates", file_model.name, removed_count
            )

    def _rename_files(self, model: ProjectModel, patterns_map: Dict[str, str], target_files: Set[str]) -> ProjectModel:
        """Rename files and update model.files keys"""
        if not patterns_map:
            return model
        
        updated_files = {}
        
        for file_path, file_model in model.files.items():
            # Only rename files in target_files
            if file_path in target_files:
                new_file_path = self._apply_rename_patterns(file_path, patterns_map)
                
                if new_file_path != file_path:
                    # Update file_model.name to match new path
                    file_model.name = new_file_path
                    self.logger.debug("Renamed file: %s -> %s", file_path, new_file_path)
                
                updated_files[new_file_path] = file_model
            else:
                # Keep original file unchanged
                updated_files[file_path] = file_model
        
        model.files = updated_files
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
                file_model = model.files[file_path]
                self.logger.debug("Applying removals to file: %s", file_path)
                
                # Apply each type of removal
                if "typedef" in remove_config:
                    self._remove_typedefs(file_model, remove_config["typedef"])
                
                if "functions" in remove_config:
                    self._remove_functions(file_model, remove_config["functions"])
                
                if "macros" in remove_config:
                    self._remove_macros(file_model, remove_config["macros"])
                
                if "globals" in remove_config:
                    self._remove_globals(file_model, remove_config["globals"])
                
                if "includes" in remove_config:
                    self._remove_includes(file_model, remove_config["includes"])
                
                if "structs" in remove_config:
                    self._remove_structs(file_model, remove_config["structs"])
                
                if "enums" in remove_config:
                    self._remove_enums(file_model, remove_config["enums"])
                
                if "unions" in remove_config:
                    self._remove_unions(file_model, remove_config["unions"])

        return model

    def _remove_typedefs(self, file_model: FileModel, patterns: List[str]) -> None:
        """Remove typedefs matching regex patterns"""
        if not patterns:
            return
        
        original_count = len(file_model.aliases)
        compiled_patterns = self._compile_patterns(patterns)
        
        # Filter out typedefs that match any pattern
        filtered_aliases = {}
        for name, alias in file_model.aliases.items():
            if not self._matches_any_pattern(name, compiled_patterns):
                filtered_aliases[name] = alias
            else:
                self.logger.debug("Removed typedef: %s", name)
        
        file_model.aliases = filtered_aliases
        removed_count = original_count - len(file_model.aliases)
        
        if removed_count > 0:
            self.logger.info(
                "Removed %d typedefs from %s", removed_count, file_model.name
            )

    def _remove_functions(self, file_model: FileModel, patterns: List[str]) -> None:
        """Remove functions matching regex patterns"""
        if not patterns:
            return
        
        original_count = len(file_model.functions)
        compiled_patterns = self._compile_patterns(patterns)
        
        # Filter out functions that match any pattern
        filtered_functions = []
        for function in file_model.functions:
            if not self._matches_any_pattern(function.name, compiled_patterns):
                filtered_functions.append(function)
            else:
                self.logger.debug("Removed function: %s", function.name)
        
        file_model.functions = filtered_functions
        removed_count = original_count - len(file_model.functions)
        
        if removed_count > 0:
            self.logger.info(
                "Removed %d functions from %s", removed_count, file_model.name
            )

    def _remove_macros(self, file_model: FileModel, patterns: List[str]) -> None:
        """Remove macros matching regex patterns"""
        if not patterns:
            return
        
        original_count = len(file_model.macros)
        compiled_patterns = self._compile_patterns(patterns)
        
        # Filter out macros that match any pattern
        filtered_macros = []
        for macro in file_model.macros:
            if not self._matches_any_pattern(macro, compiled_patterns):
                filtered_macros.append(macro)
            else:
                self.logger.debug("Removed macro: %s", macro)
        
        file_model.macros = filtered_macros
        removed_count = original_count - len(file_model.macros)
        
        if removed_count > 0:
            self.logger.info(
                "Removed %d macros from %s", removed_count, file_model.name
            )

    def _remove_globals(self, file_model: FileModel, patterns: List[str]) -> None:
        """Remove global variables matching regex patterns"""
        if not patterns:
            return
        
        original_count = len(file_model.globals)
        compiled_patterns = self._compile_patterns(patterns)
        
        # Filter out globals that match any pattern
        filtered_globals = []
        for global_var in file_model.globals:
            if not self._matches_any_pattern(global_var.name, compiled_patterns):
                filtered_globals.append(global_var)
            else:
                self.logger.debug("Removed global variable: %s", global_var.name)
        
        file_model.globals = filtered_globals
        removed_count = original_count - len(file_model.globals)
        
        if removed_count > 0:
            self.logger.info(
                "Removed %d global variables from %s", removed_count, file_model.name
            )

    def _remove_includes(self, file_model: FileModel, patterns: List[str]) -> None:
        """Remove includes matching regex patterns"""
        if not patterns:
            return
        
        original_count = len(file_model.includes)
        compiled_patterns = self._compile_patterns(patterns)
        
        # Filter out includes that match any pattern
        filtered_includes = set()
        for include in file_model.includes:
            if not self._matches_any_pattern(include, compiled_patterns):
                filtered_includes.add(include)
            else:
                self.logger.debug("Removed include: %s", include)
        
        file_model.includes = filtered_includes
        removed_count = original_count - len(file_model.includes)
        
        # Also remove matching include_relations
        if removed_count > 0:
            original_relations_count = len(file_model.include_relations)
            filtered_relations = []
            for relation in file_model.include_relations:
                if not self._matches_any_pattern(relation.included_file, compiled_patterns):
                    filtered_relations.append(relation)
                else:
                    self.logger.debug("Removed include relation: %s -> %s", 
                                    relation.source_file, relation.included_file)
            
            file_model.include_relations = filtered_relations
            removed_relations_count = original_relations_count - len(file_model.include_relations)
            
            self.logger.info(
                "Removed %d includes and %d include relations from %s", 
                removed_count, removed_relations_count, file_model.name
            )

    def _remove_structs(self, file_model: FileModel, patterns: List[str]) -> None:
        """Remove structs matching regex patterns"""
        if not patterns:
            return
        
        original_count = len(file_model.structs)
        compiled_patterns = self._compile_patterns(patterns)
        
        # Filter out structs that match any pattern
        filtered_structs = {}
        for name, struct in file_model.structs.items():
            if not self._matches_any_pattern(name, compiled_patterns):
                filtered_structs[name] = struct
            else:
                self.logger.debug("Removed struct: %s", name)
        
        file_model.structs = filtered_structs
        removed_count = original_count - len(file_model.structs)
        
        if removed_count > 0:
            self.logger.info(
                "Removed %d structs from %s", removed_count, file_model.name
            )

    def _remove_enums(self, file_model: FileModel, patterns: List[str]) -> None:
        """Remove enums matching regex patterns"""
        if not patterns:
            return
        
        original_count = len(file_model.enums)
        compiled_patterns = self._compile_patterns(patterns)
        
        # Filter out enums that match any pattern
        filtered_enums = {}
        for name, enum in file_model.enums.items():
            if not self._matches_any_pattern(name, compiled_patterns):
                filtered_enums[name] = enum
            else:
                self.logger.debug("Removed enum: %s", name)
        
        file_model.enums = filtered_enums
        removed_count = original_count - len(file_model.enums)
        
        if removed_count > 0:
            self.logger.info(
                "Removed %d enums from %s", removed_count, file_model.name
            )

    def _remove_unions(self, file_model: FileModel, patterns: List[str]) -> None:
        """Remove unions matching regex patterns"""
        if not patterns:
            return
        
        original_count = len(file_model.unions)
        compiled_patterns = self._compile_patterns(patterns)
        
        # Filter out unions that match any pattern
        filtered_unions = {}
        for name, union in file_model.unions.items():
            if not self._matches_any_pattern(name, compiled_patterns):
                filtered_unions[name] = union
            else:
                self.logger.debug("Removed union: %s", name)
        
        file_model.unions = filtered_unions
        removed_count = original_count - len(file_model.unions)
        
        if removed_count > 0:
            self.logger.info(
                "Removed %d unions from %s", removed_count, file_model.name
            )

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
