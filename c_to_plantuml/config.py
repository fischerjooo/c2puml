#!/usr/bin/env python3
"""
Configuration handling for C to PlantUML converter
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from .models import ProjectModel, FileModel


class Config:
    """Configuration for C to PlantUML converter"""
    
    def __init__(self, data: dict):
        self.logger = logging.getLogger(__name__)
        
        # Validate required fields
        if not isinstance(data, dict):
            raise ValueError("Configuration data must be a dictionary")
        
        # Basic configuration
        self.project_roots = self._validate_project_roots(data.get('project_roots', []))
        self.project_name = data.get('project_name', 'C_Project')
        self.output_dir = data.get('output_dir', './plantuml_output')
        self.model_output_path = data.get('model_output_path', f"{self.project_name}_model.json")
        self.recursive = data.get('recursive', True)
        self.include_depth = data.get('include_depth', 1)
        
        # File filters
        self.file_filters = data.get('file_filters', {})
        self.file_include_patterns = self._compile_patterns(
            self.file_filters.get('include', [])
        )
        self.file_exclude_patterns = self._compile_patterns(
            self.file_filters.get('exclude', [])
        )
        
        # Element filters
        self.element_filters = data.get('element_filters', {})
        
        self.logger.debug(f"Configuration loaded: {self.project_name}")
    
    def _validate_project_roots(self, project_roots: List[str]) -> List[str]:
        """Validate project roots"""
        if not isinstance(project_roots, list):
            raise ValueError("project_roots must be a list")
        
        validated_roots = []
        for root in project_roots:
            if not isinstance(root, str):
                raise ValueError(f"Project root must be a string: {root}")
            
            path = Path(root)
            if not path.exists():
                self.logger.warning(f"Project root does not exist: {root}")
            
            validated_roots.append(str(path.resolve()))
        
        return validated_roots
    
    def _compile_patterns(self, patterns: List[str]) -> List[re.Pattern]:
        """Compile regex patterns with error handling"""
        compiled_patterns = []
        
        for pattern in patterns:
            try:
                compiled_patterns.append(re.compile(pattern))
            except re.error as e:
                self.logger.warning(f"Invalid regex pattern '{pattern}': {e}")
        
        return compiled_patterns
    
    @classmethod
    def load(cls, config_file: str) -> 'Config':
        """Load configuration from JSON file"""
        logger = logging.getLogger(__name__)
        
        if not Path(config_file).exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Loaded configuration from: {config_file}")
            return cls(data)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file {config_file}: {e}")
        except Exception as e:
            raise ValueError(f"Failed to load configuration from {config_file}: {e}")
    
    def save(self, config_file: str) -> None:
        """Save configuration to JSON file"""
        data = {
            'project_roots': self.project_roots,
            'project_name': self.project_name,
            'output_dir': self.output_dir,
            'model_output_path': self.model_output_path,
            'recursive': self.recursive,
            'include_depth': self.include_depth,
            'file_filters': self.file_filters,
            'element_filters': self.element_filters
        }
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Configuration saved to: {config_file}")
        except Exception as e:
            raise ValueError(f"Failed to save configuration to {config_file}: {e}")
    
    def has_filters(self) -> bool:
        """Check if any filters are configured"""
        return bool(self.file_filters or self.element_filters)
    
    def apply_filters(self, model: ProjectModel) -> ProjectModel:
        """Apply configured filters to the model"""
        self.logger.debug("Applying filters to model")
        
        # Apply file filters
        if self.file_include_patterns or self.file_exclude_patterns:
            filtered_files = {}
            for file_path, file_model in model.files.items():
                if self._should_include_file(file_path):
                    filtered_files[file_path] = self._apply_element_filters(file_model)
            model.files = filtered_files
            
            self.logger.debug(f"File filtering: {len(model.files)} files after filtering")
        
        return model
    
    def _should_include_file(self, file_path: str) -> bool:
        """Check if a file should be included based on filters"""
        # Check include patterns
        if self.file_include_patterns:
            if not any(pattern.search(file_path) for pattern in self.file_include_patterns):
                return False
        
        # Check exclude patterns
        if self.file_exclude_patterns:
            if any(pattern.search(file_path) for pattern in self.file_exclude_patterns):
                return False
        
        return True
    
    def _apply_element_filters(self, file_model: FileModel) -> FileModel:
        """Apply element filters to a file model"""
        if not self.element_filters:
            return file_model
        
        # Filter structs
        if 'structs' in self.element_filters:
            file_model.structs = self._filter_dict(
                file_model.structs, 
                self.element_filters['structs']
            )
        
        # Filter enums
        if 'enums' in self.element_filters:
            file_model.enums = self._filter_dict(
                file_model.enums, 
                self.element_filters['enums']
            )
        
        # Filter functions
        if 'functions' in self.element_filters:
            file_model.functions = self._filter_list(
                file_model.functions, 
                self.element_filters['functions'],
                key=lambda f: f.name
            )
        
        # Filter globals
        if 'globals' in self.element_filters:
            file_model.globals = self._filter_list(
                file_model.globals, 
                self.element_filters['globals'],
                key=lambda g: g.name
            )
        
        return file_model
    
    def _filter_dict(self, items: Dict, filters: Dict) -> Dict:
        """Filter a dictionary based on include/exclude patterns"""
        include_patterns = self._compile_patterns(filters.get('include', []))
        exclude_patterns = self._compile_patterns(filters.get('exclude', []))
        
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
        include_patterns = self._compile_patterns(filters.get('include', []))
        exclude_patterns = self._compile_patterns(filters.get('exclude', []))
        
        filtered = []
        for item in items:
            name = key(item) if key else str(item)
            
            # Check include patterns
            if include_patterns:
                if not any(pattern.search(name) for pattern in include_patterns):
                    continue
            
            # Check exclude patterns
            if exclude_patterns:
                if any(pattern.search(name) for pattern in exclude_patterns):
                    continue
            
            filtered.append(item)
        
        return filtered
    
    def get_summary(self) -> dict:
        """Get a summary of the configuration"""
        return {
            'project_name': self.project_name,
            'project_roots': self.project_roots,
            'output_dir': self.output_dir,
            'recursive': self.recursive,
            'include_depth': self.include_depth,
            'has_file_filters': bool(self.file_filters),
            'has_element_filters': bool(self.element_filters),
            'include_patterns': len(self.file_include_patterns),
            'exclude_patterns': len(self.file_exclude_patterns)
        }