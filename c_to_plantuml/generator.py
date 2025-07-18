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
                # Only generate diagrams for .c files, not .h files
                if file_model.relative_path.endswith('.c'):
                    self._generate_file_diagram(file_model, output_path, model)
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
                # Only generate diagrams for .c files, not .h files
                if file_model.relative_path.endswith('.c'):
                    self._generate_file_diagram(file_model, output_path, model)
                    generated_count += 1
            except Exception as e:
                self.logger.error(f"Failed to generate diagram for {file_path}: {e}")
        
        self.logger.info(f"Generated {generated_count} PlantUML diagrams in {config.output_dir}")
    
    def _generate_file_diagram(self, file_model: FileModel, output_dir: Path, model: ProjectModel = None) -> None:
        """Generate PlantUML diagram for a single file"""
        # Create filename using relative path without extension
        relative_path = Path(file_model.relative_path)
        base_name = relative_path.stem
        puml_file = output_dir / f"{base_name}.puml"
        
        # Ensure output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate PlantUML content
        content = self._generate_plantuml_content(file_model, model)
        
        # Write file
        try:
            with open(puml_file, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.debug(f"Generated diagram: {puml_file}")
        except Exception as e:
            raise ValueError(f"Failed to write diagram file {puml_file}: {e}")
    
    def _generate_plantuml_content(self, file_model: FileModel, model: ProjectModel = None) -> str:
        """Generate PlantUML content for a file"""
        lines = []
        base_name = Path(file_model.relative_path).stem
        
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
        
        # Note: Includes are now shown as separate classes with relationships, not in the main class content
        
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
        
        # Add separate typedef classes for struct/enum/union
        if hasattr(file_model, 'typedefs') and file_model.typedefs:
            for typedef_name, original_type in sorted(file_model.typedefs.items()):
                # Struct typedef
                if original_type in file_model.structs:
                    struct = file_model.structs[original_type]
                    lines.append(f'class "{typedef_name}" as {typedef_name.upper()} <<typedef>> #LightYellow')
                    lines.append("{")
                    lines.append(f"    + struct {original_type}")
                    for field in struct.fields:
                        lines.append(f"        + {field.type} {field.name}")
                    lines.append("}")
                    lines.append("")
                # Enum typedef
                elif original_type in file_model.enums:
                    enum = file_model.enums[original_type]
                    lines.append(f'class "{typedef_name}" as {typedef_name.upper()} <<typedef>> #LightYellow')
                    lines.append("{")
                    lines.append(f"    + enum {original_type}")
                    for value in enum.values:
                        lines.append(f"        + {value}")
                    lines.append("}")
                    lines.append("")
                # Union typedef
                elif hasattr(file_model, 'unions') and original_type in file_model.unions:
                    union = file_model.unions[original_type]
                    lines.append(f'class "{typedef_name}" as {typedef_name.upper()} <<typedef>> #LightYellow')
                    lines.append("{")
                    lines.append(f"    + union {original_type}")
                    for field in union.fields:
                        lines.append(f"        + {field.type} {field.name}")
                    lines.append("}")
                    lines.append("")
                else:
                    # Basic or unknown type
                    lines.append(f'class "{typedef_name}" as {typedef_name.upper()} <<typedef>> #LightYellow')
                    lines.append("{")
                    lines.append(f"    + {original_type}")
                    lines.append("}")
                    lines.append("")

        # Add typedef relationships for struct/enum/union
        if hasattr(file_model, 'typedef_relations') and file_model.typedef_relations:
            for relation in sorted(file_model.typedef_relations, key=lambda r: r.typedef_name):
                # Create a class for the original type if it's not a basic type
                if not self._is_basic_type(relation.original_type):
                    # Show struct/enum/union contents if available
                    if relation.original_type in file_model.structs:
                        struct = file_model.structs[relation.original_type]
                        lines.append(f'class "{relation.original_type}" as {relation.original_type.upper()} <<type>> #LightGray')
                        lines.append("{")
                        lines.append(f"    + struct {relation.original_type}")
                        for field in struct.fields:
                            lines.append(f"        + {field.type} {field.name}")
                        lines.append("}")
                        lines.append("")
                    elif relation.original_type in file_model.enums:
                        enum = file_model.enums[relation.original_type]
                        lines.append(f'class "{relation.original_type}" as {relation.original_type.upper()} <<type>> #LightGray')
                        lines.append("{")
                        lines.append(f"    + enum {relation.original_type}")
                        for value in enum.values:
                            lines.append(f"        + {value}")
                        lines.append("}")
                        lines.append("")
                    elif hasattr(file_model, 'unions') and relation.original_type in file_model.unions:
                        union = file_model.unions[relation.original_type]
                        lines.append(f'class "{relation.original_type}" as {relation.original_type.upper()} <<type>> #LightGray')
                        lines.append("{")
                        lines.append(f"    + union {relation.original_type}")
                        for field in union.fields:
                            lines.append(f"        + {field.type} {field.name}")
                        lines.append("}")
                        lines.append("")
                    else:
                        lines.append(f'class "{relation.original_type}" as {relation.original_type.upper()} <<type>> #LightGray')
                        lines.append("{")
                        lines.append(f"    + {relation.original_type}")
                        lines.append("}")
                        lines.append("")
                # Add the relationship
                if relation.relationship_type == 'defines':
                    lines.append(f'{relation.typedef_name.upper()} *-- {relation.original_type.upper()} : «defines»')
                else:  # alias
                    lines.append(f'{relation.typedef_name.upper()} -|> {relation.original_type.upper()} : «alias»')
                lines.append("")
        
        # Add header classes and include relationships
        header_classes_added = set()
        header_models = {}  # Store header file models for content display
        
        # Get all header file models from the project
        if hasattr(file_model, 'project_root') and model is not None:
            project_root = Path(file_model.project_root)
            for file_path, file_model_in_project in model.files.items():
                if file_path.endswith('.h'):
                    header_models[Path(file_path).stem] = file_model_in_project
        
        # Add header classes from simple includes
        if hasattr(file_model, 'includes') and file_model.includes:
            for include in sorted(file_model.includes):
                include_name = Path(include).stem
                if include_name not in header_classes_added:
                    # Create a class for each included header with actual content
                    lines.append(f'class "{include_name}" as {include_name.upper()} <<header>> #LightGreen')
                    lines.append("{")
                    
                    # Show header content if available
                    if include_name in header_models:
                        header_model = header_models[include_name]
                        
                        # Add macros
                        if hasattr(header_model, 'macros') and header_model.macros:
                            lines.append("    -- Macros --")
                            for macro in sorted(header_model.macros):
                                lines.append(f"    + #define {macro}")
                            lines.append("")
                        
                        # Add typedefs
                        if hasattr(header_model, 'typedefs') and header_model.typedefs:
                            lines.append("    -- Typedefs --")
                            for typedef_name, original_type in sorted(header_model.typedefs.items()):
                                lines.append(f"    + typedef {original_type} {typedef_name}")
                            lines.append("")
                        
                        # Add global variables
                        if hasattr(header_model, 'globals') and header_model.globals:
                            lines.append("    -- Global Variables --")
                            for global_var in sorted(header_model.globals, key=lambda x: x.name):
                                lines.append(f"    - {global_var.type} {global_var.name}")
                            lines.append("")
                        
                        # Add functions
                        if hasattr(header_model, 'functions') and header_model.functions:
                            lines.append("    -- Functions --")
                            for func in sorted(header_model.functions, key=lambda x: x.name):
                                lines.append(f"    + {func.return_type} {func.name}()")
                            lines.append("")
                        
                        # Add structs
                        if hasattr(header_model, 'structs') and header_model.structs:
                            lines.append("    -- Structs --")
                            for struct_name, struct in sorted(header_model.structs.items()):
                                lines.append(f"    + struct {struct_name}")
                                if hasattr(struct, 'fields') and struct.fields:
                                    for field in sorted(struct.fields, key=lambda x: x.name):
                                        lines.append(f"        + {field.type} {field.name}")
                            lines.append("")
                        
                        # Add enums
                        if hasattr(header_model, 'enums') and header_model.enums:
                            lines.append("    -- Enums --")
                            for enum_name, enum in sorted(header_model.enums.items()):
                                lines.append(f"    + enum {enum_name}")
                                if hasattr(enum, 'values') and enum.values:
                                    for value in sorted(enum.values):
                                        lines.append(f"        + {value}")
                    else:
                        lines.append("    + Header file")
                    
                    lines.append("}")
                    lines.append("")
                    header_classes_added.add(include_name)
                
                # Add include relationship
                lines.append(f'{base_name.upper()} --> {include_name.upper()} : <<include>>')
                lines.append("")
        
        # Add include relationships with depth information if available
        if hasattr(file_model, 'include_relations') and file_model.include_relations:
            for relation in sorted(file_model.include_relations, key=lambda r: r.included_file):
                included_file_name = Path(relation.included_file).stem
                # Create a class for the included file if it's a header and not already added
                if relation.included_file.endswith('.h') and included_file_name not in header_classes_added:
                    lines.append(f'class "{included_file_name}" as {included_file_name.upper()} <<header>> #LightGreen')
                    lines.append("{")
                    
                    # Show header content if available
                    if included_file_name in header_models:
                        header_model = header_models[included_file_name]
                        
                        # Add macros
                        if hasattr(header_model, 'macros') and header_model.macros:
                            lines.append("    -- Macros --")
                            for macro in sorted(header_model.macros):
                                lines.append(f"    + #define {macro}")
                            lines.append("")
                        
                        # Add typedefs
                        if hasattr(header_model, 'typedefs') and header_model.typedefs:
                            lines.append("    -- Typedefs --")
                            for typedef_name, original_type in sorted(header_model.typedefs.items()):
                                lines.append(f"    + typedef {original_type} {typedef_name}")
                            lines.append("")
                        
                        # Add global variables
                        if hasattr(header_model, 'globals') and header_model.globals:
                            lines.append("    -- Global Variables --")
                            for global_var in sorted(header_model.globals, key=lambda x: x.name):
                                lines.append(f"    - {global_var.type} {global_var.name}")
                            lines.append("")
                        
                        # Add functions
                        if hasattr(header_model, 'functions') and header_model.functions:
                            lines.append("    -- Functions --")
                            for func in sorted(header_model.functions, key=lambda x: x.name):
                                lines.append(f"    + {func.return_type} {func.name}()")
                            lines.append("")
                        
                        # Add structs
                        if hasattr(header_model, 'structs') and header_model.structs:
                            lines.append("    -- Structs --")
                            for struct_name, struct in sorted(header_model.structs.items()):
                                lines.append(f"    + struct {struct_name}")
                                if hasattr(struct, 'fields') and struct.fields:
                                    for field in sorted(struct.fields, key=lambda x: x.name):
                                        lines.append(f"        + {field.type} {field.name}")
                            lines.append("")
                        
                        # Add enums
                        if hasattr(header_model, 'enums') and header_model.enums:
                            lines.append("    -- Enums --")
                            for enum_name, enum in sorted(header_model.enums.items()):
                                lines.append(f"    + enum {enum_name}")
                                if hasattr(enum, 'values') and enum.values:
                                    for value in sorted(enum.values):
                                        lines.append(f"        + {value}")
                    else:
                        lines.append("    + Header file")
                    
                    lines.append("}")
                    lines.append("")
                    header_classes_added.add(included_file_name)
                
                lines.append(f'{base_name.upper()} --> {included_file_name.upper()} : <<include>> (depth {relation.depth})')
                lines.append("")
        
        # Add relationships between header files
        if hasattr(file_model, 'include_relations') and file_model.include_relations:
            for relation in sorted(file_model.include_relations, key=lambda r: r.included_file):
                if relation.included_file.endswith('.h'):
                    included_file_name = Path(relation.included_file).stem
                    
                    # Check if the included header has its own includes
                    if included_file_name in header_models:
                        header_model = header_models[included_file_name]
                        if hasattr(header_model, 'includes') and header_model.includes:
                            for header_include in sorted(header_model.includes):
                                header_include_name = Path(header_include).stem
                                if header_include_name in header_classes_added:
                                    lines.append(f'{included_file_name.upper()} --> {header_include_name.upper()} : <<include>>')
                                    lines.append("")
        
        lines.append("")
        lines.append("@enduml")
        
        return "\n".join(lines)
    
    def _is_basic_type(self, type_name: str) -> bool:
        """Check if a type is a basic C type"""
        basic_types = {
            'int', 'char', 'float', 'double', 'void', 'long', 'short',
            'unsigned', 'signed', 'const', 'volatile', 'uint32_t', 'uint16_t',
            'uint8_t', 'int32_t', 'int16_t', 'int8_t', 'size_t', 'ssize_t'
        }
        
        # Handle pointer types
        if '*' in type_name:
            base_type = type_name.replace('*', '').strip()
            return base_type in basic_types
        
        return type_name in basic_types