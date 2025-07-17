import json
from typing import Dict, Tuple
from ..models.c_structures import Struct, Enum

class JSONManipulator:
    def __init__(self):
        self.filters = {}
        self.transformations = {}
        self.styling = {}
    
    def load_config(self, json_path: str) -> None:
        """Load JSON configuration"""
        with open(json_path, 'r') as f:
            config = json.load(f)
        
        self.filters = config.get('filters', {})
        self.transformations = config.get('transformations', {})
        self.styling = config.get('styling', {})
    
    def apply_filters(self, structs: Dict[str, Struct], enums: Dict[str, Enum]) -> Tuple[Dict[str, Struct], Dict[str, Enum]]:
        """Apply filters to structs and enums"""
        filtered_structs = {}
        filtered_enums = {}
        
        # Filter structs
        include_structs = self.filters.get('include_structs', [])
        exclude_structs = self.filters.get('exclude_structs', [])
        
        for name, struct in structs.items():
            if include_structs and name not in include_structs:
                continue
            if exclude_structs and name in exclude_structs:
                continue
            filtered_structs[name] = struct
        
        # Filter enums
        include_enums = self.filters.get('include_enums', [])
        exclude_enums = self.filters.get('exclude_enums', [])
        
        for name, enum in enums.items():
            if include_enums and name not in include_enums:
                continue
            if exclude_enums and name in exclude_enums:
                continue
            filtered_enums[name] = enum
        
        return filtered_structs, filtered_enums
    
    def apply_transformations(self, structs: Dict[str, Struct], enums: Dict[str, Enum]) -> Tuple[Dict[str, Struct], Dict[str, Enum]]:
        """Apply transformations to structs and enums"""
        # Rename structs
        renames = self.transformations.get('rename_structs', {})
        for old_name, new_name in renames.items():
            if old_name in structs:
                struct = structs.pop(old_name)
                struct.name = new_name
                structs[new_name] = struct
        
        # Rename enums
        renames = self.transformations.get('rename_enums', {})
        for old_name, new_name in renames.items():
            if old_name in enums:
                enum = enums.pop(old_name)
                enum.name = new_name
                enums[new_name] = enum
        
        return structs, enums 