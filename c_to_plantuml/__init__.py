"""
C to PlantUML Converter

A Python tool that analyzes C/C++ source code and generates PlantUML class diagrams.
"""

__version__ = "3.0.0"
__author__ = "C to PlantUML Team"

from .config import Config
from .generator import Generator
from .models import (
    Alias,
    Enum,
    Field,
    FileModel,
    Function,
    IncludeRelation,
    ProjectModel,
    Struct,
    Union,
)
from .parser import CParser, Parser
from .transformer import Transformer

__all__ = [
    "Parser",
    "CParser",
    "Transformer",
    "Generator",
    "Config",
    "ProjectModel",
    "FileModel",
    "Struct",
    "Enum",
    "Union",
    "Function",
    "Field",
    "IncludeRelation",
    "Alias",
]
