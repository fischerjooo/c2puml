"""
Basic Parser Module

Handles basic typedefs and types with minimal complexity:
- typedef int MyInt;
- typedef char* MyString;
- typedef int MyArray[10];
- typedef const int MyConst;
"""

import re
from typing import List, Optional, Dict, Any

from .base import BaseParser, ParserLevel, ParseContext, ParseResult, TypedefInfo


class BasicTypedefParser(BaseParser):
    """Parser for basic typedefs like 'typedef int MyInt;'."""
    
    def __init__(self):
        super().__init__()
        self.level = ParserLevel.SIMPLE
        self.name = "BasicTypedefParser"
    
    def can_parse(self, text: str, context: ParseContext) -> bool:
        """Check if this parser can handle the given typedef text."""
        text = self.preprocess_text(text)
        
        # Basic pattern: typedef <type> <name>;
        basic_pattern = r'typedef\s+(\w+(?:\s*\*\s*|\s+\[[^\]]*\])*)\s+(\w+)\s*;'
        
        # Check if it matches basic pattern
        if not re.match(basic_pattern, text):
            return False
        
        # Check that it's not a complex structure
        info = self.extract_basic_info(text)
        
        # Reject if it has complex features
        if (info['has_struct'] or info['has_union'] or info['has_enum'] or 
            info['has_function_pointer'] or info['brace_count'] != 0):
            return False
        
        return True
    
    def parse(self, text: str, context: ParseContext) -> ParseResult:
        """Parse the typedef text into a TypedefInfo."""
        try:
            text = self.preprocess_text(text)
            
            # Extract basic information
            typedef_info = self._parse_basic_typedef(text, context)
            
            return ParseResult(
                success=True,
                parsed_data=typedef_info,
                parser_level=self.level,
                confidence=1.0
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                error_message=f"Failed to parse basic typedef: {str(e)}",
                parser_level=self.level
            )
    
    def _parse_basic_typedef(self, text: str, context: ParseContext) -> TypedefInfo:
        """Parse a basic typedef into TypedefInfo."""
        # Match: typedef <type> <name>;
        match = re.match(r'typedef\s+(\w+(?:\s*\*\s*|\s+\[[^\]]*\])*)\s+(\w+)\s*;', text)
        
        if not match:
            raise ValueError(f"Cannot parse basic typedef: {text}")
        
        base_type, name = match.groups()
        
        # Determine typedef type and extract additional info
        typedef_type = "basic"
        pointer_level = 0
        array_size = None
        is_const = False
        is_volatile = False
        
        # Check for const/volatile
        if 'const' in base_type:
            is_const = True
            base_type = base_type.replace('const', '').strip()
        
        if 'volatile' in base_type:
            is_volatile = True
            base_type = base_type.replace('volatile', '').strip()
        
        # Check for pointers
        if '*' in base_type:
            pointer_level = base_type.count('*')
            typedef_type = "pointer"
            # Clean up base type
            base_type = re.sub(r'\s*\*\s*', '', base_type).strip()
        
        # Check for arrays
        if '[' in base_type and ']' in base_type:
            typedef_type = "array"
            array_match = re.search(r'\[([^\]]*)\]', base_type)
            if array_match:
                array_size = array_match.group(1).strip()
            # Clean up base type
            base_type = re.sub(r'\s*\[[^\]]*\]', '', base_type).strip()
        
        return TypedefInfo(
            name=name,
            base_type=base_type,
            typedef_type=typedef_type,
            pointer_level=pointer_level,
            array_size=array_size,
            is_const=is_const,
            is_volatile=is_volatile,
            source_text=text,
            line_number=context.line_number,
            file_path=context.file_path
        )


