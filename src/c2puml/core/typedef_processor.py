"""
Unified Typedef Processing Pipeline

This module provides a comprehensive solution for processing C/C++ typedefs,
including complex cases like anonymous structs, unions, function pointers,
and nested structures.

The TypedefProcessor uses a pipeline architecture:
1. Parse: Convert typedef text to AST
2. Extract: Identify and extract anonymous structures
3. Transform: Convert to internal model format
4. Generate: Create PlantUML representations
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any, Union, Tuple
from pathlib import Path

from ..models import Struct, Union, Field, Alias, FileModel


class TypedefType(Enum):
    """Types of typedefs that can be processed."""
    SIMPLE = "simple"  # typedef int MyInt;
    STRUCT = "struct"  # typedef struct { ... } MyStruct;
    UNION = "union"    # typedef union { ... } MyUnion;
    ENUM = "enum"      # typedef enum { ... } MyEnum;
    FUNCTION_POINTER = "function_pointer"  # typedef int (*func)(int);
    ARRAY = "array"    # typedef int MyArray[10];
    POINTER = "pointer"  # typedef int* MyPtr;
    ANONYMOUS_STRUCT = "anonymous_struct"  # struct { ... } field;
    ANONYMOUS_UNION = "anonymous_union"    # union { ... } field;


@dataclass
class TypedefAST:
    """Abstract Syntax Tree representation of a typedef."""
    typedef_type: TypedefType
    name: str
    base_type: str
    fields: List['FieldAST'] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)  # For function pointers
    array_size: Optional[str] = None
    pointer_level: int = 0
    is_const: bool = False
    is_volatile: bool = False
    source_text: str = ""
    line_number: int = 0
    file_path: str = ""


@dataclass
class FieldAST:
    """AST representation of a struct/union field."""
    name: str
    field_type: str
    is_pointer: bool = False
    pointer_level: int = 0
    is_array: bool = False
    array_size: Optional[str] = None
    is_function_pointer: bool = False
    function_parameters: List[str] = field(default_factory=list)
    is_anonymous_struct: bool = False
    is_anonymous_union: bool = False
    anonymous_content: Optional[str] = None
    source_text: str = ""


@dataclass
class AnonymousStructure:
    """Represents an extracted anonymous structure."""
    parent_name: str
    structure_type: str  # "struct" or "union"
    fields: List[FieldAST]
    generated_name: str
    source_text: str
    nesting_level: int = 0


class TypedefParser(ABC):
    """Abstract base class for typedef parsers."""
    
    @abstractmethod
    def can_parse(self, text: str) -> bool:
        """Check if this parser can handle the given typedef text."""
        pass
    
    @abstractmethod
    def parse(self, text: str, context: Dict[str, Any]) -> TypedefAST:
        """Parse the typedef text into an AST."""
        pass


class SimpleTypedefParser(TypedefParser):
    """Parser for simple typedefs like 'typedef int MyInt;'."""
    
    def can_parse(self, text: str) -> bool:
        # Simple pattern: typedef <type> <name>;
        pattern = r'typedef\s+(\w+(?:\s*\*\s*|\s+\[[^\]]*\])*)\s+(\w+)\s*;'
        return bool(re.match(pattern, text.strip()))
    
    def parse(self, text: str, context: Dict[str, Any]) -> TypedefAST:
        text = text.strip()
        match = re.match(r'typedef\s+(\w+(?:\s*\*\s*|\s+\[[^\]]*\])*)\s+(\w+)\s*;', text)
        
        if not match:
            raise ValueError(f"Cannot parse simple typedef: {text}")
        
        base_type, name = match.groups()
        
        # Determine if it's a pointer or array
        pointer_level = base_type.count('*')
        is_array = '[' in base_type
        
        # Extract array size if present
        array_size = None
        if is_array:
            array_match = re.search(r'\[([^\]]*)\]', base_type)
            if array_match:
                array_size = array_match.group(1)
        
        # Clean up base type
        clean_base_type = re.sub(r'\s*\*\s*|\s*\[[^\]]*\]', '', base_type).strip()
        
        return TypedefAST(
            typedef_type=TypedefType.SIMPLE,
            name=name,
            base_type=clean_base_type,
            pointer_level=pointer_level,
            array_size=array_size,
            source_text=text,
            line_number=context.get('line_number', 0),
            file_path=context.get('file_path', '')
        )


class StructTypedefParser(TypedefParser):
    """Parser for struct typedefs."""
    
    def can_parse(self, text: str) -> bool:
        # Pattern: typedef struct [tag] { ... } name;
        pattern = r'typedef\s+struct\s+(?:\w+\s+)?\{[^}]*\}\s+\w+\s*;'
        return bool(re.search(pattern, text.strip()))
    
    def parse(self, text: str, context: Dict[str, Any]) -> TypedefAST:
        text = text.strip()
        
        # Extract struct name
        name_match = re.search(r'typedef\s+struct\s+(?:\w+\s+)?\{[^}]*\}\s+(\w+)\s*;', text)
        if not name_match:
            raise ValueError(f"Cannot parse struct typedef: {text}")
        
        name = name_match.group(1)
        
        # Extract struct content
        content_match = re.search(r'typedef\s+struct\s+(?:\w+\s+)?\{([^}]*)\}\s+\w+\s*;', text)
        if not content_match:
            raise ValueError(f"Cannot extract struct content: {text}")
        
        content = content_match.group(1).strip()
        
        # Parse fields
        fields = self._parse_fields(content)
        
        return TypedefAST(
            typedef_type=TypedefType.STRUCT,
            name=name,
            base_type="struct",
            fields=fields,
            source_text=text,
            line_number=context.get('line_number', 0),
            file_path=context.get('file_path', '')
        )
    
    def _parse_fields(self, content: str) -> List[FieldAST]:
        """Parse struct fields from content."""
        fields = []
        
        if not content.strip():
            return fields
        
        # Split by semicolons to get individual field declarations
        field_declarations = [f.strip() for f in content.split(';') if f.strip()]
        
        for decl in field_declarations:
            field = self._parse_field_declaration(decl)
            if field:
                fields.append(field)
        
        return fields
    
    def _parse_field_declaration(self, decl: str) -> Optional[FieldAST]:
        """Parse a single field declaration."""
        if not decl.strip():
            return None
        
        # Handle anonymous struct/union fields
        anon_match = re.match(r'(struct|union)\s*\{([^}]*)\}\s+(\w+)', decl)
        if anon_match:
            struct_type, content, name = anon_match.groups()
            return FieldAST(
                name=name,
                field_type=f"{struct_type} {{ {content} }}",
                is_anonymous_struct=(struct_type == "struct"),
                is_anonymous_union=(struct_type == "union"),
                anonymous_content=content,
                source_text=decl
            )
        
        # Handle function pointer fields
        func_ptr_match = re.search(r'\(\*\s*(\w+)\s*\)\s*\(([^)]*)\)', decl)
        if func_ptr_match:
            name, params = func_ptr_match.groups()
            return FieldAST(
                name=name,
                field_type=decl.strip(),
                is_function_pointer=True,
                function_parameters=[p.strip() for p in params.split(',') if p.strip()],
                source_text=decl
            )
        
        # Handle array fields
        array_match = re.match(r'(.+?)\s+(\w+)\s*\[([^\]]*)\]', decl)
        if array_match:
            field_type, name, array_size = array_match.groups()
            return FieldAST(
                name=name,
                field_type=field_type.strip(),
                is_array=True,
                array_size=array_size.strip(),
                source_text=decl
            )
        
        # Handle pointer fields
        if '*' in decl:
            parts = decl.split('*')
            if len(parts) >= 2:
                field_type = parts[0].strip()
                name = parts[-1].strip()
                pointer_level = decl.count('*')
                return FieldAST(
                    name=name,
                    field_type=field_type,
                    is_pointer=True,
                    pointer_level=pointer_level,
                    source_text=decl
                )
        
        # Regular field
        parts = decl.strip().split()
        if len(parts) >= 2:
            field_type = ' '.join(parts[:-1])
            name = parts[-1]
            return FieldAST(
                name=name,
                field_type=field_type,
                source_text=decl
            )
        
        return None


class TypedefProcessor:
    """Main processor for handling all typedef operations."""
    
    def __init__(self):
        self.parsers: List[TypedefParser] = [
            SimpleTypedefParser(),
            StructTypedefParser(),
        ]
        self.anonymous_structures: List[AnonymousStructure] = []
        self.processed_typedefs: Dict[str, TypedefAST] = {}
    
    def process_file(self, file_model: FileModel) -> None:
        """Process all typedefs in a file."""
        # Process structs
        for struct_name, struct_data in file_model.structs.items():
            self._process_struct_typedefs(struct_name, struct_data, file_model)
        
        # Process unions
        for union_name, union_data in file_model.unions.items():
            self._process_union_typedefs(union_name, union_data, file_model)
        
        # Process aliases (typedefs)
        for alias_name, alias_data in file_model.aliases.items():
            self._process_alias_typedefs(alias_name, alias_data, file_model)
    
    def _process_struct_typedefs(self, struct_name: str, struct_data: Struct, file_model: FileModel) -> None:
        """Process typedefs within a struct."""
        # Extract anonymous structures from struct fields
        for field in struct_data.fields:
            if self._is_anonymous_structure_field(field):
                self._extract_anonymous_structure(field, struct_name, "struct", file_model)
    
    def _process_union_typedefs(self, union_name: str, union_data: Union, file_model: FileModel) -> None:
        """Process typedefs within a union."""
        # Extract anonymous structures from union fields
        for field in union_data.fields:
            if self._is_anonymous_structure_field(field):
                self._extract_anonymous_structure(field, union_name, "union", file_model)
    
    def _process_alias_typedefs(self, alias_name: str, alias_data: Alias, file_model: FileModel) -> None:
        """Process alias typedefs."""
        # Parse the typedef using appropriate parser
        typedef_text = alias_data.type
        context = {
            'line_number': 0,  # TODO: Get actual line number
            'file_path': file_model.file_path
        }
        
        for parser in self.parsers:
            if parser.can_parse(typedef_text):
                try:
                    ast = parser.parse(typedef_text, context)
                    self.processed_typedefs[alias_name] = ast
                    
                    # Extract anonymous structures from the typedef
                    self._extract_anonymous_from_typedef(ast, alias_name, file_model)
                    break
                except ValueError as e:
                    print(f"Warning: Failed to parse typedef {alias_name}: {e}")
                    continue
    
    def _is_anonymous_structure_field(self, field: Field) -> bool:
        """Check if a field contains an anonymous structure."""
        field_type = field.type.lower()
        return (
            'struct {' in field_type or 
            'union {' in field_type or
            field_type.startswith('struct {') or
            field_type.startswith('union {')
        )
    
    def _extract_anonymous_structure(self, field: Field, parent_name: str, parent_type: str, file_model: FileModel) -> None:
        """Extract anonymous structure from a field."""
        # Parse the anonymous structure content
        content = self._extract_anonymous_content(field.type)
        if not content:
            return
        
        # Generate a unique name for the anonymous structure
        generated_name = f"{parent_name}_anonymous_{parent_type}_{len(self.anonymous_structures) + 1}"
        
        # Parse the fields
        fields = self._parse_anonymous_fields(content)
        
        # Create anonymous structure
        anon_struct = AnonymousStructure(
            parent_name=parent_name,
            structure_type=parent_type,
            fields=fields,
            generated_name=generated_name,
            source_text=field.type
        )
        
        self.anonymous_structures.append(anon_struct)
        
        # Add to file model
        if parent_type == "struct":
            file_model.structs[generated_name] = Struct(
                name=generated_name,
                fields=[self._convert_field_ast_to_field(f) for f in fields]
            )
        else:  # union
            file_model.unions[generated_name] = Union(
                name=generated_name,
                fields=[self._convert_field_ast_to_field(f) for f in fields]
            )
    
    def _extract_anonymous_content(self, field_type: str) -> Optional[str]:
        """Extract content from anonymous structure field type."""
        # Handle struct { ... } pattern
        struct_match = re.search(r'struct\s*\{([^}]*)\}', field_type)
        if struct_match:
            return struct_match.group(1).strip()
        
        # Handle union { ... } pattern
        union_match = re.search(r'union\s*\{([^}]*)\}', field_type)
        if union_match:
            return union_match.group(1).strip()
        
        return None
    
    def _parse_anonymous_fields(self, content: str) -> List[FieldAST]:
        """Parse fields from anonymous structure content."""
        fields = []
        
        if not content.strip():
            return fields
        
        # Split by semicolons to get individual field declarations
        field_declarations = [f.strip() for f in content.split(';') if f.strip()]
        
        for decl in field_declarations:
            field = self._parse_field_declaration(decl)
            if field:
                fields.append(field)
        
        return fields
    
    def _parse_field_declaration(self, decl: str) -> Optional[FieldAST]:
        """Parse a single field declaration."""
        if not decl.strip():
            return None
        
        # Handle function pointer fields
        func_ptr_match = re.search(r'\(\*\s*(\w+)\s*\)\s*\(([^)]*)\)', decl)
        if func_ptr_match:
            name, params = func_ptr_match.groups()
            return FieldAST(
                name=name,
                field_type=decl.strip(),
                is_function_pointer=True,
                function_parameters=[p.strip() for p in params.split(',') if p.strip()],
                source_text=decl
            )
        
        # Handle array fields
        array_match = re.match(r'(.+?)\s+(\w+)\s*\[([^\]]*)\]', decl)
        if array_match:
            field_type, name, array_size = array_match.groups()
            return FieldAST(
                name=name,
                field_type=field_type.strip(),
                is_array=True,
                array_size=array_size.strip(),
                source_text=decl
            )
        
        # Handle pointer fields
        if '*' in decl:
            parts = decl.split('*')
            if len(parts) >= 2:
                field_type = parts[0].strip()
                name = parts[-1].strip()
                pointer_level = decl.count('*')
                return FieldAST(
                    name=name,
                    field_type=field_type,
                    is_pointer=True,
                    pointer_level=pointer_level,
                    source_text=decl
                )
        
        # Regular field
        parts = decl.strip().split()
        if len(parts) >= 2:
            field_type = ' '.join(parts[:-1])
            name = parts[-1]
            return FieldAST(
                name=name,
                field_type=field_type,
                source_text=decl
            )
        
        return None
    
    def _convert_field_ast_to_field(self, field_ast: FieldAST) -> Field:
        """Convert FieldAST to Field model."""
        field_type = field_ast.field_type
        
        # Add pointer indicators
        if field_ast.is_pointer:
            field_type += '*' * field_ast.pointer_level
        
        # Add array indicators
        if field_ast.is_array and field_ast.array_size:
            field_type += f"[{field_ast.array_size}]"
        
        return Field(
            name=field_ast.name,
            type=field_type,
            value=None
        )
    
    def _extract_anonymous_from_typedef(self, ast: TypedefAST, typedef_name: str, file_model: FileModel) -> None:
        """Extract anonymous structures from a typedef AST."""
        for field in ast.fields:
            if field.is_anonymous_struct or field.is_anonymous_union:
                self._extract_anonymous_structure_from_field(field, typedef_name, file_model)
    
    def _extract_anonymous_structure_from_field(self, field: FieldAST, parent_name: str, file_model: FileModel) -> None:
        """Extract anonymous structure from a field AST."""
        if not field.anonymous_content:
            return
        
        # Generate a unique name
        structure_type = "struct" if field.is_anonymous_struct else "union"
        generated_name = f"{parent_name}_anonymous_{structure_type}_{len(self.anonymous_structures) + 1}"
        
        # Parse the fields
        fields = self._parse_anonymous_fields(field.anonymous_content)
        
        # Create anonymous structure
        anon_struct = AnonymousStructure(
            parent_name=parent_name,
            structure_type=structure_type,
            fields=fields,
            generated_name=generated_name,
            source_text=field.source_text
        )
        
        self.anonymous_structures.append(anon_struct)
        
        # Add to file model
        if structure_type == "struct":
            file_model.structs[generated_name] = Struct(
                name=generated_name,
                fields=[self._convert_field_ast_to_field(f) for f in fields]
            )
        else:  # union
            file_model.unions[generated_name] = Union(
                name=generated_name,
                fields=[self._convert_field_ast_to_field(f) for f in fields]
            )