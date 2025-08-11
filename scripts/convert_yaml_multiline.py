#!/usr/bin/env python3
import sys
import os
from typing import List, Any
import yaml


class BlockStyleDumper(yaml.SafeDumper):
    pass


def str_presenter(dumper: yaml.Dumper, data: str):
    style = '|' if ('\n' in data or '\r' in data) else None
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style=style)


BlockStyleDumper.add_representer(str, str_presenter)


def convert_node(node: Any) -> Any:
    if isinstance(node, list):
        return [convert_node(x) for x in node]
    if isinstance(node, dict):
        return {k: convert_node(v) for k, v in node.items()}
    return node


def convert_file(path: str) -> bool:
    with open(path, 'r', encoding='utf-8') as f:
        original = f.read()

    docs = list(yaml.safe_load_all(original))
    converted_docs = [convert_node(d) for d in docs]

    new_content = yaml.dump_all(
        converted_docs,
        Dumper=BlockStyleDumper,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=1000,
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