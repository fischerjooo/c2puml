#!/usr/bin/env python3
"""
PlantUML Generator that creates proper PlantUML diagrams from C source and header files.
Follows the template format with strict separation of typedefs and clear relationship groupings.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional

from .models import FileModel, ProjectModel

# PlantUML generation constants
MAX_LINE_LENGTH = 120  # Maximum line length for PlantUML
TRUNCATION_LENGTH = 100  # Length at which to start truncating function signatures
INDENT = "    "  # Standard indentation for PlantUML content

# PlantUML styling colors
COLOR_SOURCE = "#LightBlue"
COLOR_HEADER = "#LightGreen" 
COLOR_TYPEDEF = "#LightYellow"

# UML prefixes
PREFIX_HEADER = "HEADER_"
PREFIX_TYPEDEF = "TYPEDEF_"


class PlantUMLGenerator:
    """PlantUML generator that creates proper diagrams following the template format.
    
    This class handles the core PlantUML generation logic, including:
    - Building include trees for files
    - Generating UML IDs for all elements
    - Creating PlantUML classes for C files, headers, and typedefs
    - Generating relationships between elements
    """

    def generate_diagram(
        self, file_model: FileModel, project_model: ProjectModel, include_depth: int = 1
    ) -> str:
        """Generate a PlantUML diagram for a file following the template format"""
        basename = Path(file_model.file_path).stem

        # Build include tree for this file
        include_tree = self._build_include_tree(
            file_model, project_model, include_depth
        )

        # Get UML IDs for all elements in the include tree
        uml_ids = self._generate_uml_ids(include_tree, project_model)

        # Generate PlantUML content
        lines = []
        lines.append(f"@startuml {basename}")
        lines.append("")

        # Generate classes for C files in include tree
        for file_path, file_data in sorted(include_tree.items()):
            if file_path.endswith(".c"):
                self._generate_c_file_class(lines, file_data, uml_ids)

        # Generate classes for H files in include tree
        for file_path, file_data in sorted(include_tree.items()):
            if file_path.endswith(".h"):
                self._generate_header_class(lines, file_data, uml_ids)

        # Generate typedef classes
        for file_path, file_data in sorted(include_tree.items()):
            self._generate_typedef_classes(lines, file_data, uml_ids)

        lines.append("")

        # Generate relationships
        self._generate_relationships(lines, include_tree, uml_ids, project_model)

        lines.append("")
        lines.append("@enduml")

        return "\n".join(lines)

    def _build_include_tree(
        self, root_file: FileModel, project_model: ProjectModel, include_depth: int
    ) -> Dict[str, FileModel]:
        """Build include tree starting from root file"""
        include_tree = {}
        visited = set()

        def find_file_key(file_name: str) -> str:
            """Find the correct key for a file in project_model.files using path matching"""
            # First try exact match
            if file_name in project_model.files:
                return file_name
            
            # Try matching by filename
            filename = Path(file_name).name
            if filename in project_model.files:
                return filename
            
            # Try matching by relative path
            for key in project_model.files.keys():
                if Path(key).name == filename:
                    return key
            
            # If not found, return the filename (will be handled gracefully)
            return filename

        def add_file_to_tree(file_name: str, depth: int):
            if depth > include_depth or file_name in visited:
                return

            visited.add(file_name)
            file_key = find_file_key(file_name)
            
            if file_key in project_model.files:
                include_tree[file_key] = project_model.files[file_key]

                # Add included files
                if depth < include_depth:
                    for include in project_model.files[file_key].includes:
                        # Clean the include name (remove quotes/angle brackets)
                        clean_include = include.strip('<>"')
                        add_file_to_tree(clean_include, depth + 1)

        # Start with the root file - find the correct key
        root_key = find_file_key(root_file.relative_path)
        add_file_to_tree(root_key, 0)

        return include_tree

    def _generate_uml_ids(
        self, include_tree: Dict[str, FileModel], project_model: ProjectModel
    ) -> Dict[str, str]:
        """Generate UML IDs for all elements in the include tree using filename-based keys"""
        uml_ids = {}

        for filename, file_model in include_tree.items():
            basename = Path(filename).stem.upper()
            file_key = Path(filename).name  # Use just the filename as key

            if filename.endswith(".c"):
                # C files: no prefix
                uml_ids[file_key] = basename
            elif filename.endswith(".h"):
                # H files: HEADER_ prefix
                uml_ids[file_key] = f"{PREFIX_HEADER}{basename}"

            # Generate typedef UML IDs
            for typedef_name in file_model.structs:
                uml_ids[f"typedef_{typedef_name}"] = f"{PREFIX_TYPEDEF}{typedef_name.upper()}"
            for typedef_name in file_model.enums:
                uml_ids[f"typedef_{typedef_name}"] = f"{PREFIX_TYPEDEF}{typedef_name.upper()}"
            for typedef_name in file_model.aliases:
                uml_ids[f"typedef_{typedef_name}"] = f"{PREFIX_TYPEDEF}{typedef_name.upper()}"
            for typedef_name in file_model.unions:
                uml_ids[f"typedef_{typedef_name}"] = f"{PREFIX_TYPEDEF}{typedef_name.upper()}"

        return uml_ids

    def _format_macro(self, macro: str, prefix: str = "") -> str:
        """Format a macro with the given prefix (+ for headers, - for source)."""
        if "(" in macro and ")" in macro:
            # Function-like macro
            macro_name = macro.split("(")[0].replace("#define ", "")
            params = macro.split("(")[1].split(")")[0]
            return f"{INDENT}{prefix}#define {macro_name}({params})"
        else:
            # Simple macro
            macro_name = macro.replace("#define ", "")
            return f"{INDENT}{prefix}#define {macro_name}"

    def _format_global_variable(self, global_var, prefix: str = "") -> str:
        """Format a global variable with the given prefix."""
        return f"{INDENT}{prefix}{global_var.type} {global_var.name}"

    def _format_function_signature(self, func, prefix: str = "") -> str:
        """Format a function signature with truncation if needed."""
        params = []
        for p in func.parameters:
            if p.name == "..." and p.type == "...":
                params.append("...")
            else:
                params.append(f"{p.type} {p.name}")
        param_str = ", ".join(params)
        
        # Handle long function signatures by truncating if necessary
        full_signature = f"{INDENT}{prefix}{func.return_type} {func.name}({param_str})"
        if len(full_signature) > MAX_LINE_LENGTH:
            # Truncate the signature but keep it readable
            truncated_params = []
            current_length = len(f"{INDENT}{prefix}{func.return_type} {func.name}(")
            for param in params:
                if current_length + len(param) + 2 > TRUNCATION_LENGTH:  # Leave room for closing paren
                    truncated_params.append("...")
                    break
                truncated_params.append(param)
                current_length += len(param) + 2
            param_str = ", ".join(truncated_params)
            return f"{INDENT}{prefix}{func.return_type} {func.name}({param_str})"
        else:
            return full_signature

    def _add_macros_section(self, lines: List[str], file_model: FileModel, prefix: str = ""):
        """Add macros section to lines with given prefix."""
        if file_model.macros:
            lines.append(f"{INDENT}-- Macros --")
            for macro in sorted(file_model.macros):
                lines.append(self._format_macro(macro, prefix))

    def _add_globals_section(self, lines: List[str], file_model: FileModel, prefix: str = ""):
        """Add global variables section to lines with given prefix."""
        if file_model.globals:
            lines.append(f"{INDENT}-- Global Variables --")
            for global_var in sorted(file_model.globals, key=lambda x: x.name):
                lines.append(self._format_global_variable(global_var, prefix))

    def _add_functions_section(self, lines: List[str], file_model: FileModel, 
                              prefix: str = "", is_declaration_only: bool = False):
        """Add functions section to lines with given prefix and filter."""
        if file_model.functions:
            lines.append(f"{INDENT}-- Functions --")
            for func in sorted(file_model.functions, key=lambda x: x.name):
                if is_declaration_only and func.is_declaration:
                    lines.append(self._format_function_signature(func, prefix))
                elif not is_declaration_only and not func.is_declaration:
                    lines.append(self._format_function_signature(func, prefix))

    def _generate_c_file_class(
        self, lines: List[str], file_model: FileModel, uml_ids: Dict[str, str]
    ):
        """Generate class for C file using filename-based keys"""
        basename = Path(file_model.relative_path).stem
        
        # Find the UML ID for this file using filename
        filename = Path(file_model.relative_path).name
        uml_id = uml_ids.get(filename)

        if not uml_id:
            return  # Skip if no UML ID found

        lines.append(f'class "{basename}" as {uml_id} <<source>> {COLOR_SOURCE}')
        lines.append("{")

        # Add sections with source-specific formatting
        self._add_macros_section(lines, file_model, "- ")
        self._add_globals_section(lines, file_model, "")
        self._add_functions_section(lines, file_model, "", is_declaration_only=False)

        lines.append("}")
        lines.append("")

    def _generate_header_class(
        self, lines: List[str], file_model: FileModel, uml_ids: Dict[str, str]
    ):
        """Generate class for header file using filename-based keys"""
        basename = Path(file_model.relative_path).stem
        
        # Find the UML ID for this file using filename
        filename = Path(file_model.relative_path).name
        uml_id = uml_ids.get(filename)

        if not uml_id:
            return  # Skip if no UML ID found

        lines.append(f'class "{basename}" as {uml_id} <<header>> {COLOR_HEADER}')
        lines.append("{")

        # Add sections with header-specific formatting
        self._add_macros_section(lines, file_model, "+ ")
        self._add_globals_section(lines, file_model, "+ ")
        self._add_functions_section(lines, file_model, "+ ", is_declaration_only=True)

        lines.append("}")
        lines.append("")

    def _generate_typedef_classes(
        self, lines: List[str], file_model: FileModel, uml_ids: Dict[str, str]
    ):
        """Generate classes for typedefs"""
        self._generate_struct_classes(lines, file_model, uml_ids)
        self._generate_enum_classes(lines, file_model, uml_ids)
        self._generate_alias_classes(lines, file_model, uml_ids)
        self._generate_union_classes(lines, file_model, uml_ids)

    def _generate_struct_classes(
        self, lines: List[str], file_model: FileModel, uml_ids: Dict[str, str]
    ):
        """Generate classes for struct typedefs"""
        for struct_name, struct_data in sorted(file_model.structs.items()):
            uml_id = uml_ids.get(f"typedef_{struct_name}")
            if uml_id:
                lines.append(
                    f'class "{struct_name}" as {uml_id} <<typedef>> {COLOR_TYPEDEF}'
                )
                lines.append("{")
                for field in sorted(struct_data.fields, key=lambda x: x.name):
                    self._generate_field_with_nested_structs(lines, field, "    ")
                lines.append("}")
                lines.append("")

    def _generate_enum_classes(
        self, lines: List[str], file_model: FileModel, uml_ids: Dict[str, str]
    ):
        """Generate classes for enum typedefs"""
        for enum_name, enum_data in sorted(file_model.enums.items()):
            uml_id = uml_ids.get(f"typedef_{enum_name}")
            if uml_id:
                lines.append(
                    f'class "{enum_name}" as {uml_id} <<typedef>> {COLOR_TYPEDEF}'
                )
                lines.append("{")
                for value in sorted(enum_data.values, key=lambda x: x.name):
                    if value.value:
                        lines.append(f"    + {value.name} = {value.value}")
                    else:
                        lines.append(f"    + {value.name}")
                lines.append("}")
                lines.append("")

    def _generate_alias_classes(
        self, lines: List[str], file_model: FileModel, uml_ids: Dict[str, str]
    ):
        """Generate classes for alias typedefs (simple typedefs)"""
        for alias_name, alias_data in sorted(file_model.aliases.items()):
            uml_id = uml_ids.get(f"typedef_{alias_name}")
            if uml_id:
                lines.append(
                    f'class "{alias_name}" as {uml_id} <<typedef>> {COLOR_TYPEDEF}'
                )
                lines.append("{")
                self._process_alias_content(lines, alias_data)
                lines.append("}")
                lines.append("")

    def _generate_union_classes(
        self, lines: List[str], file_model: FileModel, uml_ids: Dict[str, str]
    ):
        """Generate classes for union typedefs"""
        for union_name, union_data in sorted(file_model.unions.items()):
            uml_id = uml_ids.get(f"typedef_{union_name}")
            if uml_id:
                lines.append(
                    f'class "{union_name}" as {uml_id} <<typedef>> {COLOR_TYPEDEF}'
                )
                lines.append("{")
                for field in sorted(union_data.fields, key=lambda x: x.name):
                    self._generate_field_with_nested_structs(lines, field, "    ")
                lines.append("}")
                lines.append("")

    def _process_alias_content(self, lines: List[str], alias_data):
        """Process the content of an alias typedef with proper formatting"""
        # Handle multi-line alias types with proper nested struct indentation
        alias_lines = alias_data.original_type.split('\n')
        inside_struct = False
        nested_content = []
        
        # Check if this is a truncated typedef (missing closing parenthesis or brace)
        if self._is_truncated_typedef(alias_data, alias_lines):
            self._handle_truncated_typedef(lines, alias_lines)
        else:
            self._handle_normal_alias(lines, alias_lines, inside_struct, nested_content)

    def _is_truncated_typedef(self, alias_data, alias_lines: List[str]) -> bool:
        """Check if this is a truncated typedef"""
        return (
            (alias_data.original_type.strip().endswith('(') or 
             alias_data.original_type.strip().endswith('nested1') or
             alias_data.original_type.strip().endswith('{')) and 
            len(alias_lines) > 1
        )

    def _handle_truncated_typedef(self, lines: List[str], alias_lines: List[str]):
        """Handle truncated function pointer typedef"""
        first_line = alias_lines[0].strip()
        if '(' in first_line and not first_line.endswith(')'):
            # Add ellipsis to indicate truncation
            lines.append(f"    + {first_line}...)")
        else:
            lines.append(f"    + {first_line}")

    def _handle_normal_alias(self, lines: List[str], alias_lines: List[str], 
                           inside_struct: bool, nested_content: List[str]):
        """Handle normal multi-line alias processing"""
        for i, line in enumerate(alias_lines):
            line = line.strip()
            
            if i == 0:
                lines.append(f"    + {line}")
            elif line.startswith("struct {"):
                # Start collecting nested struct content
                inside_struct = True
                nested_content = []
            elif line == "}":
                if inside_struct:
                    # Close nested struct with flattened content
                    if nested_content:
                        content_str = "; ".join(nested_content)
                        lines.append(f"    + struct {{ {content_str} }}")
                    else:
                        lines.append(f"    + struct {{ }}")
                    inside_struct = False
                    nested_content = []
                else:
                    lines.append(f"    }}")
            elif line and line != "}":
                if inside_struct:
                    nested_content.append(line)  # Collect nested content
                else:
                    lines.append(f"+ {line}")
        
        # If we were inside a struct but didn't find a closing brace, add one
        if inside_struct and nested_content:
            content_str = "; ".join(nested_content)
            lines.append(f"    + struct {{ {content_str} }}")

    def _generate_field_with_nested_structs(self, lines: List[str], field, base_indent: str):
        """Generate field with proper handling of nested structures"""
        field_text = f"{field.type} {field.name}"
        
        # Check if this is a nested struct field
        if field.type.startswith("struct {") and '\n' in field.type:
            # Parse the nested struct content and flatten it
            struct_parts = field.type.split('\n')
            
            # For nested structs, flatten them to avoid PlantUML parsing issues
            # Format as: + struct { field_type field_name }
            nested_content = []
            for part in struct_parts[1:]:
                part = part.strip()
                if part and part != "}":
                    nested_content.append(part)
            
            if nested_content:
                # Create a flattened representation
                content_str = "; ".join(nested_content)
                lines.append(f"{base_indent}+ struct {{ {content_str} }} {field.name}")
            else:
                lines.append(f"{base_indent}+ struct {{ }} {field.name}")
        else:
            # Handle regular multi-line field types
            field_lines = field_text.split('\n')
            for i, line in enumerate(field_lines):
                if i == 0:
                    lines.append(f"{base_indent}+ {line}")
                else:
                    lines.append(f"+ {line}")

    def _generate_relationships(
        self,
        lines: List[str],
        include_tree: Dict[str, FileModel],
        uml_ids: Dict[str, str],
        project_model: ProjectModel,
    ):
        """Generate relationships between elements"""
        self._generate_include_relationships(lines, include_tree, uml_ids)
        self._generate_declaration_relationships(lines, include_tree, uml_ids)
        self._generate_uses_relationships(lines, include_tree, uml_ids)

    def _generate_include_relationships(
        self, lines: List[str], include_tree: Dict[str, FileModel], uml_ids: Dict[str, str]
    ):
        """Generate include relationships between files"""
        lines.append("' Include relationships")
        for file_name, file_model in sorted(include_tree.items()):
            file_key = Path(file_name).name
            file_uml_id = uml_ids.get(file_key)
            if file_uml_id:
                for include in sorted(file_model.includes):
                    # Clean the include name (remove quotes/angle brackets)
                    clean_include = include.strip('<>"')
                    
                    # Find the included file's UML ID using filename
                    include_filename = Path(clean_include).name
                    include_uml_id = uml_ids.get(include_filename)
                    
                    # If found, create the relationship
                    if include_uml_id:
                        lines.append(f"{file_uml_id} --> {include_uml_id} : <<include>>")
        lines.append("")

    def _generate_declaration_relationships(
        self, lines: List[str], include_tree: Dict[str, FileModel], uml_ids: Dict[str, str]
    ):
        """Generate declaration relationships between files and typedefs"""
        lines.append("' Declaration relationships")
        for file_name, file_model in sorted(include_tree.items()):
            file_key = Path(file_name).name
            file_uml_id = uml_ids.get(file_key)
            if file_uml_id:
                # Generate declarations for all typedef types
                typedef_collections = [
                    file_model.structs,
                    file_model.enums,
                    file_model.aliases,
                    file_model.unions
                ]
                
                for typedef_collection in typedef_collections:
                    for typedef_name in sorted(typedef_collection.keys()):
                        typedef_uml_id = uml_ids.get(f"typedef_{typedef_name}")
                        if typedef_uml_id:
                            lines.append(f"{file_uml_id} ..> {typedef_uml_id} : <<declares>>")
        lines.append("")

    def _generate_uses_relationships(
        self, lines: List[str], include_tree: Dict[str, FileModel], uml_ids: Dict[str, str]
    ):
        """Generate uses relationships between typedefs"""
        lines.append("' Uses relationships")
        for file_name, file_model in sorted(include_tree.items()):
            # Struct uses relationships
            self._add_typedef_uses_relationships(
                lines, file_model.structs, uml_ids, "struct"
            )
            # Alias uses relationships  
            self._add_typedef_uses_relationships(
                lines, file_model.aliases, uml_ids, "alias"
            )

    def _add_typedef_uses_relationships(
        self, lines: List[str], typedef_collection: Dict, uml_ids: Dict[str, str], typedef_type: str
    ):
        """Add uses relationships for a specific typedef collection"""
        for typedef_name, typedef_data in sorted(typedef_collection.items()):
            typedef_uml_id = uml_ids.get(f"typedef_{typedef_name}")
            if typedef_uml_id and hasattr(typedef_data, "uses"):
                for used_type in sorted(typedef_data.uses):
                    used_uml_id = uml_ids.get(f"typedef_{used_type}")
                    if used_uml_id:
                        lines.append(f"{typedef_uml_id} ..> {used_uml_id} : <<uses>>")


class Generator:
    """Generator that creates proper PlantUML files.
    
    This class provides a facade for the PlantUML generation process, handling:
    - Loading project models from JSON files
    - Creating output directories
    - Orchestrating PlantUML content generation
    - Writing output files to disk
    """

    def generate(
        self, model_file: str, output_dir: str = "./output", include_depth: int = 1
    ) -> str:
        """Generate PlantUML files for all C files in the model"""
        # Load the model
        project_model = self._load_model(model_file)

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Generate a PlantUML file for each C file
        generated_files = []
        generator = PlantUMLGenerator()

        for filename, file_model in sorted(project_model.files.items()):
            # Only process C files (not headers) for diagram generation
            if file_model.relative_path.endswith(".c"):
                # Generate PlantUML content
                puml_content = generator.generate_diagram(
                    file_model, project_model, include_depth
                )

                # Create output filename
                basename = Path(filename).stem
                output_file = os.path.join(output_dir, f"{basename}.puml")

                # Write the file
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(puml_content)

                generated_files.append(output_file)

        return output_dir

    def _load_model(self, model_file: str) -> ProjectModel:
        """Load the project model from JSON file"""
        return ProjectModel.load(model_file)
