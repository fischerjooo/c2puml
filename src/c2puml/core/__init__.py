"""
Core processing modules for c2puml.

This package contains the main processing logic for parsing C/C++ code,
transforming the parsed model, and generating PlantUML diagrams.
"""

from .parser import CParser, Parser
from .transformer import Transformer
from .generator import Generator
from .preprocessor import PreprocessorManager
from .verifier import ModelVerifier

__all__ = [
    "Parser",
    "CParser", 
    "Transformer",
    "Generator",
    "PreprocessorManager",
    "ModelVerifier",
]