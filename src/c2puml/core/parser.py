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
from .parser_anonymous_processor import AnonymousTypedefProcessor
from ..utils import detect_file_encoding

if TYPE_CHECKING:
    from ..config import Config
    from ..models import Alias, Enum, Field, Function, Struct, Union


class CParser:
    """C/C++ parser for extracting structural information from source code using tokenization"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tokenizer = CTokenizer()
        self.preprocessor = PreprocessorManager()

    def parse_project(
        self, source_folder: str, recursive_search: bool = True, config: "Config" = None
    ) -> ProjectModel:
        """Parse a C/C++ project and return a model"""
        # Enhanced source path validation
        if not source_folder or not isinstance(source_folder, str):
            raise ValueError(f"Source folder must be a non-empty string, got: {type(source_folder)}")
        
        if not source_folder.strip():
            raise ValueError("Source folder cannot be empty or whitespace")
        
        try:
            source_folder_path = Path(source_folder).resolve()
        except (OSError, RuntimeError) as e:
            raise ValueError(f"Failed to resolve source folder path '{source_folder}': {e}")

        if not source_folder_path.exists():
            # Provide helpful error message with suggestions
            error_msg = f"Source folder not found: {source_folder_path}"
            
            # Check if it's a relative path issue
            if not Path(source_folder).is_absolute():
                current_dir = Path.cwd()
                error_msg += f"\nCurrent working directory: {current_dir}"
                error_msg += f"\nTried to resolve relative path: {source_folder}"
            
            # Check if parent directory exists
            parent_dir = source_folder_path.parent
            if parent_dir.exists():
                error_msg += f"\nParent directory exists: {parent_dir}"
                # List contents of parent directory
                try:
                    contents = [item.name for item in parent_dir.iterdir() if item.is_dir()]
                    if contents:
                        error_msg += f"\nAvailable directories in parent: {', '.join(contents[:10])}"
                        if len(contents) > 10:
                            error_msg += f" (and {len(contents) - 10} more)"
                except (OSError, PermissionError):
                    error_msg += "\nCannot list parent directory contents (permission denied)"
            else:
                error_msg += f"\nParent directory does not exist: {parent_dir}"
            
            raise ValueError(error_msg)

        if not source_folder_path.is_dir():
            raise ValueError(f"Source folder must be a directory, got: {source_folder_path} (is_file: {source_folder_path.is_file()})")

        # Check if directory is readable
        try:
            source_folder_path.iterdir()
        except PermissionError:
            raise ValueError(f"Permission denied accessing source folder: {source_folder_path}")
        except OSError as e:
            raise ValueError(f"Error accessing source folder '{source_folder_path}': {e}")

        self.logger.info("Parsing project: %s", source_folder_path)

        # Find all C/C++ files in the project
        try:
            all_c_files = self._find_c_files(source_folder_path, recursive_search)
        except OSError as e:
            raise ValueError(f"Error searching for C/C++ files in '{source_folder_path}': {e}")
        
        self.logger.info("Found %d C/C++ files", len(all_c_files))

        # Apply file filtering based on configuration
        c_files = []
        if config:
            for file_path in all_c_files:
                if config._should_include_file(file_path.name):
                    c_files.append(file_path)
                    self.logger.debug(
                        "Included file after filtering: %s", file_path.name
                    )
                else:
                    self.logger.debug(
                        "Excluded file after filtering: %s", file_path.name
                    )
        else:
            c_files = all_c_files

        self.logger.info("After filtering: %d C/C++ files", len(c_files))

        # Parse each file using filename as key for simplified tracking
        files = {}
        failed_files = []

        for file_path in c_files:
            try:
                # Use relative path for tracking and filename as key
                relative_path = str(file_path.relative_to(source_folder_path))
                file_model = self.parse_file(file_path, relative_path)

                # Use filename as key (filenames are guaranteed to be unique)
                if file_model.name in files:
                    raise RuntimeError(
                        f"Duplicate filename detected: '{file_model.name}' from '{file_path}'. "
                        f"Already seen from '{files[file_model.name].file_path}'."
                    )
                files[file_model.name] = file_model

                self.logger.debug("Successfully parsed: %s", relative_path)

            except (OSError, ValueError) as e:
                self.logger.warning("Failed to parse %s: %s", file_path, e)
                failed_files.append(str(file_path))

        if failed_files:
            error_msg = (
                f"Failed to parse {len(failed_files)} files: {failed_files}. "
                "Stopping model processing."
            )
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

        model = ProjectModel(
            project_name=source_folder_path.name,
            source_folder=str(source_folder_path),
            files=files,
        )

        # Update all uses fields across the entire project
        model.update_uses_fields()

        self.logger.info("Parsing complete. Parsed %d files successfully.", len(files))
        return model

    def parse_file(self, file_path: Path, relative_path: str) -> FileModel:
        """Parse a single C/C++ file and return a file model using tokenization"""
        self.logger.debug("Parsing file: %s", file_path)

        # Detect encoding
        encoding = self._detect_encoding(file_path)

        # Read file content
        with open(file_path, "r", encoding=encoding) as f:
            content = f.read()

        # Tokenize the content
        tokens = self.tokenizer.tokenize(content)
        self.logger.debug("Tokenized file into %d tokens", len(tokens))

        # Process preprocessor directives
        self.preprocessor.add_defines_from_content(tokens)
        processed_tokens = self.preprocessor.process_file(tokens)
        self.logger.debug(
            "Preprocessor processed %d tokens -> %d tokens",
            len(tokens),
            len(processed_tokens),
        )

        # Filter out whitespace and comments for structure finding
        filtered_tokens = self.tokenizer.filter_tokens(processed_tokens)
        structure_finder = StructureFinder(filtered_tokens)

        # Parse different structures using tokenizer
        structs = self._parse_structs_with_tokenizer(processed_tokens, structure_finder)
        enums = self._parse_enums_with_tokenizer(processed_tokens, structure_finder)
        unions = self._parse_unions_with_tokenizer(processed_tokens, structure_finder)
        functions = self._parse_functions_with_tokenizer(
            processed_tokens, structure_finder
        )
        aliases = self._parse_aliases_with_tokenizer(processed_tokens)

        # "uses" fields will be updated when we have the full project model

        # Map typedef names to anonymous structs/enums/unions if needed
        # This logic will be handled by typedef_relations instead

        file_model = FileModel(
            file_path=str(file_path),
            structs=structs,
            enums=enums,
            unions=unions,
            functions=functions,
            globals=self._parse_globals_with_tokenizer(processed_tokens),
            includes=self._parse_includes_with_tokenizer(processed_tokens),
            macros=self._parse_macros_with_tokenizer(processed_tokens),
            aliases=aliases,
            # Tag names are now stored in struct/enum/union objects
        )

        # Process anonymous typedefs after initial parsing
        anonymous_processor = AnonymousTypedefProcessor()
        anonymous_processor.process_file_model(file_model)

        return file_model

    def _parse_structs_with_tokenizer(
        self, tokens, structure_finder
    ) -> Dict[str, "Struct"]:
        """Parse struct definitions using tokenizer"""

        structs = {}
        struct_infos = structure_finder.find_structs()

        for start_pos, end_pos, struct_name in struct_infos:
            # Need to map back to original token positions
            # Find the original token positions by looking at line/column info
            original_start = self._find_original_token_pos(
                tokens, structure_finder.tokens, start_pos
            )
            original_end = self._find_original_token_pos(
                tokens, structure_finder.tokens, end_pos
            )

            if original_start is not None and original_end is not None:
                # Extract field information from original token range
                field_tuples = find_struct_fields(tokens, original_start, original_end)

                # Convert to Field objects
                fields = []
                for field_name, field_type in field_tuples:
                    try:
                        fields.append(Field(field_name, field_type))
                    except ValueError as e:
                        self.logger.warning(
                            "Error creating field %s: %s", field_name, e
                        )

                # For anonymous structs, use a special key that can be mapped later
                if not struct_name:
                    struct_name = "__anonymous_struct__"

                # Extract tag name if this is a typedef struct
                tag_name = ""
                if struct_name and not struct_name.startswith("__anonymous"):
                    # Check if this struct has a typedef
                    tag_name = self._extract_tag_name_for_struct(tokens, struct_name)

                # Only register non-empty struct names here; anonymous will be created by the anonymous processor
                if struct_name:
                    structs[struct_name] = Struct(
                        struct_name, fields, tag_name=tag_name, uses=[]
                    )
                self.logger.debug(
                    "Parsed struct: %s with %d fields", struct_name, len(fields)
                )

        return structs

    def _parse_enums_with_tokenizer(
        self, tokens, structure_finder
    ) -> Dict[str, "Enum"]:
        """Parse enum definitions using tokenizer"""
        enums = {}
        enum_infos = structure_finder.find_enums()

        for start_pos, end_pos, enum_name in enum_infos:
            # Need to map back to original token positions
            original_start = self._find_original_token_pos(
                tokens, structure_finder.tokens, start_pos
            )
            original_end = self._find_original_token_pos(
                tokens, structure_finder.tokens, end_pos
            )

            if original_start is not None and original_end is not None:
                # Extract enum values from original token range
                value_strs = find_enum_values(tokens, original_start, original_end)
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

                # For anonymous enums, use a special key that can be mapped later
                if not enum_name:
                    enum_name = "__anonymous_enum__"

                # Extract tag name if this is a typedef enum
                tag_name = ""
                if enum_name and not enum_name.startswith("__anonymous"):
                    # Check if this enum has a typedef
                    tag_name = self._extract_tag_name_for_enum(tokens, enum_name)

                enums[enum_name] = Enum(enum_name, values, tag_name=tag_name)
                self.logger.debug(
                    "Parsed enum: %s with %d values", enum_name, len(values)
                )

        return enums

    def _parse_unions_with_tokenizer(
        self, tokens, structure_finder
    ) -> Dict[str, "Union"]:
        """Parse union definitions using tokenizer"""
        from ..models import Field, Union

        unions = {}
        union_infos = structure_finder.find_unions()

        for start_pos, end_pos, union_name in union_infos:
            # Need to map back to original token positions
            original_start = self._find_original_token_pos(
                tokens, structure_finder.tokens, start_pos
            )
            original_end = self._find_original_token_pos(
                tokens, structure_finder.tokens, end_pos
            )

            if original_start is not None and original_end is not None:
                # Extract field information from original token range
                field_tuples = find_struct_fields(tokens, original_start, original_end)

                # Convert to Field objects
                fields = []
                for field_name, field_type in field_tuples:
                    try:
                        fields.append(Field(field_name, field_type))
                    except ValueError as e:
                        self.logger.warning(
                            "Error creating union field %s: %s", field_name, e
                        )

                # For anonymous unions, use a special key that can be mapped later
                if not union_name:
                    union_name = "__anonymous_union__"

                # Extract tag name if this is a typedef union
                tag_name = ""
                if union_name and not union_name.startswith("__anonymous"):
                    # Check if this union has a typedef
                    tag_name = self._extract_tag_name_for_union(tokens, union_name)

                unions[union_name] = Union(
                    union_name, fields, tag_name=tag_name, uses=[]
                )
                self.logger.debug(
                    "Parsed union: %s with %d fields", union_name, len(fields)
                )

        return unions

    def _parse_functions_with_tokenizer(
        self, tokens, structure_finder
    ) -> List["Function"]:
        """Parse function declarations/definitions using tokenizer"""
        from ..models import Function

        functions = []
        function_infos = structure_finder.find_functions()

        for (
            start_pos,
            end_pos,
            func_name,
            return_type,
            is_declaration,
            is_inline,
        ) in function_infos:
            # Map back to original token positions to parse parameters
            original_start = self._find_original_token_pos(
                tokens, structure_finder.tokens, start_pos
            )
            original_end = self._find_original_token_pos(
                tokens, structure_finder.tokens, end_pos
            )

            parameters = []
            if original_start is not None and original_end is not None:
                # Parse parameters from the token range
                parameters = self._parse_function_parameters(
                    tokens, original_start, original_end, func_name
                )

            try:
                # Create function with declaration flag
                function = Function(func_name, return_type, parameters)
                # Add custom attributes to track if this is a declaration and if it's inline
                function.is_declaration = is_declaration
                function.is_inline = is_inline
                functions.append(function)
                self.logger.debug(
                    f"Parsed function: {func_name} with {len(parameters)} parameters (declaration: {is_declaration}, inline: {is_inline})"
                )
            except Exception as e:
                self.logger.warning("Error creating function %s: %s", func_name, e)

        return functions

    def _parse_globals_with_tokenizer(self, tokens) -> List["Field"]:
        """Parse global variables using tokenizer"""
        from ..models import Field

        globals_list = []

        i = 0
        while i < len(tokens):
            # Skip preprocessor directives, comments, etc.
            if tokens[i].type in [
                TokenType.INCLUDE,
                TokenType.DEFINE,
                TokenType.COMMENT,
                TokenType.WHITESPACE,
                TokenType.NEWLINE,
            ]:
                i += 1
                continue

            # Skip preprocessor directives but keep their content
            if tokens[i].type == TokenType.PREPROCESSOR:
                i = self._skip_preprocessor_directives(tokens, i)
                continue

            # Skip function definitions (look for parentheses)
            if self._looks_like_function(tokens, i):
                i = self._skip_function(tokens, i)
                continue

            # Skip struct/enum/union definitions
            if tokens[i].type in [
                TokenType.STRUCT,
                TokenType.ENUM,
                TokenType.UNION,
                TokenType.TYPEDEF,
            ]:
                i = self._skip_structure_definition(tokens, i)
                continue

            # Skip if we're inside a struct definition (look for opening brace)
            if i > 0 and tokens[i - 1].type == TokenType.LBRACE:
                # We're inside a struct, skip until closing brace
                brace_count = 1
                j = i
                while j < len(tokens) and brace_count > 0:
                    if tokens[j].type == TokenType.LBRACE:
                        brace_count += 1
                    elif tokens[j].type == TokenType.RBRACE:
                        brace_count -= 1
                    j += 1
                i = j
                continue

            # Skip macros and other preprocessor content
            if tokens[i].type == TokenType.DEFINE:
                # Skip the entire macro content (multi-line macros are now merged)
                i += 1
                continue

            # Additional check: skip if we're inside any brace block (struct, function, etc.)
            brace_count = 0
            j = i - 1
            while j >= 0:
                if tokens[j].type == TokenType.RBRACE:
                    brace_count += 1
                elif tokens[j].type == TokenType.LBRACE:
                    brace_count -= 1
                    if brace_count < 0:
                        # We're inside a brace block, skip this token
                        i += 1
                        break
                j -= 1
            else:
                # Not inside a brace block, proceed with global variable parsing
                global_info = self._parse_global_variable(tokens, i)
                if global_info:
                    var_name, var_type, var_value = global_info
                    # Only add if it looks like a real global variable (not a fragment)
                    if (
                        var_name
                        and var_name.strip()
                        and var_type
                        and var_type.strip()
                        and not var_name.startswith("#")
                        and len(var_type) < 200
                        and not var_type.startswith("\\")
                        and not var_name.startswith("\\")
                        and "\\" not in var_type
                        and "\\" not in var_name
                    ):
                        try:
                            # Additional validation before creating Field
                            stripped_name = var_name.strip()
                            stripped_type = var_type.strip()
                            if stripped_name and stripped_type:
                                globals_list.append(
                                    Field(
                                        name=stripped_name,
                                        type=stripped_type,
                                        value=var_value,
                                    )
                                )
                                self.logger.debug(
                                    f"Parsed global: {stripped_name} : {stripped_type}"
                                )
                        except Exception as e:
                            self.logger.warning(
                                f"Error creating global field {var_name}: {e}"
                            )
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
                # e.g., '#include "header.h"' -> "header.h"
                # e.g., "#include 'header.h'" -> "header.h"
                import re

                match = re.search(r'[<"\']([^>\'"]+)[>\'"]', token.value)
                if match:
                    # Return just the filename without quotes or angle brackets
                    includes.append(match.group(1))

        return includes

    def _parse_macros_with_tokenizer(self, tokens) -> List[str]:
        """Parse macro definitions using tokenizer"""
        macros = []

        for token in tokens:
            if token.type == TokenType.DEFINE:
                # Store the full macro definition for display flexibility
                # e.g., "#define PI 3.14159" -> "#define PI 3.14159"
                # e.g., "#define MIN(a, b) ((a) < (b) ? (a) : (b))" -> "#define MIN(a, b) ((a) < (b) ? (a) : (b))"
                macro_definition = token.value.strip()
                if macro_definition not in macros:
                    macros.append(macro_definition)

        return macros

    def _parse_aliases_with_tokenizer(self, tokens) -> Dict[str, "Alias"]:
        """Parse type aliases (primitive or derived typedefs) using tokenizer"""
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
                            name=typedef_name, original_type=original_type, uses=[]
                        )

            i += 1

        return aliases

    # _parse_typedef_relations_with_tokenizer method removed - tag names are now in struct/enum/union

    def _extract_tag_name_for_struct(self, tokens, struct_name: str) -> str:
        """Extract tag name for a struct if it has a typedef"""
        i = 0
        while i < len(tokens):
            if tokens[i].type == TokenType.TYPEDEF:
                typedef_info = self._parse_single_typedef(tokens, i)
                if typedef_info:
                    typedef_name, original_type = typedef_info
                    if original_type == "struct" and typedef_name == struct_name:
                        # Extract the tag name from the typedef
                        return self._extract_tag_name_from_typedef(tokens, i)
            i += 1
        return ""

    def _extract_tag_name_for_enum(self, tokens, enum_name: str) -> str:
        """Extract tag name for an enum if it has a typedef"""
        i = 0
        while i < len(tokens):
            if tokens[i].type == TokenType.TYPEDEF:
                typedef_info = self._parse_single_typedef(tokens, i)
                if typedef_info:
                    typedef_name, original_type = typedef_info
                    if original_type == "enum" and typedef_name == enum_name:
                        # Extract the tag name from the typedef
                        return self._extract_tag_name_from_typedef(tokens, i)
            i += 1
        return ""

    def _extract_tag_name_for_union(self, tokens, union_name: str) -> str:
        """Extract tag name for a union if it has a typedef"""
        i = 0
        while i < len(tokens):
            if tokens[i].type == TokenType.TYPEDEF:
                typedef_info = self._parse_single_typedef(tokens, i)
                if typedef_info:
                    typedef_name, original_type = typedef_info
                    if original_type == "union" and typedef_name == union_name:
                        # Extract the tag name from the typedef
                        return self._extract_tag_name_from_typedef(tokens, i)
            i += 1
        return ""

    def _extract_non_primitive_types(
        self, type_str: str, available_types: Set[str]
    ) -> List[str]:
        """Extract non-primitive type names from a type string that exist in available_types"""
        # Define primitive types
        primitive_types = {
            "void",
            "char",
            "short",
            "int",
            "long",
            "float",
            "double",
            "signed",
            "unsigned",
            "const",
            "volatile",
            "static",
            "extern",
            "auto",
            "register",
            "inline",
            "restrict",
            "size_t",
            "ptrdiff_t",
            "int8_t",
            "int16_t",
            "int32_t",
            "int64_t",
            "uint8_t",
            "uint16_t",
            "uint32_t",
            "uint64_t",
            "intptr_t",
            "uintptr_t",
            "bool",
            "true",
            "false",
            "NULL",
            "nullptr",
        }

        # Remove common C keywords and operators
        import re

        # Split by common delimiters and operators
        parts = re.split(r"[\[\]\(\)\{\}\s\*&,;]", type_str)

        # Extract potential type names that exist in available_types
        types = []
        for part in parts:
            part = part.strip()
            if part and len(part) > 1 and part not in primitive_types:
                # Check if it looks like a type name (starts with letter, contains letters/numbers/underscores)
                if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", part):
                    # Only include if it exists in available_types
                    if part in available_types:
                        types.append(part)

        return list(set(types))  # Remove duplicates

    def _find_c_files(
        self, source_folder_path: Path, recursive_search: bool
    ) -> List[Path]:
        """Find all C/C++ files in the source folder"""
        c_extensions = {".c", ".h", ".cpp", ".cc", ".cxx", ".hpp", ".hxx"}
        files = []

        self.logger.debug("Searching for files with extensions: %s", c_extensions)

        try:
            if recursive_search:
                for ext in c_extensions:
                    try:
                        files.extend(source_folder_path.rglob(f"*{ext}"))
                    except (OSError, PermissionError) as e:
                        self.logger.warning("Error during recursive search for %s files: %s", ext, e)
                        # Continue with other extensions
            else:
                for ext in c_extensions:
                    try:
                        files.extend(source_folder_path.glob(f"*{ext}"))
                    except (OSError, PermissionError) as e:
                        self.logger.warning("Error during search for %s files: %s", ext, e)
                        # Continue with other extensions
        except Exception as e:
            raise OSError(f"Failed to search for C/C++ files in '{source_folder_path}': {e}")

        # Filter out hidden files and common exclude patterns
        filtered_files = []
        exclude_patterns = {".git", "__pycache__", "node_modules", ".vscode", ".idea"}

        for file_path in files:
            try:
                # Skip hidden files and directories
                if any(part.startswith(".") for part in file_path.parts):
                    continue

                # Skip common exclude patterns
                if any(pattern in file_path.parts for pattern in exclude_patterns):
                    continue

                # Verify the file is actually accessible
                if not file_path.exists():
                    self.logger.debug("Skipping non-existent file: %s", file_path)
                    continue
                
                if not file_path.is_file():
                    self.logger.debug("Skipping non-file item: %s", file_path)
                    continue

                filtered_files.append(file_path)
            except (OSError, PermissionError) as e:
                self.logger.warning("Error accessing file %s: %s", file_path, e)
                # Skip files we can't access
                continue

        self.logger.debug("Found %d C/C++ files after filtering", len(filtered_files))
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
            if (
                token.line == target_token.line
                and token.column == target_token.column
                and token.value == target_token.value
            ):
                return i

        return None

    def _parse_single_typedef(self, tokens, start_pos):
        """Parse a single typedef starting at the given position"""
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

        # Check if it's a struct/enum/union typedef
        if tokens[pos].type in [TokenType.STRUCT, TokenType.ENUM, TokenType.UNION]:
            # Look ahead to see if this complex type is immediately followed by a function-pointer declarator
            # Pattern to detect: ... } ( * name ) ( ... )
            look = pos
            # Find the matching closing brace of the outer struct/union/enum
            if tokens[look].type in [TokenType.STRUCT, TokenType.ENUM, TokenType.UNION]:
                # Advance to the opening brace
                while look < len(tokens) and tokens[look].type != TokenType.LBRACE:
                    look += 1
                if look < len(tokens) and tokens[look].type == TokenType.LBRACE:
                    brace_count = 1
                    look += 1
                    while look < len(tokens) and brace_count > 0:
                        if tokens[look].type == TokenType.LBRACE:
                            brace_count += 1
                        elif tokens[look].type == TokenType.RBRACE:
                            brace_count -= 1
                        look += 1
                    # Now 'look' is token after the closing brace
                    j = look
                    # Skip whitespace/comments
                    while j < len(tokens) and tokens[j].type in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
                        j += 1
                    # Detect function-pointer declarator: ( * IDENT ) (
                    if (
                        j + 4 < len(tokens)
                        and tokens[j].type == TokenType.LPAREN
                        and tokens[j + 1].type == TokenType.ASTERISK
                        and tokens[j + 2].type == TokenType.IDENTIFIER
                        and tokens[j + 3].type == TokenType.RPAREN
                        and tokens[j + 4].type == TokenType.LPAREN
                    ):
                        typedef_name = tokens[j + 2].value
                        # Collect the full typedef original type up to the semicolon, preserving parentheses/brackets spacing
                        k = pos
                        formatted: list[str] = []
                        while k < len(tokens) and tokens[k].type != TokenType.SEMICOLON:
                            t = tokens[k]
                            if t.type in [TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACKET, TokenType.RBRACKET]:
                                formatted.append(t.value)
                            elif formatted and formatted[-1] not in ["(", ")", "[", "]"]:
                                # Prepend space before non-bracket tokens when previous isn't a bracket
                                formatted.append(" " + t.value)
                            else:
                                formatted.append(t.value)
                            k += 1
                        original_type = "".join(formatted)
                        # Clean excessive whitespace inside type
                        original_type = self._clean_type_string(original_type)
                        return (typedef_name, original_type)
            # Fallback to standard complex typedef parsing
            return self._parse_complex_typedef(tokens, pos)

        # Collect all non-whitespace/comment tokens until semicolon
        # But handle nested structures properly
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
                # For function pointer typedefs, we need to be outside the parameter list parentheses
                if brace_count == 0 and paren_count == 0:
                    # We're outside any nested structures and parentheses
                    break
            
            if token.type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                all_tokens.append(token)
            pos += 1

        if len(all_tokens) < 2:
            return None

        # Function pointer typedef: typedef ret (*name)(params);
        for i in range(len(all_tokens) - 3):
            if (
                all_tokens[i].type
                in [
                    TokenType.IDENTIFIER,
                    TokenType.INT,
                    TokenType.VOID,
                    TokenType.CHAR,
                    TokenType.FLOAT,
                    TokenType.DOUBLE,
                    TokenType.LONG,
                    TokenType.SHORT,
                    TokenType.UNSIGNED,
                    TokenType.SIGNED,
                ]
                and all_tokens[i + 1].type == TokenType.LPAREN
                and all_tokens[i + 2].type == TokenType.ASTERISK
                and all_tokens[i + 3].type == TokenType.IDENTIFIER
            ):
                # Check if this is followed by a parameter list
                if i + 4 < len(all_tokens) and all_tokens[i + 4].type == TokenType.RPAREN:
                    if i + 5 < len(all_tokens) and all_tokens[i + 5].type == TokenType.LPAREN:
                        # This is a function pointer with parameters - skip this pattern and use the complex logic
                        break
                
                # Simple function pointer typedef without complex parameters
                typedef_name = all_tokens[i + 3].value
                # Fix: Properly format function pointer type - preserve spaces between tokens but not around parentheses
                formatted_tokens = []
                for j, token in enumerate(all_tokens):
                    if token.type in [TokenType.LPAREN, TokenType.RPAREN]:
                        # Don't add spaces around parentheses
                        formatted_tokens.append(token.value)
                    elif j > 0 and all_tokens[j - 1].type not in [
                        TokenType.LPAREN,
                        TokenType.RPAREN,
                    ]:
                        # Add space before token if previous token wasn't a parenthesis
                        formatted_tokens.append(" " + token.value)
                    else:
                        # No space before token
                        formatted_tokens.append(token.value)
                original_type = "".join(formatted_tokens)
                return (typedef_name, original_type)

        # Complex function pointer typedef: typedef ret (*name)(complex_params);
        # This handles cases where the function pointer has complex parameters that span multiple tokens
        if len(all_tokens) >= 6:
            # Look for pattern: type ( * name ) ( ... )
            for i in range(len(all_tokens) - 5):
                if (
                    all_tokens[i].type
                    in [
                        TokenType.IDENTIFIER,
                        TokenType.INT,
                        TokenType.VOID,
                        TokenType.CHAR,
                        TokenType.FLOAT,
                        TokenType.DOUBLE,
                        TokenType.LONG,
                        TokenType.SHORT,
                        TokenType.UNSIGNED,
                        TokenType.SIGNED,
                    ]
                    and all_tokens[i + 1].type == TokenType.LPAREN
                    and all_tokens[i + 2].type == TokenType.ASTERISK
                    and all_tokens[i + 3].type == TokenType.IDENTIFIER
                    and all_tokens[i + 4].type == TokenType.RPAREN
                    and all_tokens[i + 5].type == TokenType.LPAREN
                ):
                    # Find the closing parenthesis for the parameter list
                    paren_count = 1
                    param_end = i + 6
                    while param_end < len(all_tokens) and paren_count > 0:
                        if all_tokens[param_end].type == TokenType.LPAREN:
                            paren_count += 1
                        elif all_tokens[param_end].type == TokenType.RPAREN:
                            paren_count -= 1
                        param_end += 1

                    if paren_count == 0:
                        typedef_name = all_tokens[i + 3].value
                        # Format the complete typedef properly
                        formatted_tokens = []
                        for j, token in enumerate(all_tokens):
                            if token.type in [TokenType.LPAREN, TokenType.RPAREN]:
                                # Don't add spaces around parentheses
                                formatted_tokens.append(token.value)
                            elif j > 0 and all_tokens[j - 1].type not in [
                                TokenType.LPAREN,
                                TokenType.RPAREN,
                            ]:
                                # Add space before token if previous token wasn't a parenthesis
                                formatted_tokens.append(" " + token.value)
                            else:
                                # No space before token
                                formatted_tokens.append(token.value)
                        original_type = "".join(formatted_tokens)
                        return (typedef_name, original_type)

        # Array typedef: typedef type name[size];
        for i in range(len(all_tokens)):
            if (
                all_tokens[i].type == TokenType.LBRACKET
                and i > 0
                and all_tokens[i - 1].type == TokenType.IDENTIFIER
            ):
                typedef_name = all_tokens[i - 1].value
                # Fix: Properly format array type - preserve spaces between tokens but not around brackets
                formatted_tokens = []
                for j, token in enumerate(all_tokens):
                    if token.type in [TokenType.LBRACKET, TokenType.RBRACKET]:
                        # Don't add spaces around brackets
                        formatted_tokens.append(token.value)
                    elif j > 0 and all_tokens[j - 1].type not in [
                        TokenType.LBRACKET,
                        TokenType.RBRACKET,
                    ]:
                        # Add space before token if previous token wasn't a bracket
                        formatted_tokens.append(" " + token.value)
                    else:
                        # No space before token
                        formatted_tokens.append(token.value)
                original_type = "".join(formatted_tokens)
                return (typedef_name, original_type)

        # Pointer typedef: typedef type * name;
        for i in range(len(all_tokens) - 2):
            if (
                all_tokens[i].type == TokenType.ASTERISK
                and all_tokens[i + 1].type == TokenType.IDENTIFIER
            ):
                typedef_name = all_tokens[i + 1].value
                # Fix: Properly format pointer type - preserve spaces between tokens
                formatted_tokens = []
                for j, token in enumerate(all_tokens):
                    if j > 0:
                        # Add space before token
                        formatted_tokens.append(" " + token.value)
                    else:
                        # No space before first token
                        formatted_tokens.append(token.value)
                original_type = "".join(formatted_tokens)
                return (typedef_name, original_type)

        # Basic typedef: the last token is the typedef name, everything else is the type
        typedef_name = all_tokens[-1].value
        type_tokens = all_tokens[:-1]
        original_type = " ".join(t.value for t in type_tokens)
        original_type = self._clean_type_string(original_type)
        original_type = self._fix_array_bracket_spacing(original_type)
        return (typedef_name, original_type)

    def _parse_complex_typedef(self, tokens, start_pos):
        """Parse complex typedef (struct/enum/union)"""
        # Parse complex typedefs with proper structure detection

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

    def _extract_tag_name_from_typedef(self, tokens, start_pos):
        """Extract the tag name from a typedef like 'typedef struct TagName { ... } TypedefName;'"""
        # Skip 'typedef' keyword
        pos = start_pos + 1

        # Skip whitespace and comments
        while pos < len(tokens) and tokens[pos].type in [
            TokenType.WHITESPACE,
            TokenType.COMMENT,
        ]:
            pos += 1

        if pos >= len(tokens):
            return ""

        # Check if it's a struct/enum/union
        if tokens[pos].type not in [TokenType.STRUCT, TokenType.ENUM, TokenType.UNION]:
            return ""

        # Skip struct/enum/union keyword
        pos += 1

        # Skip whitespace and comments
        while pos < len(tokens) and tokens[pos].type in [
            TokenType.WHITESPACE,
            TokenType.COMMENT,
        ]:
            pos += 1

        # Look for tag name (identifier before opening brace)
        if pos < len(tokens) and tokens[pos].type == TokenType.IDENTIFIER:
            tag_name = tokens[pos].value
            return tag_name

        return ""

    def _looks_like_function(self, tokens, start_pos):
        """Check if the token sequence starting at start_pos looks like a function"""
        # Look ahead for parentheses within a reasonable distance
        for i in range(start_pos, min(start_pos + 10, len(tokens))):
            if tokens[i].type == TokenType.LPAREN:
                return True
            if tokens[i].type in [
                TokenType.SEMICOLON,
                TokenType.LBRACE,
                TokenType.RBRACE,
            ]:
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
            elif (
                tokens[i].type == TokenType.SEMICOLON
                and paren_count == 0
                and brace_count == 0
            ):
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
        while start_idx < len(collected_tokens) and collected_tokens[
            start_idx
        ].type in [TokenType.STATIC, TokenType.EXTERN, TokenType.CONST]:
            start_idx += 1

        # Check if there's an assignment
        assign_idx = None
        for j in range(start_idx, len(collected_tokens)):
            if collected_tokens[j].type == TokenType.ASSIGN:
                assign_idx = j
                break

        # Extract variable name and type
        if assign_idx is not None:
            # Has assignment: type name = value or type name[size] = value
            if assign_idx > start_idx + 1:
                # Check if this is an array declaration with assignment
                bracket_idx = None
                for j in range(assign_idx - 1, start_idx, -1):
                    if collected_tokens[j].type == TokenType.RBRACKET:
                        bracket_idx = j
                        break
                
                if bracket_idx is not None:
                    # Array declaration with assignment: find the identifier before the first '['
                    # First, find the matching '[' for this last bracket
                    for j in range(bracket_idx - 1, start_idx, -1):
                        if collected_tokens[j].type == TokenType.LBRACKET:
                            # Found the first '[' of the trailing bracket groups; now find the identifier before it
                            for k in range(j - 1, start_idx, -1):
                                if collected_tokens[k].type == TokenType.IDENTIFIER:
                                    var_name = collected_tokens[k].value
                                    type_tokens = collected_tokens[start_idx:k]
                                    # Format base type preserving spaces
                                    formatted_type = []
                                    for idx, token in enumerate(type_tokens):
                                        if idx > 0:
                                            formatted_type.append(" " + token.value)
                                        else:
                                            formatted_type.append(token.value)
                                    base_type = "".join(formatted_type)
                                    # Collect all trailing [size] groups between name and '='
                                    dims = []
                                    idx = k + 1
                                    while idx + 2 < assign_idx and collected_tokens[idx].type == TokenType.LBRACKET and collected_tokens[idx + 2].type == TokenType.RBRACKET:
                                        size_val = collected_tokens[idx + 1].value
                                        # Normalize numeric sizes like 5U/6UL to 5/6
                                        import re as _re
                                        m = _re.match(r"\s*(\d+)", size_val)
                                        size_clean = m.group(1) if m else size_val
                                        dims.append(size_clean)
                                        idx += 3
                                    var_type = base_type + "".join(f"[{d}]" for d in dims)
                                    var_type = self._clean_type_string(var_type)
                                    value_tokens = collected_tokens[assign_idx + 1 :]
                                    var_value = " ".join(t.value for t in value_tokens)
                                    var_value = self._clean_value_string(var_value)
                                    return (var_name, var_type, var_value)
                            break
                else:
                    # Regular assignment: type name = value
                    var_name = collected_tokens[assign_idx - 1].value
                    type_tokens = collected_tokens[start_idx : assign_idx - 1]
                    value_tokens = collected_tokens[assign_idx + 1 :]
                    var_type = " ".join(t.value for t in type_tokens)
                    var_type = self._clean_type_string(var_type)
                    var_type = self._fix_array_bracket_spacing(var_type)
                    var_value = " ".join(t.value for t in value_tokens)
                    # Clean the value string to remove excessive whitespace and newlines
                    var_value = self._clean_value_string(var_value)
                    return (var_name, var_type, var_value)
        else:
            # No assignment: type name or type name[size][size]...
            if len(collected_tokens) > start_idx + 1:
                # Check if this is an array declaration
                bracket_idx = None
                for j in range(len(collected_tokens) - 1, start_idx, -1):
                    if collected_tokens[j].type == TokenType.RBRACKET:
                        bracket_idx = j
                        break

                if bracket_idx is not None:
                    # Array declaration: find the identifier before the first '[' and collect all dims
                    for j in range(bracket_idx - 1, start_idx, -1):
                        if collected_tokens[j].type == TokenType.LBRACKET:
                            # Found the first '[' of the trailing bracket groups; look for identifier before it
                            for k in range(j - 1, start_idx, -1):
                                if collected_tokens[k].type == TokenType.IDENTIFIER:
                                    var_name = collected_tokens[k].value
                                    type_tokens = collected_tokens[start_idx:k]
                                    # Format base type preserving spaces
                                    formatted_type = []
                                    for idx2, token in enumerate(type_tokens):
                                        if idx2 > 0:
                                            formatted_type.append(" " + token.value)
                                        else:
                                            formatted_type.append(token.value)
                                    base_type = "".join(formatted_type)
                                    # Collect all trailing [size] groups after the name
                                    dims = []
                                    idx2 = k + 1
                                    while idx2 + 2 < len(collected_tokens) and collected_tokens[idx2].type == TokenType.LBRACKET and collected_tokens[idx2 + 2].type == TokenType.RBRACKET:
                                        size_val = collected_tokens[idx2 + 1].value
                                        import re as _re
                                        m = _re.match(r"\s*(\d+)", size_val)
                                        size_clean = m.group(1) if m else size_val
                                        dims.append(size_clean)
                                        idx2 += 3
                                    var_type = base_type + "".join(f"[{d}]" for d in dims)
                                    var_type = self._clean_type_string(var_type)
                                    return (var_name, var_type, None)
                            break
                else:
                    # Regular variable: last token is the name
                    var_name = collected_tokens[-1].value
                    type_tokens = collected_tokens[start_idx:-1]
                    var_type = " ".join(t.value for t in type_tokens)
                    var_type = self._clean_type_string(var_type)
                    var_type = self._fix_array_bracket_spacing(var_type)
                    return (var_name, var_type, None)

        return None

    def _skip_to_semicolon(self, tokens, start_pos):
        """Skip to the next semicolon"""
        i = start_pos
        while i < len(tokens) and tokens[i].type != TokenType.SEMICOLON:
            i += 1
        return i + 1 if i < len(tokens) else i

    def _skip_preprocessor_directives(self, tokens, start_pos):
        """Skip preprocessor directives but keep their content for parsing"""
        # This method is deprecated - use the PreprocessorManager instead
        i = start_pos
        while i < len(tokens) and tokens[i].type == TokenType.PREPROCESSOR:
            # Skip the preprocessor directive itself
            i += 1
        return i

    def _parse_function_parameters(self, tokens, start_pos, end_pos, func_name):
        """Parse function parameters from token range"""

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
            if tokens[i].type not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
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
        """Parse a single function parameter from tokens"""
        from ..models import Field

        if not param_tokens:
            return None

        # Handle variadic parameters (three consecutive dots)
        if len(param_tokens) == 3 and all(t.value == "." for t in param_tokens):
            return Field(name="...", type="...")

        # Handle variadic parameters (single ... token)
        if len(param_tokens) == 1 and param_tokens[0].value == "...":
            return Field(name="...", type="...")

        # Handle function pointer parameters: type (*name)(params)
        if len(param_tokens) >= 5:
            # Look for pattern: type ( * name ) ( params )
            for i in range(len(param_tokens) - 4):
                if (
                    param_tokens[i].type == TokenType.LPAREN
                    and param_tokens[i + 1].type == TokenType.ASTERISK
                    and param_tokens[i + 2].type == TokenType.IDENTIFIER
                    and param_tokens[i + 3].type == TokenType.RPAREN
                    and param_tokens[i + 4].type == TokenType.LPAREN
                ):
                    # Found function pointer pattern
                    func_name = param_tokens[i + 2].value

                    # Find the closing parenthesis for the parameter list
                    paren_count = 1
                    param_end = i + 5
                    while param_end < len(param_tokens) and paren_count > 0:
                        if param_tokens[param_end].type == TokenType.LPAREN:
                            paren_count += 1
                        elif param_tokens[param_end].type == TokenType.RPAREN:
                            paren_count -= 1
                        param_end += 1

                    if paren_count == 0:
                        # Extract the type (everything before the function pointer)
                        type_tokens = param_tokens[:i]
                        param_type = " ".join(t.value for t in type_tokens)

                        # Extract the function pointer part
                        func_ptr_tokens = param_tokens[i:param_end]
                        func_ptr_type = " ".join(t.value for t in func_ptr_tokens)

                        # Combine type and function pointer
                        full_type = (param_type + " " + func_ptr_type).strip()
                        
                        # Fix array bracket spacing
                        full_type = self._fix_array_bracket_spacing(full_type)

                        return Field(name=func_name, type=full_type)
                    else:
                        # Incomplete function pointer - try to reconstruct
                        type_tokens = param_tokens[:i]
                        param_type = " ".join(t.value for t in type_tokens)
                        func_ptr_tokens = param_tokens[i:]
                        func_ptr_type = " ".join(t.value for t in func_ptr_tokens)
                        full_type = (param_type + " " + func_ptr_type).strip()
                        full_type = self._fix_array_bracket_spacing(full_type)
                        return Field(name=func_name, type=full_type)
            
            # Also look for pattern: type ( * name ) ( params ) with spaces
            for i in range(len(param_tokens) - 4):
                if (
                    param_tokens[i].type == TokenType.LPAREN
                    and param_tokens[i + 1].type == TokenType.ASTERISK
                    and param_tokens[i + 2].type == TokenType.IDENTIFIER
                    and param_tokens[i + 3].type == TokenType.RPAREN
                    and param_tokens[i + 4].type == TokenType.LPAREN
                ):
                    # Found function pointer pattern
                    func_name = param_tokens[i + 2].value

                    # Find the closing parenthesis for the parameter list
                    paren_count = 1
                    param_end = i + 5
                    while param_end < len(param_tokens) and paren_count > 0:
                        if param_tokens[param_end].type == TokenType.LPAREN:
                            paren_count += 1
                        elif param_tokens[param_end].type == TokenType.RPAREN:
                            paren_count -= 1
                        param_end += 1

                    if paren_count == 0:
                        # Extract the type (everything before the function pointer)
                        type_tokens = param_tokens[:i]
                        param_type = " ".join(t.value for t in type_tokens)

                        # Extract the function pointer part
                        func_ptr_tokens = param_tokens[i:param_end]
                        func_ptr_type = " ".join(t.value for t in func_ptr_tokens)

                        # Combine type and function pointer
                        full_type = (param_type + " " + func_ptr_type).strip()
                        
                        # Fix array bracket spacing
                        full_type = self._fix_array_bracket_spacing(full_type)

                        return Field(name=func_name, type=full_type)
                    else:
                        # Incomplete function pointer - try to reconstruct
                        type_tokens = param_tokens[:i]
                        param_type = " ".join(t.value for t in type_tokens)
                        func_ptr_tokens = param_tokens[i:]
                        func_ptr_type = " ".join(t.value for t in func_ptr_tokens)
                        full_type = (param_type + " " + func_ptr_type).strip()
                        full_type = self._fix_array_bracket_spacing(full_type)
                        return Field(name=func_name, type=full_type)

                    # For parameters like "int x" or "const char *name" or "char* argv[]"
        if len(param_tokens) >= 2:
            # Check if the last token is a closing bracket (array parameter)
            if param_tokens[-1].type == TokenType.RBRACKET:
                # Find the opening bracket to get the array size
                bracket_start = None
                for i in range(len(param_tokens) - 1, -1, -1):
                    if param_tokens[i].type == TokenType.LBRACKET:
                        bracket_start = i
                        break
                
                if bracket_start is not None:
                    # Extract the parameter name (last identifier before the opening bracket)
                    param_name = None
                    for i in range(bracket_start - 1, -1, -1):
                        if param_tokens[i].type == TokenType.IDENTIFIER:
                            param_name = param_tokens[i].value
                            break
                    
                    if param_name:
                        # Extract the type (everything before the parameter name)
                        type_tokens = param_tokens[:i]
                        param_type = " ".join(t.value for t in type_tokens)
                        
                        # Add the array brackets to the type
                        array_size = ""
                        if bracket_start + 1 < len(param_tokens) - 1:
                            # There's content between brackets
                            array_content = param_tokens[bracket_start + 1:-1]
                            array_size = " ".join(t.value for t in array_content)
                        
                        param_type = param_type + "[" + array_size + "]"
                        
                        # Fix array bracket spacing
                        param_type = self._fix_array_bracket_spacing(param_type)
                        
                        return Field(name=param_name, type=param_type)
            else:
                # Regular parameter: last token is the parameter name
                param_name = param_tokens[-1].value
                type_tokens = param_tokens[:-1]
                param_type = " ".join(t.value for t in type_tokens)
                
                # Fix array bracket spacing and pointer spacing
                param_type = self._fix_array_bracket_spacing(param_type)
                param_type = self._fix_pointer_spacing(param_type)

            # Handle unnamed parameters (just type)
            if param_name in [
                "void",
                "int",
                "char",
                "float",
                "double",
                "long",
                "short",
                "unsigned",
                "signed",
            ]:
                # This is just a type without a name
                return Field(name="unnamed", type=param_type + " " + param_name)

            # Additional validation before creating Field
            if param_name and param_name.strip() and param_type and param_type.strip():
                return Field(name=param_name.strip(), type=param_type.strip())
            else:
                # Fallback for invalid parameters - try to reconstruct the full parameter
                full_param = " ".join(t.value for t in param_tokens)
                full_param = self._fix_array_bracket_spacing(full_param)
                if full_param.strip():
                    return Field(name="unnamed", type=full_param.strip())
                else:
                    return Field(name="unnamed", type="unknown")
        elif len(param_tokens) == 1:
            # Single token - might be just type (like "void") or name
            token_value = param_tokens[0].value
            if token_value in [
                "void",
                "int",
                "char",
                "float",
                "double",
                "long",
                "short",
                "unsigned",
                "signed",
            ]:
                return Field(name="unnamed", type=token_value)
            else:
                # If we can't determine the type, use the token value as type
                if token_value and token_value.strip():
                    return Field(name="unnamed", type=token_value.strip())
                else:
                    return Field(name="unnamed", type="unknown")

        return None

    def _fix_array_bracket_spacing(self, type_str: str) -> str:
        """Fix spacing around array brackets in type strings"""
        # First clean the type string to remove newlines
        type_str = self._clean_type_string(type_str)
        # Replace patterns like "type[ size ]" with "type[size]"
        import re
        # Remove spaces around array brackets
        type_str = re.sub(r'\s*\[\s*', '[', type_str)
        type_str = re.sub(r'\s*\]\s*', ']', type_str)
        return type_str

    def _fix_pointer_spacing(self, type_str: str) -> str:
        """Fix spacing around pointer asterisks in type strings"""
        import re
        # Fix double pointer spacing: "type * *" -> "type **"
        type_str = re.sub(r'\*\s+\*', '**', type_str)
        # Fix triple pointer spacing: "type * * *" -> "type ***"
        type_str = re.sub(r'\*\s+\*\s+\*', '***', type_str)
        return type_str

    def _clean_type_string(self, type_str: str) -> str:
        """Clean type string by removing newlines and normalizing whitespace"""
        if not type_str:
            return type_str
        # Replace newlines with spaces and normalize whitespace
        cleaned = type_str.replace('\n', ' ')
        # Normalize multiple spaces to single space
        import re
        cleaned = re.sub(r'\s+', ' ', cleaned)
        # Strip leading/trailing whitespace
        cleaned = cleaned.strip()
        return cleaned

    def _clean_value_string(self, value_str: str) -> str:
        """Clean value string by removing excessive whitespace and newlines"""
        if not value_str:
            return value_str
        # Replace newlines with spaces and normalize whitespace
        cleaned = value_str.replace('\n', ' ')
        # Normalize multiple spaces to single space
        import re
        cleaned = re.sub(r'\s+', ' ', cleaned)
        # Strip leading/trailing whitespace
        cleaned = cleaned.strip()
        # Remove excessive spaces around braces and operators
        cleaned = re.sub(r'\s*{\s*', '{', cleaned)
        cleaned = re.sub(r'\s*}\s*', '}', cleaned)
        cleaned = re.sub(r'\s*,\s*', ', ', cleaned)
        cleaned = re.sub(r'\s*&\s*', '&', cleaned)
        return cleaned

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
        self,
        source_folders: "List[str]",
        output_file: str = "model.json",
        recursive_search: bool = True,
        config: "Config" = None,
    ) -> str:
        """Parse C/C++ projects and generate model.json

        Args:
            source_folders: List of source folder directories within the project
            output_file: Path to the output model.json file
            recursive_search: Whether to search subdirectories recursively
            config: Configuration object for filtering and processing

        Returns:
            Path to the generated model.json file
        """
        # Enhanced validation for source_folders
        if not isinstance(source_folders, list):
            raise TypeError(f"source_folders must be a list of strings, got: {type(source_folders)}")

        if not source_folders:
            raise ValueError("At least one source folder must be provided")

        # Validate all items are strings and not empty
        for i, folder in enumerate(source_folders):
            if not isinstance(folder, str):
                raise TypeError(f"All source folders must be strings, got {type(folder)} at index {i}: {folder}")
            if not folder.strip():
                raise ValueError(f"Source folder at index {i} cannot be empty or whitespace: {repr(folder)}")

        self.logger.info(
            f"Step 1: Parsing C/C++ project with {len(source_folders)} source folders"
        )

        # Get project name from config or use default
        project_name = (
            getattr(config, "project_name", "C_Project") if config else "C_Project"
        )

        # Parse each source folder and combine results
        all_files = {}
        total_structs = 0
        total_enums = 0
        total_functions = 0
        failed_folders = []

        for i, source_folder in enumerate(source_folders):
            self.logger.info(
                f"Parsing source folder {i+1}/{len(source_folders)}: {source_folder}"
            )

            try:
                # Parse the individual source folder
                model = self.c_parser.parse_project(
                    source_folder, recursive_search, config
                )

                all_files.update(model.files)

                # Update totals
                total_structs += sum(len(f.structs) for f in model.files.values())
                total_enums += sum(len(f.enums) for f in model.files.values())
                total_functions += sum(len(f.functions) for f in model.files.values())

                self.logger.info(
                    f"Successfully parsed source folder {source_folder}: {len(model.files)} files"
                )

            except Exception as e:
                self.logger.error(
                    "Failed to parse source folder %s: %s", source_folder, e
                )
                failed_folders.append((source_folder, str(e)))
                
                # If this is the only source folder, re-raise the error
                if len(source_folders) == 1:
                    raise
                
                # For multiple source folders, continue with others but log the failure
                self.logger.warning(
                    "Continuing with other source folders despite failure in %s", source_folder
                )

        # If all source folders failed, raise an error
        if failed_folders and len(failed_folders) == len(source_folders):
            error_msg = "All source folders failed to parse:\n"
            for folder, error in failed_folders:
                error_msg += f"  - {folder}: {error}\n"
            raise RuntimeError(error_msg)

        # If some folders failed, log a warning
        if failed_folders:
            self.logger.warning(
                f"Failed to parse {len(failed_folders)} out of {len(source_folders)} source folders"
            )

        # Create combined project model
        combined_model = ProjectModel(
            project_name=project_name,
            source_folder=(
                ",".join(source_folders)
                if len(source_folders) > 1
                else source_folders[0]
            ),
            files=all_files,
        )

        # Update all uses fields across the entire combined project
        combined_model.update_uses_fields()

        # Save combined model to JSON file
        try:
            combined_model.save(output_file)
        except Exception as e:
            raise RuntimeError(f"Failed to save model to {output_file}: {e}") from e

        # Step 1.5: Verify model sanity
        self.logger.info("Step 1.5: Verifying model sanity...")
        from .verifier import ModelVerifier

        verifier = ModelVerifier()
        is_valid, issues = verifier.verify_model(combined_model)

        if not is_valid:
            self.logger.warning(
                f"Model verification found {len(issues)} issues - model may contain parsing errors"
            )
            # Continue processing but warn about potential issues
        else:
            self.logger.info("Model verification passed - all values look sane")

        self.logger.info("Step 1 complete! Model saved to: %s", output_file)
        self.logger.info(
            f"Found {len(all_files)} total files across {len(source_folders)} source folder(s)"
        )

        # Print summary
        self.logger.info(
            f"Summary: {total_structs} structs, {total_enums} enums, "
            f"{total_functions} functions"
        )

        return output_file
