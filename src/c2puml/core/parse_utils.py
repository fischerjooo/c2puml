#!/usr/bin/env python3
"""
Shared parsing utilities for the C to PlantUML converter.

Centralizes small but widely used helpers so parser/tokenizer code can
delegate to a single source of truth, reducing duplication and divergence.
"""

from __future__ import annotations

import re
from typing import List, Optional


def clean_type_string(type_str: str) -> str:
    """Clean type string by removing newlines and normalizing whitespace."""
    if not type_str:
        return type_str
    cleaned = type_str.replace('\n', ' ')
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.strip()
    return cleaned


def clean_value_string(value_str: str) -> str:
    """Clean value string by removing excessive whitespace and newlines."""
    if not value_str:
        return value_str
    cleaned = value_str.replace('\n', ' ')
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = cleaned.strip()
    cleaned = re.sub(r"\s*\{\s*", "{", cleaned)
    cleaned = re.sub(r"\s*\}\s*", "}", cleaned)
    cleaned = re.sub(r"\s*,\s*", ", ", cleaned)
    cleaned = re.sub(r"\s*&\s*", "&", cleaned)
    return cleaned


def fix_array_bracket_spacing(type_str: str) -> str:
    """Fix spacing around array brackets in type strings."""
    type_str = clean_type_string(type_str)
    type_str = re.sub(r"\s*\[\s*", "[", type_str)
    type_str = re.sub(r"\s*\]\s*", "]", type_str)
    return type_str


def fix_pointer_spacing(type_str: str) -> str:
    """Fix spacing around pointer asterisks in type strings."""
    # Fix double pointer spacing: "type * *" -> "type **"
    type_str = re.sub(r"\*\s+\*", "**", type_str)
    # Fix triple pointer spacing: "type * * *" -> "type ***"
    type_str = re.sub(r"\*\s+\*\s+\*", "***", type_str)
    return type_str


def find_matching_brace(tokens, start_pos: int) -> Optional[int]:
    """Find a matching closing brace in a token list starting at an opening brace.

    Mirrors StructureFinder._find_matching_brace to allow reuse in other
    components without duplicating logic.
    """
    # Import locally to avoid circular dependencies at module import time
    from .parser_tokenizer import TokenType

    if start_pos >= len(tokens) or tokens[start_pos].type != TokenType.LBRACE:
        return None

    depth = 1
    pos = start_pos + 1
    while pos < len(tokens) and depth > 0:
        if tokens[pos].type == TokenType.LBRACE:
            depth += 1
        elif tokens[pos].type == TokenType.RBRACE:
            depth -= 1
        pos += 1

    return pos - 1 if depth == 0 else None


def collect_array_dimensions_from_tokens(tokens, start_index: int) -> tuple[list[str], int]:
    """Collect one or more array dimension groups starting at start_index.

    Expects tokens[start_index] to be a LBRACKET. Returns (dims, next_index)
    where dims is a list of strings (each the content between brackets), and
    next_index is the index after the last closing bracket.
    """
    from .parser_tokenizer import TokenType

    dims: list[str] = []
    i = start_index
    while i < len(tokens) and tokens[i].type == TokenType.LBRACKET:
        j = i + 1
        content_parts: list[str] = []
        while j < len(tokens) and tokens[j].type != TokenType.RBRACKET:
            if tokens[j].type not in (TokenType.WHITESPACE, TokenType.COMMENT, TokenType.NEWLINE):
                content_parts.append(tokens[j].value)
            j += 1
        # Join with spaces to preserve readability for expressions
        dim_str = " ".join(content_parts).strip()
        dims.append(dim_str)
        # Move past the closing bracket if present
        i = j + 1 if j < len(tokens) and tokens[j].type == TokenType.RBRACKET else j
    return dims, i


def join_type_with_dims(base_type: str, dims: list[str]) -> str:
    """Append collected array dimensions to a base type and normalize spacing."""
    if not dims:
        return base_type
    type_with_dims = base_type + "".join(f"[{d}]" for d in dims)
    return fix_array_bracket_spacing(type_with_dims)

