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
        c_extensions = {'.c', '.cpp', '.cc', '.cxx'}
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
        globals_ = self.extract_globals_from_parser(parser)
        c_base = os.path.splitext(os.path.basename(c_file))[0]
        c_uml_id = to_uml_id(os.path.basename(c_file))
        # --- Extract macros from the C file ---
        macros = self.extract_macros_from_content(content)
        # ---
        header_infos = []
        for h in includes:
            h_path = self.resolve_header_path(h, c_file, project_root)
            prototypes, h_macros = parse_header_for_prototypes_and_macros(h_path)
            header_infos.append({
                'name': h,
                'uml_id': to_uml_id(h),
                'prototypes': prototypes,
                'macros': h_macros,
                'stereotype': '<<public_header>>' if h.endswith('.h') else '<<private_header>>',
            })
        plantuml_content = self.generator.generate_c_file_diagram_with_macros_and_globals(
            c_base, c_uml_id, functions, macros, globals_, header_infos
        )  # type: ignore
        output_path = os.path.join(output_dir, f"{c_base}.puml")
        with open(output_path, 'w', encoding='utf-8') as out_file:
            out_file.write(plantuml_content)
        print(f"PlantUML diagram written to {output_path}")
    def extract_functions_from_parser(self, parser: CParser) -> List[str]:
        functions = []
        seen = set()
        # Functions associated with structs
        for struct in parser.structs.values():
            for func in struct.functions:
                params_str = ', '.join([f"{p.type} {p.name}" for p in func.parameters])
                sig = f"{func.return_type} {func.name}({params_str})"
                if sig not in seen:
                    visibility = '-' if func.is_static else '+'
                    functions.append(f"{visibility}{func.return_type} {func.name}({params_str})")
                    seen.add(sig)
        # Top-level (non-struct) functions
        for func in parser.functions:
            params_str = ', '.join([f"{p.type} {p.name}" for p in func.parameters])
            sig = f"{func.return_type} {func.name}({params_str})"
            if sig not in seen:
                visibility = '-' if func.is_static else '+'
                functions.append(f"{visibility}{func.return_type} {func.name}({params_str})")
                seen.add(sig)
        return functions
    def resolve_header_path(self, header: str, c_file: str, project_root: str) -> str:
        c_dir = os.path.dirname(c_file)
        candidate = os.path.join(c_dir, header)
        if os.path.exists(candidate):
            return candidate
        candidate = os.path.join(project_root, header)
        if os.path.exists(candidate):
            return candidate
        # Case-insensitive search in c_dir
        for fname in os.listdir(c_dir):
            if fname.lower() == header.lower():
                return os.path.join(c_dir, fname)
        # Case-insensitive search in project_root
        for fname in os.listdir(project_root):
            if fname.lower() == header.lower():
                return os.path.join(project_root, fname)
        return header

    def extract_macros_from_content(self, content: str) -> list:
        """Extract #define macro names from C file content using CParser.parse_header_file logic, but mark as '-' for private."""
        import tempfile
        import os
        from c_to_plantuml.parsers.c_parser import CParser
        # Write content to a temporary file to reuse parse_header_file
        with tempfile.NamedTemporaryFile('w+', delete=False, suffix='.h') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            _, macros = CParser.parse_header_file(tmp_path)
        finally:
            os.unlink(tmp_path)
        # Change + to - for private macros
        macros = [macro.replace('+', '-', 1) if macro.startswith('+') else macro for macro in macros]
        return macros

    def extract_globals_from_parser(self, parser: CParser) -> list:
        """Extract global variables from the parser as PlantUML field strings, using '-' for static (local) and '+' for extern/public."""
        globals_ = []
        for field in parser.globals:
            type_str = field.type
            if field.is_pointer:
                type_str += "*"
            if field.is_array:
                type_str += f"[{field.array_size or ''}]"
            # Use '-' for static, '+' otherwise
            visibility = '-' if getattr(field, 'is_static', False) else '+'
            globals_.append(f"{visibility} {type_str} {field.name}")
        return globals_

# Extend PlantUMLGenerator with a new method for the requested format
setattr(PlantUMLGenerator, 'generate_c_file_diagram_with_macros_and_globals', lambda self, c_base, c_uml_id, functions, macros, globals_, header_infos: (
    '\n'.join([
        f"@startuml CLS: {c_base}",
        '',
        f'class "{c_base}" as {c_uml_id} <<source>> #LightBlue',
        '{',
        *(f"    {g}" for g in globals_),
        *(f"    {macro}" for macro in macros),
        *(f"    {func}" for func in functions),
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