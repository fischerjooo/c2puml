#!/usr/bin/env python3
"""
Data models for C to PlantUML converter
"""

import json
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class Field:
    """Represents a field in a struct or global variable"""

    name: str
    type: str
    value: Optional[str] = None

    def __repr__(self):
        if self.value is not None:
            return f"Field(name={self.name}, type={self.type}, value={self.value})"
        return f"Field(name={self.name}, type={self.type})"

    def __post_init__(self):
        """Validate field data after initialization"""
        if not isinstance(self.name, str):
            raise ValueError(
                f"Field name must be a string, got {type(self.name)}: {repr(self.name)}"
            )
        if not self.type or not isinstance(self.type, str):
            raise ValueError(
                f"Field type must be a non-empty string, got {type(self.type)}: {repr(self.type)}"
            )

        # Additional validation: ensure name and type are not just whitespace
        if not self.name.strip():
            raise ValueError(
                f"Field name cannot be empty or whitespace, got: {repr(self.name)}"
            )
        if not self.type.strip():
            raise ValueError(
                f"Field type cannot be empty or whitespace, got: {repr(self.type)}"
            )


# TypedefRelation class removed - tag names moved to struct/enum/union


@dataclass
class IncludeRelation:
    """Represents an include relationship"""

    source_file: str
    included_file: str
    depth: int

    def __post_init__(self):
        """Validate include relation data after initialization"""
        if not self.source_file or not isinstance(self.source_file, str):
            raise ValueError("Source file must be a non-empty string")
        if not self.included_file or not isinstance(self.included_file, str):
            raise ValueError("Included file must be a non-empty string")
        if not isinstance(self.depth, int) or self.depth < 0:
            raise ValueError("Depth must be a non-negative integer")


@dataclass
class Function:
    """Represents a function"""

    name: str
    return_type: str
    parameters: List[Field] = field(default_factory=list)
    is_static: bool = False
    is_declaration: bool = False
    is_inline: bool = False

    def __post_init__(self):
        """Validate function data after initialization"""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Function name must be a non-empty string")
        if not self.return_type or not isinstance(self.return_type, str):
            raise ValueError("Function return type must be a non-empty string")

        # Convert parameters to Field objects if they're dictionaries
        if self.parameters:
            converted_params = []
            for param in self.parameters:
                if isinstance(param, dict):
                    converted_params.append(Field(**param))
                else:
                    converted_params.append(param)
            self.parameters = converted_params


@dataclass
class Struct:
    """Represents a C struct"""

    name: str
    fields: List[Field] = field(default_factory=list)
    methods: List[Function] = field(default_factory=list)
    tag_name: str = ""  # Tag name for typedef structs
    uses: List[str] = field(
        default_factory=list
    )  # Non-primitive types used by this struct

    def __post_init__(self):
        """Validate struct data after initialization"""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Struct name must be a non-empty string")


@dataclass
class EnumValue:
    name: str
    value: Optional[str] = None

    def __post_init__(self):
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Enum value name must be a non-empty string")


@dataclass
class Enum:
    """Represents a C enum"""

    name: str
    values: List[EnumValue] = field(default_factory=list)
    tag_name: str = ""  # Tag name for typedef enums

    def __post_init__(self):
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Enum name must be a non-empty string")
        # Convert any string values to EnumValue
        self.values = [
            v if isinstance(v, EnumValue) else EnumValue(v) for v in self.values
        ]


@dataclass
class Union:
    """Represents a C union"""

    name: str
    fields: List[Field] = field(default_factory=list)
    tag_name: str = ""  # Tag name for typedef unions
    uses: List[str] = field(
        default_factory=list
    )  # Non-primitive types used by this union

    def __post_init__(self):
        """Validate union data after initialization"""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Union name must be a non-empty string")


@dataclass
class Alias:
    """Represents a type alias (typedef)"""

    name: str
    original_type: str
    uses: List[str] = field(
        default_factory=list
    )  # Non-primitive types used by this alias

    def __post_init__(self):
        """Validate alias data after initialization"""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Alias name must be a non-empty string")
        if not self.original_type or not isinstance(self.original_type, str):
            raise ValueError("Original type must be a non-empty string")


