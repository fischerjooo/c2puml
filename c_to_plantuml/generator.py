#!/usr/bin/env python3
"""
Simple PlantUML Generator that creates empty PlantUML files for each C file in the model.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from .models import FileModel, ProjectModel


class PlantUMLGenerator:
    """Simple PlantUML generator that creates empty files"""

    def __init__(self):
        pass

    def generate_diagram(
        self, file_model: FileModel, project_model: ProjectModel, include_depth: int = 1
    ) -> str:
        """Generate a simple PlantUML diagram for a file"""
        basename = Path(file_model.file_path).stem
        
        # Create a simple empty PlantUML diagram
        lines = []
        lines.append("@startuml")
        lines.append(f"title {basename}")
        lines.append("")
        lines.append(f"class {basename} {{")
        lines.append("    + File: " + file_model.file_path)
        lines.append("    + Structs: " + str(len(file_model.structs)))
        lines.append("    + Enums: " + str(len(file_model.enums)))
        lines.append("    + Functions: " + str(len(file_model.functions)))
        lines.append("    + Globals: " + str(len(file_model.globals)))
        lines.append("    + Includes: " + str(len(file_model.includes)))
        lines.append("    + Aliases: " + str(len(file_model.aliases)))
        lines.append("    + Unions: " + str(len(file_model.unions)))
        lines.append("}")
        lines.append("")
        lines.append("@enduml")
        
        return "\n".join(lines)


class Generator:
    """Simple generator that creates empty PlantUML files"""

    def __init__(self):
        pass

    def generate(self, model_file: str, output_dir: str = "./output", include_depth: int = 1) -> str:
        """Generate PlantUML files for all C files in the model"""
        # Load the model
        project_model = self._load_model(model_file)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a PlantUML file for each C file
        generated_files = []
        generator = PlantUMLGenerator()
        
        for file_path, file_model in project_model.files.items():
            # Only process C/C++ files
            if file_model.file_path.endswith(('.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.hxx')):
                # Generate PlantUML content
                puml_content = generator.generate_diagram(file_model, project_model, include_depth)
                
                # Create output filename
                basename = Path(file_model.file_path).stem
                output_file = os.path.join(output_dir, f"{basename}.puml")
                
                # Write the file
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(puml_content)
                
                generated_files.append(output_file)
        
        return output_dir

    def _load_model(self, model_file: str) -> ProjectModel:
        """Load the project model from JSON file"""
        return ProjectModel.load(model_file)