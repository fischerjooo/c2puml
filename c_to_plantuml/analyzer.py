#!/usr/bin/env python3
"""
Core analyzer for C/C++ projects
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from .parser import CParser
from .models import ProjectModel, FileModel
from .config import Config


class Analyzer:
    """Main analyzer for C/C++ projects"""
    
    def __init__(self):
        self.parser = CParser()
    
    def analyze_project(self, project_root: str, recursive: bool = True) -> ProjectModel:
        """Analyze a C/C++ project and return a model"""
        project_root = Path(project_root).resolve()
        
        if not project_root.exists():
            raise ValueError(f"Project root not found: {project_root}")
        
        # Find C/C++ files
        c_files = self._find_c_files(project_root, recursive)
        
        # Parse each file
        files = {}
        for file_path in c_files:
            try:
                file_model = self.parser.parse_file(file_path)
                relative_path = str(file_path.relative_to(project_root))
                # Update the file model with correct relative path
                file_model.relative_path = relative_path
                file_model.project_root = str(project_root)
                files[relative_path] = file_model
            except Exception as e:
                print(f"Warning: Failed to parse {file_path}: {e}")
        
        return ProjectModel(
            project_name=project_root.name,
            project_root=str(project_root),
            files=files,
            created_at=self._get_timestamp()
        )
    
    def analyze_with_config(self, config: Config) -> ProjectModel:
        """Analyze project using configuration"""
        # Analyze all project roots
        all_files = {}
        
        for project_root in config.project_roots:
            model = self.analyze_project(project_root, config.recursive)
            all_files.update(model.files)
        
        # Create combined model
        combined_model = ProjectModel(
            project_name=config.project_name,
            project_root=",".join(config.project_roots),
            files=all_files,
            created_at=self._get_timestamp()
        )
        
        # Apply filters if specified
        if config.has_filters():
            combined_model = config.apply_filters(combined_model)
        
        return combined_model
    
    def _find_c_files(self, project_root: Path, recursive: bool) -> List[Path]:
        """Find all C/C++ files in the project"""
        c_extensions = {'.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.hxx'}
        files = []
        
        if recursive:
            for ext in c_extensions:
                files.extend(project_root.rglob(f"*{ext}"))
        else:
            for ext in c_extensions:
                files.extend(project_root.glob(f"*{ext}"))
        
        return sorted(files)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().isoformat()