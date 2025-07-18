#!/usr/bin/env python3
"""
C/C++ code parser
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from .models import FileModel, Struct, Enum, Function, Field, TypedefRelation


class CParser:
    """Parser for C/C++ source files"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Compile regex patterns for better performance
        self.struct_pattern = re.compile(r'struct\s+(\w+)\s*\{([^}]+)\}')
        self.typedef_struct_pattern = re.compile(r'typedef\s+struct\s*\{([^}]+)\}\s*(\w+)\s*;')
        self.enum_pattern = re.compile(r'enum\s+(\w+)\s*\{([^}]+)\}')
        self.function_pattern = re.compile(r'(\w+(?:\s+\w+)*)\s+(\w+)\s*\([^)]*\)\s*;?')
        self.global_pattern = re.compile(r'(\w+(?:\s+\w+)*)\s+(\w+)\s*;')
        self.macro_pattern = re.compile(r'#define\s+(\w+)')
        self.typedef_pattern = re.compile(r'typedef\s+(\w+(?:\s+\w+)*)\s+(\w+)\s*;')
        self.include_pattern = re.compile(r'#include\s*[<"]([^>"]+)[>"]')
        
        # Improved patterns for better parsing
        self.field_pattern = re.compile(r'(\w+(?:\s*\*\s*)?)\s+(\w+)(?:\s*\[[^\]]*\])?\s*;')
        self.enum_value_pattern = re.compile(r'(\w+)(?:\s*=\s*[^,]+)?,?')
        self.variable_pattern = re.compile(r'(\w+(?:\s*\*\s*)?)\s+(\w+)(?:\s*=\s*[^;]+)?\s*;')
    
    def parse_file(self, file_path: Path) -> FileModel:
        """Parse a C/C++ file and return a FileModel"""
        try:
            content = self._read_file(file_path)
        except Exception as e:
            raise ValueError(f"Failed to read file {file_path}: {e}")
        
        self.logger.debug(f"Parsing file: {file_path}")
        
        # Parse different elements
        structs = self._parse_structs(content)
        enums = self._parse_enums(content)
        functions = self._parse_functions(content)
        globals = self._parse_globals(content)
        macros = self._parse_macros(content)
        typedefs = self._parse_typedefs(content)
        includes = self._parse_includes(content)
        typedef_relations = self._parse_typedef_relations(content)
        
        self.logger.debug(f"Parsed {len(structs)} structs, {len(enums)} enums, "
                         f"{len(functions)} functions, {len(globals)} globals")
        
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
            typedefs=typedefs,
            typedef_relations=typedef_relations
        )
    
    def _read_file(self, file_path: Path) -> str:
        """Read file content with encoding detection"""
        encodings = ['utf-8', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                content = file_path.read_text(encoding=encoding)
                self.logger.debug(f"Successfully read {file_path} with {encoding} encoding")
                return content
            except UnicodeDecodeError:
                continue
        
        raise ValueError(f"Could not decode file {file_path} with any encoding")
    
    def _parse_structs(self, content: str) -> Dict[str, Struct]:
        """Parse struct definitions"""
        structs = {}
        
        # Parse regular struct declarations
        for match in self.struct_pattern.finditer(content):
            name = match.group(1)
            body = match.group(2)
            
            # Parse fields
            fields = self._parse_struct_fields(body)
            structs[name] = Struct(name, fields, [])
            
            self.logger.debug(f"Parsed struct: {name} with {len(fields)} fields")
        
        # Parse typedef struct declarations
        for match in self.typedef_struct_pattern.finditer(content):
            body = match.group(1)
            name = match.group(2)
            
            # Parse fields
            fields = self._parse_struct_fields(body)
            structs[name] = Struct(name, fields, [])
            
            self.logger.debug(f"Parsed typedef struct: {name} with {len(fields)} fields")
        
        return structs
    
    def _parse_struct_fields(self, body: str) -> List[Field]:
        """Parse fields from a struct body"""
        fields = []
        lines = body.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//') and not line.startswith('/*'):
                field_match = self.field_pattern.match(line)
                if field_match:
                    field_type = field_match.group(1).strip()
                    field_name = field_match.group(2)
                    fields.append(Field(field_name, field_type))
        
        return fields
    
    def _parse_enums(self, content: str) -> Dict[str, Enum]:
        """Parse enum definitions"""
        enums = {}
        
        for match in self.enum_pattern.finditer(content):
            name = match.group(1)
            body = match.group(2)
            
            # Parse enum values
            values = self._parse_enum_values(body)
            enums[name] = Enum(name, values)
            
            self.logger.debug(f"Parsed enum: {name} with {len(values)} values")
        
        return enums
    
    def _parse_enum_values(self, body: str) -> List[str]:
        """Parse values from an enum body"""
        values = []
        lines = body.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//') and not line.startswith('/*'):
                value_match = self.enum_value_pattern.match(line)
                if value_match:
                    values.append(value_match.group(1))
        
        return values
    
    def _parse_functions(self, content: str) -> List[Function]:
        """Parse function declarations"""
        functions = []
        
        for match in self.function_pattern.finditer(content):
            return_type = match.group(1).strip()
            name = match.group(2)
            
            # Skip if it looks like a variable declaration or modifier
            if return_type in ['static', 'extern', 'const', 'volatile', 'inline']:
                continue
            
            # Skip if it's a macro or typedef
            if return_type.startswith('#') or return_type == 'typedef':
                continue
            
            functions.append(Function(name, return_type, []))
        
        self.logger.debug(f"Parsed {len(functions)} functions")
        return functions
    
    def _parse_globals(self, content: str) -> List[Field]:
        """Parse global variable declarations"""
        globals = []
        
        # Track context to avoid parsing struct/enum fields as globals
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
            
            # Skip typedefs and other declarations
            if line.startswith('typedef') or line.startswith('#define'):
                continue
            
            # Try to match variable declarations
            match = self.variable_pattern.search(line)
            if match:
                var_type = match.group(1).strip()
                var_name = match.group(2)
                
                # Only include basic types as globals
                if self._is_basic_type(var_type):
                    globals.append(Field(var_name, var_type))
        
        self.logger.debug(f"Parsed {len(globals)} global variables")
        return globals
    
    def _is_basic_type(self, type_name: str) -> bool:
        """Check if a type is a basic C type"""
        basic_types = {
            'int', 'char', 'float', 'double', 'void', 'long', 'short',
            'unsigned', 'signed', 'const', 'volatile'
        }
        
        # Handle pointer types
        if '*' in type_name:
            base_type = type_name.replace('*', '').strip()
            return base_type in basic_types
        
        return type_name in basic_types
    
    def _parse_macros(self, content: str) -> List[str]:
        """Parse macro definitions"""
        macros = []
        
        for match in self.macro_pattern.finditer(content):
            macro_name = match.group(1)
            macros.append(macro_name)
        
        self.logger.debug(f"Parsed {len(macros)} macros")
        return macros
    
    def _parse_typedefs(self, content: str) -> Dict[str, str]:
        """Parse typedef definitions"""
        typedefs = {}
        
        # Improved typedef patterns to handle various cases
        typedef_patterns = [
            # Basic typedef: typedef type name;
            re.compile(r'typedef\s+(\w+(?:\s+\w+)*)\s+(\w+)\s*;'),
            # Pointer typedef: typedef type* name;
            re.compile(r'typedef\s+(\w+(?:\s+\w+)*\s*\*)\s+(\w+)\s*;'),
            # Function pointer: typedef return_type (*name)(params);
            re.compile(r'typedef\s+(\w+(?:\s+\w+)*)\s*\(\s*\*\s*(\w+)\s*\)\s*\([^)]*\)\s*;'),
            # Struct typedef: typedef struct { ... } name;
            re.compile(r'typedef\s+struct\s*\{[^}]*\}\s+(\w+)\s*;'),
            # Named struct typedef: typedef struct name { ... } alias;
            re.compile(r'typedef\s+struct\s+(\w+)\s*\{[^}]*\}\s+(\w+)\s*;')
        ]
        
        for pattern in typedef_patterns:
            for match in pattern.finditer(content):
                if len(match.groups()) == 2:
                    original_type = match.group(1).strip()
                    new_type = match.group(2)
                    typedefs[new_type] = original_type
                elif len(match.groups()) == 1:
                    # For struct typedefs with only one group
                    new_type = match.group(1)
                    typedefs[new_type] = f"struct {new_type}"
        
        self.logger.debug(f"Parsed {len(typedefs)} typedefs")
        return typedefs
    
    def _parse_includes(self, content: str) -> Set[str]:
        """Parse include statements"""
        includes = set()
        
        for match in self.include_pattern.finditer(content):
            include_name = match.group(1)
            includes.add(include_name)
        
        self.logger.debug(f"Parsed {len(includes)} includes")
        return includes
    
    def _parse_typedef_relations(self, content: str) -> List[TypedefRelation]:
        """Parse typedef relationships"""
        relations = []
        
        # Improved typedef patterns to handle various cases
        typedef_patterns = [
            # Basic typedef: typedef type name;
            re.compile(r'typedef\s+(\w+(?:\s+\w+)*)\s+(\w+)\s*;'),
            # Pointer typedef: typedef type* name;
            re.compile(r'typedef\s+(\w+(?:\s+\w+)*\s*\*)\s+(\w+)\s*;'),
            # Function pointer: typedef return_type (*name)(params);
            re.compile(r'typedef\s+(\w+(?:\s+\w+)*)\s*\(\s*\*\s*(\w+)\s*\)\s*\([^)]*\)\s*;'),
            # Struct typedef: typedef struct { ... } name;
            re.compile(r'typedef\s+struct\s*\{[^}]*\}\s+(\w+)\s*;'),
            # Named struct typedef: typedef struct name { ... } alias;
            re.compile(r'typedef\s+struct\s+(\w+)\s*\{[^}]*\}\s+(\w+)\s*;')
        ]
        
        for pattern in typedef_patterns:
            for match in pattern.finditer(content):
                if len(match.groups()) == 2:
                    original_type = match.group(1).strip()
                    new_type = match.group(2)
                    
                    # Determine relationship type
                    # If the original type is a basic type, it's an alias
                    # If it's a complex type or struct, it's a definition
                    if self._is_basic_type(original_type):
                        relationship_type = 'alias'
                    else:
                        relationship_type = 'defines'
                    
                    relations.append(TypedefRelation(
                        typedef_name=new_type,
                        original_type=original_type,
                        relationship_type=relationship_type
                    ))
                elif len(match.groups()) == 1:
                    # For struct typedefs with only one group
                    new_type = match.group(1)
                    original_type = f"struct {new_type}"
                    
                    relations.append(TypedefRelation(
                        typedef_name=new_type,
                        original_type=original_type,
                        relationship_type='defines'
                    ))
        
        self.logger.debug(f"Parsed {len(relations)} typedef relations")
        return relations