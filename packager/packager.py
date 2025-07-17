import os
import shutil
from typing import List

def package_puml_files(output_dir: str, output_dir_packaged: str, project_roots: List[str]):
    """
    Copy and rename .puml files from output_dir to output_dir_packaged, renaming to CLS_<BASENAME>.puml (all caps),
    and structuring them in the same folder structure as the C files are found under the project roots.
    """
    # Map .puml files to their original .c file structure
    c_extensions = {'.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.hxx'}
    c_file_map = {}
    for project_root in project_roots:
        for root, _, files in os.walk(project_root):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in c_extensions:
                    rel_path = os.path.relpath(os.path.join(root, file), project_root)
                    base_no_ext = os.path.splitext(file)[0]
                    c_file_map[base_no_ext.lower()] = rel_path  # use lower for matching
    # Now process .puml files
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.puml'):
                base_no_ext = os.path.splitext(file)[0]
                new_puml_name = f'CLS_{base_no_ext.upper()}.puml'
                rel_path = c_file_map.get(base_no_ext.lower(), None)
                if rel_path:
                    rel_dir = os.path.dirname(rel_path)
                    dest_dir = os.path.join(output_dir_packaged, rel_dir)
                else:
                    dest_dir = output_dir_packaged
                os.makedirs(dest_dir, exist_ok=True)
                dest_path = os.path.join(dest_dir, new_puml_name)
                shutil.copy2(os.path.join(root, file), dest_path)
                print(f"Packaged {file} to {dest_path}") 