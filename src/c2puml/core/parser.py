#!/usr/bin/env python3
"""
Parser module for C to PlantUML converter - Step 1: Parse C code files and generate model.json
"""
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Set

from ..models import Enum, EnumValue, Field, FileModel, ProjectModel, Struct
from .parser_tokenizer import (
    CTokenizer,
    StructureFinder,
    TokenType,
    find_enum_values,
    find_struct_fields,
)
from .preprocessor import PreprocessorManager
from .parser import AnonymousTypedefProcessor  # Updated import to use new unified system
from ..utils import detect_file_encoding

if TYPE_CHECKING:
    from ..config import Config
    from ..models import Alias, Enum, Field, Function, Struct, Union


# Compatibility wrapper classes for the old API
class CParser:
    """Compatibility wrapper for the old CParser class."""
    
    def __init__(self, config: Optional['Config'] = None):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.preprocessor = PreprocessorManager()
        self.anonymous_processor = AnonymousTypedefProcessor()
        self.tokenizer = CTokenizer()
    
    def parse_file(self, file_path: Path, config: Optional['Config'] = None) -> FileModel:
        """Parse a single C file and return a FileModel."""
        if config is None:
            config = self.config
        
        if config is None:
            raise ValueError("Config is required for parsing")
        
        self.logger.info(f"Parsing file: {file_path}")
        
        # Detect file encoding
        encoding = detect_file_encoding(file_path)
        
        # Read and preprocess the file
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        # Apply preprocessor directives
        processed_content = self.preprocessor.process(content, file_path, config)
        
        # Tokenize the content
        tokens = self.tokenizer.tokenize(processed_content)
        
        # Create structure finder
        structure_finder = StructureFinder(tokens)
        
        # Create file model
        file_model = FileModel(
            file_path=str(file_path),
            content=processed_content,
            structs={},
            unions={},
            enums={},
            aliases={},
            functions={},
            includes=[],
            defines={}
        )
        
        # Parse structures, unions, enums, and aliases using tokenizer
        self._parse_structures_with_tokenizer(file_model, tokens, structure_finder)
        self._parse_unions_with_tokenizer(file_model, tokens, structure_finder)
        self._parse_enums_with_tokenizer(file_model, tokens, structure_finder)
        self._parse_aliases_with_tokenizer(file_model, tokens)
        self._parse_functions_with_tokenizer(file_model, tokens, structure_finder)
        self._parse_includes_with_tokenizer(file_model, tokens)
        self._parse_defines_with_tokenizer(file_model, tokens)
        
        # Process anonymous typedefs using the new unified system
        self.anonymous_processor.process_file_model(file_model)
        
        return file_model
    
    def parse_project(self, source_paths: List[Path], config: 'Config') -> ProjectModel:
        """Parse multiple C files and return a ProjectModel."""
        self.logger.info(f"Parsing project with {len(source_paths)} source paths")
        
        project_model = ProjectModel(
            source_paths=[str(p) for p in source_paths],
            files={},
            global_types={},
            include_tree={}
        )
        
        # Parse each file
        for source_path in source_paths:
            if source_path.is_file():
                file_model = self.parse_file(source_path, config)
                project_model.files[str(source_path)] = file_model
            elif source_path.is_dir():
                # Recursively find C files
                for c_file in source_path.rglob("*.c"):
                    if self._should_parse_file(c_file, config):
                        file_model = self.parse_file(c_file, config)
                        project_model.files[str(c_file)] = file_model
                
                for h_file in source_path.rglob("*.h"):
                    if self._should_parse_file(h_file, config):
                        file_model = self.parse_file(h_file, config)
                        project_model.files[str(h_file)] = file_model
        
        # Build global types and include tree
        self._build_global_types(project_model)
        self._build_include_tree(project_model)
        
        return project_model
    
    def _should_parse_file(self, file_path: Path, config: 'Config') -> bool:
        """Check if a file should be parsed based on config filters."""
        # Check exclude patterns
        for pattern in config.exclude_patterns:
            if pattern.search(str(file_path)):
                return False
        
        # Check include patterns
        if config.include_patterns:
            for pattern in config.include_patterns:
                if pattern.search(str(file_path)):
                    return True
            return False
        
        return True
    
    def _parse_structures_with_tokenizer(self, file_model: FileModel, tokens, structure_finder) -> None:
        """Parse struct definitions using tokenizer."""
        structs = structure_finder.find_structs()
        
        for start_pos, end_pos, struct_name in structs:
            # Extract field information from token range
            field_tuples = find_struct_fields(tokens, start_pos, end_pos)
            
            # Convert to Field objects
            fields = []
            for field_name, field_type in field_tuples:
                try:
                    fields.append(Field(name=field_name, type=field_type))
                except ValueError as e:
                    self.logger.warning(f"Error creating field {field_name}: {e}")
            
            # For anonymous structs, use a special key
            if not struct_name:
                struct_name = "__anonymous_struct__"
            
            struct = Struct(
                name=struct_name,
                fields=fields
            )
            file_model.structs[struct_name] = struct
    
    def _parse_unions_with_tokenizer(self, file_model: FileModel, tokens, structure_finder) -> None:
        """Parse union definitions using tokenizer."""
        unions = structure_finder.find_unions()
        
        for start_pos, end_pos, union_name in unions:
            # Extract field information from token range
            field_tuples = find_struct_fields(tokens, start_pos, end_pos)
            
            # Convert to Field objects
            fields = []
            for field_name, field_type in field_tuples:
                try:
                    fields.append(Field(name=field_name, type=field_type))
                except ValueError as e:
                    self.logger.warning(f"Error creating union field {field_name}: {e}")
            
            # For anonymous unions, use a special key
            if not union_name:
                union_name = "__anonymous_union__"
            
            from ..models import Union
            union = Union(
                name=union_name,
                fields=fields
            )
            file_model.unions[union_name] = union
    
    def _parse_enums_with_tokenizer(self, file_model: FileModel, tokens, structure_finder) -> None:
        """Parse enum definitions using tokenizer."""
        enums = structure_finder.find_enums()
        
        for start_pos, end_pos, enum_name in enums:
            # Extract enum values from token range
            value_strs = find_enum_values(tokens, start_pos, end_pos)
            
            values = []
            for v in value_strs:
                if "=" in v:
                    name, val = v.split("=", 1)
                    name = name.strip()
                    val = val.strip()
                    if name:  # Only add if name is not empty
                        values.append(EnumValue(name=name, value=val))
                else:
                    name = v.strip()
                    if name:  # Only add if name is not empty
                        values.append(EnumValue(name=name))
            
            # For anonymous enums, use a special key
            if not enum_name:
                enum_name = "__anonymous_enum__"
            
            enum = Enum(
                name=enum_name,
                values=values
            )
            file_model.enums[enum_name] = enum
    
    def _parse_aliases_with_tokenizer(self, file_model: FileModel, tokens) -> None:
        """Parse typedef aliases using tokenizer."""
        from ..models import Alias
        
        aliases = {}
        i = 0
        while i < len(tokens):
            if tokens[i].type == TokenType.TYPEDEF:
                # Found typedef, parse it
                typedef_info = self._parse_single_typedef(tokens, i)
                if typedef_info:
                    typedef_name, original_type = typedef_info
                    
                    # Only include if it's NOT a struct/enum/union typedef
                    if original_type not in ["struct", "enum", "union"]:
                        aliases[typedef_name] = Alias(
                            name=typedef_name, type=original_type
                        )
            i += 1
        
        file_model.aliases = aliases
    
    def _parse_functions_with_tokenizer(self, file_model: FileModel, tokens, structure_finder) -> None:
        """Parse function declarations using tokenizer."""
        from ..models import Function
        
        functions = structure_finder.find_functions()
        
        for start_pos, end_pos, func_name, return_type, is_declaration in functions:
            # Parse parameters from the token range
            parameters = self._parse_function_parameters(tokens, start_pos, end_pos, func_name)
            
            try:
                function = Function(
                    name=func_name,
                    return_type=return_type,
                    parameters=parameters
                )
                # Add a custom attribute to track if this is a declaration
                function.is_declaration = is_declaration
                file_model.functions[func_name] = function
            except Exception as e:
                self.logger.warning(f"Error creating function {func_name}: {e}")
    
    def _parse_includes_with_tokenizer(self, file_model: FileModel, tokens) -> None:
        """Parse include directives using tokenizer."""
        includes = []
        
        for token in tokens:
            if token.type == TokenType.INCLUDE:
                # Extract include filename from the token value
                import re
                match = re.search(r'[<"\']([^>\'"]+)[>\'"]', token.value)
                if match:
                    includes.append(match.group(1))
        
        file_model.includes = includes
    
    def _parse_defines_with_tokenizer(self, file_model: FileModel, tokens) -> None:
        """Parse macro definitions using tokenizer."""
        defines = {}
        
        for token in tokens:
            if token.type == TokenType.DEFINE:
                # Extract macro name and parameters
                import re
                
                # For function-like macros: extract name and parameters
                func_match = re.search(
                    r"#define\s+([A-Za-z_][A-Za-z0-9_]*\s*\([^)]*\))", token.value
                )
                if func_match:
                    defines[func_match.group(1)] = token.value
                else:
                    # For simple defines: extract only the name
                    simple_match = re.search(
                        r"#define\s+([A-Za-z_][A-Za-z0-9_]*)", token.value
                    )
                    if simple_match:
                        defines[simple_match.group(1)] = token.value
        
        file_model.defines = defines
    
    def _parse_single_typedef(self, tokens, start_pos):
        """Parse a single typedef starting at the given position."""
        # Skip 'typedef' keyword
        pos = start_pos + 1
        
        # Skip whitespace and comments
        while pos < len(tokens) and tokens[pos].type in [
            TokenType.WHITESPACE,
            TokenType.COMMENT,
        ]:
            pos += 1
        
        if pos >= len(tokens):
            return None
        
        # Check if it's a struct/enum/union typedef (we'll handle these separately)
        if tokens[pos].type in [TokenType.STRUCT, TokenType.ENUM, TokenType.UNION]:
            return self._parse_complex_typedef(tokens, pos)
        
        # Collect all non-whitespace/comment tokens until semicolon
        all_tokens = []
        brace_count = 0
        paren_count = 0
        
        while pos < len(tokens):
            token = tokens[pos]
            
            # Track nested braces and parentheses
            if token.type == TokenType.LBRACE:
                brace_count += 1
            elif token.type == TokenType.RBRACE:
                brace_count -= 1
            elif token.type == TokenType.LPAREN:
                paren_count += 1
            elif token.type == TokenType.RPAREN:
                paren_count -= 1
            elif token.type == TokenType.SEMICOLON:
                # Only treat semicolon as end if we're not inside nested structures
                if brace_count == 0 and paren_count == 0:
                    break
            
            if token.type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                all_tokens.append(token)
            pos += 1
        
        if len(all_tokens) < 2:
            return None
        
        # Basic typedef: the last token is the typedef name, everything else is the type
        typedef_name = all_tokens[-1].value
        type_tokens = all_tokens[:-1]
        original_type = " ".join(t.value for t in type_tokens)
        
        return (typedef_name, original_type)
    
    def _parse_complex_typedef(self, tokens, start_pos):
        """Parse complex typedef (struct/enum/union)."""
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
        while pos < len(tokens) and tokens[pos].type in [
            TokenType.WHITESPACE,
            TokenType.COMMENT,
        ]:
            pos += 1
        
        if pos < len(tokens) and tokens[pos].type == TokenType.IDENTIFIER:
            typedef_name = tokens[pos].value
            struct_type = tokens[start_pos].value  # struct/enum/union
            return (typedef_name, struct_type)
        
        return None
    
    def _parse_function_parameters(self, tokens, start_pos, end_pos, func_name):
        """Parse function parameters from token range."""
        from ..models import Field
        
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
                    elif tokens[j].type not in [
                        TokenType.WHITESPACE,
                        TokenType.COMMENT,
                    ]:
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
        if not param_tokens or (
            len(param_tokens) == 1 and param_tokens[0].value == "void"
        ):
            return parameters
        
        # Split parameters by commas, but handle function pointers correctly
        current_param = []
        paren_depth = 0
        for token in param_tokens:
            if token.type == TokenType.LPAREN:
                paren_depth += 1
            elif token.type == TokenType.RPAREN:
                paren_depth -= 1
            elif token.type == TokenType.COMMA and paren_depth == 0:
                # Only split on commas that are not inside parentheses
                if current_param:
                    param = self._parse_single_parameter(current_param)
                    if param:
                        parameters.append(param)
                    current_param = []
                continue
            
            current_param.append(token)
        
        # Handle last parameter
        if current_param:
            param = self._parse_single_parameter(current_param)
            if param:
                parameters.append(param)
        
        return parameters
    
    def _parse_single_parameter(self, param_tokens):
        """Parse a single function parameter from tokens."""
        from ..models import Field
        
        if not param_tokens:
            return None
        
        # Handle variadic parameters
        if len(param_tokens) == 3 and all(t.value == "." for t in param_tokens):
            return Field(name="...", type="...")
        
        if len(param_tokens) == 1 and param_tokens[0].value == "...":
            return Field(name="...", type="...")
        
        # Regular parameter: last token is the parameter name
        if len(param_tokens) >= 2:
            param_name = param_tokens[-1].value
            type_tokens = param_tokens[:-1]
            param_type = " ".join(t.value for t in type_tokens)
            
            # Handle unnamed parameters (just type)
            if param_name in [
                "void", "int", "char", "float", "double", "long", "short", "unsigned", "signed",
            ]:
                return Field(name="unnamed", type=param_type + " " + param_name)
            
            if param_name and param_name.strip() and param_type and param_type.strip():
                return Field(name=param_name.strip(), type=param_type.strip())
        
        return None
    
    def _build_global_types(self, project_model: ProjectModel) -> None:
        """Build global types from all files."""
        global_types = {}
        
        for file_path, file_model in project_model.files.items():
            # Add structs
            for struct_name, struct in file_model.structs.items():
                global_types[struct_name] = {
                    'type': 'struct',
                    'file': file_path,
                    'data': struct
                }
            
            # Add unions
            for union_name, union in file_model.unions.items():
                global_types[union_name] = {
                    'type': 'union',
                    'file': file_path,
                    'data': union
                }
            
            # Add enums
            for enum_name, enum in file_model.enums.items():
                global_types[enum_name] = {
                    'type': 'enum',
                    'file': file_path,
                    'data': enum
                }
            
            # Add aliases
            for alias_name, alias in file_model.aliases.items():
                global_types[alias_name] = {
                    'type': 'alias',
                    'file': file_path,
                    'data': alias
                }
        
        project_model.global_types = global_types
    
    def _build_include_tree(self, project_model: ProjectModel) -> None:
        """Build include dependency tree."""
        include_tree = {}
        
        for file_path, file_model in project_model.files.items():
            include_tree[file_path] = file_model.includes
        
        project_model.include_tree = include_tree


class Parser(CParser):
    """Compatibility alias for CParser."""
    pass
