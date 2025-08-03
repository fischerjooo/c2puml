"""
Struct Parser Module

Handles struct and union parsing with field extraction:
- typedef struct { ... } MyStruct;
- typedef union { ... } MyUnion;
- struct field parsing
- union field parsing
"""

import re
from typing import List, Optional, Dict, Any, Tuple

from .base import BaseParser, ParserLevel, ParseContext, ParseResult, TypedefInfo
from .simple_parser import SimpleFieldParser


class StructTypedefParser(BaseParser):
    """Parser for struct typedefs."""
    
    def __init__(self):
        super().__init__()
        self.level = ParserLevel.STRUCT
        self.name = "StructTypedefParser"
        self.field_parser = SimpleFieldParser()
    
    def can_parse(self, text: str, context: ParseContext) -> bool:
        """Check if this parser can handle the given typedef text."""
        text = self.preprocess_text(text)
        
        # Pattern: typedef struct [tag] { ... } name;
        struct_pattern = r'typedef\s+struct\s+(?:\w+\s+)?\{[^}]*\}\s+\w+\s*;'
        
        if not re.search(struct_pattern, text):
            return False
        
        # Check that it's not too complex
        info = self.extract_basic_info(text)
        
        # Reject if it has function pointers or is too nested
        if (info['has_function_pointer'] or info['brace_count'] > 2 or 
            info['parenthesis_count'] > 2):
            return False
        
        return True
    
    def parse(self, text: str, context: ParseContext) -> ParseResult:
        """Parse the struct typedef text into a TypedefInfo."""
        try:
            text = self.preprocess_text(text)
            
            # Extract struct information
            typedef_info = self._parse_struct_typedef(text, context)
            
            return ParseResult(
                success=True,
                parsed_data=typedef_info,
                parser_level=self.level,
                confidence=1.0
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                error_message=f"Failed to parse struct typedef: {str(e)}",
                parser_level=self.level
            )
    
    def _parse_struct_typedef(self, text: str, context: ParseContext) -> TypedefInfo:
        """Parse a struct typedef into TypedefInfo."""
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
        fields = self._parse_struct_fields(content, context)
        
        return TypedefInfo(
            name=name,
            base_type="struct",
            typedef_type="struct",
            fields=fields,
            source_text=text,
            line_number=context.line_number,
            file_path=context.file_path
        )
    
    def _parse_struct_fields(self, content: str, context: ParseContext) -> List:
        """Parse struct fields from content."""
        from ...models import Field
        
        fields = []
        
        if not content.strip():
            return fields
        
        # Split by semicolons to get individual field declarations
        field_declarations = [f.strip() for f in content.split(';') if f.strip()]
        
        for decl in field_declarations:
            field = self._parse_field_declaration(decl, context)
            if field:
                fields.append(field)
        
        return fields
    
    def _parse_field_declaration(self, decl: str, context: ParseContext):
        """Parse a single field declaration."""
        from ...models import Field
        
        if not decl.strip():
            return None
        
        # Try to parse as simple field first
        field_context = ParseContext(
            file_path=context.file_path,
            line_number=context.line_number,
            parent_structure=context.parent_structure,
            nesting_level=context.nesting_level + 1
        )
        
        result = self.field_parser.parse(decl, field_context)
        if result.success:
            return result.parsed_data
        
        # Handle anonymous struct/union fields
        anon_match = re.match(r'(struct|union)\s*\{([^}]*)\}\s+(\w+)', decl)
        if anon_match:
            struct_type, content, name = anon_match.groups()
            field_type = f"{struct_type} {{ {content} }}"
            return Field(name=name, type=field_type, value=None)
        
        # Handle function pointer fields
        func_ptr_match = re.search(r'\(\*\s*(\w+)\s*\)\s*\(([^)]*)\)', decl)
        if func_ptr_match:
            name, params = func_ptr_match.groups()
            return Field(name=name, type=decl.strip(), value=None)
        
        # Handle array fields
        array_match = re.match(r'(.+?)\s+(\w+)\s*\[([^\]]*)\]', decl)
        if array_match:
            field_type, name, array_size = array_match.groups()
            field_type = field_type.strip()
            name = name.strip()
            array_size = array_size.strip()
            
            full_type = f"{field_type}[{array_size}]"
            return Field(name=name, type=full_type, value=None)
        
        # Handle pointer fields
        if '*' in decl:
            parts = decl.split('*')
            if len(parts) >= 2:
                field_type = parts[0].strip()
                name = parts[-1].strip()
                pointer_level = decl.count('*')
                
                full_type = f"{field_type}{'*' * pointer_level}"
                return Field(name=name, type=full_type, value=None)
        
        # Regular field
        parts = decl.strip().split()
        if len(parts) >= 2:
            field_type = ' '.join(parts[:-1])
            name = parts[-1]
            
            return Field(name=name, type=field_type, value=None)
        
        return None