class BasicFieldParser(BaseParser):
    """Parser for basic field declarations within structs/unions."""
    
    def __init__(self):
        super().__init__()
        self.level = ParserLevel.SIMPLE
        self.name = "BasicFieldParser"
    
    def can_parse(self, text: str, context: ParseContext) -> bool:
        """Check if this parser can handle the given field text."""
        text = self.preprocess_text(text)
        
        # Basic field pattern: <type> <name>;
        basic_pattern = r'^\s*\w+(?:\s*\*\s*|\s+\[[^\]]*\])*\s+\w+\s*;?\s*$'
        
        if not re.match(basic_pattern, text):
            return False
        
        # Check that it's not complex
        info = self.extract_basic_info(text)
        
        # Reject if it has complex features
        if (info['has_struct'] or info['has_union'] or info['has_enum'] or 
            info['has_function_pointer'] or info['brace_count'] != 0):
            return False
        
        return True
    
    def parse(self, text: str, context: ParseContext) -> ParseResult:
        """Parse the field text into a Field object."""
        try:
            text = self.preprocess_text(text)
            
            # Parse the field
            field = self._parse_basic_field(text)
            
            return ParseResult(
                success=True,
                parsed_data=field,
                parser_level=self.level,
                confidence=1.0
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                error_message=f"Failed to parse basic field: {str(e)}",
                parser_level=self.level
            )
    
    def _parse_basic_field(self, text: str):
        """Parse a basic field declaration."""
        from ...models import Field
        
        # Remove trailing semicolon if present
        text = text.rstrip(';').strip()
        
        # Handle array fields: type name[size]
        array_match = re.match(r'(.+?)\s+(\w+)\s*\[([^\]]*)\]', text)
        if array_match:
            field_type, name, array_size = array_match.groups()
            field_type = field_type.strip()
            name = name.strip()
            array_size = array_size.strip()
            
            # Create field with array type
            full_type = f"{field_type}[{array_size}]"
            return Field(name=name, type=full_type, value=None)
        
        # Handle pointer fields: type *name or type* name
        if '*' in text:
            # Split by * and find the field name
            parts = text.split('*')
            if len(parts) >= 2:
                field_type = parts[0].strip()
                name = parts[-1].strip()
                pointer_level = text.count('*')
                
                # Create field with pointer type
                full_type = f"{field_type}{'*' * pointer_level}"
                return Field(name=name, type=full_type, value=None)
        
        # Regular field: type name
        parts = text.strip().split()
        if len(parts) >= 2:
            field_type = ' '.join(parts[:-1])
            name = parts[-1]
            
            return Field(name=name, type=field_type, value=None)
        
        raise ValueError(f"Cannot parse field: {text}")


class BasicTypeParser(BaseParser):
    """Parser for basic type declarations."""
    
    def __init__(self):
        super().__init__()
        self.level = ParserLevel.SIMPLE
        self.name = "BasicTypeParser"
    
    def can_parse(self, text: str, context: ParseContext) -> bool:
        """Check if this parser can handle the given type text."""
        text = self.preprocess_text(text)
        
        # Basic type pattern: just a type name
        basic_pattern = r'^\s*\w+(?:\s*\*\s*|\s+\[[^\]]*\])*\s*$'
        
        if not re.match(basic_pattern, text):
            return False
        
        # Check that it's not complex
        info = self.extract_basic_info(text)
        
        # Reject if it has complex features
        if (info['has_struct'] or info['has_union'] or info['has_enum'] or 
            info['has_function_pointer'] or info['brace_count'] != 0):
            return False
        
        return True
    
    def parse(self, text: str, context: ParseContext) -> ParseResult:
        """Parse the type text into type information."""
        try:
            text = self.preprocess_text(text)
            
            # Parse the type
            type_info = self._parse_basic_type(text)
            
            return ParseResult(
                success=True,
                parsed_data=type_info,
                parser_level=self.level,
                confidence=1.0
            )
            
        except Exception as e:
            return ParseResult(
                success=False,
                error_message=f"Failed to parse basic type: {str(e)}",
                parser_level=self.level
            )
    
    def _parse_basic_type(self, text: str) -> Dict[str, Any]:
        """Parse a basic type declaration."""
        text = text.strip()
        
        # Extract basic type information
        base_type = text
        pointer_level = 0
        array_size = None
        is_const = False
        is_volatile = False
        
        # Check for const/volatile
        if 'const' in text:
            is_const = True
            base_type = base_type.replace('const', '').strip()
        
        if 'volatile' in text:
            is_volatile = True
            base_type = base_type.replace('volatile', '').strip()
        
        # Check for pointers
        if '*' in base_type:
            pointer_level = base_type.count('*')
            base_type = re.sub(r'\s*\*\s*', '', base_type).strip()
        
        # Check for arrays
        if '[' in base_type and ']' in base_type:
            array_match = re.search(r'\[([^\]]*)\]', base_type)
            if array_match:
                array_size = array_match.group(1).strip()
            base_type = re.sub(r'\s*\[[^\]]*\]', '', base_type).strip()
        
        return {
            'base_type': base_type,
            'pointer_level': pointer_level,
            'array_size': array_size,
            'is_const': is_const,
            'is_volatile': is_volatile,
            'full_type': text
        }