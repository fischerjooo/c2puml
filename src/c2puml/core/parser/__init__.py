"""
Unified Parser Module

This module provides a comprehensive, modular parsing system for C/C++ code
with different complexity levels handled by specialized sub-modules.

Architecture:
- base.py: Base classes and interfaces
- basic_parser.py: Basic typedefs and types
- struct_parser.py: Struct/union parsing
- complex_parser.py: Function pointers, arrays, nested structures
- anonymous_parser.py: Anonymous struct/union extraction
- token_processor.py: Token-based parsing utilities
- pipeline.py: Main parsing pipeline coordinator
"""

from .pipeline import UnifiedParser, AnonymousTypedefProcessor, Parser
from .base import ParserLevel, BaseParser, ParseResult
from .basic_parser import BasicTypedefParser, BasicFieldParser, BasicTypeParser
from .struct_parser import StructTypedefParser, UnionTypedefParser, EnumTypedefParser

__all__ = [
    # New unified system
    'UnifiedParser',
    'AnonymousTypedefProcessor',
    'Parser',
    'ParserLevel',
    'BaseParser', 
    'ParseResult',
    'BasicTypedefParser',
    'BasicFieldParser',
    'BasicTypeParser',
    'StructTypedefParser',
    'UnionTypedefParser',
    'EnumTypedefParser'
]