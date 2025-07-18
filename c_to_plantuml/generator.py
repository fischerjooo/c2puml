#!/usr/bin/env python3
"""
PlantUML diagram generator
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from .models import ProjectModel, FileModel
from .config import Config


class Generator:
    """Generator for PlantUML diagrams"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_from_model(self, model_file: str, output_dir: str) -> None:
        """Generate PlantUML diagrams from a JSON model file"""
        self.logger.info(f"Generating diagrams from model: {model_file}")
        
        # Load model
        try:
            with open(model_file, 'r') as f:
                model_data = json.load(f)
            
            model = ProjectModel.from_dict(model_data)
        except Exception as e:
            raise ValueError(f"Failed to load model file {model_file}: {e}")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate diagrams for each file
        generated_count = 0
        for file_path, file_model in model.files.items():
            try:
                self._generate_file_diagram(file_model, output_path)
                generated_count += 1
            except Exception as e:
                self.logger.error(f"Failed to generate diagram for {file_path}: {e}")
        
        self.logger.info(f"Generated {generated_count} PlantUML diagrams in {output_dir}")
    
    def generate_with_config(self, model: ProjectModel, config: Config) -> None:
        """Generate PlantUML diagrams using configuration"""
        self.logger.info(f"Generating diagrams with config: {config.project_name}")
        
        # Create output directory
        output_path = Path(config.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate diagrams for each file
        generated_count = 0
        for file_path, file_model in model.files.items():
            try:
                self._generate_file_diagram(file_model, output_path)
                generated_count += 1
            except Exception as e:
                self.logger.error(f"Failed to generate diagram for {file_path}: {e}")
        
        self.logger.info(f"Generated {generated_count} PlantUML diagrams in {config.output_dir}")
    
    def _generate_file_diagram(self, file_model: FileModel, output_dir: Path) -> None:
        """Generate PlantUML diagram for a single file"""
        # Create filename
        base_name = Path(file_model.file_path).stem
        puml_file = output_dir / f"{base_name}.puml"
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate PlantUML content
        content = self._generate_plantuml_content(file_model)
        
        # Write file
        try:
            with open(puml_file, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.debug(f"Generated diagram: {puml_file}")
        except Exception as e:
            raise ValueError(f"Failed to write diagram file {puml_file}: {e}")
    
    def _generate_plantuml_content(self, file_model: FileModel) -> str:
        """Generate PlantUML content for a file"""
        lines = []
        base_name = Path(file_model.file_path).stem
        
        # Header
        lines.append(f"@startuml {base_name}")
        lines.append("!theme plain")
        lines.append("skinparam classAttributeIconSize 0")
        lines.append("skinparam classFontSize 12")
        lines.append("skinparam classFontName Arial")
        lines.append("")
        
        # Main class
        lines.append(f'class "{base_name}" as {base_name.upper()} <<source>> #LightBlue')
        lines.append("{")
        
        # Add includes
        if hasattr(file_model, 'includes') and file_model.includes:
            lines.append("    -- Includes --")
            for include in sorted(file_model.includes):
                lines.append(f"    + #include <{include}>")
            lines.append("")
        
        # Add macros
        if hasattr(file_model, 'macros') and file_model.macros:
            lines.append("    -- Macros --")
            for macro in sorted(file_model.macros):
                lines.append(f"    + #define {macro}")
            lines.append("")
        
        # Add typedefs
        if hasattr(file_model, 'typedefs') and file_model.typedefs:
            lines.append("    -- Typedefs --")
            for typedef_name, original_type in sorted(file_model.typedefs.items()):
                lines.append(f"    + typedef {original_type} {typedef_name}")
            lines.append("")
        
        # Add global variables
        if hasattr(file_model, 'globals') and file_model.globals:
            lines.append("    -- Global Variables --")
            for global_var in sorted(file_model.globals, key=lambda x: x.name):
                lines.append(f"    - {global_var.type} {global_var.name}")
            lines.append("")
        
        # Add functions
        if hasattr(file_model, 'functions') and file_model.functions:
            lines.append("    -- Functions --")
            for func in sorted(file_model.functions, key=lambda x: x.name):
                lines.append(f"    + {func.return_type} {func.name}()")
            lines.append("")
        
        # Add structs
        if hasattr(file_model, 'structs') and file_model.structs:
            lines.append("    -- Structs --")
            for struct_name, struct in sorted(file_model.structs.items()):
                lines.append(f"    + struct {struct_name}")
                if hasattr(struct, 'fields') and struct.fields:
                    for field in sorted(struct.fields, key=lambda x: x.name):
                        lines.append(f"        + {field.type} {field.name}")
            lines.append("")
        
        # Add enums
        if hasattr(file_model, 'enums') and file_model.enums:
            lines.append("    -- Enums --")
            for enum_name, enum in sorted(file_model.enums.items()):
                lines.append(f"    + enum {enum_name}")
                if hasattr(enum, 'values') and enum.values:
                    for value in sorted(enum.values):
                        lines.append(f"        + {value}")
        
        lines.append("}")
        lines.append("")
        
        # Add separate typedef classes
        if hasattr(file_model, 'typedefs') and file_model.typedefs:
            for typedef_name, original_type in sorted(file_model.typedefs.items()):
                lines.append(f'class "{typedef_name}" as {typedef_name.upper()} <<typedef>> #LightYellow')
                lines.append("{")
                lines.append(f"    + {original_type}")
                lines.append("}")
                lines.append("")
        
        # Add relationships
        if hasattr(file_model, 'includes') and file_model.includes:
            for include in sorted(file_model.includes):
                include_name = Path(include).stem
                lines.append(f'{base_name.upper()} --> {include_name.upper()} : <<include>>')
        
        lines.append("")
        lines.append("@enduml")
        
        return "\n".join(lines)