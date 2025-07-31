"""
c2puml - Convert C/C++ code to PlantUML diagrams

A Python tool that analyzes C/C++ source code and generates PlantUML class diagrams
with advanced filtering and transformation capabilities.
"""

__version__ = "3.0.0"
__author__ = "C2PUML Team"

# Import from main for CLI entry point
from .main import main

# Import configuration
from .config import Config

# Import data models
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

# Import core processing modules
from .core.parser import CParser, Parser
from .core.transformer import Transformer
from .core.generator import Generator
from .core.preprocessor import PreprocessorManager
from .core.verifier import ModelVerifier

__all__ = [
    "main",
    "Config",
    "Parser",
    "CParser",
    "Transformer",
    "Generator",
    "PreprocessorManager",
    "ModelVerifier",
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