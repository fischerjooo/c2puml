#!/usr/bin/env python3
"""
PlantUML Generator - Creates PlantUML diagrams from C source and header files.
Clean, simple implementation following single responsibility principle.
"""

import os
from pathlib import Path
from typing import Dict, List, Set

from .models import FileModel, ProjectModel


class Generator:
    """Clean PlantUML generator with focused responsibilities"""

    def __init__(self):
        self.uml_ids: Dict[str, str] = {}

    def generate(
        self, model_file: str, output_dir: str = "./output", include_depth: int = 1
    ) -> str:
        """Generate PlantUML files for all C files in the model"""
        project_model = ProjectModel.load(model_file)
        os.makedirs(output_dir, exist_ok=True)

        generated_files = []
        for filename, file_model in sorted(project_model.files.items()):
            if file_model.relative_path.endswith(".c"):
                puml_content = self._generate_diagram(file_model, project_model, include_depth)
                output_file = os.path.join(output_dir, f"{Path(filename).stem}.puml")
                
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(puml_content)
                generated_files.append(output_file)

        return output_dir

    def _generate_diagram(
        self, root_file: FileModel, project_model: ProjectModel, include_depth: int
    ) -> str:
        """Generate a complete PlantUML diagram for a file"""
        include_tree = self._build_include_tree(root_file, project_model, include_depth)
        self._generate_uml_ids(include_tree)
        
        lines = [
            f"@startuml {Path(root_file.file_path).stem}",
            "",
            *self._generate_classes(include_tree),
            "",
            *self._generate_relationships(include_tree, project_model),
            "",
            "@enduml"
        ]
        
        return "\n".join(lines)

    def _build_include_tree(
        self, root_file: FileModel, project_model: ProjectModel, include_depth: int
    ) -> Dict[str, FileModel]:
        """Build include tree starting from root file"""
        include_tree = {}
        visited = set()

        def add_file_to_tree(file_name: str, depth: int):
            if depth > include_depth or file_name in visited:
                return

            visited.add(file_name)
            file_key = self._find_file_key(file_name, project_model)
            
            if file_key in project_model.files:
                include_tree[file_key] = project_model.files[file_key]
                
                if depth < include_depth:
                    for include in project_model.files[file_key].includes:
                        clean_include = include.strip('<>"')
                        add_file_to_tree(clean_include, depth + 1)

        root_key = self._find_file_key(root_file.relative_path, project_model)
        add_file_to_tree(root_key, 0)
        return include_tree

    def _find_file_key(self, file_name: str, project_model: ProjectModel) -> str:
        """Find the correct key for a file in project_model.files"""
        if file_name in project_model.files:
            return file_name
        
        filename = Path(file_name).name
        if filename in project_model.files:
            return filename
        
        for key in project_model.files.keys():
            if Path(key).name == filename:
                return key
        
        return filename

    def _generate_uml_ids(self, include_tree: Dict[str, FileModel]) -> None:
        """Generate UML IDs for all elements in the include tree"""
        self.uml_ids.clear()
        
        for filename, file_model in include_tree.items():
            basename = Path(filename).stem.upper()
            file_key = Path(filename).name

            # File UML IDs
            if filename.endswith(".c"):
                self.uml_ids[file_key] = basename
            elif filename.endswith(".h"):
                self.uml_ids[file_key] = f"HEADER_{basename}"

            # Typedef UML IDs
            for typedef_name in self._get_all_typedefs(file_model):
                self.uml_ids[f"typedef_{typedef_name}"] = f"TYPEDEF_{typedef_name.upper()}"

    def _get_all_typedefs(self, file_model: FileModel) -> Set[str]:
        """Get all typedef names from a file model"""
        typedefs = set()
        typedefs.update(file_model.structs.keys())
        typedefs.update(file_model.enums.keys())
        typedefs.update(file_model.aliases.keys())
        typedefs.update(file_model.unions.keys())
        return typedefs

    def _generate_classes(self, include_tree: Dict[str, FileModel]) -> List[str]:
        """Generate all class definitions"""
        lines = []
        
        # C files first
        for file_path, file_data in sorted(include_tree.items()):
            if file_path.endswith(".c"):
                lines.extend(self._generate_c_file_class(file_data))
        
        # Header files
        for file_path, file_data in sorted(include_tree.items()):
            if file_path.endswith(".h"):
                lines.extend(self._generate_header_class(file_data))
        
        # Typedef classes
        for file_path, file_data in sorted(include_tree.items()):
            lines.extend(self._generate_typedef_classes(file_data))
        
        return lines

    def _generate_c_file_class(self, file_model: FileModel) -> List[str]:
        """Generate class for C file"""
        filename = Path(file_model.relative_path).name
        uml_id = self.uml_ids.get(filename)
        if not uml_id:
            return []

        basename = Path(file_model.relative_path).stem
        lines = [f'class "{basename}" as {uml_id} <<source>> #LightBlue', "{"]

        # Add sections
        if file_model.macros:
            lines.extend(self._generate_macros_section(file_model.macros))
        
        if file_model.globals:
            lines.extend(self._generate_globals_section(file_model.globals))
        
        if file_model.functions:
            lines.extend(self._generate_functions_section(file_model.functions))

        lines.append("}")
        return lines

    def _generate_header_class(self, file_model: FileModel) -> List[str]:
        """Generate class for header file"""
        filename = Path(file_model.relative_path).name
        uml_id = self.uml_ids.get(filename)
        if not uml_id:
            return []

        basename = Path(file_model.relative_path).stem
        lines = [f'class "{basename}" as {uml_id} <<header>> #LightGreen', "{"]

        # Add sections
        if file_model.macros:
            lines.extend(self._generate_macros_section(file_model.macros))
        
        if file_model.functions:
            lines.extend(self._generate_functions_section(file_model.functions))

        lines.append("}")
        return lines

    def _generate_typedef_classes(self, file_model: FileModel) -> List[str]:
        """Generate typedef classes"""
        lines = []
        
        for typedef_name in self._get_all_typedefs(file_model):
            typedef_uml_id = self.uml_ids.get(f"typedef_{typedef_name}")
            if not typedef_uml_id:
                continue

            lines.append(f'class "{typedef_name}" as {typedef_uml_id} <<typedef>> #LightYellow')
            lines.append("{")
            
            # Add typedef content based on type
            if typedef_name in file_model.structs:
                lines.extend(self._generate_struct_fields(file_model.structs[typedef_name]))
            elif typedef_name in file_model.enums:
                lines.extend(self._generate_enum_values(file_model.enums[typedef_name]))
            elif typedef_name in file_model.unions:
                lines.extend(self._generate_union_fields(file_model.unions[typedef_name]))
            elif typedef_name in file_model.aliases:
                lines.extend(self._generate_alias_definition(file_model.aliases[typedef_name]))
            
            lines.append("}")
        
        return lines

    def _generate_macros_section(self, macros: List[str]) -> List[str]:
        """Generate macros section"""
        lines = ["    -- Macros --"]
        for macro in sorted(macros):
            if "(" in macro and ")" in macro:
                macro_name = macro.split("(")[0].replace("#define ", "")
                params = macro.split("(")[1].split(")")[0]
                lines.append(f"    - #define {macro_name}({params})")
            else:
                macro_name = macro.replace("#define ", "")
                lines.append(f"    - #define {macro_name}")
        return lines

    def _generate_globals_section(self, globals_list: List) -> List[str]:
        """Generate global variables section"""
        lines = ["    -- Global Variables --"]
        for global_var in sorted(globals_list, key=lambda x: x.name):
            lines.append(f"    {global_var.type} {global_var.name}")
        return lines

    def _generate_functions_section(self, functions: List) -> List[str]:
        """Generate functions section"""
        lines = ["    -- Functions --"]
        for func in sorted(functions, key=lambda x: x.name):
            if not func.is_declaration:
                signature = self._format_function_signature(func)
                lines.append(f"    {signature}")
        return lines

    def _format_function_signature(self, func) -> str:
        """Format function signature with parameter truncation if needed"""
        params = []
        for p in func.parameters:
            if p.name == "..." and p.type == "...":
                params.append("...")
            else:
                params.append(f"{p.type} {p.name}")
        
        param_str = ", ".join(params)
        signature = f"{func.return_type} {func.name}({param_str})"
        
        if len(signature) > 120:
            # Truncate parameters if too long
            truncated_params = []
            current_length = len(f"{func.return_type} {func.name}(")
            for param in params:
                if current_length + len(param) + 2 > 100:
                    truncated_params.append("...")
                    break
                truncated_params.append(param)
                current_length += len(param) + 2
            
            param_str = ", ".join(truncated_params)
            signature = f"{func.return_type} {func.name}({param_str})"
        
        return signature

    def _generate_struct_fields(self, struct_data) -> List[str]:
        """Generate struct fields"""
        lines = []
        for field in struct_data.fields:
            field_line = f"    {field.type} {field.name}"
            if hasattr(field, 'array_size') and field.array_size:
                field_line += f"[{field.array_size}]"
            lines.append(field_line)
        return lines

    def _generate_enum_values(self, enum_data) -> List[str]:
        """Generate enum values"""
        lines = []
        for value in enum_data.values:
            if hasattr(value, 'value') and value.value is not None:
                lines.append(f"    {value.name} = {value.value}")
            else:
                lines.append(f"    {value.name}")
        return lines

    def _generate_union_fields(self, union_data) -> List[str]:
        """Generate union fields"""
        lines = []
        for field in union_data.fields:
            field_line = f"    {field.type} {field.name}"
            if hasattr(field, 'array_size') and field.array_size:
                field_line += f"[{field.array_size}]"
            lines.append(field_line)
        return lines

    def _generate_alias_definition(self, alias_data) -> List[str]:
        """Generate alias definition"""
        return [f"    {alias_data.type}"]

    def _generate_relationships(self, include_tree: Dict[str, FileModel], project_model: ProjectModel) -> List[str]:
        """Generate all relationships"""
        lines = []
        
        # Include relationships
        lines.append("' Include relationships")
        for file_name, file_model in sorted(include_tree.items()):
            file_uml_id = self.uml_ids.get(Path(file_name).name)
            if file_uml_id:
                for include in sorted(file_model.includes):
                    include_clean = include.strip('<>"')
                    include_uml_id = self.uml_ids.get(Path(include_clean).name)
                    if include_uml_id:
                        lines.append(f"{file_uml_id} ..> {include_uml_id} : <<includes>>")

        lines.append("")

        # Declares relationships
        lines.append("' Declares relationships")
        for file_name, file_model in sorted(include_tree.items()):
            file_uml_id = self.uml_ids.get(Path(file_name).name)
            if file_uml_id:
                for typedef_name in sorted(self._get_all_typedefs(file_model)):
                    typedef_uml_id = self.uml_ids.get(f"typedef_{typedef_name}")
                    if typedef_uml_id:
                        lines.append(f"{file_uml_id} ..> {typedef_uml_id} : <<declares>>")

        lines.append("")

        # Uses relationships
        lines.append("' Uses relationships")
        for file_name, file_model in sorted(include_tree.items()):
            for typedef_name in self._get_all_typedefs(file_model):
                typedef_uml_id = self.uml_ids.get(f"typedef_{typedef_name}")
                if typedef_uml_id:
                    typedef_data = self._get_typedef_data(file_model, typedef_name)
                    if hasattr(typedef_data, "uses"):
                        for used_type in sorted(typedef_data.uses):
                            used_uml_id = self.uml_ids.get(f"typedef_{used_type}")
                            if used_uml_id:
                                lines.append(f"{typedef_uml_id} ..> {used_uml_id} : <<uses>>")

        return lines

    def _get_typedef_data(self, file_model: FileModel, typedef_name: str):
        """Get typedef data from file model"""
        if typedef_name in file_model.structs:
            return file_model.structs[typedef_name]
        elif typedef_name in file_model.enums:
            return file_model.enums[typedef_name]
        elif typedef_name in file_model.aliases:
            return file_model.aliases[typedef_name]
        elif typedef_name in file_model.unions:
            return file_model.unions[typedef_name]
        return None
