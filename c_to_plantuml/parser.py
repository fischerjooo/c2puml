#!/usr/bin/env python3
"""
Parser module for C to PlantUML converter - Step 1: Parse C code files and generate model.json
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from .models import Struct, Enum, Union, Function, Field, TypedefRelation

from .models import FileModel, ProjectModel
from .utils import detect_file_encoding


class CParser:
    """C/C++ parser for extracting structural information from source code"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse_project(self, project_root: str, recursive: bool = True) -> ProjectModel:
        """Parse a C/C++ project and return a model"""
        project_root = Path(project_root).resolve()

        if not project_root.exists():
            raise ValueError(f"Project root not found: {project_root}")

        if not project_root.is_dir():
            raise ValueError(f"Project root must be a directory: {project_root}")

        self.logger.info(f"Parsing project: {project_root}")

        # Find C/C++ files
        c_files = self._find_c_files(project_root, recursive)
        self.logger.info(f"Found {len(c_files)} C/C++ files")

        # Parse each file
        files = {}
        failed_files = []

        for file_path in c_files:
            try:
                relative_path = str(file_path.relative_to(project_root))
                file_model = self.parse_file(
                    file_path, relative_path, str(project_root)
                )
                files[relative_path] = file_model

                self.logger.debug(f"Successfully parsed: {relative_path}")

            except Exception as e:
                self.logger.warning(f"Failed to parse {file_path}: {e}")
                failed_files.append(str(file_path))

        if failed_files:
            error_msg = (
                f"Failed to parse {len(failed_files)} files: {failed_files}. "
                "Stopping model processing."
            )
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

        model = ProjectModel(
            project_name=project_root.name,
            project_root=str(project_root),
            files=files,
            created_at=self._get_timestamp(),
        )

        self.logger.info(f"Parsing complete. Parsed {len(files)} files successfully.")
        return model

    def parse_file(
        self, file_path: Path, relative_path: str, project_root: str
    ) -> FileModel:
        """Parse a single C/C++ file and return a file model"""
        self.logger.debug(f"Parsing file: {file_path}")

        # Detect encoding
        encoding = self._detect_encoding(file_path)

        # Read file content
        with open(file_path, "r", encoding=encoding) as f:
            content = f.read()

        # Parse structs first
        structs = self._parse_structs(content)
        
        return FileModel(
            file_path=str(file_path),
            relative_path=relative_path,
            project_root=project_root,
            encoding_used=encoding,
            structs=structs,
            enums=self._parse_enums(content),
            functions=self._parse_functions(content),
            globals=self._parse_globals(content),
            includes=self._parse_includes(content),
            macros=self._parse_macros(content),
            typedefs=self._parse_typedefs(content),
            typedef_relations=self._parse_typedef_relations(content, structs),
            include_relations=[],
        )

    def _find_c_files(self, project_root: Path, recursive: bool) -> List[Path]:
        """Find all C/C++ files in the project"""
        c_extensions = {".c", ".h", ".cpp", ".cc", ".cxx", ".hpp", ".hxx"}
        files = []

        self.logger.debug(f"Searching for files with extensions: {c_extensions}")

        if recursive:
            for ext in c_extensions:
                files.extend(project_root.rglob(f"*{ext}"))
        else:
            for ext in c_extensions:
                files.extend(project_root.glob(f"*{ext}"))

        # Filter out hidden files and common exclude patterns
        filtered_files = []
        exclude_patterns = {".git", "__pycache__", "node_modules", ".vscode", ".idea"}

        for file_path in files:
            # Skip hidden files and directories
            if any(part.startswith(".") for part in file_path.parts):
                continue

            # Skip common exclude patterns
            if any(pattern in file_path.parts for pattern in exclude_patterns):
                continue

            filtered_files.append(file_path)

        self.logger.debug(f"Found {len(filtered_files)} C/C++ files after filtering")
        return sorted(filtered_files)

    def _detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding with platform-aware fallbacks"""
        return detect_file_encoding(file_path)

    def _parse_struct_fields(self, struct_body: str) -> List["Field"]:
        """Parse fields from a struct body"""
        import re
        from .models import Field
        
        fields = []
        # Improved regex: match type (with pointers/arrays), name, and array size if present
        # Handles: int x; char label[32]; double *ptr; int (*cb)(int);
        field_pattern = r"([A-Za-z_][A-Za-z0-9_\*\s]*?)\s+([A-Za-z_][A-Za-z0-9_]*)(\s*\[[^;]*\])?\s*;"
        import logging
        logger = logging.getLogger(__name__)
        for field_match in re.finditer(field_pattern, struct_body):
            field_type = field_match.group(1).strip()
            field_name = field_match.group(2).strip()
            array_size = field_match.group(3)
            if array_size:
                field_type = f"{field_type}{array_size.strip()}"
            logger.debug(f"[struct] About to create Field: type='{field_type}', name='{field_name}'")
            try:
                if field_name:
                    fields.append(Field(field_name, field_type))
            except Exception as e:
                logger.error(f"[struct] Exception creating Field: {e} | type='{field_type}', name='{field_name}'")
                raise
        return fields

    def _parse_structs(self, content: str) -> Dict[str, "Struct"]:
        """Parse struct definitions from content"""
        import re

        from .models import Field, Struct

        structs = {}
        
        # Pattern 1: struct name { ... }; (struct definition)
        pattern1 = r"struct\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{([^}]+)\}"
        matches1 = re.findall(pattern1, content, re.DOTALL)

        for struct_name, struct_body in matches1:
            fields = self._parse_struct_fields(struct_body)
            structs[struct_name] = Struct(struct_name, fields)

        # Pattern 2: typedef struct name { ... } typedef_name; (struct typedef)
        pattern2 = r"typedef\s+struct\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{([^}]+)\}\s+([A-Za-z_][A-Za-z0-9_]*)\s*;"
        matches2 = re.findall(pattern2, content, re.DOTALL)

        for struct_tag_name, struct_body, typedef_name in matches2:
            fields = self._parse_struct_fields(struct_body)
            # Remove "_tag" suffix if present for consistency
            clean_struct_name = struct_tag_name.replace('_tag', '')
            # Store both the struct tag name and the typedef name
            structs[clean_struct_name] = Struct(clean_struct_name, fields)
            # Also store under typedef name for backward compatibility
            structs[typedef_name] = Struct(typedef_name, fields)

        # Pattern 3: typedef struct { ... } typedef_name; (anonymous struct typedef)
        pattern3 = r"typedef\s+struct\s*\{([^}]+)\}\s+([A-Za-z_][A-Za-z0-9_]*)\s*;"
        matches3 = re.findall(pattern3, content, re.DOTALL)

        for struct_body, typedef_name in matches3:
            fields = self._parse_struct_fields(struct_body)
            structs[typedef_name] = Struct(typedef_name, fields)

        return structs

    def _parse_enums(self, content: str) -> Dict[str, "Enum"]:
        """Parse enum definitions from content"""
        import re

        from .models import Enum

        enums = {}
        
        # Pattern 1: enum name { ... }; (enum definition)
        pattern1 = r"enum\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{([^}]+)\}"
        matches1 = re.findall(pattern1, content, re.DOTALL)

        for enum_name, enum_body in matches1:
            values = self._parse_enum_values(enum_body)
            enums[enum_name] = Enum(enum_name, values)

        # Pattern 2: typedef enum name { ... } typedef_name; (enum typedef)
        pattern2 = r"typedef\s+enum\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{([^}]+)\}\s+([A-Za-z_][A-Za-z0-9_]*)\s*;"
        matches2 = re.findall(pattern2, content, re.DOTALL)

        for enum_tag_name, enum_body, typedef_name in matches2:
            values = self._parse_enum_values(enum_body)
            # Remove "_tag" suffix if present for consistency
            clean_enum_name = enum_tag_name.replace('_tag', '')
            # Store both the enum tag name and the typedef name
            enums[clean_enum_name] = Enum(clean_enum_name, values)
            # Also store under typedef name for backward compatibility
            enums[typedef_name] = Enum(typedef_name, values)

        # Pattern 3: typedef enum { ... } typedef_name; (anonymous enum typedef)
        pattern3 = r"typedef\s+enum\s*\{([^}]+)\}\s+([A-Za-z_][A-Za-z0-9_]*)\s*;"
        matches3 = re.findall(pattern3, content, re.DOTALL)

        for enum_body, typedef_name in matches3:
            values = self._parse_enum_values(enum_body)
            enums[typedef_name] = Enum(typedef_name, values)

        return enums

    def _parse_enum_values(self, enum_body: str) -> List[str]:
        """Parse enum values from enum body"""
        import re
        
        values = []
        # Parse enum values - handle both simple names and assignments
        # Pattern: NAME or NAME = VALUE
        value_pattern = r"([A-Za-z_][A-Za-z0-9_]*)(?:\s*=\s*([^,\s]+))?"
        value_matches = re.findall(value_pattern, enum_body)
        
        for value_match in value_matches:
            value_name = value_match[0]
            value_assignment = value_match[1] if value_match[1] else ""
            if value_assignment:
                values.append(f"{value_name} = {value_assignment}")
            else:
                values.append(value_name)
        
        return values

    def _parse_unions(self, content: str) -> Dict[str, "Union"]:
        """Parse union definitions from content"""
        # Implementation would go here - simplified for now
        return {}

    def _parse_functions(self, content: str) -> List["Function"]:
        """Parse function declarations and definitions from content, including prototypes in headers."""
        import re
        from .models import Function, Field

        functions = []
        seen = set()

        # Match function definitions: return_type name(params) {...}
        def_pattern = r"(?:static|inline|extern)?\s*([A-Za-z_][A-Za-z0-9_\*\s]*)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)\s*\{"  # with body
        # Match function declarations (prototypes): return_type name(params);
        decl_pattern = r"(?:static|inline|extern)?\s*([A-Za-z_][A-Za-z0-9_\*\s]*)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)\s*;"

        # Helper to parse parameter list
        def parse_params(param_str):
            params = []
            param_str = param_str.strip()
            if not param_str or param_str == 'void':
                return params
            for param in param_str.split(','):
                param = param.strip()
                if not param:
                    continue
                if param == '...':
                    # Skip variadic parameter
                    continue
                # Improved: handle pointer types and multiple spaces
                import re
                # Match: type (with pointers/const), name
                match = re.match(r'^(.*\S)\s+([A-Za-z_][A-Za-z0-9_]*)$', param)
                if match:
                    type_, name = match.groups()
                else:
                    # If only one word, treat as name if valid identifier, else skip
                    if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', param):
                        type_, name = '', param
                    else:
                        continue
                import logging
                logger = logging.getLogger(__name__)
                logger.debug(f"[funcparam] About to create Field: type='{type_}', name='{name}'")
                try:
                    if name and type_:
                        params.append(Field(name=name, type=type_.strip()))
                except Exception as e:
                    logger.error(f"[funcparam] Exception creating Field: {e} | type='{type_}', name='{name}'")
                    raise
            return params

        # Parse function definitions
        for match in re.finditer(def_pattern, content):
            return_type, func_name, params = match.groups()
            # Skip malformed functions
            if func_name.lower() in ['return', 'if', 'for', 'while', 'switch']:
                continue
            key = (func_name, return_type)
            if key not in seen:
                seen.add(key)
                functions.append(Function(func_name, return_type.strip(), parse_params(params)))

        # Parse function declarations (prototypes)
        for match in re.finditer(decl_pattern, content):
            return_type, func_name, params = match.groups()
            # Skip malformed functions
            if func_name.lower() in ['return', 'if', 'for', 'while', 'switch']:
                continue
            key = (func_name, return_type)
            if key not in seen:
                seen.add(key)
                functions.append(Function(func_name, return_type.strip(), parse_params(params)))

        return functions

    def _parse_globals(self, content: str) -> List["Field"]:
        """Parse global variable declarations from content"""
        import re
        import logging

        from .models import Field

        logger = logging.getLogger(__name__)
        globals_list = []
        
        # Track brace depth to ensure we're only parsing at top level
        brace_depth = 0
        in_function = False
        in_struct_or_enum = False
        struct_enum_brace_depth = 0
        
        # Split content into lines and process each line
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            original_line = line
            line = line.strip()
            
            logger.debug(f"Global parsing line {i+1}: '{original_line}' -> '{line}'")
            
            # Skip empty lines, comments, and preprocessor directives
            if (not line or 
                line.startswith('//') or 
                line.startswith('/*') or 
                line.startswith('#')):
                logger.debug(f"  Skipping line {i+1}: empty/comment/preprocessor")
                continue
                
            # Skip typedef declarations
            if line.startswith('typedef '):
                logger.debug(f"  Skipping line {i+1}: typedef")
                continue

            # Skip lines that are just closing braces (e.g., '} triangle_t;')
            if line.startswith('}') and line.endswith(';'):
                # This is a closing brace with a name, skip it
                logger.debug(f"  Skipping line {i+1}: closing brace with name")
                continue
            elif line.startswith('}'):
                # This is a closing brace that should be counted for depth tracking
                logger.debug(f"  Processing line {i+1}: closing brace")
                pass
                
            # Check if we're entering a struct or enum definition
            if line.startswith('struct ') or line.startswith('enum '):
                in_struct_or_enum = True
                logger.debug(f"  Entering struct/enum at line {i+1}")
            elif in_struct_or_enum and line.endswith(';') and struct_enum_brace_depth == 0:
                # End of struct/enum definition (closing brace with semicolon)
                in_struct_or_enum = False
                struct_enum_brace_depth = 0
                logger.debug(f"  Exiting struct/enum at line {i+1}")
                
            # Track brace depth separately for struct/enum vs main code
            open_braces = line.count('{')
            close_braces = line.count('}')
            
            if in_struct_or_enum:
                struct_enum_brace_depth += open_braces - close_braces
                logger.debug(f"  Struct/enum brace depth: {struct_enum_brace_depth}")
                
                # If we've closed all braces in the struct/enum, we're no longer in it
                if struct_enum_brace_depth <= 0:
                    in_struct_or_enum = False
                    struct_enum_brace_depth = 0
                    logger.debug(f"  Exiting struct/enum (braces closed) at line {i+1}")
            else:
                brace_depth += open_braces - close_braces
            
            # Ensure brace_depth doesn't go negative
            brace_depth = max(0, brace_depth)
            struct_enum_brace_depth = max(0, struct_enum_brace_depth)
            
            logger.debug(f"  Line {i+1}: brace_depth={brace_depth}, struct_enum_brace_depth={struct_enum_brace_depth}, in_function={in_function}, in_struct_or_enum={in_struct_or_enum}")
            
            # Check if we're entering a function (function declaration followed by opening brace)
            if '(' in line and ')' in line and '{' in line and not in_struct_or_enum:
                in_function = True
                logger.debug(f"  Entering function at line {i+1}")
            elif brace_depth == 0:
                in_function = False
                logger.debug(f"  Exiting function at line {i+1}")
            
            # Reset in_function flag when we're at top level and not in a function
            if brace_depth == 0 and not ('(' in line and ')' in line and '{' in line):
                in_function = False
            
            # Skip if we're inside a function, any block, or inside a struct/enum definition
            if in_function or brace_depth > 0 or in_struct_or_enum:
                logger.debug(f"  Skipping line {i+1}: inside function/block/struct_enum")
                continue
                
            # Skip lines with function-like declarations (containing parentheses)
            if '(' in line and ')' in line:
                logger.debug(f"  Skipping line {i+1}: function-like declaration")
                continue
                
            # Skip switch/case/default statements (case insensitive)
            line_lower = line.lower()
            if line_lower.startswith('case ') or line_lower.startswith('default:') or line_lower.startswith('switch '):
                logger.debug(f"  Skipping line {i+1}: switch/case/default")
                continue
                
            # Skip return statements
            if line_lower.startswith('return '):
                logger.debug(f"  Skipping line {i+1}: return statement")
                continue
                
            # Check if line ends with semicolon (basic global variable indicator)
            if line.endswith(';'):
                logger.debug(f"  Processing potential global at line {i+1}: '{line}'")
                # Remove semicolon
                line = line[:-1].strip()
                
                # Split by equals sign to handle assignments
                if '=' in line:
                    # Format: type name = value
                    declaration_part = line.split('=')[0].strip()
                    initialization_part = line.split('=', 1)[1].strip()
                else:
                    # Format: type name;
                    declaration_part = line
                    initialization_part = ""
                
                # Split declaration into parts
                parts = declaration_part.split()
                
                if len(parts) >= 2:
                    # Handle static keyword
                    if parts[0] == 'static':
                        parts = parts[1:]  # Remove 'static'
                    
                    if len(parts) >= 2:
                        # Last part is the variable name (may include array brackets)
                        var_name = parts[-1]
                        
                        # Check if variable name is valid (including array declarations)
                        if re.match(r'^[A-Za-z_][A-Za-z0-9_]*(\[[^\]]*\])*$', var_name):
                            # Extract base name without array brackets
                            base_name = re.sub(r'\[[^\]]*\]', '', var_name)
                            
                            # Everything before the variable name is the type
                            type_parts = parts[:-1]
                            type_name = ' '.join(type_parts).strip()
                            
                            if type_name:
                                # Create field with initialization value if present
                                field_type = type_name
                                if initialization_part:
                                    field_type = f"{type_name} = {initialization_part}"
                                
                                logger.debug(f"About to create Field: line='{line}', type='{field_type}', name='{base_name}'")
                                try:
                                    globals_list.append(Field(base_name, field_type))
                                    logger.debug(f"  Successfully added global: {base_name}")
                                except Exception as e:
                                    logger.error(f"Exception creating Field: {e} | line='{line}', type='{field_type}', name='{base_name}'")
                                    raise
                        else:
                            logger.debug(f"  Invalid variable name: {var_name}")
                    else:
                        logger.debug(f"  Not enough parts in declaration: {parts}")
                else:
                    logger.debug(f"  Not enough parts in line: {parts}")
            else:
                logger.debug(f"  Line {i+1} doesn't end with semicolon")

        logger.debug(f"Global parsing complete. Found {len(globals_list)} globals")
        return globals_list

    def _parse_includes(self, content: str) -> List[str]:
        """Parse #include directives from content"""
        import re

        includes = []
        # Match #include <header.h> or #include "header.h"
        pattern = r'#include\s*[<"]([^>"]+)[>"]'
        matches = re.findall(pattern, content)
        includes.extend(matches)
        return includes

    def _parse_macros(self, content: str) -> List[str]:
        """Parse macro definitions from content"""
        import re

        macros = []
        # Match #define MACRO_NAME or #define MACRO_NAME value
        pattern = r"#define\s+([A-Za-z_][A-Za-z0-9_]*)"
        matches = re.findall(pattern, content)
        macros.extend(matches)
        return macros

    def _parse_typedefs(self, content: str) -> Dict[str, str]:
        """Parse typedef definitions from content"""
        import re

        typedefs = {}
        
        # Split content into lines to handle multi-line typedefs
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('//') or line.startswith('/*'):
                i += 1
                continue
                
            # Check for typedef
            if line.startswith('typedef '):
                # Collect the full typedef declaration (may span multiple lines)
                typedef_text = line
                j = i + 1
                
                # For struct/enum/union typedefs, we need to collect until we find the closing brace and semicolon
                if 'struct {' in line or 'enum {' in line or 'union {' in line:
                    brace_count = 0
                    if '{' in line:
                        brace_count = line.count('{') - line.count('}')
                    
                    # Continue collecting lines until we find the closing brace and semicolon
                    while j < len(lines) and (brace_count > 0 or ';' not in typedef_text):
                        next_line = lines[j].strip()
                        typedef_text += ' ' + next_line
                        if '{' in next_line:
                            brace_count += next_line.count('{')
                        if '}' in next_line:
                            brace_count -= next_line.count('}')
                        j += 1
                else:
                    # For simple typedefs, continue until we find the semicolon
                    while j < len(lines) and ';' not in typedef_text:
                        typedef_text += ' ' + lines[j].strip()
                        j += 1
                
                # Now parse the complete typedef
                if ';' in typedef_text:
                    # Remove 'typedef ' prefix and ';' suffix
                    typedef_body = typedef_text[8:].rstrip(';').strip()
                    
                    # Handle different typedef patterns
                    
                    # Pattern 1: typedef type name; (simple typedef)
                    simple_pattern = r'^([^;]+)\s+([A-Za-z_][A-Za-z0-9_]*)$'
                    match = re.match(simple_pattern, typedef_body)
                    if match:
                        original_type, typedef_name = match.groups()
                        typedefs[typedef_name] = original_type.strip()
                    
                    # Pattern 2: typedef struct { ... } name; (struct typedef)
                    elif typedef_body.startswith('struct {') or typedef_body.startswith('struct{'):
                        # Find the closing brace and typedef name
                        brace_count = 0
                        start_pos = typedef_body.find('{')
                        if start_pos != -1:
                            brace_count = 1
                            pos = start_pos + 1
                            while pos < len(typedef_body) and brace_count > 0:
                                if typedef_body[pos] == '{':
                                    brace_count += 1
                                elif typedef_body[pos] == '}':
                                    brace_count -= 1
                                pos += 1
                            
                            if brace_count == 0:
                                # Extract the typedef name after the closing brace
                                remaining = typedef_body[pos:].strip()
                                name_match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)$', remaining)
                                if name_match:
                                    typedef_name = name_match.group(1)
                                    typedefs[typedef_name] = 'struct'
                    
                    # Pattern 3: typedef enum { ... } name; (enum typedef)
                    elif typedef_body.startswith('enum {') or typedef_body.startswith('enum{'):
                        # Find the closing brace and typedef name
                        brace_count = 0
                        start_pos = typedef_body.find('{')
                        if start_pos != -1:
                            brace_count = 1
                            pos = start_pos + 1
                            while pos < len(typedef_body) and brace_count > 0:
                                if typedef_body[pos] == '{':
                                    brace_count += 1
                                elif typedef_body[pos] == '}':
                                    brace_count -= 1
                                pos += 1
                            
                            if brace_count == 0:
                                # Extract the typedef name after the closing brace
                                remaining = typedef_body[pos:].strip()
                                name_match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)$', remaining)
                                if name_match:
                                    typedef_name = name_match.group(1)
                                    typedefs[typedef_name] = 'enum'
                    
                    # Pattern 4: typedef union { ... } name; (union typedef)
                    elif typedef_body.startswith('union {') or typedef_body.startswith('union{'):
                        # Find the closing brace and typedef name
                        brace_count = 0
                        start_pos = typedef_body.find('{')
                        if start_pos != -1:
                            brace_count = 1
                            pos = start_pos + 1
                            while pos < len(typedef_body) and brace_count > 0:
                                if typedef_body[pos] == '{':
                                    brace_count += 1
                                elif typedef_body[pos] == '}':
                                    brace_count -= 1
                                pos += 1
                            
                            if brace_count == 0:
                                # Extract the typedef name after the closing brace
                                remaining = typedef_body[pos:].strip()
                                name_match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)$', remaining)
                                if name_match:
                                    typedef_name = name_match.group(1)
                                    typedefs[typedef_name] = 'union'
                    
                    # Pattern 5: typedef void (*name)(params); (function pointer)
                    func_ptr_pattern = r'^([^(*]+)\s*\(\s*\*\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)\s*\([^)]*\)$'
                    match = re.match(func_ptr_pattern, typedef_body)
                    if match:
                        return_type, typedef_name = match.groups()
                        typedefs[typedef_name] = f"{return_type.strip()} (*)(...)"
                    
                    # Pattern 6: typedef type name[size]; (array typedef)
                    array_pattern = r'^([A-Za-z_][A-Za-z0-9_\*\s]*)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\[([^\]]+)\]$'
                    match = re.match(array_pattern, typedef_body)
                    if match:
                        base_type, typedef_name, array_size = match.groups()
                        typedefs[typedef_name] = f"{base_type.strip()}[{array_size.strip()}]"
                
                i = j  # Skip the lines we've processed
            else:
                i += 1
                
        return typedefs

    def _parse_typedef_relations(self, content: str, structs: Dict[str, "Struct"]) -> List["TypedefRelation"]:
        """Parse typedef relationships from content"""
        import re
        from .models import TypedefRelation
        typedef_relations = []
        lines = content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith('//') or line.startswith('/*'):
                i += 1
                continue
            if line.startswith('typedef '):
                typedef_text = line
                j = i + 1
                # Continue reading lines until we find the closing brace and semicolon
                brace_count = 0
                if '{' in typedef_text:
                    brace_count = typedef_text.count('{') - typedef_text.count('}')
                
                while j < len(lines):
                    next_line = lines[j].strip()
                    typedef_text += ' ' + next_line
                    if '{' in next_line:
                        brace_count += next_line.count('{')
                    if '}' in next_line:
                        brace_count -= next_line.count('}')
                    if ';' in next_line and brace_count == 0:
                        break
                    j += 1
                
                if ';' in typedef_text:
                    typedef_body = typedef_text[8:].rstrip(';').strip()
                    
                    # Pattern 1: typedef type name; (simple typedef)
                    # Only match if there are no braces in the typedef body
                    if '{' not in typedef_body and '}' not in typedef_body:
                        simple_pattern = r'^([^;]+)\s+([A-Za-z_][A-Za-z0-9_]*)$'
                        match = re.match(simple_pattern, typedef_body)
                        if match:
                            original_type, typedef_name = match.groups()
                            relationship_type = 'alias'
                            # If the original type is a known struct/enum/union name, treat as defines
                            if original_type.startswith('struct') or original_type.startswith('enum') or original_type.startswith('union'):
                                relationship_type = 'defines'
                            typedef_relations.append(TypedefRelation(typedef_name, original_type.strip(), relationship_type))
                    
                    # Pattern 2: typedef struct { ... } name; (struct typedef)
                    elif typedef_body.startswith('struct {') or typedef_body.startswith('struct{'):
                        # Find the closing brace and typedef name
                        brace_count = 0
                        start_pos = typedef_body.find('{')
                        if start_pos != -1:
                            brace_count = 1
                            pos = start_pos + 1
                            while pos < len(typedef_body) and brace_count > 0:
                                if typedef_body[pos] == '{':
                                    brace_count += 1
                                elif typedef_body[pos] == '}':
                                    brace_count -= 1
                                pos += 1
                            
                            if brace_count == 0:
                                # Extract the typedef name after the closing brace
                                remaining = typedef_body[pos:].strip()
                                name_match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)$', remaining)
                                if name_match:
                                    typedef_name = name_match.group(1)
                                    typedef_relations.append(TypedefRelation(typedef_name, 'struct', 'defines'))
                                    
                                    # Extract struct field information and add to structs
                                    struct_body = typedef_body[start_pos+1:pos-1]  # Extract content between braces
                                    fields = self._parse_struct_fields(struct_body)
                                    from .models import Struct
                                    structs[typedef_name] = Struct(typedef_name, fields)
                    
                    # Pattern 2b: typedef struct tag { ... } name; (struct typedef with tag)
                    elif re.match(r'^struct\s+[A-Za-z_][A-Za-z0-9_]*\s*\{', typedef_body):
                        # Extract the struct tag name first
                        struct_tag_match = re.match(r'^struct\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{', typedef_body)
                        if struct_tag_match:
                            struct_tag_name = struct_tag_match.group(1)
                            # Remove "_tag" suffix if present for consistency
                            clean_struct_tag_name = struct_tag_name.replace('_tag', '')
                            # Find the closing brace and typedef name
                            brace_count = 0
                            start_pos = typedef_body.find('{')
                            if start_pos != -1:
                                brace_count = 1
                                pos = start_pos + 1
                                while pos < len(typedef_body) and brace_count > 0:
                                    if typedef_body[pos] == '{':
                                        brace_count += 1
                                    elif typedef_body[pos] == '}':
                                        brace_count -= 1
                                    pos += 1
                                
                                if brace_count == 0:
                                    # Extract the typedef name after the closing brace
                                    remaining = typedef_body[pos:].strip()
                                    name_match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)$', remaining)
                                    if name_match:
                                        typedef_name = name_match.group(1)
                                        typedef_relations.append(TypedefRelation(typedef_name, 'struct', 'defines', clean_struct_tag_name))
                                        
                                        # Extract struct field information and add to structs
                                        struct_body = typedef_body[start_pos+1:pos-1]  # Extract content between braces
                                        fields = self._parse_struct_fields(struct_body)
                                        from .models import Struct
                                        structs[clean_struct_tag_name] = Struct(clean_struct_tag_name, fields)
                    
                    # Pattern 3: typedef enum { ... } name; (enum typedef)
                    elif typedef_body.startswith('enum {') or typedef_body.startswith('enum{'):
                        # Find the closing brace and typedef name
                        brace_count = 0
                        start_pos = typedef_body.find('{')
                        if start_pos != -1:
                            brace_count = 1
                            pos = start_pos + 1
                            while pos < len(typedef_body) and brace_count > 0:
                                if typedef_body[pos] == '{':
                                    brace_count += 1
                                elif typedef_body[pos] == '}':
                                    brace_count -= 1
                                pos += 1
                            
                            if brace_count == 0:
                                # Extract the typedef name after the closing brace
                                remaining = typedef_body[pos:].strip()
                                name_match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)$', remaining)
                                if name_match:
                                    typedef_name = name_match.group(1)
                                    typedef_relations.append(TypedefRelation(typedef_name, 'enum', 'defines'))
                    
                    # Pattern 3b: typedef enum tag { ... } name; (enum typedef with tag)
                    elif re.match(r'^enum\s+[A-Za-z_][A-Za-z0-9_]*\s*\{', typedef_body):
                        # Extract the enum tag name first
                        enum_tag_match = re.match(r'^enum\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{', typedef_body)
                        if enum_tag_match:
                            enum_tag_name = enum_tag_match.group(1)
                            # Remove "_tag" suffix if present for consistency
                            clean_enum_tag_name = enum_tag_name.replace('_tag', '')
                            # Find the closing brace and typedef name
                            brace_count = 0
                            start_pos = typedef_body.find('{')
                            if start_pos != -1:
                                brace_count = 1
                                pos = start_pos + 1
                                while pos < len(typedef_body) and brace_count > 0:
                                    if typedef_body[pos] == '{':
                                        brace_count += 1
                                    elif typedef_body[pos] == '}':
                                        brace_count -= 1
                                    pos += 1
                                
                                if brace_count == 0:
                                    # Extract the typedef name after the closing brace
                                    remaining = typedef_body[pos:].strip()
                                    name_match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)$', remaining)
                                    if name_match:
                                        typedef_name = name_match.group(1)
                                        typedef_relations.append(TypedefRelation(typedef_name, 'enum', 'defines', "", clean_enum_tag_name))
                    
                    # Pattern 4: typedef union { ... } name; (union typedef)
                    elif typedef_body.startswith('union {') or typedef_body.startswith('union{'):
                        # Find the closing brace and typedef name
                        brace_count = 0
                        start_pos = typedef_body.find('{')
                        if start_pos != -1:
                            brace_count = 1
                            pos = start_pos + 1
                            while pos < len(typedef_body) and brace_count > 0:
                                if typedef_body[pos] == '{':
                                    brace_count += 1
                                elif typedef_body[pos] == '}':
                                    brace_count -= 1
                                pos += 1
                            
                            if brace_count == 0:
                                # Extract the typedef name after the closing brace
                                remaining = typedef_body[pos:].strip()
                                name_match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)$', remaining)
                                if name_match:
                                    typedef_name = name_match.group(1)
                                    typedef_relations.append(TypedefRelation(typedef_name, 'union', 'defines'))
                    
                    # Pattern 4b: typedef union tag { ... } name; (union typedef with tag)
                    elif re.match(r'^union\s+[A-Za-z_][A-Za-z0-9_]*\s*\{', typedef_body):
                        # Find the closing brace and typedef name
                        brace_count = 0
                        start_pos = typedef_body.find('{')
                        if start_pos != -1:
                            brace_count = 1
                            pos = start_pos + 1
                            while pos < len(typedef_body) and brace_count > 0:
                                if typedef_body[pos] == '{':
                                    brace_count += 1
                                elif typedef_body[pos] == '}':
                                    brace_count -= 1
                                pos += 1
                            
                            if brace_count == 0:
                                # Extract the typedef name after the closing brace
                                remaining = typedef_body[pos:].strip()
                                name_match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)$', remaining)
                                if name_match:
                                    typedef_name = name_match.group(1)
                                    typedef_relations.append(TypedefRelation(typedef_name, 'union', 'defines'))
                    
                    # Pattern 5: typedef void (*name)(params); (function pointer)
                    func_ptr_pattern = r'^([^(*]+)\s*\(\s*\*\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)\s*\([^)]*\)$'
                    match = re.match(func_ptr_pattern, typedef_body)
                    if match:
                        return_type, typedef_name = match.groups()
                        typedef_relations.append(TypedefRelation(typedef_name, f"{return_type.strip()} (*)(...)", 'alias'))
                    
                    # Pattern 6: typedef type name[size]; (array typedef)
                    array_pattern = r'^([A-Za-z_][A-Za-z0-9_\*\s]*)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\[([^\]]+)\]$'
                    match = re.match(array_pattern, typedef_body)
                    if match:
                        base_type, typedef_name, array_size = match.groups()
                        typedef_relations.append(TypedefRelation(typedef_name, f"{base_type.strip()}[{array_size.strip()}]", 'alias'))
                
                i = j
            else:
                i += 1
        return typedef_relations

    def _get_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime

        return datetime.now().isoformat()


