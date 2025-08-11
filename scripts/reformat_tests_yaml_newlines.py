#!/usr/bin/env python3
import sys
import os
from pathlib import Path
from typing import Any

try:
    from ruamel.yaml import YAML
    from ruamel.yaml.comments import CommentedMap, CommentedSeq
    from ruamel.yaml.scalarstring import (
        DoubleQuotedScalarString,
        SingleQuotedScalarString,
        LiteralScalarString,
        FoldedScalarString,
    )
except Exception as e:
    print("Error: ruamel.yaml is required. Install with: pip install ruamel.yaml", file=sys.stderr)
    raise


def transform_scalar(value: Any) -> Any:
    # Only convert double-quoted scalars that contain the literal backslash-n sequence
    if isinstance(value, DoubleQuotedScalarString) and "\\n" in value:
        # Replace the escape sequences with actual newlines and switch style to literal block scalar
        new_text = value.replace("\\n", "\n")
        return LiteralScalarString(new_text)

    # Do NOT touch single-quoted scalars; they likely intend literal backslashes
    if isinstance(value, SingleQuotedScalarString):
        return value

    # Recurse into collections
    if isinstance(value, (CommentedMap, dict)):
        for k in list(value.keys()):
            value[k] = transform_scalar(value[k])
        return value
    if isinstance(value, (CommentedSeq, list, tuple)):
        for i in range(len(value)):
            value[i] = transform_scalar(value[i])
        return value

    return value


def process_file(path: Path) -> bool:
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)

    # Load all YAML documents
    with path.open("r", encoding="utf-8") as f:
        docs = list(yaml.load_all(f))

    changed = False
    new_docs = []
    for doc in docs:
        before = str(doc)
        transformed = transform_scalar(doc)
        after = str(transformed)
        if before != after:
            changed = True
        new_docs.append(transformed)

    if changed:
        with path.open("w", encoding="utf-8", newline="\n") as f:
            yaml.dump_all(new_docs, f)
    return changed


def main(argv: list[str]) -> int:
    root = Path("/workspace/tests")
    if not root.exists():
        print(f"Tests directory not found: {root}", file=sys.stderr)
        return 1

    yml_files = sorted(root.rglob("*.yml"))
    if not yml_files:
        print("No YAML files found under tests/", file=sys.stderr)
        return 0

    changed_count = 0
    for yml in yml_files:
        try:
            if process_file(yml):
                changed_count += 1
                print(f"Reformatted: {yml}")
        except Exception as e:
            print(f"Failed to process {yml}: {e}", file=sys.stderr)
            return 2

    print(f"Done. Files changed: {changed_count} / {len(yml_files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))