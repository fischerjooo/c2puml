"""
Unified Parser Pipeline

Main coordinator for the unified parser system that integrates all parser modules
and provides the interface for the existing architecture.
"""

import logging
from typing import List, Optional, Dict, Any, Set
from pathlib import Path

from .base import (
    ParserLevel, ParseContext, ParseResult, TypedefInfo, 
    AnonymousStructure, ParserRegistry, ParsingPipeline, ParserError
)
from .basic_parser import BasicTypedefParser, BasicFieldParser, BasicTypeParser
from .struct_parser import StructTypedefParser, UnionTypedefParser, EnumTypedefParser
from ...models import Struct, Union, Field, Alias, FileModel, ProjectModel


class UnifiedParser:
    """Main unified parser that coordinates all parsing operations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.pipeline = ParsingPipeline()
        self.anonymous_structures: List[AnonymousStructure] = []
        self.processed_typedefs: Dict[str, TypedefInfo] = {}
        
        # Register all parsers
        self._register_parsers()
    
    def _register_parsers(self):
        """Register all available parsers in the pipeline."""
        # Basic parsers
        self.pipeline.add_parser(BasicTypedefParser())
        self.pipeline.add_parser(BasicFieldParser())
        self.pipeline.add_parser(BasicTypeParser())
        
        # Struct parsers
        self.pipeline.add_parser(StructTypedefParser())
        self.pipeline.add_parser(UnionTypedefParser())
        self.pipeline.add_parser(EnumTypedefParser())
        
        # TODO: Add complex parsers and anonymous parsers
        # self.pipeline.add_parser(FunctionPointerParser())
        # self.pipeline.add_parser(AnonymousStructParser())
    
    def process_file(self, file_model: FileModel) -> None:
        """Process all typedefs in a file using the unified parser system."""
        self.logger.debug(f"Processing file: {file_model.file_path}")
        
        # Process structs
        for struct_name, struct_data in file_model.structs.items():
            self._process_struct_typedefs(struct_name, struct_data, file_model)
        
        # Process unions
        for union_name, union_data in file_model.unions.items():
            self._process_union_typedefs(union_name, union_data, file_model)
        
        # Process aliases (typedefs)
        for alias_name, alias_data in file_model.aliases.items():
            self._process_alias_typedefs(alias_name, alias_data, file_model)
    
    def _process_struct_typedefs(self, struct_name: str, struct_data: Struct, file_model: FileModel) -> None:
        """Process typedefs within a struct."""
        context = ParseContext(
            file_path=file_model.file_path,
            parent_structure=struct_name,
            nesting_level=0
        )
        
        # Extract anonymous structures from struct fields
        for field in struct_data.fields:
            if self._is_anonymous_structure_field(field):
                self._extract_anonymous_structure(field, struct_name, "struct", file_model, context)
    
    def _process_union_typedefs(self, union_name: str, union_data: Union, file_model: FileModel) -> None:
        """Process typedefs within a union."""
        context = ParseContext(
            file_path=file_model.file_path,
            parent_structure=union_name,
            nesting_level=0
        )
        
        # Extract anonymous structures from union fields
        for field in union_data.fields:
            if self._is_anonymous_structure_field(field):
                self._extract_anonymous_structure(field, union_name, "union", file_model, context)
    
    def _process_alias_typedefs(self, alias_name: str, alias_data: Alias, file_model: FileModel) -> None:
        """Process alias typedefs."""
        context = ParseContext(
            file_path=file_model.file_path,
            line_number=0,  # TODO: Get actual line number
            available_types=self._get_available_types(file_model)
        )
        
        # Parse the typedef using the pipeline
        result = self.pipeline.parse_text(alias_data.original_type, context)
        
        if result.success and isinstance(result.parsed_data, TypedefInfo):
            self.processed_typedefs[alias_name] = result.parsed_data
            
            # Extract anonymous structures from the typedef
            self._extract_anonymous_from_typedef(result.parsed_data, alias_name, file_model, context)
        else:
            self.logger.warning(f"Failed to parse typedef {alias_name}: {result.error_message}")
    
    def _is_anonymous_structure_field(self, field: Field) -> bool:
        """Check if a field contains an anonymous structure."""
        field_type = field.type.lower()
        return (
            'struct {' in field_type or 
            'union {' in field_type or
            field_type.startswith('struct {') or
            field_type.startswith('union {')
        )
    
    def _extract_anonymous_structure(self, field: Field, parent_name: str, parent_type: str, 
                                   file_model: FileModel, context: ParseContext) -> None:
        """Extract anonymous structure from a field."""
        # Parse the anonymous structure content
        content = self._extract_anonymous_content(field.type)
        if not content:
            return
        
        # Generate a unique name for the anonymous structure
        generated_name = f"{parent_name}_anonymous_{parent_type}_{len(self.anonymous_structures) + 1}"
        
        # Parse the fields using the pipeline
        fields = self._parse_anonymous_fields(content, context)
        
        # Create anonymous structure
        anon_struct = AnonymousStructure(
            parent_name=parent_name,
            structure_type=parent_type,
            fields=fields,
            generated_name=generated_name,
            source_text=field.type,
            original_field_name=field.name
        )
        
        self.anonymous_structures.append(anon_struct)
        
        # Add to file model
        if parent_type == "struct":
            file_model.structs[generated_name] = Struct(
                name=generated_name,
                fields=fields
            )
        else:  # union
            file_model.unions[generated_name] = Union(
                name=generated_name,
                fields=fields
            )
    
    def _extract_anonymous_content(self, field_type: str) -> Optional[str]:
        """Extract content from anonymous structure field type."""
        import re
        
        # Handle struct { ... } pattern
        struct_match = re.search(r'struct\s*\{([^}]*)\}', field_type)
        if struct_match:
            return struct_match.group(1).strip()
        
        # Handle union { ... } pattern
        union_match = re.search(r'union\s*\{([^}]*)\}', field_type)
        if union_match:
            return union_match.group(1).strip()
        
        return None
    
    def _parse_anonymous_fields(self, content: str, context: ParseContext) -> List[Field]:
        """Parse fields from anonymous structure content."""
        fields = []
        
        if not content.strip():
            return fields
        
        # Split by semicolons to get individual field declarations
        field_declarations = [f.strip() for f in content.split(';') if f.strip()]
        
        for decl in field_declarations:
            # Use the pipeline to parse each field
            field_context = ParseContext(
                file_path=context.file_path,
                line_number=context.line_number,
                parent_structure=context.parent_structure,
                nesting_level=context.nesting_level + 1
            )
            
            result = self.pipeline.parse_text(decl, field_context)
            if result.success and isinstance(result.parsed_data, Field):
                fields.append(result.parsed_data)
        
        return fields
    
    def _extract_anonymous_from_typedef(self, typedef_info: TypedefInfo, typedef_name: str, 
                                      file_model: FileModel, context: ParseContext) -> None:
        """Extract anonymous structures from a typedef AST."""
        for field in typedef_info.fields:
            if self._is_anonymous_structure_field(field):
                self._extract_anonymous_structure_from_field(field, typedef_name, file_model, context)
    
    def _extract_anonymous_structure_from_field(self, field: Field, parent_name: str, 
                                              file_model: FileModel, context: ParseContext) -> None:
        """Extract anonymous structure from a field."""
        # Parse the anonymous structure content
        content = self._extract_anonymous_content(field.type)
        if not content:
            return
        
        # Generate a unique name
        structure_type = "struct" if "struct {" in field.type else "union"
        generated_name = f"{parent_name}_anonymous_{structure_type}_{len(self.anonymous_structures) + 1}"
        
        # Parse the fields
        fields = self._parse_anonymous_fields(content, context)
        
        # Create anonymous structure
        anon_struct = AnonymousStructure(
            parent_name=parent_name,
            structure_type=structure_type,
            fields=fields,
            generated_name=generated_name,
            source_text=field.type,
            original_field_name=field.name
        )
        
        self.anonymous_structures.append(anon_struct)
        
        # Add to file model
        if structure_type == "struct":
            file_model.structs[generated_name] = Struct(
                name=generated_name,
                fields=fields
            )
        else:  # union
            file_model.unions[generated_name] = Union(
                name=generated_name,
                fields=fields
            )
    
    def _get_available_types(self, file_model: FileModel) -> Set[str]:
        """Get all available type names from the file model."""
        types = set()
        
        # Add struct names
        types.update(file_model.structs.keys())
        
        # Add union names
        types.update(file_model.unions.keys())
        
        # Add enum names
        types.update(file_model.enums.keys())
        
        # Add alias names
        types.update(file_model.aliases.keys())
        
        return types
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get parsing statistics."""
        stats = self.pipeline.get_statistics()
        stats.update({
            'anonymous_structures_count': len(self.anonymous_structures),
            'processed_typedefs_count': len(self.processed_typedefs),
        })
        return stats
    
    def get_anonymous_structures(self) -> List[AnonymousStructure]:
        """Get all extracted anonymous structures."""
        return self.anonymous_structures.copy()
    
    def get_processed_typedefs(self) -> Dict[str, TypedefInfo]:
        """Get all processed typedefs."""
        return self.processed_typedefs.copy()


