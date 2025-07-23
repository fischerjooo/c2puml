#!/usr/bin/env python3
"""
PlantUML Generator that creates proper PlantUML diagrams from C source and header files.
Follows the template format with strict separation of typedefs and clear relationship groupings.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict

from .models import FileModel, ProjectModel


class PlantUMLGenerator:
    """PlantUML generator that creates proper diagrams following the template format"""

    def __init__(self):
        pass

    def generate_diagram(
        self, file_model: FileModel, project_model: ProjectModel, include_depth: int = 1
    ) -> str:
        """Generate a PlantUML diagram for a file following the template format"""
        basename = Path(file_model.file_path).stem
        
        # Build include tree for this file
        include_tree = self._build_include_tree(file_model, project_model, include_depth)
        
        # Get UML IDs for all elements in the include tree
        uml_ids = self._generate_uml_ids(include_tree, project_model)
        
        # Generate PlantUML content
        lines = []
        lines.append(f"@startuml {basename}")
        lines.append("")
        
        # Generate classes for C files in include tree
        for file_path, file_data in include_tree.items():
            if file_path.endswith('.c'):
                self._generate_c_file_class(lines, file_data, uml_ids)
        
        # Generate classes for H files in include tree
        for file_path, file_data in include_tree.items():
            if file_path.endswith('.h'):
                self._generate_header_class(lines, file_data, uml_ids)
        
        # Generate typedef classes
        for file_path, file_data in include_tree.items():
            self._generate_typedef_classes(lines, file_data, uml_ids)
        
        lines.append("")
        
        # Generate relationships
        self._generate_relationships(lines, include_tree, uml_ids, project_model)
        
        lines.append("")
        lines.append("@enduml")
        
        return "\n".join(lines)

    def _build_include_tree(self, root_file: FileModel, project_model: ProjectModel, include_depth: int) -> Dict[str, FileModel]:
        """Build include tree starting from root file"""
        include_tree = {}
        visited = set()
        
        def add_file_to_tree(file_path: str, depth: int):
            if depth > include_depth or file_path in visited:
                return
            
            visited.add(file_path)
            if file_path in project_model.files:
                include_tree[file_path] = project_model.files[file_path]
                
                # Add included files
                if depth < include_depth:
                    for include in project_model.files[file_path].includes:
                        # Find the actual file path for this include
                        include_path = self._find_include_file(include, project_model)
                        if include_path:
                            add_file_to_tree(include_path, depth + 1)
        
        # Start with the root file - use the key that matches the model files
        root_key = Path(root_file.file_path).name
        add_file_to_tree(root_key, 0)
        
        # Also add the root file itself if it's not already in the tree
        if root_key not in include_tree:
            include_tree[root_key] = root_file
        
        return include_tree

    def _find_include_file(self, include_name: str, project_model: ProjectModel) -> Optional[str]:
        """Find the actual file path for an include"""
        # Remove angle brackets and quotes
        clean_include = include_name.strip('<>"')
        
        # Look for exact match first
        for file_path in project_model.files:
            if Path(file_path).name == clean_include:
                return file_path
        
        # Look for header with .h extension
        for file_path in project_model.files:
            if Path(file_path).name == f"{clean_include}.h":
                return file_path
        
        # Look for header without extension if clean_include doesn't have one
        if not clean_include.endswith('.h'):
            for file_path in project_model.files:
                if Path(file_path).name == f"{clean_include}.h":
                    return file_path
        
        # If the model files are stored with just the filename, try direct match
        if clean_include in project_model.files:
            return clean_include
        
        return None

    def _generate_uml_ids(self, include_tree: Dict[str, FileModel], project_model: ProjectModel) -> Dict[str, str]:
        """Generate UML IDs for all elements in the include tree"""
        uml_ids = {}
        
        for file_path, file_model in include_tree.items():
            basename = Path(file_path).stem.upper()
            
            if file_path.endswith('.c'):
                # C files: no prefix
                uml_ids[file_path] = basename
            elif file_path.endswith('.h'):
                # H files: HEADER_ prefix
                uml_ids[file_path] = f"HEADER_{basename}"
            
            # Generate typedef UML IDs
            for typedef_name in file_model.structs:
                uml_ids[f"typedef_{typedef_name}"] = f"TYPEDEF_{typedef_name.upper()}"
            for typedef_name in file_model.enums:
                uml_ids[f"typedef_{typedef_name}"] = f"TYPEDEF_{typedef_name.upper()}"
            for typedef_name in file_model.aliases:
                uml_ids[f"typedef_{typedef_name}"] = f"TYPEDEF_{typedef_name.upper()}"
            for typedef_name in file_model.unions:
                uml_ids[f"typedef_{typedef_name}"] = f"TYPEDEF_{typedef_name.upper()}"
        
        return uml_ids

    def _generate_c_file_class(self, lines: List[str], file_model: FileModel, uml_ids: Dict[str, str]):
        """Generate class for C file"""
        basename = Path(file_model.file_path).stem
        # Find the UML ID for this file by looking for the key that matches this file
        uml_id = None
        for file_key, uml_id_value in uml_ids.items():
            if file_key.endswith('.c') and Path(file_key).stem == basename:
                uml_id = uml_id_value
                break
        
        if not uml_id:
            return  # Skip if no UML ID found
        
        lines.append(f"class \"{basename}\" as {uml_id} <<source>> #LightBlue")
        lines.append("{")
        
        # Add macros
        if file_model.macros:
            lines.append("    -- Macros --")
            for macro in file_model.macros:
                if '(' in macro and ')' in macro:
                    # Function-like macro
                    macro_name = macro.split('(')[0].replace('#define ', '')
                    params = macro.split('(')[1].split(')')[0]
                    lines.append(f"    - #define {macro_name}({params})")
                else:
                    # Simple macro
                    macro_name = macro.replace('#define ', '')
                    lines.append(f"    - #define {macro_name}")
        
        # Add global variables
        if file_model.globals:
            lines.append("    -- Global Variables --")
            for global_var in file_model.globals:
                lines.append(f"    {global_var.type} {global_var.name}")
        
        # Add functions
        if file_model.functions:
            lines.append("    -- Functions --")
            for func in file_model.functions:
                if not func.is_declaration:  # Only implementation, not declarations
                    params = []
                    for p in func.parameters:
                        if p.name == "..." and p.type == "...":
                            params.append("...")
                        else:
                            params.append(f"{p.type} {p.name}")
                    param_str = ", ".join(params)
                    lines.append(f"    {func.return_type} {func.name}({param_str})")
        
        lines.append("}")
        lines.append("")

    def _generate_header_class(self, lines: List[str], file_model: FileModel, uml_ids: Dict[str, str]):
        """Generate class for header file"""
        basename = Path(file_model.file_path).stem
        # Find the UML ID for this file by looking for the key that matches this file
        uml_id = None
        for file_key, uml_id_value in uml_ids.items():
            if file_key.endswith('.h') and Path(file_key).stem == basename:
                uml_id = uml_id_value
                break
        
        if not uml_id:
            return  # Skip if no UML ID found
        
        lines.append(f"class \"{basename}\" as {uml_id} <<header>> #LightGreen")
        lines.append("{")
        
        # Add macros
        if file_model.macros:
            lines.append("    -- Macros --")
            for macro in file_model.macros:
                if '(' in macro and ')' in macro:
                    # Function-like macro
                    macro_name = macro.split('(')[0].replace('#define ', '')
                    params = macro.split('(')[1].split(')')[0]
                    lines.append(f"    + #define {macro_name}({params})")
                else:
                    # Simple macro
                    macro_name = macro.replace('#define ', '')
                    lines.append(f"    + #define {macro_name}")
        
        # Add global variables
        if file_model.globals:
            lines.append("    -- Global Variables --")
            for global_var in file_model.globals:
                lines.append(f"    + {global_var.type} {global_var.name}")
        
        # Add functions (only declarations)
        if file_model.functions:
            lines.append("    -- Functions --")
            for func in file_model.functions:
                if func.is_declaration:  # Only declarations
                    params = []
                    for p in func.parameters:
                        if p.name == "..." and p.type == "...":
                            params.append("...")
                        else:
                            params.append(f"{p.type} {p.name}")
                    param_str = ", ".join(params)
                    lines.append(f"    + {func.return_type} {func.name}({param_str})")
        
        lines.append("}")
        lines.append("")

    def _generate_typedef_classes(self, lines: List[str], file_model: FileModel, uml_ids: Dict[str, str]):
        """Generate classes for typedefs"""
        # Structs
        for struct_name, struct_data in file_model.structs.items():
            uml_id = uml_ids.get(f"typedef_{struct_name}")
            if uml_id:
                lines.append(f"class \"{struct_name}\" as {uml_id} <<typedef>> #LightYellow")
                lines.append("{")
                for field in struct_data.fields:
                    lines.append(f"    + {field.type} {field.name}")
                lines.append("}")
                lines.append("")
        
        # Enums
        for enum_name, enum_data in file_model.enums.items():
            uml_id = uml_ids.get(f"typedef_{enum_name}")
            if uml_id:
                lines.append(f"class \"{enum_name}\" as {uml_id} <<typedef>> #LightYellow")
                lines.append("{")
                for value in enum_data.values:
                    if value.value:
                        lines.append(f"    + {value.name} = {value.value}")
                    else:
                        lines.append(f"    + {value.name}")
                lines.append("}")
                lines.append("")
        
        # Aliases (simple typedefs)
        for alias_name, alias_data in file_model.aliases.items():
            uml_id = uml_ids.get(f"typedef_{alias_name}")
            if uml_id:
                lines.append(f"class \"{alias_name}\" as {uml_id} <<typedef>> #LightYellow")
                lines.append("{")
                lines.append(f"    + {alias_data.original_type}")
                lines.append("}")
                lines.append("")
        
        # Unions
        for union_name, union_data in file_model.unions.items():
            uml_id = uml_ids.get(f"typedef_{union_name}")
            if uml_id:
                lines.append(f"class \"{union_name}\" as {uml_id} <<typedef>> #LightYellow")
                lines.append("{")
                for field in union_data.fields:
                    lines.append(f"    + {field.type} {field.name}")
                lines.append("}")
                lines.append("")

    def _generate_relationships(self, lines: List[str], include_tree: Dict[str, FileModel], uml_ids: Dict[str, str], project_model: ProjectModel):
        """Generate relationships between elements"""
        # 1. Include relationships
        lines.append("' Include relationships")
        for file_path, file_model in include_tree.items():
            file_uml_id = uml_ids.get(file_path)
            if file_uml_id:
                for include in file_model.includes:
                    include_path = self._find_include_file(include, project_model)
                    if include_path and include_path in uml_ids:
                        include_uml_id = uml_ids[include_path]
                        lines.append(f"{file_uml_id} --> {include_uml_id} : <<include>>")
        
        lines.append("")
        
        # 2. Declaration relationships
        lines.append("' Declaration relationships")
        for file_path, file_model in include_tree.items():
            file_uml_id = uml_ids.get(file_path)
            if file_uml_id:
                # Find all typedefs declared in this file
                for typedef_name in file_model.structs:
                    typedef_uml_id = uml_ids.get(f"typedef_{typedef_name}")
                    if typedef_uml_id:
                        lines.append(f"{file_uml_id} ..> {typedef_uml_id} : <<declares>>")
                
                for typedef_name in file_model.enums:
                    typedef_uml_id = uml_ids.get(f"typedef_{typedef_name}")
                    if typedef_uml_id:
                        lines.append(f"{file_uml_id} ..> {typedef_uml_id} : <<declares>>")
                
                for typedef_name in file_model.aliases:
                    typedef_uml_id = uml_ids.get(f"typedef_{typedef_name}")
                    if typedef_uml_id:
                        lines.append(f"{file_uml_id} ..> {typedef_uml_id} : <<declares>>")
                
                for typedef_name in file_model.unions:
                    typedef_uml_id = uml_ids.get(f"typedef_{typedef_name}")
                    if typedef_uml_id:
                        lines.append(f"{file_uml_id} ..> {typedef_uml_id} : <<declares>>")
        
        lines.append("")
        
        # 3. Uses relationships
        lines.append("' Uses relationships")
        for file_path, file_model in include_tree.items():
            # Struct uses relationships
            for struct_name, struct_data in file_model.structs.items():
                struct_uml_id = uml_ids.get(f"typedef_{struct_name}")
                if struct_uml_id and hasattr(struct_data, 'uses'):
                    for used_type in struct_data.uses:
                        used_uml_id = uml_ids.get(f"typedef_{used_type}")
                        if used_uml_id:
                            lines.append(f"{struct_uml_id} ..> {used_uml_id} : <<uses>>")
            
            # Alias uses relationships
            for alias_name, alias_data in file_model.aliases.items():
                alias_uml_id = uml_ids.get(f"typedef_{alias_name}")
                if alias_uml_id and hasattr(alias_data, 'uses'):
                    for used_type in alias_data.uses:
                        used_uml_id = uml_ids.get(f"typedef_{used_type}")
                        if used_uml_id:
                            lines.append(f"{alias_uml_id} ..> {used_uml_id} : <<uses>>")


class Generator:
    """Generator that creates proper PlantUML files"""

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
            # Only process C files (not headers) for diagram generation
            if file_model.file_path.endswith('.c'):
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