#!/usr/bin/env python3
"""
PlantUML Generator that creates proper PlantUML diagrams from C source and header files.
Follows the template format with strict separation of typedefs and clear relationship groupings.
"""

import glob
import os
import re
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

    # Configuration (set by main based on Config)
    max_function_signature_chars: int = 0  # 0 or less = unlimited
    hide_macro_values: bool = False  # Hide macro values in generated PlantUML diagrams
    convert_empty_class_to_artifact: bool = False  # Render empty headers as artifacts when enabled

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
        self, model_file: str, output_dir: str = "./output"
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
                    file_model, project_model
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
        self, file_model: FileModel, project_model: ProjectModel
    ) -> str:
        """Generate a PlantUML diagram for a file following the template format"""
        basename = Path(file_model.name).stem
        # Capture placeholder headers for this diagram (if provided by transformer)
        self._placeholder_headers = set(getattr(file_model, "placeholder_headers", set()))
        include_tree = self._build_include_tree(
            file_model, project_model
        )
        # Precompute header-declared names for visibility
        header_function_decl_names: set[str] = set()
        header_global_names: set[str] = set()
        for filename, fm in project_model.files.items():
            if filename.endswith(".h"):
                for f in fm.functions:
                    if f.is_declaration:
                        header_function_decl_names.add(f.name)
                for g in fm.globals:
                    header_global_names.add(g.name)

        uml_ids = self._generate_uml_ids(include_tree, project_model)

        lines = [f"@startuml {basename}", ""]

        self._generate_all_file_classes(
            lines,
            include_tree,
            uml_ids,
            project_model,
            header_function_decl_names,
            header_global_names,
        )
        self._generate_relationships(lines, include_tree, uml_ids, project_model)

        lines.extend(["", "@enduml"])
        return "\n".join(lines)

    def _generate_all_file_classes(
        self,
        lines: List[str],
        include_tree: Dict[str, FileModel],
        uml_ids: Dict[str, str],
        project_model: ProjectModel,
        header_function_decl_names: set[str],
        header_global_names: set[str],
    ):
        """Generate all file classes (C files, headers, and typedefs)"""
        # Precompute names of function-pointer aliases to suppress duplicate struct classes
        funcptr_alias_names: set[str] = set()
        for _file_path, file_data in include_tree.items():
            # Skip placeholder headers entirely for content processing
            if _file_path.endswith(".h") and _file_path in getattr(self, "_placeholder_headers", set()):
                continue
            for alias_name, alias_data in file_data.aliases.items():
                if self._is_function_pointer_type(alias_data.original_type):
                    funcptr_alias_names.add(alias_name)

        self._generate_file_classes_by_extension(
            lines,
            include_tree,
            uml_ids,
            project_model,
            header_function_decl_names,
            header_global_names,
            ".c",
            self._generate_c_file_class,
        )
        self._generate_file_classes_by_extension(
            lines,
            include_tree,
            uml_ids,
            project_model,
            header_function_decl_names,
            header_global_names,
            ".h",
            self._generate_header_class,
        )
        self._generate_typedef_classes_for_all_files(lines, include_tree, uml_ids, funcptr_alias_names)

    def _generate_file_classes_by_extension(
        self,
        lines: List[str],
        include_tree: Dict[str, FileModel],
        uml_ids: Dict[str, str],
        project_model: ProjectModel,
        header_function_decl_names: set[str],
        header_global_names: set[str],
        extension: str,
        generator_method,
    ):
        """Generate file classes for files with specific extension"""
        for file_path, file_data in sorted(include_tree.items()):
            if file_path.endswith(extension):
                generator_method(
                    lines,
                    file_data,
                    uml_ids,
                    project_model,
                    header_function_decl_names,
                    header_global_names,
                )

    def _generate_typedef_classes_for_all_files(
        self,
        lines: List[str],
        include_tree: Dict[str, FileModel],
        uml_ids: Dict[str, str],
        funcptr_alias_names: set[str],
    ):
        """Generate typedef classes for all files in include tree"""
        # No suppression in unit test mode: keep both generic and specific typedefs available
        suppressed_structs: set[str] = set()
        suppressed_unions: set[str] = set()

        for file_path, file_data in sorted(include_tree.items()):
            # Skip typedef class generation for placeholder headers
            if file_path.endswith(".h") and file_path in getattr(self, "_placeholder_headers", set()):
                continue
            self._generate_typedef_classes(
                lines,
                file_data,
                uml_ids,
                suppressed_structs,
                suppressed_unions,
                funcptr_alias_names,
            )
        lines.append("")

    def _load_model(self, model_file: str) -> ProjectModel:
        """Load the project model from JSON file"""
        return ProjectModel.load(model_file)

    def _build_include_tree(
        self, root_file: FileModel, project_model: ProjectModel
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
        # This is the authoritative source built by the transformer (respecting include_depth and filters)
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
            # Fall back: only direct includes (depth=1) when no include_relations exist
            visited = set()

            def add_file_to_tree_once(file_name: str):
                if file_name in visited:
                    return
                visited.add(file_name)
                file_key = find_file_key(file_name)
                if file_key in project_model.files:
                    include_tree[file_key] = project_model.files[file_key]

            # Start traversal from root (already added above)
            if root_key in project_model.files:
                root_file_model = project_model.files[root_key]
                for include in root_file_model.includes:
                    clean_include = include.strip('<>"')
                    add_file_to_tree_once(clean_include)

        return include_tree

    def _generate_uml_ids(
        self, include_tree: Dict[str, FileModel], project_model: ProjectModel
    ) -> Dict[str, str]:
        """Generate UML IDs for all elements in the include tree using filename-based keys"""
        uml_ids = {}

        for filename, file_model in include_tree.items():
            basename = Path(filename).stem.upper().replace("-", "_")
            file_key = Path(filename).name  # Use just the filename as key

            if filename.endswith(".c"):
                # C files: no prefix
                uml_ids[file_key] = basename
            elif filename.endswith(".h"):
                # H files: HEADER_ prefix
                uml_ids[file_key] = f"{PREFIX_HEADER}{basename}"

            # For placeholder headers, only generate the file UML ID; skip typedef UML IDs
            if filename.endswith(".h") and Path(filename).name in getattr(self, "_placeholder_headers", set()):
                continue

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
        import re

        hide_values = getattr(self, "hide_macro_values", False)

        # Regex for function-like macro (no space before '(')
        func_like_pattern = re.compile(r"#define\s+([A-Za-z_][A-Za-z0-9_]*\([^)]*\))")
        obj_like_pattern = re.compile(r"#define\s+([A-Za-z_][A-Za-z0-9_]*)")

        match = func_like_pattern.search(macro)
        if match:
            # Function-like macros: only show name+params
            macro_name_with_params = match.group(1)
            return f"{INDENT}{prefix}#define {macro_name_with_params}"

        match = obj_like_pattern.search(macro)
        if match:
            if hide_values:
                # Only name
                macro_name = match.group(1)
                return f"{INDENT}{prefix}#define {macro_name}"
            else:
                # Full definition
                clean_macro = macro.strip()
                if clean_macro.startswith("#define"):
                    return f"{INDENT}{prefix}{clean_macro}"

        # Fallback
        return f"{INDENT}{prefix}{macro}"

    def _format_global_variable(self, global_var, prefix: str = "") -> str:
        """Format a global variable with the given prefix."""
        return f"{INDENT}{prefix}{global_var.type} {global_var.name}"

    def _format_function_signature(self, func, prefix: str = "") -> str:
        """Format a function signature with truncation if needed."""
        params = self._format_function_parameters(func.parameters)
        param_str_full = ", ".join(params)

        # Remove 'extern' and 'LOCAL_INLINE' keywords from return type for UML diagrams
        return_type = func.return_type.replace("extern ", "").replace("LOCAL_INLINE ", "").strip()

        # Build full signature
        full_signature = f"{INDENT}{prefix}{return_type} {func.name}({param_str_full})"
        limit = getattr(self, "max_function_signature_chars", 0)
        if isinstance(limit, int) and limit > 0 and len(full_signature) > limit:
            # Try to truncate parameters by characters while preserving readability and appending ...
            head = f"{INDENT}{prefix}{return_type} {func.name}("
            remaining = limit - len(head) - 1  # -1 for closing paren
            if remaining <= 0:
                return head + "...)"
            # fill with params until remaining would be exceeded
            out = []
            consumed = 0
            for i, p in enumerate(params):
                add = (", " if i > 0 else "") + p
                if consumed + len(add) + 3 > remaining:  # +3 for ellipsis when needed
                    out.append(", ..." if i > 0 else "...")
                    break
                out.append(add)
                consumed += len(add)
            param_str = "".join(out)
            return head + param_str + ")"
        return full_signature

    def _format_function_parameters(self, parameters) -> List[str]:
        """Format function parameters into string list."""
        params = []
        for p in parameters:
            if p.name == "..." and p.type == "...":
                params.append("...")
                continue

            # Avoid duplicating the name for function pointer parameters if the type already contains it
            type_str = p.type.strip()
            name_str = p.name.strip()
            # Detect patterns like "( * name )" within the type
            try:
                contains_func_ptr = "( *" in type_str and ")" in type_str
                name_inside = None
                if contains_func_ptr:
                    after = type_str.split("( *", 1)[1]
                    name_inside = after.split(")", 1)[0].strip()
                if name_inside and name_str and name_str == name_inside:
                    params.append(type_str)
                else:
                    params.append(f"{type_str} {name_str}".strip())
            except Exception:
                # Fallback if any unexpected formatting occurs
                params.append(f"{type_str} {name_str}".strip())
        return params

    # Truncation disabled to ensure complete signatures are rendered

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
        if not file_model.functions:
            return

        # Collect matching function lines first to avoid emitting an empty header
        function_lines: List[str] = []
        for func in sorted(file_model.functions, key=lambda x: x.name):
            if is_declaration_only and (func.is_declaration or func.is_inline):
                function_lines.append(self._format_function_signature(func, prefix))
            elif not is_declaration_only and not func.is_declaration:
                function_lines.append(self._format_function_signature(func, prefix))

        if function_lines:
            lines.append(f"{INDENT}-- Functions --")
            lines.extend(function_lines)

    def _generate_c_file_class(
        self,
        lines: List[str],
        file_model: FileModel,
        uml_ids: Dict[str, str],
        project_model: ProjectModel,
        header_function_decl_names: set[str],
        header_global_names: set[str],
    ):
        """Generate class for C file using unified method with dynamic visibility"""
        self._generate_file_class_unified(
            lines=lines,
            file_model=file_model,
            uml_ids=uml_ids,
            header_function_decl_names=header_function_decl_names,
            header_global_names=header_global_names,
            class_type="source",
            color=COLOR_SOURCE,
            macro_prefix="- ",
            is_declaration_only=False,
            use_dynamic_visibility=True,
        )

    def _generate_header_class(
        self,
        lines: List[str],
        file_model: FileModel,
        uml_ids: Dict[str, str],
        project_model: ProjectModel,
        header_function_decl_names: set[str],
        header_global_names: set[str],
    ):
        """Generate class for header file using unified method with static '+' visibility"""
        self._generate_file_class_unified(
            lines=lines,
            file_model=file_model,
            uml_ids=uml_ids,
            header_function_decl_names=header_function_decl_names,
            header_global_names=header_global_names,
            class_type="header",
            color=COLOR_HEADER,
            macro_prefix="+ ",
            is_declaration_only=True,
            use_dynamic_visibility=False,
        )

    def _generate_file_class_unified(
        self,
        lines: List[str],
        file_model: FileModel,
        uml_ids: Dict[str, str],
        header_function_decl_names: set[str],
        header_global_names: set[str],
        class_type: str,
        color: str,
        macro_prefix: str,
        is_declaration_only: bool,
        use_dynamic_visibility: bool,
    ):
        """Generate class for a file; dynamic visibility for sources, static for headers."""
        basename = Path(file_model.name).stem
        filename = Path(file_model.name).name
        uml_id = uml_ids.get(filename)

        if not uml_id:
            return

        lines.append(f'class "{basename}" as {uml_id} <<{class_type}>> {color}')
        lines.append("{")

        # If this header is marked as placeholder for this diagram, render as empty class
        if class_type == "header" and Path(filename).name in getattr(self, "_placeholder_headers", set()):
            # When configured, render empty headers as artifact nodes instead of empty classes
            if getattr(self, "convert_empty_class_to_artifact", False):
                # Remove the opening brace and replace the class line with artifact syntax
                lines.pop()
                lines[-1] = f'() "{basename}" as {uml_id} <<{class_type}>> {color}'
                lines.append("")
                return
            lines.append("}")
            lines.append("")
            return

        self._add_macros_section(lines, file_model, macro_prefix)
        if use_dynamic_visibility:
            # Use precomputed header visibility sets
            self._add_globals_section_with_visibility(
                lines, file_model, header_global_names
            )
            self._add_functions_section_with_visibility(
                lines, file_model, header_function_decl_names, is_declaration_only
            )
        else:
            # Static '+' visibility for headers
            self._add_globals_section(lines, file_model, "+ ")
            self._add_functions_section(
                lines, file_model, "+ ", is_declaration_only
            )

        lines.append("}")
        lines.append("")

    def _add_globals_section_with_visibility(
        self, lines: List[str], file_model: FileModel, header_global_names: set[str]
    ):
        """Add global variables section with visibility based on header presence, grouped by visibility"""
        if file_model.globals:
            lines.append(f"{INDENT}-- Global Variables --")
            
            # Separate globals into public and private groups
            public_globals = []
            private_globals = []
            
            for global_var in sorted(file_model.globals, key=lambda x: x.name):
                prefix = "+ " if global_var.name in header_global_names else "- "
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
        header_function_decl_names: set[str],
        is_declaration_only: bool = False,
    ):
        """Add functions section with visibility based on header presence, grouped by visibility"""
        if not file_model.functions:
            return

        # Separate functions into public and private groups, collecting first
        public_functions: List[str] = []
        private_functions: List[str] = []

        for func in sorted(file_model.functions, key=lambda x: x.name):
            if is_declaration_only and (func.is_declaration or func.is_inline):
                prefix = "+ "
                formatted_function = self._format_function_signature(func, prefix)
                public_functions.append(formatted_function)
            elif not is_declaration_only and not func.is_declaration:
                prefix = "+ " if func.name in header_function_decl_names else "- "
                formatted_function = self._format_function_signature(func, prefix)

                if prefix == "+ ":
                    public_functions.append(formatted_function)
                else:
                    private_functions.append(formatted_function)

        if public_functions or private_functions:
            lines.append(f"{INDENT}-- Functions --")
            # Add public functions first
            for function_line in public_functions:
                lines.append(function_line)

            # Add empty line between public and private if both exist
            if public_functions and private_functions:
                lines.append("")

            # Add private functions
            for function_line in private_functions:
                lines.append(function_line)

    # Removed O(N^2) header scans in favor of precomputed header visibility sets

    def _generate_typedef_classes(
        self,
        lines: List[str],
        file_data: FileModel,
        uml_ids: Dict[str, str],
        suppressed_structs: set[str],
        suppressed_unions: set[str],
        funcptr_alias_names: set[str],
    ):
        """Generate classes for typedefs"""
        self._generate_struct_classes(lines, file_data, uml_ids, suppressed_structs, funcptr_alias_names)
        self._generate_enum_classes(lines, file_data, uml_ids)
        self._generate_alias_classes(lines, file_data, uml_ids)
        self._generate_union_classes(lines, file_data, uml_ids, suppressed_unions)

    def _generate_struct_classes(
        self,
        lines: List[str],
        file_model: FileModel,
        uml_ids: Dict[str, str],
        suppressed_structs: set[str],
        funcptr_alias_names: set[str],
    ):
        """Generate classes for struct typedefs"""
        for struct_name, struct_data in sorted(file_model.structs.items()):
            # Skip if suppressed due to duplicate suffix with a more specific name
            if struct_name in suppressed_structs:
                continue
            # Skip if there is a function-pointer alias with the same name to avoid duplicate typedef of result_generator_t
            if struct_name in funcptr_alias_names:
                continue
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
        # Preserve original declaration order by iterating without sorting
        for enum_name, enum_data in file_model.enums.items():
            uml_id = uml_ids.get(f"typedef_{enum_name}")
            if uml_id:
                lines.append(
                    f'class "{enum_name}" as {uml_id} <<enumeration>> {COLOR_TYPEDEF}'
                )
                lines.append("{")
                # Preserve source order: do not sort enum values
                for value in enum_data.values:
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
        if self._is_function_pointer_type(original_type):
            return "<<function pointer>>"
        return "<<typedef>>"

    def _is_function_pointer_type(self, type_str: str) -> bool:
        """Heuristically detect C function pointer type patterns with optional whitespace.
        Examples: int (*name)(...), int ( * name ) ( ... ), int (*(*name)(...))(...) 
        """
        pattern = re.compile(r"\(\s*\*\s*\w+\s*\)\s*\(")
        if pattern.search(type_str):
            return True
        # Also detect nested function pointer returns: (*(*name)(...))(
        pattern_nested = re.compile(r"\(\s*\*\s*\(\s*\*\s*\w+\s*\)\s*\)\s*\(")
        return bool(pattern_nested.search(type_str))

    def _generate_union_classes(
        self,
        lines: List[str],
        file_model: FileModel,
        uml_ids: Dict[str, str],
        suppressed_unions: set[str],
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

    # Removed dead/unused alias handling helpers (_is_truncated_typedef, _handle_truncated_typedef, _handle_normal_alias)

    def _generate_field_with_nested_structs(
        self, lines: List[str], field, base_indent: str
    ):
        """Generate field with proper handling of nested structures"""
        field_text = f"{field.type} {field.name}"

        # Check if this is a nested struct field with newlines
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
        # Fallback: if a garbled anonymous pattern is detected, render as placeholder
        elif re.search(r"}\s+\w+;\s*struct\s*{", field.type):
            struct_type = "struct" if "struct" in field.type else ("union" if "union" in field.type else "struct")
            lines.append(f"{base_indent}{struct_type} {{ ... }} {field.name}")
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
        self._generate_declaration_relationships(lines, include_tree, uml_ids, project_model)
        self._generate_uses_relationships(lines, include_tree, uml_ids, project_model)
        self._generate_anonymous_relationships(lines, project_model, uml_ids)

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
        project_model: ProjectModel,
    ):
        """Generate declaration relationships between files and typedefs"""
        lines.append("' Declaration relationships")
        typedef_collections_names = ["structs", "enums", "aliases", "unions"]

        for file_name, file_model in sorted(include_tree.items()):
            # Suppress declaration relationships from placeholder headers
            if file_name.endswith(".h") and Path(file_name).name in getattr(self, "_placeholder_headers", set()):
                continue
            file_uml_id = self._get_file_uml_id(file_name, uml_ids)
            if file_uml_id:
                for collection_name in typedef_collections_names:
                    typedef_collection = getattr(file_model, collection_name)
                    for typedef_name in sorted(typedef_collection.keys()):
                        # Skip anonymous structures - they should not have declares relationships from files
                        if self._is_anonymous_structure_in_project(typedef_name, project_model):
                            continue
                        
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

    def _is_anonymous_structure_in_project(self, typedef_name: str, project_model: ProjectModel) -> bool:
        """Check if a typedef is an anonymous structure using the provided project model"""
        for file_model in project_model.files.values():
            if file_model.anonymous_relationships:
                for parent_name, children in file_model.anonymous_relationships.items():
                    if typedef_name in children:
                        return True
        return False

    def _generate_uses_relationships(
        self,
        lines: List[str],
        include_tree: Dict[str, FileModel],
        uml_ids: Dict[str, str],
        project_model: ProjectModel,
    ):
        """Generate uses relationships between typedefs"""
        lines.append("' Uses relationships")
        for file_name, file_model in sorted(include_tree.items()):
            # Struct uses relationships
            self._add_typedef_uses_relationships(
                lines, file_model.structs, uml_ids, "struct", project_model
            )
            # Alias uses relationships
            self._add_typedef_uses_relationships(
                lines, file_model.aliases, uml_ids, "alias", project_model
            )
            # Union uses relationships
            self._add_typedef_uses_relationships(
                lines, file_model.unions, uml_ids, "union", project_model
            )

    def _add_typedef_uses_relationships(
        self,
        lines: List[str],
        typedef_collection: Dict,
        uml_ids: Dict[str, str],
        typedef_type: str,
        project_model: ProjectModel,
    ):
        """Add uses relationships for a specific typedef collection"""
        for typedef_name, typedef_data in sorted(typedef_collection.items()):
            # Skip emitting uses from anonymous parents to reduce duplication/noise in diagrams
            if isinstance(typedef_name, str) and typedef_name.startswith("__anonymous_"):
                continue
            typedef_uml_id = uml_ids.get(f"typedef_{typedef_name}")
            if typedef_uml_id and hasattr(typedef_data, "uses"):
                for used_type in sorted(typedef_data.uses):
                    used_uml_id = uml_ids.get(f"typedef_{used_type}")
                    if used_uml_id:
                        # Allow uses when the parent itself is anonymous; otherwise skip anonymous children (handled via composition)
                        is_parent_anonymous = typedef_name.startswith("__anonymous_")
                        if self._is_anonymous_structure_in_project(used_type, project_model) and not is_parent_anonymous:
                            continue
                        # If there is a composition for this pair, do not add a duplicate uses relation
                        if self._is_anonymous_composition_pair(typedef_name, used_type, project_model):
                            continue
                        lines.append(f"{typedef_uml_id} ..> {used_uml_id} : <<uses>>")

    def _generate_anonymous_relationships(
        self, lines: List[str], project_model: ProjectModel, uml_ids: Dict[str, str]
    ):
        """Generate composition relationships for anonymous structures."""
        # First, check if there are any anonymous relationships
        has_relationships = False
        relationships_to_generate = []
        
        # Process all files in the project model
        for file_name, file_model in project_model.files.items():
            if not file_model.anonymous_relationships:
                continue
                
            # Generate relationships for each parent-child pair
            for parent_name, children in file_model.anonymous_relationships.items():
                parent_id = self._get_anonymous_uml_id(parent_name, uml_ids)
                
                for child_name in children:
                    # Skip only pure generic placeholders as children (allow suffixed ones)
                    if child_name in ("__anonymous_struct__", "__anonymous_union__"):
                        continue
                    child_id = self._get_anonymous_uml_id(child_name, uml_ids)
                    
                    if parent_id and child_id:
                        has_relationships = True
                        relationships_to_generate.append(f"{parent_id} *-- {child_id} : <<contains>>")
        
        # Only add the section header and relationships if we have any
        if has_relationships:
            lines.append("")
            lines.append("' Anonymous structure relationships (composition)")
            for relationship in relationships_to_generate:
                lines.append(relationship)


    def _get_anonymous_uml_id(self, entity_name: str, uml_ids: Dict[str, str]) -> Optional[str]:
        """Get UML ID for an anonymous structure entity using typedef-based keys with case-insensitive fallback."""
        # Try direct key
        if entity_name in uml_ids:
            return uml_ids[entity_name]
        
        # Try exact typedef key
        typedef_exact = f"typedef_{entity_name}"
        if typedef_exact in uml_ids:
            return uml_ids[typedef_exact]

        # Case-insensitive match for typedef keys
        entity_lower = entity_name.lower()
        for key, value in uml_ids.items():
            if key.startswith("typedef_") and key[len("typedef_"):].lower() == entity_lower:
                return value

        return None

    def _is_anonymous_composition_pair(self, parent_name: str, child_name: str, project_model: ProjectModel) -> bool:
        """Return True if a given parent->child anonymous composition exists in the project model."""
        for file_model in project_model.files.values():
            rels = getattr(file_model, "anonymous_relationships", None)
            if not rels:
                continue
            if parent_name in rels and child_name in rels[parent_name]:
                return True
        return False