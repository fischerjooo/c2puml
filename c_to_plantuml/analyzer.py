#!/usr/bin/env python3
"""
Core analyzer for C/C++ projects
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
from .parser import CParser
from .models import ProjectModel, FileModel, IncludeRelation
from .config import Config


class Analyzer:
    """Main analyzer for C/C++ projects"""
    
    def __init__(self):
        self.parser = CParser()
        self.logger = logging.getLogger(__name__)
    
    def analyze_project(self, project_root: str, recursive: bool = True) -> ProjectModel:
        """Analyze a C/C++ project and return a model"""
        project_root = Path(project_root).resolve()
        
        if not project_root.exists():
            raise ValueError(f"Project root not found: {project_root}")
        
        if not project_root.is_dir():
            raise ValueError(f"Project root must be a directory: {project_root}")
        
        self.logger.info(f"Analyzing project: {project_root}")
        
        # Find C/C++ files
        c_files = self._find_c_files(project_root, recursive)
        self.logger.info(f"Found {len(c_files)} C/C++ files")
        
        # Parse each file
        files = {}
        failed_files = []
        
        for file_path in c_files:
            try:
                file_model = self.parser.parse_file(file_path)
                relative_path = str(file_path.relative_to(project_root))
                # Update the file model with correct relative path
                file_model.relative_path = relative_path
                file_model.project_root = str(project_root)
                files[relative_path] = file_model
                
                self.logger.debug(f"Successfully parsed: {relative_path}")
                
            except Exception as e:
                self.logger.warning(f"Failed to parse {file_path}: {e}")
                failed_files.append(str(file_path))
        
        if failed_files:
            self.logger.warning(f"Failed to parse {len(failed_files)} files: {failed_files}")
        
        model = ProjectModel(
            project_name=project_root.name,
            project_root=str(project_root),
            files=files,
            created_at=self._get_timestamp()
        )
        
        self.logger.info(f"Analysis complete. Parsed {len(files)} files successfully.")
        return model
    
    def analyze_with_config(self, config: Config) -> ProjectModel:
        """Analyze project using configuration"""
        self.logger.info(f"Analyzing project with config: {config.project_name}")
        
        # Analyze all project roots
        all_files = {}
        
        for project_root in config.project_roots:
            self.logger.info(f"Analyzing project root: {project_root}")
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
            self.logger.info("Applying filters to model")
            combined_model = config.apply_filters(combined_model)
        
        # Process include relationships if depth > 1
        if config.include_depth > 1:
            self.logger.info(f"Processing include relationships with depth {config.include_depth}")
            combined_model = self._process_include_relations(combined_model, config.include_depth)
        
        self.logger.info(f"Combined analysis complete. Total files: {len(combined_model.files)}")
        return combined_model
    
    def _find_c_files(self, project_root: Path, recursive: bool) -> List[Path]:
        """Find all C/C++ files in the project"""
        c_extensions = {'.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.hxx'}
        files = []
        
        self.logger.debug(f"Searching for files with extensions: {c_extensions}")
        
        if recursive:
            for ext in c_extensions:
                files.extend(project_root.rglob(f"*{ext}"))
        else:
            for ext in c_extensions:
                files.extend(project_root.glob(f"*{ext}"))
        
        # Filter out hidden files and common exclude patterns
        filtered_files = []
        exclude_patterns = {'.git', '__pycache__', 'node_modules', '.vscode', '.idea'}
        
        for file_path in files:
            # Skip hidden files and directories
            if any(part.startswith('.') for part in file_path.parts):
                continue
            
            # Skip common exclude patterns
            if any(pattern in file_path.parts for pattern in exclude_patterns):
                continue
            
            filtered_files.append(file_path)
        
        self.logger.debug(f"Found {len(filtered_files)} C/C++ files after filtering")
        return sorted(filtered_files)
    
    def _process_include_relations(self, model: ProjectModel, max_depth: int) -> ProjectModel:
        """Process include relationships up to specified depth"""
        self.logger.info(f"Processing include relations with max depth: {max_depth}")
        
        # Create a mapping of file paths to their models for quick lookup
        file_map = {file_model.file_path: file_model for file_model in model.files.values()}
        
        # Process each file's includes
        for file_path, file_model in model.files.items():
            self._process_file_includes(file_model, file_map, max_depth, 1, set())
        
        return model
    
    def _process_file_includes(self, file_model: FileModel, file_map: Dict[str, FileModel], 
                              max_depth: int, current_depth: int, visited: Set[str]) -> None:
        """Recursively process includes for a file"""
        if current_depth > max_depth or file_model.file_path in visited:
            return
        
        visited.add(file_model.file_path)
        
        # Process each include
        for include_name in file_model.includes:
            # Try to find the included file
            included_file_path = self._find_included_file(include_name, file_model.project_root)
            
            if included_file_path and included_file_path in file_map:
                # Create include relation
                include_relation = IncludeRelation(
                    source_file=file_model.file_path,
                    included_file=included_file_path,
                    depth=current_depth
                )
                file_model.include_relations.append(include_relation)
                
                # Recursively process the included file
                included_file_model = file_map[included_file_path]
                self._process_file_includes(included_file_model, file_map, max_depth, 
                                          current_depth + 1, visited.copy())
    
    def _find_included_file(self, include_name: str, project_root: str) -> Optional[str]:
        """Find the actual file path for an include"""
        # Common include paths to search
        search_paths = [
            Path(project_root),
            Path(project_root) / "include",
            Path(project_root) / "src",
            Path(project_root) / "lib",
            Path(project_root) / "headers"
        ]
        
        # Try different extensions
        extensions = ['.h', '.hpp', '.hxx', '']
        
        for search_path in search_paths:
            if not search_path.exists():
                continue
                
            for ext in extensions:
                file_path = search_path / f"{include_name}{ext}"
                if file_path.exists():
                    return str(file_path.resolve())
        
        return None
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().isoformat()