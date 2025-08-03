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
        # Process alias typedefs with improved complexity filtering
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
        
        # Filter out overly complex structures that might cause parsing issues
        filtered_structs = []
        for struct_content, struct_type in anonymous_structs:
            # Skip structures with function pointer arrays or other complex patterns
            if not self._is_too_complex_to_process(struct_content):
                filtered_structs.append((struct_content, struct_type))
        
        if filtered_structs:
            for i, (struct_content, struct_type) in enumerate(filtered_structs, 1):
                anon_name = self._generate_anonymous_name(alias_name, struct_type, counter=i)
                
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
        
        # Check if this text starts with 'typedef struct' - if so, skip the outer struct
        text_stripped = text.strip()
        skip_first_struct = text_stripped.startswith('typedef struct') or text_stripped.startswith('typedef union')
        
        # Look for struct/union keywords followed by {
        pattern = r'(struct|union)\s*\{'
        first_match_skipped = False
        
        for match in re.finditer(pattern, text):
            struct_type = match.group(1)
            start_pos = match.end() - 1  # Position of the opening brace
            
            # Skip the first struct/union if it's a typedef outer structure
            if skip_first_struct and not first_match_skipped:
                first_match_skipped = True
                continue
            
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

    def _generate_anonymous_name(self, parent_name: str, struct_type: str, counter: int = None, field_name: str = None) -> str:
        """Generate a meaningful name for an anonymous structure.
        
        Uses the improved naming convention: ParentType_fieldName when field_name is available,
        otherwise falls back to the counter-based approach.
        """
        if field_name:
            return f"{parent_name}_{field_name}"
        else:
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
            
            # Handle comma-separated declarations: int a, b, c; char *ptr1, *ptr2;
            if ',' in decl:
                fields.extend(self._parse_comma_separated_fields(decl))
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
            
            # Regular single field: type name
            parts = decl.strip().split()
            if len(parts) >= 2:
                field_type = ' '.join(parts[:-1])
                field_name = parts[-1]
                # Clean up field name (remove trailing punctuation)
                field_name = re.sub(r'[^\w]', '', field_name)
                if field_name:  # Only add if we have a valid name
                    fields.append(Field(name=field_name, type=field_type))
        
        return fields

    def _parse_comma_separated_fields(self, decl: str) -> List[Field]:
        """Parse comma-separated field declarations like 'int a, b, c;' or 'char *ptr1, *ptr2;'."""
        fields = []
        
        # Split by comma to get individual field parts
        field_parts = [part.strip() for part in decl.split(',')]
        if not field_parts:
            return fields
            
        # Parse the first field to get the base type
        first_field = field_parts[0].strip()
        
        # Handle array case for first field: int arr1[10], arr2[20]
        array_match = re.match(r'(.+?)\s+(\w+)\s*\[([^\]]*)\]\s*$', first_field)
        if array_match:
            base_type = array_match.group(1).strip()
            first_name = array_match.group(2).strip()
            first_size = array_match.group(3).strip()
            
            if first_size:
                first_type = f"{base_type}[{first_size}]"
            else:
                first_type = f"{base_type}[]"
            fields.append(Field(name=first_name, type=first_type))
            
            # Process remaining fields as arrays
            for part in field_parts[1:]:
                part = part.strip()
                # Look for array syntax: arr2[20]
                array_match = re.match(r'(\w+)\s*\[([^\]]*)\]\s*$', part)
                if array_match:
                    name = array_match.group(1).strip()
                    size = array_match.group(2).strip()
                    if size:
                        field_type = f"{base_type}[{size}]"
                    else:
                        field_type = f"{base_type}[]"
                    fields.append(Field(name=name, type=field_type))
                else:
                    # Simple name without array - treat as simple field
                    name = re.sub(r'[^\w]', '', part)
                    if name:
                        fields.append(Field(name=name, type=base_type))
            return fields
        
        # Parse first field normally to extract base type
        first_parts = first_field.split()
        if len(first_parts) < 2:
            return fields
            
        # Extract base type and first field name
        base_type = ' '.join(first_parts[:-1])
        first_name = first_parts[-1]
        
        # Handle pointer syntax: char *ptr1, *ptr2
        if first_name.startswith('*'):
            base_type += " *"
            first_name = first_name[1:]  # Remove leading *
        
        # Clean up first field name
        first_name = re.sub(r'[^\w]', '', first_name)
        if first_name:
            fields.append(Field(name=first_name, type=base_type))
        
        # Process remaining fields
        for part in field_parts[1:]:
            part = part.strip()
            if not part:
                continue
                
            # Handle pointer syntax: *ptr2
            field_type = base_type
            if part.startswith('*'):
                if not base_type.endswith('*'):
                    field_type = base_type + " *"
                part = part[1:]  # Remove leading *
            
            # Clean up field name
            field_name = re.sub(r'[^\w]', '', part)
            if field_name:
                fields.append(Field(name=field_name, type=field_type))
        
        return fields

    def _is_too_complex_to_process(self, struct_content: str) -> bool:
        """Check if a struct is too complex to safely process."""
        # Skip structures with function pointer arrays as they're too complex
        if 'handlers[' in struct_content or ('(*' in struct_content and '[' in struct_content):
            return True
        
        # Skip structures with multiple function pointers (complex cases)
        func_ptr_count = struct_content.count('(*')
        if func_ptr_count > 2:
            return True
        
        # Skip structures with deeply nested function pointers
        if '(*' in struct_content and '(*' in struct_content[struct_content.find('(*') + 2:]:
            # Check if there are nested function pointers within function pointers
            first_func_ptr = struct_content.find('(*')
            if first_func_ptr != -1:
                # Find the closing ) for the first function pointer
                paren_count = 0
                pos = first_func_ptr + 2
                while pos < len(struct_content):
                    if struct_content[pos] == '(':
                        paren_count += 1
                    elif struct_content[pos] == ')':
                        if paren_count == 0:
                            # Check if there's another function pointer after this one
                            remaining = struct_content[pos:]
                            if '(*' in remaining:
                                return True
                            break
                        paren_count -= 1
                    pos += 1
        
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
        # Check for simplified anonymous structures (created by find_struct_fields)
        if field.type in ["union { ... }", "struct { ... }"]:
            return True
        
        # Check for patterns like "struct { ... } field_name" or "union { ... } field_name"
        if re.match(r'^(struct|union)\s*\{\s*\.\.\.\s*\}\s+\w+', field.type):
            return True
        
        # Check for actual anonymous struct/union patterns like "struct { int x; } nested"
        if re.search(r'(struct|union)\s*\{[^}]*\}\s+\w+', field.type):
            return True
        
        # Check for anonymous structs without field names like "struct { int x; }"
        if re.search(r'(struct|union)\s*\{[^}]*\}(?!\s*\w)', field.type):
            return True
        
        return False

    def _extract_anonymous_from_field(
        self, file_model: FileModel, parent_name: str, field: Field
    ) -> None:
        """Extract anonymous structures from a field definition."""
        # Handle simplified anonymous structure types
        if field.type in ["struct { ... }", "union { ... }"]:
            struct_type = "struct" if "struct" in field.type else "union"
            anon_name = self._generate_anonymous_name(parent_name, struct_type, field_name=field.name)
            
            # Create a placeholder anonymous struct/union
            if struct_type == "struct":
                anon_struct = Struct(anon_name, [], tag_name="")
                file_model.structs[anon_name] = anon_struct
            elif struct_type == "union":
                anon_union = Union(anon_name, [], tag_name="")
                file_model.unions[anon_name] = anon_union
            
            # Track the relationship
            if parent_name not in file_model.anonymous_relationships:
                file_model.anonymous_relationships[parent_name] = []
            file_model.anonymous_relationships[parent_name].append(anon_name)
            
            # Update the field type to reference the named structure
            field.type = anon_name
            
        # Handle preserved content format: "struct { /*ANON:encoded_content:field_name*/ ... }"
        elif re.search(r'/\*ANON:([^:]+):([^*]+)\*/', field.type):
            struct_match = re.search(r'(struct|union)', field.type)
            content_match = re.search(r'/\*ANON:([^:]+):([^*]+)\*/', field.type)
            if struct_match and content_match:
                struct_type = struct_match.group(1)
                encoded_content = content_match.group(1)
                field_name = content_match.group(2)
                
                # Decode the preserved content
                import base64
                try:
                    content = base64.b64decode(encoded_content).decode()
                    anon_name = self._generate_anonymous_name(parent_name, struct_type, field_name=field_name)
                    
                    # Parse the content to create the structure with actual fields
                    if struct_type == "struct":
                        anon_struct = self._create_anonymous_struct(anon_name, content)
                        file_model.structs[anon_name] = anon_struct
                    elif struct_type == "union":
                        anon_union = self._create_anonymous_union(anon_name, content)
                        file_model.unions[anon_name] = anon_union
                    
                    # Track the relationship
                    if parent_name not in file_model.anonymous_relationships:
                        file_model.anonymous_relationships[parent_name] = []
                    file_model.anonymous_relationships[parent_name].append(anon_name)
                    
                    # Update the field type to reference the named structure  
                    field.type = anon_name
                    
                except Exception as e:
                    # If decoding fails, fall back to placeholder
                    print(f"Warning: Failed to decode anonymous structure content: {e}")
                    import traceback
                    traceback.print_exc()
            
        # Handle patterns like "struct { ... } field_name"
        elif re.match(r'^(struct|union)\s*\{\s*\.\.\.\s*\}\s+\w+', field.type):
            match = re.match(r'^(struct|union)\s*\{\s*\.\.\.\s*\}\s+(\w+)', field.type)
            if match:
                struct_type = match.group(1)
                field_name = match.group(2)
                anon_name = self._generate_anonymous_name(parent_name, struct_type, field_name=field_name)
                
                # Create a placeholder anonymous struct/union
                if struct_type == "struct":
                    anon_struct = Struct(anon_name, [], tag_name="")
                    file_model.structs[anon_name] = anon_struct
                elif struct_type == "union":
                    anon_union = Union(anon_name, [], tag_name="")
                    file_model.unions[anon_name] = anon_union
                
                # Track the relationship
                if parent_name not in file_model.anonymous_relationships:
                    file_model.anonymous_relationships[parent_name] = []
                file_model.anonymous_relationships[parent_name].append(anon_name)
                
                # Update the field type to reference the named structure
                field.type = f"{anon_name} {field_name}"
        
        # Handle actual anonymous struct/union patterns like "struct { int x; } nested"
        elif re.search(r'(struct|union)\s*\{[^}]*\}\s+\w+', field.type):
            # Extract the anonymous struct content and field name
            match = re.search(r'((struct|union)\s*\{[^}]*\})\s+(\w+)', field.type)
            if match:
                struct_content = match.group(1)
                struct_type = match.group(2)
                field_name = match.group(3)
                anon_name = self._generate_anonymous_name(parent_name, struct_type, field_name=field_name)
                
                # Create the anonymous struct/union with actual content
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
                field.type = f"{anon_name} {field_name}"
        
        # Handle anonymous structs without field names like "struct { int x; }"
        elif re.search(r'(struct|union)\s*\{[^}]*\}(?!\s*\w)', field.type):
            # Extract the anonymous struct content
            match = re.search(r'((struct|union)\s*\{[^}]*\})', field.type)
            if match:
                struct_content = match.group(1)
                struct_type = match.group(2)
                # For anonymous structs without field names, use counter-based naming
                anon_name = self._generate_anonymous_name(parent_name, struct_type, counter=1)
                
                # Create the anonymous struct/union with actual content
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
                field.type = anon_name
        
        # Handle complex anonymous structures (original logic)
        else:
            anonymous_structs = self._extract_anonymous_structs_from_text(field.type)
            
            if anonymous_structs:
                for i, (struct_content, struct_type) in enumerate(anonymous_structs, 1):
                    anon_name = self._generate_anonymous_name(parent_name, struct_type, counter=i)
                    
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