class Parser:
    """Main parser class for Step 1: Parse C code files and generate model.json"""

    def __init__(self):
        self.c_parser = CParser()
        self.logger = logging.getLogger(__name__)

    def parse(
        self, project_root: str, output_file: str = "model.json", recursive: bool = True
    ) -> str:
        """
        Step 1: Parse C code files and generate model.json

        Args:
            project_root: Root directory of C/C++ project
            output_file: Output JSON model file path
            recursive: Whether to search subdirectories recursively

        Returns:
            Path to the generated model.json file
        """
        self.logger.info(f"Step 1: Parsing C/C++ project: {project_root}")

        # Parse the project
        try:
            model = self.c_parser.parse_project(project_root, recursive)
        except RuntimeError as e:
            self.logger.error(f"Failed to parse project: {e}")
            raise

        # Save model to JSON file
        model.save(output_file)

        self.logger.info(f"Step 1 complete! Model saved to: {output_file}")
        self.logger.info(f"Found {len(model.files)} files")

        # Print summary
        total_structs = sum(len(f.structs) for f in model.files.values())
        total_enums = sum(len(f.enums) for f in model.files.values())
        total_functions = sum(len(f.functions) for f in model.files.values())
        self.logger.info(
            f"Summary: {total_structs} structs, {total_enums} enums, "
            f"{total_functions} functions"
        )

        return output_file