class UnionTypedefParser(BaseParser):
    """Parser for union typedefs."""
    
    def __init__(self):
        super().__init__()
        self.level = ParserLevel.STRUCT
        self.name = "UnionTypedefParser"
        self.field_parser = SimpleFieldParser()
    
    def can_parse(self, text: str, context: ParseContext) -> bool:
        """Check if this parser can handle the given typedef text."""
        text = self.preprocess_text(text)
        
        # Pattern: typedef union [tag] { ... } name;
        union_pattern = r'typedef\s+union\s+(?:\w+\s+)?\{[^}]*\}\s+\w+\s*;'
        
        if not re.search(union_pattern, text):
            return False
        
        # Check that it's not too complex
        info = self.extract_basic_info(text)
        
        # Reject if it has function pointers or is too nested
        if (info['has_function_pointer'] or info['brace_count'] > 2 or 
            info['parenthesis_count'] > 2):
            return False
        
        return True
    
    def parse(self, text: str, context: ParseContext) -> ParseResult:
        """Parse the union typedef text into a TypedefInfo."""
        try:
            text = self.preprocess_text(text)
            
            # Extract union information
            typedef_info = self._parse_union_typedef(text, context)
            
            return ParseResult(
                success=True,
                parsed_data=typedef_info,
                parser_level=self.level,
                confidence=1.0
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                error_message=f"Failed to parse union typedef: {str(e)}",
                parser_level=self.level
            )
    
    def _parse_union_typedef(self, text: str, context: ParseContext) -> TypedefInfo:
        """Parse a union typedef into TypedefInfo."""
        # Extract union name
        name_match = re.search(r'typedef\s+union\s+(?:\w+\s+)?\{[^}]*\}\s+(\w+)\s*;', text)
        if not name_match:
            raise ValueError(f"Cannot parse union typedef: {text}")
        
        name = name_match.group(1)
        
        # Extract union content
        content_match = re.search(r'typedef\s+union\s+(?:\w+\s+)?\{([^}]*)\}\s+\w+\s*;', text)
        if not content_match:
            raise ValueError(f"Cannot extract union content: {text}")
        
        content = content_match.group(1).strip()
        
        # Parse fields
        fields = self._parse_union_fields(content, context)
        
        return TypedefInfo(
            name=name,
            base_type="union",
            typedef_type="union",
            fields=fields,
            source_text=text,
            line_number=context.line_number,
            file_path=context.file_path
        )
    
    def _parse_union_fields(self, content: str, context: ParseContext) -> List:
        """Parse union fields from content."""
        from ...models import Field
        
        fields = []
        
        if not content.strip():
            return fields
        
        # Split by semicolons to get individual field declarations
        field_declarations = [f.strip() for f in content.split(';') if f.strip()]
        
        for decl in field_declarations:
            field = self._parse_field_declaration(decl, context)
            if field:
                fields.append(field)
        
        return fields
    
    def _parse_field_declaration(self, decl: str, context: ParseContext):
        """Parse a single field declaration."""
        from ...models import Field
        
        if not decl.strip():
            return None
        
        # Try to parse as simple field first
        field_context = ParseContext(
            file_path=context.file_path,
            line_number=context.line_number,
            parent_structure=context.parent_structure,
            nesting_level=context.nesting_level + 1
        )
        
        result = self.field_parser.parse(decl, field_context)
        if result.success:
            return result.parsed_data
        
        # Handle anonymous struct/union fields
        anon_match = re.match(r'(struct|union)\s*\{([^}]*)\}\s+(\w+)', decl)
        if anon_match:
            struct_type, content, name = anon_match.groups()
            field_type = f"{struct_type} {{ {content} }}"
            return Field(name=name, type=field_type, value=None)
        
        # Handle function pointer fields
        func_ptr_match = re.search(r'\(\*\s*(\w+)\s*\)\s*\(([^)]*)\)', decl)
        if func_ptr_match:
            name, params = func_ptr_match.groups()
            return Field(name=name, type=decl.strip(), value=None)
        
        # Handle array fields
        array_match = re.match(r'(.+?)\s+(\w+)\s*\[([^\]]*)\]', decl)
        if array_match:
            field_type, name, array_size = array_match.groups()
            field_type = field_type.strip()
            name = name.strip()
            array_size = array_size.strip()
            
            full_type = f"{field_type}[{array_size}]"
            return Field(name=name, type=full_type, value=None)
        
        # Handle pointer fields
        if '*' in decl:
            parts = decl.split('*')
            if len(parts) >= 2:
                field_type = parts[0].strip()
                name = parts[-1].strip()
                pointer_level = decl.count('*')
                
                full_type = f"{field_type}{'*' * pointer_level}"
                return Field(name=name, type=full_type, value=None)
        
        # Regular field
        parts = decl.strip().split()
        if len(parts) >= 2:
            field_type = ' '.join(parts[:-1])
            name = parts[-1]
            
            return Field(name=name, type=field_type, value=None)
        
        return None


