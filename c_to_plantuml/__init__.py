"""
C to PlantUML Converter

A Python tool that analyzes C/C++ source code and generates PlantUML class diagrams.
"""

__version__ = "2.0.0"
__author__ = "C to PlantUML Team"

from .analyzer import Analyzer
from .generator import Generator
from .parser import CParser
from .config import Config
from .models import ProjectModel, FileModel, Struct, Enum, Function, Field

__all__ = [
    'Analyzer',
    'Generator', 
    'CParser',
    'Config',
    'ProjectModel',
    'FileModel',
    'Struct',
    'Enum',
    'Function',
    'Field'
] 