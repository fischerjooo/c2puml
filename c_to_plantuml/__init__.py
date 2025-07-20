"""
C to PlantUML Converter

A Python tool that analyzes C/C++ source code and generates PlantUML class diagrams.
"""

__version__ = "3.0.0"
__author__ = "C to PlantUML Team"

from .config import Config
from .generator import Generator, PlantUMLGenerator
from .models import (
    Enum,
    Field,
    FileModel,
    Function,
    IncludeRelation,
    ProjectModel,
    Struct,
    TypedefRelation,
    Union,
)
from .parser import CParser, Parser
from .transformer import Transformer

__all__ = [
    "Parser",
    "CParser",
    "Transformer",
    "Generator",
    "PlantUMLGenerator",
    "Config",
    "ProjectModel",
    "FileModel",
    "Struct",
    "Enum",
    "Union",
    "Function",
    "Field",
    "TypedefRelation",
    "IncludeRelation",
]
