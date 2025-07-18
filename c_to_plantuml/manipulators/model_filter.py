#!/usr/bin/env python3
"""
Model Filter for advanced manipulation of parsed C model data
Supports regex-based filtering, renaming, and model manipulation
"""

import re
import json
from typing import Dict, List, Any, Pattern, Optional, Union
from ..models.project_model import ProjectModel, FileModel
from ..models.c_structures import Struct, Enum, Function, Field


class ModelFilter:
    """
    Advanced filter for manipulating parsed C models using regex patterns
    Supports file filtering, element filtering, renaming, and additions
    """
    
    def __init__(self):
        self.file_filters = {}
        self.element_filters = {}
        self.transformations = {}
        self.additions = {}
        self.compiled_patterns = {}
        
    def load_config(self, config_path: str) -> None:
        """Load filtering configuration from JSON file"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        self.file_filters = config.get('file_filters', {})
        self.element_filters = config.get('element_filters', {})
        self.transformations = config.get('transformations', {})
        self.additions = config.get('additions', {})
        
        # Pre-compile regex patterns for performance
        self._compile_patterns()
        
    def _compile_patterns(self) -> None:
        """Pre-compile all regex patterns for better performance"""
        self.compiled_patterns = {}
        
        # Compile file filter patterns
        for filter_type, patterns in self.file_filters.items():
            if isinstance(patterns, dict):
                for key, pattern_list in patterns.items():
                    if isinstance(pattern_list, list):
                        self.compiled_patterns[f"file_{filter_type}_{key}"] = [
                            re.compile(pattern) for pattern in pattern_list
                        ]
                    elif isinstance(pattern_list, str):
                        self.compiled_patterns[f"file_{filter_type}_{key}"] = [re.compile(pattern_list)]
        
        # Compile element filter patterns
        for element_type, filters in self.element_filters.items():
            if isinstance(filters, dict):
                for filter_action, patterns in filters.items():
                    if isinstance(patterns, list):
                        self.compiled_patterns[f"element_{element_type}_{filter_action}"] = [
                            re.compile(pattern) for pattern in patterns
                        ]
                    elif isinstance(patterns, str):
                        self.compiled_patterns[f"element_{element_type}_{filter_action}"] = [re.compile(patterns)]
        
        # Compile transformation patterns
        for transform_type, transforms in self.transformations.items():
            if isinstance(transforms, dict):
                for pattern, replacement in transforms.items():
                    self.compiled_patterns[f"transform_{transform_type}_{pattern}"] = re.compile(pattern)
    
    def apply_file_filters(self, model: ProjectModel) -> ProjectModel:
        """Apply file-level filters to remove/include files based on regex patterns"""
        filtered_files = {}
        
        include_patterns = self.compiled_patterns.get('file_files_include', [])
        exclude_patterns = self.compiled_patterns.get('file_files_exclude', [])
        
        for file_path, file_model in model.files.items():
            # Check if file should be included
            if include_patterns:
                if not any(pattern.search(file_path) for pattern in include_patterns):
                    continue
            
            # Check if file should be excluded
            if exclude_patterns:
                if any(pattern.search(file_path) for pattern in exclude_patterns):
                    continue
                    
            filtered_files[file_path] = file_model
        
        # Create new model with filtered files
        return ProjectModel(
            project_name=model.project_name,
            project_roots=model.project_roots,
            files=filtered_files,
            global_includes=model.global_includes,
            created_at=model.created_at
        )
    
    def apply_element_filters(self, model: ProjectModel) -> ProjectModel:
        """Apply element-level filters (structs, enums, functions) using regex patterns"""
        filtered_files = {}
        
        for file_path, file_model in model.files.items():
            # Filter structs
            filtered_structs = self._filter_elements(
                file_model.structs, 'structs', lambda s: s.name
            )
            
            # Filter enums
            filtered_enums = self._filter_elements(
                file_model.enums, 'enums', lambda e: e.name
            )
            
            # Filter functions
            filtered_functions = self._filter_function_list(file_model.functions)
            
            # Filter globals
            filtered_globals = self._filter_field_list(file_model.globals, 'globals')
            
            # Create filtered file model
            filtered_files[file_path] = FileModel(
                file_path=file_model.file_path,
                relative_path=file_model.relative_path,
                project_root=file_model.project_root,
                encoding_used=file_model.encoding_used,
                structs=filtered_structs,
                enums=filtered_enums,
                functions=filtered_functions,
                globals=filtered_globals,
                includes=file_model.includes,
                macros=file_model.macros,
                typedefs=file_model.typedefs
            )
        
        return ProjectModel(
            project_name=model.project_name,
            project_roots=model.project_roots,
            files=filtered_files,
            global_includes=model.global_includes,
            created_at=model.created_at
        )
    
    def _filter_elements(self, elements: Dict[str, Any], element_type: str, name_getter) -> Dict[str, Any]:
        """Generic element filtering using regex patterns"""
        include_patterns = self.compiled_patterns.get(f'element_{element_type}_include', [])
        exclude_patterns = self.compiled_patterns.get(f'element_{element_type}_exclude', [])
        
        filtered = {}
        for name, element in elements.items():
            element_name = name_getter(element)
            
            # Check include patterns
            if include_patterns:
                if not any(pattern.search(element_name) for pattern in include_patterns):
                    continue
            
            # Check exclude patterns
            if exclude_patterns:
                if any(pattern.search(element_name) for pattern in exclude_patterns):
                    continue
            
            filtered[name] = element
        
        return filtered
    
    def _filter_function_list(self, functions: List[Function]) -> List[Function]:
        """Filter function list using regex patterns"""
        include_patterns = self.compiled_patterns.get('element_functions_include', [])
        exclude_patterns = self.compiled_patterns.get('element_functions_exclude', [])
        
        filtered = []
        for func in functions:
            # Check include patterns
            if include_patterns:
                if not any(pattern.search(func.name) for pattern in include_patterns):
                    continue
            
            # Check exclude patterns
            if exclude_patterns:
                if any(pattern.search(func.name) for pattern in exclude_patterns):
                    continue
            
            filtered.append(func)
        
        return filtered
    
    def _filter_field_list(self, fields: List[Field], element_type: str) -> List[Field]:
        """Filter field list using regex patterns"""
        include_patterns = self.compiled_patterns.get(f'element_{element_type}_include', [])
        exclude_patterns = self.compiled_patterns.get(f'element_{element_type}_exclude', [])
        
        filtered = []
        for field in fields:
            # Check include patterns
            if include_patterns:
                if not any(pattern.search(field.name) for pattern in include_patterns):
                    continue
            
            # Check exclude patterns
            if exclude_patterns:
                if any(pattern.search(field.name) for pattern in exclude_patterns):
                    continue
            
            filtered.append(field)
        
        return filtered
    
    def apply_transformations(self, model: ProjectModel) -> ProjectModel:
        """Apply transformations (renaming) using regex patterns"""
        transformed_files = {}
        
        for file_path, file_model in model.files.items():
            # Transform structs
            transformed_structs = self._transform_elements(
                file_model.structs, 'structs', lambda s, new_name: self._rename_struct(s, new_name)
            )
            
            # Transform enums
            transformed_enums = self._transform_elements(
                file_model.enums, 'enums', lambda e, new_name: self._rename_enum(e, new_name)
            )
            
            # Transform functions
            transformed_functions = self._transform_function_list(file_model.functions)
            
            # Create transformed file model
            transformed_files[file_path] = FileModel(
                file_path=file_model.file_path,
                relative_path=file_model.relative_path,
                project_root=file_model.project_root,
                encoding_used=file_model.encoding_used,
                structs=transformed_structs,
                enums=transformed_enums,
                functions=transformed_functions,
                globals=file_model.globals,
                includes=file_model.includes,
                macros=file_model.macros,
                typedefs=file_model.typedefs
            )
        
        return ProjectModel(
            project_name=model.project_name,
            project_roots=model.project_roots,
            files=transformed_files,
            global_includes=model.global_includes,
            created_at=model.created_at
        )
    
    def _transform_elements(self, elements: Dict[str, Any], element_type: str, rename_func) -> Dict[str, Any]:
        """Apply regex-based transformations to elements"""
        transformed = {}
        
        # Get transformation patterns for this element type
        transform_configs = self.transformations.get(element_type, {})
        
        for name, element in elements.items():
            new_name = name
            new_element = element
            
            # Apply each transformation pattern
            for pattern_str, replacement in transform_configs.items():
                pattern_key = f"transform_{element_type}_{pattern_str}"
                if pattern_key in self.compiled_patterns:
                    pattern = self.compiled_patterns[pattern_key]
                    if pattern.search(new_name):
                        new_name = pattern.sub(replacement, new_name)
                        new_element = rename_func(new_element, new_name)
            
            transformed[new_name] = new_element
        
        return transformed
    
    def _transform_function_list(self, functions: List[Function]) -> List[Function]:
        """Apply regex-based transformations to function names"""
        transformed = []
        transform_configs = self.transformations.get('functions', {})
        
        for func in functions:
            new_name = func.name
            
            # Apply each transformation pattern
            for pattern_str, replacement in transform_configs.items():
                pattern_key = f"transform_functions_{pattern_str}"
                if pattern_key in self.compiled_patterns:
                    pattern = self.compiled_patterns[pattern_key]
                    if pattern.search(new_name):
                        new_name = pattern.sub(replacement, new_name)
            
            # Create new function with transformed name
            transformed_func = Function(
                name=new_name,
                return_type=func.return_type,
                parameters=func.parameters,
                is_static=func.is_static
            )
            transformed.append(transformed_func)
        
        return transformed
    
    def _rename_struct(self, struct: Struct, new_name: str) -> Struct:
        """Create a new struct with updated name"""
        return Struct(
            name=new_name,
            fields=struct.fields,
            functions=struct.functions,
            typedef_name=struct.typedef_name
        )
    
    def _rename_enum(self, enum: Enum, new_name: str) -> Enum:
        """Create a new enum with updated name"""
        return Enum(
            name=new_name,
            values=enum.values,
            typedef_name=enum.typedef_name
        )
    
    def apply_additions(self, model: ProjectModel) -> ProjectModel:
        """Add new elements to the model based on configuration"""
        modified_files = {}
        
        for file_path, file_model in model.files.items():
            # Add new structs
            new_structs = dict(file_model.structs)
            for struct_config in self.additions.get('structs', []):
                if self._should_add_to_file(file_path, struct_config.get('target_files', [])):
                    struct = self._create_struct_from_config(struct_config)
                    new_structs[struct.name] = struct
            
            # Add new enums
            new_enums = dict(file_model.enums)
            for enum_config in self.additions.get('enums', []):
                if self._should_add_to_file(file_path, enum_config.get('target_files', [])):
                    enum = self._create_enum_from_config(enum_config)
                    new_enums[enum.name] = enum
            
            # Add new functions
            new_functions = list(file_model.functions)
            for func_config in self.additions.get('functions', []):
                if self._should_add_to_file(file_path, func_config.get('target_files', [])):
                    func = self._create_function_from_config(func_config)
                    new_functions.append(func)
            
            modified_files[file_path] = FileModel(
                file_path=file_model.file_path,
                relative_path=file_model.relative_path,
                project_root=file_model.project_root,
                encoding_used=file_model.encoding_used,
                structs=new_structs,
                enums=new_enums,
                functions=new_functions,
                globals=file_model.globals,
                includes=file_model.includes,
                macros=file_model.macros,
                typedefs=file_model.typedefs
            )
        
        return ProjectModel(
            project_name=model.project_name,
            project_roots=model.project_roots,
            files=modified_files,
            global_includes=model.global_includes,
            created_at=model.created_at
        )
    
    def _should_add_to_file(self, file_path: str, target_patterns: List[str]) -> bool:
        """Check if element should be added to specific file using regex"""
        if not target_patterns:
            return True  # Add to all files if no specific targets
        
        for pattern in target_patterns:
            if re.search(pattern, file_path):
                return True
        return False
    
    def _create_struct_from_config(self, config: Dict[str, Any]) -> Struct:
        """Create a struct from configuration dictionary"""
        fields = []
        for field_config in config.get('fields', []):
            field = Field(
                name=field_config['name'],
                type=field_config['type'],
                array_size=field_config.get('array_size')
            )
            fields.append(field)
        
        return Struct(
            name=config['name'],
            fields=fields,
            functions=[],  # Functions would need separate configuration
            typedef_name=config.get('typedef_name')
        )
    
    def _create_enum_from_config(self, config: Dict[str, Any]) -> Enum:
        """Create an enum from configuration dictionary"""
        return Enum(
            name=config['name'],
            values=config.get('values', []),
            typedef_name=config.get('typedef_name')
        )
    
    def _create_function_from_config(self, config: Dict[str, Any]) -> Function:
        """Create a function from configuration dictionary"""
        parameters = []
        for param_config in config.get('parameters', []):
            param = Field(
                name=param_config['name'],
                type=param_config['type'],
                array_size=param_config.get('array_size')
            )
            parameters.append(param)
        
        return Function(
            name=config['name'],
            return_type=config.get('return_type', 'void'),
            parameters=parameters,
            is_static=config.get('is_static', False)
        )
    
    def apply_all_filters(self, model: ProjectModel) -> ProjectModel:
        """Apply all configured filters and transformations in sequence"""
        # Apply filters in sequence
        filtered_model = self.apply_file_filters(model)
        filtered_model = self.apply_element_filters(filtered_model)
        filtered_model = self.apply_transformations(filtered_model)
        filtered_model = self.apply_additions(filtered_model)
        
        return filtered_model