import os
from typing import List, Dict, Optional
from ..models.project_model import ProjectModel, FileModel
from ..models.c_structures import Field, Function, Struct, Enum

class PlantUMLGenerator:
    """Generates PlantUML diagrams from a ProjectModel (loaded from JSON)"""
    
    def __init__(self):
        self.output = []
    
    def generate_from_model(self, model: ProjectModel, output_dir: str) -> None:
        """Generate PlantUML files for each file in the project model"""
        print(f"Generating PlantUML diagrams from model for project: {model.project_name}")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate a diagram for each file
        for file_path, file_model in model.files.items():
            self._generate_file_diagram(file_model, output_dir)
        
        print(f"Generated {len(model.files)} PlantUML diagrams in {output_dir}")
    
    def _generate_file_diagram(self, file_model: FileModel, output_dir: str) -> None:
        """Generate a PlantUML diagram for a single file"""
        c_base = os.path.splitext(os.path.basename(file_model.file_path))[0]
        c_uml_id = self._to_uml_id(os.path.basename(file_model.file_path))
        
        # Extract functions for display
        functions = self._extract_functions_display(file_model)
        
        # Extract globals for display
        globals_display = self._extract_globals_display(file_model)
        
        # Process includes and resolve header information
        header_infos = self._process_includes(file_model)
        
        # Generate PlantUML content
        plantuml_content = self._generate_file_diagram_content(
            c_base, c_uml_id, functions, file_model.macros, 
            globals_display, header_infos
        )
        
        # Write to file
        output_path = os.path.join(output_dir, f"{c_base}.puml")
        with open(output_path, 'w', encoding='utf-8') as out_file:
            out_file.write(plantuml_content)
        
        print(f"Generated PlantUML diagram: {output_path}")
    
    def _to_uml_id(self, name: str) -> str:
        """Convert name to UML ID format"""
        return name.replace('.', '_').replace('-', '_').upper()
    
    def _extract_functions_display(self, file_model: FileModel) -> List[str]:
        """Extract functions for PlantUML display"""
        functions = []
        seen = set()
        
        # Functions associated with structs
        for struct in file_model.structs.values():
            for func in struct.functions:
                params_str = ', '.join([f"{p.type} {p.name}" for p in func.parameters])
                sig = f"{func.return_type} {func.name}({params_str})"
                if sig not in seen:
                    visibility = '-' if func.is_static else '+'
                    functions.append(f"{visibility}{func.return_type} {func.name}({params_str})")
                    seen.add(sig)
        
        # Top-level (non-struct) functions
        for func in file_model.functions:
            params_str = ', '.join([f"{p.type} {p.name}" for p in func.parameters])
            sig = f"{func.return_type} {func.name}({params_str})"
            if sig not in seen:
                visibility = '-' if func.is_static else '+'
                functions.append(f"{visibility}{func.return_type} {func.name}({params_str})")
                seen.add(sig)
        
        return functions
    
    def _extract_globals_display(self, file_model: FileModel) -> List[str]:
        """Extract global variables for PlantUML display"""
        globals_display = []
        for field in file_model.globals:
            type_str = field.type
            if field.is_pointer:
                type_str += "*"
            if field.is_array:
                type_str += f"[{field.array_size or ''}]"
            
            # Use '-' for static, '+' otherwise
            visibility = '-' if getattr(field, 'is_static', False) else '+'
            globals_display.append(f"{visibility} {type_str} {field.name}")
        
        return globals_display
    
    def _process_includes(self, file_model: FileModel) -> List[Dict]:
        """Process includes and create header info structures"""
        header_infos = []
        
        for include in file_model.includes:
            # Try to resolve header path and parse it
            h_path = self._resolve_header_path(include, file_model.file_path, file_model.project_root)
            
            if h_path and os.path.exists(h_path):
                # Use the standard header parser
                from ..parsers.c_parser import CParser
                prototypes, h_macros = CParser.parse_header_file(h_path)
            else:
                prototypes, h_macros = [], []
            
            header_infos.append({
                'name': include,
                'uml_id': self._to_uml_id(include),
                'prototypes': prototypes,
                'macros': h_macros,
                'stereotype': '<<public_header>>' if include.endswith('.h') else '<<private_header>>',
            })
        
        return header_infos
    
    def _resolve_header_path(self, header: str, c_file: str, project_root: str) -> Optional[str]:
        """Resolve header file path (simplified version)"""
        c_dir = os.path.dirname(c_file)
        
        # Try relative to C file directory
        candidate = os.path.join(c_dir, header)
        if os.path.exists(candidate):
            return candidate
        
        # Try relative to project root
        candidate = os.path.join(project_root, header)
        if os.path.exists(candidate):
            return candidate
        
        # Case-insensitive search in c_dir
        try:
            for fname in os.listdir(c_dir):
                if fname.lower() == header.lower():
                    return os.path.join(c_dir, fname)
        except OSError:
            pass
        
        # Case-insensitive search in project_root
        try:
            for fname in os.listdir(project_root):
                if fname.lower() == header.lower():
                    return os.path.join(project_root, fname)
        except OSError:
            pass
        
        return None
    
    def _generate_file_diagram_content(self, c_base: str, c_uml_id: str, 
                                     functions: List[str], macros: List[str], 
                                     globals_display: List[str], header_infos: List[Dict]) -> str:
        """Generate the actual PlantUML content"""
        content_lines = [
            f"@startuml CLS: {c_base}",
            '',
            f'class "{c_base}" as {c_uml_id} <<source>> #LightBlue',
            '{'
        ]
        
        # Add globals
        for global_var in globals_display:
            content_lines.append(f"    {global_var}")
        
        # Add macros
        for macro in macros:
            content_lines.append(f"    {macro}")
        
        # Add functions
        for func in functions:
            content_lines.append(f"    {func}")
        
        content_lines.append('}')
        content_lines.append('')
        
        # Add header interfaces
        for h in header_infos:
            content_lines.extend([
                f'interface "{h["name"]}" as {h["uml_id"]} {h["stereotype"]} #LightGreen',
                '{'
            ])
            
            # Add header macros
            for macro in h['macros']:
                content_lines.append(f"    {macro}")
            
            # Add header prototypes
            for proto in h['prototypes']:
                content_lines.append(f"    {proto}")
            
            content_lines.extend([
                '}',
                '',
                f'{c_uml_id} --> {h["uml_id"]} : <<include>>',
                ''
            ])
        
        content_lines.append('@enduml')
        
        return '\n'.join(content_lines)
    
    def generate_project_overview(self, model: ProjectModel, output_path: str) -> None:
        """Generate a project overview diagram showing file relationships"""
        print(f"Generating project overview diagram: {output_path}")
        
        content_lines = [
            f"@startuml Project: {model.project_name}",
            '!theme plain',
            '',
            f'package "{model.project_name}" <<folder>> {{',
            ''
        ]
        
        # Add each file as a component
        for file_path, file_model in model.files.items():
            file_name = os.path.basename(file_path)
            file_base = os.path.splitext(file_name)[0]
            file_uml_id = self._to_uml_id(file_name)
            
            # Count elements in file
            struct_count = len(file_model.structs)
            func_count = len(file_model.functions)
            macro_count = len(file_model.macros)
            
            content_lines.append(
                f'  component "{file_base}\\n({struct_count} structs, {func_count} funcs, {macro_count} macros)" as {file_uml_id}'
            )
        
        content_lines.extend([
            '',
            '}',
            '',
            'note top : Generated from C to PlantUML converter',
            f'note bottom : Created: {model.created_at}',
            '',
            '@enduml'
        ])
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content_lines))
        
        print(f"Project overview diagram saved to: {output_path}")

def generate_plantuml_from_json(model_json_path: str, output_dir: str) -> None:
    """Convenience function to generate PlantUML from a JSON model file"""
    print(f"Loading project model from: {model_json_path}")
    
    model = ProjectModel.load_from_json(model_json_path)
    generator = PlantUMLGenerator()
    
    # Generate individual file diagrams
    generator.generate_from_model(model, output_dir)
    
    # Generate project overview
    overview_path = os.path.join(output_dir, f"{model.project_name}_overview.puml")
    generator.generate_project_overview(model, overview_path)
    
    print(f"PlantUML generation complete. Output in: {output_dir}") 