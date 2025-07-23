#!/usr/bin/env python3
"""
Generator module for C to PlantUML converter - Step 3: Generate puml files based on model.json
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import re

from .models import FileModel, ProjectModel, EnumValue


class PlantUMLGenerator:
    """PlantUML diagram generator"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate_diagram(
        self, file_model: FileModel, project_model: ProjectModel, include_depth: int = 1
    ) -> str:
        """Generate PlantUML diagram for a single file"""
        self.logger.debug(f"Generating diagram for: {file_model.file_path}")

        # Get file basename for diagram name
        file_path = Path(file_model.file_path)
        basename = file_path.stem

        # Start PlantUML diagram
        diagram_lines = [f"@startuml {basename}", ""]

        # Generate main class for the file
        diagram_lines.extend(self._generate_main_class(file_model, basename, project_model))

        # Build include hierarchy for relationship filtering
        include_hierarchy = self._build_include_hierarchy(file_model, project_model)
        
        # Collect all typedef names and header names that will be referenced in relationships
        referenced_typedefs = self._collect_referenced_typedefs(file_model, project_model, include_hierarchy)
        referenced_headers = self._collect_referenced_headers(file_model, project_model, include_hierarchy)

        # Generate typedef classes (including all referenced typedefs)
        diagram_lines.extend(self._generate_typedef_classes_with_references(file_model, project_model, include_depth, referenced_typedefs, include_hierarchy))
        
        # Generate header classes (including all referenced headers)
        diagram_lines.extend(self._generate_header_classes_with_references(file_model, project_model, include_depth, referenced_headers))

        # Generate relationships
        diagram_lines.extend(self._generate_relationships(file_model, project_model))

        # Generate typedef uses relations
        
        # Generate function and variable type dependencies
        diagram_lines.extend(self.generate_type_dependencies(file_model, project_model, include_hierarchy))
        
        # Generate declares relationships between files and typedefs
        diagram_lines.extend(self.generate_declares_relationships(file_model, project_model, include_hierarchy))
        
        # Generate declares relationships for included header files
        diagram_lines.extend(self.generate_included_declares_relationships(file_model, project_model, include_hierarchy))

        # Deduplicate relationships to prevent duplicates
        diagram_lines = self._deduplicate_relationships(diagram_lines)

        # End diagram
        diagram_lines.extend(["", "@enduml"])

        return "\n".join(diagram_lines)

    def _format_function_signature(self, function) -> str:
        """Format a function signature with parameters for PlantUML display"""
        if function.parameters:
            param_str = ", ".join([f"{param.type} {param.name}" for param in function.parameters])
            return f"{function.return_type} {function.name}({param_str})"
        else:
            return f"{function.return_type} {function.name}()"

    def _clean_function_signature(self, signature: str) -> str:
        """Clean up function signature by removing unwanted content like include statements"""
        # Remove include statements that might have been mixed in
        import re
        
        # Remove #include statements
        signature = re.sub(r'#include\s+[<"][^>"]*[>"]', '', signature)
        
        # Remove struct definitions and other non-function content
        signature = re.sub(r'typedef\s+struct[^;]+;', '', signature)
        signature = re.sub(r'struct\s+\w+\s*{[^}]*}', '', signature)
        
        # Remove function bodies (everything after { until the end)
        signature = re.sub(r'\s*\{[^}]*\}(?:\s*;)?$', ';', signature)
        
        # Fix malformed variadic functions (replace ... ... with ...)
        signature = re.sub(r'\.\.\.\s+\.\.\.', '...', signature)
        
        # Clean up extra whitespace
        signature = re.sub(r'\s+', ' ', signature).strip()
        
        return signature

    def _deduplicate_functions(self, functions: List) -> List:
        """Remove duplicate functions and keep only declarations for headers"""
        seen = set()
        unique_functions = []
        
        for func in functions:
            # Create a key based on function name and parameters
            param_str = ', '.join([f"{p.type} {p.name}" for p in func.parameters]) if func.parameters else ""
            key = f"{func.name}({param_str})"
            
            if key not in seen:
                seen.add(key)
                unique_functions.append(func)
        
        return unique_functions

    def _is_function_declaration_only(self, function) -> bool:
        """Check if this is a function declaration (no body)"""
        # If the function has a body, it's an implementation, not a declaration
        # We can detect this by checking if there are any tokens that indicate a function body
        # For now, we'll use a simple heuristic: if the function signature ends with ';' it's likely a declaration
        signature = self._format_function_signature(function)
        return signature.strip().endswith(';')

    def _generate_main_class(self, file_model: FileModel, basename: str, project_model: ProjectModel) -> List[str]:
        """Generate the main class for the file using the new PlantUML template"""
        # Determine if this is a header file
        is_header = file_model.file_path.endswith('.h')
        
        # Use appropriate stereotype and UML ID method
        if is_header:
            stereotype = "<<header>>"
            color = "#LightGreen"
            uml_id = self._get_header_uml_id(basename)
        else:
            stereotype = "<<source>>"
            color = "#LightBlue"
            uml_id = self._get_uml_id(basename)
        
        lines = [
            f'class "{basename}" as {uml_id} {stereotype} {color}',
            "{",
        ]
        
        if file_model.macros:
            lines.append("    -- Macros --")
            for macro in file_model.macros:
                lines.append(f"    - #define {macro}")
        
        if file_model.globals:
            lines.append("    -- Global Variables --")
            for glob in file_model.globals:
                # Determine visibility based on file type and variable type
                is_header = file_model.file_path.endswith('.h')
                is_static = glob.type.startswith('static ')
                
                # Headers use + for all globals, source files use - for all globals
                if is_header:
                    visibility = "+"
                else:
                    visibility = "-"
                
                # Remove 'static ' prefix from type for display
                display_type = glob.type.replace('static ', '') if is_static else glob.type
                
                if hasattr(glob, 'value') and glob.value is not None:
                    lines.append(f"    {visibility} {display_type} {glob.name} = {glob.value}")
                else:
                    lines.append(f"    {visibility} {display_type} {glob.name}")
        
        if file_model.functions:
            lines.append("    -- Functions --")
            # Deduplicate functions but keep both declarations and implementations
            unique_functions = self._deduplicate_functions(file_model.functions)
            
            for function in unique_functions:
                # Clean up the function signature to remove any unwanted content
                signature = self._format_function_signature(function)
                signature = self._clean_function_signature(signature)
                
                # For implementations, remove the function body if it's too long
                if hasattr(function, 'is_declaration') and not function.is_declaration:
                    # This is an implementation - truncate if it's too long
                    if len(signature) > 100:
                        # Find the opening brace and truncate
                        brace_pos = signature.find('{')
                        if brace_pos > 0:
                            signature = signature[:brace_pos].rstrip() + ' { ... }'
                
                lines.append(f"    {signature}")
        
        # Do not show structs/enums/unions directly if they are only present as typedefs
        # (They will be shown in their own class if needed)
        lines.append("}")
        lines.append("")
        return lines

    def _generate_header_classes(
        self, file_model: FileModel, project_model: ProjectModel, include_depth: int = 1
    ) -> List[str]:
        """Generate classes for included header files"""
        lines = []
        seen_headers = set()

        # Process direct includes (depth 1)
        for include_name in file_model.includes:
            # First try to find the file directly in project_model.files
            included_file_model = None
            for key, model in project_model.files.items():
                # Check if the file name matches the include (with or without extension)
                file_basename = Path(key).stem
                if file_basename == include_name or key == include_name:
                    included_file_model = model
                    break
            # If not found in project_model.files, try to find it on the file system
            if not included_file_model:
                included_file_path = self._find_included_file(
                    include_name, file_model.project_root, project_model
                )
                
                if included_file_path:
                    # Try to find the file in project_model.files by matching file paths
                    for key, model in project_model.files.items():
                        if model.file_path == included_file_path:
                            included_file_model = model
                            break
            # Skip self-include
            if included_file_model and included_file_model.file_path == file_model.file_path:
                continue
            if included_file_model:
                header_basename = Path(included_file_model.file_path).stem
                if header_basename not in seen_headers:
                    seen_headers.add(header_basename)
                    lines.extend(
                        self._generate_header_class(included_file_model, header_basename)
                    )
            else:
                # This is an external header that couldn't be found
                # Generate an empty header class for it
                header_basename = include_name
                if header_basename not in seen_headers:
                    seen_headers.add(header_basename)
                    lines.extend(
                        self._generate_external_header_class(header_basename)
                    )

        # Process indirect includes from include_relations (up to configured depth)
        if include_depth > 1:
                included_file_model = None
                # Try to find the included file model by matching file_path
                for key, model in project_model.files.items():
                    if model.file_path == included_file_path:
                        included_file_model = model
                        break
                # If not found by file_path, try to find by relative path
                if not included_file_model:
                    included_file_basename = Path(included_file_path).name
                    for key, model in project_model.files.items():
                        if key == included_file_basename:
                            included_file_model = model
                            break
                if included_file_model:
                    header_basename = Path(included_file_model.file_path).stem
                    if header_basename not in seen_headers:
                        seen_headers.add(header_basename)
                        lines.extend(
                            self._generate_header_class(included_file_model, header_basename)
                        )
                    
                    # Recursively process include relationships from the included file (respecting depth)
                    self._process_nested_includes(included_file_model, project_model, seen_headers, lines, depth=1, max_depth=include_depth)
                else:
                    # Debug logging to see what's happening
                    import logging
                    logging.getLogger(__name__).debug(f"Could not find included file model for: {included_file_path}")
                    logging.getLogger(__name__).debug(f"Available keys: {list(project_model.files.keys())}")
                
                # Also process external headers from included files
                if included_file_model:
                    for include_name in included_file_model.includes:
                        # Check if this is an external header
                        included_file_path = self._find_included_file(
                            include_name, included_file_model.project_root, project_model
                        )
                        if included_file_path and included_file_path.startswith("EXTERNAL:"):
                            external_header_name = included_file_path.split(":", 1)[1]
                            # Ensure external header has .h extension for consistency
                            if not external_header_name.endswith('.h'):
                                external_header_name = f"{external_header_name}.h"
                            
                            if external_header_name not in seen_headers:
                                seen_headers.add(external_header_name)
                                lines.extend(
                                    self._generate_external_header_class(external_header_name)
                                )

        return lines

    def _process_nested_includes(self, file_model: FileModel, project_model: ProjectModel, seen_headers: set, lines: List[str], visited_files: set = None, depth: int = 0, max_depth: int = 3, include_hierarchy: set = None) -> None:
        """Recursively process include relationships from included files"""
        if visited_files is None:
            visited_files = set()
        
        # Prevent infinite recursion and respect max_depth
        if depth >= max_depth or file_model.file_path in visited_files:
            return
        
        visited_files.add(file_model.file_path)
        
        # Process each include
        for include_name in file_model.includes:
            included_file_path = self._find_included_file(include_name, file_model.project_root, project_model)
            if not included_file_path:
                continue
                
            included_file_model = None
            # Try to find the included file model by matching file_path
            for key, model in project_model.files.items():
                if model.file_path == included_file_path:
                    included_file_model = model
                    break
            # If not found by file_path, try to find by relative path
            if not included_file_model:
                included_file_basename = Path(included_file_path).name
                for key, model in project_model.files.items():
                    if key == included_file_basename:
                        included_file_model = model
                        break
            if included_file_model:
                header_basename = Path(included_file_model.file_path).stem
                # Only include headers that are in the include hierarchy
                if (include_hierarchy is None or header_basename in include_hierarchy) and header_basename not in seen_headers:
                    seen_headers.add(header_basename)
                    lines.extend(
                        self._generate_header_class(included_file_model, header_basename)
                    )
                    # Recursively process further nested includes (respecting max_depth)
                    self._process_nested_includes(included_file_model, project_model, seen_headers, lines, visited_files, depth + 1, max_depth, include_hierarchy)

    def _process_nested_typedefs(self, file_model: FileModel, project_model: ProjectModel, seen_typedefs: set, lines: List[str], visited_files: set = None, depth: int = 0, max_depth: int = 3) -> None:
        """Recursively process typedefs from included files"""
        if visited_files is None:
            visited_files = set()
        
        # Prevent infinite recursion and respect max_depth
        if depth >= max_depth or file_model.file_path in visited_files:
            return
        
        visited_files.add(file_model.file_path)
        
        # Process each include
        for include_name in file_model.includes:
            included_file_path = self._find_included_file(include_name, file_model.project_root, project_model)
            if not included_file_path:
                continue
                
            included_file_model = None
            # Try to find the included file model by matching file_path
            for key, model in project_model.files.items():
                if model.file_path == included_file_path:
                    included_file_model = model
                    break
            # If not found by file_path, try to find by relative path
            if not included_file_model:
                included_file_basename = Path(included_file_path).name
                for key, model in project_model.files.items():
                    if key == included_file_basename:
                        included_file_model = model
                        break
            if included_file_model:
                # Only process typedefs from direct includes (depth 0) to avoid duplicates
                if depth == 0:
                    # Process simple typedefs from the aliases dictionary
                    for typedef_name, original_type in included_file_model.aliases.items():
                        if typedef_name not in seen_typedefs:
                            seen_typedefs.add(typedef_name)
                            lines.extend(self._generate_simple_typedef_class(typedef_name, original_type, project_model))
                    
