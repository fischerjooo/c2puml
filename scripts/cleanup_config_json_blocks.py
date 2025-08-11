#!/usr/bin/env python3
import re
from pathlib import Path

CONFIG_KEY_PATTERN = re.compile(r'^(?P<indent>\s*)config\.json:\s*\|\s*$')

# Joins sequences produced by YAML-escaped backslash-newline into nothing
JOIN_CONTINUATIONS = re.compile(r"\\\r?\n[ \t]*")

# Strip stray leading backslashes/spaces before JSON tokens
LEADING_STRAY_BSLASH = re.compile(r'^(?P<indent>\s*)\\\s*')
# Remove single backslash sitting between whitespace and a JSON token start (" { [ or alpha)
INLINE_STRAY_BSLASH = re.compile(r'(?P<pre>\s)\\\s*(?=(\"|\{|\[|[A-Za-z]))')


def normalize_lines(raw: str) -> str:
    # Undo backslash-newline continuations
    raw = JOIN_CONTINUATIONS.sub("", raw)
    # Unescape escaped quotes inside strings for clarity (" -> ")
    raw = raw.replace('\\"', '"')
    # Normalize stray backslashes
    norm_lines = []
    for ln in raw.split('\n'):
        ln2 = LEADING_STRAY_BSLASH.sub(lambda m: m.group('indent'), ln)
        ln2 = INLINE_STRAY_BSLASH.sub(lambda m: m.group('pre'), ln2)
        norm_lines.append(ln2)
    return "\n".join(norm_lines)


def fix_block(block_lines: list[str], content_indent: str) -> list[str]:
    # Remove the leading content indent from each line
    raw = "\n".join(line[len(content_indent):] if line.startswith(content_indent) else line for line in block_lines)
    raw = normalize_lines(raw)
    # Split back into lines with original content indentation
    fixed_lines = [content_indent + ln if ln != '' else content_indent for ln in raw.split('\n')]
    return fixed_lines


def process_file(path: Path) -> bool:
    lines = path.read_text(encoding='utf-8').splitlines()
    out: list[str] = []
    i = 0
    changed = False
    while i < len(lines):
        m = CONFIG_KEY_PATTERN.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        # Found a config.json block start
        out.append(lines[i])
        i += 1
        content_lines: list[str] = []
        # Determine content indent from the next line
        if i < len(lines) and lines[i].strip() != '---':
            next_line = lines[i]
            content_indent_len = len(next_line) - len(next_line.lstrip(' '))
            content_indent = next_line[:content_indent_len]
        else:
            content_indent = m.group('indent') + '  '
        # Collect until a line with less indent or EOF or a document separator
        while i < len(lines):
            if lines[i].startswith(content_indent) or lines[i].strip() == '':
                content_lines.append(lines[i])
                i += 1
            else:
                break
        fixed = fix_block(content_lines, content_indent)
        if fixed != content_lines:
            changed = True
        out.extend(fixed)
    if changed:
        path.write_text("\n".join(out) + "\n", encoding='utf-8')
    return changed


def main() -> int:
    root = Path('/workspace/tests')
    changed = 0
    total = 0
    for yml in sorted(root.rglob('*.yml')):
        total += 1
        if process_file(yml):
            print(f"Cleaned: {yml}")
            changed += 1
    print(f"Done. Files cleaned: {changed} / {total}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())