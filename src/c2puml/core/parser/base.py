"""
Base Parser Classes and Interfaces

This module defines the foundational classes and interfaces for the unified
parser system, including parser levels, base classes, and common data structures.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any, Union, Tuple, Set
from pathlib import Path

from ...models import Struct, Union, Field, Alias, FileModel


class ParserLevel(Enum):
    """Defines the complexity level of parsing operations."""
    SIMPLE = "simple"           # Basic typedefs, simple types
    STRUCT = "struct"           # Struct/union parsing
    COMPLEX = "complex"         # Function pointers, arrays, nested structures
    ANONYMOUS = "anonymous"     # Anonymous struct/union extraction


@dataclass
class ParseContext:
    """Context information for parsing operations."""
    file_path: str
    line_number: int = 0
    source_text: str = ""
    available_types: Set[str] = field(default_factory=set)
    parent_structure: Optional[str] = None
    nesting_level: int = 0


@dataclass
class ParseResult:
    """Result of a parsing operation."""
    success: bool
    parsed_data: Optional[Any] = None
    error_message: Optional[str] = None
    parser_level: ParserLevel = ParserLevel.SIMPLE
    confidence: float = 0.0  # 0.0 to 1.0, how confident the parser is


@dataclass
class TypedefInfo:
    """Information about a parsed typedef."""
    name: str
    base_type: str
    typedef_type: str  # "simple", "struct", "union", "function_pointer", etc.
    fields: List[Field] = field(default_factory=list)
    parameters: List[str] = field(default_factory=list)  # For function pointers
    array_size: Optional[str] = None
    pointer_level: int = 0
    is_const: bool = False
    is_volatile: bool = False
    source_text: str = ""
    line_number: int = 0
    file_path: str = ""


@dataclass
class AnonymousStructure:
    """Represents an extracted anonymous structure."""
    parent_name: str
    structure_type: str  # "struct" or "union"
    fields: List[Field]
    generated_name: str
    source_text: str
    nesting_level: int = 0
    original_field_name: Optional[str] = None


class BaseParser(ABC):
    """Abstract base class for all parsers in the system."""
    
    def __init__(self):
        self.level: ParserLevel = ParserLevel.SIMPLE
        self.name: str = self.__class__.__name__
    
    @abstractmethod
    def can_parse(self, text: str, context: ParseContext) -> bool:
        """Check if this parser can handle the given text."""
        pass
    
    @abstractmethod
    def parse(self, text: str, context: ParseContext) -> ParseResult:
        """Parse the text and return a result."""
        pass
    
    def get_confidence(self, text: str, context: ParseContext) -> float:
        """Get confidence level for parsing this text (0.0 to 1.0)."""
        if self.can_parse(text, context):
            return 1.0
        return 0.0
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text before parsing."""
        # Remove comments
        text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_basic_info(self, text: str) -> Dict[str, Any]:
        """Extract basic information from typedef text."""
        info = {
            'has_typedef': 'typedef' in text,
            'has_struct': 'struct' in text,
            'has_union': 'union' in text,
            'has_enum': 'enum' in text,
            'has_function_pointer': '(*' in text and ')' in text,
            'has_array': '[' in text and ']' in text,
            'has_pointer': '*' in text,
            'has_anonymous': '{' in text and '}' in text,
            'brace_count': text.count('{') - text.count('}'),
            'parenthesis_count': text.count('(') - text.count(')'),
            'bracket_count': text.count('[') - text.count(']'),
        }
        return info


class ParserRegistry:
    """Registry for managing all available parsers."""
    
    def __init__(self):
        self.parsers: Dict[ParserLevel, List[BaseParser]] = {
            ParserLevel.SIMPLE: [],
            ParserLevel.STRUCT: [],
            ParserLevel.COMPLEX: [],
            ParserLevel.ANONYMOUS: [],
        }
    
    def register_parser(self, parser: BaseParser) -> None:
        """Register a parser for its level."""
        self.parsers[parser.level].append(parser)
    
    def get_parsers_for_level(self, level: ParserLevel) -> List[BaseParser]:
        """Get all parsers for a specific level."""
        return self.parsers.get(level, [])
    
    def find_best_parser(self, text: str, context: ParseContext) -> Optional[BaseParser]:
        """Find the best parser for the given text."""
        best_parser = None
        best_confidence = 0.0
        
        # Try parsers in order of complexity
        for level in [ParserLevel.SIMPLE, ParserLevel.STRUCT, ParserLevel.COMPLEX, ParserLevel.ANONYMOUS]:
            for parser in self.parsers[level]:
                confidence = parser.get_confidence(text, context)
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_parser = parser
        
        return best_parser if best_confidence > 0.0 else None
    
    def parse_with_best_parser(self, text: str, context: ParseContext) -> ParseResult:
        """Parse text using the best available parser."""
        parser = self.find_best_parser(text, context)
        if parser:
            return parser.parse(text, context)
        
        return ParseResult(
            success=False,
            error_message=f"No suitable parser found for: {text[:100]}...",
            parser_level=ParserLevel.SIMPLE
        )


class ParserError(Exception):
    """Base exception for parser errors."""
    
    def __init__(self, message: str, parser_name: str = "", context: Optional[ParseContext] = None):
        super().__init__(message)
        self.parser_name = parser_name
        self.context = context


class ParsingPipeline:
    """Coordinates the parsing pipeline across different complexity levels."""
    
    def __init__(self):
        self.registry = ParserRegistry()
        self.results: List[ParseResult] = []
        self.errors: List[ParserError] = []
    
    def add_parser(self, parser: BaseParser) -> None:
        """Add a parser to the registry."""
        self.registry.register_parser(parser)
    
    def parse_text(self, text: str, context: ParseContext) -> ParseResult:
        """Parse text using the appropriate parser."""
        try:
            result = self.registry.parse_with_best_parser(text, context)
            self.results.append(result)
            return result
        except Exception as e:
            error = ParserError(str(e), context=context)
            self.errors.append(error)
            return ParseResult(
                success=False,
                error_message=str(e),
                parser_level=ParserLevel.SIMPLE
            )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get parsing statistics."""
        total_parses = len(self.results)
        successful_parses = sum(1 for r in self.results if r.success)
        
        level_counts = {}
        for level in ParserLevel:
            level_counts[level.value] = sum(
                1 for r in self.results 
                if r.success and r.parser_level == level
            )
        
        return {
            'total_parses': total_parses,
            'successful_parses': successful_parses,
            'error_count': len(self.errors),
            'success_rate': successful_parses / total_parses if total_parses > 0 else 0.0,
            'level_counts': level_counts
        }