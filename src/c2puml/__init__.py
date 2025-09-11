"""
c2puml - Convert C/C++ code to PlantUML diagrams

A Python tool that analyzes C/C++ source code and generates PlantUML class diagrams
with advanced filtering and transformation capabilities.
"""

__version__ = "2025.9.11"
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

# Create module aliases for backward compatibility with existing imports
from . import core
# Make c2puml.parser available (points to core.parser)
import sys
parser = core.parser
sys.modules[__name__ + '.parser'] = parser
# Make c2puml.generator available (points to core.generator) 
generator = core.generator
sys.modules[__name__ + '.generator'] = generator
# Make c2puml.transformer available (points to core.transformer)
transformer = core.transformer  
sys.modules[__name__ + '.transformer'] = transformer
# Make c2puml.parser_tokenizer available (points to core.parser_tokenizer)
parser_tokenizer = core.parser_tokenizer
sys.modules[__name__ + '.parser_tokenizer'] = parser_tokenizer
# Make c2puml.verifier available (points to core.verifier)
verifier = core.verifier
sys.modules[__name__ + '.verifier'] = verifier

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