#!/usr/bin/env python3
"""
Parser module for C to PlantUML converter - Step 1: Parse C code files and generate model.json
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
from .models import ProjectModel, FileModel, IncludeRelation


class CParser:
    """C/C++ parser for extracting structural information from source code"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_project(self, project_root: str, recursive: bool = True) -> ProjectModel:
        """Parse a C/C++ project and return a model"""
        project_root = Path(project_root).resolve()
        
        if not project_root.exists():
            raise ValueError(f"Project root not found: {project_root}")
        
        if not project_root.is_dir():
            raise ValueError(f"Project root must be a directory: {project_root}")
        
        self.logger.info(f"Parsing project: {project_root}")
        
        # Find C/C++ files
        c_files = self._find_c_files(project_root, recursive)
        self.logger.info(f"Found {len(c_files)} C/C++ files")
        
        # Parse each file
        files = {}
        failed_files = []
        
        for file_path in c_files:
            try:
                file_model = self.parse_file(file_path)
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
        
        self.logger.info(f"Parsing complete. Parsed {len(files)} files successfully.")
        return model
    
    def parse_file(self, file_path: Path) -> FileModel:
        """Parse a single C/C++ file and return a file model"""
        self.logger.debug(f"Parsing file: {file_path}")
        
        # Detect encoding
        encoding = self._detect_encoding(file_path)
        
        # Read file content
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        # Parse file content
        file_model = FileModel(
            file_path=str(file_path.resolve()),
            relative_path="",
            project_root="",
            encoding_used=encoding,
            structs=self._parse_structs(content),
            enums=self._parse_enums(content),
            unions=self._parse_unions(content),
            functions=self._parse_functions(content),
            globals=self._parse_globals(content),
            includes=self._parse_includes(content),
            macros=self._parse_macros(content),
            typedefs=self._parse_typedefs(content),
            typedef_relations=self._parse_typedef_relations(content),
            include_relations=[]
        )
        
        return file_model
    
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
    
    def _detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding"""
        try:
            import chardet
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except ImportError:
            return 'utf-8'
    
    def _parse_structs(self, content: str) -> Dict[str, 'Struct']:
        """Parse struct definitions from content"""
        # Implementation would go here - simplified for now
        return {}
    
    def _parse_enums(self, content: str) -> Dict[str, 'Enum']:
        """Parse enum definitions from content"""
        # Implementation would go here - simplified for now
        return {}
    
    def _parse_unions(self, content: str) -> Dict[str, 'Union']:
        """Parse union definitions from content"""
        # Implementation would go here - simplified for now
        return {}
    
    def _parse_functions(self, content: str) -> List['Function']:
        """Parse function declarations from content"""
        # Implementation would go here - simplified for now
        return []
    
    def _parse_globals(self, content: str) -> List['Field']:
        """Parse global variable declarations from content"""
        # Implementation would go here - simplified for now
        return []
    
    def _parse_includes(self, content: str) -> List[str]:
        """Parse #include directives from content"""
        # Implementation would go here - simplified for now
        return []
    
    def _parse_macros(self, content: str) -> List[str]:
        """Parse macro definitions from content"""
        # Implementation would go here - simplified for now
        return []
    
    def _parse_typedefs(self, content: str) -> Dict[str, str]:
        """Parse typedef definitions from content"""
        # Implementation would go here - simplified for now
        return {}
    
    def _parse_typedef_relations(self, content: str) -> List['TypedefRelation']:
        """Parse typedef relationships from content"""
        # Implementation would go here - simplified for now
        return []
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().isoformat()


class Parser:
    """Main parser class for Step 1: Parse C code files and generate model.json"""
    
    def __init__(self):
        self.c_parser = CParser()
        self.logger = logging.getLogger(__name__)
    
    def parse(self, project_root: str, output_file: str = "model.json", recursive: bool = True) -> str:
        """
        Step 1: Parse C code files and generate model.json
        
        Args:
            project_root: Root directory of C/C++ project
            output_file: Output JSON model file path
            recursive: Whether to search subdirectories recursively
            
        Returns:
            Path to the generated model.json file
        """
        self.logger.info(f"Step 1: Parsing C/C++ project: {project_root}")
        
        # Parse the project
        model = self.c_parser.parse_project(project_root, recursive)
        
        # Save model to JSON file
        model.save(output_file)
        
        self.logger.info(f"Step 1 complete! Model saved to: {output_file}")
        self.logger.info(f"Found {len(model.files)} files")
        
        # Print summary
        total_structs = sum(len(f.structs) for f in model.files.values())
        total_enums = sum(len(f.enums) for f in model.files.values())
        total_functions = sum(len(f.functions) for f in model.files.values())
        self.logger.info(f"Summary: {total_structs} structs, {total_enums} enums, {total_functions} functions")
        
        return output_file