class EnumTypedefParser(BaseParser):
    """Parser for enum typedefs."""
    
    def __init__(self):
        super().__init__()
        self.level = ParserLevel.STRUCT
        self.name = "EnumTypedefParser"
    
    def can_parse(self, text: str, context: ParseContext) -> bool:
        """Check if this parser can handle the given typedef text."""
        text = self.preprocess_text(text)
        
        # Pattern: typedef enum [tag] { ... } name;
        enum_pattern = r'typedef\s+enum\s+(?:\w+\s+)?\{[^}]*\}\s+\w+\s*;'
        
        return bool(re.search(enum_pattern, text))
    
    def parse(self, text: str, context: ParseContext) -> ParseResult:
        """Parse the enum typedef text into a TypedefInfo."""
        try:
            text = self.preprocess_text(text)
            
            # Extract enum information
            typedef_info = self._parse_enum_typedef(text, context)
            
            return ParseResult(
                success=True,
                parsed_data=typedef_info,
                parser_level=self.level,
                confidence=1.0
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                error_message=f"Failed to parse enum typedef: {str(e)}",
                parser_level=self.level
            )
    
    def _parse_enum_typedef(self, text: str, context: ParseContext) -> TypedefInfo:
        """Parse an enum typedef into TypedefInfo."""
        # Extract enum name
        name_match = re.search(r'typedef\s+enum\s+(?:\w+\s+)?\{[^}]*\}\s+(\w+)\s*;', text)
        if not name_match:
            raise ValueError(f"Cannot parse enum typedef: {text}")
        
        name = name_match.group(1)
        
        # Extract enum content
        content_match = re.search(r'typedef\s+enum\s+(?:\w+\s+)?\{([^}]*)\}\s+\w+\s*;', text)
        if not content_match:
            raise ValueError(f"Cannot extract enum content: {text}")
        
        content = content_match.group(1).strip()
        
        # Parse enum values
        values = self._parse_enum_values(content)
        
        return TypedefInfo(
            name=name,
            base_type="enum",
            typedef_type="enum",
            parameters=values,  # Use parameters field for enum values
            source_text=text,
            line_number=context.line_number,
            file_path=context.file_path
        )
    
    def _parse_enum_values(self, content: str) -> List[str]:
        """Parse enum values from content."""
        values = []
        
        if not content.strip():
            return values
        
        # Split by commas to get individual enum values
        value_declarations = [v.strip() for v in content.split(',') if v.strip()]
        
        for decl in value_declarations:
            # Handle enum values with assignments: NAME = VALUE
            if '=' in decl:
                name = decl.split('=')[0].strip()
            else:
                name = decl.strip()
            
            if name:
                values.append(name)
        
        return values