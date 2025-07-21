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
        diagram_lines.extend(self._generate_main_class(file_model, basename))

        # Generate header classes for includes
        diagram_lines.extend(self._generate_header_classes(file_model, project_model))

        # Generate typedef classes
        diagram_lines.extend(self._generate_typedef_classes(file_model))

        # Generate relationships
        diagram_lines.extend(self._generate_relationships(file_model, project_model))

        # End diagram
        diagram_lines.extend(["", "@enduml"])

        return "\n".join(diagram_lines)

    def _generate_main_class(self, file_model: FileModel, basename: str) -> List[str]:
        """Generate the main class for the file"""
        lines = [
            f'class "{basename}" as {self._get_uml_id(basename)} <<source>> #LightBlue',
            "{",
        ]

        # Add macros
        if file_model.macros:
            lines.append("    -- Macros --")
            for macro in file_model.macros:
                lines.append(f"    + #define {macro}")
            lines.append("")

        # Add typedefs
        if file_model.typedefs:
            lines.append("    -- Typedefs --")
            for typedef_name, original_type in file_model.typedefs.items():
                lines.append(f"    + typedef {original_type} {typedef_name}")
            lines.append("")

        # Add global variables
        if file_model.globals:
            lines.append("    -- Global Variables --")
            for global_var in file_model.globals:
                lines.append(f"    - {global_var.type} {global_var.name}")
            lines.append("")

        # Add functions
        if file_model.functions:
            lines.append("    -- Functions --")
            for function in file_model.functions:
                lines.append(f"    + {function.return_type} {function.name}()")
            lines.append("")

        # Add structs
        if file_model.structs:
            lines.append("    -- Structs --")
            for struct_name, struct in file_model.structs.items():
                lines.append(f"    + struct {struct_name}")
                for field in struct.fields:
                    lines.append(f"        + {field.type} {field.name}")
            lines.append("")

        # Add enums
        if file_model.enums:
            lines.append("    -- Enums --")
            for enum_name, enum in file_model.enums.items():
                lines.append(f"    + enum {enum_name}")
                for value in enum.values:
                    lines.append(f"        + {value}")
            lines.append("")

        # Add unions
        if file_model.unions:
            lines.append("    -- Unions --")
            for union_name, union in file_model.unions.items():
                lines.append(f"    + union {union_name}")
                for field in union.fields:
                    lines.append(f"        + {field.type} {field.name}")
            lines.append("")

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
            included_file_path = self._find_included_file(
                include_name, file_model.project_root, project_model
            )

            # Try to find the file in project_model.files by matching file paths
            included_file_model = None
            for key, model in project_model.files.items():
                if model.file_path == included_file_path:
                    included_file_model = model
                    break

            if included_file_model:
                header_basename = Path(included_file_path).stem

                lines.extend(
                    self._generate_header_class(included_file_model, header_basename)
                )

        return lines

    def _generate_header_class(self, file_model: FileModel, basename: str) -> List[str]:
        """Generate a class for a header file"""
        lines = [
            f'class "{basename}" as {self._get_header_uml_id(basename)} '
            f"<<header>> #LightGreen",
            "{",
        ]

        # Add macros
        if file_model.macros:
            lines.append("    -- Macros --")
            for macro in file_model.macros:
                lines.append(f"    + #define {macro}")
            lines.append("")

        # Add typedefs
        if file_model.typedefs:
            lines.append("    -- Typedefs --")
            for typedef_name, original_type in file_model.typedefs.items():
                lines.append(f"    + typedef {original_type} {typedef_name}")
            lines.append("")

        # Add global variables
        if file_model.globals:
            lines.append("    -- Global Variables --")
            for global_var in file_model.globals:
                lines.append(f"    - {global_var.type} {global_var.name}")
            lines.append("")

        # Add functions
        if file_model.functions:
            lines.append("    -- Functions --")
            for function in file_model.functions:
                lines.append(f"    + {function.return_type} {function.name}()")
            lines.append("")

        # Add structs
        if file_model.structs:
            lines.append("    -- Structs --")
            for struct_name, struct in file_model.structs.items():
                lines.append(f"    + struct {struct_name}")
                for field in struct.fields:
                    lines.append(f"        + {field.type} {field.name}")
            lines.append("")

        # Add enums
        if file_model.enums:
            lines.append("    -- Enums --")
            for enum_name, enum in file_model.enums.items():
                lines.append(f"    + enum {enum_name}")
                for value in enum.values:
                    lines.append(f"        + {value}")
            lines.append("")

        # Add unions
        if file_model.unions:
            lines.append("    -- Unions --")
            for union_name, union in file_model.unions.items():
                lines.append(f"    + union {union_name}")
                for field in union.fields:
                    lines.append(f"        + {field.type} {field.name}")
            lines.append("")

        lines.append("}")
        lines.append("")

        return lines

    def _generate_typedef_classes(self, file_model: FileModel) -> List[str]:
        """Generate classes for typedefs"""
        lines = []

        for typedef_relation in file_model.typedef_relations:
            typedef_name = typedef_relation.typedef_name
            original_type = typedef_relation.original_type
            relationship_type = typedef_relation.relationship_type

            # Generate typedef class
            lines.extend(
                [
                    f'class "{typedef_name}" as '
                    f"{self._get_typedef_uml_id(typedef_name)} "
                    f"<<typedef>> #LightYellow",
                    "{",
                    f"    + {original_type}",
                    "}",
                    "",
                ]
            )

            # Generate original type class if it's a struct/enum/union
            if relationship_type == "defines":
                # Find the original type in the file
                if original_type in file_model.structs:
                    struct = file_model.structs[original_type]
                    lines.extend(
                        [
                            f'class "{original_type}" as '
                            f"{self._get_type_uml_id(original_type)} "
                            f"<<type>> #LightGray",
                            "{",
                            f"    + struct {original_type}",
                        ]
                    )
                    for field in struct.fields:
                        lines.append(f"        + {field.type} {field.name}")
                    lines.extend(["}", ""])
                elif original_type in file_model.enums:
                    enum = file_model.enums[original_type]
                    lines.extend(
                        [
                            f'class "{original_type}" as '
                            f"{self._get_type_uml_id(original_type)} "
                            f"<<type>> #LightGray",
                            "{",
                            f"    + enum {original_type}",
                        ]
                    )
                    for value in enum.values:
                        lines.append(f"        + {value}")
                    lines.extend(["}", ""])
                elif original_type in file_model.unions:
                    union = file_model.unions[original_type]
                    lines.extend(
                        [
                            f'class "{original_type}" as '
                            f"{self._get_type_uml_id(original_type)} "
                            f"<<type>> #LightGray",
                            "{",
                            f"    + union {original_type}",
                        ]
                    )
                    for field in union.fields:
                        lines.append(f"        + {field.type} {field.name}")
                    lines.extend(["}", ""])

        return lines

    def _generate_relationships(
        self, file_model: FileModel, project_model: ProjectModel
    ) -> List[str]:
        """Generate relationships between classes"""
        lines = []

        # Include relationships
        for include_name in file_model.includes:
            included_file_path = self._find_included_file(
                include_name, file_model.project_root, project_model
            )

            # Try to find the file in project_model.files by matching file paths
            included_file_model = None
            for key, model in project_model.files.items():
                if model.file_path == included_file_path:
                    included_file_model = model
                    break

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
            lines.append(
                f"{self._get_header_uml_id(source_basename)} --> "
                f"{self._get_header_uml_id(included_basename)} : <<include>>"
            )

        # Typedef relationships
        for typedef_relation in file_model.typedef_relations:
            typedef_name = typedef_relation.typedef_name
            original_type = typedef_relation.original_type
            relationship_type = typedef_relation.relationship_type

            if relationship_type == "defines":
                lines.append(
                    f"{self._get_typedef_uml_id(typedef_name)} *-- "
                    f"{self._get_type_uml_id(original_type)} : «defines»"
                )
            else:  # alias
                lines.append(
                    f"{self._get_typedef_uml_id(typedef_name)} -|> "
                    f"{self._get_type_uml_id(original_type)} : «alias»"
                )

        return lines

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
