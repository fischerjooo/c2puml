#!/usr/bin/env python3
"""
PlantUML diagram generator
"""

import os
import json
from pathlib import Path
from typing import Dict, List
from .models import ProjectModel, FileModel
from .config import Config


class Generator:
    """Generator for PlantUML diagrams"""
    
    def __init__(self):
        pass
    
    def generate_from_model(self, model_file: str, output_dir: str):
        """Generate PlantUML diagrams from a JSON model file"""
        # Load model
        with open(model_file, 'r') as f:
            model_data = json.load(f)
        
        model = ProjectModel.from_dict(model_data)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate diagrams for each file
        for file_path, file_model in model.files.items():
            self._generate_file_diagram(file_model, output_path)
        
        print(f"Generated {len(model.files)} PlantUML diagrams in {output_dir}")
    
    def generate_with_config(self, model: ProjectModel, config: Config):
        """Generate PlantUML diagrams using configuration"""
        # Create output directory
        output_path = Path(config.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate diagrams for each file
        for file_path, file_model in model.files.items():
            self._generate_file_diagram(file_model, output_path)
        
        print(f"Generated {len(model.files)} PlantUML diagrams in {config.output_dir}")
    
    def _generate_file_diagram(self, file_model: FileModel, output_dir: Path):
        """Generate PlantUML diagram for a single file"""
        # Create filename
        base_name = Path(file_model.file_path).stem
        puml_file = output_dir / f"{base_name}.puml"
        
        # Generate PlantUML content
        content = self._generate_plantuml_content(file_model)
        
        # Write file
        with open(puml_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_plantuml_content(self, file_model: FileModel) -> str:
        """Generate PlantUML content for a file"""
        lines = []
        
        # Header
        base_name = Path(file_model.file_path).stem
        lines.append(f"@startuml {base_name}")
        lines.append("")
        
        # Main class
        lines.append(f'class "{base_name}" as {base_name.upper()} <<source>> #LightBlue')
        lines.append("{")
        
        # Add macros
        for macro in file_model.macros:
            lines.append(f"    - #define {macro}")
        
        # Add global variables
        for global_var in file_model.globals:
            lines.append(f"    - {global_var.type} {global_var.name}")
        
        # Add functions
        for func in file_model.functions:
            lines.append(f"    + {func.return_type} {func.name}()")
        
        # Add structs
        for struct_name, struct in file_model.structs.items():
            lines.append(f"    + struct {struct_name}")
            for field in struct.fields:
                lines.append(f"        + {field.type} {field.name}")
        
        # Add enums
        for enum_name, enum in file_model.enums.items():
            lines.append(f"    + enum {enum_name}")
            for value in enum.values:
                lines.append(f"        + {value}")
        
        lines.append("}")
        lines.append("")
        
        # Add typedefs
        for typedef_name, original_type in file_model.typedefs.items():
            lines.append(f'class "{typedef_name}" as {typedef_name.upper()} <<typedef>> #LightYellow')
            lines.append("{")
            lines.append(f"    + {original_type}")
            lines.append("}")
            lines.append("")
        
        # Add relationships
        for include in file_model.includes:
            include_name = Path(include).stem
            lines.append(f'{base_name.upper()} --> {include_name.upper()} : <<include>>')
        
        lines.append("")
        lines.append("@enduml")
        
        return "\n".join(lines)