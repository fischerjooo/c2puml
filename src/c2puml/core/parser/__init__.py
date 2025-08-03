"""
Unified Parser Module

This module provides a comprehensive, modular parsing system for C/C++ code
with different complexity levels handled by specialized sub-modules.

Architecture:
- base.py: Base classes and interfaces
- simple_parser.py: Basic typedefs and simple types
- struct_parser.py: Struct/union parsing
- complex_parser.py: Function pointers, arrays, nested structures
- anonymous_parser.py: Anonymous struct/union extraction
- token_processor.py: Token-based parsing utilities
- pipeline.py: Main parsing pipeline coordinator
"""

from .pipeline import UnifiedParser, AnonymousTypedefProcessor
from .base import ParserLevel, BaseParser, ParseResult
from .simple_parser import SimpleTypedefParser, SimpleFieldParser, SimpleTypeParser
from .struct_parser import StructTypedefParser, UnionTypedefParser, EnumTypedefParser

__all__ = [
    # New unified system
    'UnifiedParser',
    'AnonymousTypedefProcessor',
    'ParserLevel',
    'BaseParser', 
    'ParseResult',
    'SimpleTypedefParser',
    'SimpleFieldParser',
    'SimpleTypeParser',
    'StructTypedefParser',
    'UnionTypedefParser',
    'EnumTypedefParser'
]