#!/usr/bin/env python3
"""
Transformer module for C to PlantUML converter - Step 2: Transform model based on
configuration
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Pattern, Set, Tuple, Union as TypingUnion
from collections import deque

from ..models import (
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

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def transform(
        self, model_file: str, config_file: str, output_file: Optional[str] = None
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

        # Load the model and configuration
        model = self._load_model(model_file)
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
        model_path = Path(model_file)
        if not model_path.exists():
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
        config_path = Path(config_file)
        if not config_path.exists():
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

        # Discover and apply transformation containers
        model = self._apply_transformation_containers(model, config)

        # Apply simplified depth-based include processing
        if self._should_process_include_relations(config):
            model = self._process_include_relations_simplified(model, config)

        self.logger.info(
            "Transformations complete. Model now has %d files", len(model.files)
        )
        return model

    def _apply_transformation_containers(
        self, model: ProjectModel, config: Dict[str, Any]
    ) -> ProjectModel:
        """Discover and apply transformation containers in alphabetical order"""
        transformation_containers = self._discover_transformation_containers(config)
        
        if not transformation_containers:
            return model
            
        for container_name, transformation_config in transformation_containers:
            self.logger.info("Applying transformation container: %s", container_name)
            model = self._apply_single_transformation_container(
                model, transformation_config, container_name
            )
            self._log_model_state_after_container(model, container_name)
                
        return model

    def _log_model_state_after_container(
        self, model: ProjectModel, container_name: str
    ) -> None:
        """Log model state after applying a transformation container"""
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

    def _should_process_include_relations(self, config: Dict[str, Any]) -> bool:
        """Check if include relations should be processed based on global or file-specific settings"""
        # Check global include_depth
        if config.get("include_depth", 1) > 1:
            return True
        
        # Check file-specific include_depth settings
        if "file_specific" in config:
            for file_config in config["file_specific"].values():
                if file_config.get("include_depth", 1) > 1:
                    return True
        
        return False

    def _discover_transformation_containers(self, config: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Discover all transformation containers and sort them alphabetically
        
        Returns:
            List of (container_name, transformation_config) tuples sorted by name
        """
        transformation_containers = [
            (key, value)
            for key, value in config.items()
            if key.startswith("transformations") and isinstance(value, dict)
        ]
        
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
        """
        # Make a copy to avoid modifying the original
        config = config.copy()
        
        # Check if old format is used (single 'transformations' key)
        if self._is_legacy_transformation_format(config):
            self.logger.info("Converting legacy 'transformations' format to container format")
            
            # Move old transformations to a default container
            old_transformations = config.pop("transformations")
            config["transformations_00_default"] = old_transformations
            
            self.logger.debug("Converted to container: transformations_00_default")
        
        return config

    def _is_legacy_transformation_format(self, config: Dict[str, Any]) -> bool:
        """Check if configuration uses legacy transformation format"""
        return (
            "transformations" in config and 
            not any(key.startswith("transformations_") for key in config.keys())
        )

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
        
        # Determine target files for this container
        target_files = self._get_target_files(model, transformation_config)
        
        # Apply transformations in specific order: remove -> rename -> add
        # This order ensures that removals happen first, then renaming with deduplication,
        # then additions to the cleaned model
        model = self._apply_remove_operations(model, transformation_config, target_files, container_name)
        model = self._apply_rename_operations(model, transformation_config, target_files, container_name)
        model = self._apply_add_operations(model, transformation_config, target_files, container_name)
        
        return model

    def _get_target_files(
        self, model: ProjectModel, transformation_config: Dict[str, Any]
    ) -> Set[str]:
        """Determine which files to apply transformations to based on file_selection"""
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
            target_files = self._match_files_by_patterns(model, selected_files)
            self.logger.debug(
                "File selection patterns %s matched %d files: %s",
                selected_files, len(target_files), list(target_files)
            )
        
        return target_files

    def _match_files_by_patterns(
        self, model: ProjectModel, patterns: List[str]
    ) -> Set[str]:
        """Match files based on selection patterns"""
        target_files = set()
        for pattern in patterns:
            for file_path in model.files.keys():
                if self._matches_pattern(file_path, pattern):
                    target_files.add(file_path)
        return target_files

    def _apply_remove_operations(
        self, 
        model: ProjectModel, 
        transformation_config: Dict[str, Any], 
        target_files: Set[str],
        container_name: str
    ) -> ProjectModel:
        """Apply remove operations for a transformation container"""
        if "remove" not in transformation_config:
            return model
            
        self.logger.debug("Applying remove operations for container: %s", container_name)
        
        # Collect typedef names BEFORE removing them for type reference cleanup
        removed_typedef_names = self._collect_typedef_names_for_removal(
            model, transformation_config["remove"], target_files
        )
        
        model = self._apply_removals(model, transformation_config["remove"], target_files)
        
        # Clean up type references after typedef removal using pre-collected names
        if removed_typedef_names:
            self.logger.debug("Calling type reference cleanup for container: %s", container_name)
            self._cleanup_type_references_by_names(model, removed_typedef_names)
            
        return model

    def _apply_rename_operations(
        self, 
        model: ProjectModel, 
        transformation_config: Dict[str, Any], 
        target_files: Set[str],
        container_name: str
    ) -> ProjectModel:
        """Apply rename operations for a transformation container"""
        if "rename" not in transformation_config:
            return model
            
        self.logger.debug("Applying rename operations for container: %s", container_name)
        return self._apply_renaming(model, transformation_config["rename"], target_files)

    def _apply_add_operations(
        self, 
        model: ProjectModel, 
        transformation_config: Dict[str, Any], 
        target_files: Set[str],
        container_name: str
    ) -> ProjectModel:
        """Apply add operations for a transformation container"""
        if "add" not in transformation_config:
            return model
            
        self.logger.debug("Applying add operations for container: %s", container_name)
        return self._apply_additions(model, transformation_config["add"], target_files)

    def _collect_typedef_names_for_removal(
        self, 
        model: ProjectModel, 
        remove_config: Dict[str, Any], 
        target_files: Set[str]
    ) -> Set[str]:
        """Collect typedef names that will be removed for type reference cleanup"""
        removed_typedef_names = set()
        
        if "typedef" not in remove_config:
            return removed_typedef_names
            
        typedef_patterns = remove_config["typedef"]
        compiled_patterns = self._compile_patterns(typedef_patterns)
        
        if not compiled_patterns:
            return removed_typedef_names
            
        for file_path in target_files:
            if file_path in model.files:
                file_model = model.files[file_path]
                for alias_name in file_model.aliases.keys():
                    if self._matches_any_pattern(alias_name, compiled_patterns):
                        removed_typedef_names.add(alias_name)
                        
        self.logger.debug("Pre-identified typedefs for removal: %s", list(removed_typedef_names))
        return removed_typedef_names

    def _process_include_relations_with_file_specific_settings(
        self, model: ProjectModel, config: Dict[str, Any]
    ) -> ProjectModel:
        """Process include relations with support for file-specific include_depth and include_filter"""
        global_include_depth = config.get("include_depth", 1)
        file_specific_config = config.get("file_specific", {})
        
        # Clear all include_relations first
        self._clear_include_relations(model)

        # Process each .c file individually with its specific settings
        c_files = self._get_c_files(model)
        for file_model in c_files:
            self._process_c_file_include_relations(
                model, file_model, global_include_depth, file_specific_config
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

    def _clear_include_relations(self, model: ProjectModel) -> None:
        """Clear all include relations in the model"""
        for file_model in model.files.values():
            file_model.include_relations = []

    def _get_c_files(self, model: ProjectModel) -> List[FileModel]:
        """Get all .c files from the model"""
        return [
            file_model for file_model in model.files.values()
            if file_model.name.endswith(".c")
        ]

    def _process_c_file_include_relations(
        self, 
        model: ProjectModel, 
        file_model: FileModel, 
        global_include_depth: int,
        file_specific_config: Dict[str, Any]
    ) -> None:
        """Process include relations for a single .c file"""
        root_filename = Path(file_model.name).name
        
        # Get file-specific settings
        include_depth, include_filter_patterns = self._get_file_include_settings(
            root_filename, file_specific_config, global_include_depth
        )
        
        # Only process if include_depth > 1
        if include_depth <= 1:
            return
            
        # Compile include filter patterns
        compiled_filters = self._compile_include_filter_patterns(
            include_filter_patterns, root_filename, include_depth
        )
        
        # Process this specific file's include relations
        self._process_single_file_include_relations(
            model, file_model, include_depth, compiled_filters
        )

    def _get_file_include_settings(
        self, 
        root_filename: str, 
        file_specific_config: Dict[str, Any], 
        global_include_depth: int
    ) -> Tuple[int, List[str]]:
        """Get include depth and filter patterns for a specific file"""
        if root_filename in file_specific_config:
            file_config = file_specific_config[root_filename]
            include_depth = file_config.get("include_depth", global_include_depth)
            include_filter_patterns = file_config.get("include_filter", [])
        else:
            include_depth = global_include_depth
            include_filter_patterns = []
            
        return include_depth, include_filter_patterns

    def _compile_include_filter_patterns(
        self, patterns: List[str], root_filename: str, include_depth: int
    ) -> List[Pattern[str]]:
        """Compile include filter patterns with error handling"""
        if not patterns:
            return []
            
        try:
            compiled_filters = [re.compile(pattern) for pattern in patterns]
            self.logger.debug(
                "Using %d include filter patterns for %s with depth %d", 
                len(compiled_filters), root_filename, include_depth
            )
            return compiled_filters
        except re.error as e:
            self.logger.warning(
                "Invalid regex pattern for file %s: %s", root_filename, e
            )
            return []

    def _process_single_file_include_relations(
        self, 
        model: ProjectModel, 
        root_file_model: "FileModel",
        max_depth: int,
        compiled_filters: List[Any]
    ) -> None:
        """Process include relations for a single root file with specific depth and filters"""
        
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
        """Apply include filters for each root file based on regex patterns
        
        Args:
            model: The project model to apply filters to
            include_filters: Dictionary mapping root files to their include filter patterns
        """
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
                # Apply comprehensive filtering (preserve includes arrays, filter include_relations)
                self._filter_file_includes_comprehensive(
                    file_model, compiled_filters[root_file], root_file
                )

        return model

    def _create_header_to_root_mapping(self, model: ProjectModel) -> Dict[str, str]:
        """Create a mapping from header files to their root C files"""
        header_to_root = {}

        # First, map C files to themselves
        c_files = []
        for file_path, file_model in model.files.items():
            if file_model.name.endswith(".c"):
                header_to_root[file_model.name] = file_model.name
                c_files.append(file_model.name)

        # Then, map header files to their corresponding C files
        for file_path, file_model in model.files.items():
            if not file_model.name.endswith(".c"):  # It's a header file
                # Strategy 1: Look for a C file with the same base name
                header_base_name = Path(file_model.name).stem
                matching_c_file = header_base_name + ".c"
                
                if matching_c_file in [Path(c_file).name for c_file in c_files]:
                    header_to_root[file_model.name] = matching_c_file
                else:
                    # Strategy 2: Find which C file includes this header
                    including_c_files = []
                    for c_file_path, c_file_model in model.files.items():
                        if (c_file_model.name.endswith(".c") and 
                            file_model.name in c_file_model.includes):
                            including_c_files.append(c_file_model.name)
                    
                    if including_c_files:
                        # Use the first C file that includes this header
                        header_to_root[file_model.name] = including_c_files[0]
                    else:
                        # Strategy 3: Fallback to first available C file
                        if c_files:
                            header_to_root[file_model.name] = c_files[0]

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

        # For header files, find the corresponding .c file
        base_name = Path(file_path).stem

        # Look for a .c file with the same base name
        if base_name and not filename.startswith("."):
            return base_name + ".c"

        # Fallback: use the filename as root (original behavior)
        return filename

    def _filter_file_includes(
        self, file_model: FileModel, patterns: List[re.Pattern], root_file: str
    ) -> None:
        """Filter include_relations while preserving original includes arrays.
        This is used by the main transformation pipeline to maintain source information."""
        self.logger.debug(
            "Filtering include_relations for file %s (root: %s)", file_model.name, root_file
        )

        # Preserve includes arrays - they contain important source information
        original_includes_count = len(file_model.includes)

        # Filter include_relations based on patterns
        original_relations_count = len(file_model.include_relations)
        filtered_relations = []

        for relation in file_model.include_relations:
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
            "Include filtering for %s: includes preserved (%d), relations %d->%d",
            file_model.name,
            original_includes_count,
            original_relations_count,
            len(file_model.include_relations),
        )

    def _filter_file_includes_comprehensive(
        self, file_model: FileModel, patterns: List[re.Pattern], root_file: str
    ) -> None:
        """Comprehensive filtering that affects only include_relations, preserving includes arrays.
        This is used by the direct _apply_include_filters method for complete filtering."""
        self.logger.debug(
            "Comprehensive filtering for file %s (root: %s)", file_model.name, root_file
        )

        # IMPORTANT: Do NOT filter includes arrays - they should be preserved
        # Only filter include_relations based on the patterns
        original_relations_count = len(file_model.include_relations)
        filtered_relations = []

        for relation in file_model.include_relations:
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
            "Comprehensive filtering for %s: includes preserved (%d), relations %d->%d",
            file_model.name,
            len(file_model.includes),
            original_relations_count,
            len(file_model.include_relations),
        )



    def _matches_any_pattern(self, text: str, patterns: List[Pattern[str]]) -> bool:
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
            
            # Clean up type references after typedef removal
            if "typedef" in transformations["remove"]:
                self._cleanup_type_references(model, transformations["remove"]["typedef"], target_files)

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
                self._apply_file_level_renaming(file_model, rename_config)
        
        # Apply file renaming (affects model.files keys)
        if "files" in rename_config:
            model = self._rename_files(model, rename_config["files"], target_files)

        return model

    def _apply_file_level_renaming(
        self, file_model: FileModel, rename_config: Dict[str, Any]
    ) -> None:
        """Apply all renaming operations to a single file"""
        rename_operations = [
            ("typedef", self._rename_typedefs),
            ("functions", self._rename_functions),
            ("macros", self._rename_macros),
            ("globals", self._rename_globals),
            ("includes", self._rename_includes),
            ("structs", self._rename_structs),
            ("enums", self._rename_enums),
            ("unions", self._rename_unions),
        ]
        
        for config_key, rename_method in rename_operations:
            if config_key in rename_config:
                rename_method(file_model, rename_config[config_key])
    
    def _cleanup_type_references(
        self, model: ProjectModel, removed_typedef_patterns: List[str], target_files: Set[str]
    ) -> None:
        """
        Clean up type references after typedef removal
        
        This method removes type references that point to removed typedefs from:
        - Function parameters and return types
        - Global variable types  
        - Struct field types
        """
        self.logger.debug("Starting type reference cleanup with patterns: %s, target_files: %s", 
                         removed_typedef_patterns, list(target_files))
        
        if not removed_typedef_patterns:
            self.logger.debug("No typedef patterns to clean up")
            return
            
        compiled_patterns = self._compile_patterns(removed_typedef_patterns)
        if not compiled_patterns:
            self.logger.debug("No valid compiled patterns")
            return
            
        # Track removed type names for cleanup
        removed_types = set()
        
        # First, collect all removed typedef names from all target files
        for file_path in target_files:
            if file_path in model.files:
                file_model = model.files[file_path]
                
                # Check what typedefs would be removed from this file
                for alias_name in list(file_model.aliases.keys()):
                    if self._matches_any_pattern(alias_name, compiled_patterns):
                        removed_types.add(alias_name)
                        self.logger.debug("Found removed typedef: %s in file %s", alias_name, file_path)
        
        self.logger.debug("Total removed types identified: %s", list(removed_types))
        
        # Clean up type references across all files since typedefs can be used anywhere
        cleaned_count = 0
        for file_path, file_model in model.files.items():
            file_cleaned = 0
            
            # Clean function parameter and return types
            for func in file_model.functions:
                # Clean return type
                if func.return_type and self._contains_removed_type(func.return_type, removed_types):
                    old_type = func.return_type
                    func.return_type = self._remove_type_references(func.return_type, removed_types)
                    if func.return_type != old_type:
                        file_cleaned += 1
                        self.logger.debug(
                            "Cleaned return type '%s' -> '%s' in function %s", 
                            old_type, func.return_type, func.name
                        )
                
                # Clean parameter types
                for param in func.parameters:
                    if param.type and self._contains_removed_type(param.type, removed_types):
                        old_type = param.type
                        param.type = self._remove_type_references(param.type, removed_types)
                        if param.type != old_type:
                            file_cleaned += 1
                            self.logger.debug(
                                "Cleaned parameter type '%s' -> '%s' for parameter %s", 
                                old_type, param.type, param.name
                            )
            
            # Clean global variable types
            for global_var in file_model.globals:
                if global_var.type and self._contains_removed_type(global_var.type, removed_types):
                    old_type = global_var.type
                    global_var.type = self._remove_type_references(global_var.type, removed_types)
                    if global_var.type != old_type:
                        file_cleaned += 1
                        self.logger.debug(
                            "Cleaned global variable type '%s' -> '%s' for %s", 
                            old_type, global_var.type, global_var.name
                        )
            
            # Clean struct field types
            for struct in file_model.structs.values():
                for field in struct.fields:
                    if field.type and self._contains_removed_type(field.type, removed_types):
                        old_type = field.type
                        field.type = self._remove_type_references(field.type, removed_types)
                        if field.type != old_type:
                            file_cleaned += 1
                            self.logger.debug(
                                "Cleaned struct field type '%s' -> '%s' for %s.%s", 
                                old_type, field.type, struct.name, field.name
                            )
            
            cleaned_count += file_cleaned
        
        if cleaned_count > 0:
            self.logger.info(
                "Cleaned %d type references to removed typedefs: %s", 
                cleaned_count, list(removed_types)
            )
    
    def _contains_removed_type(self, type_str: str, removed_types: Set[str]) -> bool:
        """Check if a type string contains any of the removed types"""
        if not type_str or not removed_types:
            return False
            
        # Check for removed type names in the type string
        # This handles cases like "old_point_t *", "const old_config_t", etc.
        for removed_type in removed_types:
            if removed_type in type_str:
                return True
        return False
    
    def _remove_type_references(self, type_str: str, removed_types: Set[str]) -> str:
        """Remove references to removed types from a type string"""
        if not type_str or not removed_types:
            return type_str
            
        cleaned_type = type_str
        for removed_type in removed_types:
            if removed_type in cleaned_type:
                # Replace the removed type with "void" to maintain type safety
                cleaned_type = cleaned_type.replace(removed_type, "void")
                
        # Clean up any double spaces or other artifacts
        cleaned_type = " ".join(cleaned_type.split())
        return cleaned_type
    
    def _cleanup_type_references_by_names(
        self, model: ProjectModel, removed_typedef_names: Set[str]
    ) -> None:
        """
        Clean up type references using pre-collected typedef names
        
        This method removes type references that point to removed typedefs from:
        - Function parameters and return types
        - Global variable types  
        - Struct field types
        """
        if not removed_typedef_names:
            self.logger.debug("No removed typedef names provided")
            return
            
        self.logger.debug("Cleaning type references for removed typedefs: %s", list(removed_typedef_names))
        
        # Clean up type references across all files since typedefs can be used anywhere
        cleaned_count = 0
        for file_path, file_model in model.files.items():
            file_cleaned = 0
            
            # Clean function parameter and return types
            for func in file_model.functions:
                # Clean return type
                if func.return_type and self._contains_removed_type(func.return_type, removed_typedef_names):
                    old_type = func.return_type
                    func.return_type = self._remove_type_references(func.return_type, removed_typedef_names)
                    if func.return_type != old_type:
                        file_cleaned += 1
                        self.logger.debug(
                            "Cleaned return type '%s' -> '%s' in function %s", 
                            old_type, func.return_type, func.name
                        )
                
                # Clean parameter types
                for param in func.parameters:
                    if param.type and self._contains_removed_type(param.type, removed_typedef_names):
                        old_type = param.type
                        param.type = self._remove_type_references(param.type, removed_typedef_names)
                        if param.type != old_type:
                            file_cleaned += 1
                            self.logger.debug(
                                "Cleaned parameter type '%s' -> '%s' for parameter %s", 
                                old_type, param.type, param.name
                            )
            
            # Clean global variable types
            for global_var in file_model.globals:
                if global_var.type and self._contains_removed_type(global_var.type, removed_typedef_names):
                    old_type = global_var.type
                    global_var.type = self._remove_type_references(global_var.type, removed_typedef_names)
                    if global_var.type != old_type:
                        file_cleaned += 1
                        self.logger.debug(
                            "Cleaned global variable type '%s' -> '%s' for %s", 
                            old_type, global_var.type, global_var.name
                        )
            
            # Clean struct field types
            for struct in file_model.structs.values():
                for field in struct.fields:
                    if field.type and self._contains_removed_type(field.type, removed_typedef_names):
                        old_type = field.type
                        field.type = self._remove_type_references(field.type, removed_typedef_names)
                        if field.type != old_type:
                            file_cleaned += 1
                            self.logger.debug(
                                "Cleaned struct field type '%s' -> '%s' for %s.%s", 
                                old_type, field.type, struct.name, field.name
                            )
            
            cleaned_count += file_cleaned
            if file_cleaned > 0:
                self.logger.debug("Cleaned %d type references in file %s", file_cleaned, file_path)
        
        if cleaned_count > 0:
            self.logger.info(
                "Cleaned %d type references to removed typedefs: %s", 
                cleaned_count, list(removed_typedef_names)
            )
        else:
            self.logger.debug("No type references found to clean up")

    def _update_type_references_for_renames(self, file_model: FileModel, typedef_renames: Dict[str, str]) -> None:
        """Update all type references when typedefs are renamed"""
        updated_count = 0
        
        # Update function return types and parameter types
        for func in file_model.functions:
            # Update return type
            if func.return_type:
                old_type = func.return_type
                new_type = self._update_type_string_for_renames(func.return_type, typedef_renames)
                if new_type != old_type:
                    func.return_type = new_type
                    updated_count += 1
                    self.logger.debug(
                        "Updated return type '%s' -> '%s' in function %s", 
                        old_type, new_type, func.name
                    )
            
            # Update parameter types
            for param in func.parameters:
                if param.type:
                    old_type = param.type
                    new_type = self._update_type_string_for_renames(param.type, typedef_renames)
                    if new_type != old_type:
                        param.type = new_type
                        updated_count += 1
                        self.logger.debug(
                            "Updated parameter type '%s' -> '%s' for parameter %s in function %s", 
                            old_type, new_type, param.name, func.name
                        )
        
        # Update global variable types
        for global_var in file_model.globals:
            if global_var.type:
                old_type = global_var.type
                new_type = self._update_type_string_for_renames(global_var.type, typedef_renames)
                if new_type != old_type:
                    global_var.type = new_type
                    updated_count += 1
                    self.logger.debug(
                        "Updated global variable type '%s' -> '%s' for %s", 
                        old_type, new_type, global_var.name
                    )
        
        # Update struct field types
        for struct in file_model.structs.values():
            for field in struct.fields:
                if field.type:
                    old_type = field.type
                    new_type = self._update_type_string_for_renames(field.type, typedef_renames)
                    if new_type != old_type:
                        field.type = new_type
                        updated_count += 1
                        self.logger.debug(
                            "Updated struct field type '%s' -> '%s' for %s.%s", 
                            old_type, new_type, struct.name, field.name
                        )
        
        # Update union field types
        for union in file_model.unions.values():
            for field in union.fields:
                if field.type:
                    old_type = field.type
                    new_type = self._update_type_string_for_renames(field.type, typedef_renames)
                    if new_type != old_type:
                        field.type = new_type
                        updated_count += 1
                        self.logger.debug(
                            "Updated union field type '%s' -> '%s' for %s.%s", 
                            old_type, new_type, union.name, field.name
                        )
        
        if updated_count > 0:
            self.logger.info(
                "Updated %d type references for renamed typedefs in %s: %s", 
                updated_count, file_model.name, typedef_renames
            )

    def _update_type_string_for_renames(self, type_str: str, typedef_renames: Dict[str, str]) -> str:
        """Update a type string by replacing old typedef names with new ones"""
        if not type_str or not typedef_renames:
            return type_str
        
        updated_type = type_str
        for old_name, new_name in typedef_renames.items():
            # Use word boundaries to avoid partial matches
            # This handles cases like "old_config_t *", "const old_config_t", etc.
            pattern = r'\b' + re.escape(old_name) + r'\b'
            updated_type = re.sub(pattern, new_name, updated_type)
        
        return updated_type

    def _rename_dict_elements(
        self, 
        elements_dict: Dict[str, Any], 
        patterns_map: Dict[str, str], 
        create_renamed_element: Callable[[str, Any], Any],
        element_type: str,
        file_name: str
    ) -> Dict[str, Any]:
        """Generic method to rename dictionary elements with deduplication"""
        original_count = len(elements_dict)
        seen_names = set()
        deduplicated_elements = {}
        
        for name, element in elements_dict.items():
            # Apply rename patterns
            new_name = self._apply_rename_patterns(name, patterns_map)
            
            # Check for duplicates
            if new_name in seen_names:
                self.logger.debug(
                    "Deduplicating %s: removing duplicate '%s' (renamed from '%s')", 
                    element_type, new_name, name
                )
                continue
                
            seen_names.add(new_name)
            
            # Create updated element with new name
            updated_element = create_renamed_element(new_name, element)
            deduplicated_elements[new_name] = updated_element
        
        removed_count = original_count - len(deduplicated_elements)
        if removed_count > 0:
            self.logger.info(
                "Renamed %ss in %s, removed %d duplicates", element_type, file_name, removed_count
            )
            
        return deduplicated_elements

    def _rename_list_elements(
        self, 
        elements_list: List[Any], 
        patterns_map: Dict[str, str], 
        get_element_name: Callable[[Any], str],
        create_renamed_element: Callable[[str, Any], Any],
        element_type: str,
        file_name: str
    ) -> List[Any]:
        """Generic method to rename list elements with deduplication"""
        original_count = len(elements_list)
        seen_names = set()
        deduplicated_elements = []
        
        for element in elements_list:
            name = get_element_name(element)
            # Apply rename patterns
            new_name = self._apply_rename_patterns(name, patterns_map)
            
            # Check for duplicates
            if new_name in seen_names:
                self.logger.debug(
                    "Deduplicating %s: removing duplicate '%s' (renamed from '%s')", 
                    element_type, new_name, name
                )
                continue
                
            seen_names.add(new_name)
            
            # Create updated element with new name
            updated_element = create_renamed_element(new_name, element)
            deduplicated_elements.append(updated_element)
        
        removed_count = original_count - len(deduplicated_elements)
        if removed_count > 0:
            self.logger.info(
                "Renamed %ss in %s, removed %d duplicates", element_type, file_name, removed_count
            )
            
        return deduplicated_elements

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
        
        # Track old to new name mappings for type reference updates
        typedef_renames = {}
        
        def create_renamed_alias(name: str, alias: Alias) -> Alias:
            return Alias(name, alias.original_type, alias.uses)
        
        # Capture renames before applying them
        for old_name in file_model.aliases:
            new_name = self._apply_rename_patterns(old_name, patterns_map)
            if new_name != old_name:
                typedef_renames[old_name] = new_name
        
        file_model.aliases = self._rename_dict_elements(
            file_model.aliases, patterns_map, create_renamed_alias, "typedef", file_model.name
        )
        
        # Update type references throughout the file
        if typedef_renames:
            self._update_type_references_for_renames(file_model, typedef_renames)

    def _rename_functions(self, file_model: FileModel, patterns_map: Dict[str, str]) -> None:
        """Rename functions with deduplication"""
        if not patterns_map:
            return
        
        def get_function_name(func: Function) -> str:
            return func.name
        
        def create_renamed_function(name: str, func: Function) -> Function:
            return Function(
                name, func.return_type, func.parameters, func.is_static, func.is_declaration
            )
        
        file_model.functions = self._rename_list_elements(
            file_model.functions, patterns_map, get_function_name, 
            create_renamed_function, "function", file_model.name
        )

    def _rename_macros(self, file_model: FileModel, patterns_map: Dict[str, str]) -> None:
        """Rename macros with deduplication"""
        if not patterns_map:
            return
        
        def get_macro_name(macro: str) -> str:
            # Extract macro name from "#define MACRO_NAME value" format
            if macro.startswith("#define "):
                return macro.split(" ")[1]
            return macro
        
        def create_renamed_macro(name: str, macro: str) -> str:
            # Replace the macro name in the original macro string
            if macro.startswith("#define "):
                parts = macro.split(" ", 2)  # Split into ["#define", "OLD_NAME", "rest"]
                if len(parts) >= 2:
                    return f"#define {name} {parts[2]}" if len(parts) > 2 else f"#define {name}"
            # If it's just a macro name without #define prefix, return the new name
            return name
        
        file_model.macros = self._rename_list_elements(
            file_model.macros, patterns_map, get_macro_name, 
            create_renamed_macro, "macro", file_model.name
        )

    def _rename_globals(self, file_model: FileModel, patterns_map: Dict[str, str]) -> None:
        """Rename global variables with deduplication"""
        if not patterns_map:
            return
        
        def get_global_name(global_var: Field) -> str:
            return global_var.name
        
        def create_renamed_global(name: str, global_var: Field) -> Field:
            return Field(name, global_var.type)
        
        file_model.globals = self._rename_list_elements(
            file_model.globals, patterns_map, get_global_name, 
            create_renamed_global, "global", file_model.name
        )

    def _rename_includes(self, file_model: FileModel, patterns_map: Dict[str, str]) -> None:
        """Rename includes with deduplication"""
        if not patterns_map:
            return
        
        # Rename includes using set-based deduplication
        file_model.includes = self._rename_set_elements(
            file_model.includes, patterns_map, "include", file_model.name
        )
        
        # Also update include_relations with new names
        file_model.include_relations = self._rename_include_relations(
            file_model.include_relations, patterns_map
        )

    def _rename_set_elements(
        self, 
        elements_set: Set[str], 
        patterns_map: Dict[str, str], 
        element_type: str,
        file_name: str
    ) -> Set[str]:
        """Generic method to rename set elements with deduplication"""
        original_count = len(elements_set)
        seen_names = set()
        deduplicated_elements = set()
        
        for element in elements_set:
            # Apply rename patterns
            new_name = self._apply_rename_patterns(element, patterns_map)
            
            # Check for duplicates
            if new_name in seen_names:
                self.logger.debug(
                    "Deduplicating %s: removing duplicate '%s' (renamed from '%s')", 
                    element_type, new_name, element
                )
                continue
                
            seen_names.add(new_name)
            deduplicated_elements.add(new_name)
        
        removed_count = original_count - len(deduplicated_elements)
        if removed_count > 0:
            self.logger.info(
                "Renamed %ss in %s, removed %d duplicates", element_type, file_name, removed_count
            )
            
        return deduplicated_elements

    def _rename_include_relations(
        self, relations: List[IncludeRelation], patterns_map: Dict[str, str]
    ) -> List[IncludeRelation]:
        """Rename include relations with pattern mapping"""
        updated_relations = []
        for relation in relations:
            new_included_file = self._apply_rename_patterns(relation.included_file, patterns_map)
            updated_relation = IncludeRelation(
                relation.source_file,
                new_included_file,
                relation.depth
            )
            updated_relations.append(updated_relation)
        return updated_relations

    def _rename_structs(self, file_model: FileModel, patterns_map: Dict[str, str]) -> None:
        """Rename structs with deduplication"""
        if not patterns_map:
            return
        
        def create_renamed_struct(name: str, struct: Struct) -> Struct:
            return Struct(name, struct.fields)
        
        file_model.structs = self._rename_dict_elements(
            file_model.structs, patterns_map, create_renamed_struct, "struct", file_model.name
        )

    def _rename_enums(self, file_model: FileModel, patterns_map: Dict[str, str]) -> None:
        """Rename enums with deduplication"""
        if not patterns_map:
            return
        
        def create_renamed_enum(name: str, enum: Enum) -> Enum:
            return Enum(name, enum.values)
        
        file_model.enums = self._rename_dict_elements(
            file_model.enums, patterns_map, create_renamed_enum, "enum", file_model.name
        )

    def _rename_unions(self, file_model: FileModel, patterns_map: Dict[str, str]) -> None:
        """Rename unions with deduplication"""
        if not patterns_map:
            return
        
        def create_renamed_union(name: str, union: Union) -> Union:
            return Union(name, union.fields)
        
        file_model.unions = self._rename_dict_elements(
            file_model.unions, patterns_map, create_renamed_union, "union", file_model.name
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
                self._apply_file_level_removals(file_model, remove_config)

        return model

    def _apply_file_level_removals(
        self, file_model: FileModel, remove_config: Dict[str, Any]
    ) -> None:
        """Apply all removal operations to a single file"""
        removal_operations = [
            ("typedef", self._remove_typedefs),
            ("functions", self._remove_functions),
            ("macros", self._remove_macros),
            ("globals", self._remove_globals),
            ("includes", self._remove_includes),
            ("structs", self._remove_structs),
            ("enums", self._remove_enums),
            ("unions", self._remove_unions),
        ]
        
        for config_key, removal_method in removal_operations:
            if config_key in remove_config:
                removal_method(file_model, remove_config[config_key])

    def _remove_dict_elements(
        self, 
        elements_dict: Dict[str, Any], 
        patterns: List[str], 
        element_type: str,
        file_name: str
    ) -> Dict[str, Any]:
        """Generic method to remove dictionary elements matching patterns"""
        if not patterns:
            return elements_dict
            
        original_count = len(elements_dict)
        compiled_patterns = self._compile_patterns(patterns)
        
        # Filter out elements that match any pattern
        filtered_elements = {}
        for name, element in elements_dict.items():
            if not self._matches_any_pattern(name, compiled_patterns):
                filtered_elements[name] = element
            else:
                self.logger.debug("Removed %s: %s", element_type, name)
        
        removed_count = original_count - len(filtered_elements)
        if removed_count > 0:
            self.logger.info(
                "Removed %d %ss from %s", removed_count, element_type, file_name
            )
            
        return filtered_elements

    def _remove_list_elements(
        self, 
        elements_list: List[Any], 
        patterns: List[str], 
        get_element_name: Callable[[Any], str],
        element_type: str,
        file_name: str
    ) -> List[Any]:
        """Generic method to remove list elements matching patterns"""
        if not patterns:
            return elements_list
            
        original_count = len(elements_list)
        compiled_patterns = self._compile_patterns(patterns)
        
        # Filter out elements that match any pattern
        filtered_elements = []
        for element in elements_list:
            name = get_element_name(element)
            if not self._matches_any_pattern(name, compiled_patterns):
                filtered_elements.append(element)
            else:
                self.logger.debug("Removed %s: %s", element_type, name)
        
        removed_count = original_count - len(filtered_elements)
        if removed_count > 0:
            self.logger.info(
                "Removed %d %ss from %s", removed_count, element_type, file_name
            )
            
        return filtered_elements

    def _remove_typedefs(self, file_model: FileModel, patterns: List[str]) -> None:
        """Remove typedefs matching regex patterns"""
        file_model.aliases = self._remove_dict_elements(
            file_model.aliases, patterns, "typedef", file_model.name
        )

    def _remove_functions(self, file_model: FileModel, patterns: List[str]) -> None:
        """Remove functions matching regex patterns"""
        def get_function_name(func: Function) -> str:
            return func.name
            
        file_model.functions = self._remove_list_elements(
            file_model.functions, patterns, get_function_name, "function", file_model.name
        )

    def _remove_macros(self, file_model: FileModel, patterns: List[str]) -> None:
        """Remove macros matching regex patterns"""
        def get_macro_name(macro: str) -> str:
            # Extract macro name from "#define MACRO_NAME value" format
            if macro.startswith("#define "):
                return macro.split(" ")[1]
            return macro
            
        file_model.macros = self._remove_list_elements(
            file_model.macros, patterns, get_macro_name, "macro", file_model.name
        )

    def _remove_globals(self, file_model: FileModel, patterns: List[str]) -> None:
        """Remove global variables matching regex patterns"""
        def get_global_name(global_var: Field) -> str:
            return global_var.name
            
        file_model.globals = self._remove_list_elements(
            file_model.globals, patterns, get_global_name, "global variable", file_model.name
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
            self._remove_matching_include_relations(file_model, compiled_patterns, removed_count)

    def _remove_matching_include_relations(
        self, file_model: FileModel, compiled_patterns: List[Pattern[str]], removed_includes_count: int
    ) -> None:
        """Remove include relations that match the removed includes"""
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
            removed_includes_count, removed_relations_count, file_model.name
        )

    def _remove_structs(self, file_model: FileModel, patterns: List[str]) -> None:
        """Remove structs matching regex patterns"""
        file_model.structs = self._remove_dict_elements(
            file_model.structs, patterns, "struct", file_model.name
        )

    def _remove_enums(self, file_model: FileModel, patterns: List[str]) -> None:
        """Remove enums matching regex patterns"""
        file_model.enums = self._remove_dict_elements(
            file_model.enums, patterns, "enum", file_model.name
        )

    def _remove_unions(self, file_model: FileModel, patterns: List[str]) -> None:
        """Remove unions matching regex patterns"""
        file_model.unions = self._remove_dict_elements(
            file_model.unions, patterns, "union", file_model.name
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

    def _compile_patterns(self, patterns: List[str]) -> List[Pattern[str]]:
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
        include_patterns: List[Pattern[str]],
        exclude_patterns: List[Pattern[str]],
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

    def _filter_dict(self, items: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
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

    def _filter_list(self, items: List[Any], filters: Dict[str, Any], key: Optional[Callable[[Any], str]] = None) -> List[Any]:
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

    def _dict_to_file_model(self, data: Dict[str, Any]) -> FileModel:
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

    def _process_include_relations_simplified(
        self, model: ProjectModel, config: Dict[str, Any]
    ) -> ProjectModel:
        """
        Simplified include processing following a structured depth-based approach:
        1. Each include structure has a single root C file
        2. Process C file's direct includes through filters first  
        3. Then recursively process header files' includes with filtering
        4. Continue until include_depth is reached
        """
        global_include_depth = config.get("include_depth", 1)
        file_specific_config = config.get("file_specific", {})
        
        self.logger.info(
            "Processing includes with simplified depth-based approach (global_depth=%d)", 
            global_include_depth
        )
        
        # Clear all existing include relations
        for file_model in model.files.values():
            file_model.include_relations = []
        
        # Create filename to file model mapping for quick lookup
        file_map = {}
        for file_model in model.files.values():
            filename = Path(file_model.name).name
            file_map[filename] = file_model
        
        # Process each C file as a root with its own include structure
        c_files = [fm for fm in model.files.values() if fm.name.endswith(".c")]
        
        for root_file in c_files:
            self._process_root_c_file_includes(
                root_file, file_map, global_include_depth, file_specific_config
            )
            
        return model
    
    def _process_root_c_file_includes(
        self, 
        root_file: FileModel, 
        file_map: Dict[str, FileModel],
        global_include_depth: int,
        file_specific_config: Dict[str, Any]
    ) -> None:
        """
        Process includes for a single root C file following the simplified approach:
        - Start with root C file
        - Apply filters at each depth level
        - Process layer by layer until max depth reached
        """
        root_filename = Path(root_file.name).name
        
        # Get file-specific settings or use global defaults
        include_depth = global_include_depth
        include_filters = []
        
        if root_filename in file_specific_config:
            file_config = file_specific_config[root_filename]
            include_depth = file_config.get("include_depth", global_include_depth)
            include_filters = file_config.get("include_filter", [])
        
        # Skip processing if depth is 1 or less (no include relations needed)
        if include_depth <= 1:
            self.logger.debug(
                "Skipping include processing for %s (depth=%d)", 
                root_filename, include_depth
            )
            return
            
        # Compile filter patterns
        compiled_filters = []
        if include_filters:
            try:
                compiled_filters = [re.compile(pattern) for pattern in include_filters]
                self.logger.debug(
                    "Compiled %d filter patterns for %s", 
                    len(compiled_filters), root_filename
                )
            except re.error as e:
                self.logger.warning(
                    "Invalid regex pattern for %s: %s", root_filename, e
                )
        
        self.logger.debug(
            "Processing includes for root C file %s (depth=%d, filters=%d)",
            root_filename, include_depth, len(compiled_filters)
        )
        
        # Track processed files to avoid cycles
        processed_files = set()
        
        # Process includes level by level using BFS approach
        current_level = [root_file]  # Start with the root C file
        
        for depth in range(1, include_depth + 1):
            next_level = []
            
            self.logger.debug(
                "Processing depth %d for %s (%d files at current level)",
                depth, root_filename, len(current_level)
            )
            
            for current_file in current_level:
                current_filename = Path(current_file.name).name
                
                # Skip if already processed to avoid cycles
                if current_filename in processed_files:
                    continue
                processed_files.add(current_filename)
                
                # Process each include in the current file
                for include_name in current_file.includes:
                    # Apply include filters only at depth 1 (direct includes from root C file)
                    if compiled_filters and depth == 1:
                        if not any(pattern.search(include_name) for pattern in compiled_filters):
                            self.logger.debug(
                                "Filtered out include %s at depth %d for %s",
                                include_name, depth, root_filename
                            )
                            continue
                    
                    # Check if included file exists in our project
                    if include_name not in file_map:
                        self.logger.debug(
                            "Include %s not found in project files (depth %d, root %s)",
                            include_name, depth, root_filename
                        )
                        continue
                    
                    # Prevent self-references
                    if include_name == current_filename:
                        self.logger.debug(
                            "Skipping self-reference %s at depth %d for %s",
                            include_name, depth, root_filename
                        )
                        continue
                    
                    # Check for duplicate relations to prevent cycles
                    existing_relation = any(
                        rel.source_file == current_filename and rel.included_file == include_name
                        for rel in root_file.include_relations
                    )
                    
                    if existing_relation:
                        self.logger.debug(
                            "Skipping duplicate relation %s -> %s for %s",
                            current_filename, include_name, root_filename
                        )
                        continue
                    
                    # Prevent processing files that would create cycles (already processed)
                    if include_name in processed_files:
                        self.logger.debug(
                            "Skipping already processed file %s to prevent cycle for %s",
                            include_name, root_filename
                        )
                        continue
                    
                    # Create and add the include relation to the root C file
                    relation = IncludeRelation(
                        source_file=current_filename,
                        included_file=include_name,
                        depth=depth
                    )
                    root_file.include_relations.append(relation)
                    
                    self.logger.debug(
                        "Added include relation: %s -> %s (depth %d) for root %s",
                        current_filename, include_name, depth, root_filename
                    )
                    
                    # Add included file to next level for further processing
                    included_file = file_map[include_name]
                    if included_file not in next_level and include_name not in processed_files:
                        next_level.append(included_file)
            
            # Move to next level for the next iteration
            current_level = next_level
            
            # Break if no more files to process
            if not current_level:
                self.logger.debug(
                    "No more files to process at depth %d for %s", 
                    depth + 1, root_filename
                )
                break
        
        self.logger.debug(
            "Completed include processing for %s: %d relations generated",
            root_filename, len(root_file.include_relations)
        )