@dataclass
class FileModel:
    """Represents a parsed C/C++ file"""

    file_path: str

    name: str = ""  # Filename extracted from file_path
    structs: Dict[str, Struct] = field(default_factory=dict)
    enums: Dict[str, Enum] = field(default_factory=dict)
    functions: List[Function] = field(default_factory=list)
    globals: List[Field] = field(default_factory=list)
    includes: Set[str] = field(default_factory=set)
    macros: List[str] = field(default_factory=list)
    aliases: Dict[str, Alias] = field(default_factory=dict)
    unions: Dict[str, Union] = field(default_factory=dict)
    include_relations: List[IncludeRelation] = field(default_factory=list)
    anonymous_relationships: Dict[str, List[str]] = field(default_factory=dict)  # parent -> [child1, child2, ...]
    placeholder_headers: Set[str] = field(default_factory=set)  # Headers shown as empty (placeholders) in diagrams
    def __post_init__(self):
        """Extract filename from file_path if not provided"""
        if not self.name:
            from pathlib import Path

            self.name = Path(self.file_path).name

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)

        # Convert set to list for JSON serialization and sort for consistency
        data["includes"] = sorted(list(self.includes))
        # Serialize placeholder headers as sorted list
        data["placeholder_headers"] = sorted(list(self.placeholder_headers))
        # Convert include_relations to list of dicts and sort for consistency
        data["include_relations"] = sorted(
            [asdict(rel) for rel in self.include_relations],
            key=lambda x: (x["source_file"], x["included_file"]),
        )
        # Sort all dictionary fields for consistent ordering
        data["structs"] = dict(sorted(data["structs"].items()))
        data["enums"] = dict(sorted(data["enums"].items()))
        data["unions"] = dict(sorted(data["unions"].items()))
        data["aliases"] = dict(sorted(data["aliases"].items()))
        data["macros"] = sorted(data["macros"])
        # Sort anonymous relationships for consistent ordering
        data["anonymous_relationships"] = {k: sorted(v) for k, v in sorted(data["anonymous_relationships"].items())}
        # Sort functions and globals by name (they are already objects, not dicts)
        data["functions"] = sorted(self.functions, key=lambda x: x.name)
        data["globals"] = sorted(self.globals, key=lambda x: x.name)
        # Convert functions and globals to dicts after sorting
        data["functions"] = [asdict(f) for f in data["functions"]]
        data["globals"] = [asdict(g) for g in data["globals"]]

        # Sort "uses" arrays in structs, unions, and aliases for consistent ordering
        for struct_data in data["structs"].values():
            if "uses" in struct_data:
                struct_data["uses"] = sorted(struct_data["uses"])
        for union_data in data["unions"].values():
            if "uses" in union_data:
                union_data["uses"] = sorted(union_data["uses"])
        for alias_data in data["aliases"].values():
            if "uses" in alias_data:
                alias_data["uses"] = sorted(alias_data["uses"])

        # Tag names are now stored in struct/enum/union objects
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "FileModel":
        """Create from dictionary"""
        # Convert list back to set
        includes = set(data.get("includes", []))

        # Convert globals back to Field objects
        globals_data = data.get("globals", [])
        globals = [Field(**g) if isinstance(g, dict) else g for g in globals_data]

        # Convert functions back to Function objects
        functions_data = data.get("functions", [])
        functions = [
            Function(**f) if isinstance(f, dict) else f for f in functions_data
        ]

        # Convert structs back to Struct objects
        structs_data = data.get("structs", {})
        structs = {}
        for name, struct_data in structs_data.items():
            if isinstance(struct_data, dict):
                fields = [
                    Field(**field) if isinstance(field, dict) else field
                    for field in struct_data.get("fields", [])
                ]
                methods = [
                    Function(**method) if isinstance(method, dict) else method
                    for method in struct_data.get("methods", [])
                ]
                structs[name] = Struct(
                    name=struct_data.get("name", name),
                    fields=fields,
                    methods=methods,
                    tag_name=struct_data.get("tag_name", ""),
                    uses=struct_data.get("uses", []),
                )
            else:
                structs[name] = struct_data

        # Convert enums back to Enum objects
        enums_data = data.get("enums", {})
        enums = {}
        for name, enum_data in enums_data.items():
            if isinstance(enum_data, dict):
                values = [
                    EnumValue(**val) if isinstance(val, dict) else EnumValue(val)
                    for val in enum_data.get("values", [])
                ]
                enums[name] = Enum(name=enum_data.get("name", name), values=values)
            else:
                enums[name] = enum_data

        # Tag names are now stored in struct/enum/union objects

        # Convert include_relations back to IncludeRelation objects
        include_relations_data = data.get("include_relations", [])
        include_relations = [
            IncludeRelation(**rel) if isinstance(rel, dict) else rel
            for rel in include_relations_data
        ]

        # Convert unions back to Union objects
        unions_data = data.get("unions", {})
        unions = {}
        for name, union_data in unions_data.items():
            if isinstance(union_data, dict):
                fields = [
                    Field(**field) if isinstance(field, dict) else field
                    for field in union_data.get("fields", [])
                ]
                unions[name] = Union(
                    name=union_data.get("name", name),
                    fields=fields,
                    tag_name=union_data.get("tag_name", ""),
                    uses=union_data.get("uses", []),
                )
            else:
                unions[name] = union_data

        # Convert aliases back to Alias objects
        aliases_data = data.get("aliases", {})
        aliases = {}
        for name, alias_data in aliases_data.items():
            if isinstance(alias_data, dict):
                aliases[name] = Alias(
                    name=alias_data.get("name", name),
                    original_type=alias_data.get("original_type", ""),
                    uses=alias_data.get("uses", []),
                )
            else:
                # Handle legacy format where aliases was Dict[str, str]
                aliases[name] = Alias(name=name, original_type=alias_data, uses=[])

        # Create new data dict with converted objects
        new_data = data.copy()
        new_data["includes"] = includes
        new_data["globals"] = globals
        new_data["functions"] = functions
        new_data["structs"] = structs
        new_data["enums"] = enums
        new_data["unions"] = unions
        new_data["aliases"] = aliases
        new_data["include_relations"] = include_relations
        # Load placeholder headers (if present)
        new_data["placeholder_headers"] = set(data.get("placeholder_headers", []))

        return cls(**new_data)




