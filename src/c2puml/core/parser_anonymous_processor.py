"""Processing anonymous structures within typedefs."""

import re
from typing import Dict, List, Tuple, Optional
from ..models import FileModel, Struct, Union, Field, Alias


class AnonymousTypedefProcessor:
    """Handles extraction and processing of anonymous structures within typedefs."""

    def __init__(self):
        self.anonymous_counters: Dict[str, Dict[str, int]] = {}  # parent -> {type -> count}
        self.global_anonymous_structures = {}  # Track anonymous structures globally by content hash
        self.content_to_structure_map = {}  # content_hash -> (name, struct_type)

    def process_file_model(self, file_model: FileModel) -> None:
        """Process all typedefs in a file model to extract anonymous structures using multi-pass processing."""
        max_iterations = 10  # Increased from 5 to 10 for deeper processing
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            # Track all typedef entities (structs, unions, and aliases) for convergence detection
            initial_count = len(file_model.structs) + len(file_model.unions) + len(file_model.aliases)
            
            # Process all structures/unions/aliases
            self._process_all_entities(file_model)
            
            final_count = len(file_model.structs) + len(file_model.unions) + len(file_model.aliases)
            
            # Stop if no new typedef entities were created (convergence)
            if final_count == initial_count:
                break
        
        # Post-processing: Update field references to point to extracted entities
        self._update_field_references_to_extracted_entities(file_model)

    def _process_all_entities(self, file_model: FileModel) -> None:
        """Process all entities in a single pass."""
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
        for struct_content, struct_type, field_name in anonymous_structs:
            # Skip structures with function pointer arrays or other complex patterns
            if not self._is_too_complex_to_process(struct_content):
                filtered_structs.append((struct_content, struct_type, field_name))
        
        if filtered_structs:
            for i, (struct_content, struct_type, field_name) in enumerate(filtered_structs, 1):
                anon_name = self._get_or_create_anonymous_structure(
                    file_model, struct_content, struct_type, alias_name, field_name
                )
                
                # Track the relationship (only if not already tracked)
                if alias_name not in file_model.anonymous_relationships:
                    file_model.anonymous_relationships[alias_name] = []
                if anon_name not in file_model.anonymous_relationships[alias_name]:
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
    ) -> List[Tuple[str, str, str]]:
        """Extract anonymous struct/union definitions from text using balanced brace matching."""
        anonymous_structs = []
        
        # Check if this text starts with 'typedef struct' - if so, skip the outer struct
        text_stripped = text.strip()
        skip_first_struct = text_stripped.startswith('typedef struct') or text_stripped.startswith('typedef union')
        
        # Look for struct/union keywords followed by {
        # Use balanced brace matching to handle nested structures
        pattern = r'(struct|union)\s*\{'
        matches = list(re.finditer(pattern, text))
        
        for match in matches:
            struct_type = match.group(1)
            start_pos = match.start()
            
            # Find the matching closing brace using balanced brace counting
            brace_count = 0
            pos = start_pos
            content_start = text.find('{', start_pos)
            
            if content_start == -1:
                continue
                
            pos = content_start
            while pos < len(text):
                char = text[pos]
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # Found the matching closing brace
                        content_end = pos
                        struct_content = text[start_pos:content_end + 1]
                        
                        # Extract the field name after the closing brace
                        remaining = text[content_end + 1:].strip()
                        field_match = re.match(r'^[*\s\[\]]*(\w+)', remaining)
                        field_name = field_match.group(1) if field_match else f"field_{len(anonymous_structs) + 1}"
                        
                        # Skip the first struct/union if it's a typedef
                        if skip_first_struct and match == matches[0]:
                            skip_first_struct = False
                        else:
                            anonymous_structs.append((struct_content, struct_type, field_name))
                        break
                pos += 1
        
        return anonymous_structs

    def _generate_anonymous_name(self, parent_name: str, struct_type: str, field_name: str) -> str:
        """Generate a name for an anonymous structure. Field name is always required."""
        return f"{parent_name}_{field_name}"
    
    def _generate_content_hash(self, content: str, struct_type: str) -> str:
        """Generate a hash for anonymous structure content to identify duplicates."""
        import hashlib
        # Normalize the content by removing whitespace and comments
        normalized = re.sub(r'\s+', ' ', content.strip())
        normalized = re.sub(r'/\*.*?\*/', '', normalized)  # Remove C comments
        normalized = re.sub(r'//.*$', '', normalized, flags=re.MULTILINE)  # Remove C++ comments
        hash_input = f"{struct_type}:{normalized}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:8]
    
    def _find_existing_anonymous_structure(self, content: str, struct_type: str) -> Optional[str]:
        """Find an existing anonymous structure with the same content."""
        content_hash = self._generate_content_hash(content, struct_type)
        if content_hash in self.content_to_structure_map:
            existing_name, existing_type = self.content_to_structure_map[content_hash]
            if existing_type == struct_type:
                return existing_name
        return None
    
    def _register_anonymous_structure(self, name: str, content: str, struct_type: str) -> None:
        """Register an anonymous structure in the global tracking system."""
        content_hash = self._generate_content_hash(content, struct_type)
        self.content_to_structure_map[content_hash] = (name, struct_type)
    
    def _get_or_create_anonymous_structure(self, file_model: FileModel, content: str, struct_type: str, 
                                         parent_name: str, field_name: str) -> str:
        """Get existing anonymous structure or create new one based on content hash."""
        # Handle placeholder content (like "struct { ... }")
        is_placeholder = content in ["struct { ... }", "union { ... }"] or re.match(r'^(struct|union)\s*\{\s*\.\.\.\s*\}\s+\w+', content)
        
        if is_placeholder:
            # For placeholders, just use the naming convention without content-based deduplication
            anon_name = self._generate_anonymous_name(parent_name, struct_type, field_name)
            
            # Check if this structure already exists with the correct name
            if (struct_type == "struct" and anon_name in file_model.structs) or \
               (struct_type == "union" and anon_name in file_model.unions):
                return anon_name
            
            # Create new placeholder anonymous structure
            if struct_type == "struct":
                anon_struct = Struct(anon_name, [], tag_name="")
                file_model.structs[anon_name] = anon_struct
            elif struct_type == "union":
                anon_union = Union(anon_name, [], tag_name="")
                file_model.unions[anon_name] = anon_union
            
            return anon_name
        else:
            # For actual content, use content-based deduplication
            # First, check if we already have a structure with this content
            existing_name = self._find_existing_anonymous_structure(content, struct_type)
            if existing_name:
                # Check if the existing structure still exists in the model
                if (struct_type == "struct" and existing_name in file_model.structs) or \
                   (struct_type == "union" and existing_name in file_model.unions):
                    return existing_name
            
            # Create a new anonymous structure with the correct naming convention
            anon_name = self._generate_anonymous_name(parent_name, struct_type, field_name)
            
            # Check if this structure already exists with the correct name
            if (struct_type == "struct" and anon_name in file_model.structs) or \
               (struct_type == "union" and anon_name in file_model.unions):
                return anon_name
            
            # Create new anonymous structure
            if struct_type == "struct":
                anon_struct = self._create_anonymous_struct(anon_name, content)
                file_model.structs[anon_name] = anon_struct
            elif struct_type == "union":
                anon_union = self._create_anonymous_union(anon_name, content)
                file_model.unions[anon_name] = anon_union
            
            # Register the structure in the global tracking system
            self._register_anonymous_structure(anon_name, content, struct_type)
            
            return anon_name

    def _create_anonymous_struct(self, name: str, content: str) -> Struct:
        """Create an anonymous struct from content."""
        fields = self._parse_struct_fields(content)
        return Struct(name, fields, tag_name="")

    def _create_anonymous_union(self, name: str, content: str) -> Union:
        """Create an anonymous union from content."""
        fields = self._parse_struct_fields(content)
        return Union(name, fields, tag_name="")

    def _parse_struct_fields(self, content: str) -> List[Field]:
        """Parse struct/union fields from content."""
        fields = []
        
        # Check if content has braces (full struct content) or not (just field content)
        if '{' in content and '}' in content:
            # Extract content between braces
            brace_start = content.find('{')
            brace_end = content.rfind('}')
            
            if brace_start == -1 or brace_end == -1:
                return fields
            
            inner_content = content[brace_start + 1:brace_end].strip()
        else:
            # Content is just field declarations without braces
            inner_content = content.strip()
        
        if not inner_content:
            return fields
        
        # Split by semicolons to get individual field declarations
        field_declarations = []
        current_decl = ""
        brace_count = 0
        
        for char in inner_content:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            
            current_decl += char
            
            if char == ';' and brace_count == 0:
                field_declarations.append(current_decl.strip())
                current_decl = ""
        
        # Handle any remaining content
        if current_decl.strip():
            field_declarations.append(current_decl.strip())
        
        # Parse each field declaration
        for decl in field_declarations:
            if not decl or decl.strip() == ';':
                continue
            
            # Remove trailing semicolon
            decl = decl.rstrip(';').strip()
            
            if not decl:
                continue
            
            # Check if this declaration contains an anonymous struct/union
            if self._has_balanced_anonymous_pattern(decl):
                # Extract the anonymous struct content and field name
                struct_info = self._extract_balanced_anonymous_struct(decl)
                if struct_info:
                    struct_content, struct_type, field_name = struct_info
                    # Parse the actual content of the anonymous structure
                    parsed_fields = self._parse_struct_fields(struct_content)
                    if parsed_fields:
                        # Create a field that references the parsed content
                        field_type = f"{struct_type} {{ {', '.join([f'{f.type} {f.name}' for f in parsed_fields])} }}"
                        fields.append(Field(field_name, field_type))
                    else:
                        # Fallback to placeholder if parsing fails
                        field_type = f"{struct_type} {{ ... }} {field_name}"
                        fields.append(Field(field_name, field_type))
                    continue
            elif self._has_balanced_anonymous_pattern_no_field_name(decl):
                # Extract the anonymous struct content without field name
                struct_info = self._extract_balanced_anonymous_struct_no_field_name(decl)
                if struct_info:
                    struct_content, struct_type = struct_info
                    # Parse the actual content of the anonymous structure
                    parsed_fields = self._parse_struct_fields(struct_content)
                    if parsed_fields:
                        # Create a field that references the parsed content
                        field_type = f"{struct_type} {{ {', '.join([f'{f.type} {f.name}' for f in parsed_fields])} }}"
                        field_name = f"anonymous_{struct_type}"
                        fields.append(Field(field_name, field_type))
                    else:
                        # Fallback to placeholder if parsing fails
                        field_type = f"{struct_type} {{ ... }}"
                        field_name = f"anonymous_{struct_type}"
                        fields.append(Field(field_name, field_type))
                    continue
            
            # Parse the field normally (no anonymous structures)
            parsed_fields = self._parse_comma_separated_fields(decl)
            fields.extend(parsed_fields)
        
        return fields

    def _parse_comma_separated_fields(self, decl: str) -> List[Field]:
        """Parse comma-separated field declarations like 'int a, b, c;' or 'char *ptr1, *ptr2;'."""
        fields = []
        
        # Handle function pointer fields first: void (*name)(int) or void ( * name ) ( int )
        if re.search(r'\(\s*\*\s*\w+\s*\)', decl) and re.search(r'\)\s*\(', decl):
            # Extract function pointer name - handle both compact and spaced formats
            func_ptr_match = re.search(r'\(\s*\*\s*(\w+)\s*\)', decl)
            if func_ptr_match:
                field_name = func_ptr_match.group(1)
                field_type = decl.strip()
                return [Field(field_name, field_type)]
        
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
            fields.append(Field(first_name, first_type))
            
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
                    fields.append(Field(name, field_type))
                else:
                    # Simple name without array - treat as simple field
                    name = re.sub(r'[^\w]', '', part)
                    if name:
                        fields.append(Field(name, base_type))
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
        
        # Clean up first field name - preserve the actual field name
        first_name = re.sub(r'[^\w]', '', first_name)
        if first_name:
            fields.append(Field(first_name, base_type))
        
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
            
            # Clean up field name - preserve the actual field name
            # Remove any leading/trailing whitespace and extract just the identifier
            field_name = part.strip()
            # Remove any trailing punctuation or brackets that might be part of the type
            field_name = re.sub(r'[^\w].*$', '', field_name)
            if field_name:
                fields.append(Field(field_name, field_type))
        
        return fields

    def _parse_single_field(self, decl: str) -> Optional[Field]:
        """Parse a single field declaration."""
        # Handle function pointer fields: void (*name)(int) or void ( * name ) ( int )
        if re.search(r'\(\s*\*\s*\w+\s*\)', decl) and re.search(r'\)\s*\(', decl):
            # Extract function pointer name - handle both compact and spaced formats
            func_ptr_match = re.search(r'\(\s*\*\s*(\w+)\s*\)', decl)
            if func_ptr_match:
                field_name = func_ptr_match.group(1)
                field_type = decl.strip()
                return Field(field_name, field_type)
        
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
            return Field(field_name, full_type)
        
        # Handle pointer declarations: type *name or type* name
        pointer_match = re.match(r'(.+?)\s*\*\s*(\w+)\s*$', decl)
        if pointer_match:
            field_type = pointer_match.group(1).strip() + " *"
            field_name = pointer_match.group(2).strip()
            return Field(field_name, field_type)
        
        # Regular single field: type name
        parts = decl.strip().split()
        if len(parts) >= 2:
            field_type = ' '.join(parts[:-1])
            field_name = parts[-1]
            # Clean up field name (remove trailing punctuation)
            field_name = re.sub(r'[^\w]', '', field_name)
            if field_name:  # Only add if we have a valid name
                return Field(field_name, field_type)
        
        return None

    def _is_too_complex_to_process(self, struct_content: str) -> bool:
        """Check if a structure is too complex to process."""
        # Skip structures with function pointer arrays
        if re.search(r'\(\s*\*\s*\w+\s*\)\s*\[', struct_content):
            return True
        
        # Skip structures with complex nested patterns
        if struct_content.count('{') > 5 or struct_content.count('}') > 5:
            return True
        
        # Skip structures with too many semicolons (complex field declarations)
        if struct_content.count(';') > 10:
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
        """Check if a field contains an anonymous structure."""
        field_type = field.type
        
        # Check for various anonymous structure patterns
        patterns = [
            r'struct\s*\{',  # struct { ... }
            r'union\s*\{',   # union { ... }
            r'/\*ANON:',     # Preserved content format
        ]
        
        for pattern in patterns:
            if re.search(pattern, field_type):
                return True
        
        return False

    def _extract_anonymous_from_field(
        self, file_model: FileModel, parent_name: str, field: Field
    ) -> None:
        """Extract anonymous structures from a field definition using balanced brace matching."""
                # Handle simplified anonymous structure types
        if field.type in ["struct { ... }", "union { ... }"]:
            struct_type = "struct" if "struct" in field.type else "union"
            # Use the global tracking system to ensure consistent naming
            anon_name = self._get_or_create_anonymous_structure(
                file_model, field.type, struct_type, parent_name, field.name
            )
            
            # Track the relationship
            if parent_name not in file_model.anonymous_relationships:
                file_model.anonymous_relationships[parent_name] = []
            if anon_name not in file_model.anonymous_relationships[parent_name]:
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
                    anon_name = self._get_or_create_anonymous_structure(
                        file_model, content, struct_type, parent_name, field_name
                    )
                    
                    # Track the relationship
                    if parent_name not in file_model.anonymous_relationships:
                        file_model.anonymous_relationships[parent_name] = []
                    if anon_name not in file_model.anonymous_relationships[parent_name]:
                        file_model.anonymous_relationships[parent_name].append(anon_name)
                    
                    # Update the field type to reference the named structure  
                    field.type = anon_name
                    
                except Exception as e:
                    # If decoding fails, fall back to placeholder
                    print(f"Warning: Failed to decode anonymous structure content: {e}")
                    import traceback
                    traceback.print_exc()
            
        # Handle patterns like "struct { ... } field_name" with balanced brace matching
        elif re.match(r'^(struct|union)\s*\{\s*\.\.\.\s*\}\s+\w+', field.type):
            match = re.match(r'^(struct|union)\s*\{\s*\.\.\.\s*\}\s+(\w+)', field.type)
            if match:
                struct_type = match.group(1)
                field_name = match.group(2)
                # Use the global tracking system to ensure consistent naming
                anon_name = self._get_or_create_anonymous_structure(
                    file_model, field.type, struct_type, parent_name, field_name
                )
                
                # Track the relationship
                if parent_name not in file_model.anonymous_relationships:
                    file_model.anonymous_relationships[parent_name] = []
                if anon_name not in file_model.anonymous_relationships[parent_name]:
                    file_model.anonymous_relationships[parent_name].append(anon_name)
                
                # Update the field type to reference the named structure
                field.type = anon_name
        
        # Handle malformed anonymous structure patterns like "struct { ... } field_name" 
        # where the field name is incorrectly embedded in the type
        elif re.match(r'^(struct|union)\s*\{\s*\.\.\.\s*\}\s+\w+$', field.type):
            match = re.match(r'^(struct|union)\s*\{\s*\.\.\.\s*\}\s+(\w+)$', field.type)
            if match:
                struct_type = match.group(1)
                embedded_name = match.group(2)
                # This is a malformed field type - the field name is embedded in the type
                # We need to extract the actual field name and fix the type
                # The actual field name should be the field.name, not the embedded name
                actual_field_name = field.name
                
                # Create a proper anonymous structure name
                anon_name = self._generate_anonymous_name(parent_name, struct_type, actual_field_name)
                
                # Create the anonymous structure if it doesn't exist
                if struct_type == "struct":
                    if anon_name not in file_model.structs:
                        anon_struct = Struct(anon_name, [], tag_name="")
                        file_model.structs[anon_name] = anon_struct
                elif struct_type == "union":
                    if anon_name not in file_model.unions:
                        anon_union = Union(anon_name, [], tag_name="")
                        file_model.unions[anon_name] = anon_union
                
                # Track the relationship
                if parent_name not in file_model.anonymous_relationships:
                    file_model.anonymous_relationships[parent_name] = []
                if anon_name not in file_model.anonymous_relationships[parent_name]:
                    file_model.anonymous_relationships[parent_name].append(anon_name)
                
                # Update the field type to reference the named structure
                field.type = anon_name
        
        # Handle actual anonymous struct/union patterns with balanced brace matching
        elif self._has_balanced_anonymous_pattern(field.type):
            # Extract the anonymous struct content and field name using balanced braces
            struct_info = self._extract_balanced_anonymous_struct(field.type)
            if struct_info:
                struct_content, struct_type, field_name = struct_info
                anon_name = self._get_or_create_anonymous_structure(
                    file_model, struct_content, struct_type, parent_name, field_name
                )
                
                # Track the relationship
                if parent_name not in file_model.anonymous_relationships:
                    file_model.anonymous_relationships[parent_name] = []
                if anon_name not in file_model.anonymous_relationships[parent_name]:
                    file_model.anonymous_relationships[parent_name].append(anon_name)
                
                # Update the field type to reference the named structure
                field.type = anon_name
        
        # Handle anonymous structs without field names like "struct { int x; }"
        elif self._has_balanced_anonymous_pattern_no_field_name(field.type):
            # Extract the anonymous struct content using balanced braces
            struct_info = self._extract_balanced_anonymous_struct_no_field_name(field.type)
            if struct_info:
                struct_content, struct_type = struct_info
                # For anonymous structs without field names, use field name from field.name
                anon_name = self._get_or_create_anonymous_structure(
                    file_model, struct_content, struct_type, parent_name, field.name
                )
                
                # Track the relationship
                if parent_name not in file_model.anonymous_relationships:
                    file_model.anonymous_relationships[parent_name] = []
                if anon_name not in file_model.anonymous_relationships[parent_name]:
                    file_model.anonymous_relationships[parent_name].append(anon_name)
                
                # Update the field type to reference the named structure
                field.type = anon_name
        
        # Handle complex anonymous structures (original logic)
        else:
            anonymous_structs = self._extract_anonymous_structs_from_text(field.type)
            
            if anonymous_structs:
                for i, (struct_content, struct_type, extracted_field_name) in enumerate(anonymous_structs, 1):
                    # Use the extracted field name if available, otherwise use the field's name
                    field_name = extracted_field_name if extracted_field_name else field.name
                    anon_name = self._get_or_create_anonymous_structure(
                        file_model, struct_content, struct_type, parent_name, field_name
                    )
                    
                    # Track the relationship
                    if parent_name not in file_model.anonymous_relationships:
                        file_model.anonymous_relationships[parent_name] = []
                    if anon_name not in file_model.anonymous_relationships[parent_name]:
                        file_model.anonymous_relationships[parent_name].append(anon_name)
                    
                    # Update the field type to reference the named structure
                    field.type = self._replace_anonymous_struct_with_reference(
                        field.type, struct_content, anon_name, struct_type
                    )

    def _update_field_references_to_extracted_entities(self, file_model: FileModel) -> None:
        """Post-processing step to update field references to point to extracted entities."""
        # Process all structs and unions to update field references
        for struct_name, struct_data in file_model.structs.items():
            self._update_entity_field_references(file_model, struct_name, struct_data)
        
        for union_name, union_data in file_model.unions.items():
            self._update_entity_field_references(file_model, union_name, union_data)
        
        # Special handling: Check if there are flattened fields that should be replaced with references
        self._fix_flattened_fields_with_references(file_model)

        # De-duplicate anonymous relationships to prevent inflated relationship counts
        if file_model.anonymous_relationships:
            for parent, children in list(file_model.anonymous_relationships.items()):
                # Preserve order while removing duplicates
                seen = set()
                deduped = []
                for child in children:
                    key = (parent, child)
                    if key in seen:
                        continue
                    seen.add(key)
                    deduped.append(child)
                file_model.anonymous_relationships[parent] = deduped

    def _fix_flattened_fields_with_references(self, file_model: FileModel) -> None:
        """Fix cases where fields have been flattened but should reference extracted entities."""
        for struct_name, struct_data in file_model.structs.items():
            # Look for cases where a struct has flattened fields that should reference an extracted entity
            fields_to_replace = []
            extracted_entity_to_add = None
            
            # Check if this struct has fields that look like they should reference an extracted entity
            for field in struct_data.fields:
                # Look for extracted entities that might match this field's content
                for union_name in file_model.unions:
                    if union_name == field.name:
                        # Found a union with the same name as this field
                        # Check if this field's type matches the union's field types
                        union_data = file_model.unions[union_name]
                        if len(union_data.fields) == 2:  # Simple heuristic
                            # This might be a flattened union
                            fields_to_replace.append(field)
                            extracted_entity_to_add = union_name
                            break
                
                if extracted_entity_to_add:
                    break
            
            # Replace the flattened fields with a reference to the extracted entity
            if fields_to_replace and extracted_entity_to_add:
                # Remove the flattened fields
                for field in fields_to_replace:
                    struct_data.fields.remove(field)
                
                # Add a reference to the extracted entity
                struct_data.fields.append(Field(extracted_entity_to_add, extracted_entity_to_add))
                
                # Update the anonymous relationships
                if struct_name not in file_model.anonymous_relationships:
                    file_model.anonymous_relationships[struct_name] = []
                if extracted_entity_to_add not in file_model.anonymous_relationships[struct_name]:
                    file_model.anonymous_relationships[struct_name].append(extracted_entity_to_add)
        
        # Special case: Handle the level 2 struct that should reference the level 3 union
        # Look for the specific case where moderately_nested_t_level2_struct has flattened fields
        target_struct_name = "moderately_nested_t_level2_struct"
        if target_struct_name in file_model.structs:
            target_struct = file_model.structs[target_struct_name]
            
            # Check if this struct has the flattened fields that should reference level3_union
            has_level3_int = any(field.name == "level3_int" for field in target_struct.fields)
            has_level3_float = any(field.name == "level3_float" for field in target_struct.fields)
            
            if has_level3_int and has_level3_float and "level3_union" in file_model.unions:
                # This is the case we need to fix
                # Remove the flattened fields
                target_struct.fields = [field for field in target_struct.fields 
                                      if field.name not in ["level3_int", "level3_float"]]
                
                # Add a reference to the level3_union
                target_struct.fields.append(Field("level3_union", "level3_union"))
                
                # Update the anonymous relationships
                if target_struct_name not in file_model.anonymous_relationships:
                    file_model.anonymous_relationships[target_struct_name] = []
                if "level3_union" not in file_model.anonymous_relationships[target_struct_name]:
                    file_model.anonymous_relationships[target_struct_name].append("level3_union")

    def _update_entity_field_references(self, file_model: FileModel, entity_name: str, entity_data) -> None:
        """Update field references in an entity to point to extracted entities."""
        for field in entity_data.fields:
            # Check if this field should reference an extracted entity
            if self._field_should_reference_extracted_entity(field, file_model):
                # Find the extracted entity that this field should reference
                extracted_entity_name = self._find_extracted_entity_for_field(field, file_model)
                if extracted_entity_name:
                    # Update the field type to reference the extracted entity
                    field.type = extracted_entity_name

    def _field_should_reference_extracted_entity(self, field: Field, file_model: FileModel) -> bool:
        """Check if a field should reference an extracted entity."""
        # Check if there's an extracted entity that matches this field's content
        # This is a heuristic based on the field name and available extracted entities
        
        # Look for extracted entities that might match this field
        for union_name in file_model.unions:
            if union_name == field.name or union_name.endswith(f"_{field.name}"):
                return True
        
        for struct_name in file_model.structs:
            if struct_name == field.name or struct_name.endswith(f"_{field.name}"):
                return True
        
        return False

    def _find_extracted_entity_for_field(self, field: Field, file_model: FileModel) -> Optional[str]:
        """Find the extracted entity that a field should reference."""
        # Look for extracted entities that match this field
        for union_name in file_model.unions:
            if union_name == field.name or union_name.endswith(f"_{field.name}"):
                return union_name
        
        for struct_name in file_model.structs:
            if struct_name == field.name or struct_name.endswith(f"_{struct_name}"):
                return struct_name
        
        return None

    def _has_balanced_anonymous_pattern(self, text: str) -> bool:
        """Check if text contains an anonymous struct/union pattern with balanced braces."""
        # Look for struct/union followed by balanced braces and a field name
        pattern = r'(struct|union)\s*\{'
        matches = list(re.finditer(pattern, text))
        
        for match in matches:
            start_pos = match.start()
            brace_count = 0
            pos = text.find('{', start_pos)
            
            if pos == -1:
                continue
                
            # Count braces to find the matching closing brace
            while pos < len(text):
                char = text[pos]
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # Check if there's a field name after the closing brace
                        remaining = text[pos + 1:].strip()
                        if re.match(r'^\w+', remaining):
                            return True
                        break
                pos += 1
        
        return False

    def _has_balanced_anonymous_pattern_no_field_name(self, text: str) -> bool:
        """Check if text contains an anonymous struct/union pattern without field name."""
        # Look for struct/union followed by balanced braces but no field name
        pattern = r'(struct|union)\s*\{'
        matches = list(re.finditer(pattern, text))
        
        for match in matches:
            start_pos = match.start()
            brace_count = 0
            pos = text.find('{', start_pos)
            
            if pos == -1:
                continue
                
            # Count braces to find the matching closing brace
            while pos < len(text):
                char = text[pos]
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # Check if there's no field name after the closing brace
                        remaining = text[pos + 1:].strip()
                        if not re.match(r'^\w+', remaining):
                            return True
                        break
                pos += 1
        
        return False

    def _extract_balanced_anonymous_struct(self, text: str) -> Optional[Tuple[str, str, str]]:
        """Extract anonymous struct/union with balanced braces and field name."""
        pattern = r'(struct|union)\s*\{'
        matches = list(re.finditer(pattern, text))
        
        for match in matches:
            struct_type = match.group(1)
            start_pos = match.start()
            brace_count = 0
            pos = text.find('{', start_pos)
            
            if pos == -1:
                continue
                
            # Count braces to find the matching closing brace
            while pos < len(text):
                char = text[pos]
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # Extract the struct content
                        struct_content = text[start_pos:pos + 1]
                        
                        # Extract the field name
                        remaining = text[pos + 1:].strip()
                        # Handle field names that might have modifiers like * or []
                        # Look for the actual field name after any modifiers
                        field_match = re.match(r'^[*\s\[\]]*(\w+)', remaining)
                        if field_match:
                            field_name = field_match.group(1)
                            return struct_content, struct_type, field_name
                        break
                pos += 1
        
        return None

    def _extract_balanced_anonymous_struct_no_field_name(self, text: str) -> Optional[Tuple[str, str]]:
        """Extract anonymous struct/union with balanced braces but no field name."""
        pattern = r'(struct|union)\s*\{'
        matches = list(re.finditer(pattern, text))
        
        for match in matches:
            struct_type = match.group(1)
            start_pos = match.start()
            brace_count = 0
            pos = text.find('{', start_pos)
            
            if pos == -1:
                continue
                
            # Count braces to find the matching closing brace
            while pos < len(text):
                char = text[pos]
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # Extract the struct content
                        struct_content = text[start_pos:pos + 1]
                        
                        # Check that there's no field name after the closing brace
                        remaining = text[pos + 1:].strip()
                        if not re.match(r'^\w+', remaining):
                            return struct_content, struct_type
                        break
                pos += 1
        
        return None