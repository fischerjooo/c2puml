#!/usr/bin/env python3
from __future__ import annotations
import sys
import re
from pathlib import Path
from typing import List, Tuple


def find_quoted_value(lines: List[str], start_line: int, start_col: int) -> Tuple[str, int, int]:
    """
    Given lines and a starting position at the opening quote (") of a YAML value,
    return the full quoted value content (without quotes) and the end position
    (end_line, end_col) at the closing quote.
    Handles escaped quotes (\") and spans multiple lines.
    """
    buf: List[str] = []
    line_idx = start_line
    col_idx = start_col + 1  # skip opening quote
    escaped = False
    while line_idx < len(lines):
        line = lines[line_idx]
        while col_idx < len(line):
            ch = line[col_idx]
            if escaped:
                buf.append(ch)
                escaped = False
            else:
                if ch == '\\':
                    # keep the backslash in buffer so we can detect sequences like \\n later
                    buf.append('\\')
                    escaped = True
                elif ch == '"':
                    # closing quote
                    return ("".join(buf), line_idx, col_idx)
                else:
                    buf.append(ch)
            col_idx += 1
        # move to next line (include a real newline to preserve the raw scalar text formatting)
        buf.append('\n')
        line_idx += 1
        col_idx = 0
    raise ValueError(f"Unterminated quoted string starting at line {start_line+1}:{start_col+1}")


def rewrite_to_block_scalar(indent: str, key: str, raw_value: str) -> str | None:
    # Only rewrite if the raw_value contains literal backslash-n sequence
    if "\\n" not in raw_value:
        return None

    # Replace escaped quote sequences with normal quotes for block content
    text = raw_value.replace('\\"', '"')
    # Replace YAML line-continuations: backslash at end-of-line meaning join lines
    # These appear in the captured text as "\\\n[spaces]"
    text = re.sub(r"\\\r?\n[ \t]*", "", text)
    # Replace literal backslash-n with real newlines
    text = text.replace('\\n', '\n')

    # Build block scalar with two-space additional indent
    content_indent = indent + '  '
    content_lines = text.split('\n')
    # Ensure we do not add trailing spaces to empty lines
    body = "\n".join((f"{content_indent}{ln}" if ln != '' else f"{content_indent}") for ln in content_lines)
    return f"{indent}{key}: |\n{body}"


def process_file(path: Path) -> bool:
    lines = path.read_text(encoding='utf-8').splitlines()
    i = 0
    changed = False
    out_lines: List[str] = []

    while i < len(lines):
        line = lines[i]
        # Find a colon that starts a value immediately followed by optional spaces and a double-quote
        # We also capture indentation and key up to the colon (avoid mapping values with inline maps)
        # Simple scan for first colon not within quotes
        in_quote = False
        esc = False
        colon_pos = -1
        for idx, ch in enumerate(line):
            if in_quote:
                if esc:
                    esc = False
                elif ch == '\\':
                    esc = True
                elif ch == '"':
                    in_quote = False
            else:
                if ch == '"':
                    in_quote = True
                elif ch == ':':
                    colon_pos = idx
                    break
        if colon_pos == -1:
            out_lines.append(line)
            i += 1
            continue

        # Determine indentation and key
        before = line[:colon_pos]
        after = line[colon_pos+1:]
        indent_len = len(before) - len(before.lstrip(' '))
        indent = before[:indent_len]
        key = before[indent_len:]
        # If value starts with spaces then a double-quote, we can parse it as a quoted scalar
        j = 0
        while j < len(after) and after[j] in ' \t':
            j += 1
        if j < len(after) and after[j] == '"':
            # parse quoted value across lines
            try:
                raw_value, end_line, end_col = find_quoted_value(lines, i, colon_pos + 1 + j)
            except ValueError:
                # Fallback: leave as is
                out_lines.append(line)
                i += 1
                continue
            replacement = rewrite_to_block_scalar(indent, key.strip(), raw_value)
            if replacement is None:
                # No change; emit original lines slice
                out_lines.append(line)
                # plus any continuation lines within the quoted scalar untouched
                # We need to append the full original joined segment
                k = i + 1
                while k <= end_line:
                    out_lines.append(lines[k])
                    k += 1
                i = end_line + 1
                continue
            # We have a block scalar replacement. Append it and skip original spanned lines.
            out_lines.append(replacement)
            changed = True
            i = end_line + 1
            # Skip any trailing content on the closing quote line (unlikely in our YAML)
            continue
        else:
            # Not a double-quoted scalar value; copy line and continue
            out_lines.append(line)
            i += 1

    if changed:
        Path(path).write_text("\n".join(out_lines) + "\n", encoding='utf-8')
    return changed


def main() -> int:
    root = Path('/workspace/tests')
    files = sorted(root.rglob('*.yml'))
    changed = 0
    for f in files:
        if process_file(f):
            print(f"Reformatted: {f}")
            changed += 1
    print(f"Done. Files changed: {changed} / {len(files)}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())