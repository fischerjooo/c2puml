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
            self.logger.warning(
                f"Failed to parse {len(failed_files)} files: {failed_files}"
            )

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

        # Parse file content
        file_model = FileModel(
            file_path=str(file_path.resolve()),
            relative_path=relative_path,
            project_root=project_root,
            encoding_used=encoding,
            structs=self._parse_structs(content),
            enums=self._parse_enums(content),
            unions=self._parse_unions(content),
            functions=self._parse_functions(content),
            globals=self._parse_globals(content),
            includes=self._parse_includes(content),
            macros=self._parse_macros(content),
            typedefs=self._parse_typedefs(content),
            typedef_relations=self._parse_typedef_relations(content),
            include_relations=[],
        )

        return file_model

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

        # No filtering at parsing step - all filtering should be done in transformer
        self.logger.debug(f"Found {len(files)} C/C++ files")
        return sorted(files)

    def _detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding"""
        try:
            import chardet

            with open(file_path, "rb") as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
                return result["encoding"] or "utf-8"
        except ImportError:
            return "utf-8"

    def _parse_structs(self, content: str) -> Dict[str, "Struct"]:
        """Parse struct definitions from content"""
        import re

        from .models import Field, Struct

        structs = {}
        # Match struct name { ... };
        pattern = r"struct\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{([^}]+)\}"
        matches = re.findall(pattern, content, re.DOTALL)

        for struct_name, struct_body in matches:
            fields = []
            # Parse fields within struct
            field_pattern = r"([A-Za-z_][A-Za-z0-9_]*)\s+([A-Za-z_][A-Za-z0-9_]*)\s*;"
            field_matches = re.findall(field_pattern, struct_body)
            for field_type, field_name in field_matches:
                fields.append(Field(field_name, field_type))

            structs[struct_name] = Struct(struct_name, fields)

        return structs

    def _parse_enums(self, content: str) -> Dict[str, "Enum"]:
        """Parse enum definitions from content"""
        import re

        from .models import Enum

        enums = {}
        # Match enum name { ... };
        pattern = r"enum\s+([A-Za-z_][A-Za-z0-9_]*)\s*\{([^}]+)\}"
        matches = re.findall(pattern, content, re.DOTALL)

        for enum_name, enum_body in matches:
            values = []
            # Parse enum values
            value_pattern = r"([A-Za-z_][A-Za-z0-9_]*)"
            value_matches = re.findall(value_pattern, enum_body)
            values.extend(value_matches)

            enums[enum_name] = Enum(enum_name, values)

        return enums

    def _parse_unions(self, content: str) -> Dict[str, "Union"]:
        """Parse union definitions from content"""
        # Implementation would go here - simplified for now
        return {}

    def _parse_functions(self, content: str) -> List["Function"]:
        """Parse function declarations from content"""
        import re

        from .models import Function

        functions = []
        # Match function declarations: return_type name(parameters)
        pattern = (
            r"([A-Za-z_][A-Za-z0-9_]*)\s+([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)\s*\{"
        )
        matches = re.findall(pattern, content)

        for return_type, func_name in matches:
            functions.append(Function(func_name, return_type, []))

        return functions

    def _parse_globals(self, content: str) -> List["Field"]:
        """Parse global variable declarations from content"""
        import re

        from .models import Field

        globals_list = []
        
        # Split content into lines and process each line
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines, comments, and preprocessor directives
            if (not line or 
                line.startswith('//') or 
                line.startswith('/*') or 
                line.startswith('#')):
                continue
                
            # Skip lines with function-like declarations (containing parentheses)
            if '(' in line and ')' in line:
                continue
                
            # Check if line ends with semicolon (basic global variable indicator)
            if line.endswith(';'):
                # Remove semicolon
                line = line[:-1].strip()
                
                # Split by equals sign to handle assignments
                if '=' in line:
                    # Format: type name = value
                    declaration_part = line.split('=')[0].strip()
                else:
                    # Format: type name;
                    declaration_part = line
                
                # Split declaration into parts
                parts = declaration_part.split()
                
                if len(parts) >= 2:
                    # Handle static keyword
                    if parts[0] == 'static':
                        parts = parts[1:]  # Remove 'static'
                    
                    if len(parts) >= 2:
                        # Last part is the variable name
                        var_name = parts[-1]
                        
                        # Check if variable name is valid
                        if re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', var_name):
                            # Everything before the variable name is the type
                            type_parts = parts[:-1]
                            type_name = ' '.join(type_parts).strip()
                            
                            if type_name:
                                globals_list.append(Field(var_name, type_name))

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
                
                # Continue collecting lines until we find the semicolon
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
                    struct_pattern = r'^struct\s*\{[^}]*\}\s+([A-Za-z_][A-Za-z0-9_]*)$'
                    match = re.match(struct_pattern, typedef_body, re.DOTALL)
                    if match:
                        typedef_name = match.group(1)
                        typedefs[typedef_name] = 'struct'
                    
                    # Pattern 3: typedef void (*name)(params); (function pointer)
                    func_ptr_pattern = r'^([^(*]+)\s*\(\s*\*\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)\s*\([^)]*\)$'
                    match = re.match(func_ptr_pattern, typedef_body)
                    if match:
                        return_type, typedef_name = match.groups()
                        typedefs[typedef_name] = f"{return_type.strip()} (*)(...)"
                
                i = j  # Skip the lines we've processed
            else:
                i += 1
                
        return typedefs

    def _parse_typedef_relations(self, content: str) -> List["TypedefRelation"]:
        """Parse typedef relationships from content"""
        # Implementation would go here - simplified for now
        return []

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
        model = self.c_parser.parse_project(project_root, recursive)

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
