import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
from .parsers.c_parser import CParser
from .models.project_model import ProjectModel, FileModel
from .utils.file_utils import find_c_files

class ProjectAnalyzer:
    """Analyzes C projects and builds a comprehensive abstract model"""
    
    def __init__(self):
        self.parser = CParser()
        self.file_cache = {}  # For directory listing cache
    
    def analyze_project(self, project_roots: List[str], project_name: str = "C_Project", 
                       c_file_prefixes: Optional[List[str]] = None, recursive: bool = True) -> ProjectModel:
        """
        Analyze a C project and return a comprehensive model
        
        Args:
            project_roots: List of root directories to scan
            project_name: Name for the project
            c_file_prefixes: Optional prefixes to filter files
            recursive: Whether to search recursively
            
        Returns:
            ProjectModel containing all parsed information
        """
        print(f"Starting analysis of project: {project_name}")
        
        # Collect all C files from all project roots
        all_c_files = []
        c_extensions = {'.c', '.cpp', '.cc', '.cxx'}
        
        for project_root in project_roots:
            print(f"Scanning project root: {project_root}")
            if not os.path.exists(project_root):
                print(f"Warning: Project root does not exist: {project_root}")
                continue
                
            c_files = [f for f in find_c_files(project_root, recursive) 
                      if os.path.splitext(f)[1].lower() in c_extensions]
            
            # Apply prefix filter if specified
            if c_file_prefixes:
                c_files = [f for f in c_files 
                          if any(os.path.basename(f).startswith(prefix) for prefix in c_file_prefixes)]
            
            all_c_files.extend([(f, project_root) for f in c_files])
        
        if not all_c_files:
            print("No C files found matching criteria")
            return ProjectModel(
                project_name=project_name,
                project_roots=project_roots,
                files={},
                global_includes=[],
                created_at=datetime.now().isoformat()
            )
        
        print(f"Found {len(all_c_files)} C files to analyze")
        
        # Build the comprehensive model
        files_model = {}
        global_includes = set()
        
        for i, (c_file, project_root) in enumerate(all_c_files, 1):
            print(f"Analyzing file {i}/{len(all_c_files)}: {os.path.basename(c_file)}")
            
            try:
                file_model = self._analyze_single_file(c_file, project_root)
                files_model[c_file] = file_model
                global_includes.update(file_model.includes)
                
                # Clear cache periodically to manage memory
                if len(self.parser.file_cache) > 50:
                    self.parser.clear_cache()
                    
            except Exception as e:
                print(f"Error analyzing {c_file}: {e}")
                continue
        
        # Create the comprehensive project model
        project_model = ProjectModel(
            project_name=project_name,
            project_roots=project_roots,
            files=files_model,
            global_includes=sorted(list(global_includes)),
            created_at=datetime.now().isoformat()
        )
        
        print(f"Analysis complete. Processed {len(files_model)} files successfully.")
        return project_model
    
    def _analyze_single_file(self, c_file: str, project_root: str) -> FileModel:
        """Analyze a single C file and return a FileModel"""
        
        # Parse the file
        content, encoding = self.parser.parse_file(c_file)
        
        # Calculate relative path
        try:
            relative_path = os.path.relpath(c_file, project_root)
        except ValueError:
            # Handle case where c_file is not under project_root
            relative_path = os.path.basename(c_file)
        
        # Create file model
        file_model = FileModel(
            file_path=c_file,
            relative_path=relative_path,
            project_root=project_root,
            encoding_used=encoding,
            structs=self.parser.structs.copy(),
            enums=self.parser.enums.copy(),
            functions=self.parser.functions.copy(),
            globals=self.parser.globals.copy(),
            includes=sorted(list(self.parser.includes)),
            macros=self.parser.macros.copy(),
            typedefs=self.parser.typedefs.copy()
        )
        
        return file_model
    
    def save_model_to_json(self, model: ProjectModel, output_path: str) -> None:
        """Save the project model to a JSON file"""
        print(f"Saving project model to: {output_path}")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        model.save_to_json(output_path)
        print(f"Project model saved successfully to {output_path}")
    
    def analyze_and_save(self, project_roots: List[str], output_path: str, 
                        project_name: str = "C_Project", 
                        c_file_prefixes: Optional[List[str]] = None, 
                        recursive: bool = True) -> ProjectModel:
        """
        Convenience method to analyze project and save model in one step
        
        Returns the created model for further processing
        """
        model = self.analyze_project(
            project_roots=project_roots,
            project_name=project_name,
            c_file_prefixes=c_file_prefixes,
            recursive=recursive
        )
        
        self.save_model_to_json(model, output_path)
        return model

def load_config_and_analyze(config_path: str) -> ProjectModel:
    """Load configuration and analyze project using the config file"""
    import json
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    project_roots = config.get('project_roots', [])
    project_name = config.get('project_name', 'C_Project')
    c_file_prefixes = config.get('c_file_prefixes', [])
    recursive = config.get('recursive', True)
    model_output_path = config.get('model_output_path', './project_model.json')
    
    if not isinstance(c_file_prefixes, list):
        c_file_prefixes = [c_file_prefixes] if c_file_prefixes else []
    
    if not project_roots:
        raise ValueError('No project_roots specified in config!')
    
    analyzer = ProjectAnalyzer()
    return analyzer.analyze_and_save(
        project_roots=project_roots,
        output_path=model_output_path,
        project_name=project_name,
        c_file_prefixes=c_file_prefixes,
        recursive=recursive
    )