#!/usr/bin/env python3
"""
Fixed tokenizer module for C to PlantUML converter - Helper library for tokenizing C/C++ code
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


def find_struct_fields_fixed(
    tokens: List[Token], struct_start: int, struct_end: int
) -> List[Tuple[str, str]]:
    """Extract field information from struct token range with improved logic
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

    # Only parse fields up to the closing brace
    while pos < closing_brace_pos and tokens[pos].type != TokenType.RBRACE:
        field_tokens = []
        # Collect tokens until we find the semicolon that ends this field
        # For nested structures, we need to handle braces properly
        brace_count = 0
        field_start_pos = pos
        
        # First pass: collect tokens until we find a semicolon outside of braces
        while pos < closing_brace_pos:
            if tokens[pos].type == TokenType.LBRACE:
                brace_count += 1
            elif tokens[pos].type == TokenType.RBRACE:
                brace_count -= 1
                # Only stop if we're at the main closing brace
                if pos == closing_brace_pos:
                    break
            elif tokens[pos].type == TokenType.SEMICOLON and brace_count == 0:
                # This is the semicolon that ends the field
                break
            
            if tokens[pos].type not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
                field_tokens.append(tokens[pos])
            pos += 1
        
        # For nested structures, we need to continue collecting tokens until we find the field name
        # and the semicolon that ends the entire field
        if (len(field_tokens) >= 3 and 
            field_tokens[0].type in [TokenType.STRUCT, TokenType.UNION] and 
            field_tokens[1].type == TokenType.LBRACE):
            # This might be a nested structure, continue collecting until we find the field name
            temp_pos = pos
            brace_count = 0  # Track nested braces to find the correct field boundary
            field_complete = False
            
            # First, collect all tokens until we find the closing brace of this nested structure
            while temp_pos < len(tokens) and not field_complete:
                if tokens[temp_pos].type == TokenType.LBRACE:
                    brace_count += 1
                elif tokens[temp_pos].type == TokenType.RBRACE:
                    brace_count -= 1
                    # If we're back to brace_count == 0, we've found the closing brace of this nested structure
                    if brace_count == 0:
                        # Look for the field name after this closing brace
                        name_pos = temp_pos + 1
                        while name_pos < len(tokens):
                            if tokens[name_pos].type == TokenType.IDENTIFIER:
                                # Found the field name, now look for the semicolon
                                semicolon_pos = name_pos + 1
                                while semicolon_pos < len(tokens):
                                    if tokens[semicolon_pos].type == TokenType.SEMICOLON:
                                        # Found the complete field, collect all tokens up to the semicolon
                                        for i in range(temp_pos + 1, semicolon_pos + 1):
                                            if tokens[i].type not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
                                                field_tokens.append(tokens[i])
                                        pos = semicolon_pos + 1
                                        field_complete = True
                                        break
                                    elif tokens[semicolon_pos].type not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
                                        # Found something other than whitespace before semicolon, this is not a valid field
                                        break
                                    semicolon_pos += 1
                                break
                            elif tokens[name_pos].type not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
                                # Found something other than whitespace before identifier, this is not a valid field
                                break
                            name_pos += 1
                        break
                elif tokens[temp_pos].type == TokenType.SEMICOLON and brace_count == 0:
                    # Found the semicolon that ends the field (not inside nested braces)
                    break
                
                if not field_complete and tokens[temp_pos].type not in [TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE]:
                    field_tokens.append(tokens[temp_pos])
                temp_pos += 1
            
            if not field_complete:
                pos = temp_pos

        # Parse field from collected tokens
        if len(field_tokens) >= 2:
            # Check if this is a nested struct field
            if (
                len(field_tokens) >= 3
                and field_tokens[0].type == TokenType.STRUCT
                and field_tokens[1].type == TokenType.LBRACE
            ):
                # This is a nested struct - find the field name after the closing brace
                # Look for the pattern: struct { ... } field_name;
                field_name = None
                # Find the LAST closing brace and then the field name
                # This handles deeply nested structures correctly
                for i in range(len(field_tokens) - 1, -1, -1):
                    if field_tokens[i].type == TokenType.RBRACE and i + 1 < len(field_tokens):
                        # The field name should be the next identifier after the closing brace
                        for j in range(i + 1, len(field_tokens)):
                            if field_tokens[j].type == TokenType.IDENTIFIER:
                                field_name = field_tokens[j].value
                                break
                        if field_name:
                            break
                
                if field_name:
                    # Extract the content between braces for anonymous structure processing
                    content = _extract_brace_content(field_tokens)
                    if content:
                        # Preserve content for anonymous processor using special format
                        import base64
                        encoded_content = base64.b64encode(content.encode()).decode()
                        field_type = f"struct {{ /*ANON:{encoded_content}:{field_name}*/ ... }}"
                    else:
                        field_type = "struct { ... }"
                    
                    if field_name not in ["[", "]", ";", "}"]:
                        fields.append((field_name, field_type))
                        # Skip parsing the nested struct's fields as separate fields
                        # Let the normal flow handle semicolon advancement
            # Check if this is a nested union field
            elif (
                len(field_tokens) >= 3
                and field_tokens[0].type == TokenType.UNION
                and field_tokens[1].type == TokenType.LBRACE
            ):
                # This is a nested union - find the field name after the closing brace
                # Look for the pattern: union { ... } field_name;
                field_name = None
                # Find the LAST closing brace and then the field name
                # This handles deeply nested structures correctly
                for i in range(len(field_tokens) - 1, -1, -1):
                    if field_tokens[i].type == TokenType.RBRACE and i + 1 < len(field_tokens):
                        # The field name should be the next identifier after the closing brace
                        for j in range(i + 1, len(field_tokens)):
                            if field_tokens[j].type == TokenType.IDENTIFIER:
                                field_name = field_tokens[j].value
                                break
                        if field_name:
                            break
                
                if field_name:
                    # Extract the content between braces for anonymous structure processing
                    content = _extract_brace_content(field_tokens)
                    if content:
                        # Preserve content for anonymous processor using special format
                        import base64
                        encoded_content = base64.b64encode(content.encode()).decode()
                        field_type = f"union {{ /*ANON:{encoded_content}:{field_name}*/ ... }}"
                    else:
                        field_type = "union { ... }"
                    
                    if field_name not in ["[", "]", ";", "}"]:
                        fields.append((field_name, field_type))
                        # Skip parsing the nested union's fields as separate fields
                        # Let the normal flow handle semicolon advancement
            # Function pointer array field: type (*name[size])(params)
            elif (
                len(field_tokens) >= 8
                and field_tokens[1].type == TokenType.LPAREN
                and field_tokens[2].type == TokenType.ASTERISK
                and any(t.type == TokenType.LBRACKET for t in field_tokens)
                and any(t.type == TokenType.RBRACKET for t in field_tokens)
            ):
                # Find the function pointer name (between * and [)
                # Look for the identifier between * and [
                name_start = 3  # After the *
                name_end = None
                for i in range(name_start, len(field_tokens)):
                    if field_tokens[i].type == TokenType.LBRACKET:
                        name_end = i
                        break

                if name_end is not None:
                    field_name = " ".join(
                        t.value for t in field_tokens[name_start:name_end]
                    )

                    # Format the type properly - preserve spaces between tokens but not around brackets/parentheses
                    formatted_tokens = []
                    for j, token in enumerate(field_tokens):
                        if token.type in [
                            TokenType.LPAREN,
                            TokenType.RPAREN,
                            TokenType.LBRACKET,
                            TokenType.RBRACKET,
                        ]:
                            # Don't add spaces around brackets/parentheses
                            formatted_tokens.append(token.value)
                        elif j > 0 and field_tokens[j - 1].type not in [
                            TokenType.LPAREN,
                            TokenType.RPAREN,
                            TokenType.LBRACKET,
                            TokenType.RBRACKET,
                        ]:
                            # Add space before token if previous token wasn't a bracket/parenthesis
                            formatted_tokens.append(" " + token.value)
                        else:
                            # No space before token
                            formatted_tokens.append(token.value)
                    field_type = "".join(formatted_tokens)

                    # Validate and add the field
                    if (
                        field_name
                        and field_name.strip()
                        and field_type.strip()
                        and field_name not in ["[", "]", ";", "}"]
                    ):
                        stripped_name = field_name.strip()
                        stripped_type = field_type.strip()
                        if stripped_name and stripped_type:
                            fields.append((stripped_name, stripped_type))
            # Function pointer field: type (*name)(params) or type (*name[size])(params)
            elif (
                len(field_tokens) >= 5
                and any(field_tokens[i].type == TokenType.LPAREN and field_tokens[i + 1].type == TokenType.ASTERISK for i in range(len(field_tokens) - 1))
            ):
                # Find the opening parenthesis and asterisk pattern
                func_ptr_start = None
                for i in range(len(field_tokens) - 1):
                    if field_tokens[i].type == TokenType.LPAREN and field_tokens[i + 1].type == TokenType.ASTERISK:
                        func_ptr_start = i
                        break
                
                if func_ptr_start is not None:
                    # Extract the type (everything before the opening parenthesis)
                    type_tokens = field_tokens[:func_ptr_start]
                    field_type = " ".join(t.value for t in type_tokens)
                    
                    # Find the closing parenthesis after the function name
                    paren_count = 0
                    name_end = None
                    for i in range(func_ptr_start, len(field_tokens)):
                        if field_tokens[i].type == TokenType.LPAREN:
                            paren_count += 1
                        elif field_tokens[i].type == TokenType.RPAREN:
                            paren_count -= 1
                            if paren_count == 0 and i > func_ptr_start + 1:
                                name_end = i
                                break
                    
                    if name_end is not None:
                        # Extract function name (between * and closing parenthesis)
                        name_tokens = field_tokens[func_ptr_start + 2:name_end]
                        field_name = " ".join(t.value for t in name_tokens)
                        
                        # Extract the parameter list as part of the type
                        param_tokens = field_tokens[name_end + 1:]
                        param_type = " ".join(t.value for t in param_tokens)
                        
                        # Combine type and parameter list (without the function name in the type)
                        # The function name is already extracted as field_name, so we don't include it in the type
                        func_ptr_start_tokens = field_tokens[func_ptr_start:func_ptr_start + 2]  # ( *
                        func_ptr_end_tokens = field_tokens[name_end:name_end + 1]  # )
                        full_type = field_type + " " + " ".join(t.value for t in func_ptr_start_tokens) + " " + " ".join(t.value for t in func_ptr_end_tokens) + " " + param_type
                        
                        if (
                            field_name
                            and field_name.strip()
                            and full_type.strip()
                            and field_name not in ["[", "]", ";", "}"]
                        ):
                            stripped_name = field_name.strip()
                            stripped_type = full_type.strip()
                            if stripped_name and stripped_type:
                                fields.append((stripped_name, stripped_type))
            # Array field: type name [ size ]
            elif (
                len(field_tokens) >= 4
                and field_tokens[-3].type == TokenType.LBRACKET
                and field_tokens[-1].type == TokenType.RBRACKET
            ):
                field_name = field_tokens[-4].value
                # Fix: Properly format array type - preserve spaces between tokens
                type_tokens = field_tokens[:-4]
                field_type = " ".join(t.value for t in type_tokens) + "[" + field_tokens[-2].value + "]"
                if (
                    field_name
                    and field_name.strip()
                    and field_type.strip()
                    and field_name not in ["[", "]", ";", "}"]
                ):
                    # Additional validation to ensure we don't have empty strings
                    stripped_name = field_name.strip()
                    stripped_type = field_type.strip()
                    if stripped_name and stripped_type:
                        fields.append((stripped_name, stripped_type))
            else:
                # Regular field: type name
                field_name = field_tokens[-1].value
                field_type = " ".join(t.value for t in field_tokens[:-1])
                if (
                    field_name not in ["[", "]", ";", "}"]
                    and field_name
                    and field_name.strip()
                    and field_type.strip()
                ):
                    # Additional validation to ensure we don't have empty strings
                    stripped_name = field_name.strip()
                    stripped_type = field_type.strip()
                    if stripped_name and stripped_type:
                        fields.append((stripped_name, stripped_type))
        if pos < closing_brace_pos:
            pos += 1  # Skip semicolon
    return fields


def _extract_brace_content(field_tokens: List[Token]) -> str:
    """Extract content between braces from field tokens"""
    content = []
    brace_count = 0
    in_braces = False
    
    for token in field_tokens:
        if token.type == TokenType.LBRACE:
            brace_count += 1
            if brace_count == 1:
                in_braces = True
                continue
        elif token.type == TokenType.RBRACE:
            brace_count -= 1
            if brace_count == 0:
                in_braces = False
                break
        
        if in_braces:
            content.append(token.value)
    
    return " ".join(content)