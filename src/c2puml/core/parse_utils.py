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


def normalize_dim_value(dim: str) -> str:
    """Normalize numeric dimension tokens like 5U/6UL to plain digits; keep expressions as-is."""
    m = re.match(r"\s*(\d+)", dim)
    return m.group(1) if m else dim


def normalize_type_and_name_for_arrays(base_type: str, name: str) -> tuple[str, str]:
    """Normalize cases where array dimensions are attached to the name or
    accidentally glued to the type.

    Handles typical forms:
    - name carries dims:  base_type, name="var[2U][3]" -> (base_type[2][3], "var")
    - type accidentally includes name+dims (parser edge):
      base_type="T var[2", name="U" -> (T[2], "var")
    - type already has dims: base_type="T[2]", name="var" -> unchanged
    """
    # First, the straightforward case: dimensions present on the name
    if name and '[' in name:
        dims = re.findall(r"\[(.*?)\]", name)
        if dims:
            dims = [normalize_dim_value(d) for d in dims]
            clean_name = re.split(r"\[", name, 1)[0].strip()
            type_with_dims = join_type_with_dims(base_type, dims)
            return type_with_dims, clean_name

    # If name doesn't have dims but base_type looks like it ends with
    # "identifier [ <expr>" (possibly with a split numeric suffix like 'U' in name),
    # try to pull dims off the end of base_type and extract the real name.
    # This guards against tokenizer/parse edge cases in some codebases.
    trailing_dim_match = re.search(r"\[\s*([^\]]*)\s*$", base_type)
    if trailing_dim_match:
        # Split base_type into prefix (before name), name candidate, and leftover before '['
        before_bracket = base_type[: trailing_dim_match.start()].rstrip()
        # The candidate variable name is the last identifier in before_bracket
        m_name = re.search(r"([A-Za-z_][A-Za-z0-9_]*)\s*$", before_bracket)
        if m_name:
            var_name_candidate = m_name.group(1)
            # True type is everything before the candidate name
            true_base_type = before_bracket[: m_name.start()].rstrip()
            # Normalize the dimension value; if the current 'name' is just a numeric suffix (e.g. 'U', 'UL'),
            # append it to the dim string for normalization purposes
            dim_raw = (trailing_dim_match.group(1) or "").strip()
            suffix = name.strip() if name and re.fullmatch(r"[uUlL]+", name.strip()) else ""
            # If we have a split numeric suffix like 'U', reconstruct two dims:
            # first without suffix, second with suffix preserved -> e.g., [2][2U]
            if var_name_candidate and dim_raw:
                dims_out: list[str] = []
                # First dimension without suffix normalization in source code often is separate;
                # we normalize numeric tokens (2U -> 2) only for the first copy.
                dims_out.append(normalize_dim_value(dim_raw))
                if suffix:
                    dims_out.append(f"{dim_raw}{suffix}")
                fixed_type = join_type_with_dims(true_base_type or base_type, dims_out)
                fixed_name = var_name_candidate
                return fixed_type, fixed_name

    return base_type, name

