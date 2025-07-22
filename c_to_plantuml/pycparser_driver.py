#!/usr/bin/env python3
"""
pycparser-based parser for C to PlantUML model extraction.
Extracts typedefs, structs, enums, and functions from C files using pycparser.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

from pycparser import parse_file, c_ast, c_generator

FAKE_LIBC_DIR = Path(__file__).parent.parent / "fake_libc_include"

class ModelExtractor(c_ast.NodeVisitor):
    """Walk the AST and build a minimal JSON-serialisable model."""
    def __init__(self) -> None:
        super().__init__()
        self.gen = c_generator.CGenerator()
        self.model: Dict[str, list] = {
            "typedefs": [],
            "structs": [],
            "enums": [],
            "functions": [],
        }

    def _type_to_str(self, typ) -> str:
        return self.gen.visit(typ)

    def visit_Typedef(self, node: c_ast.Typedef) -> None:
        self.model["typedefs"].append({
            "name": node.name,
            "type": self._type_to_str(node.type),
            "coord": str(node.coord),
        })

    def visit_Struct(self, node: c_ast.Struct) -> None:
        if not node.name:
            return
        fields = []
        if node.decls:
            for decl in node.decls:
                fields.append({
                    "name": decl.name,
                    "type": self._type_to_str(decl.type),
                })
        self.model["structs"].append({
            "name": node.name,
            "fields": fields,
            "coord": str(node.coord),
        })

    def visit_Enum(self, node: c_ast.Enum) -> None:
        if not node.name:
            return
        values = []
        if node.values:
            for enumerator in node.values.enumerators:
                values.append(enumerator.name)
        self.model["enums"].append({
            "name": node.name,
            "values": values,
            "coord": str(node.coord),
        })

    def visit_FuncDef(self, node: c_ast.FuncDef) -> None:
        decl: c_ast.Decl = node.decl
        func_type: c_ast.FuncDecl = decl.type  # type: ignore[assignment]
        params = []
        if func_type.args:
            for param in func_type.args.params:
                if isinstance(param, c_ast.Decl):
                    params.append({
                        "name": param.name,
                        "type": self._type_to_str(param.type),
                    })
        self.model["functions"].append({
            "name": decl.name,
            "return_type": self._type_to_str(func_type.type),
            "params": params,
            "coord": str(decl.coord),
        })

def parse_c_file(c_file: Path, extra_include_dirs: List[Path] = None) -> Dict[str, list]:
    """Parse a C file and return the extracted model."""
    cpp_args = [
        '-E',
        '-nostdinc',
        '-I', str(FAKE_LIBC_DIR),
    ]
    if extra_include_dirs:
        for inc_dir in extra_include_dirs:
            cpp_args.extend(['-I', str(inc_dir)])
    try:
        ast = parse_file(
            filename=str(c_file),
            use_cpp=True,
            cpp_path='gcc',
            cpp_args=cpp_args,
        )
    except Exception as exc:
        print(f"[warning] failed to parse {c_file}: {exc}", file=sys.stderr)
        return {}
    extractor = ModelExtractor()
    extractor.visit(ast)
    return extractor.model

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Parse a C file into a JSON model using pycparser.")
    parser.add_argument('c_file', help="Path to the C file to parse.")
    parser.add_argument('--output', default=None, help="Destination JSON file for the extracted model.")
    parser.add_argument('--include', action='append', default=[], help="Extra include directories.")
    args = parser.parse_args()

    c_file = Path(args.c_file)
    extra_includes = [Path(p) for p in args.include]
    model = parse_c_file(c_file, extra_includes)
    output = json.dumps(model, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"Model written to {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main()