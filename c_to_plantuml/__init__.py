"""
C to PlantUML Converter

A Python tool that analyzes C/C++ source code and generates PlantUML class diagrams.
"""

__version__ = "3.0.0"
__author__ = "C to PlantUML Team"

from .parser import Parser, CParser
from .transformer import Transformer
from .generator import Generator, PlantUMLGenerator
from .config import Config
from .models import ProjectModel, FileModel, Struct, Enum, Union, Function, Field, TypedefRelation, IncludeRelation

__all__ = [
    'Parser',
    'CParser',
    'Transformer',
    'Generator',
    'PlantUMLGenerator',
    'Config',
    'ProjectModel',
    'FileModel',
    'Struct',
    'Enum',
    'Union',
    'Function',
    'Field',
    'TypedefRelation',
    'IncludeRelation'
] 