#!/usr/bin/env python3
from pathlib import Path
import re

has_config_pattern = re.compile(r'^\s*config\.json\s*:\s*\|', re.M)
source_files_doc_pattern = re.compile(r'^source_files\s*:\s*$', re.M)

DEFAULT_CONFIG = (
    'config.json: |\n'
    '  {\n'
    '    "project_name": "auto_test",\n'
    '    "source_folders": ["."],\n'
    '    "output_dir": "./output",\n'
    '    "recursive_search": true\n'
    '  }\n'
)

def ensure_config(path: Path) -> bool:
    text = path.read_text(encoding='utf-8')
    if has_config_pattern.search(text):
        return False
    # Only add if the file defines source_files
    if not source_files_doc_pattern.search(text):
        return False
    # Insert after the first document following source_files doc
    parts = text.split('\n---\n')
    inserted = False
    for idx, part in enumerate(parts):
        if source_files_doc_pattern.search(part):
            # Insert a new doc after this index
            parts.insert(idx + 1, DEFAULT_CONFIG)
            inserted = True
            break
    if not inserted:
        return False
    # Rejoin with document separators
    new_text = ('\n---\n').join(parts)
    path.write_text(new_text if new_text.endswith('\n') else new_text + '\n', encoding='utf-8')
    return True


def main() -> int:
    root = Path('/workspace/tests')
    changed = 0
    for yml in sorted(root.rglob('*.yml')):
        try:
            if ensure_config(yml):
                print(f'Inserted default config.json in: {yml}')
                changed += 1
        except Exception as e:
            print(f'Failed to process {yml}: {e}')
            return 2
    print(f'Done. Default config inserted in {changed} files.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())