# Compatibility wrapper for the old Parser interface
class Parser:
    """Compatibility wrapper for the old Parser interface using the new UnifiedParser system."""
    
    def __init__(self):
        self.unified_parser = UnifiedParser()
        self.logger = logging.getLogger(__name__)
        # Import the old parser components directly
        from ..parser_tokenizer import CTokenizer, StructureFinder
        from ..preprocessor import PreprocessorManager
        from ...models import ProjectModel, FileModel
        from ...utils import detect_file_encoding
        
        self.tokenizer = CTokenizer()
        self.StructureFinder = StructureFinder  # Store the class, not an instance
        self.preprocessor = PreprocessorManager()
        self.detect_encoding = detect_file_encoding
        
        # Add c_parser attribute for backward compatibility
        self.c_parser = self
    
    def parse(self, source_folders: List[str], output_file: str = "model.json", 
              recursive_search: bool = True, config=None) -> "ProjectModel":
        """Parse C/C++ projects and generate model.json - compatibility wrapper."""
        self.logger.info(f"Parsing project with {len(source_folders)} source folders")
        
        # Convert source folders to Path objects
        source_paths = [Path(folder) for folder in source_folders]
        
        # Create project model with required parameters
        project_name = config.project_name if config and hasattr(config, 'project_name') else "Unknown"
        source_folder = str(source_paths[0]) if source_paths else "."
        project_model = ProjectModel(project_name=project_name, source_folder=source_folder)
        
        # Process each source folder
        for source_path in source_paths:
            if not source_path.exists():
                raise FileNotFoundError(f"Source folder not found: {source_path}")
            
            self.logger.info(f"Processing source folder: {source_path}")
            
            # Find all C/C++ files
            c_files = []
            if recursive_search:
                c_files.extend(source_path.rglob("*.c"))
                c_files.extend(source_path.rglob("*.h"))
                c_files.extend(source_path.rglob("*.cpp"))
                c_files.extend(source_path.rglob("*.hpp"))
            else:
                c_files.extend(source_path.glob("*.c"))
                c_files.extend(source_path.glob("*.h"))
                c_files.extend(source_path.glob("*.cpp"))
                c_files.extend(source_path.glob("*.hpp"))
            
            self.logger.info(f"Found {len(c_files)} C/C++ files in {source_path}")
            for file_path in c_files:
                self.logger.info(f"  - {file_path}")
            
            # Process each file
            for file_path in c_files:
                try:
                    self.logger.info(f"Processing file: {file_path}")
                    
                    # Read file content
                    encoding = self.detect_encoding(file_path)
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    
                    self.logger.info(f"File content length: {len(content)}")
                    
                    # Tokenize content first
                    tokens = self.tokenizer.tokenize(content)
                    self.logger.info(f"Tokenized into {len(tokens)} tokens")
                    
                    # Preprocess tokens
                    processed_tokens = self.preprocessor.process_file(tokens)
                    self.logger.info(f"Preprocessed into {len(processed_tokens)} tokens")
                    
                    # Convert back to content for structure finder
                    processed_content = ' '.join([token.value for token in processed_tokens])
                    
                    # Create structure finder with tokens
                    structure_finder = self.StructureFinder(tokens)
                    
                    # Find structures
                    structs = structure_finder.find_structs()
                    unions = structure_finder.find_unions()
                    enums = structure_finder.find_enums()
                    functions = structure_finder.find_functions()
                    typedefs = structure_finder.find_typedefs()
                    
                    self.logger.info(f"Found {len(structs)} structs, {len(unions)} unions, {len(enums)} enums, {len(functions)} functions, {len(typedefs)} typedefs")
                    
                    # Convert to the expected format
                    structs_dict = {}
                    unions_dict = {}
                    enums_dict = {}
                    aliases_dict = {}
                    functions_dict = {}
                    
                    # Process typedefs
                    for start_pos, end_pos, typedef_name, original_type in typedefs:
                        self.logger.info(f"Processing typedef: {typedef_name} = {original_type}")
                        # Create Alias object
                        from ...models import Alias
                        aliases_dict[typedef_name] = Alias(
                            name=typedef_name,
                            original_type=original_type
                        )
                        self.logger.info(f"Created alias object for {typedef_name}")
                    
                    # Process structs
                    for start_pos, end_pos, name in structs:
                        self.logger.info(f"Processing struct: {name} at positions {start_pos}-{end_pos}")
                        struct_content = self._extract_token_range(tokens, start_pos, end_pos)
                        fields = self._parse_struct_fields(tokens, start_pos, end_pos)
                        self.logger.info(f"Found {len(fields)} fields for struct {name}")
                        
                        # Convert fields to Field objects
                        field_objects = []
                        for field_name, field_type in fields:
                            field_objects.append(Field(name=field_name, type=field_type))
                        
                        # Create Struct object
                        from ...models import Struct
                        structs_dict[name] = Struct(
                            name=name,
                            fields=field_objects,
                            tag_name=""
                        )
                        self.logger.info(f"Created struct object for {name}")
                    
                    # Process unions
                    for start_pos, end_pos, name in unions:
                        self.logger.info(f"Processing union: {name} at positions {start_pos}-{end_pos}")
                        union_content = self._extract_token_range(tokens, start_pos, end_pos)
                        fields = self._parse_struct_fields(tokens, start_pos, end_pos)
                        # Convert fields to Field objects
                        field_objects = []
                        for field_name, field_type in fields:
                            field_objects.append(Field(name=field_name, type=field_type))
                        
                        # Create Union object
                        from ...models import Union
                        unions_dict[name] = Union(
                            name=name,
                            fields=field_objects,
                            tag_name=""
                        )
                        self.logger.info(f"Created union object for {name}")
                    
                    # Process enums
                    for start_pos, end_pos, name in enums:
                        self.logger.info(f"Processing enum: {name} at positions {start_pos}-{end_pos}")
                        enum_content = self._extract_token_range(tokens, start_pos, end_pos)
                        values = self._parse_enum_values(tokens, start_pos, end_pos)
                        # Convert values to EnumValue objects
                        from ...models import EnumValue, Enum
                        enum_value_objects = []
                        for value_name in values:
                            enum_value_objects.append(EnumValue(name=value_name))
                        
                        # Create Enum object
                        enums_dict[name] = Enum(
                            name=name,
                            values=enum_value_objects
                        )
                        self.logger.info(f"Created enum object for {name}")
                    
                    # Create file model
                    self.logger.info(f"Creating file model with {len(structs_dict)} structs, {len(unions_dict)} unions, {len(enums_dict)} enums")
                    file_model = FileModel(
                        file_path=str(file_path),
                        structs=structs_dict,
                        unions=unions_dict,
                        enums=enums_dict,
                        aliases=aliases_dict,
                        functions=functions_dict,
                        includes=[]
                    )
                    
                    # Process with unified parser
                    self.unified_parser.process_file(file_model)
                    
                    # Add to project model
                    project_model.files[file_path.name] = file_model
                    self.logger.info(f"Added file {file_path.name} to project model")
                    
                except Exception as e:
                    self.logger.warning(f"Failed to process file {file_path}: {e}")
                    import traceback
                    self.logger.warning(f"Traceback: {traceback.format_exc()}")
        
        # Save to output file
        project_model.save(output_file)
        
        return project_model
    
    def parse_project(self, source_paths, config=None, recursive_search: bool = True) -> "ProjectModel":
        """Parse project - compatibility method."""
        # Handle both Path objects and strings
        if isinstance(source_paths, (str, Path)):
            source_paths = [source_paths]
        
        # Convert to Path objects if they're strings
        path_objects = []
        for path in source_paths:
            if isinstance(path, str):
                path_objects.append(Path(path))
            else:
                path_objects.append(path)
        
        source_folders = [str(path) for path in path_objects]
        return self.parse(source_folders, "model.json", recursive_search, config)
    
    def parse_file(self, file_path: Path, filename: str) -> str:
        """Parse single file - compatibility method."""
        # For single file parsing, we'll create a temporary project model
        project_name = "SingleFile"
        source_folder = str(file_path.parent)
        project_model = ProjectModel(project_name=project_name, source_folder=source_folder)
        
        try:
            # Read file content
            encoding = self.detect_encoding(file_path)
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            # Tokenize content first
            tokens = self.tokenizer.tokenize(content)
            
            # Preprocess tokens
            processed_tokens = self.preprocessor.process_file(tokens)
            
            # Convert back to content for structure finder
            processed_content = ' '.join([token.value for token in processed_tokens])
            
            # Create structure finder with tokens
            structure_finder = self.StructureFinder(tokens)
            
            # Find structures
            structs = structure_finder.find_structs()
            unions = structure_finder.find_unions()
            enums = structure_finder.find_enums()
            functions = structure_finder.find_functions()
            typedefs = structure_finder.find_typedefs()
            
            # Convert to the expected format
            structs_dict = {}
            unions_dict = {}
            enums_dict = {}
            aliases_dict = {}
            functions_dict = {}
            
            # Process typedefs
            for start_pos, end_pos, typedef_name, original_type in typedefs:
                # Create Alias object
                from ...models import Alias
                aliases_dict[typedef_name] = Alias(
                    name=typedef_name,
                    original_type=original_type
                )
            
            # Process structs
            for start_pos, end_pos, name in structs:
                struct_content = self._extract_token_range(tokens, start_pos, end_pos)
                fields = self._parse_struct_fields(tokens, start_pos, end_pos)
                # Convert fields to Field objects
                field_objects = []
                for field_name, field_type in fields:
                    field_objects.append(Field(name=field_name, type=field_type))
                
                # Create Struct object
                from ...models import Struct
                structs_dict[name] = Struct(
                    name=name,
                    fields=field_objects,
                    tag_name=""
                )
            
            # Process unions
            for start_pos, end_pos, name in unions:
                union_content = self._extract_token_range(tokens, start_pos, end_pos)
                fields = self._parse_struct_fields(tokens, start_pos, end_pos)
                # Convert fields to Field objects
                field_objects = []
                for field_name, field_type in fields:
                    field_objects.append(Field(name=field_name, type=field_type))
                
                # Create Union object
                from ...models import Union
                unions_dict[name] = Union(
                    name=name,
                    fields=field_objects,
                    tag_name=""
                )
            
            # Process enums
            for start_pos, end_pos, name in enums:
                enum_content = self._extract_token_range(tokens, start_pos, end_pos)
                values = self._parse_enum_values(tokens, start_pos, end_pos)
                # Convert values to EnumValue objects
                from ...models import EnumValue, Enum
                enum_value_objects = []
                for value_name in values:
                    enum_value_objects.append(EnumValue(name=value_name))
                
                # Create Enum object
                enums_dict[name] = Enum(
                    name=name,
                    values=enum_value_objects
                )
            
            # Create file model
            file_model = FileModel(
                file_path=str(file_path),
                structs=structs_dict,
                unions=unions_dict,
                enums=enums_dict,
                aliases=aliases_dict,
                functions=functions_dict,
                includes=[]
            )
            
            # Process with unified parser
            self.unified_parser.process_file(file_model)
            
            # Add to project model
            project_model.files[file_path.name] = file_model
            
        except Exception as e:
            self.logger.warning(f"Failed to process file {file_path}: {e}")
            raise
        
        # Save to output file
        output_file = f"{filename}_model.json"
        project_model.save(output_file)
        
        return output_file
    
    def _extract_token_range(self, tokens, start, end):
        """Extract text from token range."""
        from ..parser_tokenizer import extract_token_range
        return extract_token_range(tokens, start, end)
    
    def _parse_struct_fields(self, tokens, start, end):
        """Parse struct fields."""
        from ..parser_tokenizer import find_struct_fields
        return find_struct_fields(tokens, start, end)
    
    def _parse_enum_values(self, tokens, start, end):
        """Parse enum values."""
        from ..parser_tokenizer import find_enum_values
        return find_enum_values(tokens, start, end)


# Main parser interface
class AnonymousTypedefProcessor:
    """Main processor for anonymous typedefs using the unified parser system."""
    
    def __init__(self):
        self.unified_parser = UnifiedParser()
        self.logger = logging.getLogger(__name__)
    
    def process_file_model(self, file_model: FileModel) -> None:
        """Process file model using the unified parser system."""
        self.logger.debug(f"Processing file model: {file_model.file_path}")
        self.unified_parser.process_file(file_model)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return self.unified_parser.get_statistics()