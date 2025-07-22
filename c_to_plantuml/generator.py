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
        diagram_lines.extend(self._generate_typedef_classes_with_references(file_model, project_model, include_depth, referenced_typedefs))
        
        # Generate header classes (including all referenced headers)
        diagram_lines.extend(self._generate_header_classes_with_references(file_model, project_model, include_depth, referenced_headers))

        # Generate relationships
        diagram_lines.extend(self._generate_relationships(file_model, project_model))

        # Generate typedef uses relations
        diagram_lines.extend(self.generate_typedef_uses_relations(file_model, project_model, include_hierarchy))
        
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
            for include_relation in file_model.include_relations:
                included_file_path = include_relation.included_file
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

    def _process_nested_includes(self, file_model: FileModel, project_model: ProjectModel, seen_headers: set, lines: List[str], visited_files: set = None, depth: int = 0, max_depth: int = 3) -> None:
        """Recursively process include relationships from included files"""
        if visited_files is None:
            visited_files = set()
        
        # Prevent infinite recursion and respect max_depth
        if depth >= max_depth or file_model.file_path in visited_files:
            return
        
        visited_files.add(file_model.file_path)
        
        for include_relation in file_model.include_relations:
            included_file_path = include_relation.included_file
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
                    # Recursively process further nested includes (respecting max_depth)
                    self._process_nested_includes(included_file_model, project_model, seen_headers, lines, visited_files, depth + 1, max_depth)

    def _process_nested_typedefs(self, file_model: FileModel, project_model: ProjectModel, seen_typedefs: set, lines: List[str], visited_files: set = None, depth: int = 0, max_depth: int = 3) -> None:
        """Recursively process typedefs from included files"""
        if visited_files is None:
            visited_files = set()
        
        # Prevent infinite recursion and respect max_depth
        if depth >= max_depth or file_model.file_path in visited_files:
            return
        
        visited_files.add(file_model.file_path)
        
        for include_relation in file_model.include_relations:
            included_file_path = include_relation.included_file
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
                    # Process simple typedefs from the typedefs dictionary
                    for typedef_name, original_type in included_file_model.typedefs.items():
                        if typedef_name not in seen_typedefs:
                            seen_typedefs.add(typedef_name)
                            lines.extend(self._generate_simple_typedef_class(typedef_name, original_type, project_model))
                    
                    # Process complex typedefs from typedef_relations
                    for typedef_relation in included_file_model.typedef_relations:
                        typedef_name = typedef_relation.typedef_name
                        if typedef_name not in seen_typedefs:
                            seen_typedefs.add(typedef_name)
                            lines.extend(self._generate_single_typedef_class(typedef_relation, included_file_model, project_model))
                
                # Recursively process further nested typedefs (respecting max_depth)
                self._process_nested_typedefs(included_file_model, project_model, seen_typedefs, lines, visited_files, depth + 1, max_depth)

    def _generate_header_class(self, file_model: FileModel, basename: str) -> List[str]:
        """Generate a class for a header file using the new PlantUML template"""
        lines = [
            f'class "{basename}" as {self._get_header_uml_id(basename)} <<header>> #LightGreen',
            "{",
        ]
        
        # Show macros section if we have any macros
        if file_model.macros:
            lines.append("    -- Macros --")
            for macro in file_model.macros:
                lines.append(f"    + #define {macro}")
        
        # Show global variables section if we have any globals
        if file_model.globals:
            lines.append("    -- Global Variables --")
            for global_var in file_model.globals:
                # Format global variable properly
                if hasattr(global_var, 'value') and global_var.value is not None:
                    lines.append(f"    + {global_var.type} {global_var.name} = {global_var.value}")
                else:
                    lines.append(f"    + {global_var.type} {global_var.name}")
        
        # Show functions section - only declarations, no implementations
        if file_model.functions:
            lines.append("    -- Functions --")
            # Filter to only declarations and deduplicate
            declarations = [f for f in file_model.functions if hasattr(f, 'is_declaration') and f.is_declaration]
            unique_functions = self._deduplicate_functions(declarations)
            
            for function in unique_functions:
                # Clean up the function signature
                signature = self._format_function_signature(function)
                signature = self._clean_function_signature(signature)
                
                # Ensure it ends with semicolon for declarations
                if not signature.strip().endswith(';'):
                    signature = signature.rstrip() + ';'
                
                lines.append(f"    + {signature}")
        
        lines.append("}")
        return lines

    def _generate_external_header_class(self, basename: str) -> List[str]:
        """Generate an empty class for an external header file"""
        # Handle external headers that might come with or without .h extension
        if not basename.endswith('.h'):
            basename = f"{basename}.h"
        
        lines = [
            f'class "{basename}" as {self._get_header_uml_id(basename)} <<header>> #LightGray',
            "{",
            "}",
            "",
        ]
        return lines

    def _generate_typedef_classes(self, file_model: FileModel, project_model: ProjectModel, include_depth: int = 1) -> List[str]:
        """Generate classes for typedefs using the new PlantUML template"""
        lines = []
        seen_typedefs = set()
        
        # First, process complex typedefs from typedef_relations (these have tag names)
        for typedef_relation in file_model.typedef_relations:
            typedef_name = typedef_relation.typedef_name
            if typedef_name not in seen_typedefs:
                seen_typedefs.add(typedef_name)
                import logging
                logging.getLogger(__name__).debug(f"Processing typedef_relation for '{typedef_name}' with tag names: struct='{typedef_relation.struct_tag_name}', enum='{typedef_relation.enum_tag_name}'")
                lines.extend(self._generate_single_typedef_class(typedef_relation, file_model, project_model))
        
        # Then, process simple typedefs from the typedefs dictionary (only if not already processed)
        for typedef_name, original_type in file_model.typedefs.items():
            if typedef_name not in seen_typedefs:
                seen_typedefs.add(typedef_name)
                lines.extend(self._generate_simple_typedef_class(typedef_name, original_type, project_model))
        
        # Process typedefs from included header files (respecting include_depth)
        if include_depth > 1:
            self._process_nested_typedefs(file_model, project_model, seen_typedefs, lines, max_depth=include_depth)
        
        return lines
    
    def _find_included_file_model(self, include: str, project_model: ProjectModel):
        """Find the file model for an included file"""
        # Try different possible paths for the included file
        for relative_path, file_model in project_model.files.items():
            if (file_model.relative_path.endswith(include) or 
                file_model.relative_path == include or
                relative_path.endswith(include)):
                return file_model
        return None
    
    def _generate_simple_typedef_class(self, typedef_name: str, original_type: str, project_model: ProjectModel = None) -> List[str]:
        """Generate a class for a simple typedef"""
        lines = []
        
        if original_type == "enum":
            # For enum typedefs, create an enum class with values
            lines.append(f'enum "{typedef_name}" as {self._get_typedef_uml_id(typedef_name)} <<typedef>> #LightYellow')
            lines.append("{")
            
            # Try to find the enum values from the project model
            if project_model:
                found_enum = None
                # Look for the enum by the typedef name or with _tag suffix
                for f_model in project_model.files.values():
                    if typedef_name in f_model.enums:
                        found_enum = f_model.enums[typedef_name]
                        break
                    elif f"{typedef_name}_tag" in f_model.enums:
                        found_enum = f_model.enums[f"{typedef_name}_tag"]
                        break
                
                if found_enum:
                    for value in found_enum.values:
                        if value.value is not None:
                            lines.append(f"    {value.name} = {value.value}")
                        else:
                            lines.append(f"    {value.name}")
                else:
                    lines.append(f"    + {original_type}")
            else:
                lines.append(f"    + {original_type}")
            lines.append("}")
        else:
            # For non-enum typedefs, create a regular class
            lines.append(f'class "{typedef_name}" as {self._get_typedef_uml_id(typedef_name)} <<typedef>> #LightYellow')
            lines.append("{")
            
            # For struct/union typedefs, try to show fields
            if original_type == "struct":
                # Try to find the struct in the project model
                if project_model:
                    found_struct = None
                    # Try multiple possible struct names
                    possible_struct_names = [typedef_name]
                    if typedef_name.endswith('_t'):
                        possible_struct_names.append(typedef_name[:-2])  # Remove "_t" suffix
                        possible_struct_names.append(f"{typedef_name[:-2]}_tag")  # Add _tag suffix to base name
                    possible_struct_names.append(f"{typedef_name}_tag")
                    # Also try the typedef name itself (in case parser stored it that way)
                    if typedef_name not in possible_struct_names:
                        possible_struct_names.append(typedef_name)
                    
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.debug(f"Looking for struct '{typedef_name}' with possible names: {possible_struct_names}")
                    
                    for f_model in project_model.files.values():
                        logger.debug(f"Checking file '{f_model.file_path}' for structs: {list(f_model.structs.keys())}")
                        for name in possible_struct_names:
                            if name in f_model.structs:
                                found_struct = f_model.structs[name]
                                logger.debug(f"Found struct '{name}' in file '{f_model.file_path}'")
                                break
                        if found_struct:
                            break
                    
                    if found_struct:
                        for field in found_struct.fields:
                            lines.append(f"    + {field.type} {field.name}")
                    else:
                        lines.append(f"    + {original_type}")
                else:
                    lines.append(f"    + {original_type}")
            elif original_type == "union":
                # Try to find the union in the project model
                if project_model:
                    found_union = None
                    for f_model in project_model.files.values():
                        if typedef_name in f_model.unions:
                            found_union = f_model.unions[typedef_name]
                            break
                    
                    if found_union:
                        for field in found_union.fields:
                            lines.append(f"    + {field.type} {field.name}")
                    else:
                        lines.append(f"    + {original_type}")
                else:
                    lines.append(f"    + {original_type}")
            else:
                lines.append(f"    + {original_type}")
            lines.append("}")
        
        lines.append("")
        return lines
    
    def _generate_single_typedef_class(self, typedef_relation, file_model: FileModel, project_model: ProjectModel) -> List[str]:
        """Generate a single typedef class"""
        lines = []
        typedef_name = typedef_relation.typedef_name
        original_type = typedef_relation.original_type
        relationship_type = typedef_relation.relationship_type
        
        if original_type == "enum":
            # For enum typedefs, create an enum class with values
            lines.append(f'enum "{typedef_name}" as {self._get_typedef_uml_id(typedef_name)} <<typedef>> #LightYellow')
            lines.append("{")
            
            # Try to find the enum by the typedef name first, then by the enum tag name
            enum_name = typedef_name
            if not any(enum_name in f_model.enums for f_model in project_model.files.values()):
                # If typedef name not found, try the enum tag name
                if hasattr(typedef_relation, 'enum_tag_name') and typedef_relation.enum_tag_name:
                    enum_name = typedef_relation.enum_tag_name
            # Look for the enum in the project model
            found_enum = None
            import logging
            logging.getLogger(__name__).debug(f"Looking for enum '{enum_name}' in project model")
            for f_model in project_model.files.values():
                if enum_name in f_model.enums:
                    found_enum = f_model.enums[enum_name]
                    logging.getLogger(__name__).debug(f"Found enum '{enum_name}' in file '{f_model.file_path}'")
                    break
            
            if found_enum:
                for value in found_enum.values:
                    if value.value is not None:
                        lines.append(f"    {value.name} = {value.value}")
                    else:
                        lines.append(f"    {value.name}")
            else:
                logging.getLogger(__name__).debug(f"Enum '{enum_name}' not found in project model")
                lines.append(f"    + {original_type}")
        else:
            # For non-enum typedefs, create a regular class
            lines.append(f'class "{typedef_name}" as {self._get_typedef_uml_id(typedef_name)} <<typedef>> #LightYellow')
            lines.append("{")
            
            # For struct/union typedefs, show fields/values
            if original_type in ["struct", "union"]:
                if original_type == "struct":
                    # Try to find the struct by the typedef name first, then by the struct tag name
                    import logging
                    logging.getLogger(__name__).debug(f"typedef_relation.struct_tag_name: '{typedef_relation.struct_tag_name}', typedef_name: '{typedef_name}'")
                    
                    # Try multiple possible struct names, starting with typedef name
                    possible_struct_names = [typedef_name]
                    if typedef_relation.struct_tag_name:
                        possible_struct_names.append(typedef_relation.struct_tag_name)
                    if typedef_name.endswith('_t'):
                        possible_struct_names.append(typedef_name[:-2])  # Remove "_t" suffix
                    if typedef_relation.struct_tag_name and typedef_relation.struct_tag_name.endswith('_tag'):
                        possible_struct_names.append(typedef_relation.struct_tag_name[:-4])  # Remove "_tag" suffix
                    # Also try adding "_tag" suffix to the typedef name
                    if not typedef_name.endswith('_tag'):
                        possible_struct_names.append(f"{typedef_name}_tag")
                    
                    logging.getLogger(__name__).debug(f"Looking for struct with possible names: {possible_struct_names} in file '{file_model.file_path}', available structs: {list(file_model.structs.keys())}")
                    
                    found_struct = None
                    for name in possible_struct_names:
                        if name in file_model.structs:
                            found_struct = file_model.structs[name]
                            logging.getLogger(__name__).debug(f"Found struct '{name}' in file '{file_model.file_path}'")
                            break
                    
                    if found_struct:
                        for field in found_struct.fields:
                            lines.append(f"    + {field.type} {field.name}")
                    else:
                        # Try to find the struct in the project model
                        for f_model in project_model.files.values():
                            for name in possible_struct_names:
                                if name in f_model.structs:
                                    found_struct = f_model.structs[name]
                                    logging.getLogger(__name__).debug(f"Found struct '{name}' in file '{f_model.file_path}'")
                                    break
                            if found_struct:
                                break
                        
                        if found_struct:
                            for field in found_struct.fields:
                                lines.append(f"    + {field.type} {field.name}")
                        else:
                            lines.append(f"    + {original_type}")
                elif original_type == "union":
                    # Try to find the union by the typedef name
                    if typedef_name in file_model.unions:
                        union = file_model.unions[typedef_name]
                        for field in union.fields:
                            lines.append(f"    + {field.type} {field.name}")
                    else:
                        # Try to find the union in the project model
                        found_union = None
                        for f_model in project_model.files.values():
                            if typedef_name in f_model.unions:
                                found_union = f_model.unions[typedef_name]
                                break
                        
                        if found_union:
                            for field in found_union.fields:
                                lines.append(f"    + {field.type} {field.name}")
                        else:
                            lines.append(f"    + {original_type}")
                else:
                    lines.append(f"    + {original_type}")
            else:
                lines.append(f"    + {original_type}")
        
        lines.append("}")
        lines.append("")
        return lines

    def _build_include_hierarchy(self, file_model: FileModel, project_model: ProjectModel) -> set:
        """Build the complete include hierarchy starting from the root file"""
        hierarchy = set()
        visited_files = set()
        
        def add_to_hierarchy(file_path: str, depth: int = 0, max_depth: int = 10):
            if depth >= max_depth or file_path in visited_files:
                return
            
            visited_files.add(file_path)
            
            # Find the file model
            file_model_to_process = None
            for key, model in project_model.files.items():
                if model.file_path == file_path:
                    file_model_to_process = model
                    break
            
            if not file_model_to_process:
                return
            
            # Add this file to hierarchy
            hierarchy.add(Path(file_path).stem)
            
            # Process includes recursively
            for include_relation in file_model_to_process.include_relations:
                included_file_path = include_relation.included_file
                add_to_hierarchy(included_file_path, depth + 1, max_depth)
            
            # Process direct includes
            for include_name in file_model_to_process.includes:
                included_file_path = self._find_included_file(
                    include_name, file_model_to_process.project_root, project_model
                )
                if included_file_path and not included_file_path.startswith("EXTERNAL:"):
                    add_to_hierarchy(included_file_path, depth + 1, max_depth)
        
        # Start from the root file
        add_to_hierarchy(file_model.file_path)
        return hierarchy

    def _collect_referenced_typedefs(self, file_model: FileModel, project_model: ProjectModel, include_hierarchy: set) -> set:
        """Collect all typedef names that are referenced in relationships"""
        referenced_typedefs = set()
        
        # Collect typedefs from the current file's relationships
        for typedef_name, original_type in file_model.typedefs.items():
            referenced_typedefs.add(typedef_name)
        
        for typedef_relation in file_model.typedef_relations:
            referenced_typedefs.add(typedef_relation.typedef_name)
        
        # Collect typedefs from included files that are in the include hierarchy
        self._collect_nested_referenced_typedefs(file_model, project_model, referenced_typedefs, include_hierarchy)
        
        return referenced_typedefs

    def _collect_nested_referenced_typedefs(self, file_model: FileModel, project_model: ProjectModel, referenced_typedefs: set, include_hierarchy: set, visited_files: set = None, depth: int = 0, max_depth: int = 3) -> None:
        """Recursively collect typedef names from included files that are in the include hierarchy"""
        if visited_files is None:
            visited_files = set()
        
        # Prevent infinite recursion and respect max_depth
        if depth >= max_depth or file_model.file_path in visited_files:
            return
        
        visited_files.add(file_model.file_path)
        
        # Process each include in the current file
        for include in file_model.includes:
            # Find the included file model
            included_file_model = self._find_included_file_model(include, project_model)
            if included_file_model and included_file_model.file_path.endswith('.h'):
                # Check if this included file is in the include hierarchy
                included_file_basename = Path(included_file_model.file_path).stem
                if include_hierarchy and included_file_basename not in include_hierarchy:
                    continue
                
                # Add typedefs from this included file
                for typedef_name, original_type in included_file_model.typedefs.items():
                    referenced_typedefs.add(typedef_name)
                
                for typedef_relation in included_file_model.typedef_relations:
                    referenced_typedefs.add(typedef_relation.typedef_name)
                
                # Recursively process further nested includes
                self._collect_nested_referenced_typedefs(included_file_model, project_model, referenced_typedefs, include_hierarchy, visited_files, depth + 1, max_depth)

    def _generate_typedef_classes_with_references(self, file_model: FileModel, project_model: ProjectModel, include_depth: int, referenced_typedefs: set) -> List[str]:
        """Generate typedef classes including all referenced typedefs"""
        lines = []
        seen_typedefs = set()
        
        # First, process complex typedefs from typedef_relations (these have tag names)
        for typedef_relation in file_model.typedef_relations:
            typedef_name = typedef_relation.typedef_name
            if typedef_name not in seen_typedefs:
                seen_typedefs.add(typedef_name)
                import logging
                logging.getLogger(__name__).debug(f"Processing typedef_relation for '{typedef_name}' with tag names: struct='{typedef_relation.struct_tag_name}', enum='{typedef_relation.enum_tag_name}'")
                lines.extend(self._generate_single_typedef_class(typedef_relation, file_model, project_model))
        
        # Then, process simple typedefs from the typedefs dictionary (only if not already processed)
        for typedef_name, original_type in file_model.typedefs.items():
            if typedef_name not in seen_typedefs:
                seen_typedefs.add(typedef_name)
                lines.extend(self._generate_simple_typedef_class(typedef_name, original_type, project_model))
        
        # Process typedefs from included header files (respecting include_depth)
        if include_depth > 1:
            self._process_nested_typedefs(file_model, project_model, seen_typedefs, lines, max_depth=include_depth)
        
        # Add any referenced typedefs that weren't already processed
        for typedef_name in referenced_typedefs:
            if typedef_name not in seen_typedefs:
                seen_typedefs.add(typedef_name)
                # Try to find the typedef definition in the project model
                typedef_found = False
                
                # Look for simple typedefs
                for f_model in project_model.files.values():
                    if typedef_name in f_model.typedefs:
                        lines.extend(self._generate_simple_typedef_class(typedef_name, f_model.typedefs[typedef_name], project_model))
                        typedef_found = True
                        break
                
                # Look for complex typedefs (typedef_relations)
                if not typedef_found:
                    for f_model in project_model.files.values():
                        for typedef_relation in f_model.typedef_relations:
                            if typedef_relation.typedef_name == typedef_name:
                                lines.extend(self._generate_single_typedef_class(typedef_relation, f_model, project_model))
                                typedef_found = True
                                break
                        if typedef_found:
                            break
                
                # If still not found, create a placeholder typedef class
                if not typedef_found:
                    lines.extend(self._generate_simple_typedef_class(typedef_name, "unknown", project_model))
        
        return lines

    def _collect_referenced_headers(self, file_model: FileModel, project_model: ProjectModel, include_hierarchy: set) -> set:
        """Collect all header names that are referenced in relationships"""
        referenced_headers = set()
        
        # Collect headers from the current file's relationships
        for include in file_model.includes:
            included_file_model = self._find_included_file_model(include, project_model)
            if included_file_model and included_file_model.file_path.endswith('.h'):
                referenced_headers.add(Path(included_file_model.file_path).stem)
            else:
                # External header
                referenced_headers.add(include)
        
        # Collect headers from included files that are in the include hierarchy
        self._collect_nested_referenced_headers(file_model, project_model, referenced_headers, include_hierarchy)
        
        # Also collect headers that are referenced by other headers in the hierarchy
        self._collect_indirect_referenced_headers(file_model, project_model, referenced_headers, include_hierarchy)
        
        return referenced_headers

    def _collect_nested_referenced_headers(self, file_model: FileModel, project_model: ProjectModel, referenced_headers: set, include_hierarchy: set, visited_files: set = None, depth: int = 0, max_depth: int = 3) -> None:
        """Recursively collect header names from included files that are in the include hierarchy"""
        if visited_files is None:
            visited_files = set()
        
        # Prevent infinite recursion and respect max_depth
        if depth >= max_depth or file_model.file_path in visited_files:
            return
        
        visited_files.add(file_model.file_path)
        
        # Process each include in the current file
        for include in file_model.includes:
            # Find the included file model
            included_file_model = self._find_included_file_model(include, project_model)
            if included_file_model and included_file_model.file_path.endswith('.h'):
                # Check if this included file is in the include hierarchy
                included_file_basename = Path(included_file_model.file_path).stem
                if include_hierarchy and included_file_basename not in include_hierarchy:
                    continue
                
                # Add this header
                referenced_headers.add(included_file_basename)
                
                # Recursively process further nested includes
                self._collect_nested_referenced_headers(included_file_model, project_model, referenced_headers, include_hierarchy, visited_files, depth + 1, max_depth)

    def _collect_indirect_referenced_headers(self, file_model: FileModel, project_model: ProjectModel, referenced_headers: set, include_hierarchy: set, visited_files: set = None, depth: int = 0, max_depth: int = 3) -> None:
        """Collect headers that are referenced by other headers in the hierarchy"""
        if visited_files is None:
            visited_files = set()
        
        # Prevent infinite recursion and respect max_depth
        if depth >= max_depth or file_model.file_path in visited_files:
            return
        
        visited_files.add(file_model.file_path)
        
        # Process each include in the current file
        for include in file_model.includes:
            # Find the included file model
            included_file_model = self._find_included_file_model(include, project_model)
            if included_file_model and included_file_model.file_path.endswith('.h'):
                # Check if this included file is in the include hierarchy
                included_file_basename = Path(included_file_model.file_path).stem
                if include_hierarchy and included_file_basename not in include_hierarchy:
                    continue
                
                # Add all includes from this header file
                for nested_include in included_file_model.includes:
                    nested_included_file_model = self._find_included_file_model(nested_include, project_model)
                    if nested_included_file_model and nested_included_file_model.file_path.endswith('.h'):
                        referenced_headers.add(Path(nested_included_file_model.file_path).stem)
                    else:
                        # External header
                        referenced_headers.add(nested_include)
                
                # Recursively process further nested includes
                self._collect_indirect_referenced_headers(included_file_model, project_model, referenced_headers, include_hierarchy, visited_files, depth + 1, max_depth)

    def _generate_header_classes_with_references(self, file_model: FileModel, project_model: ProjectModel, include_depth: int, referenced_headers: set) -> List[str]:
        """Generate header classes including all referenced headers"""
        lines = []
        seen_headers = set()
        
        # First, process headers from the current file
        for include in file_model.includes:
            included_file_model = self._find_included_file_model(include, project_model)
            if included_file_model and included_file_model.file_path.endswith('.h'):
                header_basename = Path(included_file_model.file_path).stem
                if header_basename not in seen_headers:
                    seen_headers.add(header_basename)
                    lines.extend(self._generate_header_class(included_file_model, header_basename))
            else:
                # External header
                if include not in seen_headers:
                    seen_headers.add(include)
                    lines.extend(self._generate_external_header_class(include))
        
        # Process headers from included header files (respecting include_depth)
        if include_depth > 1:
            self._process_nested_includes(file_model, project_model, seen_headers, lines, max_depth=include_depth)
        
        # Add any referenced headers that weren't already processed
        for header_name in referenced_headers:
            if header_name not in seen_headers:
                seen_headers.add(header_name)
                # Try to find the header file in the project model
                header_found = False
                
                for f_model in project_model.files.values():
                    if f_model.file_path.endswith('.h') and Path(f_model.file_path).stem == header_name:
                        lines.extend(self._generate_header_class(f_model, header_name))
                        header_found = True
                        break
                
                # If not found, create an external header class
                if not header_found:
                    lines.extend(self._generate_external_header_class(header_name))
        
        return lines

    def _generate_relationships(
        self, file_model: FileModel, project_model: ProjectModel
    ) -> List[str]:
        """Generate relationships between classes using the new PlantUML template"""
        lines = []
        seen_relationships = set()
        
        # Build the include hierarchy from the root file
        include_hierarchy = self._build_include_hierarchy(file_model, project_model)
        
        # Track which headers are actually included in this diagram
        included_headers = set()
        
        # Add direct includes from the current file
        for include_name in file_model.includes:
            included_file_path = self._find_included_file(
                include_name, file_model.project_root, project_model
            )
            if included_file_path and included_file_path.startswith("EXTERNAL:"):
                external_header_name = included_file_path.split(":", 1)[1]
                if not external_header_name.endswith('.h'):
                    external_header_name = f"{external_header_name}.h"
                included_headers.add(external_header_name)
            else:
                # Find the actual header file
                for key, model in project_model.files.items():
                    if model.file_path == included_file_path:
                        header_basename = Path(model.file_path).stem
                        included_headers.add(header_basename)
                        break
        
        # Add headers from include_relations
        for include_relation in file_model.include_relations:
            included_file_path = include_relation.included_file
            for key, model in project_model.files.items():
                if model.file_path == included_file_path:
                    header_basename = Path(model.file_path).stem
                    included_headers.add(header_basename)
                    break
        
        # Add external headers that are included by project headers
        for include_relation in file_model.include_relations:
            included_file_path = include_relation.included_file
            for key, model in project_model.files.items():
                if model.file_path == included_file_path:
                    # This is a project header, check its includes
                    for include_name in model.includes:
                        nested_included_file_path = self._find_included_file(
                            include_name, model.project_root, project_model
                        )
                        if nested_included_file_path and nested_included_file_path.startswith("EXTERNAL:"):
                            external_header_name = nested_included_file_path.split(":", 1)[1]
                            if not external_header_name.endswith('.h'):
                                external_header_name = f"{external_header_name}.h"
                            included_headers.add(external_header_name)
                        else:
                            # This is a project header, add it to included_headers
                            for key2, model2 in project_model.files.items():
                                if model2.file_path == nested_included_file_path:
                                    nested_header_basename = Path(model2.file_path).stem
                                    included_headers.add(nested_header_basename)
                                    break
                    break
        
        # Process direct includes from the current file
        for include_name in file_model.includes:
            included_file_path = self._find_included_file(
                include_name, file_model.project_root, project_model
            )
            
            # Check if this is an external header
            if included_file_path and included_file_path.startswith("EXTERNAL:"):
                # This is an external header
                external_header_name = included_file_path.split(":", 1)[1]
                # Ensure external header has .h extension for consistency
                if not external_header_name.endswith('.h'):
                    external_header_name = f"{external_header_name}.h"
                
                # Use appropriate UML ID method based on file type
                is_header = file_model.file_path.endswith('.h')
                if is_header:
                    source_class = self._get_header_uml_id(Path(file_model.file_path).stem)
                else:
                    source_class = self._get_uml_id(Path(file_model.file_path).stem)
                target_class = self._get_header_uml_id(external_header_name)
                
                # Check if this relationship was already added
                relationship_id = f"{Path(file_model.file_path).stem}->{external_header_name}:include"
                if relationship_id not in seen_relationships:
                    seen_relationships.add(relationship_id)
                    lines.append(f"{source_class} --> {target_class} : <<include>>")
            else:
                # This is a project header
                for key, model in project_model.files.items():
                    if model.file_path == included_file_path:
                        included_file_model = model
                        break
                # Skip self-include
                if included_file_model and included_file_model.file_path == file_model.file_path:
                    continue
                if included_file_model:
                    header_basename = Path(included_file_path).stem
                    # Use appropriate UML ID method based on file type
                    is_header = file_model.file_path.endswith('.h')
                    if is_header:
                        source_class = self._get_header_uml_id(Path(file_model.file_path).stem)
                    else:
                        source_class = self._get_uml_id(Path(file_model.file_path).stem)
                    target_class = self._get_header_uml_id(header_basename)
                    
                    # Check if this relationship was already added
                    relationship_id = f"{Path(file_model.file_path).stem}->{header_basename}:include"
                    if relationship_id not in seen_relationships:
                        seen_relationships.add(relationship_id)
                        lines.append(f"{source_class} --> {target_class} : <<include>>")
        
        # Process direct include relationships from include_relations (for header-to-header relationships)
        for include_relation in file_model.include_relations:
            included_file_path = include_relation.included_file
            
            # Find the included file model
            included_file_model = None
            for key, model in project_model.files.items():
                if model.file_path == included_file_path:
                    included_file_model = model
                    break
            
            if included_file_model:
                source_basename = Path(file_model.file_path).stem
                target_basename = Path(included_file_path).stem
                
                # Skip self-include
                if source_basename == target_basename:
                    continue
                
                # Use appropriate UML ID method based on file type
                is_header = file_model.file_path.endswith('.h')
                if is_header:
                    source_class = self._get_header_uml_id(source_basename)
                else:
                    source_class = self._get_uml_id(source_basename)
                target_class = self._get_header_uml_id(target_basename)
                
                # Check if this relationship was already added
                relationship_id = f"{source_basename}->{target_basename}:include"
                if relationship_id not in seen_relationships:
                    seen_relationships.add(relationship_id)
                    lines.append(f"{source_class} --> {target_class} : <<include>>")
        
        # Process relationships between included headers (only for headers that are in this diagram)
        for include_relation in file_model.include_relations:
            included_file_path = include_relation.included_file
            included_file_model = None
            
            # Find the included file model
            for key, model in project_model.files.items():
                if model.file_path == included_file_path:
                    included_file_model = model
                    break
            
            if included_file_model:
                # Process direct includes from the included file (only if they're in our diagram)
                for include_name in included_file_model.includes:
                    nested_included_file_path = self._find_included_file(
                        include_name, included_file_model.project_root, project_model
                    )
                    
                    if nested_included_file_path and nested_included_file_path.startswith("EXTERNAL:"):
                        # External header
                        external_header_name = nested_included_file_path.split(":", 1)[1]
                        if not external_header_name.endswith('.h'):
                            external_header_name = f"{external_header_name}.h"
                        
                        source_basename = Path(included_file_model.file_path).stem
                        source_class = self._get_header_uml_id(source_basename)
                        target_class = self._get_header_uml_id(external_header_name)
                        
                        # Only add if both source and target are in our diagram
                        if source_basename in included_headers and external_header_name in included_headers:
                            relationship_id = f"{source_basename}->{external_header_name}:include"
                            if relationship_id not in seen_relationships:
                                seen_relationships.add(relationship_id)
                                lines.append(f"{source_class} --> {target_class} : <<include>>")
                    else:
                        # Project header
                        for key, model in project_model.files.items():
                            if model.file_path == nested_included_file_path:
                                nested_header_basename = Path(model.file_path).stem
                                source_basename = Path(included_file_model.file_path).stem
                                
                                # Only add if both source and target are in our diagram
                                if source_basename in included_headers and nested_header_basename in included_headers:
                                    source_class = self._get_header_uml_id(source_basename)
                                    target_class = self._get_header_uml_id(nested_header_basename)
                                    
                                    relationship_id = f"{source_basename}->{nested_header_basename}:include"
                                    if relationship_id not in seen_relationships:
                                        seen_relationships.add(relationship_id)
                                        lines.append(f"{source_class} --> {target_class} : <<include>>")
                                break
                
                # Also process include_relations from the included file (transitive includes)
                for nested_include_relation in included_file_model.include_relations:
                    nested_included_file_path = nested_include_relation.included_file
                    
                    # Find the nested included file model
                    nested_included_file_model = None
                    for key, model in project_model.files.items():
                        if model.file_path == nested_included_file_path:
                            nested_included_file_model = model
                            break
                    
                    if nested_included_file_model:
                        source_basename = Path(included_file_model.file_path).stem
                        target_basename = Path(nested_included_file_path).stem
                        
                        # Only add if both source and target are in our diagram
                        if source_basename in included_headers and target_basename in included_headers:
                            source_class = self._get_header_uml_id(source_basename)
                            target_class = self._get_header_uml_id(target_basename)
                            
                            relationship_id = f"{source_basename}->{target_basename}:include"
                            if relationship_id not in seen_relationships:
                                seen_relationships.add(relationship_id)
                                lines.append(f"{source_class} --> {target_class} : <<include>>")

        # Process direct includes from all header files that are in the diagram
        # This captures relationships that might be missed by the above processing
        for key, model in project_model.files.items():
            if model.file_path.endswith('.h'):
                header_basename = Path(model.file_path).stem
                # Only process headers that are actually in our diagram
                if header_basename in included_headers:
                    # Process direct includes from this header
                    for include_name in model.includes:
                        included_file_path = self._find_included_file(
                            include_name, model.project_root, project_model
                        )
                        
                        if included_file_path and included_file_path.startswith("EXTERNAL:"):
                            # External header
                            external_header_name = included_file_path.split(":", 1)[1]
                            if not external_header_name.endswith('.h'):
                                external_header_name = f"{external_header_name}.h"
                            
                            source_class = self._get_header_uml_id(header_basename)
                            target_class = self._get_header_uml_id(external_header_name)
                            
                            # Add the relationship if the external header is in our diagram
                            if external_header_name in included_headers:
                                relationship_id = f"{header_basename}->{external_header_name}:include"
                                if relationship_id not in seen_relationships:
                                    seen_relationships.add(relationship_id)
                                    lines.append(f"{source_class} --> {target_class} : <<include>>")
                        else:
                            # Project header
                            for key2, model2 in project_model.files.items():
                                if model2.file_path == included_file_path:
                                    included_header_basename = Path(model2.file_path).stem
                                    
                                    # Skip self-include
                                    if header_basename == included_header_basename:
                                        break
                                    
                                    # Add the relationship if the included header is in our diagram
                                    if included_header_basename in included_headers:
                                        source_class = self._get_header_uml_id(header_basename)
                                        target_class = self._get_header_uml_id(included_header_basename)
                                        
                                        relationship_id = f"{header_basename}->{included_header_basename}:include"
                                        if relationship_id not in seen_relationships:
                                            seen_relationships.add(relationship_id)
                                            lines.append(f"{source_class} --> {target_class} : <<include>>")
                                    break

        # Typedef relationships - process typedefs from current file and included files
        # Use the same seen_relationships set to avoid duplicates
        
        # Process typedefs from current file
        for typedef_relation in file_model.typedef_relations:
            self._process_typedef_relationships(typedef_relation, file_model, project_model, lines, seen_relationships)
        
        # Process typedefs from included header files
        for include_relation in file_model.include_relations:
            included_file_path = include_relation.included_file
            included_file_model = None
            for key, model in project_model.files.items():
                if model.file_path == included_file_path:
                    included_file_model = model
                    break
            if included_file_model:
                for typedef_relation in included_file_model.typedef_relations:
                    self._process_typedef_relationships(typedef_relation, included_file_model, project_model, lines, seen_relationships)
        
        # Process type dependencies and macro dependencies
        self._process_type_dependencies(file_model, project_model, lines, seen_relationships)
        
        return lines

    def _process_typedef_relationships(self, typedef_relation, file_model: FileModel, project_model: ProjectModel, lines: List[str], seen_relationships: set):
        """Process relationships for a single typedef"""
        typedef_name = typedef_relation.typedef_name
        original_type = typedef_relation.original_type
        relationship_type = typedef_relation.relationship_type
        
        # Create a unique identifier for this typedef relation to avoid duplicates
        relation_id = f"{file_model.file_path}:{typedef_name}:declares"
        if relation_id in seen_relationships:
            return
        seen_relationships.add(relation_id)
        
        # Show a 'declares' relation from the file that defines the typedef
        file_basename = Path(file_model.file_path).stem
        main_class_id = self._get_uml_id(file_basename)
        header_class_id = self._get_header_uml_id(file_basename)
        
        # Only add the relationship if the typedef class exists in the diagram
        typedef_class_id = self._get_typedef_uml_id(typedef_name)
        
        # Determine which file actually defines this typedef
        # If the typedef_relation is from the current file_model, it's defined in the current file
        # If it's from an included file, it's defined in the header
        current_file_typedefs = {tr.typedef_name for tr in file_model.typedef_relations}
        
        if typedef_name in current_file_typedefs:
            # Typedef is defined in the current file (could be .c or .h)
            if file_model.file_path.endswith('.h'):
                # Typedef is defined in header file
                lines.append(f"{header_class_id} ..> {typedef_class_id} : <<declares>>")
            else:
                # Typedef is defined in source file
                lines.append(f"{main_class_id} ..> {typedef_class_id} : <<declares>>")
        else:
            # Typedef is from an included header file
            lines.append(f"{header_class_id} ..> {typedef_class_id} : <<declares>>")
        
        # For complex typedefs, show the 'defines' relation from the typedef class to the type class
        if relationship_type == "defines":
            if original_type in ("struct", "enum", "union"):
                # For struct/enum/union typedefs, don't create a relationship to a non-existent type class
                # since the fields/values are already shown in the typedef class itself
                pass

        # Check for relationships between typedefs (when one typedef uses another)
        if relationship_type == "defines" and original_type == "struct":
            # Look for the struct definition to find typedef dependencies
            struct_name = typedef_relation.struct_tag_name if typedef_relation.struct_tag_name else typedef_name
            if struct_name in file_model.structs:
                struct = file_model.structs[struct_name]
                for field in struct.fields:
                    # Check if the field type is a typedef
                    field_type = field.type
                    # Remove array notation for checking
                    if '[' in field_type:
                        field_type = field_type[:field_type.index('[')]
                    # Remove pointer notation for checking
                    if field_type.endswith('*'):
                        field_type = field_type[:-1].strip()
                    
                    # Check if this field type is a typedef in the project
                    for key, model in project_model.files.items():
                        for other_typedef_relation in model.typedef_relations:
                            if other_typedef_relation.typedef_name == field_type:
                                other_typedef_class_id = self._get_typedef_uml_id(field_type)
                                relationship_id = f"{typedef_name}->{field_type}:uses"
                                if relationship_id not in seen_relationships:
                                    seen_relationships.add(relationship_id)
                                    lines.append(f"{typedef_class_id} --> {other_typedef_class_id} : <<uses>>")
        
        # Show which header declares this typedef (for typedefs from included files)
        # Find which header actually declares this typedef
        for key, model in project_model.files.items():
            for other_typedef_relation in model.typedef_relations:
                if other_typedef_relation.typedef_name == typedef_name:
                    # This typedef is declared in this model
                    if model.file_path != file_model.file_path:
                        # It's declared in a different file
                        header_class_id = self._get_header_uml_id(Path(model.file_path).stem)
                        typedef_class_id = self._get_typedef_uml_id(typedef_name)
                        relationship_id = f"{Path(model.file_path).stem}->{typedef_name}:declares"
                        if relationship_id not in seen_relationships:
                            seen_relationships.add(relationship_id)
                            lines.append(f"{header_class_id} ..> {typedef_class_id} : <<declares>>")
        
        # Also show which header declares typedefs that are used in the current file
        # This helps show the relationship between headers and the typedefs they provide
        if file_model.file_path.endswith('.c'):
            # For source files, show which headers declare the typedefs they use
            for include_relation in file_model.include_relations:
                included_file_path = include_relation.included_file
                included_file_model = None
                for key, model in project_model.files.items():
                    if model.file_path == included_file_path:
                        included_file_model = model
                        break
                if included_file_model:
                    for other_typedef_relation in included_file_model.typedef_relations:
                        header_class_id = self._get_header_uml_id(Path(included_file_model.file_path).stem)
                        typedef_class_id = self._get_typedef_uml_id(other_typedef_relation.typedef_name)
                        relationship_id = f"{Path(included_file_model.file_path).stem}->{other_typedef_relation.typedef_name}:declares"
                        if relationship_id not in seen_relationships:
                            seen_relationships.add(relationship_id)
                            lines.append(f"{header_class_id} ..> {typedef_class_id} : <<declares>>")

    def _process_type_dependencies(self, file_model: FileModel, project_model: ProjectModel, lines: List[str], seen_relationships: set):
        """Process type dependencies and macro dependencies"""
        # Process typedefs from current file and included files
        all_typedefs = []
        
        # Add typedefs from current file
        for typedef_relation in file_model.typedef_relations:
            all_typedefs.append((typedef_relation, file_model))
        
        # Add typedefs from included files
        for include_relation in file_model.include_relations:
            included_file_path = include_relation.included_file
            included_file_model = None
            for key, model in project_model.files.items():
                if model.file_path == included_file_path:
                    included_file_model = model
                    break
            if included_file_model:
                for typedef_relation in included_file_model.typedef_relations:
                    all_typedefs.append((typedef_relation, included_file_model))
        
        # Process each typedef for dependencies
        for typedef_relation, typedef_file_model in all_typedefs:
            if typedef_relation.relationship_type == "defines" and typedef_relation.original_type == "struct":
                # Look for struct definition to find field dependencies
                struct_name = typedef_relation.struct_tag_name if typedef_relation.struct_tag_name else typedef_relation.typedef_name
                if struct_name in typedef_file_model.structs:
                    struct = typedef_file_model.structs[struct_name]
                    for field in struct.fields:
                        self._process_field_dependencies(field, typedef_relation, typedef_file_model, project_model, lines, seen_relationships)
        
        # Process macro dependencies
        self._process_macro_dependencies(file_model, project_model, lines, seen_relationships)

    def _process_field_dependencies(self, field, typedef_relation, typedef_file_model: FileModel, project_model: ProjectModel, lines: List[str], seen_relationships: set):
        """Process dependencies for a struct field"""
        field_type = field.type
        
        # Remove array notation for checking
        if '[' in field_type:
            field_type = field_type[:field_type.index('[')]
        # Remove pointer notation for checking
        if field_type.endswith('*'):
            field_type = field_type[:-1].strip()
        
        # Check if this field type is a typedef in the project
        # Note: We skip this check here because it's already handled in _process_typedef_relationships
        # to avoid duplicate "uses" relationships
        
        # Check for macro usage in field type (e.g., MAX_LABEL_LEN)
        if 'MAX_LABEL_LEN' in field.type:
            # Find which header defines MAX_LABEL_LEN
            for key, model in project_model.files.items():
                if 'MAX_LABEL_LEN' in model.macros:
                    typedef_class_id = self._get_typedef_uml_id(typedef_relation.typedef_name)
                    header_class_id = self._get_header_uml_id(Path(model.file_path).stem)
                    
                    # Create a unique identifier for this relationship
                    relationship_id = f"{typedef_relation.typedef_name}->{Path(model.file_path).stem}:macro"
                    if relationship_id not in seen_relationships:
                        seen_relationships.add(relationship_id)
                        lines.append(f"{typedef_class_id} ..> {header_class_id} : <<uses>> MAX_LABEL_LEN")
                    break

    def _process_macro_dependencies(self, file_model: FileModel, project_model: ProjectModel, lines: List[str], seen_relationships: set):
        """Process macro dependencies between files"""
        # Check for macro usage in the current file
        for macro in file_model.macros:
            # Check if this macro is used in other files
            for key, model in project_model.files.items():
                if model.file_path != file_model.file_path:
                    # Check if the macro is used in typedefs, functions, or globals
                    for typedef_relation in model.typedef_relations:
                        if typedef_relation.relationship_type == "defines" and typedef_relation.original_type == "struct":
                            struct_name = typedef_relation.struct_tag_name if typedef_relation.struct_tag_name else typedef_relation.typedef_name
                            if struct_name in model.structs:
                                struct = model.structs[struct_name]
                                for field in struct.fields:
                                    if macro in field.type:
                                        # Create relationship showing macro usage
                                        typedef_class_id = self._get_typedef_uml_id(typedef_relation.typedef_name)
                                        header_class_id = self._get_header_uml_id(Path(file_model.file_path).stem)
                                        
                                        relationship_id = f"{typedef_relation.typedef_name}->{Path(file_model.file_path).stem}:{macro}"
                                        if relationship_id not in seen_relationships:
                                            seen_relationships.add(relationship_id)
                                            lines.append(f"{typedef_class_id} ..> {header_class_id} : <<uses>> {macro}")

    def _find_included_file(
        self, include_name: str, project_root: str, project_model: ProjectModel
    ) -> Optional[str]:
        """Find the actual file path for an include"""
        # Common include paths to search
        search_paths = [
            Path(project_root),
            Path(project_root) / "include",
            Path(project_root) / "src",
            Path(project_root) / "lib",
            Path(project_root) / "headers",
        ]

        # Try different extensions
        extensions = [".h", ".hpp", ".hxx", ""]

        for search_path in search_paths:
            if not search_path.exists():
                continue

            for ext in extensions:
                file_path = search_path / f"{include_name}{ext}"
                if file_path.exists():
                    return str(file_path.resolve())

        # If not found in project, it's an external header
        # Return a special identifier for external headers
        return f"EXTERNAL:{include_name}"

    def _get_uml_id(self, name: str) -> str:
        """Generate UML ID for a class"""
        return name.upper().replace("-", "_").replace(".", "_")

    def _get_header_uml_id(self, name: str) -> str:
        """Generate UML ID for a header class"""
        # Remove .h extension if present
        if name.endswith('.h'):
            name = name[:-2]
        return f"HEADER_{self._get_uml_id(name)}"

    def _get_typedef_uml_id(self, name: str) -> str:
        """Generate UML ID for a typedef class"""
        # Convert to uppercase and replace special characters
        base_id = name.upper().replace("-", "_").replace(".", "_")
        return f"TYPEDEF_{base_id}"

    def _get_type_uml_id(self, name: str) -> str:
        """Generate UML ID for a type class"""
        return f"TYPE_{self._get_uml_id(name)}"

    def _deduplicate_relationships(self, diagram_lines: List[str]) -> List[str]:
        """Remove duplicate relationship lines from the diagram"""
        seen_relationships = set()
        deduplicated_lines = []
        
        for line in diagram_lines:
            line = line.strip()
            
            # Check if this is a relationship line (contains --> or ..>)
            if ('-->' in line or '..>' in line) and ':' in line:
                # Normalize the relationship line for comparison
                # Remove extra whitespace and normalize formatting
                normalized_line = re.sub(r'\s+', ' ', line.strip())
                
                # Further normalize by removing angle brackets from relationship type
                # This handles cases like "declares" vs "<<declares>>"
                normalized_line = re.sub(r'<<([^>]+)>>', r'\1', normalized_line)
                
                if normalized_line in seen_relationships:
                    # Skip this duplicate relationship
                    continue
                else:
                    seen_relationships.add(normalized_line)
                    deduplicated_lines.append(line)
            else:
                # Not a relationship line, keep it as is
                deduplicated_lines.append(line)
        
        return deduplicated_lines

    def generate_typedef_uses_relations(self, file_model: FileModel, project_model: ProjectModel, include_hierarchy: set = None) -> List[str]:
        # For each typedef, if its fields use another typedef, emit a uses relation
        lines = []
        typedef_names = set()
        
        # Collect all typedef names from all files (for relationship processing)
        for f in project_model.files.values():
            typedef_names.update(f.typedefs.keys())
            # Also add typedef names from typedef_relations
            for typedef_rel in f.typedef_relations:
                typedef_names.add(typedef_rel.typedef_name)
        
        # Process typedefs from the current file and its include chain
        self._process_file_typedef_uses(file_model, project_model, typedef_names, lines, include_hierarchy=include_hierarchy)
        
        return lines
    
    def _process_file_typedef_uses(self, file_model: FileModel, project_model: ProjectModel, typedef_names: set, lines: List[str], visited_files: set = None, depth: int = 0, include_hierarchy: set = None) -> None:
        """Process typedef uses for a file and its include chain"""
        if visited_files is None:
            visited_files = set()
        
        # Prevent infinite recursion
        if depth > 3 or file_model.file_path in visited_files:
            return
        
        visited_files.add(file_model.file_path)
        
        # Check if this file is in the include hierarchy
        file_basename = Path(file_model.file_path).stem
        if include_hierarchy and file_basename not in include_hierarchy:
            return
        
        # Process typedefs from the current file
        for typedef in file_model.typedef_relations:
            typedef_name = typedef.typedef_name
            self._process_typedef_uses(typedef_name, file_model, typedef_names, lines, project_model)
        
        # Process simple typedefs from the current file
        for typedef_name, original_type in file_model.typedefs.items():
            if original_type == "struct":
                self._process_typedef_uses(typedef_name, file_model, typedef_names, lines, project_model)
            elif "(" in original_type and "*" in original_type:
                # This is likely a function pointer typedef
                self._process_function_pointer_typedef_uses(typedef_name, original_type, typedef_names, lines)
            elif "*" in original_type and "(" not in original_type:
                # This is likely a pointer typedef
                self._process_pointer_typedef_uses(typedef_name, original_type, typedef_names, lines)
            elif "[" in original_type:
                # This is likely an array typedef
                self._process_array_typedef_uses(typedef_name, original_type, typedef_names, lines)
        
        # Process typedefs from included files (recursively)
        for include_relation in file_model.include_relations:
            included_file_path = include_relation.included_file
            included_file_model = None
            # Try to find the included file model
            for key, model in project_model.files.items():
                if model.file_path == included_file_path:
                    included_file_model = model
                    break
            if not included_file_model:
                included_file_basename = Path(included_file_path).name
                for key, model in project_model.files.items():
                    if key == included_file_basename:
                        included_file_model = model
                        break
            
            if included_file_model:
                self._process_file_typedef_uses(included_file_model, project_model, typedef_names, lines, visited_files, depth + 1, include_hierarchy)
    
    def _process_typedef_uses(self, typedef_name: str, file_model: FileModel, typedef_names: set, lines: List[str], project_model: ProjectModel = None) -> None:
        """Process uses relationships for a single typedef"""
        # Find the struct/union/enum fields for this typedef
        struct = None
        
        # Try to find the struct by the typedef name itself
        struct = file_model.structs.get(typedef_name)
        
        # If not found, try common variations
        if not struct:
            # Try with _tag suffix
            if not typedef_name.endswith('_tag'):
                struct = file_model.structs.get(f"{typedef_name}_tag")
        
        # If still not found, try without _t suffix
        if not struct and typedef_name.endswith('_t'):
            base_name = typedef_name[:-2]
            struct = file_model.structs.get(base_name)
            
            # Also try with _tag suffix
            if not struct:
                struct = file_model.structs.get(f"{base_name}_tag")
        
        # If still not found and we have project_model, check included files
        if not struct and project_model:
            for include_relation in file_model.include_relations:
                included_file_path = include_relation.included_file
                included_file_model = None
                # Try to find the included file model
                for key, model in project_model.files.items():
                    if model.file_path == included_file_path:
                        included_file_model = model
                        break
                if not included_file_model:
                    included_file_basename = Path(included_file_path).name
                    for key, model in project_model.files.items():
                        if key == included_file_basename:
                            included_file_model = model
                            break
                
                if included_file_model:
                    # Try to find the struct in the included file
                    struct = included_file_model.structs.get(typedef_name)
                    if not struct and not typedef_name.endswith('_tag'):
                        struct = included_file_model.structs.get(f"{typedef_name}_tag")
                    if not struct and typedef_name.endswith('_t'):
                        base_name = typedef_name[:-2]
                        struct = included_file_model.structs.get(base_name)
                        if not struct:
                            struct = included_file_model.structs.get(f"{base_name}_tag")
                    if struct:
                        break
        
        if struct:
            for field in struct.fields:
                # If the field type is another typedef, emit a uses relation
                # Strip array syntax, pointers, const, etc.
                field_type = field.type.replace('const ', '').replace('*', '').strip()
                # Remove array syntax like [3], [MAX_LABEL_LEN], etc.
                field_type = re.sub(r'\[[^\]]*\]', '', field_type).strip()
                # Remove field name if present (everything after the first space)
                if ' ' in field_type:
                    field_type = field_type.split(' ')[0].strip()
                
                # Check if the field type is a typedef
                if field_type in typedef_names and field_type != typedef_name:
                    lines.append(f"{self._get_typedef_uml_id(typedef_name)} ..> {self._get_typedef_uml_id(field_type)} : <<uses>>")

    def _process_function_pointer_typedef_uses(self, typedef_name: str, original_type: str, typedef_names: set, lines: List[str]) -> None:
        """Process uses relationships for a function pointer typedef"""
        # Extract parameter types from function pointer definition
        # Example: "int ( * MyCallback ) ( MyBuffer * buffer )"
        # We need to extract "MyBuffer" from the parameters
        
        # Find the parameter list between the last set of parentheses
        param_start = original_type.rfind('(')
        param_end = original_type.rfind(')')
        
        if param_start != -1 and param_end != -1 and param_end > param_start:
            param_list = original_type[param_start + 1:param_end].strip()
            
            # Split parameters by comma and process each one
            if param_list:
                # Handle single parameter case
                params = [param_list] if ',' not in param_list else [p.strip() for p in param_list.split(',')]
                
                for param in params:
                    # Extract the type from the parameter
                    # Remove parameter name, pointers, const, etc.
                    param_type = param.replace('const ', '').replace('*', '').strip()
                    # Remove parameter name (everything after the last space)
                    if ' ' in param_type:
                        param_type = param_type.rsplit(' ', 1)[0].strip()
                    
                    # Check if the parameter type is a typedef
                    if param_type in typedef_names and param_type != typedef_name:
                        lines.append(f"{self._get_typedef_uml_id(typedef_name)} ..> {self._get_typedef_uml_id(param_type)} : <<uses>>")

    def _process_pointer_typedef_uses(self, typedef_name: str, original_type: str, typedef_names: set, lines: List[str]) -> None:
        """Process uses relationships for a pointer typedef"""
        # Extract the base type from pointer typedef
        # Example: "MyComplex *" -> extract "MyComplex"
        
        # Remove pointer symbols and whitespace
        base_type = original_type.replace('*', '').strip()
        
        # Check if the base type is a typedef
        if base_type in typedef_names and base_type != typedef_name:
            lines.append(f"{self._get_typedef_uml_id(typedef_name)} ..> {self._get_typedef_uml_id(base_type)} : <<uses>>")

    def _process_array_typedef_uses(self, typedef_name: str, original_type: str, typedef_names: set, lines: List[str]) -> None:
        """Process uses relationships for an array typedef"""
        # Extract the base type from array typedef
        # Example: "MyComplexPtr MyComplexArray [ 10 ]" -> extract "MyComplexPtr"
        
        # Find the array name and remove it along with the array syntax
        # Split by space and take the first part (the base type)
        parts = original_type.split()
        if len(parts) >= 2:
            base_type = parts[0]
            
            # Check if the base type is a typedef
            if base_type in typedef_names and base_type != typedef_name:
                lines.append(f"{self._get_typedef_uml_id(typedef_name)} ..> {self._get_typedef_uml_id(base_type)} : <<uses>>")

    def generate_type_dependencies(self, file_model: FileModel, project_model: ProjectModel, include_hierarchy: set = None) -> List[str]:
        """Generate relationships for typedef-to-typedef dependencies only"""
        lines = []
        seen_relationships = set()
        
        # Collect all typedef names from all files
        typedef_names = set()
        for f in project_model.files.values():
            typedef_names.update(f.typedefs.keys())
            for typedef_rel in f.typedef_relations:
                typedef_names.add(typedef_rel.typedef_name)
        
        # Process typedefs that use other typedefs in their fields
        for typedef_relation in file_model.typedef_relations:
            if typedef_relation.relationship_type == "struct":
                # Check if the struct definition uses other typedefs
                struct_name = typedef_relation.typedef_name
                struct = file_model.structs.get(struct_name)
                if not struct:
                    # Try with _tag suffix
                    struct = file_model.structs.get(f"{struct_name}_tag")
                
                if struct:
                    for field in struct.fields:
                        # Extract base type from field type (remove pointers, arrays, etc.)
                        base_type = self._extract_base_type(field.type)
                        if base_type in typedef_names and base_type != struct_name:
                            relationship_key = f"typedef_field_{struct_name}_{base_type}"
                            if relationship_key not in seen_relationships:
                                seen_relationships.add(relationship_key)
                                lines.append(f"{self._get_typedef_uml_id(struct_name)} ..> {self._get_typedef_uml_id(base_type)} : <<uses>>")
        
        # Process function pointer typedefs that use other typedefs
        for typedef_name, original_type in file_model.typedefs.items():
            if "(" in original_type and "*" in original_type:
                # This is a function pointer typedef, check if it uses other typedefs
                # Extract parameter types from function pointer
                import re
                param_match = re.search(r'\(\s*([^)]+)\s*\)', original_type)
                if param_match:
                    params_str = param_match.group(1)
                    # Split parameters and check each one
                    params = [p.strip() for p in params_str.split(',')]
                    for param in params:
                        base_type = self._extract_base_type(param)
                        if base_type in typedef_names and base_type != typedef_name:
                            relationship_key = f"typedef_func_ptr_{typedef_name}_{base_type}"
                            if relationship_key not in seen_relationships:
                                seen_relationships.add(relationship_key)
                                lines.append(f"{self._get_typedef_uml_id(typedef_name)} ..> {self._get_typedef_uml_id(base_type)} : <<uses>>")
        
        return lines
    
    def _extract_base_type(self, type_str: str) -> str:
        """Extract the base type from a complex type string (remove pointers, arrays, etc.)"""
        import re
        
        # Remove common prefixes
        type_str = re.sub(r'^(const\s+|static\s+|extern\s+)', '', type_str)
        
        # Remove pointer indicators
        type_str = re.sub(r'\s*\*\s*$', '', type_str)
        type_str = re.sub(r'\s*\*\s*', ' ', type_str)
        
        # Remove array indicators
        type_str = re.sub(r'\s*\[\s*\d*\s*\]\s*$', '', type_str)
        
        # Remove function pointer syntax
        type_str = re.sub(r'\(\s*\*\s*[^)]*\)\s*\([^)]*\)', '', type_str)
        
        # Clean up extra whitespace
        type_str = re.sub(r'\s+', ' ', type_str).strip()
        
        return type_str

    def generate_declares_relationships(self, file_model: FileModel, project_model: ProjectModel, include_hierarchy: set = None) -> List[str]:
        """Generate declares relationships between files and typedefs they define"""
        lines = []
        seen_relationships = set()
        
        # Get the class ID for the current file
        if file_model.file_path.endswith('.h'):
            class_id = self._get_header_uml_id(Path(file_model.file_path).stem)
        else:
            class_id = self._get_uml_id(Path(file_model.file_path).stem)
        
        # Check if this file is in the include hierarchy
        file_basename = Path(file_model.file_path).stem
        if include_hierarchy and file_basename not in include_hierarchy:
            return lines
        
        # Process typedefs defined in the current file
        for typedef_name, original_type in file_model.typedefs.items():
            relationship_key = f"declares_{class_id}_{typedef_name}"
            if relationship_key not in seen_relationships:
                seen_relationships.add(relationship_key)
                lines.append(f"{class_id} ..> {self._get_typedef_uml_id(typedef_name)} : <<declares>>")
        
        # Process typedefs from typedef_relations (complex typedefs like structs, enums, unions)
        for typedef_relation in file_model.typedef_relations:
            typedef_name = typedef_relation.typedef_name
            relationship_key = f"declares_{class_id}_{typedef_name}"
            if relationship_key not in seen_relationships:
                seen_relationships.add(relationship_key)
                lines.append(f"{class_id} ..> {self._get_typedef_uml_id(typedef_name)} : <<declares>>")
        
        return lines

    def generate_included_declares_relationships(self, file_model: FileModel, project_model: ProjectModel, include_hierarchy: set = None) -> List[str]:
        """Generate declares relationships for typedefs declared in included header files"""
        lines = []
        seen_relationships = set()
        
        # Process nested includes recursively
        self._process_nested_declares_relationships(file_model, project_model, seen_relationships, lines, include_hierarchy=include_hierarchy)
        
        return lines
    
    def _process_nested_declares_relationships(self, file_model: FileModel, project_model: ProjectModel, seen_relationships: set, lines: List[str], visited_files: set = None, depth: int = 0, max_depth: int = 3, include_hierarchy: set = None) -> None:
        """Recursively process declares relationships from included files"""
        if visited_files is None:
            visited_files = set()
        
        # Prevent infinite recursion and respect max_depth
        if depth >= max_depth or file_model.file_path in visited_files:
            return
        
        visited_files.add(file_model.file_path)
        
        # Process each include in the current file
        for include in file_model.includes:
            # Find the included file model
            included_file_model = self._find_included_file_model(include, project_model)
            if included_file_model and included_file_model.file_path.endswith('.h'):
                # Check if this included file is in the include hierarchy
                included_file_basename = Path(included_file_model.file_path).stem
                if include_hierarchy and included_file_basename not in include_hierarchy:
                    continue
                
                # Get the header class ID
                header_class_id = self._get_header_uml_id(Path(included_file_model.file_path).stem)
                
                # Process typedefs defined in the included header file
                for typedef_name, original_type in included_file_model.typedefs.items():
                    relationship_key = f"declares_{header_class_id}_{typedef_name}"
                    if relationship_key not in seen_relationships:
                        seen_relationships.add(relationship_key)
                        lines.append(f"{header_class_id} ..> {self._get_typedef_uml_id(typedef_name)} : <<declares>>")
                
                # Process typedefs from typedef_relations in the included header file
                for typedef_relation in included_file_model.typedef_relations:
                    typedef_name = typedef_relation.typedef_name
                    relationship_key = f"declares_{header_class_id}_{typedef_name}"
                    if relationship_key not in seen_relationships:
                        seen_relationships.add(relationship_key)
                        lines.append(f"{header_class_id} ..> {self._get_typedef_uml_id(typedef_name)} : <<declares>>")
                
                # Recursively process further nested includes (respecting max_depth)
                self._process_nested_declares_relationships(included_file_model, project_model, seen_relationships, lines, visited_files, depth + 1, max_depth)


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
        typedef_relations = []
        for rel_data in data.get("typedef_relations", []):
                    typedef_relations.append(
            TypedefRelation(
                rel_data["typedef_name"],
                rel_data["original_type"],
                rel_data["relationship_type"],
                rel_data.get("struct_tag_name", ""),  # Include struct_tag_name with default empty string
                rel_data.get("enum_tag_name", ""),  # Include enum_tag_name with default empty string
            )
        )

        # Convert include relations
        include_relations = []
        for rel_data in data.get("include_relations", []):
            include_relations.append(
                IncludeRelation(
                    rel_data["source_file"],
                    rel_data["included_file"],
                    rel_data["depth"],
                )
            )

        return FileModel(
            file_path=data["file_path"],
            relative_path=data["relative_path"],
            project_root=data["project_root"],
            encoding_used=data["encoding_used"],
            structs=structs,
            enums=enums,
            unions=unions,
            functions=functions,
            globals=globals_list,
            includes=data.get("includes", []),
            macros=data.get("macros", []),
            typedefs=data.get("typedefs", {}),
            typedef_relations=typedef_relations,
            include_relations=include_relations,
        )
