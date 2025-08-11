#!/usr/bin/env python3
import re
from pathlib import Path

# Pattern to match lines like: key: "..." where the value is a single-line double-quoted scalar
LINE_PATTERN = re.compile(r'^(?P<indent>\s*)(?P<key>[^:\n]+?):\s*"(?P<value>.*)"\s*$')
# Replace unescaped \n (not preceded by backslash) with a real newline
UNESCAPED_NEWLINE = re.compile(r'(?<!\\)\\n')


def convert_line_to_block(indent: str, key: str, value: str) -> str | None:
    # Only proceed if the value contains at least one unescaped \n
    if not UNESCAPED_NEWLINE.search(value):
        return None

    # Convert YAML-escaped quotes (\") to normal quotes for block scalar content
    # Keep escaped backslash-n (\\n) intact for C string literals
    text = value
    text = text.replace('\\"', '"')
    text = UNESCAPED_NEWLINE.sub('\n', text)

    # Emit block scalar with two-space indent for content
    content_indent = indent + '  '
    lines = text.split('\n')
    block_lines = [f"{content_indent}{ln}" if ln != '' else f"{content_indent}" for ln in lines]
    return f"{indent}{key}: |\n" + "\n".join(block_lines)


def process_file(path: Path) -> bool:
    original = path.read_text(encoding='utf-8')
    lines = original.splitlines()

    changed_any = False
    new_lines: list[str] = []

    for line in lines:
        m = LINE_PATTERN.match(line)
        if m:
            repl = convert_line_to_block(m.group('indent'), m.group('key'), m.group('value'))
            if repl is not None:
                new_lines.append(repl)
                changed_any = True
                continue
        new_lines.append(line)

    if changed_any:
        # Ensure final file ends with a newline
        path.write_text("\n".join(new_lines) + "\n", encoding='utf-8')
    return changed_any


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