#!/usr/bin/env python3
""""""

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
	""""""

	def __init__(self) -> None:
		self.logger = logging.getLogger(__name__)

	def transform(
		self, model_file: str, config_file: str, output_file: Optional[str] = None
	) -> str:
		""""""
		self.logger.info("Step 2: Transforming model: %s", model_file)

		model = self._load_model(model_file)
		config = self._load_config(config_file)

		transformed_model = self._apply_transformations(model, config)

		output_path = output_file or model_file
		self._save_model(transformed_model, output_path)

		self.logger.info("Step 2 complete! Transformed model saved to: %s", output_path)
		return output_path

	def _load_model(self, model_file: str) -> ProjectModel:
		""""""
		model_path = Path(model_file)
		if not model_path.exists():
			raise FileNotFoundError(f"Model file not found: {model_file}")

		try:
			model = ProjectModel.load(model_file)
			self.logger.debug("Loaded model with %d files", len(model.files))
			return model
		except Exception as e:
			raise ValueError(f"Failed to load model from {model_file}: {e}") from e

	def _load_config(self, config_file: str) -> Dict[str, Any]:
		""""""
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
		""""""
		self.logger.info("Applying transformations to model")

		if "file_filters" in config:
			model = self._apply_file_filters(model, config["file_filters"])

		config = self._ensure_backward_compatibility(config)

		model = self._apply_transformation_containers(model, config)

		if self._should_process_include_relations(config):
			model = self._process_include_relations_simplified(model, config)

		self.logger.info(
			"Transformations complete. Model now has %d files", len(model.files)
		)
		return model

	def _apply_transformation_containers(
		self, model: ProjectModel, config: Dict[str, Any]
	) -> ProjectModel:
		""""""
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
		""""""
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
		""""""
		if config.get("include_depth", 1) > 1:
			return True
		
		if "file_specific" in config:
			for file_config in config["file_specific"].values():
				if file_config.get("include_depth", 1) > 1:
					return True
		
		return False

	def _discover_transformation_containers(self, config: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
		""""""
		transformation_containers = [
			(key, value)
			for key, value in config.items()
			if key.startswith("transformations") and isinstance(value, dict)
		]
		
		transformation_containers.sort(key=lambda x: x[0])
		
		self.logger.info(
			"Discovered %d transformation containers: %s",
			len(transformation_containers),
			[name for name, _ in transformation_containers]
		)
		
		return transformation_containers

	def _ensure_backward_compatibility(self, config: Dict[str, Any]) -> Dict[str, Any]:
		""""""
		config = config.copy()
		
		if self._is_legacy_transformation_format(config):
			self.logger.info("Converting legacy 'transformations' format to container format")
			old_transformations = config.pop("transformations")
			config["transformations_00_default"] = old_transformations
			self.logger.debug("Converted to container: transformations_00_default")
		
		return config

	def _is_legacy_transformation_format(self, config: Dict[str, Any]) -> bool:
		""""""
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
		""""""
		self.logger.debug("Processing transformation container: %s", container_name)
		
		target_files = self._get_target_files(model, transformation_config)
		
		model = self._apply_remove_operations(model, transformation_config, target_files, container_name)
		model = self._apply_rename_operations(model, transformation_config, target_files, container_name)
		model = self._apply_add_operations(model, transformation_config, target_files, container_name)
		
		return model

	def _get_target_files(
		self, model: ProjectModel, transformation_config: Dict[str, Any]
	) -> Set[str]:
		""""""
		selected_files = transformation_config.get("file_selection", [])
		
		if not isinstance(selected_files, list):
			selected_files = []
			self.logger.warning("Invalid file_selection format, must be a list, defaulting to empty list")
		
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
		""""""
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
		""""""
		if "remove" not in transformation_config:
			return model
			
		self.logger.debug("Applying remove operations for container: %s", container_name)
		
		removed_typedef_names = self._collect_typedef_names_for_removal(
			model, transformation_config["remove"], target_files
		)
		
		model = self._apply_removals(model, transformation_config["remove"], target_files)
		
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
		""""""
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
		""""""
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
		""""""
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

	def _process_include_relations_simplified(
		self, model: ProjectModel, config: Dict[str, Any]
	) -> ProjectModel:
		""""""
		global_include_depth = config.get("include_depth", 1)
		file_specific_config = config.get("file_specific", {})
		include_filter_local_only = config.get("include_filter_local_only", False)
		always_show_includes = config.get("always_show_includes", False)
		
		self.logger.info(
			"Processing includes with simplified depth-based approach (global_depth=%d)", 
			global_include_depth
		)
		
		for file_model in model.files.values():
			file_model.include_relations = []
		
		file_map = {}
		for file_model in model.files.values():
			filename = Path(file_model.name).name
			file_map[filename] = file_model
		
		c_files = sorted([
			fm for fm in model.files.values() if fm.name.endswith(".c")
		], key=lambda fm: fm.name)
		
		for root_file in c_files:
			self._process_root_c_file_includes(
				root_file, file_map, global_include_depth, file_specific_config, include_filter_local_only, always_show_includes
			)
			
		return model
	
	def _process_root_c_file_includes(
		self, 
		root_file: FileModel, 
		file_map: Dict[str, FileModel],
		global_include_depth: int,
		file_specific_config: Dict[str, Any],
		include_filter_local_only: bool,
		always_show_includes: bool
	) -> None:
		""""""
		root_filename = Path(root_file.name).name
		
		include_depth = global_include_depth
		include_filters = []
		
		if root_filename in file_specific_config:
			file_config = file_specific_config[root_filename]
			include_depth = file_config.get("include_depth", global_include_depth)
			include_filters = file_config.get("include_filter", [])
		
		if include_filter_local_only:
			local_header_pattern = f"^{Path(root_filename).stem}\\.h$"
			if local_header_pattern not in include_filters:
				include_filters.append(local_header_pattern)
		
		if include_depth <= 1:
			self.logger.debug(
				"Skipping include processing for %s (depth=%d)", 
				root_filename, include_depth
			)
			return
			
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
		
		processed_files = set()
		try:
			root_file.placeholder_headers.clear()
		except Exception:
			root_file.placeholder_headers = set()
		
		current_level = [root_file]
		
		for depth in range(1, include_depth + 1):
			next_level = []
			
			self.logger.debug(
				"Processing depth %d for %s (%d files at current level)",
				depth, root_filename, len(current_level)
			)
			
			for current_file in sorted(current_level, key=lambda fm: Path(fm.name).name):
				current_filename = Path(current_file.name).name
				
				if current_filename in processed_files:
					continue
				processed_files.add(current_filename)
				
				for include_name in sorted(current_file.includes):
					filtered_out_by_patterns = False
					if compiled_filters:
						if not any(pattern.search(include_name) for pattern in compiled_filters):
							if always_show_includes:
								filtered_out_by_patterns = True
								self.logger.debug(
									"Include %s filtered by patterns at depth %d for %s, but will be shown as placeholder",
									include_name, depth, root_filename
								)
								# Intentionally do not continue here; still add relation and mark placeholder
							else:
								self.logger.debug(
									"Filtered out include %s at depth %d for %s",
									include_name, depth, root_filename
								)
								continue
					
					if include_name not in file_map:
						self.logger.debug(
							"Include %s not found in project files (depth %d, root %s)",
							include_name, depth, root_filename
						)
						continue
					
					if include_name == current_filename:
						self.logger.debug(
							"Skipping self-reference %s at depth %d for %s",
							include_name, depth, root_filename
						)
						continue
					
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
					
					if filtered_out_by_patterns:
						try:
							root_file.placeholder_headers.add(include_name)
						except Exception:
							root_file.placeholder_headers = {include_name}
						continue
					
					included_file = file_map[include_name]
					if included_file not in next_level and include_name not in processed_files:
						next_level.append(included_file)
			
			current_level = sorted(next_level, key=lambda fm: Path(fm.name).name)
			
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

	def _apply_file_filters(
		self, model: ProjectModel, filters: Dict[str, Any]
	) -> ProjectModel:
		""""""
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
		""""""
		self.logger.info(
			"Applying include filters for %d root files", len(include_filters)
		)

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
				continue

		if not compiled_filters:
			self.logger.warning(
				"No valid include filters found, skipping include filtering"
			)
			return model

		header_to_root = self._create_header_to_root_mapping(model)

		for file_path, file_model in model.files.items():
			root_file = self._find_root_file_with_mapping(
				file_path, file_model, header_to_root
			)

			if root_file in compiled_filters:
				self._filter_include_relations(
					file_model, compiled_filters[root_file], root_file
				)

		return model

	def _create_header_to_root_mapping(self, model: ProjectModel) -> Dict[str, str]:
		""""""
		header_to_root = {}
		c_files = []
		for file_path, file_model in model.files.items():
			if file_model.name.endswith(".c"):
				header_to_root[file_model.name] = file_model.name
				c_files.append(file_model.name)
		for file_path, file_model in model.files.items():
			if not file_model.name.endswith(".c"):
				header_base_name = Path(file_model.name).stem
				matching_c_file = header_base_name + ".c"
				
				if matching_c_file in [Path(c_file).name for c_file in c_files]:
					header_to_root[file_model.name] = matching_c_file
				else:
					including_c_files = []
					for c_file_path, c_file_model in model.files.items():
						if (c_file_model.name.endswith(".c") and 
							file_model.name in c_file_model.includes):
							including_c_files.append(c_file_model.name)
					
					if including_c_files:
						header_to_root[file_model.name] = including_c_files[0]
					else:
						if c_files:
							header_to_root[file_model.name] = c_files[0]
		return header_to_root

	def _find_root_file_with_mapping(
		self, file_path: str, file_model: FileModel, header_to_root: Dict[str, str]
	) -> str:
		""""""
		if file_model.name.endswith(".c"):
			return file_model.name
		return header_to_root.get(file_model.name, file_model.name)

	def _find_root_file(self, file_path: str, file_model: FileModel) -> str:
		""""""
		filename = Path(file_path).name
		if filename.endswith(".c"):
			return filename
		base_name = Path(file_path).stem
		if base_name and not filename.startswith("."):
			return base_name + ".c"
		return filename

	def _filter_include_relations(
		self, file_model: FileModel, patterns: List[re.Pattern], root_file: str
	) -> None:
		""""""
		self.logger.debug(
			"Filtering include_relations for file %s (root: %s)", file_model.name, root_file
		)

		original_relations_count = len(file_model.include_relations)
		filtered_relations: List[IncludeRelation] = []

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
				try:
					file_model.placeholder_headers.add(relation.included_file)
				except Exception:
					file_model.placeholder_headers = {relation.included_file}

		file_model.include_relations = filtered_relations

		self.logger.debug(
			"Include filtering for %s: relations %d->%d (includes preserved)",
			file_model.name,
			original_relations_count,
			len(file_model.include_relations),
		)

	def _matches_any_pattern(self, text: str, patterns: List[Pattern[str]]) -> bool:
		""""""
		return any(pattern.search(text) for pattern in patterns)
	
	def _matches_pattern(self, text: str, pattern: str) -> bool:
		""""""
		try:
			return bool(re.search(pattern, text))
		except re.error as e:
			self.logger.warning("Invalid regex pattern '%s': %s", pattern, e)
			return False

	# Removed unused _apply_model_transformations (legacy API)

	def _apply_renaming(
		self, model: ProjectModel, rename_config: Dict[str, Any], target_files: Set[str]
	) -> ProjectModel:
		""""""
		self.logger.debug(
			"Applying renaming transformations to %d files", len(target_files)
		)

		for file_path in target_files:
			if file_path in model.files:
				file_model = model.files[file_path]
				self.logger.debug("Applying renaming to file: %s", file_path)
				self._apply_file_level_renaming(file_model, rename_config)
		
		if "files" in rename_config:
			model = self._rename_files(model, rename_config["files"], target_files)

		return model

	def _apply_file_level_renaming(
		self, file_model: FileModel, rename_config: Dict[str, Any]
	) -> None:
		""""""
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
		""""""
		self.logger.debug("Starting type reference cleanup with patterns: %s, target_files: %s", 
						 removed_typedef_patterns, list(target_files))
		
		if not removed_typedef_patterns:
			self.logger.debug("No typedef patterns to clean up")
			return
			
		compiled_patterns = self._compile_patterns(removed_typedef_patterns)
		if not compiled_patterns:
			self.logger.debug("No valid compiled patterns")
			return
			
		removed_types = set()
		
		for file_path in target_files:
			if file_path in model.files:
				file_model = model.files[file_path]
				
				for alias_name in list(file_model.aliases.keys()):
					if self._matches_any_pattern(alias_name, compiled_patterns):
						removed_types.add(alias_name)
						self.logger.debug("Found removed typedef: %s in file %s", alias_name, file_path)
		
		self.logger.debug("Total removed types identified: %s", list(removed_types))
		
		cleaned_count = 0
		for file_path, file_model in model.files.items():
			file_cleaned = 0
			
			for func in file_model.functions:
				if func.return_type and self._contains_removed_type(func.return_type, removed_types):
					old_type = func.return_type
					func.return_type = self._remove_type_references(func.return_type, removed_types)
					if func.return_type != old_type:
						file_cleaned += 1
						self.logger.debug(
							"Cleaned return type '%s' -> '%s' in function %s", 
							old_type, func.return_type, func.name
						)
				
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
		""""""
		if not type_str or not removed_types:
			return False
			
		for removed_type in removed_types:
			if removed_type in type_str:
				return True
		return False
	
	def _remove_type_references(self, type_str: str, removed_types: Set[str]) -> str:
		""""""
		if not type_str or not removed_types:
			return type_str
			
		cleaned_type = type_str
		for removed_type in removed_types:
			if removed_type in cleaned_type:
				cleaned_type = cleaned_type.replace(removed_type, "void")
				
		cleaned_type = " ".join(cleaned_type.split())
		return cleaned_type
	
	def _cleanup_type_references_by_names(
		self, model: ProjectModel, removed_typedef_names: Set[str]
	) -> None:
		""""""
		if not removed_typedef_names:
			self.logger.debug("No removed typedef names provided")
			return
			
		self.logger.debug("Cleaning type references for removed typedefs: %s", list(removed_typedef_names))
		
		cleaned_count = 0
		for file_path, file_model in model.files.items():
			file_cleaned = 0
			
			for func in file_model.functions:
				if func.return_type and self._contains_removed_type(func.return_type, removed_typedef_names):
					old_type = func.return_type
					func.return_type = self._remove_type_references(func.return_type, removed_typedef_names)
					if func.return_type != old_type:
						file_cleaned += 1
						self.logger.debug(
							"Cleaned return type '%s' -> '%s' in function %s", 
							old_type, func.return_type, func.name
						)
				
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
		""""""
		updated_count = 0
		
		for func in file_model.functions:
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
		""""""
		if not type_str or not typedef_renames:
			return type_str
		
		updated_type = type_str
		for old_name, new_name in typedef_renames.items():
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
		""""""
		original_count = len(elements_dict)
		seen_names = set()
		deduplicated_elements = {}
		
		for name, element in elements_dict.items():
			new_name = self._apply_rename_patterns(name, patterns_map)
			
			if new_name in seen_names:
				self.logger.debug(
					"Deduplicating %s: removing duplicate '%s' (renamed from '%s')", 
					element_type, new_name, name
				)
				continue
				
			seen_names.add(new_name)
			
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
		""""""
		original_count = len(elements_list)
		seen_names = set()
		deduplicated_elements = []
		
		for element in elements_list:
			name = get_element_name(element)
			new_name = self._apply_rename_patterns(name, patterns_map)
			
			if new_name in seen_names:
				self.logger.debug(
					"Deduplicating %s: removing duplicate '%s' (renamed from '%s')", 
					element_type, new_name, name
				)
				continue
				
			seen_names.add(new_name)
			
			updated_element = create_renamed_element(new_name, element)
			deduplicated_elements.append(updated_element)
		
		removed_count = original_count - len(deduplicated_elements)
		if removed_count > 0:
			self.logger.info(
				"Renamed %ss in %s, removed %d duplicates", element_type, file_name, removed_count
			)
			
		return deduplicated_elements

	def _apply_rename_patterns(self, original_name: str, patterns_map: Dict[str, str]) -> str:
		""""""
		for pattern, replacement in patterns_map.items():
			try:
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
		""""""
		if not patterns_map:
			return
		
		typedef_renames = {}
		
		def create_renamed_alias(name: str, alias: Alias) -> Alias:
			return Alias(name, alias.original_type, alias.uses)
		
		for old_name in file_model.aliases:
			new_name = self._apply_rename_patterns(old_name, patterns_map)
			if new_name != old_name:
				typedef_renames[old_name] = new_name
		
		file_model.aliases = self._rename_dict_elements(
			file_model.aliases, patterns_map, create_renamed_alias, "typedef", file_model.name
		)
		
		if typedef_renames:
			self._update_type_references_for_renames(file_model, typedef_renames)

	def _rename_functions(self, file_model: FileModel, patterns_map: Dict[str, str]) -> None:
		""""""
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
		""""""
		if not patterns_map:
			return
		
		def get_macro_name(macro: str) -> str:
			import re
			if macro.startswith("#define "):
				match = re.search(r"#define\s+([A-Za-z_][A-Za-z0-9_]*)", macro)
				if match:
					return match.group(1)
			return macro
		
		def create_renamed_macro(name: str, macro: str) -> str:
			import re
			if macro.startswith("#define "):
				pattern = r"(#define\s+)([A-Za-z_][A-Za-z0-9_]*)(\s*\([^)]*\))?(.*)?"
				match = re.match(pattern, macro)
				if match:
					define_part = match.group(1)
					params = match.group(3) or ""
					rest = match.group(4) or ""
					return f"{define_part}{name}{params}{rest}"
			return macro
		
		file_model.macros = self._rename_list_elements(
			file_model.macros, patterns_map, get_macro_name, 
			create_renamed_macro, "macro", file_model.name
		)

	def _rename_globals(self, file_model: FileModel, patterns_map: Dict[str, str]) -> None:
		""""""
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
		""""""
		if not patterns_map:
			return
		
		file_model.includes = self._rename_set_elements(
			file_model.includes, patterns_map, "include", file_model.name
		)
		
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
		""""""
		original_count = len(elements_set)
		seen_names = set()
		deduplicated_elements = set()
		
		for element in elements_set:
			new_name = self._apply_rename_patterns(element, patterns_map)
			
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
		""""""
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
		""""""
		if not patterns_map:
			return
		
		def create_renamed_struct(name: str, struct: Struct) -> Struct:
			return Struct(name, struct.fields)
		
		file_model.structs = self._rename_dict_elements(
			file_model.structs, patterns_map, create_renamed_struct, "struct", file_model.name
		)

	def _rename_enums(self, file_model: FileModel, patterns_map: Dict[str, str]) -> None:
		""""""
		if not patterns_map:
			return
		
		def create_renamed_enum(name: str, enum: Enum) -> Enum:
			return Enum(name, enum.values)
		
		file_model.enums = self._rename_dict_elements(
			file_model.enums, patterns_map, create_renamed_enum, "enum", file_model.name
		)

	def _rename_unions(self, file_model: FileModel, patterns_map: Dict[str, str]) -> None:
		""""""
		if not patterns_map:
			return
		
		def create_renamed_union(name: str, union: Union) -> Union:
			return Union(name, union.fields)
		
		file_model.unions = self._rename_dict_elements(
			file_model.unions, patterns_map, create_renamed_union, "union", file_model.name
		)

	def _rename_files(self, model: ProjectModel, patterns_map: Dict[str, str], target_files: Set[str]) -> ProjectModel:
		""""""
		if not patterns_map:
			return model
		
		updated_files = {}
		file_rename_map: Dict[str, str] = {}
		
		for file_path, file_model in model.files.items():
			if file_path in target_files:
				new_file_path = self._apply_rename_patterns(file_path, patterns_map)
				
				if new_file_path != file_path:
					file_model.name = new_file_path
					file_rename_map[Path(file_path).name] = Path(new_file_path).name
					self.logger.debug("Renamed file: %s -> %s", file_path, new_file_path)
				
				updated_files[new_file_path] = file_model
			else:
				updated_files[file_path] = file_model
		
		model.files = updated_files

		if file_rename_map:
			for fm in model.files.values():
				if fm.includes:
					new_includes: Set[str] = set()
					for inc in fm.includes:
						inc_new = file_rename_map.get(inc, self._apply_rename_patterns(inc, patterns_map))
						new_includes.add(inc_new)
					fm.includes = new_includes

				if fm.include_relations:
					for rel in fm.include_relations:
						src_new = file_rename_map.get(rel.source_file, self._apply_rename_patterns(rel.source_file, patterns_map))
						inc_new = file_rename_map.get(rel.included_file, self._apply_rename_patterns(rel.included_file, patterns_map))
						rel.source_file = src_new
						rel.included_file = inc_new
		
		return model

	def _apply_additions(
		self, model: ProjectModel, add_config: Dict[str, Any], target_files: Set[str]
	) -> ProjectModel:
		""""""
		self.logger.debug(
			"Applying addition transformations to %d files", len(target_files)
		)

		for file_path in target_files:
			if file_path in model.files:
				self.logger.debug("Applying additions to file: %s", file_path)

		return model

	def _apply_removals(
		self, model: ProjectModel, remove_config: Dict[str, Any], target_files: Set[str]
	) -> ProjectModel:
		""""""
		self.logger.debug(
			"Applying removal transformations to %d files", len(target_files)
		)

		for file_path in target_files:
			if file_path in model.files:
				file_model = model.files[file_path]
				self.logger.debug("Applying removals to file: %s", file_path)
				self._apply_file_level_removals(file_model, remove_config)

		return model

	def _apply_file_level_removals(
		self, file_model: FileModel, remove_config: Dict[str, Any]
	) -> None:
		""""""
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
		""""""
		if not patterns:
			return elements_dict
			
		original_count = len(elements_dict)
		compiled_patterns = self._compile_patterns(patterns)
		
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
		""""""
		if not patterns:
			return elements_list
			
		original_count = len(elements_list)
		compiled_patterns = self._compile_patterns(patterns)
		
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
		""""""
		file_model.aliases = self._remove_dict_elements(
			file_model.aliases, patterns, "typedef", file_model.name
		)

	def _remove_functions(self, file_model: FileModel, patterns: List[str]) -> None:
		""""""
		def get_function_name(func: Function) -> str:
			return func.name
			
		file_model.functions = self._remove_list_elements(
			file_model.functions, patterns, get_function_name, "function", file_model.name
		)

	def _remove_macros(self, file_model: FileModel, patterns: List[str]) -> None:
		""""""
		def get_macro_name(macro: str) -> str:
			import re
			if macro.startswith("#define "):
				match = re.search(r"#define\s+([A-Za-z_][A-Za-z0-9_]*)", macro)
				if match:
					return match.group(1)
			return macro
			
		file_model.macros = self._remove_list_elements(
			file_model.macros, patterns, get_macro_name, "macro", file_model.name
		)

	def _remove_globals(self, file_model: FileModel, patterns: List[str]) -> None:
		""""""
		def get_global_name(global_var: Field) -> str:
			return global_var.name
			
		file_model.globals = self._remove_list_elements(
			file_model.globals, patterns, get_global_name, "global variable", file_model.name
		)

	def _remove_includes(self, file_model: FileModel, patterns: List[str]) -> None:
		""""""
		if not patterns:
			return
		
		original_count = len(file_model.includes)
		compiled_patterns = self._compile_patterns(patterns)
		
		filtered_includes = set()
		for include in file_model.includes:
			if not self._matches_any_pattern(include, compiled_patterns):
				filtered_includes.add(include)
			else:
				self.logger.debug("Removed include: %s", include)
		
		file_model.includes = filtered_includes
		removed_count = original_count - len(file_model.includes)
		
		if removed_count > 0:
			self._remove_matching_include_relations(file_model, compiled_patterns, removed_count)

	def _remove_matching_include_relations(
		self, file_model: FileModel, compiled_patterns: List[Pattern[str]], removed_includes_count: int
	) -> None:
		""""""
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
		""""""
		file_model.structs = self._remove_dict_elements(
			file_model.structs, patterns, "struct", file_model.name
		)

	def _remove_enums(self, file_model: FileModel, patterns: List[str]) -> None:
		""""""
		file_model.enums = self._remove_dict_elements(
			file_model.enums, patterns, "enum", file_model.name
		)

	def _remove_unions(self, file_model: FileModel, patterns: List[str]) -> None:
		""""""
		file_model.unions = self._remove_dict_elements(
			file_model.unions, patterns, "union", file_model.name
		)

	def _should_include_file(
		self,
		file_path: str,
		include_patterns: List[Pattern[str]],
		exclude_patterns: List[Pattern[str]],
	) -> bool:
		""""""
		if include_patterns:
			if not any(pattern.search(file_path) for pattern in include_patterns):
				return False

		if exclude_patterns:
			if any(pattern.search(file_path) for pattern in exclude_patterns):
				return False

		return True

	def _compile_patterns(self, patterns: List[str]) -> List[Pattern[str]]:
		""""""
		compiled_patterns: List[Pattern[str]] = []
		for pattern in patterns:
			try:
				compiled_patterns.append(re.compile(pattern))
			except re.error as e:
				self.logger.warning("Invalid regex pattern '%s': %s", pattern, e)
		return compiled_patterns

	# Removed unused _filter_dict (not used in current pipeline)

	# Removed unused _filter_list (not used in current pipeline)

	# Removed unused _dict_to_file_model (no callers in current code)

	def _save_model(self, model: ProjectModel, output_file: str) -> None:
		""""""
		try:
			model.save(output_file)
			self.logger.debug("Model saved to: %s", output_file)
		except Exception as e:
			raise ValueError(f"Failed to save model to {output_file}: {e}") from e
