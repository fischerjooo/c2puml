#!/usr/bin/env python3
"""
Tokenizer module for C to PlantUML converter - Helper library for tokenizing C/C++ code
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Iterator, List, Optional, Tuple


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
    LBRACE = "LBRACE"           # {
    RBRACE = "RBRACE"           # }
    LPAREN = "LPAREN"           # (
    RPAREN = "RPAREN"           # )
    LBRACKET = "LBRACKET"       # [
    RBRACKET = "RBRACKET"       # ]
    SEMICOLON = "SEMICOLON"     # ;
    COMMA = "COMMA"             # ,
    ASSIGN = "ASSIGN"           # =
    ASTERISK = "ASTERISK"       # *
    AMPERSAND = "AMPERSAND"     # &
    
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
        'struct': TokenType.STRUCT,
        'enum': TokenType.ENUM,
        'union': TokenType.UNION,
        'typedef': TokenType.TYPEDEF,
        'static': TokenType.STATIC,
        'extern': TokenType.EXTERN,
        'inline': TokenType.INLINE,
        'const': TokenType.CONST,
        'void': TokenType.VOID,
        'char': TokenType.CHAR,
        'int': TokenType.INT,
        'float': TokenType.FLOAT,
        'double': TokenType.DOUBLE,
        'long': TokenType.LONG,
        'short': TokenType.SHORT,
        'unsigned': TokenType.UNSIGNED,
        'signed': TokenType.SIGNED,
    }
    
    # Single character tokens
    SINGLE_CHAR_TOKENS = {
        '{': TokenType.LBRACE,
        '}': TokenType.RBRACE,
        '(': TokenType.LPAREN,
        ')': TokenType.RPAREN,
        '[': TokenType.LBRACKET,
        ']': TokenType.RBRACKET,
        ';': TokenType.SEMICOLON,
        ',': TokenType.COMMA,
        '=': TokenType.ASSIGN,
        '*': TokenType.ASTERISK,
        '&': TokenType.AMPERSAND,
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Compiled regex patterns for efficiency
        self.patterns = {
            'identifier': re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*'),
            'number': re.compile(r'0[xX][0-9a-fA-F]+[uUlL]*|0[bB][01]+[uUlL]*|0[0-7]+[uUlL]*|\d+\.\d*([eE][+-]?\d+)?[fFlL]*|\d+([eE][+-]?\d+)?[fFlL]*|\d+[uUlL]*'),
            'string': re.compile(r'"([^"\\]|\\.)*"'),
            'char': re.compile(r"'([^'\\]|\\.)'"),
            'comment_single': re.compile(r'//.*'),
            'comment_multi': re.compile(r'/\*.*?\*/', re.DOTALL),
            'preprocessor': re.compile(r'#.*'),
            'whitespace': re.compile(r'[ \t]+'),
            'newline': re.compile(r'\n'),
        }
    
    def tokenize(self, content: str) -> List[Token]:
        """Tokenize C/C++ source code content"""
        tokens = []
        lines = content.split('\n')
        total_lines = len(lines)
        
        for line_num, line in enumerate(lines, 1):
            line_tokens = self._tokenize_line(line, line_num)
            tokens.extend(line_tokens)
            
            # Add newline token after each line (except the last line)
            if line_num < total_lines:
                tokens.append(Token(TokenType.NEWLINE, '\n', line_num, len(line)))
        
        # Add EOF token
        tokens.append(Token(TokenType.EOF, '', total_lines, len(lines[-1]) if lines else 0))
        
        return tokens
    
    def _tokenize_line(self, line: str, line_num: int) -> List[Token]:
        """Tokenize a single line of code"""
        tokens = []
        pos = 0
        
        while pos < len(line):
            # Skip whitespace but track it
            if match := self.patterns['whitespace'].match(line, pos):
                tokens.append(Token(TokenType.WHITESPACE, match.group(), line_num, pos))
                pos = match.end()
                continue
            
            # Comments
            if match := self.patterns['comment_single'].match(line, pos):
                tokens.append(Token(TokenType.COMMENT, match.group(), line_num, pos))
                pos = len(line)  # Rest of line is comment
                continue
            
            # Multi-line comments - check for /* at start of line or after whitespace
            if line[pos:].startswith('/*'):
                # Find the end of the comment
                comment_start = pos
                comment_end = line.find('*/', pos)
                if comment_end != -1:
                    # Comment ends on this line
                    comment_text = line[pos:comment_end + 2]
                    tokens.append(Token(TokenType.COMMENT, comment_text, line_num, pos))
                    pos = comment_end + 2
                    continue
                else:
                    # Comment continues to next line - handle in tokenize method
                    comment_text = line[pos:]
                    tokens.append(Token(TokenType.COMMENT, comment_text, line_num, pos))
                    pos = len(line)
                    continue
            
            # Preprocessor directives
            if match := self.patterns['preprocessor'].match(line, pos):
                value = match.group()
                if value.startswith('#include'):
                    tokens.append(Token(TokenType.INCLUDE, value, line_num, pos))
                elif value.startswith('#define'):
                    tokens.append(Token(TokenType.DEFINE, value, line_num, pos))
                else:
                    tokens.append(Token(TokenType.PREPROCESSOR, value, line_num, pos))
                pos = len(line)  # Rest of line is preprocessor
                continue
            
            # String literals
            if line[pos] == '"' or (
                pos > 0 and line[pos-1] in ['L', 'u', 'U', 'R'] and line[pos] == '"') or (
                pos > 1 and line[pos-2:pos] == 'u8' and line[pos] == '"'):
                # Handle string literals with possible prefixes
                string_start = pos
                prefix = ''
                if line[pos-2:pos] == 'u8':
                    prefix = 'u8'
                    string_start -= 2
                elif line[pos-1] in ['L', 'u', 'U', 'R']:
                    prefix = line[pos-1]
                    string_start -= 1
                pos += 1  # Skip opening quote
                while pos < len(line):
                    if line[pos] == '"':
                        # Found closing quote
                        string_text = line[string_start:pos + 1]
                        tokens.append(Token(TokenType.STRING, string_text, line_num, string_start))
                        pos += 1
                        break
                    elif line[pos] == '\\':
                        pos += 2
                    else:
                        pos += 1
                else:
                    string_text = line[string_start:]
                    tokens.append(Token(TokenType.STRING, string_text, line_num, string_start))
                    pos = len(line)
                continue
            
            # Character literals
            if match := self.patterns['char'].match(line, pos):
                tokens.append(Token(TokenType.CHAR_LITERAL, match.group(), line_num, pos))
                pos = match.end()
                continue
            
            # Numbers
            if match := self.patterns['number'].match(line, pos):
                tokens.append(Token(TokenType.NUMBER, match.group(), line_num, pos))
                pos = match.end()
                continue
            
            # Single character tokens
            if line[pos] in self.SINGLE_CHAR_TOKENS:
                token_type = self.SINGLE_CHAR_TOKENS[line[pos]]
                tokens.append(Token(token_type, line[pos], line_num, pos))
                pos += 1
                continue
            
            # Identifiers and keywords
            if match := self.patterns['identifier'].match(line, pos):
                value = match.group()
                token_type = self.KEYWORDS.get(value.lower(), TokenType.IDENTIFIER)
                tokens.append(Token(token_type, value, line_num, pos))
                pos = match.end()
                continue
            
            # Unknown character
            tokens.append(Token(TokenType.UNKNOWN, line[pos], line_num, pos))
            pos += 1
        
        return tokens
    
    def filter_tokens(self, tokens: List[Token], 
                     exclude_types: Optional[List[TokenType]] = None) -> List[Token]:
        """Filter tokens by type"""
        if exclude_types is None:
            exclude_types = [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]
        
        return [token for token in tokens if token.type not in exclude_types]


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
    
    def find_functions(self) -> List[Tuple[int, int, str, str, bool]]:
        """Find all function declarations and definitions in the token stream
        
        Returns:
            List of tuples (start_pos, end_pos, func_name, return_type, is_declaration)
        """
        functions = []
        self.pos = 0
        
        while self.pos < len(self.tokens):
            result = self._parse_function()
            if result:
                functions.append(result)
        
        return functions
    
    def _current_token_is(self, token_type: TokenType) -> bool:
        """Check if current token is of specified type"""
        return (self.pos < len(self.tokens) and 
                self.tokens[self.pos].type == token_type)
    
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
        if start_pos >= len(self.tokens) or self.tokens[start_pos].type != TokenType.LBRACE:
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
        
        # Get struct name (optional for anonymous structs)
        struct_name = ""
        if self._current_token_is(TokenType.IDENTIFIER):
            struct_name = self._advance().value
        
        # Find opening brace
        while self.pos < len(self.tokens) and not self._current_token_is(TokenType.LBRACE):
            self.pos += 1
        
        if not self._current_token_is(TokenType.LBRACE):
            return None
        
        # Find matching closing brace
        brace_pos = self.pos
        end_brace_pos = self._find_matching_brace(brace_pos)
        
        if end_brace_pos is None:
            return None
        
        # Find semicolon (for struct definitions)
        self.pos = end_brace_pos + 1
        while (self.pos < len(self.tokens) and 
               not self._current_token_is(TokenType.SEMICOLON)):
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
        
        # Parse the struct part
        struct_info = self._parse_struct()
        if not struct_info:
            self.pos = start_pos + 1
            return None
        
        # Look for typedef name after struct
        struct_end = struct_info[1]
        self.pos = struct_end
        
        # Look forward to find typedef name
        while self.pos < len(self.tokens):
            if self.tokens[self.pos].type == TokenType.IDENTIFIER:
                typedef_name = self.tokens[self.pos].value
                return (start_pos, self.pos, typedef_name)
            elif self.tokens[self.pos].type == TokenType.SEMICOLON:
                # Reached end without finding name
                break
            self.pos += 1
        
        return (start_pos, struct_end, "")
    
    def _parse_enum(self) -> Optional[Tuple[int, int, str]]:
        """Parse enum definition starting at current position"""
        start_pos = self.pos
        
        # Consume 'enum' keyword
        if not self._current_token_is(TokenType.ENUM):
            return None
        self._advance()
        
        # Get enum name (optional for anonymous enums)
        enum_name = ""
        if self._current_token_is(TokenType.IDENTIFIER):
            enum_name = self._advance().value
        
        # Find opening brace
        while self.pos < len(self.tokens) and not self._current_token_is(TokenType.LBRACE):
            self.pos += 1
        
        if not self._current_token_is(TokenType.LBRACE):
            return None
        
        # Find matching closing brace
        brace_pos = self.pos
        end_brace_pos = self._find_matching_brace(brace_pos)
        
        if end_brace_pos is None:
            return None
        
        # Find semicolon
        self.pos = end_brace_pos + 1
        while (self.pos < len(self.tokens) and 
               not self._current_token_is(TokenType.SEMICOLON)):
            self.pos += 1
        
        end_pos = self.pos
        return (start_pos, end_pos, enum_name)
    
    def _parse_typedef_enum(self) -> Optional[Tuple[int, int, str]]:
        """Parse typedef enum definition"""
        start_pos = self.pos
        
        # Consume 'typedef'
        if not self._current_token_is(TokenType.TYPEDEF):
            return None
        self._advance()
        
        # Look for 'enum'
        if not self._current_token_is(TokenType.ENUM):
            # Not a typedef enum, reset position
            self.pos = start_pos + 1
            return None
        
        # Parse the enum part
        enum_info = self._parse_enum()
        if not enum_info:
            self.pos = start_pos + 1
            return None
        
        # Look for typedef name after enum
        enum_end = enum_info[1]
        self.pos = enum_end
        
        # Look forward to find typedef name
        while self.pos < len(self.tokens):
            if self.tokens[self.pos].type == TokenType.IDENTIFIER:
                typedef_name = self.tokens[self.pos].value
                return (start_pos, self.pos, typedef_name)
            elif self.tokens[self.pos].type == TokenType.SEMICOLON:
                # Reached end without finding name
                break
            self.pos += 1
        
        return (start_pos, enum_end, "")
    
    def _parse_function(self) -> Optional[Tuple[int, int, str, str, bool]]:
        """Parse function declaration/definition
        
        Returns:
            Tuple of (start_pos, end_pos, func_name, return_type, is_declaration)
        """
        start_pos = self.pos
        
        # Look for function pattern: [modifiers] return_type function_name (params)
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            
            # If we hit a parenthesis, check if this is a function
            if token.type == TokenType.LPAREN:
                # Look backwards for function name
                if self.pos > 0 and self.tokens[self.pos - 1].type == TokenType.IDENTIFIER:
                    func_name = self.tokens[self.pos - 1].value
                    func_name_pos = self.pos - 1
                    
                    # Look backwards from function name to find return type
                    # Start from just before the function name
                    return_type_end = func_name_pos - 1
                    return_type_start = return_type_end
                    
                    # Skip backwards over whitespace and comments
                    while return_type_start >= 0:
                        token_type = self.tokens[return_type_start].type
                        if token_type in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
                            return_type_start -= 1
                        else:
                            break
                    
                    # Define modifiers set
                    modifiers = {TokenType.STATIC, TokenType.EXTERN, TokenType.INLINE}
                    
                    # Now look backwards to find the complete return type
                    # We need to include all tokens that are part of the return type
                    # For example: "point_t *" should include both "point_t" and "*"
                    # But we need to be careful not to go too far back and include content from other functions
                    
                    # Look back at most 20 tokens to capture multi-token return types like "point_t *"
                    # This ensures we capture both "point_t" and "*" tokens
                    max_lookback = max(0, func_name_pos - 20)
                    if return_type_start < max_lookback:
                        return_type_start = max_lookback
                    

                    
                    # Skip modifiers like static, extern, inline
                    while (return_type_start >= 0 and 
                           self.tokens[return_type_start].type in modifiers):
                        return_type_start -= 1
                    
                    # Now collect the return type tokens
                    # Look back enough to capture multi-token return types like "point_t *"
                    # We need to look back further to capture the full return type
                    max_lookback = max(0, func_name_pos - 8)  # Look back at most 8 tokens
                    if return_type_start < max_lookback:
                        return_type_start = max_lookback
                    
                    # Extract return type
                    if return_type_start >= 0 and return_type_start <= return_type_end:
                        return_type_tokens = self.tokens[return_type_start:return_type_end + 1]
                        return_type = ' '.join(t.value for t in return_type_tokens).strip()
                        
                        # Find end of function (either ; for declaration or { for definition)
                        end_pos = self._find_function_end(self.pos)
                        if end_pos:
                            # Determine if this is a declaration or definition
                            is_declaration = self._is_function_declaration(end_pos)
                            self.pos = end_pos + 1
                            return (start_pos, end_pos, func_name, return_type, is_declaration)
            
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
            if token_type not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
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
        
        # Now look for either ; (declaration) or { (definition)
        while pos < len(self.tokens):
            if self.tokens[pos].type == TokenType.SEMICOLON:
                return pos
            elif self.tokens[pos].type == TokenType.LBRACE:
                # Function definition - find matching brace
                end_brace = self._find_matching_brace(pos)
                return end_brace if end_brace else pos
            pos += 1
        
        return None


def extract_token_range(tokens: List[Token], start: int, end: int) -> str:
    """Extract raw text from token range"""
    if start >= len(tokens) or end >= len(tokens) or start > end:
        return ""
    
    return ' '.join(token.value for token in tokens[start:end + 1])


def find_struct_fields(tokens: List[Token], struct_start: int, struct_end: int) -> List[Tuple[str, str]]:
    """Extract field information from struct token range
    
    Returns:
        List of tuples (field_name, field_type)
    """
    fields = []
    
    # Find the opening brace of the struct
    pos = struct_start
    while pos <= struct_end and tokens[pos].type != TokenType.LBRACE:
        pos += 1
    
    if pos > struct_end:
        return fields
    
    pos += 1  # Skip opening brace
    
    # Parse fields until closing brace
    while pos <= struct_end and tokens[pos].type != TokenType.RBRACE:
        # Look for field declarations (type name;)
        field_tokens = []
        
        # Collect tokens until semicolon
        while pos <= struct_end and tokens[pos].type != TokenType.SEMICOLON:
            if tokens[pos].type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
                field_tokens.append(tokens[pos])
            pos += 1
        
        # Parse field from collected tokens
        if len(field_tokens) >= 2:
            # Handle array fields: type name[size]
            if (len(field_tokens) >= 3 and 
                field_tokens[-3].type == TokenType.LBRACKET and 
                field_tokens[-1].type == TokenType.RBRACKET):
                # Array field: type name[size]
                field_name = field_tokens[-4].value if len(field_tokens) >= 4 else field_tokens[-2].value
                field_type = ' '.join(t.value for t in field_tokens[:-4]) + ' ' + field_tokens[-2].value + '[]'
            else:
                # Regular field: type name
                field_name = field_tokens[-1].value
                field_type = ' '.join(t.value for t in field_tokens[:-1])
            
            # Validate field name is not empty or invalid
            if field_name and field_name not in ['[', ']', ';']:
                fields.append((field_name, field_type))
        
        if pos <= struct_end:
            pos += 1  # Skip semicolon
    
    return fields


def find_enum_values(tokens: List[Token], enum_start: int, enum_end: int) -> List[str]:
    """Extract enum values from enum token range"""
    values = []
    
    # Find the opening brace of the enum
    pos = enum_start
    while pos <= enum_end and tokens[pos].type != TokenType.LBRACE:
        pos += 1
    
    if pos > enum_end:
        return values
    
    pos += 1  # Skip opening brace
    
    # Parse enum values until closing brace
    current_value = []
    
    while pos <= enum_end and tokens[pos].type != TokenType.RBRACE:
        token = tokens[pos]
        
        if token.type == TokenType.COMMA:
            # End of current enum value
            if current_value:
                # Filter out whitespace and comments from current value
                filtered_value = [t for t in current_value if t.type not in [TokenType.WHITESPACE, TokenType.COMMENT]]
                if filtered_value:
                    values.append(' '.join(t.value for t in filtered_value))
                current_value = []
        elif token.type not in [TokenType.WHITESPACE, TokenType.COMMENT]:
            current_value.append(token)
        
        pos += 1
    
    # Add last value if exists
    if current_value:
        # Filter out whitespace and comments from current value
        filtered_value = [t for t in current_value if t.type not in [TokenType.WHITESPACE, TokenType.COMMENT]]
        if filtered_value:
            values.append(' '.join(t.value for t in filtered_value))
    
    return values