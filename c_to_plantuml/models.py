#!/usr/bin/env python3
"""
Data models for C to PlantUML converter
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
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
            raise ValueError("Field name must be a string")
        if not self.type or not isinstance(self.type, str):
            raise ValueError("Field type must be a non-empty string")


@dataclass
class TypedefRelation:
    """Represents a typedef relationship"""

    typedef_name: str
    original_type: str
    relationship_type: str  # 'defines' or 'alias'
    struct_tag_name: str = ""  # For struct typedefs, store the struct tag name
    enum_tag_name: str = ""  # For enum typedefs, store the enum tag name

    def __post_init__(self):
        """Validate typedef relation data after initialization"""
        if not self.typedef_name or not isinstance(self.typedef_name, str):
            raise ValueError("Typedef name must be a non-empty string")
        if not self.original_type or not isinstance(self.original_type, str):
            raise ValueError("Original type must be a non-empty string")
        if self.relationship_type not in ["defines", "alias"]:
            raise ValueError("Relationship type must be 'defines' or 'alias'")


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

    def __post_init__(self):
        """Validate function data after initialization"""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Function name must be a non-empty string")
        if not self.return_type or not isinstance(self.return_type, str):
            raise ValueError("Function return type must be a non-empty string")


@dataclass
class Struct:
    """Represents a C struct"""

    name: str
    fields: List[Field] = field(default_factory=list)
    methods: List[Function] = field(default_factory=list)

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

    def __post_init__(self):
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Enum name must be a non-empty string")
        # Convert any string values to EnumValue
        self.values = [v if isinstance(v, EnumValue) else EnumValue(v) for v in self.values]


@dataclass
class Union:
    """Represents a C union"""

    name: str
    fields: List[Field] = field(default_factory=list)

    def __post_init__(self):
        """Validate union data after initialization"""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Union name must be a non-empty string")


@dataclass
class FileModel:
    """Represents a parsed C/C++ file"""

    file_path: str
    relative_path: str
    project_root: str
    encoding_used: str
    structs: Dict[str, Struct] = field(default_factory=dict)
    enums: Dict[str, Enum] = field(default_factory=dict)
    functions: List[Function] = field(default_factory=list)
    globals: List[Field] = field(default_factory=list)
    includes: Set[str] = field(default_factory=set)
    macros: List[str] = field(default_factory=list)
    aliases: Dict[str, str] = field(default_factory=dict)
    typedef_relations: List[TypedefRelation] = field(default_factory=list)
    unions: Dict[str, Union] = field(default_factory=dict)

    def __post_init__(self):
        """Validate file model data after initialization"""
        if not self.file_path or not isinstance(self.file_path, str):
            raise ValueError("File path must be a non-empty string")
        if not self.relative_path or not isinstance(self.relative_path, str):
            raise ValueError("Relative path must be a non-empty string")
        if not self.project_root or not isinstance(self.project_root, str):
            raise ValueError("Project root must be a non-empty string")
        if not self.encoding_used or not isinstance(self.encoding_used, str):
            raise ValueError("Encoding must be a non-empty string")

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert set to list for JSON serialization
        data["includes"] = list(self.includes)
        # Convert typedef_relations to list of dicts
        data["typedef_relations"] = [asdict(rel) for rel in self.typedef_relations]
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
                    name=struct_data.get("name", name), fields=fields, methods=methods
                )
            else:
                structs[name] = struct_data

        # Convert enums back to Enum objects
        enums_data = data.get("enums", {})
        enums = {}
        for name, enum_data in enums_data.items():
            if isinstance(enum_data, dict):
                values = [EnumValue(**val) if isinstance(val, dict) else EnumValue(val) for val in enum_data.get("values", [])]
                enums[name] = Enum(
                    name=enum_data.get("name", name), values=values
                )
            else:
                enums[name] = enum_data

        # Convert typedef_relations back to TypedefRelation objects
        typedef_relations_data = data.get("typedef_relations", [])
        typedef_relations = [
            TypedefRelation(**rel) if isinstance(rel, dict) else rel
            for rel in typedef_relations_data
        ]

        # Convert include_relations back to IncludeRelation objects (disabled - field removed)
        # include_relations_data = data.get("include_relations", [])
        # include_relations = [
        #     IncludeRelation(**rel) if isinstance(rel, dict) else rel
        #     for rel in include_relations_data
        # ]

        # Convert unions back to Union objects
        unions_data = data.get("unions", {})
        unions = {}
        for name, union_data in unions_data.items():
            if isinstance(union_data, dict):
                fields = [
                    Field(**field) if isinstance(field, dict) else field
                    for field in union_data.get("fields", [])
                ]
                unions[name] = Union(name=union_data.get("name", name), fields=fields)
            else:
                unions[name] = union_data

        # Create new data dict with converted objects
        new_data = data.copy()
        new_data["includes"] = includes
        new_data["globals"] = globals
        new_data["functions"] = functions
        new_data["structs"] = structs
        new_data["enums"] = enums
        new_data["typedef_relations"] = typedef_relations
        new_data["unions"] = unions

        return cls(**new_data)

    def get_summary(self) -> dict:
        """Get a summary of the file contents"""
        return {
            "file_path": self.file_path,
            "structs_count": len(self.structs),
            "enums_count": len(self.enums),
            "functions_count": len(self.functions),
            "globals_count": len(self.globals),
            "includes_count": len(self.includes),
            "macros_count": len(self.macros),
            "aliases_count": len(self.aliases),
        }


@dataclass
class ProjectModel:
    """Represents a complete C/C++ project"""

    project_name: str
    project_root: str
    files: Dict[str, FileModel] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        """Validate project model data after initialization"""
        if not self.project_name or not isinstance(self.project_name, str):
            raise ValueError("Project name must be a non-empty string")
        if not self.project_root or not isinstance(self.project_root, str):
            raise ValueError("Project root must be a non-empty string")

    def save(self, file_path: str) -> None:
        """Save model to JSON file"""
        data = {
            "project_name": self.project_name,
            "project_root": self.project_root,
            "files": {
                path: file_model.to_dict() for path, file_model in self.files.items()
            },
            "created_at": self.created_at,
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"Failed to save model to {file_path}: {e}")

    @classmethod
    def from_dict(cls, data: dict) -> "ProjectModel":
        """Create from dictionary"""
        files = {
            path: FileModel.from_dict(file_data)
            for path, file_data in data.get("files", {}).items()
        }

        return cls(
            project_name=data.get("project_name", "Unknown"),
            project_root=data.get("project_root", ""),
            files=files,
            created_at=data.get("created_at", datetime.now().isoformat()),
        )

    @classmethod
    def load(cls, file_path: str) -> "ProjectModel":
        """Load model from JSON file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            raise ValueError(f"Failed to load model from {file_path}: {e}")

    def get_summary(self) -> dict:
        """Get a summary of the project"""
        total_structs = sum(len(f.structs) for f in self.files.values())
        total_enums = sum(len(f.enums) for f in self.files.values())
        total_functions = sum(len(f.functions) for f in self.files.values())
        total_globals = sum(len(f.globals) for f in self.files.values())

        return {
            "project_name": self.project_name,
            "project_root": self.project_root,
            "files_count": len(self.files),
            "total_structs": total_structs,
            "total_enums": total_enums,
            "total_functions": total_functions,
            "total_globals": total_globals,
            "created_at": self.created_at,
        }
