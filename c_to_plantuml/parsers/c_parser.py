import re
import os
from typing import Dict, List, Set, Optional, Tuple
from ..models.c_structures import Field, Function, Struct, Enum

class CParser:
    """C parser with compiled regex patterns and caching"""
    
    # Pre-compiled regex patterns for better performance
    COMMENT_BLOCK_PATTERN = re.compile(r'/\*.*?\*/', re.DOTALL)
    COMMENT_LINE_PATTERN = re.compile(r'//.*?$', re.MULTILINE)
    INCLUDE_PATTERN = re.compile(r'#include\s*[<\"](.*?)[>\"]')
    STRUCT_PATTERN = re.compile(
        r'typedef\s+struct\s*(\w+)?\s*\{([^}]+)\}\s*(\w+)\s*;|struct\s+(\w+)\s*\{([^}]+)\}\s*;',
        re.MULTILINE | re.DOTALL
    )
    ENUM_PATTERN = re.compile(
        r'typedef\s+enum\s*(\w+)?\s*\{([^}]+)\}\s*(\w+)\s*;|enum\s+(\w+)\s*\{([^}]+)\}\s*;',
        re.MULTILINE | re.DOTALL
    )
    TYPEDEF_PATTERN = re.compile(r'typedef\s+([^;]+?)\s+(\w+)\s*;')
    FUNCTION_PATTERN = re.compile(
        r'^\s*(?:static\s+)?([a-zA-Z_][\w\s\*]*?)\s+([a-zA-Z_][\w]*)\s*\(([^)]*)\)\s*\{',
        re.MULTILINE
    )
    GLOBAL_VAR_PATTERN = re.compile(
        r'^\s*(static\s+)?([a-zA-Z_][\w\s\*]*?)\s+([a-zA-Z_][\w]*)\s*(\[[^\]]*\])?\s*(=[^;]*)?;',
        re.MULTILINE
    )
    ARRAY_PATTERN = re.compile(r'\[([^\]]*)\]')
    MACRO_DEFINE_PATTERN = re.compile(r'^\s*#define\s+([a-zA-Z_][\w]*)', re.MULTILINE)
    FUNCTION_PROTO_PATTERN = re.compile(
        r'^\s*[a-zA-Z_][a-zA-Z0-9_ \t\*]*\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^;{]*\)\s*;$',
        re.MULTILINE
    )
    
    def __init__(self):
        self.structs: Dict[str, Struct] = {}
        self.enums: Dict[str, Enum] = {}
        self.typedefs: Dict[str, str] = {}
        self.includes: Set[str] = set()
        self.functions: List[Function] = []
        self.globals: List[Field] = []
        self.macros: List[str] = []
        
        # File caching for improved I/O performance
        self.file_cache: Dict[str, str] = {}
        self.encoding_cache: Dict[str, str] = {}
    
    def read_file_with_encoding_detection(self, file_path: str) -> Tuple[str, str]:
        """Read file with encoding detection and caching"""
        if file_path in self.file_cache:
            return self.file_cache[file_path], self.encoding_cache[file_path]
        
        # Try UTF-8 first, fall back to Latin-1
        for encoding in ['utf-8', 'latin-1']:
            try:
                with open(file_path, 'r', encoding=encoding, buffering=8192) as f:
                    content = f.read()
                self.file_cache[file_path] = content
                self.encoding_cache[file_path] = encoding
                return content, encoding
            except UnicodeDecodeError:
                continue
        
        raise ValueError(f"Could not decode file: {file_path}")
    
    def clear_cache(self) -> None:
        """Clear file cache to manage memory usage"""
        self.file_cache.clear()
        self.encoding_cache.clear()
    
    def reset_parser_state(self) -> None:
        """Reset parser state for processing a new file"""
        self.structs.clear()
        self.enums.clear()
        self.typedefs.clear()
        self.includes.clear()
        self.functions.clear()
        self.globals.clear()
        self.macros.clear()
    
    def parse_files(self, file_paths: List[str]) -> None:
        """Parse multiple C files"""
        for file_path in file_paths:
            try:
                content, encoding = self.read_file_with_encoding_detection(file_path)
                self._parse_content(content)
                print(f"Parsed: {file_path}")
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
    
    def parse_file(self, file_path: str) -> Tuple[str, str]:
        """Parse a single C file and return content and encoding used"""
        self.reset_parser_state()
        
        content, encoding = self.read_file_with_encoding_detection(file_path)
        self._parse_content(content)
        
        return content, encoding
    
    def _parse_content(self, content: str) -> None:
        """Parse C code content using compiled regex patterns"""
        # Remove comments first using compiled patterns
        content = self.COMMENT_BLOCK_PATTERN.sub('', content)
        content = self.COMMENT_LINE_PATTERN.sub('', content)
        
        # Parse different elements using compiled patterns
        self._parse_includes(content)
        self._parse_macros(content)
        self._parse_structs(content)
        self._parse_enums(content)
        self._parse_typedefs(content)
        self._parse_globals(content)
        self._parse_functions(content)
    
    def _remove_comments(self, content: str) -> str:
        """Remove C-style comments using compiled patterns"""
        content = self.COMMENT_BLOCK_PATTERN.sub('', content)
        content = self.COMMENT_LINE_PATTERN.sub('', content)
        return content
    
    def _parse_includes(self, content: str) -> None:
        """Parse #include statements using compiled regex"""
        matches = self.INCLUDE_PATTERN.findall(content)
        self.includes.update(matches)
    
    def _parse_macros(self, content: str) -> None:
        """Parse #define macros using compiled regex"""
        matches = self.MACRO_DEFINE_PATTERN.findall(content)
        self.macros = [f"- #define {macro}" for macro in matches]
    
    def _parse_structs(self, content: str) -> None:
        """Parse struct definitions using compiled regex"""
        for match in self.STRUCT_PATTERN.finditer(content):
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
                    array_match = self.ARRAY_PATTERN.search(field_name)
                    if array_match:
                        array_size = array_match.group(1)
                    field_name = self.ARRAY_PATTERN.sub('', field_name)
                
                fields.append(Field(field_name, field_type, is_pointer, is_array, array_size))
        
        return fields
    
    def _parse_enums(self, content: str) -> None:
        """Parse enum definitions using compiled regex"""
        for match in self.ENUM_PATTERN.finditer(content):
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
        """Parse typedef statements using compiled regex"""
        for match in self.TYPEDEF_PATTERN.finditer(content):
            original_type = match.group(1).strip()
            new_type = match.group(2).strip()
            
            # Skip struct and enum typedefs (already handled)
            if not ('struct' in original_type or 'enum' in original_type):
                self.typedefs[new_type] = original_type
    
    def _parse_globals(self, content: str) -> None:
        """Parse global variable declarations using compiled regex"""
        # Remove function bodies to avoid local variables
        code_wo_funcs = re.sub(r'\{[^{}]*\}', '{}', content, flags=re.DOTALL)
        
        for match in self.GLOBAL_VAR_PATTERN.finditer(code_wo_funcs):
            is_static = bool(match.group(1))
            var_type = match.group(2).strip()
            var_name = match.group(3)
            array_part = match.group(4)
            
            is_pointer = '*' in var_type or (array_part is not None)
            is_array = array_part is not None
            array_size = None
            if is_array and array_part:
                array_size = array_part.strip('[]')
            
            field = Field(var_name, var_type.replace('*', '').strip(), is_pointer, is_array, array_size)
            setattr(field, 'is_static', is_static)
            self.globals.append(field)
    
    def _parse_functions(self, content: str) -> None:
        """Parse function definitions using compiled regex"""
        control_keywords = {'if', 'else', 'for', 'while', 'switch', 'case', 'do', 'goto', 'return', 'break', 'continue', 'default'}
        
        for match in self.FUNCTION_PATTERN.finditer(content):
            return_type = match.group(1).strip()
            func_name = match.group(2)
            
            # Skip control flow keywords
            if func_name in control_keywords or return_type in control_keywords:
                continue
            
            is_static = 'static' in match.group(0)
            params_text = match.group(3)
            params = self._parse_function_params(params_text)
            
            func = Function(func_name, return_type, params, is_static)
            
            # Try to associate with struct based on naming conventions
            associated = False
            for struct_name, struct in self.structs.items():
                if func.name.lower().startswith(struct_name.lower()):
                    struct.functions.append(func)
                    associated = True
                    break
            
            if not associated:
                self.functions.append(func)
    
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
        """Parse header file and return (function prototypes, macros)"""
        if not os.path.exists(header_path):
            return [], []
        
        prototypes = []
        macros = []
        
        try:
            with open(header_path, 'r', encoding='utf-8', buffering=8192) as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(header_path, 'r', encoding='latin-1', buffering=8192) as f:
                content = f.read()
        
        # Use compiled patterns for better performance
        parser = CParser()
        
        # Extract macros
        macro_matches = parser.MACRO_DEFINE_PATTERN.findall(content)
        macros = [f'+ #define {macro}' for macro in macro_matches]
        
        # Extract function prototypes
        proto_matches = parser.FUNCTION_PROTO_PATTERN.findall(content)
        for proto in proto_matches:
            if ('typedef' not in proto and '=' not in proto and 
                '{' not in proto and '}' not in proto and not proto.startswith('#')):
                # Extra check: must have a return type (not just function name)
                tokens = proto.split('(')[0].strip().split()
                if len(tokens) > 1:
                    clean_proto = proto.replace('extern ', '').strip()
                    prototypes.append(f'+ {clean_proto}')
        
        return prototypes, macros 