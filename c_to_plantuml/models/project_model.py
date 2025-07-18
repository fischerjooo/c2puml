from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
import json
from .c_structures import Field, Function, Struct, Enum

@dataclass
class ProjectModel:
    """Comprehensive model representing all parsed C code from a project"""
    project_name: str
    project_roots: List[str]
    files: Dict[str, 'FileModel']
    global_includes: List[str]
    created_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'project_name': self.project_name,
            'project_roots': self.project_roots,
            'files': {path: file_model.to_dict() for path, file_model in self.files.items()},
            'global_includes': self.global_includes,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectModel':
        """Create from dictionary (JSON deserialization)"""
        files = {path: FileModel.from_dict(file_data) for path, file_data in data['files'].items()}
        return cls(
            project_name=data['project_name'],
            project_roots=data['project_roots'],
            files=files,
            global_includes=data['global_includes'],
            created_at=data['created_at']
        )
    
    def save_to_json(self, file_path: str) -> None:
        """Save model to JSON file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load_from_json(cls, file_path: str) -> 'ProjectModel':
        """Load model from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

@dataclass
class FileModel:
    """Model representing a single C file and its parsed contents"""
    file_path: str
    relative_path: str
    project_root: str
    encoding_used: str
    structs: Dict[str, Struct]
    enums: Dict[str, Enum]
    functions: List[Function]
    globals: List[Field]
    includes: List[str]
    macros: List[str]
    typedefs: Dict[str, str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'file_path': self.file_path,
            'relative_path': self.relative_path,
            'project_root': self.project_root,
            'encoding_used': self.encoding_used,
            'structs': {name: asdict(struct) for name, struct in self.structs.items()},
            'enums': {name: asdict(enum) for name, enum in self.enums.items()},
            'functions': [asdict(func) for func in self.functions],
            'globals': [asdict(field) for field in self.globals],
            'includes': self.includes,
            'macros': self.macros,
            'typedefs': self.typedefs
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileModel':
        """Create from dictionary (JSON deserialization)"""
        # Reconstruct structs
        structs = {}
        for name, struct_data in data['structs'].items():
            fields = [Field(**field_data) for field_data in struct_data['fields']]
            functions = [Function(**func_data) for func_data in struct_data['functions']]
            structs[name] = Struct(
                name=struct_data['name'],
                fields=fields,
                functions=functions,
                typedef_name=struct_data.get('typedef_name')
            )
        
        # Reconstruct enums
        enums = {name: Enum(**enum_data) for name, enum_data in data['enums'].items()}
        
        # Reconstruct functions
        functions = []
        for func_data in data['functions']:
            parameters = [Field(**param_data) for param_data in func_data['parameters']]
            functions.append(Function(
                name=func_data['name'],
                return_type=func_data['return_type'],
                parameters=parameters,
                is_static=func_data['is_static']
            ))
        
        # Reconstruct globals
        globals_list = [Field(**field_data) for field_data in data['globals']]
        
        return cls(
            file_path=data['file_path'],
            relative_path=data['relative_path'],
            project_root=data['project_root'],
            encoding_used=data['encoding_used'],
            structs=structs,
            enums=enums,
            functions=functions,
            globals=globals_list,
            includes=data['includes'],
            macros=data['macros'],
            typedefs=data['typedefs']
        )