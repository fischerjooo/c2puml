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

    def _generate_main_class(self, file_model: FileModel, basename: str, project_model: ProjectModel) -> List[str]:
        """Generate the main class for the file using the new PlantUML template"""
        lines = [
            f'class "{basename}" as {self._get_uml_id(basename)} <<source>> #LightBlue',
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
                lines.append(f"    {function.return_type} {function.name}()")
        
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

        # Get all included files that exist in the project
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

                lines.extend(
                    self._generate_header_class(included_file_model, header_basename)
                )

        return lines

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
                lines.append(f"    + {function.return_type} {function.name}()")
        lines.append("}")
        lines.append("")
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
                    typedef_name = typedef_relation.typedef_name
                    if typedef_name not in seen_typedefs:
                        seen_typedefs.add(typedef_name)
                        lines.extend(self._generate_single_typedef_class(typedef_relation, included_file_model, project_model))
        
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
        # Include relationships
        for include_name in file_model.includes:
            included_file_path = self._find_included_file(
                include_name, file_model.project_root, project_model
            )
            included_file_model = None
            for key, model in project_model.files.items():
                if model.file_path == included_file_path:
                    included_file_model = model
                    break
            # Skip self-include
            if included_file_model and included_file_model.file_path == file_model.file_path:
                continue
            if included_file_model:
                header_basename = Path(included_file_path).stem
                lines.append(
                    f"{self._get_uml_id(Path(file_model.file_path).stem)} --> "
                    f"{self._get_header_uml_id(header_basename)} : <<include>>"
                )
        # Header-to-header relationships
        for include_relation in file_model.include_relations:
            source_basename = Path(include_relation.source_file).stem
            included_basename = Path(include_relation.included_file).stem
            # Skip self-referencing header-to-header include relations
            if source_basename == included_basename:
                import logging
                logging.getLogger(__name__).debug(f"Skipping self-referencing header include: {source_basename} -> {included_basename}")
                continue
            lines.append(
                f"{self._get_header_uml_id(source_basename)} --> "
                f"{self._get_header_uml_id(included_basename)} : <<include>>"
            )
        # Typedef relationships - process typedefs from current file and included files
        seen_typedef_relations = set()
        
        # Process typedefs from current file
        for typedef_relation in file_model.typedef_relations:
            self._process_typedef_relationships(typedef_relation, file_model, project_model, lines, seen_typedef_relations)
        
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
                    self._process_typedef_relationships(typedef_relation, included_file_model, project_model, lines, seen_typedef_relations)
        return lines

    def _process_typedef_relationships(self, typedef_relation, file_model: FileModel, project_model: ProjectModel, lines: List[str], seen_typedef_relations: set):
        """Process relationships for a single typedef"""
        typedef_name = typedef_relation.typedef_name
        original_type = typedef_relation.original_type
        relationship_type = typedef_relation.relationship_type
        
        # Create a unique identifier for this typedef relation to avoid duplicates
        relation_id = f"{file_model.file_path}:{typedef_name}"
        if relation_id in seen_typedef_relations:
            return
        seen_typedef_relations.add(relation_id)
        
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
                lines.append(
                    f"{typedef_class_id} -|> "
                    f"{self._get_type_uml_id(original_type)} : «alias»"
                )
        elif relationship_type == "alias":
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
                                lines.append(f"{typedef_class_id} --> {other_typedef_class_id} : uses")

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

        return None

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
            functions.append(
                Function(
                    func_data["name"],
                    func_data["return_type"],
                    func_data.get("parameters", []),
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
