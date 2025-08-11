#!/usr/bin/env python3
import os, re, json

ROOT = "/workspace/tests"

def collect_yaml_ids(root: str):
    yaml_ids = {}
    for dirpath, _, files in os.walk(root):
        for fname in files:
            if fname.endswith((".yml", ".yaml")):
                base = os.path.splitext(fname)[0]
                m = re.match(r"test[_-](.+)$", base)
                if not m:
                    continue
                test_id = m.group(1)
                yaml_ids.setdefault(test_id, []).append(os.path.join(dirpath, fname))
    return yaml_ids

def collect_py_refs(root: str):
    id_to_py = {}
    patterns = [
        re.compile(r"run_test\(\s*\"([^\"]+)\"\s*\)"),
        re.compile(r"load_test_data\(\s*\"([^\"]+)\"\s*\)"),
        re.compile(r"test_id\s*=\s*\"([^\"]+)\""),
    ]
    py_files = []
    for dirpath, _, files in os.walk(root):
        for fname in files:
            if fname.endswith(".py"):
                py_files.append(os.path.join(dirpath, fname))
    for path in py_files:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                content = fh.read()
        except Exception:
            continue
        refs = set()
        for rgx in patterns:
            refs.update(rgx.findall(content))
        for tid in refs:
            id_to_py.setdefault(tid, set()).add(path)
    return id_to_py

def main():
    yaml_ids = collect_yaml_ids(ROOT)
    id_to_py = collect_py_refs(ROOT)

    orphans = sorted((tid, sorted(paths)) for tid, paths in yaml_ids.items() if tid not in id_to_py)
    missing_yaml = sorted((tid, sorted(paths)) for tid, paths in id_to_py.items() if tid not in yaml_ids)
    multiple_refs = []
    for tid, paths in id_to_py.items():
        if tid in yaml_ids and len(set(paths)) > 1:
            multiple_refs.append((tid, sorted(set(paths))))
    multiple_refs.sort()

    summary = {
        "yaml_files": sum(len(v) for v in yaml_ids.values()),
        "unique_yaml_ids": len(yaml_ids),
        "referenced_ids": len(id_to_py),
        "orphans_count": len(orphans),
        "missing_yaml_count": len(missing_yaml),
        "multiple_refs_count": len(multiple_refs),
    }
    print(json.dumps(summary, indent=2))
    print("\nORPHANS")
    for tid, files in orphans:
        print(f"- {tid}: {', '.join(files)}")
    print("\nMULTI_REFS")
    for tid, files in multiple_refs:
        print(f"- {tid}: {', '.join(files)}")
    print("\nMISSING_YAML")
    for tid, files in missing_yaml:
        print(f"- {tid}: {', '.join(files)}")

if __name__ == "__main__":
    main()