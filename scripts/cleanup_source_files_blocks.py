#!/usr/bin/env python3
import re
from pathlib import Path
from typing import List

SOURCE_FILES_START = re.compile(r'^source_files:\s*$')
BLOCK_KEY = re.compile(r'^(?P<indent>\s+)(?P<fname>[^:\n]+?):\s*\|\s*$')

# Patterns to repair 'n' artifacts into real newlines for common C constructs
REPAIRS: List[tuple[re.Pattern, str]] = [
    (re.compile(r'n#'), '\n#'),
    (re.compile(r'n#include'), '\n#include'),
    (re.compile(r'n#endif'), '\n#endif'),
    (re.compile(r'\)\s*n'), ')\n'),
    (re.compile(r'"\);\s*n'), '";\n'),
    (re.compile(r';\s*n'), ';\n'),
    (re.compile(r'\{\s*n'), '{\n'),
    (re.compile(r'n\s*\}'), '\n}'),
    (re.compile(r'nint\b'), '\nint'),
    (re.compile(r'nvoid\b'), '\nvoid'),
    (re.compile(r'nreturn\b'), '\nreturn'),
    (re.compile(r'nenum\b'), '\nenum'),
    (re.compile(r'nstruct\b'), '\nstruct'),
    (re.compile(r'nextern\b'), '\nextern'),
    (re.compile(r'nstatic\b'), '\nstatic'),
    (re.compile(r'\bn\n'), '\n'),  # collapse lone n at line end
]

# Remove EOL backslash (likely from broken continuations)
EOL_BACKSLASH = re.compile(r'[ \t]*\\\r?$')


def fix_content(text: str) -> str:
    # Remove lines that are just backslash or whitespace + backslash
    lines = text.split('\n')
    cleaned_lines = [ln for ln in lines if not ln.strip() == '\\']
    text = '\n'.join(cleaned_lines)

    # Remove end-of-line backslashes
    text = '\n'.join(EOL_BACKSLASH.sub('', ln) for ln in text.split('\n'))

    # Apply repairs
    for pat, repl in REPAIRS:
        text = pat.sub(repl, text)

    return text


def process_file(path: Path) -> bool:
    lines = path.read_text(encoding='utf-8').splitlines()
    out: List[str] = []
    i = 0
    changed = False

    while i < len(lines):
        out.append(lines[i])
        if SOURCE_FILES_START.match(lines[i]):
            i += 1
            # Inside source_files mapping until next '---' or EOF
            while i < len(lines) and not lines[i].startswith('---'):
                m = BLOCK_KEY.match(lines[i])
                if m:
                    out.append(lines[i])
                    block_indent = m.group('indent') + '  '
                    i += 1
                    block_lines: List[str] = []
                    while i < len(lines):
                        if lines[i].startswith(block_indent) or lines[i].strip() == '':
                            block_lines.append(lines[i])
                            i += 1
                        else:
                            break
                    # Strip indent, fix, re-indent
                    stripped = '\n'.join(ln[len(block_indent):] if ln.startswith(block_indent) else '' for ln in block_lines)
                    fixed = fix_content(stripped)
                    if fixed != stripped:
                        changed = True
                    for ln in fixed.split('\n'):
                        out.append(block_indent + ln if ln != '' else block_indent)
                    continue
                else:
                    i += 1
                    continue
        i += 1

    if changed:
        path.write_text('\n'.join(out) + '\n', encoding='utf-8')
    return changed


def main() -> int:
    root = Path('/workspace/tests')
    changed = 0
    total = 0
    for yml in sorted(root.rglob('*.yml')):
        total += 1
        if process_file(yml):
            print(f'Fixed source_files in: {yml}')
            changed += 1
    print(f'Done. Files fixed: {changed} / {total}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())