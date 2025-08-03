#!/usr/bin/env python3
"""
PlantUML Generator that creates proper PlantUML diagrams from C source and header files.
Follows the template format with strict separation of typedefs and clear relationship groupings.
"""

import glob
import os
from pathlib import Path
from typing import Dict, List, Optional

from ..models import Field, FileModel, Function, ProjectModel

# PlantUML generation constants
MAX_LINE_LENGTH = 120
TRUNCATION_LENGTH = 100
INDENT = "    "

# PlantUML styling colors
COLOR_SOURCE = "#LightBlue"
COLOR_HEADER = "#LightGreen"
COLOR_TYPEDEF = "#LightYellow"

# UML prefixes
PREFIX_HEADER = "HEADER_"
PREFIX_TYPEDEF = "TYPEDEF_"


class Generator:
    """Generator that creates proper PlantUML files.

    This class handles the complete PlantUML generation process, including:
    - Loading project models from JSON files
    - Building include trees for files
    - Generating UML IDs for all elements
    - Creating PlantUML classes for C files, headers, and typedefs
    - Generating relationships between elements
    - Writing output files to disk
    """

    def _clear_output_folder(self, output_dir: str) -> None:
        """Clear existing .puml and .png files from the output directory"""
        if not os.path.exists(output_dir):
            return

        # Remove files with specified extensions in the output directory
        for ext in ("*.puml", "*.png", "*.html"):
            for file_path in glob.glob(os.path.join(output_dir, ext)):
                try:
                    os.remove(file_path)
                except OSError:
                    pass  # Ignore errors if file can't be removed

    def generate(
        self, model_file: str, output_dir: str = "./output", include_depth: int = None
    ) -> str:
        """Generate PlantUML files for all C files in the model"""
        # Load the model
        project_model = self._load_model(model_file)

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Clear existing .puml and .png files from output directory
        self._clear_output_folder(output_dir)

        # Generate a PlantUML file for each C file
        generated_files = []

        for filename, file_model in sorted(project_model.files.items()):
            # Only process C files (not headers) for diagram generation
            if file_model.name.endswith(".c"):
                # Generate PlantUML content
                # include_depth is handled by the transformer which processes
                # file-specific settings and stores them in include_relations
                puml_content = self.generate_diagram(
                    file_model, project_model, include_depth=1
                )

                # Create output filename
                basename = Path(file_model.name).stem
                output_file = os.path.join(output_dir, f"{basename}.puml")

                # Write the file
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(puml_content)

                generated_files.append(output_file)

        return output_dir

    def generate_diagram(
        self, file_model: FileModel, project_model: ProjectModel, include_depth: int = 1
    ) -> str:
        """Generate a PlantUML diagram for a file following the template format"""
        basename = Path(file_model.name).stem
        include_tree = self._build_include_tree(
            file_model, project_model, include_depth
        )
        uml_ids = self._generate_uml_ids(include_tree, project_model)

        lines = [f"@startuml {basename}", ""]

        self._generate_all_file_classes(lines, include_tree, uml_ids, project_model)
        self._generate_relationships(lines, include_tree, uml_ids, project_model)

        lines.extend(["", "@enduml"])
        return "\n".join(lines)

    def _generate_all_file_classes(
        self,
        lines: List[str],
        include_tree: Dict[str, FileModel],
        uml_ids: Dict[str, str],
        project_model: ProjectModel,
    ):
        """Generate all file classes (C files, headers, and typedefs)"""
        self._generate_file_classes_by_extension(
            lines, include_tree, uml_ids, project_model, ".c", self._generate_c_file_class
        )
        self._generate_file_classes_by_extension(
            lines, include_tree, uml_ids, project_model, ".h", self._generate_header_class
        )
        self._generate_typedef_classes_for_all_files(lines, include_tree, uml_ids)

    def _generate_file_classes_by_extension(
        self,
        lines: List[str],
        include_tree: Dict[str, FileModel],
        uml_ids: Dict[str, str],
        project_model: ProjectModel,
        extension: str,
        generator_method,
    ):
        """Generate file classes for files with specific extension"""
        for file_path, file_data in sorted(include_tree.items()):
            if file_path.endswith(extension):
                generator_method(lines, file_data, uml_ids, project_model)

    def _generate_typedef_classes_for_all_files(
        self,
        lines: List[str],
        include_tree: Dict[str, FileModel],
        uml_ids: Dict[str, str],
    ):
        """Generate typedef classes for all files in include tree"""
        for file_path, file_data in sorted(include_tree.items()):
            self._generate_typedef_classes(lines, file_data, uml_ids)
        lines.append("")

    def _load_model(self, model_file: str) -> ProjectModel:
        """Load the project model from JSON file"""
        return ProjectModel.load(model_file)

    def _build_include_tree(
        self, root_file: FileModel, project_model: ProjectModel, include_depth: int
    ) -> Dict[str, FileModel]:
        """Build include tree starting from root file"""
        include_tree = {}

        def find_file_key(file_name: str) -> str:
            """Find the correct key for a file in project_model.files using filename matching"""
            # First try exact match
            if file_name in project_model.files:
                return file_name

            # Try matching by filename (filenames are guaranteed to be unique)
            filename = Path(file_name).name
            if filename in project_model.files:
                return filename

            # If not found, return the filename (will be handled gracefully)
            return filename

        # Start with the root file
        root_key = find_file_key(root_file.name)
        if root_key in project_model.files:
            include_tree[root_key] = project_model.files[root_key]

        # If root file has include_relations, use only those files (flat processing)
        if root_file.include_relations:
            # include_relations is already a flattened list of all headers needed
            included_files = set()
            for relation in root_file.include_relations:
                included_files.add(relation.included_file)
            
            # Add all files mentioned in include_relations
            for included_file in included_files:
                file_key = find_file_key(included_file)
                if file_key in project_model.files:
                    include_tree[file_key] = project_model.files[file_key]
        else:
            # Fall back to recursive traversal using includes field (backward compatibility)
            visited = set()

            def add_file_to_tree(file_name: str, depth: int):
                if depth > include_depth or file_name in visited:
                    return

                visited.add(file_name)
                file_key = find_file_key(file_name)

                if file_key in project_model.files:
                    include_tree[file_key] = project_model.files[file_key]

                    # Add included files recursively
                    if depth < include_depth:
                        file_model = project_model.files[file_key]
                        for include in file_model.includes:
                            # Clean the include name (remove quotes/angle brackets)
                            clean_include = include.strip('<>"')
                            add_file_to_tree(clean_include, depth + 1)

            # Start recursive traversal from root (already added above)
            if root_key in project_model.files:
                root_file_model = project_model.files[root_key]
                for include in root_file_model.includes:
                    clean_include = include.strip('<>"')
                    add_file_to_tree(clean_include, 1)

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
                uml_ids[f"typedef_{typedef_name}"] = (
                    f"{PREFIX_TYPEDEF}{typedef_name.upper()}"
                )
            for typedef_name in file_model.enums:
                uml_ids[f"typedef_{typedef_name}"] = (
                    f"{PREFIX_TYPEDEF}{typedef_name.upper()}"
                )
            for typedef_name in file_model.aliases:
                uml_ids[f"typedef_{typedef_name}"] = (
                    f"{PREFIX_TYPEDEF}{typedef_name.upper()}"
                )
            for typedef_name in file_model.unions:
                uml_ids[f"typedef_{typedef_name}"] = (
                    f"{PREFIX_TYPEDEF}{typedef_name.upper()}"
                )

        return uml_ids

    def _format_macro(self, macro: str, prefix: str = "") -> str:
        """Format a macro with the given prefix (+ for headers, - for source)."""
        if "(" in macro and ")" in macro:
            # Function-like macro
            macro_name = macro.split("(")[0].replace("#define ", "")
            params = macro.split("(")[1].split(")")[0]
            return f"{INDENT}{prefix}#define {macro_name}({params})"
        else:
            # Basic macro
            macro_name = macro.replace("#define ", "")
            return f"{INDENT}{prefix}#define {macro_name}"

    def _format_global_variable(self, global_var, prefix: str = "") -> str:
        """Format a global variable with the given prefix."""
        return f"{INDENT}{prefix}{global_var.type} {global_var.name}"

    def _format_function_signature(self, func, prefix: str = "") -> str:
        """Format a function signature with truncation if needed."""
        params = self._format_function_parameters(func.parameters)
        param_str = ", ".join(params)

        # Remove 'extern' keyword from return type for UML diagrams
        return_type = func.return_type.replace("extern ", "").strip()

        full_signature = f"{INDENT}{prefix}{return_type} {func.name}({param_str})"
        if len(full_signature) > MAX_LINE_LENGTH:
            param_str = self._truncate_parameters(params, func, prefix)
            return f"{INDENT}{prefix}{return_type} {func.name}({param_str})"
        return full_signature

    def _format_function_parameters(self, parameters) -> List[str]:
        """Format function parameters into string list."""
        params = []
        for p in parameters:
            if p.name == "..." and p.type == "...":
                params.append("...")
            else:
                params.append(f"{p.type} {p.name}")
        return params

    def _truncate_parameters(self, params: List[str], func, prefix: str) -> str:
        """Truncate parameters list if signature is too long."""
        truncated_params = []
        current_length = len(f"{INDENT}{prefix}{func.return_type} {func.name}(")
        for param in params:
            if current_length + len(param) + 2 > TRUNCATION_LENGTH:
                truncated_params.append("...")
                break
            truncated_params.append(param)
            current_length += len(param) + 2
        return ", ".join(truncated_params)

    def _add_macros_section(
        self, lines: List[str], file_model: FileModel, prefix: str = ""
    ):
        """Add macros section to lines with given prefix."""
        if file_model.macros:
            lines.append(f"{INDENT}-- Macros --")
            for macro in sorted(file_model.macros):
                lines.append(self._format_macro(macro, prefix))

    def _add_globals_section(
        self, lines: List[str], file_model: FileModel, prefix: str = ""
    ):
        """Add global variables section to lines with given prefix."""
        if file_model.globals:
            lines.append(f"{INDENT}-- Global Variables --")
            for global_var in sorted(file_model.globals, key=lambda x: x.name):
                lines.append(self._format_global_variable(global_var, prefix))

    def _add_functions_section(
        self,
        lines: List[str],
        file_model: FileModel,
        prefix: str = "",
        is_declaration_only: bool = False,
    ):
        """Add functions section to lines with given prefix and filter."""
        if file_model.functions:
            lines.append(f"{INDENT}-- Functions --")
            for func in sorted(file_model.functions, key=lambda x: x.name):
                if is_declaration_only and func.is_declaration:
                    lines.append(self._format_function_signature(func, prefix))
                elif not is_declaration_only and not func.is_declaration:
                    lines.append(self._format_function_signature(func, prefix))

    def _generate_c_file_class(
        self, lines: List[str], file_model: FileModel, uml_ids: Dict[str, str], project_model: ProjectModel
    ):
        """Generate class for C file using filename-based keys"""
        self._generate_file_class_with_visibility(
            lines,
            file_model,
            uml_ids,
            project_model,
            class_type="source",
            color=COLOR_SOURCE,
            macro_prefix="- ",
            is_declaration_only=False,
        )

    def _generate_header_class(
        self, lines: List[str], file_model: FileModel, uml_ids: Dict[str, str], project_model: ProjectModel
    ):
        """Generate class for header file using filename-based keys"""
        self._generate_file_class(
            lines,
            file_model,
            uml_ids,
            class_type="header",
            color=COLOR_HEADER,
            macro_prefix="+ ",
            global_prefix="+ ",
            function_prefix="+ ",
            is_declaration_only=True,
        )

    def _generate_file_class_with_visibility(
        self,
        lines: List[str],
        file_model: FileModel,
        uml_ids: Dict[str, str],
        project_model: ProjectModel,
        class_type: str,
        color: str,
        macro_prefix: str,
        is_declaration_only: bool,
    ):
        """Generate class for source file with dynamic visibility based on header presence"""
        basename = Path(file_model.name).stem
        filename = Path(file_model.name).name
        uml_id = uml_ids.get(filename)

        if not uml_id:
            return

        lines.append(f'class "{basename}" as {uml_id} <<{class_type}>> {color}')
        lines.append("{")

        self._add_macros_section(lines, file_model, macro_prefix)
        self._add_globals_section_with_visibility(lines, file_model, project_model)
        self._add_functions_section_with_visibility(lines, file_model, project_model, is_declaration_only)

        lines.append("}")
        lines.append("")

    def _generate_file_class(
        self,
        lines: List[str],
        file_model: FileModel,
        uml_ids: Dict[str, str],
        class_type: str,
        color: str,
        macro_prefix: str,
        global_prefix: str,
        function_prefix: str,
        is_declaration_only: bool,
    ):
        """Generate class for a file with specified formatting"""
        basename = Path(file_model.name).stem
        filename = Path(file_model.name).name
        uml_id = uml_ids.get(filename)

        if not uml_id:
            return

        lines.append(f'class "{basename}" as {uml_id} <<{class_type}>> {color}')
        lines.append("{")

        self._add_macros_section(lines, file_model, macro_prefix)
        self._add_globals_section(lines, file_model, global_prefix)
        self._add_functions_section(
            lines, file_model, function_prefix, is_declaration_only
        )

        lines.append("}")
        lines.append("")

    def _add_globals_section_with_visibility(
        self, lines: List[str], file_model: FileModel, project_model: ProjectModel
    ):
        """Add global variables section with visibility based on header presence, grouped by visibility"""
        if file_model.globals:
            lines.append(f"{INDENT}-- Global Variables --")
            
            # Separate globals into public and private groups
            public_globals = []
            private_globals = []
            
            for global_var in sorted(file_model.globals, key=lambda x: x.name):
                prefix = self._get_visibility_prefix_for_global(global_var, project_model)
                formatted_global = self._format_global_variable(global_var, prefix)
                
                if prefix == "+ ":
                    public_globals.append(formatted_global)
                else:
                    private_globals.append(formatted_global)
            
            # Add public globals first
            for global_line in public_globals:
                lines.append(global_line)
            
            # Add empty line between public and private if both exist
            if public_globals and private_globals:
                lines.append("")
            
            # Add private globals
            for global_line in private_globals:
                lines.append(global_line)

    def _add_functions_section_with_visibility(
        self,
        lines: List[str],
        file_model: FileModel,
        project_model: ProjectModel,
        is_declaration_only: bool = False,
    ):
        """Add functions section with visibility based on header presence, grouped by visibility"""
        if file_model.functions:
            lines.append(f"{INDENT}-- Functions --")
            
            # Separate functions into public and private groups
            public_functions = []
            private_functions = []
            
            for func in sorted(file_model.functions, key=lambda x: x.name):
                if is_declaration_only and func.is_declaration:
                    prefix = "+ "
                    formatted_function = self._format_function_signature(func, prefix)
                    public_functions.append(formatted_function)
                elif not is_declaration_only and not func.is_declaration:
                    prefix = self._get_visibility_prefix_for_function(func, project_model)
                    formatted_function = self._format_function_signature(func, prefix)
                    
                    if prefix == "+ ":
                        public_functions.append(formatted_function)
                    else:
                        private_functions.append(formatted_function)
            
            # Add public functions first
            for function_line in public_functions:
                lines.append(function_line)
            
            # Add empty line between public and private if both exist
            if public_functions and private_functions:
                lines.append("")
            
            # Add private functions
            for function_line in private_functions:
                lines.append(function_line)

    def _get_visibility_prefix_for_global(self, global_var: Field, project_model: ProjectModel) -> str:
        """Determine visibility prefix for a global variable based on header presence"""
        # Check all header files (.h files) for this global
        for filename, file_model in project_model.files.items():
            if filename.endswith(".h"):
                for header_global in file_model.globals:
                    if header_global.name == global_var.name:
                        return "+ "  # Public - present in header
        return "- "  # Private - not in any header

    def _get_visibility_prefix_for_function(self, func: Function, project_model: ProjectModel) -> str:
        """Determine visibility prefix for a function based on header presence"""
        # Check all header files (.h files) for this function
        for filename, file_model in project_model.files.items():
            if filename.endswith(".h"):
                for header_func in file_model.functions:
                    if header_func.name == func.name and header_func.is_declaration:
                        return "+ "  # Public - present in header
        return "- "  # Private - not in any header

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
                    f'class "{struct_name}" as {uml_id} <<struct>> {COLOR_TYPEDEF}'
                )
                lines.append("{")
                for field in struct_data.fields:
                    self._generate_field_with_nested_structs(lines, field, "    + ")
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
                    f'class "{enum_name}" as {uml_id} <<enumeration>> {COLOR_TYPEDEF}'
                )
                lines.append("{")
                for value in sorted(enum_data.values, key=lambda x: x.name):
                    if value.value:
                        lines.append(f"    {value.name} = {value.value}")
                    else:
                        lines.append(f"    {value.name}")
                lines.append("}")
                lines.append("")

    def _generate_alias_classes(
        self, lines: List[str], file_model: FileModel, uml_ids: Dict[str, str]
    ):
        """Generate classes for alias typedefs (simple typedefs)"""
        for alias_name, alias_data in sorted(file_model.aliases.items()):
            uml_id = uml_ids.get(f"typedef_{alias_name}")
            if uml_id:
                # Determine stereotype based on whether this is a function pointer typedef
                stereotype = self._get_alias_stereotype(alias_data)
                lines.append(
                    f'class "{alias_name}" as {uml_id} {stereotype} {COLOR_TYPEDEF}'
                )
                lines.append("{")
                self._process_alias_content(lines, alias_data)
                lines.append("}")
                lines.append("")

    def _get_alias_stereotype(self, alias_data) -> str:
        """Determine the appropriate stereotype for an alias typedef"""
        original_type = alias_data.original_type.strip()
        # Check if this is a function pointer typedef by looking for the pattern (*name)(
        if "(*" in original_type and "(" in original_type.split("(*")[1]:
            return "<<function pointer>>"
        return "<<typedef>>"

    def _generate_union_classes(
        self, lines: List[str], file_model: FileModel, uml_ids: Dict[str, str]
    ):
        """Generate classes for union typedefs"""
        for union_name, union_data in sorted(file_model.unions.items()):
            uml_id = uml_ids.get(f"typedef_{union_name}")
            if uml_id:
                lines.append(
                    f'class "{union_name}" as {uml_id} <<union>> {COLOR_TYPEDEF}'
                )
                lines.append("{")
                for field in union_data.fields:
                    self._generate_field_with_nested_structs(lines, field, "    + ")
                lines.append("}")
                lines.append("")

    def _process_alias_content(self, lines: List[str], alias_data):
        """Process the content of an alias typedef with proper formatting"""
        # For aliases, show "alias of {original_type}" format
        # Handle multi-line types properly by cleaning up newlines and extra whitespace
        original_type = alias_data.original_type.replace('\n', ' ').strip()
        # Normalize multiple spaces to single spaces
        original_type = ' '.join(original_type.split())
        lines.append(f"    alias of {original_type}")

    def _is_truncated_typedef(self, alias_data, alias_lines: List[str]) -> bool:
        """Check if this is a truncated typedef"""
        return (
            alias_data.original_type.strip().endswith("(")
            or alias_data.original_type.strip().endswith("nested1")
            or alias_data.original_type.strip().endswith("{")
        ) and len(alias_lines) > 1

    def _handle_truncated_typedef(self, lines: List[str], alias_lines: List[str]):
        """Handle truncated function pointer typedef"""
        first_line = alias_lines[0].strip()
        if "(" in first_line and not first_line.endswith(")"):
            # Add ellipsis to indicate truncation
            lines.append(f"    + {first_line}...)")
        else:
            lines.append(f"    + {first_line}")

    def _handle_normal_alias(
        self,
        lines: List[str],
        alias_lines: List[str],
        inside_struct: bool,
        nested_content: List[str],
    ):
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

    def _generate_field_with_nested_structs(
        self, lines: List[str], field, base_indent: str
    ):
        """Generate field with proper handling of nested structures"""
        field_text = f"{field.type} {field.name}"

        # Check if this is a nested struct field
        if field.type.startswith("struct {") and "\n" in field.type:
            # Parse the nested struct content and flatten it
            struct_parts = field.type.split("\n")

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
                lines.append(f"{base_indent}struct {{ {content_str} }} {field.name}")
            else:
                lines.append(f"{base_indent}struct {{ }} {field.name}")
        else:
            # Handle regular multi-line field types
            field_lines = field_text.split("\n")
            for i, line in enumerate(field_lines):
                if i == 0:
                    lines.append(f"{base_indent}{line}")
                else:
                    lines.append(f"{line}")

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
        self,
        lines: List[str],
        include_tree: Dict[str, FileModel],
        uml_ids: Dict[str, str],
    ):
        """Generate include relationships using include_relations from .c files, with fallback to includes"""
        lines.append("' Include relationships")

        # Only process .c files - never use .h files for include relationships
        for file_name, file_model in sorted(include_tree.items()):
            if not file_name.endswith(".c"):
                continue  # Skip .h files - they should not contribute include relationships

            file_uml_id = self._get_file_uml_id(file_name, uml_ids)
            if not file_uml_id:
                continue

            # Prefer include_relations if available (from transformation)
            if file_model.include_relations:
                # Use include_relations for precise control based on include_depth and include_filters
                for relation in sorted(
                    file_model.include_relations,
                    key=lambda r: (r.source_file, r.included_file),
                ):
                    source_uml_id = self._get_file_uml_id(relation.source_file, uml_ids)
                    included_uml_id = self._get_file_uml_id(
                        relation.included_file, uml_ids
                    )

                    if source_uml_id and included_uml_id:
                        lines.append(
                            f"{source_uml_id} --> {included_uml_id} : <<include>>"
                        )
            else:
                # Fall back to using includes field for .c files only (backward compatibility)
                # This happens when no transformation was applied (parsing only)
                for include in sorted(file_model.includes):
                    clean_include = include.strip('<>"')
                    include_filename = Path(clean_include).name
                    include_uml_id = uml_ids.get(include_filename)
                    if include_uml_id:
                        lines.append(
                            f"{file_uml_id} --> {include_uml_id} : <<include>>"
                        )

        lines.append("")

    def _generate_declaration_relationships(
        self,
        lines: List[str],
        include_tree: Dict[str, FileModel],
        uml_ids: Dict[str, str],
    ):
        """Generate declaration relationships between files and typedefs"""
        lines.append("' Declaration relationships")
        typedef_collections_names = ["structs", "enums", "aliases", "unions"]

        for file_name, file_model in sorted(include_tree.items()):
            file_uml_id = self._get_file_uml_id(file_name, uml_ids)
            if file_uml_id:
                for collection_name in typedef_collections_names:
                    typedef_collection = getattr(file_model, collection_name)
                    for typedef_name in sorted(typedef_collection.keys()):
                        typedef_uml_id = uml_ids.get(f"typedef_{typedef_name}")
                        if typedef_uml_id:
                            lines.append(
                                f"{file_uml_id} ..> {typedef_uml_id} : <<declares>>"
                            )
        lines.append("")

    def _get_file_uml_id(
        self, file_name: str, uml_ids: Dict[str, str]
    ) -> Optional[str]:
        """Get UML ID for a file"""
        file_key = Path(file_name).name
        return uml_ids.get(file_key)

    def _generate_uses_relationships(
        self,
        lines: List[str],
        include_tree: Dict[str, FileModel],
        uml_ids: Dict[str, str],
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
        self,
        lines: List[str],
        typedef_collection: Dict,
        uml_ids: Dict[str, str],
        typedef_type: str,
    ):
        """Add uses relationships for a specific typedef collection"""
        for typedef_name, typedef_data in sorted(typedef_collection.items()):
            typedef_uml_id = uml_ids.get(f"typedef_{typedef_name}")
            if typedef_uml_id and hasattr(typedef_data, "uses"):
                for used_type in sorted(typedef_data.uses):
                    used_uml_id = uml_ids.get(f"typedef_{used_type}")
                    if used_uml_id:
                        lines.append(f"{typedef_uml_id} ..> {used_uml_id} : <<uses>>")
