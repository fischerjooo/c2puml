"""Processing anonymous structures within typedefs."""

import re
from typing import Dict, List, Tuple, Optional
from ..models import FileModel, Struct, Union, Field, Alias


class AnonymousTypedefProcessor:
    """Handles extraction and processing of anonymous structures within typedefs."""

    def __init__(self):
        self.anonymous_counters: Dict[str, Dict[str, int]] = {}  # parent -> {type -> count}

    def process_file_model(self, file_model: FileModel) -> None:
        """Process all typedefs in a file model to extract anonymous structures."""
        # Process aliases (function pointer typedefs)
        aliases_to_process = list(file_model.aliases.items())
        for alias_name, alias_data in aliases_to_process:
            self._process_alias_for_anonymous_structs(file_model, alias_name, alias_data)

        # Process struct typedefs
        structs_to_process = list(file_model.structs.items())
        for struct_name, struct_data in structs_to_process:
            self._process_struct_for_anonymous_structs(file_model, struct_name, struct_data)

        # Process union typedefs  
        unions_to_process = list(file_model.unions.items())
        for union_name, union_data in unions_to_process:
            self._process_union_for_anonymous_structs(file_model, union_name, union_data)

    def _process_alias_for_anonymous_structs(
        self, file_model: FileModel, alias_name: str, alias_data: Alias
    ) -> None:
        """Process an alias typedef to extract anonymous structures."""
        original_type = alias_data.original_type
        
        # Find anonymous struct patterns in function pointer parameters
        anonymous_structs = self._extract_anonymous_structs_from_text(original_type)
        
        if anonymous_structs:
            for i, (struct_content, struct_type) in enumerate(anonymous_structs, 1):
                anon_name = self._generate_anonymous_name(alias_name, struct_type, i)
                
                # Create the anonymous struct/union
                if struct_type == "struct":
                    anon_struct = self._create_anonymous_struct(anon_name, struct_content)
                    file_model.structs[anon_name] = anon_struct
                elif struct_type == "union":
                    anon_union = self._create_anonymous_union(anon_name, struct_content)
                    file_model.unions[anon_name] = anon_union
                
                # Track the relationship
                if alias_name not in file_model.anonymous_relationships:
                    file_model.anonymous_relationships[alias_name] = []
                file_model.anonymous_relationships[alias_name].append(anon_name)
                
                # Replace the anonymous structure in the original type with a reference
                updated_type = self._replace_anonymous_struct_with_reference(
                    original_type, struct_content, anon_name, struct_type
                )
                alias_data.original_type = updated_type

    def _process_struct_for_anonymous_structs(
        self, file_model: FileModel, struct_name: str, struct_data: Struct
    ) -> None:
        """Process a struct to extract anonymous nested structures."""
        # Check fields for anonymous structs/unions
        for field in struct_data.fields:
            if self._field_contains_anonymous_struct(field):
                # Process this field for anonymous structures
                self._extract_anonymous_from_field(file_model, struct_name, field)

    def _process_union_for_anonymous_structs(
        self, file_model: FileModel, union_name: str, union_data: Union
    ) -> None:
        """Process a union to extract anonymous nested structures."""
        # Check fields for anonymous structs/unions
        for field in union_data.fields:
            if self._field_contains_anonymous_struct(field):
                # Process this field for anonymous structures
                self._extract_anonymous_from_field(file_model, union_name, field)

    def _extract_anonymous_structs_from_text(
        self, text: str
    ) -> List[Tuple[str, str]]:
        """Extract anonymous struct/union definitions from text."""
        anonymous_structs = []
        
        # Pattern to match anonymous struct/union: struct { ... } or union { ... }
        pattern = r'(struct|union)\s*\{\s*([^{}]*(?:\{[^{}]*\}[^{}]*)*)\s*\}'
        
        matches = re.finditer(pattern, text, re.DOTALL)
        for match in matches:
            struct_type = match.group(1)  # 'struct' or 'union'
            struct_content = match.group(2).strip()
            anonymous_structs.append((struct_content, struct_type))
        
        return anonymous_structs

    def _generate_anonymous_name(self, parent_name: str, struct_type: str, counter: int) -> str:
        """Generate a name for an anonymous structure."""
        return f"{parent_name}_anonymous_{struct_type}_{counter}"

    def _create_anonymous_struct(self, name: str, content: str) -> Struct:
        """Create a Struct object from anonymous content."""
        fields = self._parse_struct_fields(content)
        return Struct(name=name, fields=fields)

    def _create_anonymous_union(self, name: str, content: str) -> Union:
        """Create a Union object from anonymous content."""
        fields = self._parse_struct_fields(content)
        return Union(name=name, fields=fields)

    def _parse_struct_fields(self, content: str) -> List[Field]:
        """Parse field definitions from struct/union content."""
        fields = []
        
        # Simple field parsing - split by semicolons and extract type/name
        field_declarations = [f.strip() for f in content.split(';') if f.strip()]
        
        for decl in field_declarations:
            if not decl:
                continue
                
            # Handle function pointer fields: void (*name)(int)
            if '(*' in decl and ')(' in decl:
                # Extract function pointer name
                func_ptr_match = re.search(r'\(\*\s*(\w+)\s*\)', decl)
                if func_ptr_match:
                    field_name = func_ptr_match.group(1)
                    field_type = decl.strip()
                    fields.append(Field(name=field_name, type=field_type))
                continue
            
            # Regular field: type name, type name1, name2
            parts = decl.strip().split()
            if len(parts) >= 2:
                # Handle multiple declarations: int a, b, c;
                if ',' in decl:
                    # Split by comma and process each
                    type_and_first = ' '.join(parts[:-1]) if len(parts) > 1 else parts[0]
                    remaining = parts[-1]
                    
                    # Find the type (everything before the first name)
                    type_parts = type_and_first.split()
                    if len(type_parts) >= 2:
                        field_type = ' '.join(type_parts[:-1])
                        first_name = type_parts[-1].rstrip(',')
                        fields.append(Field(name=first_name, type=field_type))
                        
                        # Process remaining names
                        for name in remaining.split(','):
                            name = name.strip().rstrip(',')
                            if name:
                                fields.append(Field(name=name, type=field_type))
                else:
                    # Single declaration: type name
                    field_type = ' '.join(parts[:-1])
                    field_name = parts[-1]
                    fields.append(Field(name=field_name, type=field_type))
        
        return fields

    def _replace_anonymous_struct_with_reference(
        self, original_type: str, struct_content: str, anon_name: str, struct_type: str
    ) -> str:
        """Replace anonymous struct definition with reference to named typedef."""
        # Pattern to match the full anonymous struct: struct { content }
        pattern = rf'{struct_type}\s*\{{\s*{re.escape(struct_content)}\s*\}}'
        replacement = anon_name
        
        # Replace the anonymous struct with just the name
        updated_type = re.sub(pattern, replacement, original_type, flags=re.DOTALL)
        return updated_type

    def _field_contains_anonymous_struct(self, field: Field) -> bool:
        """Check if a field contains an anonymous struct/union definition."""
        return 'struct {' in field.type or 'union {' in field.type

    def _extract_anonymous_from_field(
        self, file_model: FileModel, parent_name: str, field: Field
    ) -> None:
        """Extract anonymous structures from a field definition."""
        anonymous_structs = self._extract_anonymous_structs_from_text(field.type)
        
        if anonymous_structs:
            for i, (struct_content, struct_type) in enumerate(anonymous_structs, 1):
                anon_name = self._generate_anonymous_name(parent_name, struct_type, i)
                
                # Create the anonymous struct/union
                if struct_type == "struct":
                    anon_struct = self._create_anonymous_struct(anon_name, struct_content)
                    file_model.structs[anon_name] = anon_struct
                elif struct_type == "union":
                    anon_union = self._create_anonymous_union(anon_name, struct_content)
                    file_model.unions[anon_name] = anon_union
                
                # Track the relationship
                if parent_name not in file_model.anonymous_relationships:
                    file_model.anonymous_relationships[parent_name] = []
                file_model.anonymous_relationships[parent_name].append(anon_name)
                
                # Update the field type to reference the named structure
                field.type = self._replace_anonymous_struct_with_reference(
                    field.type, struct_content, anon_name, struct_type
                )