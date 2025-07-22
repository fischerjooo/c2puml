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
            "typedefs_relations": [],
            "structs": [],
            "unions": [],
            "enums": [],
            "functions": [],
            "globals": [],
        }

    def _type_to_str(self, typ) -> str:
        return self.gen.visit(typ)

    def visit_Typedef(self, node: c_ast.Typedef) -> None:
        base_type = self._type_to_str(node.type)
        self.model["typedefs"].append({
            "name": node.name,
            "type": base_type,
        })
        # Record typedef relationship
        self.model["typedefs_relations"].append({
            "typedef_name": node.name,
            "base_type": base_type,
        })
        
        # Extract struct fields if this typedef contains a struct
        struct_node = None
        if isinstance(node.type, c_ast.Struct):
            struct_node = node.type
        elif isinstance(node.type, c_ast.TypeDecl) and isinstance(node.type.type, c_ast.Struct):
            struct_node = node.type.type
        
        if struct_node:
            struct_fields = []
            if struct_node.decls:
                for decl in struct_node.decls:
                    if hasattr(decl, 'name') and decl.name:
                        field_type = self._type_to_str(decl.type)
                        struct_fields.append({
                            "name": decl.name,
                            "type": field_type,
                        })
            # Add the struct to our structs list
            self.model["structs"].append({
                "name": struct_node.name or node.name,
                "fields": struct_fields,
                "coord": str(node.coord),
            })

    def visit_Struct(self, node: c_ast.Struct) -> None:
        if not node.name:
            return
        fields = []
        if node.decls:
            for decl in node.decls:
                # Handle different types of field declarations
                if hasattr(decl, 'name') and decl.name:
                    field_type = self._type_to_str(decl.type)
                    fields.append({
                        "name": decl.name,
                        "type": field_type,
                    })
                elif hasattr(decl, 'type') and hasattr(decl.type, 'names'):
                    # Handle anonymous struct fields
                    field_type = self._type_to_str(decl.type)
                    fields.append({
                        "name": f"anonymous_{len(fields)}",
                        "type": field_type,
                    })
        self.model["structs"].append({
            "name": node.name,
            "fields": fields,
            "coord": str(node.coord),
        })

    def visit_Union(self, node: c_ast.Union) -> None:
        if not node.name:
            return
        fields = []
        if node.decls:
            for decl in node.decls:
                # Handle different types of field declarations
                if hasattr(decl, 'name') and decl.name:
                    field_type = self._type_to_str(decl.type)
                    fields.append({
                        "name": decl.name,
                        "type": field_type,
                    })
                elif hasattr(decl, 'type') and hasattr(decl.type, 'names'):
                    # Handle anonymous union fields
                    field_type = self._type_to_str(decl.type)
                    fields.append({
                        "name": f"anonymous_{len(fields)}",
                        "type": field_type,
                    })
        self.model["unions"].append({
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
                if hasattr(enumerator, 'name') and enumerator.name:
                    values.append(enumerator.name)
        self.model["enums"].append({
            "name": node.name,
            "values": values,
            "coord": str(node.coord),
        })

    def visit_FuncDef(self, node: c_ast.FuncDef) -> None:
        params = []
        if node.decl.type.args:
            for param in node.decl.type.args.params:
                # Handle different types of parameter declarations
                if hasattr(param, 'name') and param.name:
                    param_type = self._type_to_str(param.type)
                    params.append({
                        "name": param.name,
                        "type": param_type,
                    })
                elif hasattr(param, 'type'):
                    # Handle anonymous parameters
                    param_type = self._type_to_str(param.type)
                    params.append({
                        "name": f"param_{len(params)}",
                        "type": param_type,
                    })
        self.model["functions"].append({
            "name": node.decl.name,
            "return_type": self._type_to_str(node.decl.type.type),
            "params": params,
            "coord": str(node.coord),
        })

    def visit_Decl(self, node: c_ast.Decl) -> None:
        # Only process global variable declarations (not function parameters)
        if (hasattr(node, 'name') and node.name and 
            not isinstance(node.type, c_ast.FuncDecl)):
            
            # Skip typedefs (they're handled by visit_Typedef)
            if hasattr(node, 'quals') and 'typedef' in node.quals:
                return
            
            # This is likely a global variable declaration
            var_type = self._type_to_str(node.type)
            self.model["globals"].append({
                "name": node.name,
                "type": var_type,
                "coord": str(node.coord),
            })
        
        # Continue visiting child nodes
        self.generic_visit(node)

def parse_c_file(file_path: str | Path) -> Dict[str, list]:
    """
    Parse a C file and extract typedefs, structs, enums, functions, and globals.
    Supports both .c and .h files.
    """
    file_path = Path(file_path)
    
    # Use fake libc headers for parsing
    fake_libc_path = str(FAKE_LIBC_DIR)
    
    try:
        # First try with preprocessing
        ast = parse_file(str(file_path), use_cpp=True, cpp_path='gcc',
                        cpp_args=['-E', '-I' + fake_libc_path])
        
        # Extract model from AST
        extractor = ModelExtractor()
        extractor.visit(ast)
        
        return extractor.model
    except Exception as e:
        print(f"Preprocessing failed for {file_path}: {e}", file=sys.stderr)
        
        # Fallback: try without preprocessing but strip preprocessor directives
        try:
            # Read the file and strip preprocessor directives
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Remove preprocessor directives and comments
            import re
            lines = content.split('\n')
            filtered_lines = []
            for line in lines:
                stripped = line.strip()
                if not stripped.startswith('#include') and not stripped.startswith('#define'):
                    # Remove C++ style comments
                    if '//' in line:
                        comment_start = line.find('//')
                        if comment_start > 0:
                            # Keep only the code part
                            code_part = line[:comment_start].rstrip()
                            if code_part:
                                filtered_lines.append(code_part)
                        # If line starts with comment, skip it entirely
                    else:
                        filtered_lines.append(line)
            
            # Write filtered content to a temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
                f.write('\n'.join(filtered_lines))
                temp_file = f.name
            
            try:
                # Parse the filtered file
                ast = parse_file(temp_file, use_cpp=False)
                extractor = ModelExtractor()
                extractor.visit(ast)
                return extractor.model
            finally:
                # Clean up temp file
                Path(temp_file).unlink()
                
        except Exception as e2:
            print(f"Fallback parsing also failed for {file_path}: {e2}", file=sys.stderr)
            # Return empty model
            return {
                "typedefs": [],
                "typedefs_relations": [],
                "structs": [],
                "unions": [],
                "enums": [],
                "functions": [],
                "globals": [],
            }

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Parse a C file into a JSON model using pycparser.")
    parser.add_argument('c_file', help="Path to the C file to parse.")
    parser.add_argument('--output', default=None, help="Destination JSON file for the extracted model.")
    parser.add_argument('--include', action='append', default=[], help="Extra include directories.")
    args = parser.parse_args()

    c_file = Path(args.c_file)
    extra_includes = [Path(p) for p in args.include]
    model = parse_c_file(c_file)
    output = json.dumps(model, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"Model written to {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main()