class Generator:
    """Main generator class for Step 3: Generate puml files based on model.json"""

    def __init__(self):
        self.plantuml_generator = PlantUMLGenerator()
        self.logger = logging.getLogger(__name__)

    def generate(self, model_file: str, output_dir: str = "./output", include_depth: int = 1) -> str:
        """
        Step 3: Generate puml files based on model.json

        Args:
            model_file: Input JSON model file path
            output_dir: Output directory for PlantUML files
            include_depth: Maximum depth for include processing

        Returns:
            Path to the output directory
        """
        self.logger.info(f"Step 3: Generating PlantUML diagrams from: {model_file}")

        # Load the model
        model = self._load_model(model_file)

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate diagrams for each C file only (not header files)
        generated_files = []
        for file_path, file_model in model.files.items():
            # Only generate PlantUML diagrams for C files, not header files
            if file_path.endswith('.c'):
                try:
                    diagram_content = self.plantuml_generator.generate_diagram(
                        file_model, model, include_depth
                    )

                    # Create output file
                    basename = Path(file_path).stem
                    output_file = output_path / f"{basename}.puml"

                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(diagram_content)

                    generated_files.append(str(output_file))
                    self.logger.debug(f"Generated: {output_file}")

                except Exception as e:
                    self.logger.warning(
                        f"Failed to generate diagram for {file_path}: {e}"
                    )
            else:
                self.logger.debug(f"Skipping header file: {file_path}")

        self.logger.info(
            f"Step 3 complete! Generated {len(generated_files)} PlantUML files "
            f"in: {output_dir}"
        )
        return output_dir

    def _load_model(self, model_file: str) -> ProjectModel:
        """Load model from JSON file"""
        if not Path(model_file).exists():
            raise FileNotFoundError(f"Model file not found: {model_file}")

        try:
            with open(model_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Convert back to ProjectModel
            model = ProjectModel(
                project_name=data["project_name"],
                project_root=data["project_root"],
                files={},
                created_at=data["created_at"],
            )

            # Convert file data back to FileModel objects
            for file_path, file_data in data["files"].items():
                model.files[file_path] = self._dict_to_file_model(file_data)

            self.logger.debug(f"Loaded model with {len(model.files)} files")
            return model

        except Exception as e:
            raise ValueError(f"Failed to load model from {model_file}: {e}")

    def _dict_to_file_model(self, data: Dict) -> FileModel:
        """Convert dictionary back to FileModel"""
        from .models import (
            Enum,
            EnumValue,
            Field,
            FileModel,
            Function,
            IncludeRelation,
            Struct,
            TypedefRelation,
            Union,
        )

        # Convert structs
        structs = {}
        for name, struct_data in data.get("structs", {}).items():
            fields = [
                Field(f["name"], f["type"]) for f in struct_data.get("fields", [])
            ]
            structs[name] = Struct(name, fields, struct_data.get("methods", []))

        # Convert enums
        enums = {}
        for name, enum_data in data.get("enums", {}).items():
            values = []
            for value_data in enum_data.get("values", []):
                if isinstance(value_data, dict):
                    values.append(EnumValue(value_data["name"], value_data.get("value")))
                else:
                    values.append(EnumValue(value_data))
            enums[name] = Enum(name, values)

        # Convert unions
        unions = {}
        for name, union_data in data.get("unions", {}).items():
            fields = [Field(f["name"], f["type"]) for f in union_data.get("fields", [])]
            unions[name] = Union(name, fields)

        # Convert functions
        functions = []
        for func_data in data.get("functions", []):
            # Convert parameters from dict to Field objects
            parameters = []
            for param_data in func_data.get("parameters", []):
                if isinstance(param_data, dict):
                    parameters.append(Field(param_data["name"], param_data["type"]))
                else:
                    # Handle case where parameters might already be Field objects
                    parameters.append(param_data)
            
            functions.append(
                Function(
                    func_data["name"],
                    func_data["return_type"],
                    parameters,
                    is_static=func_data.get("is_static", False),
                    is_declaration=func_data.get("is_declaration", False),
                )
            )

        # Convert globals
        globals_list = []
        for global_data in data.get("globals", []):
            globals_list.append(Field(global_data["name"], global_data["type"]))

        # Convert typedef relations