#!/usr/bin/env python3
import sys
import os
from typing import List, Any
import yaml


def str_presenter(dumper: yaml.Dumper, data: str):
    """Represent strings: use block style '|' for multiline content."""
    style = '|' if ('\n' in data or '\r' in data) else None
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style=style)


yaml.representer.SafeRepresenter.add_representer(str, str_presenter)


def convert_document(doc: Any) -> Any:
    """Walk the loaded YAML document and normalize multiline strings.

    For our use-case, simply returning the same structure is fine since
    the representer ensures block scalars for multiline strings on dump.
    """
    return doc


def convert_file(path: str) -> bool:
    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()

    # Load all YAML documents
    docs = list(yaml.safe_load_all(original))

    # Convert documents (no structural change; representer handles style)
    converted_docs = [convert_document(d) for d in docs]

    # Dump back to YAML with block scalars for multiline strings
    new_content = yaml.dump_all(
        converted_docs,
        Dumper=yaml.SafeDumper,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=1000,  # avoid wrapping lines unnecessarily
    )

    if new_content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print("Usage: convert_yaml_multiline.py <file1.yml> [file2.yml ...]", file=sys.stderr)
        return 2

    status = 0
    for p in argv[1:]:
        ap = os.path.abspath(p)
        if not os.path.exists(ap):
            print(f"Skipping (not found): {ap}")
            continue
        try:
            changed = convert_file(ap)
            print(f"Converted: {ap}" if changed else f"No change: {ap}")
        except Exception as e:
            print(f"Error converting {ap}: {e}", file=sys.stderr)
            status = 1

    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv))