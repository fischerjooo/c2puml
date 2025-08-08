#!/usr/bin/env python3
"""
Analyze orphan YAML files without corresponding Python test files
"""

import os
import glob

def analyze_orphan_files():
    """Find YAML files without corresponding Python test files"""
    
    # Find all YAML test files
    yaml_files = glob.glob("tests/**/*.yml", recursive=True)
    yaml_basenames = set()
    for yaml_file in yaml_files:
        # Get basename without extension
        basename = os.path.splitext(os.path.basename(yaml_file))[0]
        yaml_basenames.add((basename, yaml_file))
    
    # Find all Python test files
    py_files = glob.glob("tests/**/test_*.py", recursive=True)
    py_basenames = set()
    for py_file in py_files:
        # Get basename without extension
        basename = os.path.splitext(os.path.basename(py_file))[0]
        py_basenames.add((basename, py_file))
    
    print("=== Analysis of Test File Pairing ===\n")
    
    # Find orphan YAML files (YAML without corresponding Python)
    orphan_yamls = []
    for yaml_basename, yaml_path in yaml_basenames:
        # Check if there's a corresponding Python file
        has_python_pair = any(py_basename == yaml_basename for py_basename, _ in py_basenames)
        if not has_python_pair:
            orphan_yamls.append((yaml_basename, yaml_path))
    
    # Find orphan Python files (Python without corresponding YAML)
    orphan_pythons = []
    for py_basename, py_path in py_basenames:
        # Check if there's a corresponding YAML file
        has_yaml_pair = any(yaml_basename == py_basename for yaml_basename, _ in yaml_basenames)
        if not has_yaml_pair:
            orphan_pythons.append((py_basename, py_path))
    
    print(f"📊 Summary:")
    print(f"   Total YAML files: {len(yaml_basenames)}")
    print(f"   Total Python files: {len(py_basenames)}")
    print(f"   Orphan YAML files: {len(orphan_yamls)}")
    print(f"   Orphan Python files: {len(orphan_pythons)}")
    print()
    
    if orphan_yamls:
        print("🟡 Orphan YAML files (no corresponding .py file):")
        for basename, path in sorted(orphan_yamls):
            print(f"   - {basename}.yml → {path}")
        print()
    
    if orphan_pythons:
        print("🟡 Orphan Python files (no corresponding .yml file):")
        for basename, path in sorted(orphan_pythons):
            print(f"   - {basename}.py → {path}")
        print()
    
    # Analyze patterns in orphan YAML files
    if orphan_yamls:
        print("🔍 Analysis of orphan YAML patterns:")
        
        # Group by likely test categories
        debug_yamls = [y for y in orphan_yamls if 'debug' in y[0]]
        parser_yamls = [y for y in orphan_yamls if 'parser' in y[0]]
        function_yamls = [y for y in orphan_yamls if 'function' in y[0]]
        other_yamls = [y for y in orphan_yamls if not any(x in y[0] for x in ['debug', 'parser', 'function'])]
        
        if debug_yamls:
            print(f"   Debug tests: {len(debug_yamls)}")
            for basename, _ in debug_yamls:
                print(f"     - {basename}")
        
        if parser_yamls:
            print(f"   Parser tests: {len(parser_yamls)}")
            for basename, _ in parser_yamls:
                print(f"     - {basename}")
        
        if function_yamls:
            print(f"   Function tests: {len(function_yamls)}")
            for basename, _ in function_yamls:
                print(f"     - {basename}")
        
        if other_yamls:
            print(f"   Other tests: {len(other_yamls)}")
            for basename, _ in other_yamls:
                print(f"     - {basename}")

if __name__ == "__main__":
    analyze_orphan_files()