"""
Unified Parser Pipeline

Main coordinator for the unified parser system that integrates all parser modules
and provides the interface for the existing architecture.
"""

import logging
from typing import List, Optional, Dict, Any, Set

from .base import (
    ParserLevel, ParseContext, ParseResult, TypedefInfo, 
    AnonymousStructure, ParserRegistry, ParsingPipeline, ParserError
)
from .simple_parser import SimpleTypedefParser, SimpleFieldParser, SimpleTypeParser
from .struct_parser import StructTypedefParser, UnionTypedefParser, EnumTypedefParser
from ...models import Struct, Union, Field, Alias, FileModel


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
        # Simple parsers
        self.pipeline.add_parser(SimpleTypedefParser())
        self.pipeline.add_parser(SimpleFieldParser())
        self.pipeline.add_parser(SimpleTypeParser())
        
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
        result = self.pipeline.parse_text(alias_data.type, context)
        
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


# Backward compatibility interface
class AnonymousTypedefProcessor:
    """Backward compatibility wrapper for the existing architecture."""
    
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