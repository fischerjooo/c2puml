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

