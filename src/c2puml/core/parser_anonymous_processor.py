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
        # Skip alias processing for now to focus on simpler struct/union cases
        # aliases_to_process = list(file_model.aliases.items())
        # for alias_name, alias_data in aliases_to_process:
        #     self._process_alias_for_anonymous_structs(file_model, alias_name, alias_data)

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
        
        # Filter out overly complex structures that might cause parsing issues
        filtered_structs = []
        for struct_content, struct_type in anonymous_structs:
            # Skip structures with function pointer arrays or other complex patterns
            if not self._is_too_complex_to_process(struct_content):
                filtered_structs.append((struct_content, struct_type))
        
        if filtered_structs:
            for i, (struct_content, struct_type) in enumerate(filtered_structs, 1):
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
        """Extract anonymous struct/union definitions from text using balanced brace matching."""
        anonymous_structs = []
        
        # Look for struct/union keywords followed by {
        pattern = r'(struct|union)\s*\{'
        
        for match in re.finditer(pattern, text):
            struct_type = match.group(1)
            start_pos = match.end() - 1  # Position of the opening brace
            
            # Find the matching closing brace using balanced brace counting
            brace_count = 0
            pos = start_pos
            
            while pos < len(text):
                if text[pos] == '{':
                    brace_count += 1
                elif text[pos] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # Found the matching closing brace
                        struct_content = text[start_pos + 1:pos].strip()
                        if struct_content:  # Only add non-empty content
                            anonymous_structs.append((struct_content, struct_type))
                        break
                pos += 1
        
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
        
        # Clean up the content first
        content = content.strip()
        if not content:
            return fields
        
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
            
            # Handle array declarations: type name[size] or type name[]
            array_match = re.match(r'(.+?)\s+(\w+)\s*\[([^\]]*)\]\s*$', decl)
            if array_match:
                field_type = array_match.group(1).strip()
                field_name = array_match.group(2).strip()
                array_size = array_match.group(3).strip()
                if array_size:
                    full_type = f"{field_type}[{array_size}]"
                else:
                    full_type = f"{field_type}[]"
                fields.append(Field(name=field_name, type=full_type))
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
                    # Clean up field name (remove trailing punctuation)
                    field_name = re.sub(r'[^\w]', '', field_name)
                    if field_name:  # Only add if we have a valid name
                        fields.append(Field(name=field_name, type=field_type))
        
        return fields

    def _is_too_complex_to_process(self, struct_content: str) -> bool:
        """Check if a struct is too complex to safely process."""
        # Skip structures with function pointer arrays as they're too complex
        if 'handlers[' in struct_content or '(*' in struct_content and '[' in struct_content:
            return True
        
        # Skip all function pointer related structures for now
        if '(*' in struct_content or 'handler' in struct_content.lower():
            return True
        
        # Skip structures with very deeply nested braces (more than 3 levels)
        brace_depth = 0
        max_depth = 0
        for char in struct_content:
            if char == '{':
                brace_depth += 1
                max_depth = max(max_depth, brace_depth)
            elif char == '}':
                brace_depth -= 1
        
        if max_depth > 3:
            return True
        
        # Skip structures that are too large (more than 500 characters)
        if len(struct_content) > 500:
            return True
        
        return False

    def _replace_anonymous_struct_with_reference(
        self, original_type: str, struct_content: str, anon_name: str, struct_type: str
    ) -> str:
        """Replace anonymous struct definition with reference to named typedef."""
        # Use a more robust approach to find and replace the anonymous struct
        # Look for the exact pattern: struct_type { struct_content }
        
        # Escape special regex characters in struct_content but preserve structure
        escaped_content = re.escape(struct_content)
        # Un-escape some characters we want to match flexibly
        escaped_content = escaped_content.replace(r'\ ', r'\s*').replace(r'\n', r'\s*')
        
        # Pattern to match the full anonymous struct with flexible whitespace
        pattern = rf'{struct_type}\s*\{{\s*{escaped_content}\s*\}}'
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