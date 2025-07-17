import os
from pathlib import Path
from typing import List

def find_c_files(root_path: str, recursive: bool = True) -> List[str]:
    """Find all C files in a directory"""
    c_files = []
    c_extensions = {'.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.hxx'}
    
    root = Path(root_path)
    
    if not root.exists():
        print(f"Error: Path {root_path} does not exist")
        return []
    
    if root.is_file():
        if root.suffix.lower() in c_extensions:
            return [str(root)]
        else:
            print(f"Error: {root_path} is not a C file")
            return []
    
    # Directory traversal
    pattern = "**/*" if recursive else "*"
    
    for file_path in root.glob(pattern):
        if file_path.is_file() and file_path.suffix.lower() in c_extensions:
            c_files.append(str(file_path))
    
    # Sort for consistent output
    c_files.sort()
    
    print(f"Found {len(c_files)} C files in {root_path}")
    return c_files 