#!/usr/bin/env python3
"""
C/C++ code parser
"""

import re
from pathlib import Path
from typing import List, Dict, Set, Optional
from .models import FileModel, Struct, Enum, Function, Field


class CParser:
    """Parser for C/C++ source files"""
    
    def __init__(self):
        # Compile regex patterns for better performance
        self.struct_pattern = re.compile(r'struct\s+(\w+)\s*\{([^}]+)\}')
        self.enum_pattern = re.compile(r'enum\s+(\w+)\s*\{([^}]+)\}')
        self.function_pattern = re.compile(r'(\w+)\s+(\w+)\s*\([^)]*\)\s*;?')
        self.global_pattern = re.compile(r'(\w+)\s+(\w+)\s*;')
        self.macro_pattern = re.compile(r'#define\s+(\w+)')
        self.typedef_pattern = re.compile(r'typedef\s+(\w+)\s+(\w+)\s*;')
        self.include_pattern = re.compile(r'#include\s*[<"]([^>"]+)[>"]')
    
    def parse_file(self, file_path: Path) -> FileModel:
        """Parse a C/C++ file and return a FileModel"""
        try:
            content = self._read_file(file_path)
        except Exception as e:
            raise ValueError(f"Failed to read file {file_path}: {e}")
        
        # Parse different elements
        structs = self._parse_structs(content)
        enums = self._parse_enums(content)
        functions = self._parse_functions(content)
        globals = self._parse_globals(content)
        macros = self._parse_macros(content)
        typedefs = self._parse_typedefs(content)
        includes = self._parse_includes(content)
        
        return FileModel(
            file_path=str(file_path),
            relative_path=str(file_path),
            project_root=str(file_path.parent),
            encoding_used='utf-8',
            structs=structs,
            enums=enums,
            functions=functions,
            globals=globals,
            includes=includes,
            macros=macros,
            typedefs=typedefs
        )
    
    def _read_file(self, file_path: Path) -> str:
        """Read file content with encoding detection"""
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                return file_path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
        
        raise ValueError(f"Could not decode file {file_path} with any encoding")
    
    def _parse_structs(self, content: str) -> Dict[str, Struct]:
        """Parse struct definitions"""
        structs = {}
        
        for match in self.struct_pattern.finditer(content):
            name = match.group(1)
            body = match.group(2)
            
            # Parse fields (improved)
            fields = []
            lines = body.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('//') and not line.startswith('/*'):
                    # Improved field parsing
                    field_match = re.match(r'(\w+(?:\s*\*\s*)?)\s+(\w+)(?:\s*\[[^\]]*\])?\s*;', line)
                    if field_match:
                        field_type = field_match.group(1).strip()
                        field_name = field_match.group(2)
                        fields.append(Field(field_name, field_type))
            
            structs[name] = Struct(name, fields, [])
        
        return structs
    
    def _parse_enums(self, content: str) -> Dict[str, Enum]:
        """Parse enum definitions"""
        enums = {}
        
        for match in self.enum_pattern.finditer(content):
            name = match.group(1)
            body = match.group(2)
            
            # Parse enum values (improved)
            values = []
            lines = body.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('//') and not line.startswith('/*'):
                    # Improved value parsing
                    value_match = re.match(r'(\w+)(?:\s*=\s*[^,]+)?,?', line)
                    if value_match:
                        values.append(value_match.group(1))
            
            enums[name] = Enum(name, values)
        
        return enums
    
    def _parse_functions(self, content: str) -> List[Function]:
        """Parse function declarations"""
        functions = []
        
        for match in self.function_pattern.finditer(content):
            return_type = match.group(1)
            name = match.group(2)
            
            # Skip if it looks like a variable declaration
            if return_type in ['static', 'extern', 'const', 'volatile']:
                continue
            
            functions.append(Function(name, return_type, []))
        
        return functions
    
    def _parse_globals(self, content: str) -> List[Field]:
        """Parse global variable declarations"""
        globals = []
        
        # Remove struct and enum definitions to avoid parsing their fields as globals
        # This is a simple approach - in a more sophisticated parser we'd track context
        lines = content.split('\n')
        in_struct_or_enum = False
        brace_count = 0
        
        for line in lines:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('//') or line.startswith('/*'):
                continue
            
            # Track struct/enum context
            if line.startswith('struct') or line.startswith('enum'):
                in_struct_or_enum = True
                brace_count = 0
                continue
            
            # Count braces to track when we exit struct/enum
            brace_count += line.count('{') - line.count('}')
            if brace_count <= 0 and in_struct_or_enum:
                in_struct_or_enum = False
            
            # Skip if we're inside a struct or enum
            if in_struct_or_enum:
                continue
            
            # Skip function declarations (they have parentheses)
            if '(' in line and ')' in line:
                continue
            
            # Skip typedefs
            if line.startswith('typedef'):
                continue
            
            # Try to match variable declarations (improved pattern)
            match = re.search(r'(\w+(?:\s*\*\s*)?)\s+(\w+)(?:\s*=\s*[^;]+)?\s*;', line)
            if match:
                var_type = match.group(1).strip()
                var_name = match.group(2)
                
                # Only include basic types as globals
                if var_type in ['int', 'char', 'float', 'double', 'void', 'long', 'short', 'User*']:
                    globals.append(Field(var_name, var_type))
        
        return globals
    
    def _parse_macros(self, content: str) -> List[str]:
        """Parse macro definitions"""
        macros = []
        
        for match in self.macro_pattern.finditer(content):
            macro_name = match.group(1)
            macros.append(macro_name)
        
        return macros
    
    def _parse_typedefs(self, content: str) -> Dict[str, str]:
        """Parse typedef definitions"""
        typedefs = {}
        
        # Improved typedef pattern to handle more cases
        typedef_pattern = re.compile(r'typedef\s+(\w+(?:\s+\w+)*)\s+(\w+)\s*;')
        
        for match in typedef_pattern.finditer(content):
            original_type = match.group(1).strip()
            new_type = match.group(2)
            typedefs[new_type] = original_type
        
        return typedefs
    
    def _parse_includes(self, content: str) -> Set[str]:
        """Parse include statements"""
        includes = set()
        
        for match in self.include_pattern.finditer(content):
            include_name = match.group(1)
            includes.add(include_name)
        
        return includes