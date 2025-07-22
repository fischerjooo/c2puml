#!/usr/bin/env python3
"""
Parser module for C to PlantUML converter - Step 1: Parse C code files and generate model.json

REFACTORED: Now uses tokenizer-based parsing instead of regex-based parsing
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from .models import Struct, Enum, Union, Function, Field, TypedefRelation

from .models import FileModel, ProjectModel
from .utils import detect_file_encoding
from .parser_tokenizer import (
    CTokenizer, StructureFinder, TokenType,
    find_struct_fields, find_enum_values, extract_token_range
)


class CParser:
    """C/C++ parser for extracting structural information from source code using tokenization"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tokenizer = CTokenizer()

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
        """Parse a single C/C++ file and return a file model using tokenization"""
        self.logger.debug(f"Parsing file: {file_path}")

        # Detect encoding
        encoding = self._detect_encoding(file_path)

        # Read file content
        with open(file_path, "r", encoding=encoding) as f:
            content = f.read()

        # Tokenize the content
        tokens = self.tokenizer.tokenize(content)
        self.logger.debug(f"Tokenized file into {len(tokens)} tokens")

        # Filter out whitespace and comments for structure finding
        filtered_tokens = self.tokenizer.filter_tokens(tokens)
        structure_finder = StructureFinder(filtered_tokens)

        # Parse different structures using tokenizer
        structs = self._parse_structs_with_tokenizer(tokens, structure_finder)
        enums = self._parse_enums_with_tokenizer(tokens, structure_finder)
        functions = self._parse_functions_with_tokenizer(tokens, structure_finder)
        
        return FileModel(
            file_path=str(file_path),
            relative_path=relative_path,
            project_root=project_root,
            encoding_used=encoding,
            structs=structs,
            enums=enums,
            functions=functions,
            globals=self._parse_globals_with_tokenizer(tokens),
            includes=self._parse_includes_with_tokenizer(tokens),
            macros=self._parse_macros_with_tokenizer(tokens),
            typedefs=self._parse_typedefs_with_tokenizer(tokens),
            typedef_relations=self._parse_typedef_relations_with_tokenizer(tokens, structs),
            include_relations=[],
        )

    def _parse_structs_with_tokenizer(self, tokens, structure_finder) -> Dict[str, "Struct"]:
        """Parse struct definitions using tokenizer"""
        from .models import Struct, Field
        
        structs = {}
        struct_infos = structure_finder.find_structs()
        
        for start_pos, end_pos, struct_name in struct_infos:
            if not struct_name:  # Skip anonymous structs for now
                continue
                
            # Need to map back to original token positions
            # Find the original token positions by looking at line/column info
            original_start = self._find_original_token_pos(tokens, structure_finder.tokens, start_pos)
            original_end = self._find_original_token_pos(tokens, structure_finder.tokens, end_pos)
            
            if original_start is not None and original_end is not None:
                # Extract field information from original token range
                field_tuples = find_struct_fields(tokens, original_start, original_end)
                
                # Convert to Field objects
                fields = []
                for field_name, field_type in field_tuples:
                    try:
                        fields.append(Field(field_name, field_type))
                    except Exception as e:
                        self.logger.warning(f"Error creating field {field_name}: {e}")
                
                structs[struct_name] = Struct(struct_name, fields)
                self.logger.debug(f"Parsed struct: {struct_name} with {len(fields)} fields")
        
        return structs

    def _parse_enums_with_tokenizer(self, tokens, structure_finder) -> Dict[str, "Enum"]:
        """Parse enum definitions using tokenizer"""
        from .models import Enum
        
        enums = {}
        enum_infos = structure_finder.find_enums()
        
        for start_pos, end_pos, enum_name in enum_infos:
            if not enum_name:  # Skip anonymous enums for now
                continue
                
            # Need to map back to original token positions
            original_start = self._find_original_token_pos(tokens, structure_finder.tokens, start_pos)
            original_end = self._find_original_token_pos(tokens, structure_finder.tokens, end_pos)
            
            if original_start is not None and original_end is not None:
                # Extract enum values from original token range
                values = find_enum_values(tokens, original_start, original_end)
                
                enums[enum_name] = Enum(enum_name, values)
                self.logger.debug(f"Parsed enum: {enum_name} with {len(values)} values")
        
        return enums

    def _parse_functions_with_tokenizer(self, tokens, structure_finder) -> List["Function"]:
        """Parse function declarations/definitions using tokenizer"""
        from .models import Function, Field
        
        functions = []
        function_infos = structure_finder.find_functions()
        
        for start_pos, end_pos, func_name, return_type, is_declaration in function_infos:
            # Map back to original token positions to parse parameters
            original_start = self._find_original_token_pos(tokens, structure_finder.tokens, start_pos)
            original_end = self._find_original_token_pos(tokens, structure_finder.tokens, end_pos)
            
            parameters = []
            if original_start is not None and original_end is not None:
                # Parse parameters from the token range
                parameters = self._parse_function_parameters(tokens, original_start, original_end, func_name)
            
            try:
                # Create function with declaration flag
                function = Function(func_name, return_type, parameters)
                # Add a custom attribute to track if this is a declaration
                function.is_declaration = is_declaration
                functions.append(function)
                self.logger.debug(f"Parsed function: {func_name} with {len(parameters)} parameters (declaration: {is_declaration})")
            except Exception as e:
                self.logger.warning(f"Error creating function {func_name}: {e}")
        
        return functions

    def _parse_globals_with_tokenizer(self, tokens) -> List["Field"]:
        """Parse global variables using tokenizer"""
        from .models import Field
        
        globals_list = []
        
        # Simple global parsing: look for patterns like "type name;" or "type name = value;"
        # This is a simplified implementation - we'll need to improve it for complex cases
        
        i = 0
        while i < len(tokens):
            # Skip preprocessor directives, comments, etc.
            if tokens[i].type in [TokenType.INCLUDE, TokenType.DEFINE, TokenType.PREPROCESSOR, 
                                TokenType.COMMENT, TokenType.WHITESPACE]:
                i += 1
                continue
            
            # Skip function definitions (look for parentheses)
            if self._looks_like_function(tokens, i):
                i = self._skip_function(tokens, i)
                continue
            
            # Skip struct/enum/union definitions
            if tokens[i].type in [TokenType.STRUCT, TokenType.ENUM, TokenType.UNION, TokenType.TYPEDEF]:
                i = self._skip_structure_definition(tokens, i)
                continue
            
            # Look for global variable patterns: [static/extern] type name [= value];
            global_info = self._parse_global_variable(tokens, i)
            if global_info:
                var_name, var_type, var_value = global_info
                try:
                    globals_list.append(Field(name=var_name, type=var_type, value=var_value))
                    self.logger.debug(f"Parsed global: {var_name} : {var_type}")
                except Exception as e:
                    self.logger.warning(f"Error creating global field {var_name}: {e}")
                i = self._skip_to_semicolon(tokens, i)
            else:
                i += 1
        
        return globals_list

    def _parse_includes_with_tokenizer(self, tokens) -> List[str]:
        """Parse #include directives using tokenizer"""
        includes = []
        
        for token in tokens:
            if token.type == TokenType.INCLUDE:
                # Extract include filename from the token value
                # e.g., "#include <stdio.h>" -> "stdio.h"
                import re
                match = re.search(r'[<"]([^>"]+)[>"]', token.value)
                if match:
                    includes.append(match.group(1))
        
        return includes

    def _parse_macros_with_tokenizer(self, tokens) -> List[str]:
        """Parse macro definitions using tokenizer"""
        macros = []
        
        for token in tokens:
            if token.type == TokenType.DEFINE:
                # Extract macro name from the token value
                # e.g., "#define PI 3.14159" -> "PI"
                import re
                match = re.search(r'#define\s+([A-Za-z_][A-Za-z0-9_]*)', token.value)
                if match:
                    macros.append(match.group(1))
        
        return macros

    def _parse_typedefs_with_tokenizer(self, tokens) -> Dict[str, str]:
        """Parse typedef definitions using tokenizer"""
        typedefs = {}
        
        i = 0
        while i < len(tokens):
            if tokens[i].type == TokenType.TYPEDEF:
                # Found typedef, parse it
                typedef_info = self._parse_single_typedef(tokens, i)
                if typedef_info:
                    typedef_name, original_type = typedef_info
                    typedefs[typedef_name] = original_type
                    
            i += 1
        
        return typedefs

    def _parse_typedef_relations_with_tokenizer(self, tokens, structs) -> List["TypedefRelation"]:
        """Parse typedef relationships using tokenizer - simplified for now"""
        # TODO: Implement proper typedef relation parsing with tokenizer
        # For now, return empty list to avoid breaking the skeleton
        return []

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

    def _find_original_token_pos(self, all_tokens, filtered_tokens, filtered_pos):
        """Find the position in all_tokens that corresponds to filtered_tokens[filtered_pos]"""
        if filtered_pos >= len(filtered_tokens):
            return None
        
        target_token = filtered_tokens[filtered_pos]
        
        # Search for the token in all_tokens by line and column
        for i, token in enumerate(all_tokens):
            if (token.line == target_token.line and 
                token.column == target_token.column and 
                token.value == target_token.value):
                return i
        
        return None

    def _parse_single_typedef(self, tokens, start_pos):
        """Parse a single typedef starting at the given position"""
        # Skip 'typedef' keyword
        pos = start_pos + 1
        
        # Skip whitespace and comments
        while pos < len(tokens) and tokens[pos].type in [TokenType.WHITESPACE, TokenType.COMMENT]:
            pos += 1
        
        if pos >= len(tokens):
            return None
        
        # Check if it's a struct/enum/union typedef (we'll handle these separately)
        if tokens[pos].type in [TokenType.STRUCT, TokenType.ENUM, TokenType.UNION]:
            return self._parse_complex_typedef(tokens, pos)
        
        # Simple typedef: typedef type name; or function pointer: typedef ret (*name)(params);
        all_tokens = []
        
        # Collect all non-whitespace/comment tokens until semicolon
        while pos < len(tokens) and tokens[pos].type != TokenType.SEMICOLON:
            if tokens[pos].type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                all_tokens.append(tokens[pos])
            pos += 1
        
        if len(all_tokens) < 2:
            return None
        
        # Check for function pointer pattern: return_type (*name)(params)
        # Look for the pattern (* name ) in the tokens
        for i in range(len(all_tokens) - 2):
            if (all_tokens[i].type == TokenType.LPAREN and 
                all_tokens[i + 1].type == TokenType.ASTERISK and 
                all_tokens[i + 2].type == TokenType.IDENTIFIER and
                i + 3 < len(all_tokens) and all_tokens[i + 3].type == TokenType.RPAREN):
                
                # This is a function pointer typedef
                typedef_name = all_tokens[i + 2].value
                # The type is everything combined
                original_type = ' '.join(t.value for t in all_tokens)
                return (typedef_name, original_type)
        
        # Check for array typedef pattern: type name[size]
        for i in range(len(all_tokens)):
            if (all_tokens[i].type == TokenType.LBRACKET and 
                i > 0 and all_tokens[i - 1].type == TokenType.IDENTIFIER):
                
                # This is an array typedef
                typedef_name = all_tokens[i - 1].value
                # The type is everything combined
                original_type = ' '.join(t.value for t in all_tokens)
                return (typedef_name, original_type)
        
        # Simple typedef: the last token should be the typedef name, everything else is the type
        typedef_name = all_tokens[-1].value
        type_tokens = all_tokens[:-1]
        original_type = ' '.join(t.value for t in type_tokens)
        return (typedef_name, original_type)
        
        return None

    def _parse_complex_typedef(self, tokens, start_pos):
        """Parse complex typedef (struct/enum/union)"""
        # For now, return a simplified version
        # TODO: Implement full complex typedef parsing
        
        # Find the typedef name by looking for the pattern after the closing brace
        brace_count = 0
        pos = start_pos
        
        # Find opening brace
        while pos < len(tokens) and tokens[pos].type != TokenType.LBRACE:
            pos += 1
        
        if pos >= len(tokens):
            return None
        
        # Skip to closing brace
        brace_count = 1
        pos += 1
        
        while pos < len(tokens) and brace_count > 0:
            if tokens[pos].type == TokenType.LBRACE:
                brace_count += 1
            elif tokens[pos].type == TokenType.RBRACE:
                brace_count -= 1
            pos += 1
        
        if brace_count > 0:
            return None
        
        # Find typedef name after closing brace
        while pos < len(tokens) and tokens[pos].type in [TokenType.WHITESPACE, TokenType.COMMENT]:
            pos += 1
        
        if pos < len(tokens) and tokens[pos].type == TokenType.IDENTIFIER:
            typedef_name = tokens[pos].value
            struct_type = tokens[start_pos].value  # struct/enum/union
            return (typedef_name, struct_type)
        
        return None

    def _looks_like_function(self, tokens, start_pos):
        """Check if the token sequence starting at start_pos looks like a function"""
        # Look ahead for parentheses within a reasonable distance
        for i in range(start_pos, min(start_pos + 10, len(tokens))):
            if tokens[i].type == TokenType.LPAREN:
                return True
            if tokens[i].type in [TokenType.SEMICOLON, TokenType.LBRACE, TokenType.RBRACE]:
                return False
        return False

    def _skip_function(self, tokens, start_pos):
        """Skip over a function definition or declaration"""
        # Find the end (either semicolon for declaration or closing brace for definition)
        i = start_pos
        brace_count = 0
        paren_count = 0
        
        while i < len(tokens):
            if tokens[i].type == TokenType.LPAREN:
                paren_count += 1
            elif tokens[i].type == TokenType.RPAREN:
                paren_count -= 1
            elif tokens[i].type == TokenType.LBRACE:
                brace_count += 1
            elif tokens[i].type == TokenType.RBRACE:
                brace_count -= 1
                if brace_count == 0 and paren_count == 0:
                    return i + 1
            elif tokens[i].type == TokenType.SEMICOLON and paren_count == 0 and brace_count == 0:
                return i + 1
            i += 1
        
        return i

    def _skip_structure_definition(self, tokens, start_pos):
        """Skip over struct/enum/union/typedef definition"""
        i = start_pos
        brace_count = 0
        
        while i < len(tokens):
            if tokens[i].type == TokenType.LBRACE:
                brace_count += 1
            elif tokens[i].type == TokenType.RBRACE:
                brace_count -= 1
                if brace_count == 0:
                    # Continue until semicolon
                    while i < len(tokens) and tokens[i].type != TokenType.SEMICOLON:
                        i += 1
                    return i + 1 if i < len(tokens) else i
            elif tokens[i].type == TokenType.SEMICOLON and brace_count == 0:
                return i + 1
            i += 1
        
        return i

    def _parse_global_variable(self, tokens, start_pos):
        """Parse a global variable declaration starting at start_pos"""
        # Look for pattern: [static/extern] type name [= value];
        i = start_pos
        collected_tokens = []
        
        # Collect tokens until semicolon
        while i < len(tokens) and tokens[i].type != TokenType.SEMICOLON:
            if tokens[i].type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                collected_tokens.append(tokens[i])
            i += 1
        
        if len(collected_tokens) < 2:
            return None
        
        # Skip modifiers
        start_idx = 0
        while (start_idx < len(collected_tokens) and 
               collected_tokens[start_idx].type in [TokenType.STATIC, TokenType.EXTERN, TokenType.CONST]):
            start_idx += 1
        
        # Check if there's an assignment
        assign_idx = None
        for j in range(start_idx, len(collected_tokens)):
            if collected_tokens[j].type == TokenType.ASSIGN:
                assign_idx = j
                break
        
        # Extract variable name and type
        if assign_idx is not None:
            # Has assignment: type name = value
            if assign_idx > start_idx + 1:
                var_name = collected_tokens[assign_idx - 1].value
                type_tokens = collected_tokens[start_idx:assign_idx - 1]
                value_tokens = collected_tokens[assign_idx + 1:]
                var_type = ' '.join(t.value for t in type_tokens)
                var_value = ' '.join(t.value for t in value_tokens)
                return (var_name, var_type, var_value)
        else:
            # No assignment: type name
            if len(collected_tokens) > start_idx + 1:
                var_name = collected_tokens[-1].value
                type_tokens = collected_tokens[start_idx:-1]
                var_type = ' '.join(t.value for t in type_tokens)
                return (var_name, var_type, None)
        
        return None

    def _skip_to_semicolon(self, tokens, start_pos):
        """Skip to the next semicolon"""
        i = start_pos
        while i < len(tokens) and tokens[i].type != TokenType.SEMICOLON:
            i += 1
        return i + 1 if i < len(tokens) else i

    def _parse_function_parameters(self, tokens, start_pos, end_pos, func_name):
        """Parse function parameters from token range"""
        from .models import Field
        
        parameters = []
        
        # Find the opening parenthesis for the function
        paren_start = None
        paren_end = None
        
        for i in range(start_pos, min(end_pos + 1, len(tokens))):
            if tokens[i].type == TokenType.IDENTIFIER and tokens[i].value == func_name:
                # Look for opening parenthesis after function name
                for j in range(i + 1, min(end_pos + 1, len(tokens))):
                    if tokens[j].type == TokenType.LPAREN:
                        paren_start = j
                        break
                    elif tokens[j].type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                        break
                break
        
        if paren_start is None:
            return parameters
        
        # Find matching closing parenthesis
        paren_depth = 1
        for i in range(paren_start + 1, min(end_pos + 1, len(tokens))):
            if tokens[i].type == TokenType.LPAREN:
                paren_depth += 1
            elif tokens[i].type == TokenType.RPAREN:
                paren_depth -= 1
                if paren_depth == 0:
                    paren_end = i
                    break
        
        if paren_end is None:
            return parameters
        
        # Parse parameter tokens between parentheses
        param_tokens = []
        for i in range(paren_start + 1, paren_end):
            if tokens[i].type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                param_tokens.append(tokens[i])
        
        # If no parameters or just "void", return empty list
        if not param_tokens or (len(param_tokens) == 1 and param_tokens[0].value == 'void'):
            return parameters
        
        # Split parameters by commas
        current_param = []
        for token in param_tokens:
            if token.type == TokenType.COMMA:
                if current_param:
                    param = self._parse_single_parameter(current_param)
                    if param:
                        parameters.append(param)
                    current_param = []
            else:
                current_param.append(token)
        
        # Handle last parameter
        if current_param:
            param = self._parse_single_parameter(current_param)
            if param:
                parameters.append(param)
        
        return parameters

    def _parse_single_parameter(self, param_tokens):
        """Parse a single function parameter from tokens"""
        from .models import Field
        
        if not param_tokens:
            return None
        
        # Handle variadic parameters
        if len(param_tokens) == 1 and param_tokens[0].value == '...':
            return Field(name='...', type='...')
        
        # For parameters like "int x" or "const char *name"
        if len(param_tokens) >= 2:
            # Last token is usually the parameter name
            param_name = param_tokens[-1].value
            type_tokens = param_tokens[:-1]
            param_type = ' '.join(t.value for t in type_tokens)
            
            return Field(name=param_name, type=param_type)
        elif len(param_tokens) == 1:
            # Single token - might be just type (like "void") or name
            token_value = param_tokens[0].value
            if token_value in ['void', 'int', 'char', 'float', 'double', 'long', 'short']:
                return Field(name='', type=token_value)
            else:
                return Field(name=token_value, type='')
        
        return None

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
