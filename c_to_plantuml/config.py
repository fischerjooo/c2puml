#!/usr/bin/env python3
"""
Configuration handling for C to PlantUML converter
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
from .models import ProjectModel, FileModel


class Config:
    """Configuration for C to PlantUML converter"""
    
    def __init__(self, data: dict):
        self.project_roots = data.get('project_roots', [])
        self.project_name = data.get('project_name', 'C_Project')
        self.output_dir = data.get('output_dir', './plantuml_output')
        self.recursive = data.get('recursive', True)
        
        # File filters
        self.file_filters = data.get('file_filters', {})
        self.file_include_patterns = [re.compile(p) for p in self.file_filters.get('include', [])]
        self.file_exclude_patterns = [re.compile(p) for p in self.file_filters.get('exclude', [])]
        
        # Element filters
        self.element_filters = data.get('element_filters', {})
    
    @classmethod
    def load(cls, config_file: str) -> 'Config':
        """Load configuration from JSON file"""
        with open(config_file, 'r') as f:
            data = json.load(f)
        return cls(data)
    
    def has_filters(self) -> bool:
        """Check if any filters are configured"""
        return bool(self.file_filters or self.element_filters)
    
    def apply_filters(self, model: ProjectModel) -> ProjectModel:
        """Apply configured filters to the model"""
        # Apply file filters
        if self.file_include_patterns or self.file_exclude_patterns:
            filtered_files = {}
            for file_path, file_model in model.files.items():
                if self._should_include_file(file_path):
                    filtered_files[file_path] = self._apply_element_filters(file_model)
            model.files = filtered_files
        
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
        include_patterns = [re.compile(p) for p in filters.get('include', [])]
        exclude_patterns = [re.compile(p) for p in filters.get('exclude', [])]
        
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
        include_patterns = [re.compile(p) for p in filters.get('include', [])]
        exclude_patterns = [re.compile(p) for p in filters.get('exclude', [])]
        
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