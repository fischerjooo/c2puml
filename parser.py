import os
import re
from pathlib import Path

def parse_c_file(c_file_path):
    """Parse a C file for function definitions and included headers."""
    with open(c_file_path, 'r') as f:
        content = f.read()

    # Extract function signatures (very basic, doesn't handle all cases)
    func_pattern = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*\s+)+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)\s*\{')
    functions = func_pattern.findall(content)

    # Extract included headers
    includes = re.findall(r'#include\s+"([^"]+)"', content)

    return functions, includes

def parse_h_file(h_file_path):
    """Parse a header file for basic struct definitions."""
    with open(h_file_path, 'r') as f:
        content = f.read()

    struct_pattern = re.compile(r'typedef\s+struct\s+([a-zA-Z_][a-zA-Z0-9_]*)?\s*\{([^}]*)\}\s*([a-zA-Z_][a-zA-Z0-9_]*);')
    structs = struct_pattern.findall(content)

    return structs

def generate_plantuml(c_filename, functions, includes, struct_dict):
    """Generate PlantUML diagram content for a C file."""
    c_base = Path(c_filename).stem
    lines = ["@startuml", ""]

    # Class for the C file
    lines.append(f"class {c_base}_c {{")
    for func in functions:
        return_type = ' '.join(func[0].split()).strip()
        name = func[1]
        args = func[2].strip()
        lines.append(f"  +{return_type} {name}({args})")
    lines.append("}\n")

    # Classes for included headers
    for h in includes:
        h_base = Path(h).stem
        lines.append(f"class {h_base}_h {{")
        for struct in struct_dict.get(h, []):
            struct_name = struct[2] or struct[0] or "anonymous"
            members = [m.strip() for m in struct[1].split(';') if m.strip()]
            lines.append(f"  struct {struct_name} {{")
            for m in members:
                lines.append(f"    {m}")
            lines.append("  }")
        lines.append("}\n")
        # Add relation
        lines.append(f"{c_base}_c ..> {h_base}_h : includes\n")

    lines.append("@enduml")
    return '\n'.join(lines)

def parse_structs_and_types_from_header(header_path):
    """Extract structs, typedefs (with names), and map them to their header file."""
    with open(header_path, 'r') as f:
        content = f.read()

    struct_pattern = re.compile(
        r'typedef\s+struct\s+([a-zA-Z_][a-zA-Z0-9_]*)?\s*\{([^}]*)\}\s*([a-zA-Z_][a-zA-Z0-9_]*);'
    )
    structs = struct_pattern.findall(content)

    custom_types = {}
    for match in structs:
        typename = match[2] or match[0]
        if typename:
            custom_types[typename] = os.path.basename(header_path)
    return custom_types


def find_custom_type_usages(content, custom_types):
    """Find which custom types are used in the given C file content."""
    used_types = set()
    for typename in custom_types:
        pattern = re.compile(r'\b' + re.escape(typename) + r'\b')
        if pattern.search(content):
            used_types.add(typename)
    return used_types


def generate_enhanced_plantuml(c_filename, functions, includes, used_custom_types, custom_types):
    c_base = Path(c_filename).stem
    lines = ["@startuml", ""]

    # Class for the C file
    lines.append(f"class {c_base}_c {{")
    for func in functions:
        return_type = ' '.join(func[0].split()).strip()
        name = func[1]
        args = func[2].strip()
        lines.append(f"  +{return_type} {name}({args})")
    lines.append("}\n")

    defined_headers = set()

    # Header file classes
    for h in includes:
        h_base = Path(h).stem
        lines.append(f"class {h_base}_h")
        defined_headers.add(h_base)
        lines.append("")

    # Custom type entities and header relations
    for typename, header in custom_types.items():
        lines.append(f"class {typename}")
        h_base = Path(header).stem
        if h_base in defined_headers:
            lines.append(f"{h_base}_h --> {typename} : defines")
    lines.append("")

    # Relationships from C file to headers
    for h in includes:
        h_base = Path(h).stem
        if h_base in defined_headers:
            lines.append(f"{c_base}_c ..> {h_base}_h : includes")

    # Relationships from C file to used custom types
    for typename in used_custom_types:
        lines.append(f"{c_base}_c ..> {typename} : uses")

    lines.append("@enduml")
    return '\n'.join(lines)


def walk_and_generate_custom_type_diagram(project_dir, output_dir):
    custom_types = {}

    # Step 1: Parse all headers for custom types
    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith('.h'):
                h_path = os.path.join(root, file)
                types = parse_structs_and_types_from_header(h_path)
                custom_types.update(types)

    # Step 2: Parse all .c files, track type usage
    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith('.c'):
                c_path = os.path.join(root, file)
                with open(c_path, 'r') as f:
                    content = f.read()

                functions, includes = parse_c_file(c_path)
                used_types = find_custom_type_usages(content, custom_types)
                plantuml_text = generate_enhanced_plantuml(file, functions, includes, used_types, custom_types)

                output_path = os.path.join(output_dir, f"{Path(file).stem}.puml")
                with open(output_path, 'w') as out_file:
                    out_file.write(plantuml_text)

    return f"Custom-type-enhanced PlantUML files written to: {output_dir}"


# Usage example:
directory_path = f'D:\WORK\Sandbox\model_city_sim'
output_path = f'D:\WORK\Sandbox\generator_project'
walk_and_generate_custom_type_diagram(directory_path,output_path)