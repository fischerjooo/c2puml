import re
from typing import Dict, List, Set, Optional, Tuple
from ..models.c_structures import Field, Function, Struct, Enum
import os

class CParser:
    def __init__(self):
        self.structs: Dict[str, Struct] = {}
        self.enums: Dict[str, Enum] = {}
        self.typedefs: Dict[str, str] = {}
        self.includes: Set[str] = set()
        
    def parse_files(self, file_paths: List[str]) -> None:
        """Parse multiple C files"""
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self._parse_content(content)
                    print(f"Parsed: {file_path}")
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
    
    def _parse_content(self, content: str) -> None:
        """Parse C code content"""
        # Remove comments
        content = self._remove_comments(content)
        
        # Parse includes
        self._parse_includes(content)
        
        # Parse structs
        self._parse_structs(content)
        
        # Parse enums
        self._parse_enums(content)
        
        # Parse typedefs
        self._parse_typedefs(content)
        
        # Parse functions
        self._parse_functions(content)
    
    def _remove_comments(self, content: str) -> str:
        """Remove C-style comments"""
        # Remove /* */ comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        # Remove // comments
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        return content
    
    def _parse_includes(self, content: str) -> None:
        """Parse #include statements"""
        pattern = r'#include\s*[<\"](.*?)[>\"]'
        matches = re.findall(pattern, content)
        self.includes.update(matches)
    
    def _parse_structs(self, content: str) -> None:
        """Parse struct definitions"""
        # Pattern for struct definition
        pattern = r'typedef\s+struct\s*(\w+)?\s*\{([^}]+)\}\s*(\w+)\s*;|struct\s+(\w+)\s*\{([^}]+)\}\s*;'
        
        for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
            if match.group(1) is not None or match.group(3) is not None:  # typedef struct
                struct_name = match.group(1) or match.group(3) or "anonymous"
                fields_text = match.group(2)
                typedef_name = match.group(3)
            else:  # regular struct
                struct_name = match.group(4)
                fields_text = match.group(5)
                typedef_name = None
            # Use typedef_name as struct_name if struct_name is None or 'anonymous'
            if (not struct_name or struct_name == "anonymous") and typedef_name:
                struct_name = typedef_name
            # Skip if fields_text is None
            if not fields_text:
                continue
            fields = self._parse_struct_fields(fields_text)
            struct = Struct(struct_name, fields, [], typedef_name)
            self.structs[struct_name] = struct
    
    def _parse_struct_fields(self, fields_text: str) -> List[Field]:
        """Parse struct fields"""
        fields = []
        lines = fields_text.strip().split(';')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Basic field parsing
            tokens = line.split()
            if len(tokens) >= 2:
                field_type = ' '.join(tokens[:-1])
                field_name = tokens[-1]
                
                # Check for pointer
                is_pointer = '*' in field_name
                field_name = field_name.replace('*', '')
                
                # Check for array
                is_array = '[' in field_name
                array_size = None
                if is_array:
                    array_match = re.search(r'\[([^\]]*)\]', field_name)
                    if array_match:
                        array_size = array_match.group(1)
                    field_name = re.sub(r'\[.*?\]', '', field_name)
                
                fields.append(Field(field_name, field_type, is_pointer, is_array, array_size))
        
        return fields
    
    def _parse_enums(self, content: str) -> None:
        """Parse enum definitions"""
        pattern = r'typedef\s+enum\s*(\w+)?\s*\{([^}]+)\}\s*(\w+)\s*;|enum\s+(\w+)\s*\{([^}]+)\}\s*;'
        
        for match in re.finditer(pattern, content, re.MULTILINE | re.DOTALL):
            if match.group(1):  # typedef enum
                enum_name = match.group(1) or "anonymous"
                values_text = match.group(2)
                typedef_name = match.group(3)
            else:  # regular enum
                enum_name = match.group(4)
                values_text = match.group(5)
                typedef_name = None
            
            values = self._parse_enum_values(values_text)
            enum = Enum(enum_name, values, typedef_name)
            self.enums[enum_name] = enum
    
    def _parse_enum_values(self, values_text: str) -> List[str]:
        """Parse enum values"""
        if values_text is None:
            return []
        values = []
        lines = values_text.strip().split(',')
        for line in lines:
            line = line.strip()
            if line:
                # Remove assignment if present
                value_name = line.split('=')[0].strip()
                values.append(value_name)
        return values
    
    def _parse_typedefs(self, content: str) -> None:
        """Parse typedef statements"""
        pattern = r'typedef\s+([^;]+?)\s+(\w+)\s*;'
        
        for match in re.finditer(pattern, content):
            original_type = match.group(1).strip()
            new_type = match.group(2).strip()
            
            # Skip struct and enum typedefs (already handled)
            if not ('struct' in original_type or 'enum' in original_type):
                self.typedefs[new_type] = original_type
    
    def _parse_functions(self, content: str) -> None:
        """Parse function definitions and associate with structs"""
        # Simple function parsing - can be enhanced
        pattern = r'(?:static\s+)?(\w+(?:\s*\*)?)\s+(\w+)\s*\(([^)]*)\)\s*\{'
        
        for match in re.finditer(pattern, content, re.MULTILINE):
            is_static = 'static' in match.group(0)
            return_type = match.group(1).strip()
            func_name = match.group(2)
            params_text = match.group(3)
            
            params = self._parse_function_params(params_text)
            func = Function(func_name, return_type, params, is_static)
            
            # Try to associate with struct based on naming conventions
            self._associate_function_with_struct(func)
    
    def _parse_function_params(self, params_text: str) -> List[Field]:
        """Parse function parameters"""
        params = []
        if not params_text.strip() or params_text.strip() == 'void':
            return params
        
        param_list = params_text.split(',')
        for param in param_list:
            param = param.strip()
            if param:
                tokens = param.split()
                if len(tokens) >= 2:
                    param_type = ' '.join(tokens[:-1])
                    param_name = tokens[-1]
                    
                    is_pointer = '*' in param_name
                    param_name = param_name.replace('*', '')
                    
                    params.append(Field(param_name, param_type, is_pointer))
        
        return params
    
    def _associate_function_with_struct(self, func: Function) -> None:
        """Associate function with struct based on naming conventions"""
        # Simple heuristic: if function name starts with struct name
        for struct_name, struct in self.structs.items():
            if func.name.lower().startswith(struct_name.lower()):
                struct.functions.append(func)
                break 

    @staticmethod
    def parse_header_file(header_path: str) -> Tuple[List[str], List[str]]:
        """Return (function prototypes, macros) from a header file, supporting multi-line and avoiding false positives from calls/macros. Only macro names are included, comments and values are stripped."""
        if not os.path.exists(header_path):
            return [], []
        prototypes = []
        macros = []
        with open(header_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # Join multi-line macros and function declarations
        joined_lines = []
        buffer = ''
        in_macro = False
        in_func = False
        for line in lines:
            stripped = line.rstrip()
            if in_macro:
                buffer += '\n' + stripped
                if not stripped.endswith('\\'):
                    joined_lines.append(buffer)
                    buffer = ''
                    in_macro = False
                continue
            if in_func:
                buffer += ' ' + stripped.lstrip()
                if stripped.endswith(';'):
                    joined_lines.append(buffer)
                    buffer = ''
                    in_func = False
                continue

            if stripped.startswith('#define'):
                if stripped.endswith('\\'):
                    buffer = stripped
                    in_macro = True
                else:
                    joined_lines.append(stripped)
            elif (stripped.endswith(';') and '(' in stripped and not stripped.startswith('typedef')):
                if not stripped.endswith(');') or stripped.count('(') != stripped.count(')'):
                    buffer = stripped
                    in_func = True
                else:
                    joined_lines.append(stripped)
            else:
                joined_lines.append(stripped)
        # Now process joined_lines for macros and prototypes
        proto_pattern = re.compile(
            r'^[a-zA-Z_][a-zA-Z0-9_ \t\*]*\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^;{]*\)\s*;$', re.MULTILINE
        )
        for line in joined_lines:
            l = line.strip()
            if l.startswith('#define'):
                # Remove comments (// or /* ... */)
                l_no_comment = re.split(r'//|/\*', l)[0].strip()
                # Only keep the macro name
                macro_parts = l_no_comment.split()
                if len(macro_parts) >= 2:
                    macro_name = macro_parts[1].split('(')[0]  # handle function-like macros
                    macros.append(f'+ #define {macro_name}')
            elif (
                proto_pattern.match(l)
                and not l.startswith('typedef')
                and '=' not in l
                and '{' not in l
                and '}' not in l
                and not l.startswith('#')
                and not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*\(', l)  # function call, not declaration
            ):
                # Extra check: must have a return type (not just function name)
                tokens = l.split('(')[0].strip().split()
                if len(tokens) > 1:
                    proto = l[:-1].strip()
                    proto = proto.replace('extern ', '')
                    prototypes.append(f'+ {proto}')
        return prototypes, macros 