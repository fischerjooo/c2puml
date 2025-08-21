#!/usr/bin/env python3
"""
Tokenizer module for C to PlantUML converter - Helper library for tokenizing C/C++ code
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


class TokenType(Enum):
    """Token types for C/C++ lexical analysis"""

    # Keywords
    STRUCT = "STRUCT"
    ENUM = "ENUM"
    UNION = "UNION"
    TYPEDEF = "TYPEDEF"
    STATIC = "STATIC"
    EXTERN = "EXTERN"
    INLINE = "INLINE"
    LOCAL_INLINE = "LOCAL_INLINE"
    CONST = "CONST"
    VOID = "VOID"

    # Data types
    CHAR = "CHAR"
    INT = "INT"
    FLOAT = "FLOAT"
    DOUBLE = "DOUBLE"
    LONG = "LONG"
    SHORT = "SHORT"
    UNSIGNED = "UNSIGNED"
    SIGNED = "SIGNED"

    # Operators and punctuation
    LBRACE = "LBRACE"  # {
    RBRACE = "RBRACE"  # }
    LPAREN = "LPAREN"  # (
    RPAREN = "RPAREN"  # )
    LBRACKET = "LBRACKET"  # [
    RBRACKET = "RBRACKET"  # ]
    SEMICOLON = "SEMICOLON"  # ;
    COMMA = "COMMA"  # ,
    ASSIGN = "ASSIGN"  # =
    ASTERISK = "ASTERISK"  # *
    AMPERSAND = "AMPERSAND"  # &
    ARROW = "ARROW"  # ->

    # Literals and identifiers
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    CHAR_LITERAL = "CHAR_LITERAL"

    # Preprocessor
    INCLUDE = "INCLUDE"
    DEFINE = "DEFINE"
    PREPROCESSOR = "PREPROCESSOR"

    # Special
    COMMENT = "COMMENT"
    WHITESPACE = "WHITESPACE"
    NEWLINE = "NEWLINE"
    EOF = "EOF"
    UNKNOWN = "UNKNOWN"


@dataclass
class Token:
    """Represents a single token in C/C++ code"""

    type: TokenType
    value: str
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, '{self.value}', {self.line}:{self.column})"


class CTokenizer:
    """Tokenizer for C/C++ source code"""

    # Keywords mapping
    KEYWORDS = {
        "struct": TokenType.STRUCT,
        "enum": TokenType.ENUM,
        "union": TokenType.UNION,
        "typedef": TokenType.TYPEDEF,
        "static": TokenType.STATIC,
        "extern": TokenType.EXTERN,
        "inline": TokenType.INLINE,
        "local_inline": TokenType.LOCAL_INLINE,
        "const": TokenType.CONST,
        "void": TokenType.VOID,
        "char": TokenType.CHAR,
        "int": TokenType.INT,
        "float": TokenType.FLOAT,
        "double": TokenType.DOUBLE,
        "long": TokenType.LONG,
        "short": TokenType.SHORT,
        "unsigned": TokenType.UNSIGNED,
        "signed": TokenType.SIGNED,
    }

    # Single character tokens
    SINGLE_CHAR_TOKENS = {
        "{": TokenType.LBRACE,
        "}": TokenType.RBRACE,
        "(": TokenType.LPAREN,
        ")": TokenType.RPAREN,
        "[": TokenType.LBRACKET,
        "]": TokenType.RBRACKET,
        ";": TokenType.SEMICOLON,
        ",": TokenType.COMMA,
        "=": TokenType.ASSIGN,
        "*": TokenType.ASTERISK,
        "&": TokenType.AMPERSAND,
    }

    # Two character tokens
    TWO_CHAR_TOKENS = {
        "->": TokenType.ARROW,
    }

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Compiled regex patterns for efficiency
        self.patterns = {
            "identifier": re.compile(r"[a-zA-Z_][a-zA-Z0-9_]*"),
            "number": re.compile(
                r"0[xX][0-9a-fA-F]+[uUlL]*|0[bB][01]+[uUlL]*|0[0-7]+[uUlL]*|"
                r"\d+\.\d*([eE][+-]?\d+)?[fFlL]*|\d+([eE][+-]?\d+)?[fFlL]*|\d+[uUlL]*"
            ),
            "string": re.compile(r'"([^"\\]|\\.)*"'),
            "char": re.compile(r"'([^'\\]|\\.)'"),
            "comment_single": re.compile(r"//.*"),
            "comment_multi": re.compile(r"/\*.*?\*/", re.DOTALL),
            "preprocessor": re.compile(
                r"#(include|define|ifdef|ifndef|if|endif|elif|else|pragma|error|warning)\b.*"
            ),
            "whitespace": re.compile(r"[ \t]+"),
            "newline": re.compile(r"\n"),
        }

    def tokenize(self, content: str) -> List[Token]:
        """Tokenize C/C++ source code content"""
        tokens = []
        lines = content.splitlines()
        total_lines = len(lines)
        line_num = 1
        in_multiline_string = False
        multiline_string_value = ""
        multiline_string_start_line = 0
        multiline_string_start_col = 0
        in_multiline_comment = False
        multiline_comment_value = ""
        multiline_comment_start_line = 0
        multiline_comment_start_col = 0

        for idx, line in enumerate(lines):
            if in_multiline_string:
                multiline_string_value += "\n" + line
                if '"' in line:
                    # End of multiline string
                    in_multiline_string = False
                    tokens.append(
                        Token(
                            TokenType.STRING,
                            multiline_string_value,
                            multiline_string_start_line,
                            multiline_string_start_col,
                        )
                    )
            elif in_multiline_comment:
                # Continue multi-line comment
                multiline_comment_value += "\n" + line
                comment_end = line.find("*/")
                if comment_end != -1:
                    # End of multi-line comment
                    in_multiline_comment = False
                    multiline_comment_value = multiline_comment_value[
                        : multiline_comment_value.rfind("*/") + 2
                    ]
                    tokens.append(
                        Token(
                            TokenType.COMMENT,
                            multiline_comment_value,
                            multiline_comment_start_line,
                            multiline_comment_start_col,
                        )
                    )
            else:
                line_tokens = self._tokenize_line(line, line_num)
                # Check if a string starts but does not end on this line
                if (
                    line_tokens
                    and line_tokens[-1].type == TokenType.STRING
                    and not line_tokens[-1].value.endswith('"')
                ):
                    in_multiline_string = True
                    multiline_string_value = line_tokens[-1].value
                    multiline_string_start_line = line_tokens[-1].line
                    multiline_string_start_col = line_tokens[-1].column
                    tokens.extend(line_tokens[:-1])
                # Check if a multi-line comment starts but does not end on this line
                elif (
                    line_tokens
                    and line_tokens[-1].type == TokenType.COMMENT
                    and line_tokens[-1].value.startswith("/*")
                    and not line_tokens[-1].value.endswith("*/")
                ):
                    in_multiline_comment = True
                    multiline_comment_value = line_tokens[-1].value
                    multiline_comment_start_line = line_tokens[-1].line
                    multiline_comment_start_col = line_tokens[-1].column
                    tokens.extend(line_tokens[:-1])
                else:
                    tokens.extend(line_tokens)

            if line_num < total_lines:
                tokens.append(Token(TokenType.NEWLINE, "\n", line_num, len(line)))
            line_num += 1

        if in_multiline_string:
            tokens.append(
                Token(
                    TokenType.STRING,
                    multiline_string_value,
                    multiline_string_start_line,
                    multiline_string_start_col,
                )
            )
        if in_multiline_comment:
            tokens.append(
                Token(
                    TokenType.COMMENT,
                    multiline_comment_value,
                    multiline_comment_start_line,
                    multiline_comment_start_col,
                )
            )

        # Post-process tokens to merge multi-line macros
        tokens = self._merge_multiline_macros(tokens, lines)

        tokens.append(
            Token(TokenType.EOF, "", total_lines, len(lines[-1]) if lines else 0)
        )

        return tokens

    def _tokenize_line(self, line: str, line_num: int) -> List[Token]:
        """Tokenize a single line of code"""
        tokens = []
        pos = 0

        while pos < len(line):
            # Skip whitespace but track it
            if match := self.patterns["whitespace"].match(line, pos):
                tokens.append(Token(TokenType.WHITESPACE, match.group(), line_num, pos))
                pos = match.end()
                continue

            # Comments
            if match := self.patterns["comment_single"].match(line, pos):
                tokens.append(Token(TokenType.COMMENT, match.group(), line_num, pos))
                pos = len(line)  # Rest of line is comment
                continue

            # Multi-line comments - check for /* at start of line or after whitespace
            if line[pos:].startswith("/*"):
                # Find the end of the comment
                comment_end = line.find("*/", pos)
                if comment_end != -1:
                    # Comment ends on this line
                    comment_text = line[pos : comment_end + 2]
                    tokens.append(Token(TokenType.COMMENT, comment_text, line_num, pos))
                    pos = comment_end + 2
                    continue
                else:
                    # Comment continues to next line - create a partial comment token
                    comment_text = line[pos:]
                    tokens.append(Token(TokenType.COMMENT, comment_text, line_num, pos))
                    pos = len(line)
                    continue

            # Preprocessor directives
            if match := self.patterns["preprocessor"].match(line, pos):
                value = match.group()
                if value.startswith("#include"):
                    tokens.append(Token(TokenType.INCLUDE, value, line_num, pos))
                elif value.startswith("#define"):
                    tokens.append(Token(TokenType.DEFINE, value, line_num, pos))
                else:
                    tokens.append(Token(TokenType.PREPROCESSOR, value, line_num, pos))
                pos = len(line)  # Rest of line is preprocessor
                continue

            # String literals
            if (
                line[pos] == '"'
                or (
                    pos > 0
                    and line[pos - 1] in ["L", "u", "U", "R"]
                    and line[pos] == '"'
                )
                or (pos > 1 and line[pos - 2 : pos] == "u8" and line[pos] == '"')
            ):
                # Handle string literals with possible prefixes
                string_start = pos
                if line[pos - 2 : pos] == "u8":
                    string_start -= 2
                elif line[pos - 1] in ["L", "u", "U", "R"]:
                    string_start -= 1
                pos += 1  # Skip opening quote
                while pos < len(line):
                    if line[pos] == '"':
                        # Found closing quote
                        string_text = line[string_start : pos + 1]
                        tokens.append(
                            Token(TokenType.STRING, string_text, line_num, string_start)
                        )
                        pos += 1
                        break
                    elif line[pos] == "\\":
                        pos += 2
                    else:
                        pos += 1
                else:
                    string_text = line[string_start:]
                    tokens.append(
                        Token(TokenType.STRING, string_text, line_num, string_start)
                    )
                    pos = len(line)
                continue

            # Character literals
            if match := self.patterns["char"].match(line, pos):
                tokens.append(
                    Token(TokenType.CHAR_LITERAL, match.group(), line_num, pos)
                )
                pos = match.end()
                continue

            # Numbers
            if match := self.patterns["number"].match(line, pos):
                tokens.append(Token(TokenType.NUMBER, match.group(), line_num, pos))
                pos = match.end()
                continue

            # Single character tokens
            if line[pos] in self.SINGLE_CHAR_TOKENS:
                token_type = self.SINGLE_CHAR_TOKENS[line[pos]]
                tokens.append(Token(token_type, line[pos], line_num, pos))
                pos += 1
                continue

            # Multi-character operators (<<, >>, ->)
            if line[pos : pos + 2] in ["<<", ">>", "->"]:
                op = line[pos : pos + 2]
                if op == "->":
                    tokens.append(Token(TokenType.ARROW, op, line_num, pos))
                else:
                    tokens.append(
                        Token(
                            (
                                TokenType.OPERATOR
                                if hasattr(TokenType, "OPERATOR")
                                else TokenType.UNKNOWN
                            ),
                            op,
                            line_num,
                            pos,
                        )
                    )
                pos += 2
                continue

            # Identifiers and keywords
            if match := self.patterns["identifier"].match(line, pos):
                value = match.group()
                token_type = self.KEYWORDS.get(value.lower(), TokenType.IDENTIFIER)
                tokens.append(Token(token_type, value, line_num, pos))
                pos = match.end()
                continue

            # Unknown character (always one at a time)
            tokens.append(Token(TokenType.UNKNOWN, line[pos], line_num, pos))
            pos += 1

        return tokens

    def filter_tokens(
        self, tokens: List[Token], exclude_types: Optional[List[TokenType]] = None
    ) -> List[Token]:
        """Filter tokens by type"""
        if exclude_types is None:
            exclude_types = [
                TokenType.WHITESPACE,
                TokenType.COMMENT,
                TokenType.NEWLINE,
                TokenType.EOF,
            ]

        return [token for token in tokens if token.type not in exclude_types]

    def _merge_multiline_macros(
        self, tokens: List[Token], lines: List[str]
    ) -> List[Token]:
        """Merge multi-line macro tokens that span multiple lines with backslashes"""
        merged_tokens = []
        i = 0

        while i < len(tokens):
            token = tokens[i]

            if token.type == TokenType.DEFINE and token.value.rstrip().endswith("\\"):
                # Found a multi-line macro, merge with subsequent lines
                macro_content = token.value
                current_line = token.line

                # Continue merging lines until we find one that doesn't end with backslash
                while macro_content.rstrip().endswith("\\"):
                    # Remove the backslash and add a newline
                    macro_content = macro_content.rstrip()[:-1] + "\n"
                    current_line += 1

                    # Find the next line content
                    if current_line <= len(lines):
                        next_line = lines[current_line - 1]
                        macro_content += next_line
                    else:
                        break

                # Create a new token with the merged content
                merged_tokens.append(
                    Token(TokenType.DEFINE, macro_content, token.line, token.column)
                )
            else:
                merged_tokens.append(token)

            i += 1

        return merged_tokens


class StructureFinder:
    """Helper class to find C/C++ structures in token streams"""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.logger = logging.getLogger(__name__)

    def find_structs(self) -> List[Tuple[int, int, str]]:
        """Find struct definitions in token stream

        Returns:
            List of tuples (start_pos, end_pos, struct_name)
        """
        structs = []
        self.pos = 0

        while self.pos < len(self.tokens):
            if self._current_token_is(TokenType.STRUCT):
                struct_info = self._parse_struct()
                if struct_info:
                    structs.append(struct_info)
            elif self._current_token_is(TokenType.TYPEDEF):
                typedef_struct = self._parse_typedef_struct()
                if typedef_struct:
                    structs.append(typedef_struct)
            else:
                self.pos += 1

        return structs

    def find_enums(self) -> List[Tuple[int, int, str]]:
        """Find enum definitions in token stream"""
        enums = []
        self.pos = 0

        while self.pos < len(self.tokens):
            if self._current_token_is(TokenType.ENUM):
                enum_info = self._parse_enum()
                if enum_info:
                    enums.append(enum_info)
            elif self._current_token_is(TokenType.TYPEDEF):
                typedef_enum = self._parse_typedef_enum()
                if typedef_enum:
                    enums.append(typedef_enum)
            else:
                self.pos += 1

        return enums

    def find_functions(self) -> List[Tuple[int, int, str, str, bool, bool]]:
        """Find all function declarations and definitions in the token stream

        Returns:
            List of tuples (start_pos, end_pos, func_name, return_type, is_declaration, is_inline)
        """
        functions = []
        self.pos = 0

        while self.pos < len(self.tokens):
            result = self._parse_function()
            if result:
                functions.append(result)

        return functions

    def find_unions(self) -> List[Tuple[int, int, str]]:
        """Find union definitions in token stream"""
        unions = []
        self.pos = 0

        while self.pos < len(self.tokens):
            if self._current_token_is(TokenType.UNION):
                union_info = self._parse_union()
                if union_info:
                    unions.append(union_info)
            elif self._current_token_is(TokenType.TYPEDEF):
                typedef_union = self._parse_typedef_union()
                if typedef_union:
                    unions.append(typedef_union)
            else:
                self.pos += 1

        return unions

    def _current_token_is(self, token_type: TokenType) -> bool:
        """Check if current token is of specified type"""
        return self.pos < len(self.tokens) and self.tokens[self.pos].type == token_type

    def _peek_token(self, offset: int = 1) -> Optional[Token]:
        """Peek at token at current position + offset"""
        peek_pos = self.pos + offset
        return self.tokens[peek_pos] if peek_pos < len(self.tokens) else None

    def _advance(self) -> Optional[Token]:
        """Advance to next token and return current"""
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        return None

    def _find_matching_brace(self, start_pos: int) -> Optional[int]:
        """Find matching closing brace starting from open brace position"""
        if (
            start_pos >= len(self.tokens)
            or self.tokens[start_pos].type != TokenType.LBRACE
        ):
            return None

        depth = 1
        pos = start_pos + 1

        while pos < len(self.tokens) and depth > 0:
            if self.tokens[pos].type == TokenType.LBRACE:
                depth += 1
            elif self.tokens[pos].type == TokenType.RBRACE:
                depth -= 1
            pos += 1

        return pos - 1 if depth == 0 else None

    def _parse_struct(self) -> Optional[Tuple[int, int, str]]:
        """Parse struct definition starting at current position"""
        start_pos = self.pos

        # Consume 'struct' keyword
        if not self._current_token_is(TokenType.STRUCT):
            return None
        self._advance()

        # Check if this struct is inside a cast expression by looking backwards
        check_pos = start_pos - 1
        while check_pos >= 0:
            if self.tokens[check_pos].type == TokenType.LPAREN:
                # Found opening parenthesis before struct - this is likely a cast expression
                return None
            elif self.tokens[check_pos].type in [TokenType.STRUCT, TokenType.TYPEDEF]:
                # Found another struct or typedef - this is not a cast expression
                break
            elif self.tokens[check_pos].type not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
                # Found some other token - this is not a cast expression
                break
            check_pos -= 1

        # Skip whitespace
        while self.pos < len(self.tokens) and self._current_token_is(
            TokenType.WHITESPACE
        ):
            self.pos += 1

        # Check if this is a cast expression: (struct type*)
        if self._current_token_is(TokenType.LPAREN):
            # Look ahead to see if this is a cast expression
            check_pos = self.pos + 1
            while check_pos < len(self.tokens):
                if self.tokens[check_pos].type == TokenType.RPAREN:
                    # Found closing parenthesis - this is likely a cast expression
                    return None
                elif self.tokens[check_pos].type == TokenType.LBRACE:
                    # Found opening brace - this is a struct definition
                    break
                elif self.tokens[check_pos].type == TokenType.SEMICOLON:
                    # Found semicolon - this is a variable declaration
                    return None
                check_pos += 1

        # Get struct tag name (optional for anonymous structs)
        struct_tag = ""
        if self._current_token_is(TokenType.IDENTIFIER):
            struct_tag = self._advance().value

        # Look for opening brace or semicolon
        while self.pos < len(self.tokens):
            if self._current_token_is(TokenType.LBRACE):
                # Found opening brace - this is a struct definition
                break
            elif self._current_token_is(TokenType.SEMICOLON):
                # Found semicolon before opening brace - this is a variable declaration
                return None
            self.pos += 1

        if not self._current_token_is(TokenType.LBRACE):
            # This is a variable declaration
            return None

        # Find matching closing brace
        brace_pos = self.pos
        end_brace_pos = self._find_matching_brace(brace_pos)

        if end_brace_pos is None:
            return None

        # Look for struct name after closing brace
        name_pos = end_brace_pos + 1
        struct_name = struct_tag  # Default to tag name

        # Check if this is a typedef struct by looking backwards
        is_typedef = False
        check_pos = start_pos - 1
        while check_pos >= 0:
            if self.tokens[check_pos].type == TokenType.TYPEDEF:
                is_typedef = True
                break
            elif self.tokens[check_pos].type in [
                TokenType.STRUCT,
                TokenType.LBRACE,
                TokenType.RBRACE,
            ]:
                break
            check_pos -= 1

        if is_typedef:
            # For typedef struct, look for the typedef name after the closing brace
            while name_pos < len(self.tokens):
                if self.tokens[name_pos].type == TokenType.IDENTIFIER:
                    struct_name = self.tokens[name_pos].value
                    break
                elif self.tokens[name_pos].type == TokenType.SEMICOLON:
                    break
                name_pos += 1
        else:
            # Check if there's a variable name after the brace
            while name_pos < len(self.tokens):
                if self.tokens[name_pos].type == TokenType.IDENTIFIER:
                    # This is a variable name
                    struct_name = ""
                    break
                elif self.tokens[name_pos].type == TokenType.SEMICOLON:
                    break
                name_pos += 1

        # Find semicolon (for struct definitions)
        self.pos = end_brace_pos + 1
        while self.pos < len(self.tokens) and not self._current_token_is(
            TokenType.SEMICOLON
        ):
            self.pos += 1

        end_pos = self.pos
        return (start_pos, end_pos, struct_name)

    def _parse_typedef_struct(self) -> Optional[Tuple[int, int, str]]:
        """Parse typedef struct definition"""
        start_pos = self.pos

        # Consume 'typedef'
        if not self._current_token_is(TokenType.TYPEDEF):
            return None
        self._advance()

        # Look for 'struct'
        if not self._current_token_is(TokenType.STRUCT):
            # Not a typedef struct, reset position
            self.pos = start_pos + 1
            return None

        # Skip 'struct'
        self._advance()

        # Skip whitespace
        while self.pos < len(self.tokens) and self._current_token_is(
            TokenType.WHITESPACE
        ):
            self.pos += 1

        # Get struct tag name (optional)
        struct_tag = ""
        if self._current_token_is(TokenType.IDENTIFIER):
            struct_tag = self._advance().value

        # Skip whitespace
        while self.pos < len(self.tokens) and self._current_token_is(
            TokenType.WHITESPACE
        ):
            self.pos += 1

        # Check if this is a forward declaration (no braces)
        if not self._current_token_is(TokenType.LBRACE):
            # This is a forward declaration, skip it
            self.pos = start_pos + 1
            return None

        # Find matching closing brace
        end_brace_pos = self._find_matching_brace(self.pos)
        if end_brace_pos is None:
            self.pos = start_pos + 1
            return None

        # Look for typedef name after closing brace
        typedef_name = ""
        name_pos = end_brace_pos + 1
        while name_pos < len(self.tokens):
            if self.tokens[name_pos].type == TokenType.IDENTIFIER:
                typedef_name = self.tokens[name_pos].value
                break
            elif self.tokens[name_pos].type == TokenType.SEMICOLON:
                break
            name_pos += 1

        # Find semicolon
        while (
            name_pos < len(self.tokens)
            and not self.tokens[name_pos].type == TokenType.SEMICOLON
        ):
            name_pos += 1

        end_pos = name_pos
        return (start_pos, end_pos, typedef_name)

    def _parse_enum(self) -> Optional[Tuple[int, int, str]]:
        """Parse enum definition starting at current position"""
        start_pos = self.pos

        # Consume 'enum' keyword
        if not self._current_token_is(TokenType.ENUM):
            return None
        self._advance()

        # Skip whitespace
        while self.pos < len(self.tokens) and self._current_token_is(
            TokenType.WHITESPACE
        ):
            self.pos += 1

        # Get enum tag name (optional for anonymous enums)
        enum_tag = ""
        if self._current_token_is(TokenType.IDENTIFIER):
            enum_tag = self._advance().value

        # Find opening brace
        while self.pos < len(self.tokens) and not self._current_token_is(
            TokenType.LBRACE
        ):
            self.pos += 1

        if not self._current_token_is(TokenType.LBRACE):
            return None

        # Find matching closing brace
        brace_pos = self.pos
        end_brace_pos = self._find_matching_brace(brace_pos)

        if end_brace_pos is None:
            return None

        # Look for enum name after closing brace
        name_pos = end_brace_pos + 1
        enum_name = enum_tag  # Default to tag name

        # Check if this is a typedef enum by looking backwards
        is_typedef = False
        check_pos = start_pos - 1
        while check_pos >= 0:
            if self.tokens[check_pos].type == TokenType.TYPEDEF:
                is_typedef = True
                break
            elif self.tokens[check_pos].type in [
                TokenType.ENUM,
                TokenType.LBRACE,
                TokenType.RBRACE,
            ]:
                break
            check_pos -= 1

        if is_typedef:
            # For typedef enum, look for the typedef name after the closing brace
            while name_pos < len(self.tokens):
                if self.tokens[name_pos].type == TokenType.IDENTIFIER:
                    enum_name = self.tokens[name_pos].value
                    break
                elif self.tokens[name_pos].type == TokenType.SEMICOLON:
                    break
                name_pos += 1
        elif not enum_tag:
            # Anonymous enum - check if there's a variable name after the brace
            while name_pos < len(self.tokens):
                if self.tokens[name_pos].type == TokenType.IDENTIFIER:
                    # This is a variable name
                    enum_name = ""
                    break
                elif self.tokens[name_pos].type == TokenType.SEMICOLON:
                    break
                name_pos += 1

        # Find semicolon
        self.pos = end_brace_pos + 1
        while self.pos < len(self.tokens) and not self._current_token_is(
            TokenType.SEMICOLON
        ):
            self.pos += 1

        end_pos = self.pos
        return (start_pos, end_pos, enum_name)

    def _parse_typedef_enum(self) -> Optional[Tuple[int, int, str]]:
        """Parse typedef enum definition"""
        if not self._current_token_is(TokenType.TYPEDEF):
            return None

        start_pos = self.pos
        self._advance()  # Consumes 'typedef'

        # Skip whitespace
        while self.pos < len(self.tokens) and self._current_token_is(
            TokenType.WHITESPACE
        ):
            self.pos += 1

        # Check if next token is 'enum'
        if not self._current_token_is(TokenType.ENUM):
            return None

        self._advance()  # Consumes 'enum'

        # Skip whitespace
        while self.pos < len(self.tokens) and self._current_token_is(
            TokenType.WHITESPACE
        ):
            self.pos += 1

        # Get enum tag name (optional)
        enum_tag = ""
        if self._current_token_is(TokenType.IDENTIFIER):
            enum_tag = self._advance().value

        # Find opening brace
        while self.pos < len(self.tokens) and not self._current_token_is(
            TokenType.LBRACE
        ):
            self.pos += 1

        if self.pos >= len(self.tokens):
            return None

        # Find matching closing brace
        end_pos = self._find_matching_brace(self.pos)
        if end_pos is None:
            return None

        # Look for typedef name after closing brace
        typedef_name = ""
        self.pos = end_pos + 1
        while self.pos < len(self.tokens) and not self._current_token_is(
            TokenType.SEMICOLON
        ):
            if self._current_token_is(TokenType.IDENTIFIER):
                typedef_name = self._advance().value
                break
            self.pos += 1

        return (start_pos, end_pos, typedef_name)

    def _parse_function(self) -> Optional[Tuple[int, int, str, str, bool, bool]]:
        """Parse function declaration/definition

        Returns:
            Tuple of (start_pos, end_pos, func_name, return_type, is_declaration, is_inline)
        """
        start_pos = self.pos

        # Look for function pattern: [modifiers] return_type function_name (params)
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]

            # If we hit a parenthesis, check if this is a function
            if token.type == TokenType.LPAREN:
                # Look backwards for function name
                if (
                    self.pos > 0
                    and self.tokens[self.pos - 1].type == TokenType.IDENTIFIER
                ):
                    func_name = self.tokens[self.pos - 1].value
                    func_name_pos = self.pos - 1

                    # Look backwards from function name to find return type
                    # Start from just before the function name
                    return_type_end = func_name_pos - 1
                    return_type_start = return_type_end

                    # Skip backwards over whitespace and comments
                    while return_type_start >= 0:
                        token_type = self.tokens[return_type_start].type
                        if token_type in [
                            TokenType.WHITESPACE,
                            TokenType.COMMENT,
                            TokenType.NEWLINE,
                        ]:
                            return_type_start -= 1
                        else:
                            break

                    # If we found a non-whitespace token, that's the end of the return type
                    # Find the start by looking backwards from there
                    if return_type_start >= 0:
                        return_type_end = return_type_start
                        return_type_start = return_type_end

                        # Define modifiers set (used in token type checking below)

                        # Collect all tokens that are part of the return type (including modifiers)
                        return_type_tokens = []

                        # Look back at most 10 tokens to capture multi-token return types
                        max_lookback = max(0, func_name_pos - 10)
                        current_pos = return_type_start

                        # Collect tokens backwards until we hit a limit or non-return-type token
                        while current_pos >= max_lookback:
                            token_type = self.tokens[current_pos].type
                            if token_type in [
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
                                TokenType.ASTERISK,
                                TokenType.CONST,
                                TokenType.STATIC,
                                TokenType.EXTERN,
                                TokenType.INLINE,
                                TokenType.LOCAL_INLINE,
                            ]:
                                return_type_tokens.insert(0, self.tokens[current_pos])
                                current_pos -= 1
                            elif token_type in [
                                TokenType.WHITESPACE,
                                TokenType.COMMENT,
                                TokenType.NEWLINE,
                            ]:
                                # Skip whitespace and continue looking
                                current_pos -= 1
                            else:
                                break

                        # Extract return type
                        if return_type_tokens:
                            return_type = " ".join(
                                t.value for t in return_type_tokens
                            ).strip()

                            # Check if function is inline
                            is_inline = any(
                                token.type in [TokenType.INLINE, TokenType.LOCAL_INLINE]
                                for token in return_type_tokens
                            )

                            # Find end of function (either ; for declaration or { for definition)
                            end_pos = self._find_function_end(self.pos)
                            if end_pos:
                                # Determine if this is a declaration or definition
                                is_declaration = self._is_function_declaration(end_pos)
                                self.pos = end_pos + 1
                                return (
                                    start_pos,
                                    end_pos,
                                    func_name,
                                    return_type,
                                    is_declaration,
                                    is_inline,
                                )

            self.pos += 1

            # Prevent infinite loops - if we've gone too far, this isn't a function
            if self.pos - start_pos > 50:
                break

        # Reset position if no function found
        self.pos = start_pos + 1
        return None

    def _is_function_declaration(self, end_pos: int) -> bool:
        """Check if the function at end_pos is a declaration (ends with ;) or definition (ends with })"""
        if end_pos >= len(self.tokens):
            return False

        # Look backwards from end_pos to find the last significant token
        pos = end_pos
        while pos >= 0:
            token_type = self.tokens[pos].type
            if token_type not in [
                TokenType.WHITESPACE,
                TokenType.COMMENT,
                TokenType.NEWLINE,
            ]:
                return token_type == TokenType.SEMICOLON
            pos -= 1

        return False

    def _find_function_end(self, start_pos: int) -> Optional[int]:
        """Find end of function declaration or definition"""
        pos = start_pos

        # Find matching closing parenthesis
        if pos >= len(self.tokens) or self.tokens[pos].type != TokenType.LPAREN:
            return None

        depth = 1
        pos += 1

        while pos < len(self.tokens) and depth > 0:
            if self.tokens[pos].type == TokenType.LPAREN:
                depth += 1
            elif self.tokens[pos].type == TokenType.RPAREN:
                depth -= 1
            pos += 1

        if depth > 0:
            return None

        # Look for either ; (declaration) or { (definition)
        while pos < len(self.tokens):
            if self.tokens[pos].type == TokenType.SEMICOLON:
                return pos
            elif self.tokens[pos].type == TokenType.LBRACE:
                # Function definition - find matching brace
                end_brace = self._find_matching_brace(pos)
                return end_brace if end_brace else pos
            pos += 1

        return None

    def _parse_union(self) -> Optional[Tuple[int, int, str]]:
        """Parse union definition"""
        if not self._current_token_is(TokenType.UNION):
            return None

        start_pos = self.pos
        self._advance()  # Consumes 'union'

        # Skip whitespace
        while self.pos < len(self.tokens) and self._current_token_is(
            TokenType.WHITESPACE
        ):
            self.pos += 1

        # Get union tag name (optional for anonymous unions)
        union_tag = ""
        if self._current_token_is(TokenType.IDENTIFIER):
            union_tag = self._advance().value

        # Find opening brace
        while self.pos < len(self.tokens) and not self._current_token_is(
            TokenType.LBRACE
        ):
            self.pos += 1

        if self.pos >= len(self.tokens):
            return None

        # Find matching closing brace
        end_pos = self._find_matching_brace(self.pos)
        if end_pos is None:
            return None

        # Look for union name after closing brace (for typedefs or named unions)
        union_name = union_tag  # Default to tag name

        # Skip to semicolon
        self.pos = end_pos + 1
        while self.pos < len(self.tokens) and not self._current_token_is(
            TokenType.SEMICOLON
        ):
            if self._current_token_is(TokenType.IDENTIFIER):
                union_name = self._advance().value
                break
            self.pos += 1

        return (start_pos, end_pos, union_name)

    def _parse_typedef_union(self) -> Optional[Tuple[int, int, str]]:
        """Parse typedef union definition"""
        if not self._current_token_is(TokenType.TYPEDEF):
            return None

        start_pos = self.pos
        self._advance()  # Consumes 'typedef'

        # Skip whitespace
        while self.pos < len(self.tokens) and self._current_token_is(
            TokenType.WHITESPACE
        ):
            self.pos += 1

        # Check if next token is 'union'
        if not self._current_token_is(TokenType.UNION):
            return None

        self._advance()  # Consumes 'union'

        # Skip whitespace
        while self.pos < len(self.tokens) and self._current_token_is(
            TokenType.WHITESPACE
        ):
            self.pos += 1

        # Get union tag name (optional)
        union_tag = ""
        if self._current_token_is(TokenType.IDENTIFIER):
            union_tag = self._advance().value

        # Find opening brace
        while self.pos < len(self.tokens) and not self._current_token_is(
            TokenType.LBRACE
        ):
            self.pos += 1

        if self.pos >= len(self.tokens):
            return None

        # Find matching closing brace
        end_pos = self._find_matching_brace(self.pos)
        if end_pos is None:
            return None

        # Look for typedef name after closing brace
        typedef_name = ""
        self.pos = end_pos + 1
        while self.pos < len(self.tokens) and not self._current_token_is(
            TokenType.SEMICOLON
        ):
            if self._current_token_is(TokenType.IDENTIFIER):
                typedef_name = self._advance().value
                break
            self.pos += 1

        return (start_pos, end_pos, typedef_name)


def extract_token_range(tokens: List[Token], start: int, end: int) -> str:
    """Extract raw text from token range, excluding whitespace, comments, and newlines"""
    if start >= len(tokens) or end >= len(tokens) or start > end:
        return ""
    return " ".join(
        token.value
        for token in tokens[start : end + 1]
        if token.type
        not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]
    )


def find_struct_fields(
    tokens: List[Token], struct_start: int, struct_end: int
) -> List[Tuple[str, str]]:
    """Extract field information from struct token range
    Returns:
        List of tuples (field_name, field_type)
    """
    fields = []
    pos = struct_start
    while pos <= struct_end and tokens[pos].type != TokenType.LBRACE:
        pos += 1
    if pos > struct_end:
        return fields
    pos += 1  # Skip opening brace

    # Find the closing brace position of the main struct body
    closing_brace_pos = pos
    brace_count = 1  # Start at 1 because we're already past the opening brace
    while closing_brace_pos <= struct_end:
        if tokens[closing_brace_pos].type == TokenType.LBRACE:
            brace_count += 1
        elif tokens[closing_brace_pos].type == TokenType.RBRACE:
            brace_count -= 1
            if brace_count == 0:
                # This is the closing brace of the main struct body
                break
        closing_brace_pos += 1

    # Parse fields using a more robust approach
    while pos < closing_brace_pos:
        # Skip whitespace and comments
        while pos < closing_brace_pos and tokens[pos].type in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
            pos += 1
        
        if pos >= closing_brace_pos:
            break
        
        # Start of a new field
        field_start = pos
        field_tokens = []
        brace_count = 0
        paren_count = 0
        bracket_count = 0
        
        # Collect tokens for this field until we find the semicolon that ends it
        while pos < closing_brace_pos:
            token = tokens[pos]
            
            # Track nesting levels
            if token.type == TokenType.LBRACE:
                brace_count += 1
            elif token.type == TokenType.RBRACE:
                brace_count -= 1
            elif token.type == TokenType.LPAREN:
                paren_count += 1
            elif token.type == TokenType.RPAREN:
                paren_count -= 1
            elif token.type == TokenType.LBRACKET:
                bracket_count += 1
            elif token.type == TokenType.RBRACKET:
                bracket_count -= 1
            elif token.type == TokenType.SEMICOLON and brace_count == 0 and paren_count == 0 and bracket_count == 0:
                # This semicolon ends the field (not inside nested structures)
                break
            
            # Add non-whitespace tokens to field
            if token.type not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
                field_tokens.append(token)
            
            pos += 1
        
        # Parse the field from collected tokens
        if len(field_tokens) >= 2:
            # Check if this field has comma-separated names
            comma_positions = []
            paren_count = 0
            brace_count = 0
            
            for i, token in enumerate(field_tokens):
                if token.type == TokenType.LPAREN:
                    paren_count += 1
                elif token.type == TokenType.RPAREN:
                    paren_count -= 1
                elif token.type == TokenType.LBRACE:
                    brace_count += 1
                elif token.type == TokenType.RBRACE:
                    brace_count -= 1
                elif token.type == TokenType.COMMA and paren_count == 0 and brace_count == 0:
                    comma_positions.append(i)
            
            if comma_positions:
                # Handle comma-separated fields
                field_info = _parse_comma_separated_fields(field_tokens, comma_positions)
                if field_info:
                    field_name, field_type = field_info
                    fields.append((field_name, field_type))
                    
                    # Add additional fields after commas
                    for comma_pos in comma_positions:
                        if comma_pos + 1 < len(field_tokens):
                            # Find the next field name after the comma
                            next_field_start = None
                            for j in range(comma_pos + 1, len(field_tokens)):
                                if field_tokens[j].type == TokenType.IDENTIFIER:
                                    next_field_start = j
                                    break
                            
                            if next_field_start is not None:
                                next_field_name = field_tokens[next_field_start].value
                                fields.append((next_field_name, field_type))
            else:
                # Single field
                field_info = _parse_field_from_tokens(field_tokens)
                if field_info:
                    field_name, field_type = field_info
                    fields.append((field_name, field_type))
        
        # Move past the semicolon
        if pos < closing_brace_pos:
            pos += 1

    return fields


def _parse_field_from_tokens(field_tokens: List[Token]) -> Optional[Tuple[str, str]]:
    """Parse a single field from its tokens."""
    if len(field_tokens) < 2:
        return None
    
    # Check if this is a nested struct field
    if (len(field_tokens) >= 3 and 
        field_tokens[0].type == TokenType.STRUCT and 
        field_tokens[1].type == TokenType.LBRACE):
        return _parse_nested_struct_field(field_tokens)
    
    # Check if this is a nested union field
    if (len(field_tokens) >= 3 and 
        field_tokens[0].type == TokenType.UNION and 
        field_tokens[1].type == TokenType.LBRACE):
        return _parse_nested_union_field(field_tokens)
    
    # Check if this is a function pointer field
    if _is_function_pointer_field(field_tokens):
        return _parse_function_pointer_field(field_tokens)
    
    # Check if this is an array field
    if _is_array_field(field_tokens):
        return _parse_array_field(field_tokens)
    
    # Regular field: type name
    return _parse_regular_field(field_tokens)


def _parse_nested_struct_field(field_tokens: List[Token]) -> Optional[Tuple[str, str]]:
    """Parse a nested struct field."""
    # Find the field name after the closing brace
    field_name = None
    for i in range(len(field_tokens) - 1, -1, -1):
        if field_tokens[i].type == TokenType.RBRACE and i + 1 < len(field_tokens):
            # Look for the field name after the closing brace
            for j in range(i + 1, len(field_tokens)):
                if field_tokens[j].type == TokenType.IDENTIFIER:
                    field_name = field_tokens[j].value
                    break
            if field_name:
                break
    
    if field_name:
        # Extract the struct content for anonymous processor
        content = _extract_brace_content(field_tokens)
        if content:
            # Use special format for anonymous processor
            # Encode the complete struct content, not just the field content
            import base64
            # Create a complete struct definition that can be parsed
            complete_struct_content = f"struct {{ {content} }}"
            encoded_content = base64.b64encode(complete_struct_content.encode()).decode()
            field_type = f"struct {{ /*ANON:{encoded_content}:{field_name}*/ ... }}"
        else:
            field_type = "struct { ... }"
        
        return field_name, field_type
    
    return None


def _parse_nested_union_field(field_tokens: List[Token]) -> Optional[Tuple[str, str]]:
    """Parse a nested union field."""
    # Find the field name after the closing brace
    field_name = None
    for i in range(len(field_tokens) - 1, -1, -1):
        if field_tokens[i].type == TokenType.RBRACE and i + 1 < len(field_tokens):
            # Look for the field name after the closing brace
            for j in range(i + 1, len(field_tokens)):
                if field_tokens[j].type == TokenType.IDENTIFIER:
                    field_name = field_tokens[j].value
                    break
            if field_name:
                break
    
    if field_name:
        # Extract the union content for anonymous processor
        content = _extract_brace_content(field_tokens)
        if content:
            # Use special format for anonymous processor
            # Encode the complete union content, not just the field content
            import base64
            # Create a complete union definition that can be parsed
            complete_union_content = f"union {{ {content} }}"
            encoded_content = base64.b64encode(complete_union_content.encode()).decode()
            field_type = f"union {{ /*ANON:{encoded_content}:{field_name}*/ ... }}"
        else:
            field_type = "union { ... }"
        
        return field_name, field_type
    
    return None


def _is_function_pointer_field(field_tokens: List[Token]) -> bool:
    """Check if tokens represent a function pointer field."""
    if len(field_tokens) < 5:
        return False
    
    # Look for pattern: type (*name)(params)
    for i in range(len(field_tokens) - 4):
        if (field_tokens[i].type == TokenType.LPAREN and
            field_tokens[i + 1].type == TokenType.ASTERISK and
            field_tokens[i + 2].type == TokenType.IDENTIFIER and
            field_tokens[i + 3].type == TokenType.RPAREN):
            return True
    
    return False


def _parse_function_pointer_field(field_tokens: List[Token]) -> Optional[Tuple[str, str]]:
    """Parse a function pointer field."""
    # Find the function pointer name
    for i in range(len(field_tokens) - 4):
        if (field_tokens[i].type == TokenType.LPAREN and
            field_tokens[i + 1].type == TokenType.ASTERISK and
            field_tokens[i + 2].type == TokenType.IDENTIFIER and
            field_tokens[i + 3].type == TokenType.RPAREN):
            field_name = field_tokens[i + 2].value
            field_type = " ".join(t.value for t in field_tokens)
            return field_name, field_type
    
    return None


def _is_array_field(field_tokens: List[Token]) -> bool:
    """Check if tokens represent an array field."""
    if len(field_tokens) < 4:
        return False
    
    # Look for pattern: type name[size]
    for i in range(len(field_tokens) - 3):
        if (field_tokens[i + 1].type == TokenType.LBRACKET and
            field_tokens[i + 3].type == TokenType.RBRACKET):
            return True
    
    return False


def _parse_array_field(field_tokens: List[Token]) -> Optional[Tuple[str, str]]:
    """Parse an array field."""
    # Find the array pattern
    for i in range(len(field_tokens) - 3):
        if (field_tokens[i + 1].type == TokenType.LBRACKET and
            field_tokens[i + 3].type == TokenType.RBRACKET):
            field_name = field_tokens[i].value
            # Extract type (everything before the field name)
            type_tokens = field_tokens[:i]
            field_type = " ".join(t.value for t in type_tokens) + "[" + field_tokens[i + 2].value + "]"
            return field_name, field_type
    
    return None


def _parse_regular_field(field_tokens: List[Token]) -> Optional[Tuple[str, str]]:
    """Parse a regular field (type name)."""
    # Check for comma-separated fields
    comma_positions = []
    paren_count = 0
    brace_count = 0
    
    for i, token in enumerate(field_tokens):
        if token.type == TokenType.LPAREN:
            paren_count += 1
        elif token.type == TokenType.RPAREN:
            paren_count -= 1
        elif token.type == TokenType.LBRACE:
            brace_count += 1
        elif token.type == TokenType.RBRACE:
            brace_count -= 1
        elif token.type == TokenType.COMMA and paren_count == 0 and brace_count == 0:
            comma_positions.append(i)
    
    if comma_positions:
        # Multiple fields of the same type
        return _parse_comma_separated_fields(field_tokens, comma_positions)
    else:
        # Single field
        return _parse_single_field(field_tokens)


def _parse_comma_separated_fields(field_tokens: List[Token], comma_positions: List[int]) -> Optional[Tuple[str, str]]:
    """Parse comma-separated fields."""
    # Find the first field name to determine the type
    first_field_start = None
    for i, token in enumerate(field_tokens):
        if token.type == TokenType.IDENTIFIER:
            first_field_start = i
            break
    
    if first_field_start is None:
        return None
    
    # Extract the type (everything before the first field name)
    type_tokens = field_tokens[:first_field_start]
    field_type = " ".join(t.value for t in type_tokens)
    
    # For comma-separated fields, we need to return multiple field entries
    # Since this function can only return one field, we'll return the first one
    # and let the caller handle the rest by calling this function again
    # with the remaining tokens after the first comma
    
    # Find the first comma position
    first_comma = comma_positions[0] if comma_positions else len(field_tokens)
    
    # Extract the first field name
    field_name = field_tokens[first_field_start].value
    
    # Return the first field
    return field_name, field_type


def _parse_single_field(field_tokens: List[Token]) -> Optional[Tuple[str, str]]:
    """Parse a single field."""
    # Find the last identifier as the field name
    field_name = None
    for i in range(len(field_tokens) - 1, -1, -1):
        if field_tokens[i].type == TokenType.IDENTIFIER:
            field_name = field_tokens[i].value
            break
    
    if field_name is None:
        return None
    
    # The field type is everything except the field name
    type_tokens = [t for t in field_tokens if t.value != field_name]
    field_type = " ".join(t.value for t in type_tokens)
    
    if field_type.strip():
        return field_name, field_type.strip()
    
    return None


def _extract_brace_content(field_tokens: List[Token]) -> str:
    """Extract the content between braces from field tokens.
    
    Args:
        field_tokens: List of tokens representing a field with anonymous structure
        
    Returns:
        String content between the braces, or empty string if not found
    """
    content_tokens = []
    in_braces = False
    brace_count = 0
    
    for token in field_tokens:
        if token.type == TokenType.LBRACE:
            if not in_braces:
                in_braces = True
                brace_count = 1
            else:
                brace_count += 1
                content_tokens.append(token)
        elif token.type == TokenType.RBRACE:
            if in_braces:
                brace_count -= 1
                if brace_count == 0:
                    # Found the closing brace
                    break
                else:
                    content_tokens.append(token)
        elif in_braces:
            content_tokens.append(token)
    
    # Convert tokens back to text preserving spacing
    if content_tokens:
        result = ""
        for i, token in enumerate(content_tokens):
            result += token.value
            # Add space after most tokens except when next token is punctuation
            if (i < len(content_tokens) - 1 and 
                token.type not in [TokenType.WHITESPACE, TokenType.NEWLINE] and
                content_tokens[i + 1].type not in [TokenType.LBRACKET, TokenType.RBRACKET, 
                                                   TokenType.SEMICOLON, TokenType.COMMA,
                                                   TokenType.WHITESPACE, TokenType.NEWLINE]):
                result += " "
        return result
    return ""


def find_enum_values(tokens: List[Token], enum_start: int, enum_end: int) -> List[str]:
    """Extract enum values from enum token range"""
    values = []
    pos = enum_start
    while pos <= enum_end and tokens[pos].type != TokenType.LBRACE:
        pos += 1
    if pos > enum_end:
        return values
    pos += 1  # Skip opening brace
    current_value = []
    while pos <= enum_end and tokens[pos].type != TokenType.RBRACE:
        token = tokens[pos]
        if token.type == TokenType.COMMA:
            if current_value:
                filtered_value = [
                    t
                    for t in current_value
                    if t.type not in [TokenType.WHITESPACE, TokenType.COMMENT]
                ]
                if filtered_value:
                    value_str = " ".join(t.value for t in filtered_value).strip()
                    if value_str:
                        values.append(value_str)
                current_value = []
        elif token.type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
            current_value.append(token)
        pos += 1
    if current_value:
        filtered_value = [
            t
            for t in current_value
            if t.type not in [TokenType.WHITESPACE, TokenType.COMMENT]
        ]
        if filtered_value:
            value_str = " ".join(t.value for t in filtered_value).strip()
            if value_str:
                values.append(value_str)
    return values
