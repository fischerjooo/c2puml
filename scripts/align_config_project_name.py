#!/usr/bin/env python3
from pathlib import Path
import re

DOC_SEP = '\n---\n'
ASSERTIONS_RE = re.compile(r'^assertions\s*:\s*$', re.M)
PROJECT_NAME_RE = re.compile(r'project_name\s*:\s*([A-Za-z0-9_\-]+)')
CONFIG_DOC_RE = re.compile(r'^config\.json\s*:\s*\|\s*$', re.M)
JSON_PROJECT_RE = re.compile(r'("project_name"\s*:\s*")([^"]*)(")')


def update_config_project_name(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')
    parts = text.split(DOC_SEP)
    expected_name = None
    config_idx = None
    # Find expected project_name from assertions doc
    for idx, part in enumerate(parts):
        if ASSERTIONS_RE.search(part):
            m = PROJECT_NAME_RE.search(part)
            if m:
                expected_name = m.group(1)
                break
    if not expected_name:
        return False
    # Find config.json doc
    for idx, part in enumerate(parts):
        if CONFIG_DOC_RE.search(part):
            config_idx = idx
            break
    if config_idx is None:
        return False
    # Update JSON project_name in that doc
    def repl(match: re.Match) -> str:
        return f'{match.group(1)}{expected_name}{match.group(3)}'
    new_part = JSON_PROJECT_RE.sub(repl, parts[config_idx])
    if new_part == parts[config_idx]:
        return False
    parts[config_idx] = new_part
    new_text = DOC_SEP.join(parts)
    path.write_text(new_text if new_text.endswith('\n') else new_text + '\n', encoding='utf-8')
    return True


def main() -> int:
    root = Path('/workspace/tests')
    changed = 0
    for yml in sorted(root.rglob('*.yml')):
        try:
            if update_config_project_name(yml):
                print(f'Updated project_name in: {yml}')
                changed += 1
        except Exception as e:
            print(f'Failed to process {yml}: {e}')
            return 2
    print(f'Done. Updated {changed} files.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())