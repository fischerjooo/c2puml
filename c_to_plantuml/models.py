#!/usr/bin/env python3
"""
Data models for C to PlantUML converter
"""

import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Set, Optional


@dataclass
class Field:
    """Represents a field in a struct or global variable"""
    name: str
    type: str
    array_size: Optional[str] = None


@dataclass
class Function:
    """Represents a function"""
    name: str
    return_type: str
    parameters: List[Field]
    is_static: bool = False


@dataclass
class Struct:
    """Represents a C struct"""
    name: str
    fields: List[Field]
    methods: List[Function]


@dataclass
class Enum:
    """Represents a C enum"""
    name: str
    values: List[str]


@dataclass
class FileModel:
    """Represents a parsed C/C++ file"""
    file_path: str
    relative_path: str
    project_root: str
    encoding_used: str
    structs: Dict[str, Struct]
    enums: Dict[str, Enum]
    functions: List[Function]
    globals: List[Field]
    includes: Set[str]
    macros: List[str]
    typedefs: Dict[str, str]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert set to list for JSON serialization
        data['includes'] = list(self.includes)
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'FileModel':
        """Create from dictionary"""
        # Convert list back to set
        includes = set(data.get('includes', []))
        
        # Convert globals back to Field objects
        globals_data = data.get('globals', [])
        globals = [Field(**g) if isinstance(g, dict) else g for g in globals_data]
        
        # Convert functions back to Function objects
        functions_data = data.get('functions', [])
        functions = [Function(**f) if isinstance(f, dict) else f for f in functions_data]
        
        # Convert structs back to Struct objects
        structs_data = data.get('structs', {})
        structs = {}
        for name, struct_data in structs_data.items():
            if isinstance(struct_data, dict):
                fields = [Field(**field) if isinstance(field, dict) else field 
                         for field in struct_data.get('fields', [])]
                methods = [Function(**method) if isinstance(method, dict) else method 
                          for method in struct_data.get('methods', [])]
                structs[name] = Struct(
                    name=struct_data.get('name', name),
                    fields=fields,
                    methods=methods
                )
            else:
                structs[name] = struct_data
        
        # Convert enums back to Enum objects
        enums_data = data.get('enums', {})
        enums = {}
        for name, enum_data in enums_data.items():
            if isinstance(enum_data, dict):
                enums[name] = Enum(
                    name=enum_data.get('name', name),
                    values=enum_data.get('values', [])
                )
            else:
                enums[name] = enum_data
        
        # Create new data dict with converted objects
        new_data = data.copy()
        new_data['includes'] = includes
        new_data['globals'] = globals
        new_data['functions'] = functions
        new_data['structs'] = structs
        new_data['enums'] = enums
        
        return cls(**new_data)


@dataclass
class ProjectModel:
    """Represents a complete C/C++ project"""
    project_name: str
    project_root: str
    files: Dict[str, FileModel]
    created_at: str
    
    def save(self, file_path: str):
        """Save model to JSON file"""
        data = {
            'project_name': self.project_name,
            'project_root': self.project_root,
            'files': {path: file_model.to_dict() for path, file_model in self.files.items()},
            'created_at': self.created_at
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ProjectModel':
        """Create from dictionary"""
        files = {
            path: FileModel.from_dict(file_data) 
            for path, file_data in data.get('files', {}).items()
        }
        
        return cls(
            project_name=data.get('project_name', 'Unknown'),
            project_root=data.get('project_root', ''),
            files=files,
            created_at=data.get('created_at', '')
        )