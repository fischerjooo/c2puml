from typing import Dict, List
from ..models.c_structures import Field, Function, Struct, Enum

class PlantUMLGenerator:
    def __init__(self):
        self.output = []
    
    def generate(self, structs: Dict[str, Struct], enums: Dict[str, Enum], styling: Dict = None) -> str:
        """Generate PlantUML class diagram"""
        self.output = []
        
        # Header
        self.output.append("@startuml")
        self.output.append("!theme plain")
        self.output.append("")
        
        # Apply styling if provided
        if styling:
            self._apply_styling(styling)
        
        # Generate enums
        for enum in enums.values():
            self._generate_enum(enum)
        
        # Generate structs
        for struct in structs.values():
            self._generate_struct(struct)
        
        # Generate relationships
        self._generate_relationships(structs)
        
        # Footer
        self.output.append("@enduml")
        
        return '\n'.join(self.output)
    
    def _apply_styling(self, styling: Dict) -> None:
        """Apply styling configuration"""
        if 'colors' in styling:
            colors = styling['colors']
            for entity_type, color in colors.items():
                self.output.append(f"skinparam {entity_type} {color}")
        
        if 'layout' in styling:
            layout = styling['layout']
            self.output.append(f"!define DIRECTION {layout}")
        
        self.output.append("")
    
    def _generate_enum(self, enum: Enum) -> None:
        """Generate enum definition"""
        display_name = enum.typedef_name or enum.name
        self.output.append(f"enum {display_name} {{")
        
        for value in enum.values:
            self.output.append(f"  {value}")
        
        self.output.append("}")
        self.output.append("")
    
    def _generate_struct(self, struct: Struct) -> None:
        """Generate struct definition"""
        display_name = struct.typedef_name or struct.name
        self.output.append(f"class {display_name} {{")
        
        # Fields
        if struct.fields:
            for field in struct.fields:
                field_str = self._format_field(field)
                self.output.append(f"  {field_str}")
        
        # Separator between fields and methods
        if struct.fields and struct.functions:
            self.output.append("  --")
        
        # Functions
        if struct.functions:
            for func in struct.functions:
                func_str = self._format_function(func)
                self.output.append(f"  {func_str}")
        
        self.output.append("}")
        self.output.append("")
    
    def _format_field(self, field: Field) -> str:
        """Format field for PlantUML"""
        type_str = field.type
        if field.is_pointer:
            type_str += "*"
        if field.is_array:
            type_str += f"[{field.array_size or ''}]"
        
        return f"{type_str} {field.name}"
    
    def _format_function(self, func: Function) -> str:
        """Format function for PlantUML"""
        params_str = ", ".join([f"{p.type} {p.name}" for p in func.parameters])
        visibility = "-" if func.is_static else "+"
        return f"{visibility}{func.return_type} {func.name}({params_str})"
    
    def _generate_relationships(self, structs: Dict[str, Struct]) -> None:
        """Generate relationships between structs"""
        for struct in structs.values():
            struct_name = struct.typedef_name or struct.name
            
            for field in struct.fields:
                # Check if field type is another struct
                field_type = field.type.replace('struct ', '')
                if field_type in structs:
                    target_name = structs[field_type].typedef_name or field_type
                    if field.is_pointer:
                        self.output.append(f"{struct_name} --> {target_name}")
                    else:
                        self.output.append(f"{struct_name} *-- {target_name}") 