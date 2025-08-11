#!/usr/bin/env python3
import os
import re
import sys
from typing import Dict, List, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TESTS_DIR = os.path.join(ROOT, 'tests')

ID_PATTERN = re.compile(r"test[_-](.+)$")
PY_RUN = re.compile(r"run_test\(\s*\"([^\"]+)\"\s*\)")
PY_LOAD = re.compile(r"load_test_data\(\s*\"([^\"]+)\"\s*\)")
PY_ASSIGN = re.compile(r"test_id\s*=\s*\"([^\"]+)\"")


def gather_yaml_ids() -> Dict[str, List[str]]:
    mapping: Dict[str, List[str]] = {}
    for dirpath, _, files in os.walk(TESTS_DIR):
        for fname in files:
            if not fname.endswith((".yml", ".yaml")):
                continue
            base = os.path.splitext(fname)[0]
            m = ID_PATTERN.match(base)
            if not m:
                continue
            test_id = m.group(1)
            mapping.setdefault(test_id, []).append(os.path.join(dirpath, fname))
    return mapping


def gather_py_refs() -> Dict[str, Set[str]]:
    refs: Dict[str, Set[str]] = {}
    for dirpath, _, files in os.walk(TESTS_DIR):
        for fname in files:
            if not fname.endswith('.py'):
                continue
            fpath = os.path.join(dirpath, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as fh:
                    content = fh.read()
            except Exception:
                continue
            ids = set()
            ids.update(PY_RUN.findall(content))
            ids.update(PY_LOAD.findall(content))
            ids.update(PY_ASSIGN.findall(content))
            for tid in ids:
                refs.setdefault(tid, set()).add(fpath)
    return refs


def py_to_expected_yaml_ids(py_path: str, all_yaml_ids: Dict[str, List[str]]) -> Set[str]:
    """For a given python test file, infer the set of YAML IDs it should reference.
    Rule: For a python file named tests/<cat>/test_<base>.py, collect YAMLs in same dir
    whose filenames start with test_<base> (exact or with suffixes). Return their ids.
    """
    dirpath = os.path.dirname(py_path)
    base_py = os.path.splitext(os.path.basename(py_path))[0]
    if not base_py.startswith('test_'):
        return set()
    base = base_py  # e.g., test_124_gen_newfmt
    expected_ids: Set[str] = set()
    for fname in os.listdir(dirpath):
        if not fname.endswith(('.yml', '.yaml')):
            continue
        yaml_base = os.path.splitext(fname)[0]
        if yaml_base == base or yaml_base.startswith(base + '_'):
            m = ID_PATTERN.match(yaml_base)
            if m:
                expected_ids.add(m.group(1))
    return expected_ids


def main() -> int:
    yaml_ids = gather_yaml_ids()
    py_refs = gather_py_refs()

    errors: List[str] = []

    # 1) Each YAML id must be referenced by exactly one Python file
    for tid, files in yaml_ids.items():
        refs = py_refs.get(tid, set())
        if len(refs) == 0:
            errors.append(f"ORPHAN YAML: id '{tid}' not referenced by any Python test (files: {', '.join(files)})")
        elif len(refs) > 1:
            errors.append(f"MULTI-REFERENCED YAML: id '{tid}' referenced by multiple Python tests: {', '.join(sorted(refs))}")

    # 2) Each Python test file must reference all 'similar-named' YAMLs in same directory
    # Build quick map id -> referencing files
    for dirpath, _, files in os.walk(TESTS_DIR):
        for fname in files:
            if not fname.endswith('.py'):
                continue
            py_path = os.path.join(dirpath, fname)
            expected_ids = py_to_expected_yaml_ids(py_path, yaml_ids)
            if not expected_ids:
                continue
            # Collect actual ids referenced by this python file
            try:
                with open(py_path, 'r', encoding='utf-8') as fh:
                    content = fh.read()
            except Exception:
                continue
            actual_ids = set(PY_RUN.findall(content)) | set(PY_LOAD.findall(content)) | set(PY_ASSIGN.findall(content))
            missing = expected_ids - actual_ids
            if missing:
                errors.append(f"PY MISSING YAML REFS: {py_path} does not reference ids: {', '.join(sorted(missing))}")

    if errors:
        print("Test mapping validation failed:\n" + "\n".join(errors))
        return 1
    print("Test mapping validation passed.")
    return 0


if __name__ == '__main__':
    sys.exit(main())