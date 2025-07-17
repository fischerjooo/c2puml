import argparse
import os
import sys
import json
from typing import List, Optional, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == "__main__":
    from c_to_plantuml.parsers.c_parser import CParser
    from c_to_plantuml.generators.plantuml_generator import PlantUMLGenerator
    from c_to_plantuml.utils.file_utils import find_c_files
    from c_to_plantuml.models.c_structures import Function
else:
    from .parsers.c_parser import CParser
    from .generators.plantuml_generator import PlantUMLGenerator
    from .utils.file_utils import find_c_files
    from .models.c_structures import Function

def to_uml_id(name: str) -> str:
    return name.replace('.', '_').replace('-', '_').upper()

def parse_header_for_prototypes_and_macros(header_path: str) -> Tuple[List[str], List[str]]:
    return CParser.parse_header_file(header_path)

def load_config(config_path: str) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

class CToPlantUMLConverter:
    def __init__(self, c_file_prefixes: Optional[List[str]] = None):
        self.generator = PlantUMLGenerator()
        self.c_file_prefixes = c_file_prefixes or []
    
    def convert_projects(self, project_roots: List[str], output_dir: Optional[str] = None, recursive: bool = True) -> None:
        for project_root in project_roots:
            print(f"Processing project root: {project_root}")
            self.convert_project(project_root, output_dir, recursive)
    def convert_project(self, project_root: str, output_dir: Optional[str] = None, recursive: bool = True) -> None:
        c_extensions = {'.c', '.h', '.cpp', '.cc', '.cxx', '.hpp', '.hxx'}
        c_files = [f for f in find_c_files(project_root, recursive) if os.path.splitext(f)[1].lower() in c_extensions]
        # Only filter if c_file_prefixes is non-empty
        if self.c_file_prefixes:
            c_files = [f for f in c_files if any(os.path.basename(f).startswith(prefix) for prefix in self.c_file_prefixes)]
        if not c_files:
            print(f"No C files found in the project: {project_root}")
            return
        if not output_dir:
            output_dir = os.getcwd()
        os.makedirs(output_dir, exist_ok=True)
        for c_file in c_files:
            self.generate_diagram_for_c_file(c_file, output_dir, project_root)
    def generate_diagram_for_c_file(self, c_file: str, output_dir: str, project_root: str) -> None:
        parser = CParser()


        try:
            with open(c_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(c_file, 'r', encoding='latin-1') as f:
                content = f.read()
        parser._parse_content(content)
        includes = list(parser.includes)
        functions = self.extract_functions_from_parser(parser)
        c_base = os.path.splitext(os.path.basename(c_file))[0]
        c_uml_id = to_uml_id(os.path.basename(c_file))
        header_infos = []
        for h in includes:
            h_path = self.resolve_header_path(h, c_file, project_root)
            prototypes, macros = parse_header_for_prototypes_and_macros(h_path)
            header_infos.append({
                'name': h,
                'uml_id': to_uml_id(h),
                'prototypes': prototypes,
                'macros': macros,
                'stereotype': '<<public_header>>' if h.endswith('.h') else '<<private_header>>',
            })
        plantuml_content = self.generator.generate_c_file_diagram(
            c_base, c_uml_id, functions, header_infos
        )
        output_path = os.path.join(output_dir, f"{c_base}.puml")
        with open(output_path, 'w', encoding='utf-8') as out_file:
            out_file.write(plantuml_content)
        print(f"PlantUML diagram written to {output_path}")
    def extract_functions_from_parser(self, parser: CParser) -> List[str]:
        functions = []
        for struct in parser.structs.values():
            for func in struct.functions:
                params_str = ', '.join([f"{p.type} {p.name}" for p in func.parameters])
                functions.append(f"{func.return_type} {func.name}({params_str})")
        return functions
    def resolve_header_path(self, header: str, c_file: str, project_root: str) -> str:
        c_dir = os.path.dirname(c_file)
        candidate = os.path.join(c_dir, header)
        if os.path.exists(candidate):
            return candidate
        candidate = os.path.join(project_root, header)
        if os.path.exists(candidate):
            return candidate
        return header

# Extend PlantUMLGenerator with a new method for the requested format
setattr(PlantUMLGenerator, 'generate_c_file_diagram', lambda self, c_base, c_uml_id, functions, header_infos: (
    '\n'.join([
        f"@startuml CLS: {c_base}",
        '',
        f'class "{c_base}" as {c_uml_id} <<source>> #LightBlue',
        '{',
        *(f"    + {func}" for func in functions),
        '}',
        '',
        *[line for h in header_infos for line in (
            [f'interface "{h["name"]}" as {h["uml_id"]} {h["stereotype"]} #LightGreen', '{'] +
            [f"    {macro}" for macro in h['macros']] +
            [f"    {proto}" for proto in h['prototypes']] +
            ['}', '', f'{c_uml_id} --> {h["uml_id"]} : <<include>>', '']
        )],
        '',
        '@enduml'
    ])
))

# Usage:
#   python main.py test_config.json
#
# See test_config.json for an example configuration file.

def main():
    # Always use test_config.json as the config file
    config_path = os.path.join(os.path.dirname(__file__), '..', 'test_config.json')
    config = load_config(config_path)
    project_roots = config.get('project_roots', [])
    output_dir = config.get('output_dir', '.')
    recursive = config.get('recursive', True)
    c_file_prefixes = config.get('c_file_prefixes', [])
    if not isinstance(c_file_prefixes, list):
        c_file_prefixes = [c_file_prefixes] if c_file_prefixes else []
    if not project_roots:
        print('No project_roots specified in config!')
        sys.exit(1)
    converter = CToPlantUMLConverter(c_file_prefixes=c_file_prefixes)
    converter.convert_projects(
        project_roots,
        output_dir,
        recursive
    )

if __name__ == "__main__":
    main() 