@dataclass
class ProjectModel:
    """Represents a complete C/C++ project"""

    project_name: str
    source_folder: str
    files: Dict[str, FileModel] = field(default_factory=dict)

    def __post_init__(self):
        """Validate project model data after initialization"""
        if not self.project_name or not isinstance(self.project_name, str):
            raise ValueError("Project name must be a non-empty string")
        if not self.source_folder or not isinstance(self.source_folder, str):
            raise ValueError("Source folder must be a non-empty string")

    def save(self, file_path: str) -> None:
        """Save model to JSON file"""
        data = {
            "project_name": self.project_name,
            "source_folder": self.source_folder,
            "files": {
                path: file_model.to_dict()
                for path, file_model in sorted(self.files.items())
            },
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)
        except Exception as e:
            raise ValueError(f"Failed to save model to {file_path}: {e}") from e

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectModel":
        """Create from dictionary"""
        files = {
            path: FileModel.from_dict(file_data)
            for path, file_data in data.get("files", {}).items()
        }

        return cls(
            project_name=data.get("project_name", "Unknown"),
            source_folder=data.get("source_folder", data.get("project_root", "")),
            files=files,
        )

    @classmethod
    def load(cls, file_path: str) -> "ProjectModel":
        """Load model from JSON file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            raise ValueError(f"Failed to load model from {file_path}: {e}") from e



    def update_uses_fields(self):
        """Update all uses fields across the entire project model"""
        # Collect all available type names from the entire project
        available_types = set()
        for file_model in self.files.values():
            available_types.update(file_model.structs.keys())
            available_types.update(file_model.enums.keys())
            available_types.update(file_model.unions.keys())
            available_types.update(file_model.aliases.keys())

        # Update uses fields for all structures in all files
        for file_model in self.files.values():
            # Update struct uses
            for struct in file_model.structs.values():
                filtered_uses = []
                for struct_field in struct.fields:
                    field_uses = self._extract_non_primitive_types(
                        struct_field.type, available_types
                    )
                    filtered_uses.extend(field_uses)
                struct.uses = list(set(filtered_uses))

            # Update union uses
            for union in file_model.unions.values():
                filtered_uses = []
                for union_field in union.fields:
                    field_uses = self._extract_non_primitive_types(
                        union_field.type, available_types
                    )
                    filtered_uses.extend(field_uses)
                union.uses = list(set(filtered_uses))

            # Update alias uses
            for alias in file_model.aliases.values():
                alias.uses = self._extract_non_primitive_types(
                    alias.original_type, available_types
                )
                # Remove the alias name from its own uses list
                if alias.name in alias.uses:
                    alias.uses.remove(alias.name)

    def _extract_non_primitive_types(self, type_str: str, available_types: set) -> list:
        """Extract non-primitive type names from a type string that exist in available_types"""
        # Define primitive types
        primitive_types = {
            "void",
            "char",
            "short",
            "int",
            "long",
            "float",
            "double",
            "signed",
            "unsigned",
            "const",
            "volatile",
            "static",
            "extern",
            "auto",
            "register",
            "inline",
            "restrict",
            "size_t",
            "ptrdiff_t",
            "int8_t",
            "int16_t",
            "int32_t",
            "int64_t",
            "uint8_t",
            "uint16_t",
            "uint32_t",
            "uint64_t",
            "intptr_t",
            "uintptr_t",
            "bool",
            "true",
            "false",
            "NULL",
            "nullptr",
        }

        # Remove common C keywords and operators
        import re

        # Split by common delimiters and operators
        parts = re.split(r"[\[\]\(\)\{\}\s\*&,;]", type_str)

        # Extract potential type names that exist in available_types
        types = []
        for part in parts:
            part = part.strip()
            if part and len(part) > 1 and part not in primitive_types:
                # Check if it looks like a type name (starts with letter, contains letters/numbers/underscores)
                if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", part):
                    # Only include if it exists in available_types
                    if part in available_types:
                        types.append(part)

        return list(set(types))  # Remove duplicates
