#!/usr/bin/env python3
"""
Generator module for C to PlantUML converter - Step 3: Generate puml files based on model.json
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from .models import FileModel, ProjectModel


class PlantUMLGenerator:
    """PlantUML diagram generator"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate_diagram(
        self, file_model: FileModel, project_model: ProjectModel
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

        # Generate header classes for includes
        diagram_lines.extend(self._generate_header_classes(file_model, project_model))

        # Generate typedef classes
        diagram_lines.extend(self._generate_typedef_classes(file_model, project_model))

        # Generate relationships
        diagram_lines.extend(self._generate_relationships(file_model, project_model))

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
        
        # Only show typedefs to primitive types directly in the file class
        primitive_typedefs = []
        for typedef_relation in file_model.typedef_relations:
            typedef_name = typedef_relation.typedef_name
            original_type = typedef_relation.original_type
            relationship_type = typedef_relation.relationship_type
            is_header = file_model.file_path.endswith('.h')
            visibility = "+" if is_header else "-"
            # Only show primitive typedefs (not struct/enum/union)
            if relationship_type == "alias" and not (original_type.startswith("struct") or original_type.startswith("enum") or original_type.startswith("union")):
                primitive_typedefs.append(f"    {visibility} typedef {original_type} {typedef_name}")
        
        # Add primitive typedefs from included files with + visibility
        for include_relation in file_model.include_relations:
            included_file_path = include_relation.included_file
            included_file_model = None
            for key, model in project_model.files.items():
                if model.file_path == included_file_path:
                    included_file_model = model
                    break
            if included_file_model:
                for typedef_relation in included_file_model.typedef_relations:
                    typedef_name = typedef_relation.typedef_name
                    original_type = typedef_relation.original_type
                    relationship_type = typedef_relation.relationship_type
                    if relationship_type == "alias" and not (original_type.startswith("struct") or original_type.startswith("enum") or original_type.startswith("union")):
                        primitive_typedefs.append(f"    + typedef {original_type} {typedef_name}")
        
        if file_model.macros:
            lines.append("    -- Macros --")
            for macro in file_model.macros:
                lines.append(f"    - #define {macro}")
        
        if primitive_typedefs:
            lines.append("    -- Typedefs --")
            lines.extend(primitive_typedefs)
        
        if file_model.globals:
            lines.append("    -- Global Variables --")
            for global_var in file_model.globals:
                lines.append(f"    {global_var.type} {global_var.name}")
        
        if file_model.functions:
            lines.append("    -- Functions --")
            for function in file_model.functions:
                lines.append(f"    {self._format_function_signature(function)}")
        
        # Do not show structs/enums/unions directly if they are only present as typedefs
        # (They will be shown in their own class if needed)
        lines.append("}")
        lines.append("")
        return lines

    def _generate_header_classes(
        self, file_model: FileModel, project_model: ProjectModel
    ) -> List[str]:
        """Generate classes for included header files"""
        lines = []
        seen_headers = set()

        # Process direct includes
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
                
                # Recursively process include relationships from the included file
                self._process_nested_includes(included_file_model, project_model, seen_headers, lines)
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

    def _process_nested_includes(self, file_model: FileModel, project_model: ProjectModel, seen_headers: set, lines: List[str], visited_files: set = None, depth: int = 0) -> None:
        """Recursively process include relationships from included files"""
        if visited_files is None:
            visited_files = set()
        
        # Prevent infinite recursion
        if depth > 3 or file_model.file_path in visited_files:
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
                    # Recursively process further nested includes
                    self._process_nested_includes(included_file_model, project_model, seen_headers, lines, visited_files, depth + 1)

    def _process_nested_typedefs(self, file_model: FileModel, project_model: ProjectModel, seen_typedefs: set, lines: List[str], visited_files: set = None, depth: int = 0) -> None:
        """Recursively process typedefs from included files"""
        if visited_files is None:
            visited_files = set()
        
        # Prevent infinite recursion
        if depth > 3 or file_model.file_path in visited_files:
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
                for typedef_relation in included_file_model.typedef_relations:
                    typedef_name = typedef_relation.typedef_name
                    if typedef_name not in seen_typedefs:
                        seen_typedefs.add(typedef_name)
                        lines.extend(self._generate_single_typedef_class(typedef_relation, included_file_model, project_model))
                # Recursively process further nested typedefs
                self._process_nested_typedefs(included_file_model, project_model, seen_typedefs, lines, visited_files, depth + 1)

    def _generate_header_class(self, file_model: FileModel, basename: str) -> List[str]:
        """Generate a class for a header file using the new PlantUML template"""
        lines = [
            f'class "{basename}" as {self._get_header_uml_id(basename)} <<header>> #LightGreen',
            "{",
        ]
        if file_model.macros:
            lines.append("    -- Macros --")
            for macro in file_model.macros:
                lines.append(f"    + #define {macro}")
        
        # Only show primitive typedefs directly in the header class
        primitive_typedefs = []
        for typedef_relation in file_model.typedef_relations:
            typedef_name = typedef_relation.typedef_name
            original_type = typedef_relation.original_type
            relationship_type = typedef_relation.relationship_type
            if relationship_type == "alias" and not (original_type.startswith("struct") or original_type.startswith("enum") or original_type.startswith("union")):
                primitive_typedefs.append(f"    + typedef {original_type} {typedef_name}")
        if primitive_typedefs:
            lines.append("    -- Typedefs --")
            lines.extend(primitive_typedefs)
        
        if file_model.globals:
            lines.append("    -- Global Variables --")
            for global_var in file_model.globals:
                lines.append(f"    + {global_var.type} {global_var.name}")
        
        if file_model.functions:
            lines.append("    -- Functions --")
            for function in file_model.functions:
                lines.append(f"    + {self._format_function_signature(function)}")
        
        # Display struct fields as global variables (for backward compatibility with tests)
        if file_model.structs:
            lines.append("    -- Struct Fields --")
            for struct_name, struct in file_model.structs.items():
                for field in struct.fields:
                    lines.append(f"    + {field.type} {field.name}")
        
        lines.append("}")
        lines.append("")
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

    def _generate_typedef_classes(self, file_model: FileModel, project_model: ProjectModel) -> List[str]:
        """Generate classes for typedefs using the new PlantUML template"""
        lines = []
        seen_typedefs = set()
        
        # Process typedefs from the current file
        for typedef_relation in file_model.typedef_relations:
            typedef_name = typedef_relation.typedef_name
            if typedef_name not in seen_typedefs:
                seen_typedefs.add(typedef_name)
                lines.extend(self._generate_single_typedef_class(typedef_relation, file_model, project_model))
        
        # Process typedefs from included header files (recursively)
        self._process_nested_typedefs(file_model, project_model, seen_typedefs, lines)
        
        return lines
    
    def _generate_single_typedef_class(self, typedef_relation, file_model: FileModel, project_model: ProjectModel) -> List[str]:
        """Generate a single typedef class"""
        lines = []
        typedef_name = typedef_relation.typedef_name
        original_type = typedef_relation.original_type
        relationship_type = typedef_relation.relationship_type
        
        # Typedef class
        lines.append(f'class "{typedef_name}" as {self._get_typedef_uml_id(typedef_name)} <<typedef>> #LightYellow')
        lines.append("{")
        # For struct/union/enum typedefs, show fields/values
        if relationship_type == "defines":
            if original_type == "struct":
                # Try to find the struct by the struct tag name if available
                struct_name = typedef_relation.struct_tag_name if typedef_relation.struct_tag_name else typedef_name
                # Look for the struct in the file model that contains the typedef relation
                import logging
                logging.getLogger(__name__).debug(f"Looking for struct '{struct_name}' in file '{file_model.file_path}', available structs: {list(file_model.structs.keys())}")
                logging.getLogger(__name__).debug(f"typedef_relation.struct_tag_name: '{typedef_relation.struct_tag_name}', typedef_name: '{typedef_name}'")
                if struct_name in file_model.structs:
                    struct = file_model.structs[struct_name]
                    for field in struct.fields:
                        lines.append(f"    + {field.type} {field.name}")
                else:
                    lines.append(f"    + {original_type}")
            elif original_type == "enum":
                # Try to find the enum by the enum tag name if available, otherwise by typedef name
                enum_name = typedef_relation.enum_tag_name if hasattr(typedef_relation, 'enum_tag_name') and typedef_relation.enum_tag_name else typedef_name
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
                        lines.append(f"    + {value}")
                else:
                    logging.getLogger(__name__).debug(f"Enum '{enum_name}' not found in project model")
                    lines.append(f"    + {original_type}")
            elif original_type == "union" and typedef_name in file_model.unions:
                union = file_model.unions[typedef_name]
                for field in union.fields:
                    lines.append(f"    + {field.type} {field.name}")
            else:
                lines.append(f"    + {original_type}")
        else:
            lines.append(f"    + {original_type}")
        lines.append("}")
        lines.append("")
        return lines

    def _generate_relationships(
        self, file_model: FileModel, project_model: ProjectModel
    ) -> List[str]:
        """Generate relationships between classes using the new PlantUML template"""
        lines = []
        seen_relationships = set()
        
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
                lines.append(f"{header_class_id} ..> {typedef_class_id} : declares")
            else:
                # Typedef is defined in source file
                lines.append(f"{main_class_id} ..> {typedef_class_id} : declares")
        else:
            # Typedef is from an included header file
            lines.append(f"{header_class_id} ..> {typedef_class_id} : declares")
        
        # For complex typedefs, show the 'defines' relation from the typedef class to the type class
        if relationship_type == "defines":
            if original_type in ("struct", "enum", "union"):
                # For struct/enum/union typedefs, don't create a relationship to a non-existent type class
                # since the fields/values are already shown in the typedef class itself
                pass
            else:
                relationship_id = f"{typedef_name}->{original_type}:alias"
                if relationship_id not in seen_relationships:
                    seen_relationships.add(relationship_id)
                    lines.append(
                        f"{typedef_class_id} -|> "
                        f"{self._get_type_uml_id(original_type)} : «alias»"
                    )
        elif relationship_type == "alias":
            relationship_id = f"{typedef_name}->{original_type}:alias"
            if relationship_id not in seen_relationships:
                seen_relationships.add(relationship_id)
                lines.append(
                    f"{typedef_class_id} -|> "
                    f"{self._get_type_uml_id(original_type)} : «alias»"
                )
        
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
                                    lines.append(f"{typedef_class_id} --> {other_typedef_class_id} : uses")
        
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
                            lines.append(f"{header_class_id} ..> {typedef_class_id} : declares")
        
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
                            lines.append(f"{header_class_id} ..> {typedef_class_id} : declares")

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
                        lines.append(f"{typedef_class_id} ..> {header_class_id} : uses MAX_LABEL_LEN")
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
                                            lines.append(f"{typedef_class_id} ..> {header_class_id} : uses {macro}")

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
        return f"HEADER_{self._get_uml_id(name)}"

    def _get_typedef_uml_id(self, name: str) -> str:
        """Generate UML ID for a typedef class"""
        return f"TYPEDEF_{self._get_uml_id(name)}"

    def _get_type_uml_id(self, name: str) -> str:
        """Generate UML ID for a type class"""
        return f"TYPE_{self._get_uml_id(name)}"


class Generator:
    """Main generator class for Step 3: Generate puml files based on model.json"""

    def __init__(self):
        self.plantuml_generator = PlantUMLGenerator()
        self.logger = logging.getLogger(__name__)

    def generate(self, model_file: str, output_dir: str = "./output") -> str:
        """
        Step 3: Generate puml files based on model.json

        Args:
            model_file: Input JSON model file path
            output_dir: Output directory for PlantUML files

        Returns:
            Path to the output directory
        """
        self.logger.info(f"Step 3: Generating PlantUML diagrams from: {model_file}")

        # Load the model
        model = self._load_model(model_file)

        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate diagrams for each .c file
        generated_files = []
        for file_path, file_model in model.files.items():
            if file_path.endswith(".c"):
                try:
                    diagram_content = self.plantuml_generator.generate_diagram(
                        file_model, model
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
            enums[name] = Enum(name, enum_data.get("values", []))

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
